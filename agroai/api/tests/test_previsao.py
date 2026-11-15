"""Previsão de 7 dias (Open-Meteo simulada, sem rede): cliente, cache e rota."""
from datetime import UTC, date, datetime

import httpx
import pytest

from app.main import app
from app.services.integracao import open_meteo
from app.services.integracao.open_meteo import ClienteOpenMeteo, ErroOpenMeteo
from app.services.previsao.previsao_service import PrevisaoService, limpar_cache
from test_chat import IRECE

CORPO = {
    "daily_units": {"time": "iso8601", "temperature_2m_max": "°C", "temperature_2m_min": "°C", "precipitation_sum": "mm",
                    "precipitation_probability_max": "%", "weather_code": "wmo code"},
    "daily": {"time": ["2026-11-15", "2026-11-16"], "temperature_2m_max": [27.34, None], "temperature_2m_min": [18.3, 18.4],
              "precipitation_sum": [6.3, 0.0], "precipitation_probability_max": [84, None], "weather_code": [81, 0]},
}  # fmt: skip


def cliente(resposta) -> tuple[ClienteOpenMeteo, list[httpx.Request]]:
    pedidos = []

    def responder(request):
        pedidos.append(request)
        return resposta(request) if callable(resposta) else resposta

    return ClienteOpenMeteo(http=httpx.Client(transport=httpx.MockTransport(responder))), pedidos


@pytest.fixture(autouse=True)
def cache_limpo():
    limpar_cache()
    yield
    limpar_cache()


def test_le_os_dias_e_mantem_vazio_como_none():
    c, pedidos = cliente(httpx.Response(200, json=CORPO))
    dias = c.previsao(-15.6, -47.7)
    assert [d.data for d in dias] == [date(2026, 11, 15), date(2026, 11, 16)]
    assert dias[0].tmax == 27.3 and dias[0].chuva_mm == 6.3 and dias[0].chance_chuva == 84 and dias[0].codigo_tempo == 81
    assert dias[1].tmax is None and dias[1].chance_chuva is None
    assert pedidos[0].url.params["forecast_days"] == "7" and pedidos[0].url.params["timezone"] == "auto"


def test_unidade_diferente_falha_em_vez_de_converter_errado():
    corpo = {**CORPO, "daily_units": {**CORPO["daily_units"], "temperature_2m_max": "°F"}}
    with pytest.raises(ErroOpenMeteo):
        cliente(httpx.Response(200, json=corpo))[0].previsao(0, 0)


@pytest.mark.parametrize("resposta", [httpx.Response(500), httpx.Response(200, text="não é json")])
def test_erros_viram_erro_open_meteo(resposta):
    with pytest.raises(ErroOpenMeteo):
        cliente(resposta)[0].previsao(0, 0)


def test_cache_de_uma_hora():
    c, pedidos = cliente(httpx.Response(200, json=CORPO))
    s = PrevisaoService(c)
    s.agora = lambda: datetime(2026, 11, 15, 10, 5, tzinfo=UTC)
    s.obter(-15.6, -47.7)
    s.agora = lambda: datetime(2026, 11, 15, 10, 55, tzinfo=UTC)
    s.obter(-15.6, -47.7)
    assert len(pedidos) == 1
    s.agora = lambda: datetime(2026, 11, 15, 11, 1, tzinfo=UTC)
    s.obter(-15.6, -47.7)
    assert len(pedidos) == 2


@pytest.fixture
def rota_com(request):
    resposta = request.param
    app.dependency_overrides[open_meteo.get_cliente] = lambda: cliente(resposta)[0]
    yield
    app.dependency_overrides.clear()


@pytest.mark.parametrize("rota_com", [httpx.Response(200, json=CORPO)], indirect=True)
def test_rota(client, auth, rota_com):
    assert client.get("/fazenda/previsao").status_code == 401
    assert client.get("/fazenda/previsao", headers=auth).status_code == 404
    client.put("/fazenda", headers=auth, json={"respostas": {"q1_quem": "produtor"}})
    assert client.get("/fazenda/previsao", headers=auth).status_code == 422
    client.put("/fazenda", headers=auth, json={"respostas": IRECE})
    r = client.get("/fazenda/previsao", headers=auth)
    assert r.status_code == 200
    c = r.json()
    assert c["fonte"] == "Open-Meteo" and c["licenca"] == "CC BY 4.0" and len(c["dias"]) == 2
    assert set(c["dias"][0]) == {"data", "tmax", "tmin", "chuva_mm", "chance_chuva", "codigo_tempo"}


@pytest.mark.parametrize("rota_com", [httpx.Response(503)], indirect=True)
def test_rota_com_open_meteo_fora_do_ar_da_503(client, auth, rota_com):
    client.put("/fazenda", headers=auth, json={"respostas": IRECE})
    assert client.get("/fazenda/previsao", headers=auth).status_code == 503
