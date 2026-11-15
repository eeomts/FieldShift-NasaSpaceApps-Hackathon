"""Satélite da fazenda (SMAP, MODIS, IMERG) com o Earthdata e o NASA POWER simulados (sem rede)."""
from datetime import date, timedelta

import httpx
import pytest

from app.main import app
from app.services.integracao import earthdata
from app.services.integracao.earthdata import ClienteEarthdata, ErroEarthdata, Granulo, interpretar_csv_dap
from app.services.integracao.nasa_power import get_cliente as get_power
from app.services.satelite import grade
from app.services.satelite.satelite_service import (
    FONTE_IMERG,
    FONTE_POWER,
    AVISO_IMERG_BLOQUEADO,
    SEM_ARQUIVO,
    SEM_TOKEN,
    SateliteService,
    limpar_cache,
    situacao_ndvi,
    situacao_umidade,
)
from test_chat import IRECE, ClienteFalso

HOJE = date(2026, 11, 15)
SUP, RAIZ = "/Geophysical_Data/sm_surface", "/Geophysical_Data/sm_rootzone"
NDVI = "/MODIS_Grid_16DAY_250m_500m_VI/Data_Fields/_250m_16_days_NDVI"
CONF = "/MODIS_Grid_16DAY_250m_500m_VI/Data_Fields/_250m_16_days_pixel_reliability"


@pytest.fixture(autouse=True)
def cache_limpo():
    limpar_cache()
    yield
    limpar_cache()


def janela3(centro, vizinho=None):
    v = centro if vizinho is None else vizinho
    return [[v, v, v], [v, centro, v], [v, v, v]]


class EarthdataFalso:
    """Granulos e recortes sintéticos. `bloquear` = produtos que respondem 'sem permissão'."""

    def __init__(self, token="tok", bloquear=(), raiz_hoje=0.20, nuvem_no_centro=False, sem_smap=False):
        self.token = token
        self.bloquear = set(bloquear)
        self.raiz_hoje = raiz_hoje
        self.nuvem_no_centro = nuvem_no_centro
        self.sem_smap = sem_smap
        self.recortes = 0

    @property
    def tem_token(self):
        return bool(self.token)

    def granulos(self, nome, inicio, fim, versao=None, ponto=None, limite=50, mais_recentes_primeiro=True):
        if nome == "SPL4SMGP":
            return [] if self.sem_smap else [Granulo(f"SMAP_{fim}", fim, f"smap/{fim.year}")]
        if nome == "MOD13Q1":
            tile = grade.pixel_modis(*ponto).tile
            return [Granulo(f"MOD13Q1.A.{tile}.061", HOJE - timedelta(days=16 * k), f"modis/{k}") for k in range(5)]
        if nome == "GPM_3IMERGDL":
            return [Granulo("IMERG", HOJE - timedelta(days=k), f"imerg/{k}") for k in range(1, 31)]
        raise AssertionError(nome)

    def recorte(self, url, variaveis):
        self.recortes += 1
        produto = url.split("/")[0]
        if produto in self.bloquear:
            raise ErroEarthdata("recusado", sem_permissao=True)
        if produto == "smap":
            ano = int(url.split("/")[1])
            raiz = self.raiz_hoje if ano == HOJE.year else 0.30 + 0.01 * (ano % 3)
            return {v: janela3(0.25 if v == SUP else raiz) for v in variaveis}
        if produto == "modis":
            k = int(url.split("/")[1])
            nd = janela3(-3000 if self.nuvem_no_centro else 7000 - 1000 * k, 5000)
            cf = janela3(3 if self.nuvem_no_centro else 0, 0)
            return {NDVI: nd, CONF: cf}
        if produto == "imerg":
            k = int(url.split("/")[1])
            return {"/precipitation": janela3(float(k % 5))}
        raise AssertionError(url)


def servico(cliente=None, power=None) -> SateliteService:
    s = SateliteService(cliente or EarthdataFalso(), power or ClienteFalso())
    s.hoje = lambda: HOJE
    return s


# --- grades -----------------------------------------------------------------------


def test_pixel_modis_do_cerrado_bate_com_o_conferido_na_nasa():
    px = grade.pixel_modis(-15.6, -47.7)
    assert (px.tile, px.linha, px.coluna) == ("h13v10", 2687, 1947)


