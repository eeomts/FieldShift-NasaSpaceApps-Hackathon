"""Rotas /local/* e clientes Nominatim e POWER-climatologia, tudo com dublês (sem rede)."""
import json

import httpx
import pytest
from sqlalchemy import text

from app.core.db import get_engine
from app.main import app
from app.services.clima.celula import id_da_celula
from app.services.integracao import nominatim, power_climatologia
from app.services.integracao.nominatim import ClienteNominatim, ErroNominatim, get_nominatim
from app.services.integracao.power_climatologia import (
    ClimatologiaMensal,
    ClientePowerClimatologia,
    ErroPowerClimatologia,
    get_power_climatologia,
)

CHUVA_LEM = [5.0, 5.0, 5.5, 3.2, 0.8, 0.1, 0.01, 0.1, 0.3, 2.4, 5.3, 5.6]  # mm/dia (Aw no Sul)
TEMP_LEM = [24.3, 24.0, 24.2, 24.2, 24.3, 23.2, 22.8, 24.1, 26.4, 27.3, 25.4, 24.8]


@pytest.fixture(autouse=True)
def limpa(monkeypatch):
    nominatim._cache_busca.limpar()
    nominatim._cache_reverso.limpar()
    power_climatologia._cache.limpar()
    yield
    app.dependency_overrides.clear()


class NominatimFalso:
    def __init__(self, erro: bool = False, lugar: dict | None = None):
        self.erro, self.lugar, self.pedidos = erro, lugar, []

    def buscar(self, q, idioma, limite=5):
        self.pedidos.append(("buscar", q, idioma))
        if self.erro:
            raise ErroNominatim("fora do ar")
        return [{"nome": "Passo Fundo, Rio Grande do Sul", "pais": "Brasil", "pais_codigo": "BR", "lat": -28.25, "lon": -52.39}]

    def reverso(self, lat, lon, idioma):
        self.pedidos.append(("reverso", lat, lon, idioma))
        if self.erro:
            raise ErroNominatim("fora do ar")
        return self.lugar


class PowerFalso:
    def __init__(self, erro: bool = False, dados: ClimatologiaMensal | None = None):
        self.erro, self.pedidos = erro, []
        self.dados = dados or ClimatologiaMensal(temp_c=TEMP_LEM, chuva_mm_dia=CHUVA_LEM)

    def mensal(self, lat, lon):
        self.pedidos.append((lat, lon))
        if self.erro:
            raise ErroPowerClimatologia("fora do ar")
        return self.dados


def instala(nom=None, power=None):
    nom, power = nom or NominatimFalso(), power or PowerFalso()
    app.dependency_overrides[get_nominatim] = lambda: nom
    app.dependency_overrides[get_power_climatologia] = lambda: power
    return nom, power


LEM = {"nome": "Luís Eduardo Magalhães, Bahia", "pais": "Brasil", "pais_codigo": "BR"}


# --- rotas ---


def test_rotas_exigem_login(client):
    instala()
    assert client.get("/local/buscar?q=passo").status_code == 401
    assert client.get("/local/info?lat=-12&lon=-45").status_code == 401


def test_buscar(client, auth):
    nom, _ = instala()
    r = client.get("/local/buscar?q=Passo Fundo&idioma=en", headers=auth)
    assert r.status_code == 200
    assert r.json() == [{"nome": "Passo Fundo, Rio Grande do Sul", "pais": "Brasil", "pais_codigo": "BR", "lat": -28.25, "lon": -52.39}]
    assert nom.pedidos == [("buscar", "Passo Fundo", "en")]


def test_buscar_valida_entrada(client, auth):
    instala()
    assert client.get("/local/buscar?q=a", headers=auth).status_code == 422
    assert client.get(f"/local/buscar?q={'x' * 121}", headers=auth).status_code == 422
    assert client.get("/local/buscar", headers=auth).status_code == 422
    assert client.get("/local/buscar?q=passo&idioma=es", headers=auth).status_code == 422


def test_buscar_falha_devolve_lista_vazia(client, auth):
    instala(NominatimFalso(erro=True))
    r = client.get("/local/buscar?q=passo", headers=auth)
    assert r.status_code == 200 and r.json() == []


