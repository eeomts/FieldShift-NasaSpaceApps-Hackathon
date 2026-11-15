"""Solo de um ponto: cache por propriedade (retoma de onde parou), resultado parcial, "sem dado" e derivados (cliente falso, sem rede)."""
import pytest
from sqlalchemy.orm import Session

from app.core.db import get_engine
from app.core.erros import ErroDeNegocio
from app.models import SoloPontoCache
from app.repositories.solo_repository import SoloRepository
from app.services.integracao.soilgrids import PROPRIEDADES
from app.services.solo.solo_service import SoloService, chave_do_ponto, utilizavel
from solo_helpers import ERRO, ClienteFalso, resposta_urbana

LAT, LON = -17.644301, -51.080503


@pytest.fixture
def db():
    with Session(get_engine(), expire_on_commit=False) as s:
        yield s


def servico(db, resposta=None, falhas=()) -> tuple[SoloService, ClienteFalso]:
    cliente = ClienteFalso(resposta, falhas)
    return SoloService(SoloRepository(db), cliente), cliente


def guardadas(db) -> set[str]:
    return {l.propriedade for l in db.query(SoloPontoCache).all()}


def test_chave_com_3_casas():
    assert chave_do_ponto(LAT, LON) == "-17.644_-51.081"


def test_pede_na_ordem_textura_primeiro_e_deriva_os_numeros(db):
    s, cliente = servico(db)
    p = s.obter(LAT, LON)
    assert cliente.pedidas() == ["clay", "sand", "silt", "soc", "phh2o", "bdod", "cec"] == list(PROPRIEDADES)
    assert (p.argila_pct, p.areia_pct, p.silte_pct) == (40.0, 40.0, 20.0)
    assert p.carbono_g_kg == 20.0 and p.materia_organica_g_kg == pytest.approx(34.48)  # carbono × 1,724
    assert p.ph == 5.5 and p.ctc_cmol_kg == 10.0 and p.densidade_g_cm3 == 1.2
    assert p.classe_textural == "argilosa" and p.k_usle == pytest.approx(0.0145, abs=1e-4)
    assert p.camada == "0–30 cm" and p.fonte == "SoilGrids 2.0 (ISRIC), 250 m" and p.sem_dado is False
    assert p.incerteza["argila_pct"] == pytest.approx(1.5)  # (70 − 10) ÷ 40
    assert utilizavel(p)


def test_guarda_cada_propriedade_e_a_segunda_vez_nao_chama_a_api(db):
    s, cliente = servico(db)
    p1 = s.obter(LAT, LON)
    assert guardadas(db) == set(PROPRIEDADES)
    p2 = s.obter(LAT, LON)
    assert len(cliente.chamadas) == 7
    assert p2 == p1  # o que vem do cache é igual ao que veio da API


def test_pontos_vizinhos_dividem_a_mesma_linha(db):
    s, cliente = servico(db)
    s.obter(LAT, LON)
    s.obter(LAT + 0.0001, LON - 0.0001)  # ~11 m depois: mesma chave de 3 casas
    assert len(cliente.pontos) == 1


def test_falha_numa_propriedade_nao_derruba_as_outras_e_o_resultado_e_parcial(db):
    s, cliente = servico(db, falhas={"soc"})
    p = s.obter(LAT, LON)
    assert cliente.pedidas() == list(PROPRIEDADES)  # seguiu para as outras depois da falha
    assert guardadas(db) == set(PROPRIEDADES) - {"soc"}
    assert p.argila_pct == 40.0 and p.classe_textural == "argilosa" and p.ph == 5.5 and p.ctc_cmol_kg == 10.0
    assert p.carbono_g_kg is None and p.materia_organica_g_kg is None and p.k_usle is None  # o que falta é None, nunca 0
    assert p.incerteza["carbono_g_kg"] is None
    assert utilizavel(p)  # tem a textura


def test_retoma_de_onde_parou_so_pede_o_que_falta(db):
    s, cliente = servico(db, falhas={"soc", "cec"})
    s.obter(LAT, LON)
    cliente.falhas.clear()
    cliente.chamadas.clear()
    p = s.obter(LAT, LON)
    assert cliente.pedidas() == ["soc", "cec"]
    assert p.carbono_g_kg == 20.0 and p.k_usle == pytest.approx(0.0145, abs=1e-4) and p.ctc_cmol_kg == 10.0
    assert guardadas(db) == set(PROPRIEDADES)
    cliente.chamadas.clear()
    s.obter(LAT, LON)
    assert cliente.chamadas == []


def test_sem_a_textura_o_ponto_nao_e_utilizavel_mas_guarda_o_que_veio(db):
    s, _ = servico(db, falhas={"clay"})
    p = s.obter(LAT, LON)
    assert p.argila_pct is None and p.classe_textural is None and p.k_usle is None
    assert p.ph == 5.5 and p.carbono_g_kg == 20.0
    assert not utilizavel(p)
    assert "clay" not in guardadas(db) and "phh2o" in guardadas(db)


def test_duas_falhas_seguidas_encerram_a_busca(db):
    s, cliente = servico(db, falhas={"clay", "sand", "silt", "soc"})
    assert s.obter(LAT, LON) is None  # nada veio e nada estava guardado
    assert cliente.pedidas() == ["clay", "sand"]
    assert guardadas(db) == set()


def test_servico_fora_do_ar_devolve_none_e_nao_guarda_e_depois_tenta_de_novo(db):
    s, cliente = servico(db, ERRO)
    assert s.obter(LAT, LON) is None
    assert guardadas(db) == set()
    cliente.resposta = ClienteFalso().resposta  # voltou ao ar
    assert s.obter(LAT, LON).argila_pct == 40.0


def test_sem_dado_para_na_primeira_propriedade_e_tambem_e_guardado(db):
    s, cliente = servico(db, resposta_urbana())
    p = s.obter(-23.5505, -46.6333)
    assert p.sem_dado is True and p.argila_pct is None and p.k_usle is None and p.classe_textural is None
    assert utilizavel(p)
    assert cliente.pedidas() == ["clay"]  # o resto também seria nulo: nem pede
    assert s.obter(-23.5505, -46.6333).sem_dado is True
    assert len(cliente.chamadas) == 1  # não chama de novo
    assert all(l.sem_dado and l.superficial is None for l in db.query(SoloPontoCache).all())


def test_coordenada_fora_do_mundo_e_erro_de_negocio(db):
    s, cliente = servico(db)
    with pytest.raises(ErroDeNegocio):
        s.obter(95.0, 10.0)
    assert cliente.chamadas == []


def test_a_conexao_com_o_banco_e_liberada_antes_da_chamada_lenta(db):
    estados = []

    class Espiao(ClienteFalso):
        def propriedade(self, lat, lon, nome):
            estados.append(db.in_transaction())  # transação aberta = conexão presa durante a espera pelo SoilGrids
            return super().propriedade(lat, lon, nome)

    SoloService(SoloRepository(db), Espiao()).obter(LAT, LON)
    assert set(estados) == {False}