def test_celula_smap_bate_com_cell_lat_lon_do_arquivo():
    # conferido no OPeNDAP: cell_lat[1030][1417] = -15.6161, cell_lon = -47.6608
    assert grade.celula_ease2_9km(-15.6, -47.7) == (1030, 1417)


def test_celula_imerg_nas_bordas():
    assert grade.celula_imerg(-89.95, -179.95) == (0, 0)
    assert grade.celula_imerg(89.99, 179.99) == (3599, 1799)
    assert grade.celula_imerg(-15.62, -47.73) == (1322, 743)  # centros -47,75 e -15,65


def test_janela_nao_sai_da_grade():
    assert grade.janela(0, 10) == (0, 1, 0)
    assert grade.janela(9, 10) == (8, 9, 1)
    assert grade.janela(5, 10) == (4, 6, 1)


# --- cliente --------------------------------------------------------------------------


def test_csv_do_opendap_vira_linhas_e_preenchimento_vira_none():
    texto = "Dataset: x.h5\n/G/sm[0], 0.2, -9999, 0.3\n/G/sm[1], 0.1, 0.2, nan\n"
    assert interpretar_csv_dap(texto, ["/G/sm"]) == {"/G/sm": [[0.2, None, 0.3], [0.1, 0.2, None]]}
    with pytest.raises(ErroEarthdata):
        interpretar_csv_dap(texto, ["/G/outra"])


def test_recorte_manda_o_token_so_no_cabecalho():
    pedidos = []

    def responder(request):
        pedidos.append(request)
        return httpx.Response(200, text="Dataset: a\n/v[0], 1, 2\n")

    c = ClienteEarthdata(token="segredo", http=httpx.Client(transport=httpx.MockTransport(responder)))
    assert c.recorte("https://opendap.earthdata.nasa.gov/g", {"/v": "[0:0][0:1]"}) == {"/v": [[1.0, 2.0]]}
    assert pedidos[0].headers["Authorization"] == "Bearer segredo"
    assert "segredo" not in str(pedidos[0].url)


def test_erro_403_dentro_do_corpo_do_opendap_vira_sem_permissao():
    corpo = 'Dataset: a\nError {\n    code = 403;\n    message = "redirect";\n}'
    c = ClienteEarthdata(token="t", http=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, text=corpo))))
    with pytest.raises(ErroEarthdata) as e:
        c.recorte("https://opendap.earthdata.nasa.gov/g", {"/v": "[0]"})
    assert e.value.sem_permissao


def test_sem_token_nem_chama_a_rede():
    c = ClienteEarthdata(token=None, http=httpx.Client(transport=httpx.MockTransport(lambda r: pytest.fail("chamou a rede"))))
    with pytest.raises(ErroEarthdata) as e:
        c.recorte("https://opendap.earthdata.nasa.gov/g", {"/v": "[0]"})
    assert e.value.sem_permissao


def test_cmr_so_devolve_granulos_com_opendap():
    feed = {"feed": {"entry": [
        {"title": "a", "time_start": "2026-11-10T00:00:00.000Z", "links": [{"href": "https://opendap.earthdata.nasa.gov/collections/C1/granules/a"}]},
        {"title": "b", "time_start": "2026-11-09T00:00:00.000Z", "links": [{"href": "s3://bucket/b"}]},
    ]}}  # fmt: skip
    c = ClienteEarthdata(token=None, http=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=feed))))
    gs = c.granulos("X", date(2026, 11, 1), date(2026, 11, 10))
    assert [(g.titulo, g.data) for g in gs] == [("a", date(2026, 11, 10))]


# --- regras -------------------------------------------------------------------------


def test_situacoes():
    assert situacao_ndvi(0.1) == "descoberto" and situacao_ndvi(0.3) == "pouco"
    assert situacao_ndvi(0.5) == "verde" and situacao_ndvi(0.8) == "muito"
    assert situacao_umidade(0.2, [0.3, 0.31, 0.32])[0] == "seco"
    assert situacao_umidade(0.4, [0.3, 0.31, 0.32])[0] == "umido"
    assert situacao_umidade(0.31, [0.3, 0.31, 0.32])[0] == "normal"
    assert situacao_umidade(0.2, [0.3, 0.31]) == (None, None, None)  # pouco histórico: não julga


# --- serviço ---------------------------------------------------------------------------