def test_info_completa_e_arredonda_o_ponto(client, auth):
    nom, power = instala(NominatimFalso(lugar=LEM))
    r = client.get("/local/info?lat=-12.1049&lon=-45.7851&idioma=pt", headers=auth)
    assert r.status_code == 200
    assert r.json() == {"hemisferio": "S", "zona_climatica": "Aw", "lugar": "Luís Eduardo Magalhães, Bahia",
                        "pais": "Brasil", "pais_codigo": "BR", "geada_no_historico": None}
    # os serviços externos só recebem o ponto arredondado a 2 casas
    assert power.pedidos == [(-12.1, -45.79)]
    assert nom.pedidos == [("reverso", -12.1, -45.79, "pt")]


def test_info_hemisferio_norte(client, auth):
    instala(NominatimFalso(lugar={"nome": "Ames, Iowa", "pais": "United States", "pais_codigo": "US"}))
    r = client.get("/local/info?lat=42.03&lon=-93.62&idioma=en", headers=auth)
    assert r.json()["hemisferio"] == "N" and r.json()["pais_codigo"] == "US"


def test_info_servicos_fora_do_ar_dao_campos_nulos(client, auth):
    instala(NominatimFalso(erro=True), PowerFalso(erro=True))
    r = client.get("/local/info?lat=-12.1&lon=-45.79", headers=auth)
    assert r.status_code == 200
    assert r.json() == {"hemisferio": "S", "zona_climatica": None, "lugar": None, "pais": None,
                        "pais_codigo": None, "geada_no_historico": None}


def test_info_mes_sem_dado_do_power_nao_inventa_zona(client, auth):
    sem_dado = ClimatologiaMensal(temp_c=[None] + TEMP_LEM[1:], chuva_mm_dia=CHUVA_LEM)
    instala(NominatimFalso(lugar=None), PowerFalso(dados=sem_dado))
    r = client.get("/local/info?lat=-12.1&lon=-45.79", headers=auth)
    assert r.json()["zona_climatica"] is None and r.json()["lugar"] is None


def test_info_valida_coordenadas(client, auth):
    instala()
    assert client.get("/local/info?lat=91&lon=0", headers=auth).status_code == 422
    assert client.get("/local/info?lat=0&lon=181", headers=auth).status_code == 422
    assert client.get("/local/info?lat=0", headers=auth).status_code == 422


def _guarda_clima(lat, lon, dias_geada: list[int | None]):
    celula = id_da_celula(lat, lon)
    with get_engine().begin() as c:
        c.execute(text("INSERT INTO clima_celula (id, lat, lon, inicio, fim, fonte) "
                       "VALUES (:i, :la, :lo, '1991-01-01', '2020-12-31', 'teste')"), {"i": celula, "la": lat, "lo": lon})
        for mes, d in enumerate(dias_geada, start=1):
            c.execute(text("INSERT INTO clima_mensal (celula_id, ano, mes, dias_geada) VALUES (:i, 2000, :m, :d)"),
                      {"i": celula, "m": mes, "d": d})


@pytest.mark.parametrize("dias,esperado", [([0] * 12, False), ([0] * 6 + [3] + [0] * 5, True), ([None] * 12, None)])
def test_info_geada_no_historico(client, auth, dias, esperado):
    instala(NominatimFalso(lugar=LEM))
    _guarda_clima(-12.1, -45.79, dias)
    assert client.get("/local/info?lat=-12.1&lon=-45.79", headers=auth).json()["geada_no_historico"] is esperado


# --- clientes HTTP (transporte falso) ---


def http_falso(respostas: list, pedidos: list):
    fila = list(respostas)

    def handler(request: httpx.Request) -> httpx.Response:
        pedidos.append(request)
        item = fila.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    return httpx.Client(transport=httpx.MockTransport(handler))


ITEM_CIDADE = {"lat": "-28.2550598", "lon": "-52.3966606", "name": "Passo Fundo",
               "address": {"city": "Passo Fundo", "municipality": "Passo Fundo", "state": "Rio Grande do Sul",
                           "country": "Brasil", "country_code": "br"}}


