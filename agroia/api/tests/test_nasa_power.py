"""Cliente do NASA POWER com resposta simulada (sem rede)."""
import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from app.services.integracao import nasa_power
from app.services.integracao.nasa_power import ClienteNasaPower, ErroNasaPower

RESPOSTA = json.loads((Path(__file__).parent / "fixtures" / "nasa_power_resposta.json").read_text())


def cliente(respostas: list, pedidos: list | None = None) -> tuple[ClienteNasaPower, list[float]]:
    """Cliente cujo HTTP devolve as respostas em ordem (exceção é lançada). Devolve também as esperas pedidas."""
    fila = list(respostas)
    esperas: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if pedidos is not None:
            pedidos.append(request)
        item = fila.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    http = httpx.Client(transport=httpx.MockTransport(handler))
    return ClienteNasaPower(http, espera=esperas.append), esperas


def ok(corpo: dict | None = None) -> httpx.Response:
    return httpx.Response(200, json=corpo or RESPOSTA)


def serie(c: ClienteNasaPower):
    return c.serie_diaria(-11.5, -41.875, date(1991, 1, 1), date(1991, 1, 3))


def test_interpreta_a_resposta():
    s = serie(cliente([ok()])[0])
    assert (s.lat, s.lon, s.elevacao_m) == (-11.5, -41.875, 758.62)
    assert [d.data for d in s.dias] == [date(1991, 1, 1), date(1991, 1, 2), date(1991, 1, 3)]
    d = s.dias[0]
    assert (d.t2m, d.tmax, d.tmin, d.chuva, d.ur, d.radiacao, d.vento) == (23.67, 29.34, 18.87, 0.27, 67.83, 15.53, 2.67)


def test_menos_999_vira_none_e_chuva_zero_continua_zero():
    s = serie(cliente([ok()])[0])
    assert s.dias[1].tmax is None
    assert s.dias[1].tmin == 18.43
    assert s.dias[2].chuva == 0.0


def test_pede_os_parametros_pelo_centro_da_celula():
    pedidos: list = []
    serie(cliente([ok()], pedidos)[0])
    q = pedidos[0].url.params
    assert q["community"] == "AG"
    assert q["latitude"] == "-11.5" and q["longitude"] == "-41.875"
    assert (q["start"], q["end"], q["format"]) == ("19910101", "19910103", "JSON")
    assert set(q["parameters"].split(",")) == set(nasa_power.PARAMETROS)


def test_erro_5xx_seguido_de_sucesso_tenta_de_novo():
    c, esperas = cliente([httpx.Response(503), httpx.Response(502), ok()])
    assert len(serie(c).dias) == 3
    assert len(esperas) == 2


def test_erro_de_rede_seguido_de_sucesso_tenta_de_novo():
    c, esperas = cliente([httpx.ConnectTimeout("lento"), ok()])
    assert len(serie(c).dias) == 3
    assert len(esperas) == 1


def test_falha_final_vira_erro_proprio():
    c, esperas = cliente([httpx.Response(500)] * 3)
    with pytest.raises(ErroNasaPower, match="HTTP 500"):
        serie(c)
    assert len(esperas) == 2


def test_erro_4xx_nao_tenta_de_novo():
    c, esperas = cliente([httpx.Response(422)])
    with pytest.raises(ErroNasaPower, match="422"):
        serie(c)
    assert esperas == []


def test_resposta_que_nao_e_json():
    with pytest.raises(ErroNasaPower, match="JSON"):
        serie(cliente([httpx.Response(200, text="<html>")])[0])


def test_formato_inesperado():
    with pytest.raises(ErroNasaPower, match="formato"):
        serie(cliente([ok({"foo": 1})])[0])


def test_parametro_faltando():
    corpo = json.loads(json.dumps(RESPOSTA))
    del corpo["properties"]["parameter"]["WS2M"]
    with pytest.raises(ErroNasaPower, match="WS2M"):
        serie(cliente([ok(corpo)])[0])


def test_unidade_diferente_da_esperada_falha():
    corpo = json.loads(json.dumps(RESPOSTA))
    corpo["parameters"]["WS2M"]["units"] = "km/h"
    with pytest.raises(ErroNasaPower, match="WS2M"):
        serie(cliente([ok(corpo)])[0])
