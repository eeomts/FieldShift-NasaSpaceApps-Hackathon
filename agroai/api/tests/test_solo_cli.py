"""Pré-carga do solo (python -m app.cli.solo): CSV pequeno, cache parcial e retomada (cliente falso, sem rede)."""
import pytest
from sqlalchemy.orm import Session

from app.cli import solo as cli
from app.core.db import get_engine
from app.models import SoloPontoCache
from app.repositories.solo_repository import SoloRepository
from app.services.solo.solo_service import SoloService
from solo_helpers import ClienteFalso, resposta_urbana

CABECALHO = "id,regiao,municipio,uf,latitude,longitude,rotacao_atual,historia,soilgrids_ok\n"


@pytest.fixture
def db():
    with Session(get_engine(), expire_on_commit=False) as s:
        yield s


@pytest.fixture
def csvs(tmp_path):
    br = tmp_path / "pontos_demo.csv"
    br.write_text(CABECALHO + 'a,Cerrado,Rio Verde,GO,-17.644301,-51.080503,"soja","hist",true\nb,Sul,Passo Fundo,RS,-28.310532,-52.412854,"soja","hist",true\n', encoding="utf-8")
    eua = tmp_path / "pontos_demo_eua.csv"
    eua.write_text(CABECALHO + 'c,Corn Belt,Story County,IA,42.070000,-93.450000,"milho","hist",true\n', encoding="utf-8")
    return br, eua


def servico(db, cliente) -> SoloService:
    return SoloService(SoloRepository(db), cliente)


def test_le_os_pontos_dos_dois_csvs_e_pula_arquivo_que_nao_existe(csvs, tmp_path):
    pontos = cli.ler_pontos([*csvs, tmp_path / "nao_existe.csv"])
    assert pontos == [("Rio Verde-GO", -17.644301, -51.080503), ("Passo Fundo-RS", -28.310532, -52.412854), ("Story County-IA", 42.07, -93.45)]


def test_os_csvs_da_demo_do_repositorio_sao_lidos():
    pontos = cli.ler_pontos(cli.PONTOS_DEMO)
    assert len(pontos) >= 3 and any(n.endswith("-GO") for n, _, _ in pontos) and any(n.endswith("-IA") for n, _, _ in pontos)


def test_demo_guarda_todos_os_pontos(db, csvs):
    cliente = ClienteFalso()
    saidas: list[str] = []
    resultado = cli.baixar_pontos(cli.ler_pontos(csvs), servico(db, cliente), saidas.append)
    assert resultado == {"Rio Verde-GO": "completo", "Passo Fundo-RS": "completo", "Story County-IA": "completo"}
    assert len(cliente.pontos) == 3 and len(db.query(SoloPontoCache).all()) == 21
    assert saidas[0].startswith("Rio Verde-GO (-17.6443, -51.0805): completo (argilosa, K 0.0145)")


def test_retoma_de_onde_parou_e_nao_repete_o_que_ja_esta_no_cache(db, csvs):
    pontos = cli.ler_pontos(csvs)
    cliente = ClienteFalso(falhas={"cec"})
    saidas: list[str] = []
    assert set(cli.baixar_pontos(pontos, servico(db, cliente), saidas.append).values()) == {"parcial"}
    assert "faltam cec" in saidas[0]
    cliente.falhas.clear()
    cliente.chamadas.clear()
    assert set(cli.baixar_pontos(pontos, servico(db, cliente), saidas.append).values()) == {"completo"}
    assert cliente.pedidas() == ["cec"] * 3  # só a propriedade que faltou, em cada ponto
    cliente.chamadas.clear()
    cli.baixar_pontos(pontos, servico(db, cliente), saidas.append)
    assert cliente.chamadas == []


def test_ponto_urbano_e_servico_fora_do_ar_aparecem_no_resultado(db, csvs):
    pontos = cli.ler_pontos(csvs)[:1]
    assert cli.baixar_pontos(pontos, servico(db, ClienteFalso(resposta_urbana())), lambda _: None) == {"Rio Verde-GO": "sem dado"}
    pontos = cli.ler_pontos(csvs)[1:2]
    assert cli.baixar_pontos(pontos, servico(db, ClienteFalso(falhas={"clay", "sand"})), lambda _: None) == {"Passo Fundo-RS": "falhou"}