def test_nominatim_busca_formata_e_tira_repetidos():
    pedidos: list = []
    outro_ponto = ITEM_CIDADE | {"lat": "-28.1", "lon": "-52.3"}  # mesmo nome, outro ponto: sai
    vila = {"lat": "-1.5", "lon": "2.5", "name": "Vila", "address": {"village": "Vila", "country": "Quênia", "country_code": "ke"}}
    sem_coord = {"name": "x", "address": {"city": "x"}}
    c = ClienteNominatim(http_falso([httpx.Response(200, json=[ITEM_CIDADE, outro_ponto, vila, sem_coord])], pedidos))
    lugares = c.buscar("passo fundo", "pt")
    assert lugares == [
        {"nome": "Passo Fundo, Rio Grande do Sul", "pais": "Brasil", "pais_codigo": "BR", "lat": -28.2550598, "lon": -52.3966606},
        {"nome": "Vila", "pais": "Quênia", "pais_codigo": "KE", "lat": -1.5, "lon": 2.5},
    ]
    p = pedidos[0]
    assert p.headers["user-agent"] == nominatim.USER_AGENT
    q = dict(p.url.params)
    assert q["format"] == "jsonv2" and q["addressdetails"] == "1" and q["limit"] == "5" and q["accept-language"] == "pt"
    c.buscar("passo fundo", "pt")  # segunda vez vem do cache: não faz novo pedido
    assert len(pedidos) == 1


@pytest.mark.parametrize("resposta", [httpx.Response(500), httpx.Response(200, text="não é json"),
                                      httpx.Response(200, json={"erro": 1}), httpx.ConnectTimeout("lento")])
def test_nominatim_falha_lanca_erro_e_nao_guarda_no_cache(resposta):
    c = ClienteNominatim(http_falso([resposta], []))
    with pytest.raises(ErroNominatim):
        c.buscar("passo", "pt")
    assert nominatim._cache_busca.pegar(("passo", "pt", 5)) is None


def test_nominatim_reverso():
    pedidos: list = []
    c = ClienteNominatim(http_falso([httpx.Response(200, json=ITEM_CIDADE), httpx.Response(200, json={"error": "Unable to geocode"})], pedidos))
    assert c.reverso(-28.26, -52.41, "pt") == {"nome": "Passo Fundo, Rio Grande do Sul", "pais": "Brasil", "pais_codigo": "BR"}
    assert dict(pedidos[0].url.params)["zoom"] == "10"
    assert c.reverso(0.0, -30.0, "pt") is None  # mar: sem lugar
    assert c.reverso(0.0, -30.0, "pt") is None and len(pedidos) == 2


def resposta_power(chuva=None, temp=None, unidade_temp="C", fill=-999.0):
    meses = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    chuva, temp = chuva or CHUVA_LEM, temp or TEMP_LEM
    return {
        "geometry": {"coordinates": [-45.79, -12.1, 748.0]},
        "properties": {"parameter": {"PRECTOTCORR": dict(zip(meses, chuva)) | {"ANN": 2.86},
                                     "T2M": dict(zip(meses, temp)) | {"ANN": 24.6}}},
        "header": {"fill_value": fill},
        "parameters": {"PRECTOTCORR": {"units": "mm/day"}, "T2M": {"units": unidade_temp}},
    }


def test_power_climatologia_le_os_12_meses_e_ignora_ann():
    pedidos: list = []
    chuva = list(CHUVA_LEM)
    chuva[6] = -999.0
    c = ClientePowerClimatologia(http_falso([httpx.Response(200, json=resposta_power(chuva=chuva))], pedidos))
    r = c.mensal(-12.1, -45.79)
    assert r.temp_c == TEMP_LEM and len(r.chuva_mm_dia) == 12
    assert r.chuva_mm_dia[6] is None  # -999 vira None, nunca 0
    q = dict(pedidos[0].url.params)
    assert q["parameters"] == "T2M,PRECTOTCORR" and q["community"] == "AG" and q["latitude"] == "-12.1"
    assert json.loads(json.dumps(r.temp_c))  # só números
    c.mensal(-12.1, -45.79)
    assert len(pedidos) == 1  # cache


@pytest.mark.parametrize("resposta", [httpx.Response(429), httpx.Response(200, json={"x": 1}),
                                      httpx.Response(200, json=resposta_power(unidade_temp="K")),
                                      httpx.ReadTimeout("lento")])
def test_power_climatologia_falha(resposta):
    c = ClientePowerClimatologia(http_falso([resposta], []))
    with pytest.raises(ErroPowerClimatologia):
        c.mensal(-12.1, -45.79)
