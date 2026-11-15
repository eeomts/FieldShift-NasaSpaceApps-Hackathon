"""Reúne o que o motor precisa de uma fazenda: catálogo, rotação atual, clima da célula, relevo e restrições."""
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from app.core.erros import ErroDeNegocio
from app.models import Fazenda
from app.services.clima.agregacao import LinhaMensal
from app.services.clima.clima_service import ClimaService, media_por_mes
from app.services.clima.graus_dia import TB_MAX, TB_MIN
from app.services.clima.limiares import BASE_FIM, BASE_INICIO
from app.services.motor.catalogo import CulturaMotor, catalogo_do_pais, equipamentos_por_cultura
from app.services.motor.estados import estado_do_local
from app.services.motor.local import pais_e_codigo
from app.services.motor.modelo import ItemRotacao
from app.services.motor.relevo_service import Relevo
from app.services.onboarding.perfil import meses_sem_cobertura

MSG_SEM_LOCAL = "Marque o local da fazenda para comparar rotações."
MSG_PAIS = "Ainda só comparamos rotações no Brasil e nos Estados Unidos; o local da fazenda está fora deles."
MSG_SEM_CATALOGO = "Ainda não temos as culturas desta região na base."
MSG_SEM_ROTACAO = "Cadastre o que você planta para comparar rotações."


@dataclass
class ClimaDoLocal:
    """Clima da célula pronto para o motor. Mês sem dado = None (nunca 0)."""

    fonte: str
    periodo: str
    chuva_mm: dict[int, float | None]  # média 1991–2020 por mês (1..12)
    et0_mm: dict[int, float | None]
    dias_chuva_forte: dict[int, float | None]  # média de dias por ano
    geada_por_ano: dict[int, dict[int, int | None]]  # ano -> mês -> dias de geada (1991–2020)
    gd_por_tb_medio: dict[int, dict[str, float]]  # mês -> Tb inteira ("0".."20") -> GD médio 1991–2020


def clima_de_linhas(linhas: list[LinhaMensal], fonte: str, periodo: str) -> ClimaDoLocal:
    """Monta o clima a partir das linhas (ano, mês) da célula: climatologia, geada por ano e GD médio por Tb."""
    meses = {m.mes: m for m in media_por_mes(linhas)}
    base = [l for l in linhas if BASE_INICIO <= l.ano <= BASE_FIM]
    geada: dict[int, dict[int, int | None]] = {}
    for l in base:
        geada.setdefault(l.ano, {})[l.mes] = l.dias_geada
    gd: dict[int, dict[str, float]] = {}
    for mes in range(1, 13):
        do_mes = [l.gd_por_tb for l in base if l.mes == mes and l.gd_por_tb]  # {} e None: mês sem temperatura completa
        if do_mes:
            gd[mes] = {str(tb): sum(d[str(tb)] for d in do_mes) / len(do_mes) for tb in range(TB_MIN, TB_MAX + 1)}
    return ClimaDoLocal(
        fonte=fonte,
        periodo=periodo,
        chuva_mm={m: meses[m].chuva_mm for m in range(1, 13)},
        et0_mm={m: meses[m].et0_mm for m in range(1, 13)},
        dias_chuva_forte={m: meses[m].dias_chuva_forte for m in range(1, 13)},
        geada_por_ano=geada,
        gd_por_tb_medio=gd,
    )


class FonteClima(Protocol):
    def do_local(self, lat: float, lon: float) -> ClimaDoLocal: ...


class FonteRelevo(Protocol):
    def declividade_da_fazenda(self, f: Fazenda) -> Relevo | None: ...


class ClimaDoServico:
    """FonteClima real: célula do NASA POWER (baixa se faltar) e agregados do motor."""

    def __init__(self, clima: ClimaService):
        self.clima = clima

    def do_local(self, lat: float, lon: float) -> ClimaDoLocal:
        celula = self.clima.obter(lat, lon)
        climatologia = self.clima.climatologia(celula)
        return clima_de_linhas(self.clima.linhas(celula), climatologia.fonte, climatologia.periodo)


@dataclass
class EntradasMotor:
    pais: str
    catalogo: dict[str, CulturaMotor]
    atual: tuple[ItemRotacao, ...]
    meses_vazios: list[int]
    clima: ClimaDoLocal
    relevo: Relevo | None
    irrigacao: str | None  # sim | parte | nao | None
    excluidas: frozenset[str] = frozenset()
    equipamentos: frozenset[str] | None = None  # None = não respondeu (não filtra)
    equipamentos_cultura: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    prioridades: list[str] = field(default_factory=list)
    estado: str | None = None  # UF ou sigla USPS da fazenda; None = não sabemos (regra 13 não filtra)


def rotacao_atual(f: Fazenda) -> tuple[ItemRotacao, ...]:
    return tuple(
        ItemRotacao(c.cultura_id, c.inicio_mes, c.fim_mes, bool(c.perene), c.texto_original) for c in f.calendario
    )


def montar_entradas(
    f: Fazenda,
    fonte_clima: FonteClima,
    fonte_relevo: FonteRelevo,
    catalogo_por_pais: Callable[[str], dict[str, CulturaMotor]] = catalogo_do_pais,
    equipamentos: dict[str, dict[str, set[str]]] | None = None,
) -> EntradasMotor:
    """Entradas do motor para a fazenda. Sem local, país fora de BR/US, catálogo vazio ou calendário vazio: erro de negócio."""
    if f.lat is None or f.lon is None:
        raise ErroDeNegocio(422, MSG_SEM_LOCAL)
    pais, codigo_local = (f.pais, f.codigo_local) if f.pais else pais_e_codigo(f.lat, f.lon)
    if pais not in ("BR", "US"):
        raise ErroDeNegocio(422, MSG_PAIS)
    catalogo = catalogo_por_pais(pais)
    if not catalogo:
        raise ErroDeNegocio(422, MSG_SEM_CATALOGO)
    atual = rotacao_atual(f)
    if not atual:
        raise ErroDeNegocio(422, MSG_SEM_ROTACAO)
    ids_equipamentos = frozenset(e["equipamento_id"] for e in (f.equipamentos or []) if e.get("equipamento_id"))
    return EntradasMotor(
        pais=pais,
        catalogo=catalogo,
        atual=atual,
        meses_vazios=meses_sem_cobertura(list(atual)),  # ItemRotacao tem os mesmos campos de ItemCalendario
        clima=fonte_clima.do_local(f.lat, f.lon),
        relevo=fonte_relevo.declividade_da_fazenda(f),
        irrigacao=f.irrigacao,
        excluidas=frozenset(c["cultura_id"] for c in (f.culturas_excluidas or []) if c.get("cultura_id")),
        equipamentos=ids_equipamentos or None,
        equipamentos_cultura=equipamentos if equipamentos is not None else equipamentos_por_cultura(),
        prioridades=list(f.prioridades or []),
        estado=estado_do_local(pais, codigo_local),
    )
