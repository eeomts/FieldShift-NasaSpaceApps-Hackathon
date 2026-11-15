"""As 5 ferramentas do agente: declaradas para o Gemini e executadas aqui; cada uma devolve dados e as fontes que os geraram."""
import csv
import inspect
import logging
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import date
from functools import lru_cache

from google.genai import types

from app.core.caminhos import RAIZ_REPO
from app.core.erros import ErroDeNegocio
from app.models import Fazenda, Usuario
from app.schemas.chat import Fonte
from app.schemas.onboarding import Respostas
from app.services import catalogo
from app.services.agente.busca_conhecimento_service import BuscaConhecimentoService
from app.services.clima.clima_service import ClimaService
from app.services.clima.limiares import BASE_INICIO, CHUVA_DIA_SECO_MM, TMAX_CALOR_C, TMIN_GEADA_C
from app.services.integracao.nasa_power import ErroNasaPower
from app.services.motor.modelo import Analise, ResultadoEstrategia
from app.services.motor.motor_service import MotorService
from app.services.onboarding import perfil

log = logging.getLogger(__name__)

CSV_CULTURAS = RAIZ_REPO / "data" / "catalogo" / "culturas.csv"
MAX_FONTES_CULTURA = 3
MAX_CHARS_FONTE = 150
MAX_TRECHOS_CONHECIMENTO = 3  # os mais bem ordenados da busca: vão ao modelo e às fontes
FONTE_FICHA = "Respostas da sua fazenda"
FONTE_ANALISE = "Comparação de rotações do AgroIA"
MAX_MOTIVOS_ELIMINADAS = 3
_CENTRO_DA_CELULA = re.compile(r",? centrada em [-\d., ]+")  # a coordenada da célula não vai ao modelo


@dataclass
class Resultado:
    dados: dict
    fontes: list[Fonte] = field(default_factory=list)  # só o que de fato gerou dado


def _declaracao(nome: str, descricao: str, propriedades: dict | None = None, obrigatorios: list[str] | None = None) -> types.FunctionDeclaration:
    return types.FunctionDeclaration(
        name=nome,
        description=descricao,
        parameters=types.Schema(type="OBJECT", properties=propriedades or {}, required=obrigatorios or []),
    )


DECLARACOES = [
    types.Tool(
        function_declarations=[
            _declaracao(
                "ver_ficha",
                "Devolve a ficha da fazenda do produtor: respostas do cadastro, perfil de dados do solo, papel, "
                "retrato do solo, calendário de culturas e local (coordenada aproximada). Sem parâmetros.",
            ),
            _declaracao(
                "info_cultura",
                "Parâmetros agronômicos de uma cultura da base do AgroIA: ciclo, temperaturas, sensibilidade à geada, "
                "água, Kc, raiz. Se a cultura não estiver na base, avisa.",
                {"cultura": types.Schema(type="STRING", description="Nome da cultura como o produtor disse (ex.: sorgo, feijão, macaxeira).")},
                ["cultura"],
            ),
            _declaracao(
                "buscar_conhecimento",
                "Busca na base de conhecimento do AgroIA (glossário, metodologia, culturas, satélites) para explicar conceitos.",
                {
                    "consulta": types.Schema(type="STRING", description="O que buscar, em termos técnicos e claros (reescreva a pergunta)."),
                    "expressao_original": types.Schema(type="STRING", description="As palavras do produtor, se forem regionais ou informais (ex.: veranico, terra pelada)."),
                },
                ["consulta"],
            ),
            _declaracao(
                "consultar_clima",
                "Clima mensal da fazenda do produtor no NASA POWER (célula de ~50 km): chuva, evapotranspiração, temperaturas, "
                "dias de risco de geada, calor, chuva forte e maior sequência seca. Sem 'ano': média de 1991–2020. "
                "Com 'ano': aquele ano. Usa o local da ficha; não passe coordenada. Não é previsão do tempo.",
                {"ano": types.Schema(type="INTEGER", description="Ano específico (de 1991 ao último ano completo). Omita para a média histórica.")},
            ),
            _declaracao(
                "comparar_estrategias",
                "Compara a rotação atual da fazenda com as 2 melhores alternativas que o AgroIA calculou (água, terra, erosão, pragas, "
                "renda e animais, com o peso das prioridades do produtor), com o 'por que' e o 'onde piora'. Usa a ficha e o clima da fazenda. Sem parâmetros.",
            ),
        ]
    )
]