def test_tudo_certo_com_imerg():
    r = servico().obter(-15.6, -47.7)
    assert r.faltas == {} and r.avisos == []
    u = r.umidade
    assert u.raiz == 0.2 and u.superficie == 0.25 and u.situacao == "seco" and u.posicao == 0.0
    assert u.anos_comparados == 8 and u.data == HOJE
    assert r.ndvi.valor == 0.7 and r.ndvi.situacao == "muito" and len(r.ndvi.serie) == 5
    assert [p.data for p in r.ndvi.serie] == sorted(p.data for p in r.ndvi.serie)
    c = r.chuva
    assert c.fonte == FONTE_IMERG and len(c.dias) == 30 and c.dias[-1].data == HOJE - timedelta(days=1)
    assert c.total_30d == sum(float(k % 5) for k in range(1, 31)) and c.maior.mm == 4.0


def test_imerg_bloqueado_usa_o_power_e_avisa():
    r = servico(EarthdataFalso(bloquear={"imerg"})).obter(-15.6, -47.7)
    assert r.chuva.fonte == FONTE_POWER and r.avisos == [AVISO_IMERG_BLOQUEADO]
    assert len(r.chuva.dias) == 30 and r.umidade is not None and r.ndvi is not None


def test_imerg_bloqueado_tenta_um_arquivo_so():
    cliente = EarthdataFalso(bloquear={"imerg", "smap", "modis"})
    servico(cliente).obter(-15.6, -47.7)
    assert cliente.recortes <= 1 + 1 + 1 + 4  # 1 IMERG, 1 SMAP, MODIS falha no 1º de cada thread


def test_sem_token_mostra_o_motivo_e_a_chuva_do_power():
    r = servico(EarthdataFalso(token=None, bloquear={"smap", "modis"})).obter(-15.6, -47.7)
    assert r.faltas == {"umidade": SEM_TOKEN, "ndvi": SEM_TOKEN}
    assert r.chuva.fonte == FONTE_POWER and r.avisos == []


def test_nuvem_no_centro_usa_a_mediana_dos_vizinhos():
    r = servico(EarthdataFalso(nuvem_no_centro=True)).obter(-15.6, -47.7)
    assert {p.valor for p in r.ndvi.serie} == {0.5}


def test_uma_parte_falha_e_as_outras_aparecem():
    r = servico(EarthdataFalso(sem_smap=True)).obter(-15.6, -47.7)
    assert r.umidade is None and r.faltas["umidade"] == SEM_ARQUIVO
    assert r.ndvi is not None and r.chuva is not None


def test_cache_evita_nova_consulta_no_mesmo_dia():
    cliente = EarthdataFalso()
    servico(cliente).obter(-15.6, -47.7)
    antes = cliente.recortes
    servico(cliente).obter(-15.6, -47.7)
    assert cliente.recortes == antes


# --- rota ---------------------------------------------------------------------------------


@pytest.fixture
def externos():
    app.dependency_overrides[earthdata.get_cliente] = lambda: EarthdataFalso()
    app.dependency_overrides[get_power] = lambda: ClienteFalso()
    yield
    app.dependency_overrides.clear()


def test_rota_exige_login(client):
    assert client.get("/fazenda/satelite").status_code == 401


def test_rota_sem_fazenda_e_sem_ponto(client, auth, externos):
    assert client.get("/fazenda/satelite", headers=auth).status_code == 404
    client.put("/fazenda", headers=auth, json={"respostas": {"q1_quem": "produtor"}})
    assert client.get("/fazenda/satelite", headers=auth).status_code == 422


def test_rota_no_formato_do_contrato(client, auth, externos):
    assert client.put("/fazenda", headers=auth, json={"respostas": IRECE}).status_code == 200
    r = client.get("/fazenda/satelite", headers=auth)
    assert r.status_code == 200
    c = r.json()
    assert set(c) == {"lat", "lon", "umidade", "ndvi", "chuva", "faltas", "avisos", "gerado_em"}
    assert c["lat"] == IRECE["q5_local"]["lat"] and c["faltas"] == {}
    assert c["umidade"]["situacao"] in ("seco", "normal", "umido") and c["ndvi"]["serie"]
    assert c["chuva"]["fonte"] == FONTE_IMERG and len(c["chuva"]["dias"]) == 30
    assert c["gerado_em"].endswith(("Z", "+00:00"))
