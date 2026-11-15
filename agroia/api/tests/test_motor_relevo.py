"""Declividade da fazenda: SRTM com cache no banco e a resposta q7 como reserva (cliente simulado, sem rede)."""
import pytest
from sqlalchemy.orm import Session

from app.core.db import get_engine
from app.models import Fazenda, RelevoPonto
from app.repositories.relevo_repository import RelevoRepository
from app.services.integracao.srtm import Declividade, ErroSrtm
from app.services.motor.relevo_service import FONTE_Q7, RelevoService, chave_do_ponto


class ClienteFalso:
    def __init__(self, resposta: Declividade | Exception):
        self.resposta = resposta
        self.chamadas: list[tuple[float, float]] = []

    def declividade(self, lat, lon) -> Declividade:
        self.chamadas.append((lat, lon))
        if isinstance(self.resposta, Exception):
            raise self.resposta
        return self.resposta


@pytest.fixture
def db():
    with Session(get_engine(), expire_on_commit=False) as s:
        yield s


SRTM = Declividade(percentual=12.3, classe="ondulado", fonte="SRTM 30 m (teste)")


def servico(db, resposta) -> tuple[RelevoService, ClienteFalso]:
    cliente = ClienteFalso(resposta)
    return RelevoService(RelevoRepository(db), cliente), cliente


def fazenda(terreno=None, lat=-17.644301, lon=-51.080503) -> Fazenda:
    return Fazenda(lat=lat, lon=lon, terreno=terreno)


def test_chave_com_4_casas():
    assert chave_do_ponto(-17.644301, -51.080503) == "-17.6443_-51.0805"


def test_srtm_e_guardado_e_a_segunda_vez_nao_chama_a_api(db):
    s, cliente = servico(db, SRTM)
    r1 = s.declividade_da_fazenda(fazenda("plano"))  # a resposta q7 não pesa quando o SRTM responde
    assert (r1.classe, r1.declividade_pct, r1.fonte) == ("ondulado", 12.3, "SRTM 30 m (teste)")
    r2 = s.declividade_da_fazenda(fazenda("plano"))
    assert r2 == r1 and len(cliente.chamadas) == 1
    assert db.get(RelevoPonto, "-17.6443_-51.0805").declividade_pct == 12.3


def test_pontos_a_menos_de_11_m_dividem_o_cache(db):
    s, cliente = servico(db, SRTM)
    s.declividade_da_fazenda(fazenda(lat=-17.644301, lon=-51.080503))
    s.declividade_da_fazenda(fazenda(lat=-17.644349, lon=-51.080496))
    assert len(cliente.chamadas) == 1
    s.declividade_da_fazenda(fazenda(lat=-17.6445, lon=-51.0805))
    assert len(cliente.chamadas) == 2


@pytest.mark.parametrize("q7, classe", [("plano", "plano"), ("leve", "suave_ondulado"), ("inclinado", "ondulado")])
def test_srtm_falhou_usa_a_resposta_q7_sem_pct_e_nao_guarda(db, q7, classe):
    s, cliente = servico(db, ErroSrtm("fora do ar"))
    r = s.declividade_da_fazenda(fazenda(q7))
    assert (r.classe, r.declividade_pct, r.fonte) == (classe, None, FONTE_Q7)
    assert db.get(RelevoPonto, chave_do_ponto(-17.644301, -51.080503)) is None
    s.declividade_da_fazenda(fazenda(q7))
    assert len(cliente.chamadas) == 2  # tenta o SRTM de novo na próxima vez


def test_sem_srtm_e_sem_q7_e_lacuna(db):
    s, _ = servico(db, ErroSrtm("mar"))
    assert s.declividade_da_fazenda(fazenda(None)) is None


def test_fazenda_sem_ponto_usa_q7_sem_chamar_a_api(db):
    s, cliente = servico(db, SRTM)
    r = s.declividade_da_fazenda(fazenda("leve", lat=None, lon=None))
    assert (r.classe, r.fonte) == ("suave_ondulado", FONTE_Q7) and cliente.chamadas == []