def _poda(v):
    """Tira None, listas e dicts vazios (JSON compacto)."""
    if isinstance(v, dict):
        v = {k: _poda(x) for k, x in v.items()}
        return {k: x for k, x in v.items() if x is not None and x != {} and x != []}
    if isinstance(v, list):
        return [_poda(x) for x in v]
    return v


def _corta(texto: str, limite: int) -> str:
    """Corta no fim de uma palavra e marca com reticências."""
    if len(texto) <= limite:
        return texto
    return texto[:limite].rsplit(" ", 1)[0].rstrip(" ,;:(") + "…"


def _r(v: float | None, casas: int = 1) -> float | None:
    return None if v is None else round(v, casas)


@lru_cache
def _parametros_csv() -> dict[str, dict]:
    with CSV_CULTURAS.open(encoding="utf-8", newline="") as f:
        return {linha["id"]: linha for linha in csv.DictReader(f)}


def _converte(valor: str):
    if valor in ("true", "false"):
        return valor == "true"
    try:
        n = float(valor)
    except ValueError:
        return valor
    return int(n) if n.is_integer() and "." not in valor else n


def _parametros_da_cultura(linha: dict) -> tuple[dict, list[str]]:
    ignorar = {"id", "nome", "nome_cientifico", "familia_botanica", "codigo_pam", "nome_zarc", "tipos", "fontes"}
    fontes = [s.strip() for s in (linha.get("fontes") or "").split("|") if s.strip()]
    params = {k: _converte(v) for k, v in linha.items() if k not in ignorar and v not in ("", None)}
    return params, fontes


