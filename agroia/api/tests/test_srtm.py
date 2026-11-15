"""Declividade pelo SRTM com o OpenTopoData simulado (sem rede): Horn, classes, nova tentativa e falhas."""
import math

import httpx
import pytest

from app.services.integracao.srtm import (
    ClienteSrtm,
    ErroSrtm,
    classe_do_relevo,
    declividade_horn,
    pontos_da_grade,
)

LAT, LON = -17.644301, -51.080503
M_POR_GRAU = 111_320.0


def elevacao_plana(lat: float, lon: float, pct_leste: float, pct_norte: float) -> float:
    """Plano inclinado: sobe `pct_leste` % para o leste e `pct_norte` % para o norte (distâncias em metros)."""
    x = (lon - LON) * M_POR_GRAU * math.cos(math.radians(LAT))
    y = (lat - LAT) * M_POR_GRAU
    return 800 + x * pct_leste / 100 + y * pct_norte / 100


def terreno(pct_leste: float, pct_norte: float = 0.0) -> httpx.Response:
    """Resposta do OpenTopoData para os 9 pontos pedidos (monta pelo que o cliente pediu)."""
    return lambda request: httpx.Response(  # type: ignore[return-value]
        200,
        json={
            "status": "OK",
            "results": [
                {"elevation": elevacao_plana(*map(float, p.split(",")), pct_leste, pct_norte), "dataset": "srtm30m"}
                for p in request.url.params["locations"].split("|")
            ],
        },
    )


def cliente(*respostas) -> tuple[ClienteSrtm, list[httpx.Request], list[float]]:
    """Cada item da fila: função(request) -> Response, Response pronta ou exceção (lançada)."""
    fila, pedidos, esperas = list(respostas), [], []

    def handler(request: httpx.Request) -> httpx.Response:
        pedidos.append(request)
        item = fila.pop(0)
        if isinstance(item, Exception):
            raise item
        return item(request) if callable(item) else item

    return ClienteSrtm(httpx.Client(transport=httpx.MockTransport(handler)), espera=esperas.append), pedidos, esperas


def test_horn_a_mao():
    z = [[50, 45, 30], [80, 70, 60], [90, 80, 70]]  # linha 0 ao norte, coluna 0 a oeste
    # dz/dx = ((30 + 2*60 + 70) - (50 + 2*80 + 90)) / 240 = -80/240; dz/dy = ((50 + 90 + 30) - (90 + 160 + 70)) / 240 = -150/240
    assert declividade_horn(z) == pytest.approx(100 * math.hypot(-80 / 240, -150 / 240))
    assert declividade_horn([[7.0] * 3] * 3) == 0.0


def test_grade_de_9_pontos_com_30_m_de_passo():
    pts = pontos_da_grade(LAT, LON)
    assert len(pts) == 9 and pts[4] == (LAT, LON)
    assert pts[0][0] > LAT > pts[8][0] and pts[0][1] < LON < pts[8][1]  # a no noroeste, i no sudeste
    assert (pts[0][0] - pts[3][0]) * M_POR_GRAU == pytest.approx(30)
    assert (pts[1][1] - pts[0][1]) * M_POR_GRAU * math.cos(math.radians(LAT)) == pytest.approx(30)


def test_terreno_plano():
    c, pedidos, _ = cliente(terreno(0.0))
    d = c.declividade(LAT, LON)
    assert d.percentual == 0.0 and d.classe == "plano" and "SRTM" in d.fonte
    assert len(pedidos[0].url.params["locations"].split("|")) == 9


def test_terreno_inclinado_inclui_a_direcao_diagonal():
    d = cliente(terreno(6.0, 8.0))[0].declividade(LAT, LON)  # sobe 6% a leste e 8% ao norte: 10% no total
    assert d.percentual == pytest.approx(10.0, rel=0.02) and d.classe == "ondulado"
    assert cliente(terreno(30.0))[0].declividade(LAT, LON).classe == "forte_ondulado"
    assert cliente(terreno(-60.0))[0].declividade(LAT, LON).classe == "montanhoso"  # descida vale o mesmo


@pytest.mark.parametrize(
    "pct, classe",
    [(0, "plano"), (2.99, "plano"), (3, "suave_ondulado"), (7.99, "suave_ondulado"), (8, "ondulado"),
     (19.99, "ondulado"), (20, "forte_ondulado"), (44.99, "forte_ondulado"), (45, "montanhoso"), (120, "montanhoso")],
)  # fmt: skip
def test_classes_da_embrapa(pct, classe):
    assert classe_do_relevo(pct) == classe


def test_tenta_de_novo_em_429_e_5xx():
    c, pedidos, esperas = cliente(httpx.Response(429), httpx.Response(503), terreno(0.0))
    assert c.declividade(LAT, LON).classe == "plano"
    assert len(pedidos) == 3 and len(esperas) == 2


def test_falha_final_levanta_erro_proprio():
    c, pedidos, _ = cliente(httpx.Response(503), httpx.Response(503), httpx.Response(503))
    with pytest.raises(ErroSrtm):
        c.declividade(LAT, LON)
    assert len(pedidos) == 3
    with pytest.raises(ErroSrtm):
        cliente(httpx.ConnectError("sem rede"), httpx.ConnectError("sem rede"), httpx.ConnectError("sem rede"))[0].declividade(LAT, LON)


def test_erros_sem_nova_tentativa():
    c, pedidos, _ = cliente(httpx.Response(400, json={"error": "ruim"}))
    with pytest.raises(ErroSrtm):
        c.declividade(LAT, LON)
    assert len(pedidos) == 1
    with pytest.raises(ErroSrtm):
        cliente(httpx.Response(200, text="<html>"))[0].declividade(LAT, LON)
    with pytest.raises(ErroSrtm):
        cliente(httpx.Response(200, json={"status": "INVALID_REQUEST", "results": []}))[0].declividade(LAT, LON)


def test_elevacao_nula_no_mar_levanta_erro():
    corpo = {"status": "OK", "results": [{"elevation": None}] * 9}
    with pytest.raises(ErroSrtm):
        cliente(httpx.Response(200, json=corpo))[0].declividade(0.0, -30.0)
    um_nulo = {"status": "OK", "results": [{"elevation": 10.0}] * 8 + [{"elevation": None}]}
    with pytest.raises(ErroSrtm):
        cliente(httpx.Response(200, json=um_nulo))[0].declividade(LAT, LON)
