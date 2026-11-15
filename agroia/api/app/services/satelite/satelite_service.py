"""Satélite da fazenda para o Dashboard: umidade do solo (SMAP L4), verde da lavoura (MODIS NDVI) e chuva (GPM IMERG).

Cada parte é independente: se uma falha, as outras aparecem e a que faltou vem em `faltas` com o motivo, sem inventar
valor. A chuva usa o IMERG; se a conta do Earthdata não tiver acesso à GES DISC, usa a chuva do NASA POWER e diz isso.
"""
import logging
import statistics
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from fastapi import Depends

from app.services.integracao.cache import CacheLru
from app.services.integracao.earthdata import ClienteEarthdata, ErroEarthdata, Granulo, get_cliente
from app.services.integracao.nasa_power import ClienteNasaPower, ErroNasaPower
from app.services.integracao.nasa_power import get_cliente as get_power
from app.services.satelite import grade

log = logging.getLogger(__name__)

PARALELO = 6
ANOS_HISTORICO = 8
INICIO_SMAP = date(2015, 3, 31)
DIAS_CHUVA = 30
NDVI_FILL = -3000
NDVI_ESCALA = 0.0001
CONFIAVEL = (0, 1)  # pixel_reliability do MOD13Q1: 0 bom, 1 marginal (2 neve, 3 nuvem)

FONTE_SMAP = "NASA SMAP L4 (SPL4SMGP v8)"
FONTE_MODIS = "NASA MODIS Terra (MOD13Q1 v6.1)"
FONTE_IMERG = "NASA GPM IMERG Late, diário (v07)"
FONTE_POWER = "NASA POWER (PRECTOTCORR)"

MSG_SEM_TOKEN = "O servidor ainda não tem o token do Earthdata (EARTHDATA_TOKEN)."
MSG_IMERG_BLOQUEADO = (
    "A conta do Earthdata ainda não autorizou a GES DISC, onde fica o IMERG. "
    "Mostrando a chuva do NASA POWER, que também vem da NASA."
)

_cache = CacheLru(tamanho=500)


@dataclass
class Umidade:
    fonte: str
    resolucao: str
    data: date
    superficie: float  # m³/m³, 0-5 cm
    raiz: float  # m³/m³, 0-100 cm
    situacao: str | None  # "seco", "normal", "umido"; None sem histórico suficiente
    posicao: float | None  # 0 a 1: onde a umidade de hoje fica entre os mesmos dias dos anos anteriores
    media_historica: float | None
    anos_comparados: int


@dataclass
class PontoNdvi:
    data: date
    valor: float


@dataclass
class Ndvi:
    fonte: str
    resolucao: str
    data: date
    valor: float
    situacao: str  # "descoberto", "pouco", "verde", "muito"
    serie: list[PontoNdvi]


@dataclass
class DiaChuva:
    data: date
    mm: float


@dataclass
class Chuva:
    fonte: str
    resolucao: str
    dias: list[DiaChuva]
    total_7d: float
    total_30d: float
    maior: DiaChuva | None


@dataclass
class Satelite:
    lat: float
    lon: float
    umidade: Umidade | None
    ndvi: Ndvi | None
    chuva: Chuva | None
    faltas: dict[str, str] = field(default_factory=dict)
    avisos: list[str] = field(default_factory=list)
    gerado_em: datetime = field(default_factory=lambda: datetime.now(UTC))


def situacao_ndvi(v: float) -> str:
    if v < 0.2:
        return "descoberto"
    if v < 0.4:
        return "pouco"
    if v < 0.6:
        return "verde"
    return "muito"


def situacao_umidade(atual: float, historico: list[float]) -> tuple[str | None, float | None, float | None]:
    """Compara com o mesmo dia dos anos anteriores. Precisa de 3 anos ou mais."""
    if len(historico) < 3:
        return None, None, None
    media = statistics.fmean(historico)
    desvio = max(statistics.pstdev(historico), 0.01)
    z = (atual - media) / desvio
    situacao = "seco" if z < -0.75 else "umido" if z > 0.75 else "normal"
    posicao = (sum(h < atual for h in historico) + 0.5 * sum(h == atual for h in historico)) / len(historico)
    return situacao, round(posicao, 2), round(media, 3)


def _centro_ou_media(linhas: list[list[float | None]], i: int, j: int) -> float | None:
    try:
        v = linhas[i][j]
    except IndexError:
        v = None
    if v is not None:
        return v
    validos = [x for linha in linhas for x in linha if x is not None]
    return statistics.fmean(validos) if validos else None


def _mesmo_dia(d: date, ano: int) -> date:
    try:
        return d.replace(year=ano)
    except ValueError:  # 29/02
        return d.replace(year=ano, day=28)