class Ferramentas:
    def __init__(
        self,
        usuario: Usuario,
        clima: ClimaService,
        motor: MotorService,
        busca: Callable[[], BuscaConhecimentoService],
        conversa_id: int,
        hoje: date,
        ao_falhar: Callable[[], None] = lambda: None,
    ):
        self.usuario = usuario
        self.clima = clima
        self.motor = motor
        self.busca = busca
        self.conversa_id = conversa_id
        self.hoje = hoje
        self.ao_falhar = ao_falhar  # ex.: desfazer a transação do banco que a ferramenta deixou quebrada

    def executar(self, nome: str, args: dict | None) -> Resultado:
        funcao = {
            "ver_ficha": self.ver_ficha,
            "info_cultura": self.info_cultura,
            "buscar_conhecimento": self.buscar_conhecimento,
            "consultar_clima": self.consultar_clima,
            "comparar_estrategias": self.comparar_estrategias,
        }.get(nome)
        if funcao is None:
            return Resultado({"erro": f"Ferramenta desconhecida: {nome}."})
        aceitos = inspect.signature(funcao).parameters
        try:
            return funcao(**{k: v for k, v in (args or {}).items() if k in aceitos})
        except Exception as e:  # uma ferramenta com problema não derruba a resposta: o modelo avisa o produtor
            log.warning("Ferramenta %s falhou: %s", nome, type(e).__name__)
            self.ao_falhar()
            return Resultado({"erro": "Não consegui consultar essa fonte agora. Diga isso ao produtor, sem inventar o dado."})

    # --- 1. ficha ---

    def ver_ficha(self) -> Resultado:
        f: Fazenda | None = self.usuario.fazenda
        if f is None:
            return Resultado({"encontrada": False, "mensagem": "O produtor ainda não preencheu a ficha da fazenda."})
        r = Respostas.model_validate(f.respostas or {})
        texto_livre = {"q5_local", "q8_texto", "q8_culturas", "q26a_texto", "q26b_texto"}  # local vai arredondado, o resto está estruturado
        respostas = r.model_dump(mode="json", exclude_none=True, exclude=texto_livre)
        calendario = [
            {
                "cultura": c.cultura_id or c.texto_original,
                "na_base": c.cultura_id is not None,
                "inicio_mes": c.inicio_mes,
                "fim_mes": c.fim_mes,
                "perene": c.perene or None,
                "consorcio_com": c.consorcio_com,
                "ocupa": c.ocupa,
            }
            for c in r.q8_culturas
        ]
        retrato = f.retrato_solo or {}
        figuras = retrato.get("figuras") or {}
        dados = {
            "encontrada": True,
            "ficha_concluida": f.onboarding_concluido,
            "papel": f.papel,
            "perfil_dados_do_solo": f.perfil,  # A: só respostas; B: respostas e mapas; C: laudo
            "local_aproximado": None if f.lat is None or f.lon is None else {"lat": round(f.lat, 1), "lon": round(f.lon, 1)},
            "calendario": calendario,
            "meses_sem_cobertura": perfil.meses_sem_cobertura(r.q8_culturas),
            "respostas": respostas,
            "retrato_solo": {
                "indicadores": [
                    {k: i.get(k) for k in ("atributo", "valor", "texto", "confianca", "fonte")} for i in retrato.get("indicadores", [])
                ],
                "leitura_cor_e_jeito": figuras.get("leitura"),
                "sintese": _sintese_compacta(retrato.get("sintese")),
            },
        }
        return Resultado(_poda(dados), [Fonte(tipo="fazenda", titulo=FONTE_FICHA)])

    # --- 2. cultura ---

    def info_cultura(self, cultura: str = "") -> Resultado:
        itens = catalogo.culturas()
        achado = catalogo.casa_texto(str(cultura), itens)
        if not achado:
            return Resultado(
                {
                    "encontrada": False,
                    "mensagem": f"A cultura '{str(cultura)[:60]}' não está na base do AgroIA, então não há parâmetros. "
                    "Diga isso ao produtor; não invente valores.",
                    "culturas_na_base": [catalogo.nome_exibicao(c).lower() for c in itens.values()],
                }
            )
        cultura_id = achado[0]["id"]
        item = itens[cultura_id]
        nome = catalogo.nome_exibicao(item)
        dados = {
            "encontrada": True,
            "id": cultura_id,
            "nome": nome,
            "nomes": item["nomes"],
            "grupo": item["grupo"],
            "perene": item["perene"],
            "tipos": item["tipos"],
        }
        titulo = f"Base de culturas: {nome}"
        linha = _parametros_csv().get(cultura_id)
        if linha is None:
            dados["mensagem"] = "Esta cultura está na base, mas ainda sem parâmetros numéricos (ciclo, temperatura, água). Diga isso."
            return Resultado(_poda(dados), [Fonte(tipo="cultura", titulo=titulo, detalhe="Sem parâmetros numéricos na base")])
        params, fontes = _parametros_da_cultura(linha)
        dados["nome_cientifico"] = linha["nome_cientifico"]
        dados["parametros"] = params
        dados["fontes_dos_parametros"] = [_corta(s, MAX_CHARS_FONTE) for s in fontes[:MAX_FONTES_CULTURA]]
        detalhe = f"Parâmetros agronômicos, confiança {params.get('confianca_parametros', 'não informada')}"
        if fontes:
            detalhe += f". Fonte: {_corta(fontes[0], MAX_CHARS_FONTE)}"
        return Resultado(_poda(dados), [Fonte(tipo="cultura", titulo=titulo, detalhe=detalhe)])

    # --- 3. conhecimento ---

    def buscar_conhecimento(self, consulta: str = "", expressao_original: str | None = None) -> Resultado:
        consulta = str(consulta).strip()
        if not consulta:
            return Resultado({"erro": "Consulta vazia."})
        trechos = self.busca().buscar(consulta, expressao_original, conversa_id=self.conversa_id)[:MAX_TRECHOS_CONHECIMENTO]
        if not trechos:
            return Resultado(
                {"trechos": [], "mensagem": "A base de conhecimento do AgroIA não tem nada sobre isso. Diga ao produtor que não encontrou; não invente."}
            )
        dados = {"trechos": [{"documento": t.documento_titulo, "secao": t.secao, "texto": t.conteudo} for t in trechos]}
        fontes = [Fonte(tipo="conhecimento", titulo=t.documento_titulo, detalhe=t.secao) for t in trechos]
        return Resultado(_poda(dados), fontes)

    # --- 4. clima ---

    def consultar_clima(self, ano: int | float | None = None) -> Resultado:
        f: Fazenda | None = self.usuario.fazenda
        if f is None or f.lat is None or f.lon is None:
            return Resultado(
                {"erro": "sem_localizacao", "mensagem": "A ficha da fazenda não tem a localização do campo, então não dá para consultar o clima. Diga que falta o local."}
            )
        if ano is not None and (isinstance(ano, bool) or not isinstance(ano, (int, float))):
            return Resultado({"erro": "Ano inválido."})
        ultimo = self.hoje.year - 1
        if ano is not None and not (BASE_INICIO <= int(ano) <= ultimo):
            return Resultado({"erro": f"Só há clima de {BASE_INICIO} a {ultimo}. Para outros anos, diga que não há dado (e que isso não é previsão)."})
        try:
            celula = self.clima.obter(f.lat, f.lon, hoje=self.hoje)
        except ErroNasaPower:
            return Resultado({"erro": "Não consegui o clima do NASA POWER agora. Diga isso ao produtor, sem inventar números."})

        if ano is None:
            c = self.clima.climatologia(celula)
            meses = [
                _poda(
                    {
                        "mes": m.mes,
                        "anos_com_dado": m.anos_com_dado,
                        "chuva_mm": _r(m.chuva_mm),
                        "et0_mm": _r(m.et0_mm),
                        "tmed_c": _r(m.tmed_c),
                        "tmax_media_c": _r(m.tmax_media_c),
                        "tmin_media_c": _r(m.tmin_media_c),
                        "tmax_maxima_do_periodo_c": _r(m.tmax_absoluta_c),
                        "tmin_minima_do_periodo_c": _r(m.tmin_absoluta_c),
                        "dias_geada_por_ano": _r(m.dias_geada),
                        "dias_calor_por_ano": _r(m.dias_calor),
                        "dias_chuva_forte_por_ano": _r(m.dias_chuva_forte),
                        "maior_seq_seca_media_dias": _r(m.maior_seq_seca_dias),
                    }
                )
                for m in c.meses
            ]
            tipo, periodo, fonte = "media_historica", c.periodo, c.fonte
            extra = {"limite_chuva_forte_mm": _r(c.limite_chuva_forte_mm), "elevacao_m": _r(c.elevacao_m, 0), "notas": c.notas}
            aviso = "Média histórica por mês (média entre os anos). Não é previsão do tempo."
        else:
            a = self.clima.ano(celula, int(ano))
            if not a.meses:
                return Resultado({"erro": f"Não há dado de clima de {int(ano)} para este local. Diga isso."})
            meses = [
                _poda(
                    {
                        "mes": m.mes,
                        "chuva_mm": _r(m.chuva_mm),
                        "et0_mm": _r(m.et0_mm),
                        "tmed_c": _r(m.tmed_c),
                        "tmax_media_c": _r(m.tmax_media_c),
                        "tmin_media_c": _r(m.tmin_media_c),
                        "tmax_maxima_c": _r(m.tmax_absoluta_c),
                        "tmin_minima_c": _r(m.tmin_absoluta_c),
                        "dias_geada": m.dias_geada,
                        "dias_calor": m.dias_calor,
                        "dias_chuva_forte": m.dias_chuva_forte,
                        "maior_seq_seca_dias": m.maior_seq_seca_dias,
                        "dias_validos": m.dias_validos,
                    }
                )
                for m in a.meses
            ]
            tipo, periodo, fonte = "ano", a.periodo, a.fonte
            extra = {"limite_chuva_forte_mm": _r(celula.limite_chuva_forte_mm), "notas": a.notas}
            aviso = f"Dados observados de {int(ano)}. Não é previsão."
        dados = {
            "tipo": tipo,
            "fonte": "NASA POWER",
            "periodo": periodo,
            "escala": "célula de ~50 km (não é a medida exata do campo)",
            "aviso": aviso,
            "definicoes": {
                "geada": f"dia com temperatura mínima do ar abaixo de {TMIN_GEADA_C:g} °C (risco de geada, não geada confirmada)",
                "dia_seco": f"menos de {CHUVA_DIA_SECO_MM:g} mm de chuva; veranico = 10 dias secos seguidos ou mais",
                "calor": f"temperatura máxima acima de {TMAX_CALOR_C:g} °C",
                "chuva_forte": "dia com chuva acima do percentil 95 dos dias de chuva de 1991–2020",
            },
            **extra,
            "meses": meses,
        }
        detalhe = fonte.removeprefix("NASA POWER, ")  # período e escala, como vêm do serviço
        return Resultado(_poda(dados), [Fonte(tipo="clima", titulo="NASA POWER", detalhe=detalhe)])

    # --- 5. comparação de rotações ---

    def comparar_estrategias(self) -> Resultado:
        f: Fazenda | None = self.usuario.fazenda
        if f is None:
            return Resultado({"erro": "sem_fazenda", "mensagem": "O produtor ainda não preencheu a ficha da fazenda. Diga isso."})
        try:
            analise = self.motor.analisar(f)
        except ErroDeNegocio as e:  # falta local, culturas da região ou calendário
            return Resultado({"erro": "sem_comparacao", "mensagem": f"{e.mensagem} Diga isso ao produtor."})
        except ErroNasaPower:
            return Resultado({"erro": "Não consegui o clima do NASA POWER agora. Diga isso ao produtor, sem inventar números."})
        analise = replace(analise, fontes=[_CENTRO_DA_CELULA.sub("", s) for s in analise.fontes])
        detalhe = _corta("; ".join(analise.fontes), 250)
        return Resultado(_poda(_analise_compacta(analise)), [Fonte(tipo="analise", titulo=FONTE_ANALISE, detalhe=detalhe)])


