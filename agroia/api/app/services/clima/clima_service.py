"""Clima de um ponto: baixa do NASA POWER uma vez por célula, guarda por mês e devolve com fonte e período."""
from dataclasses import asdict, dataclass, field
from datetime import date

from fastapi import Depends

from app.core.erros import ErroDeNegocio
from app.models import ClimaCelula
from app.repositories.clima_repository import ClimaRepository
from app.services.clima.agregacao import DiaClima, LinhaMensal, agregar_por_mes, limite_chuva_forte
from app.services.clima.celula import centro_da_celula, id_da_celula
from app.services.clima.et0 import et0_diaria
from app.services.clima.limiares import BASE_FIM, BASE_INICIO
from app.services.integracao.nasa_power import ClienteNasaPower, get_cliente

FONTE = "NASA POWER daily, comunidade AG"
INICIO_SERIE = date(BASE_INICIO, 1, 1)
NOTA_ET0 = "ET0 calculada pelo Field Shift (FAO-56 Penman-Monteith) com temperatura, umidade, vento e radiação do NASA POWER."

# Variáveis que a climatologia média por mês (as contagens viram média por ano).
CAMPOS_MEDIA = (
    "chuva_mm", "et0_mm", "tmed_c", "tmax_media_c", "tmin_media_c",
    "dias_geada", "dias_calor", "dias_chuva_forte", "maior_seq_seca_dias",
)  # fmt: skip


@dataclass
class MesClimatologia:
    mes: int
    anos_com_dado: int  # anos de 1991-2020 com algum dado neste mês
    chuva_mm: float | None
    et0_mm: float | None
    tmed_c: float | None
    tmax_media_c: float | None
    tmin_media_c: float | None
    tmax_absoluta_c: float | None  # maior Tmax de todo o período-base (não é média)
    tmin_absoluta_c: float | None  # menor Tmin de todo o período-base (não é média)
    dias_geada: float | None  # média de dias por ano
    dias_calor: float | None
    dias_chuva_forte: float | None
    maior_seq_seca_dias: float | None  # média, entre os anos, da maior sequência seca do mês


@dataclass
class Climatologia:
    celula_id: str
    lat: float
    lon: float
    elevacao_m: float | None
    limite_chuva_forte_mm: float | None
    fonte: str  # "NASA POWER, média 1991–2020, célula ~50 km centrada em ..."
    periodo: str
    meses: list[MesClimatologia]
    notas: list[str] = field(default_factory=lambda: [NOTA_ET0])


@dataclass
class ClimaDoAno:
    celula_id: str
    ano: int
    fonte: str
    periodo: str
    meses: list[LinhaMensal]  # só os meses que existem na série
    notas: list[str] = field(default_factory=lambda: [NOTA_ET0])


def _media(valores: list[float]) -> float | None:
    return round(sum(valores) / len(valores), 2) if valores else None


def media_por_mes(linhas: list[LinhaMensal]) -> list[MesClimatologia]:
    """Climatologia: média de cada variável por mês sobre os anos de 1991-2020. Mês sem nenhum valor fica None."""
    base = [l for l in linhas if BASE_INICIO <= l.ano <= BASE_FIM]
    resultado = []
    for mes in range(1, 13):
        do_mes = [l for l in base if l.mes == mes and any(getattr(l, c) is not None for c in CAMPOS_MEDIA)]
        medias = {c: _media([v for l in do_mes if (v := getattr(l, c)) is not None]) for c in CAMPOS_MEDIA}
        tmaxs = [l.tmax_absoluta_c for l in do_mes if l.tmax_absoluta_c is not None]
        tmins = [l.tmin_absoluta_c for l in do_mes if l.tmin_absoluta_c is not None]
        resultado.append(
            MesClimatologia(
                mes=mes,
                anos_com_dado=len(do_mes),
                tmax_absoluta_c=max(tmaxs) if tmaxs else None,
                tmin_absoluta_c=min(tmins) if tmins else None,
                **medias,
            )
        )
    return resultado


def _descricao_celula(celula: ClimaCelula) -> str:
    return f"célula ~50 km centrada em {celula.lat}, {celula.lon}"


class ClimaService:
    def __init__(
        self,
        repositorio: ClimaRepository = Depends(),
        cliente: ClienteNasaPower = Depends(get_cliente),
    ):
        self.repositorio = repositorio
        self.cliente = cliente

    def obter(self, lat: float, lon: float, hoje: date | None = None) -> ClimaCelula:
        """Célula do ponto com o clima já no banco. Baixa do NASA POWER se não houver, faltar o último ano ou o GD."""
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ErroDeNegocio(422, "Latitude deve estar entre -90 e 90 e longitude entre -180 e 180.")
        fim = date((hoje or date.today()).year - 1, 12, 31)  # último ano completo
        celula = self.repositorio.celula_por_id(id_da_celula(lat, lon))
        if celula is not None and celula.fim >= fim and not self.repositorio.faltam_graus_dia(celula.id):
            return celula
        return self._baixar_e_gravar(lat, lon, fim)

    def _baixar_e_gravar(self, lat: float, lon: float, fim: date) -> ClimaCelula:
        clat, clon = centro_da_celula(lat, lon)  # chama o POWER pelo centro: vizinhos dividem o cache
        serie = self.cliente.serie_diaria(clat, clon, INICIO_SERIE, fim)
        dias = [
            DiaClima(
                data=d.data,
                tmed=d.t2m,
                tmax=d.tmax,
                tmin=d.tmin,
                chuva=d.chuva,
                et0=et0_diaria(d.data, d.tmax, d.tmin, d.ur, d.vento, d.radiacao, clat, serie.elevacao_m),
            )
            for d in serie.dias
        ]
        limite = limite_chuva_forte(dias)
        celula = {
            "id": id_da_celula(lat, lon),
            "lat": clat,
            "lon": clon,
            "elevacao_m": serie.elevacao_m,
            "inicio": INICIO_SERIE,
            "fim": fim,
            "limite_chuva_forte_mm": limite,
            "fonte": FONTE,
        }
        meses = [asdict(l) for l in agregar_por_mes(dias, limite)]
        return self.repositorio.gravar(celula, meses)

    def climatologia(self, celula: ClimaCelula) -> Climatologia:
        linhas = [self._linha(m) for m in self.repositorio.meses(celula.id)]
        return Climatologia(
            celula_id=celula.id,
            lat=celula.lat,
            lon=celula.lon,
            elevacao_m=celula.elevacao_m,
            limite_chuva_forte_mm=celula.limite_chuva_forte_mm,
            fonte=f"NASA POWER, média {BASE_INICIO}–{BASE_FIM}, {_descricao_celula(celula)}",
            periodo=f"{BASE_INICIO}–{BASE_FIM}",
            meses=media_por_mes(linhas),
        )

    def ano(self, celula: ClimaCelula, ano: int) -> ClimaDoAno:
        return ClimaDoAno(
            celula_id=celula.id,
            ano=ano,
            fonte=f"NASA POWER, {ano}, {_descricao_celula(celula)}",
            periodo=str(ano),
            meses=[self._linha(m) for m in self.repositorio.meses(celula.id, ano)],
        )

    @staticmethod
    def _linha(m) -> LinhaMensal:
        return LinhaMensal(**{c: getattr(m, c) for c in LinhaMensal.__dataclass_fields__})