class SateliteService:
    def __init__(
        self,
        cliente: ClienteEarthdata = Depends(get_cliente),
        power: ClienteNasaPower = Depends(get_power),
    ):
        self.cliente = cliente
        self.power = power
        self.hoje: Callable[[], date] = date.today  # os testes trocam por uma data fixa

    def obter(self, lat: float, lon: float) -> Satelite:
        partes = {"umidade": self._umidade, "ndvi": self._ndvi, "chuva": self._chuva}
        resultado = Satelite(lat=lat, lon=lon, umidade=None, ndvi=None, chuva=None)
        with ThreadPoolExecutor(len(partes)) as ex:
            futuros = {nome: ex.submit(self._com_cache, nome, f, lat, lon) for nome, f in partes.items()}
        for nome, fut in futuros.items():
            try:
                valor, avisos = fut.result()
                setattr(resultado, nome, valor)
                resultado.avisos.extend(avisos)
            except ErroEarthdata as e:
                resultado.faltas[nome] = MSG_SEM_TOKEN if e.sem_permissao and not self.cliente.tem_token else str(e)
            except ErroNasaPower as e:
                resultado.faltas[nome] = str(e)
            except Exception:  # um produto quebrado não derruba o Dashboard
                log.exception("Satélite: falha inesperada em %s", nome)
                resultado.faltas[nome] = "Erro inesperado ao ler este dado da NASA."
        return resultado

    def _com_cache(self, nome: str, f, lat: float, lon: float):
        chave = (nome, round(lat, 3), round(lon, 3), self.hoje())
        guardado = _cache.pegar(chave)
        if guardado is not None:
            return guardado
        valor = f(lat, lon)
        _cache.guardar(chave, valor)
        return valor

    # --- SMAP L4 -------------------------------------------------------------------
    def _umidade(self, lat: float, lon: float) -> tuple[Umidade | None, list[str]]:
        hoje = self.hoje()
        recentes = self.cliente.granulos("SPL4SMGP", hoje - timedelta(days=20), hoje, limite=1)
        if not recentes:
            raise ErroEarthdata("Não achei arquivo recente do SMAP L4 no catálogo da NASA.")
        g = recentes[0]
        linha, coluna = grade.celula_ease2_9km(lat, lon)
        l0, l1, ci = grade.janela(linha, grade.LINHAS_EASE)
        c0, c1, cj = grade.janela(coluna, grade.COLUNAS_EASE)
        idx = f"[{l0}:{l1}][{c0}:{c1}]"
        sup, raiz = "/Geophysical_Data/sm_surface", "/Geophysical_Data/sm_rootzone"
        dados = self.cliente.recorte(g.opendap, {sup: idx, raiz: idx})
        v_sup, v_raiz = _centro_ou_media(dados[sup], ci, cj), _centro_ou_media(dados[raiz], ci, cj)
        if v_sup is None or v_raiz is None:
            raise ErroEarthdata("O SMAP não tem umidade para este ponto (água, cidade ou gelo).")

        def do_ano(ano: int) -> float | None:
            d = _mesmo_dia(g.data, ano)
            try:
                gs = self.cliente.granulos("SPL4SMGP", d, d, limite=1)
                return _centro_ou_media(self.cliente.recorte(gs[0].opendap, {raiz: idx})[raiz], ci, cj) if gs else None
            except ErroEarthdata as e:
                log.info("SMAP histórico %s: %s", ano, e)
                return None

        anos = [a for a in range(g.data.year - ANOS_HISTORICO, g.data.year) if _mesmo_dia(g.data, a) >= INICIO_SMAP]
        with ThreadPoolExecutor(PARALELO) as ex:
            historico = [v for v in ex.map(do_ano, anos) if v is not None]
        situacao, posicao, media = situacao_umidade(v_raiz, historico)
        return Umidade(
            fonte=FONTE_SMAP,
            resolucao="~9 km",
            data=g.data,
            superficie=round(v_sup, 3),
            raiz=round(v_raiz, 3),
            situacao=situacao,
            posicao=posicao,
            media_historica=media,
            anos_comparados=len(historico),
        ), []

    # --- MODIS NDVI ----------------------------------------------------------------
    def _ndvi(self, lat: float, lon: float) -> tuple[Ndvi | None, list[str]]:
        hoje = self.hoje()
        px = grade.pixel_modis(lat, lon)
        granulos = [
            g for g in self.cliente.granulos("MOD13Q1", hoje - timedelta(days=365), hoje, versao="061", ponto=(lat, lon), limite=40)
            if f".{px.tile}." in g.titulo
        ]
        if not granulos:
            raise ErroEarthdata("Não achei imagens do MODIS para este ponto no último ano.")
        l0, l1, ci = grade.janela(px.linha, grade.PIXELS_TILE_250M)
        c0, c1, cj = grade.janela(px.coluna, grade.PIXELS_TILE_250M)
        idx = f"[{l0}:{l1}][{c0}:{c1}]"
        base = "/MODIS_Grid_16DAY_250m_500m_VI/Data_Fields/"
        v_ndvi, v_conf = base + "_250m_16_days_NDVI", base + "_250m_16_days_pixel_reliability"

        def ler(g: Granulo) -> PontoNdvi | None:
            try:
                d = self.cliente.recorte(g.opendap, {v_ndvi: idx, v_conf: idx})
            except ErroEarthdata as e:
                if e.sem_permissao:
                    raise
                log.info("MODIS %s: %s", g.titulo, e)
                return None
            nd, cf = d[v_ndvi], d[v_conf]

            def bom(i: int, j: int) -> float | None:
                try:
                    n, c = nd[i][j], cf[i][j]
                except IndexError:
                    return None
                return n if n is not None and n != NDVI_FILL and c in CONFIAVEL else None

            valor = bom(ci, cj)
            if valor is None:  # centro com nuvem: mediana dos vizinhos limpos
                vizinhos = [v for i in range(len(nd)) for j in range(len(nd[i])) if (v := bom(i, j)) is not None]
                valor = statistics.median(vizinhos) if vizinhos else None
            return None if valor is None else PontoNdvi(data=g.data, valor=round(valor * NDVI_ESCALA, 3))

        with ThreadPoolExecutor(PARALELO) as ex:
            serie = sorted((p for p in ex.map(ler, granulos) if p is not None), key=lambda p: p.data)
        if not serie:
            raise ErroEarthdata("As imagens do MODIS do último ano estão cobertas de nuvem neste ponto.")
        ultimo = serie[-1]
        return Ndvi(
            fonte=FONTE_MODIS,
            resolucao="250 m, a cada 16 dias",
            data=ultimo.data,
            valor=ultimo.valor,
            situacao=situacao_ndvi(ultimo.valor),
            serie=serie,
        ), []

    # --- Chuva: IMERG, com o NASA POWER de reserva -----------------------------------
    def _chuva(self, lat: float, lon: float) -> tuple[Chuva, list[str]]:
        if self.cliente.tem_token:
            try:
                return self._chuva_imerg(lat, lon), []
            except ErroEarthdata as e:
                log.info("IMERG indisponível, usando o NASA POWER: %s", e)
                aviso = MSG_IMERG_BLOQUEADO if e.sem_permissao else f"IMERG indisponível agora ({e}). Mostrando a chuva do NASA POWER."
                return self._chuva_power(lat, lon), [aviso]
        return self._chuva_power(lat, lon), []

    def _chuva_imerg(self, lat: float, lon: float) -> Chuva:
        hoje = self.hoje()
        gs = self.cliente.granulos("GPM_3IMERGDL", hoje - timedelta(days=DIAS_CHUVA + 10), hoje, versao="07", limite=DIAS_CHUVA)
        if not gs:
            raise ErroEarthdata("Não achei arquivos recentes do IMERG.")
        i_lon, i_lat = grade.celula_imerg(lat, lon)
        a0, a1, ci = grade.janela(i_lon, grade.COLUNAS_IMERG)
        b0, b1, cj = grade.janela(i_lat, grade.LINHAS_IMERG)
        var = "/precipitation"
        idx = f"[0][{a0}:{a1}][{b0}:{b1}]"

        def ler(g: Granulo) -> DiaChuva | None:
            v = _centro_ou_media(self.cliente.recorte(g.opendap, {var: idx})[var], ci, cj)
            return None if v is None else DiaChuva(data=g.data, mm=round(v, 1))

        # o primeiro sozinho: se a conta não tiver acesso, falha uma vez só
        primeiro = ler(gs[0])
        with ThreadPoolExecutor(PARALELO) as ex:
            resto = list(ex.map(ler, gs[1:]))
        dias = sorted((d for d in [primeiro, *resto] if d is not None), key=lambda d: d.data)
        return _resumo_chuva(FONTE_IMERG, "~10 km", dias)

    def _chuva_power(self, lat: float, lon: float) -> Chuva:
        hoje = self.hoje()
        serie = self.power.serie_diaria(lat, lon, hoje - timedelta(days=DIAS_CHUVA + 15), hoje)
        dias = [DiaChuva(data=d.data, mm=round(d.chuva, 1)) for d in serie.dias if d.chuva is not None]
        if not dias:
            raise ErroNasaPower("O NASA POWER ainda não tem a chuva dos últimos dias para este ponto.")
        return _resumo_chuva(FONTE_POWER, "~50 km", dias[-DIAS_CHUVA:])


def _resumo_chuva(fonte: str, resolucao: str, dias: list[DiaChuva]) -> Chuva:
    if not dias:
        raise ErroEarthdata("Sem dias de chuva com dado no último mês.")
    return Chuva(
        fonte=fonte,
        resolucao=resolucao,
        dias=dias,
        total_7d=round(sum(d.mm for d in dias[-7:]), 1),
        total_30d=round(sum(d.mm for d in dias), 1),
        maior=max(dias, key=lambda d: d.mm),
    )


def limpar_cache() -> None:
    _cache.limpar()