def _sintese_compacta(sintese: list[dict] | None) -> list[dict]:
    """Textura, matéria orgânica e acidez já fundidas (valor, confiança, de onde veio e a divergência); o mapa global vem como "soilgrids"."""
    return [
        {
            "atributo": a.get("atributo"),
            "valor": a.get("valor"),
            "confianca": a.get("confianca"),
            "evidencias": [{k: e.get(k) for k in ("fonte", "valor", "texto")} for e in a.get("evidencias") or []],
            "divergencia": a.get("divergencia"),
        }
        for a in sintese or []
    ]


def _pontos(v: float | None) -> int | None:
    return None if v is None else round(v * 100)


def _estrategia_compacta(r: ResultadoEstrategia) -> dict:
    return {
        "nome": r.estrategia.nome,
        "itens": [
            {"cultura": _nome_da_cultura(i.cultura_id, i.texto), "inicio_mes": i.inicio_mes, "fim_mes": i.fim_mes, "perene": i.perene or None}
            for i in r.estrategia.itens
        ],
        "nota_final_0_a_100": _pontos(r.nota_final),
        "notas_0_a_100": {c: _pontos(n.nota) for c, n in r.notas.items()},
        "por_que": r.por_que,
        "onde_piora": r.onde_piora,
        "alertas": [a.texto for a in r.alertas],
        "confianca": r.confianca,
    }


def _nome_da_cultura(cultura_id: str | None, texto: str) -> str:
    item = catalogo.culturas().get(cultura_id) if cultura_id else None
    return catalogo.nome_exibicao(item).lower() if item else texto


def _analise_compacta(a: Analise) -> dict:
    motivos = Counter(m for e in a.eliminadas for m in e.motivos).most_common(MAX_MOTIVOS_ELIMINADAS)
    return {
        "aviso": "Comparação calculada pelo AgroIA, não é decisão: o produtor confirma com o técnico e a cooperativa. Notas de 0 a 100; use só estes números.",
        "atual": _estrategia_compacta(a.atual),
        "melhores": [_estrategia_compacta(r) for r in a.melhores],
        "atual_e_a_melhor": a.atual_e_a_melhor,
        "eliminadas": {"quantas": len(a.eliminadas), "motivos_mais_comuns": [m for m, _ in motivos]},
        "pesos_das_prioridades_0_a_100": {c: _pontos(p) for c, p in a.pesos.items()},
        "fontes": a.fontes,
    }
