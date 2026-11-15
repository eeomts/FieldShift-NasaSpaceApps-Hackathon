"""SoilGrids com a API simulada (sem rede): conversões, renormalização, médias ponderadas, incerteza, sem dado e tentativas."""
import json
from pathlib import Path

import httpx
import pytest

from app.services.integracao import soilgrids
from app.services.integracao.soilgrids import (
    ClienteSoilGrids,
    ErroSoilGrids,
    converter,
    incerteza_relativa,
    interpretar,
    interpretar_propriedade,
    media_ponderada,
    montar_amostra,
    renormalizar_textura,
)
from solo_helpers import camada, resposta, resposta_argilosa, resposta_urbana


@pytest.mark.parametrize(
    "propriedade,bruto,esperado",
    [("clay", 364, 36.4), ("sand", 403, 40.3), ("silt", 232, 23.2), ("soc", 200, 20.0), ("phh2o", 56, 5.6),
     ("bdod", 125, 1.25), ("cec", 155, 15.5), ("nitrogen", 150, 1.5), ("cfvo", 105, 10.5)],
)  # fmt: skip
def test_fatores_de_conversao(propriedade, bruto, esperado):
    assert converter(propriedade, bruto) == pytest.approx(esperado)


def test_nulo_continua_nulo_nunca_vira_zero():
    assert converter("clay", None) is None


def test_media_ponderada_pela_espessura_a_mao():
    # (5·10 + 10·20 + 15·30) / 30 = 700/30
    assert media_ponderada({"0-5cm": 10.0, "5-15cm": 20.0, "15-30cm": 30.0}) == pytest.approx(700 / 30)


def test_media_ponderada_ignora_profundidade_sem_valor_e_sem_nenhuma_e_none():
    assert media_ponderada({"0-5cm": 10.0, "5-15cm": None, "15-30cm": 30.0}) == pytest.approx((5 * 10 + 15 * 30) / 20)
    assert media_ponderada({"0-5cm": None, "5-15cm": None}) is None


def test_incerteza_relativa():
    assert incerteza_relativa(20, 40, 60) == pytest.approx(1.0)
    assert incerteza_relativa(None, 40, 60) is None
    assert incerteza_relativa(20, 0, 60) is None  # mediana zero: não dá para dividir


def test_renormaliza_quando_a_soma_foge_de_100_por_mais_de_2():
    v = renormalizar_textura({"clay": 44.0, "sand": 44.0, "silt": 22.0, "phh2o": 5.0})  # soma 110
    assert v["clay"] == pytest.approx(40.0) and v["sand"] == pytest.approx(40.0) and v["silt"] == pytest.approx(20.0)
    assert v["phh2o"] == 5.0


def test_nao_renormaliza_dentro_da_tolerancia_ou_com_falta():
    dentro = {"clay": 41.0, "sand": 40.0, "silt": 20.0}  # 101
    assert renormalizar_textura(dentro) == dentro
    faltando = {"clay": 41.0, "sand": None, "silt": 20.0}
    assert renormalizar_textura(faltando) == faltando


def test_interpretar_converte_e_faz_as_duas_camadas():
    corpo = resposta(
        camada("clay", [300, 400, 500, 600, 700], q05=100, q50=400, q95=700),
        camada("sand", [400, 400, 300, 200, 100], q05=100, q50=400, q95=700),
        camada("silt", [300, 200, 200, 200, 200], q05=100, q50=200, q95=300),
        camada("phh2o", [50, 52, 56, 60, 62], q05=45, q50=55, q95=65),
    )
    a = interpretar(corpo)
    assert not a.sem_dado
    # 0–30 cm: argila (5·30 + 10·40 + 15·50)/30 = 43,33 %
    assert a.superficial.valores["clay"] == pytest.approx((5 * 30 + 10 * 40 + 15 * 50) / 30)
    # 0–100 cm: pesos 5, 10, 15, 30, 40 sobre 30, 40, 50, 60, 70
    assert a.raizes.valores["clay"] == pytest.approx((5 * 30 + 10 * 40 + 15 * 50 + 30 * 60 + 40 * 70) / 100)
    assert a.superficial.valores["phh2o"] == pytest.approx((5 * 5.0 + 10 * 5.2 + 15 * 5.6) / 30)
    # quantis iguais em todas as profundidades: (70 − 10) ÷ 40 = 1,5
    assert a.superficial.incerteza["clay"] == pytest.approx(1.5)
    assert a.superficial.incerteza["phh2o"] == pytest.approx((6.5 - 4.5) / 5.5)


def test_interpretar_renormaliza_a_textura_da_camada():
    corpo = resposta(camada("clay", [500] * 5), camada("sand", [500] * 5), camada("silt", [200] * 5))  # soma 120
    v = interpretar(corpo).superficial.valores
    assert v["clay"] + v["sand"] + v["silt"] == pytest.approx(100.0)
    assert v["clay"] == pytest.approx(50 * 100 / 120)


def test_area_urbana_ou_agua_vem_tudo_nulo_e_vira_sem_dado():
    a = interpretar(resposta_urbana())
    assert a.sem_dado is True and a.superficial is None and a.raizes is None


def test_profundidade_sem_valor_nao_vira_zero():
    corpo = resposta(camada("clay", [400, 400, 400, None, None]), camada("sand", [400] * 5), camada("silt", [200] * 5))
    a = interpretar(corpo)
    assert a.raizes.valores["clay"] == pytest.approx(40.0)  # só as três primeiras entram, ponderadas
    assert a.superficial.valores["clay"] == pytest.approx(40.0)


@pytest.mark.parametrize("corpo", [{}, {"properties": {}}, {"properties": {"layers": [{"name": "clay"}]}}, {"properties": {"layers": None}}])
def test_formato_inesperado_levanta_erro(corpo):
    with pytest.raises(ErroSoilGrids):
        interpretar(corpo)


# --- uma propriedade por vez, e propriedades que podem faltar ---


def test_propriedade_isolada_da_resposta():
    p = interpretar_propriedade(resposta_argilosa(), "soc")
    assert (p.nome, p.superficial, p.raizes, p.sem_dado) == ("soc", pytest.approx(20.0), pytest.approx(20.0), False)
    assert p.incerteza_superficial == pytest.approx((30 - 10) / 20)


def test_propriedade_que_nao_esta_na_resposta_e_erro():
    with pytest.raises(ErroSoilGrids):
        interpretar_propriedade(resposta(camada("clay", [400] * 5)), "soc")


def test_propriedade_toda_nula_e_sem_dado():
    p = interpretar_propriedade(resposta_urbana(), "clay")
    assert p.sem_dado is True and p.superficial is None


def test_amostra_parcial_so_com_o_que_veio():
    props = {n: interpretar_propriedade(resposta_argilosa(), n) for n in ("phh2o", "soc")}
    a = montar_amostra(props)
    assert a.superficial.valores == {"phh2o": pytest.approx(5.5), "soc": pytest.approx(20.0)}  # sem textura, sem renormalizar
    assert not a.sem_dado


def test_amostra_com_uma_propriedade_sem_dado_e_sem_dado():
    props = {"clay": interpretar_propriedade(resposta_urbana(), "clay")}
    assert montar_amostra(props).sem_dado is True


# --- cliente HTTP: um pedido por propriedade ---


def cliente(*falhas, corpo=None, relogio=lambda: 0.0) -> tuple[ClienteSoilGrids, list[httpx.Request], list[float]]:
    """Responde com a propriedade pedida de `corpo`; cada item de `falhas` (Response ou exceção) é usado antes, um por pedido."""
    fila, pedidos, esperas = list(falhas), [], []
    base = corpo or resposta_argilosa()

    def handler(request: httpx.Request) -> httpx.Response:
        pedidos.append(request)
        if fila:
            item = fila.pop(0)
            if isinstance(item, Exception):
                raise item
            return item
        pedidas = request.url.params.get_list("property")
        return httpx.Response(200, json=resposta(*(c for c in base["properties"]["layers"] if c["name"] in pedidas)))

    return ClienteSoilGrids(httpx.Client(transport=httpx.MockTransport(handler)), espera=esperas.append, relogio=relogio), pedidos, esperas


def test_cliente_pede_a_propriedade_com_profundidades_e_estatisticas():
    c, pedidos, _ = cliente()
    p = c.propriedade(-17.644301, -51.080503, "clay")
    q = pedidos[0].url.params
    assert pedidos[0].url.path == "/soilgrids/v2.0/properties/query" and len(pedidos) == 1
    assert q["lat"] == "-17.644301" and q["lon"] == "-51.080503" and q.get_list("property") == ["clay"]
    assert q.get_list("depth") == ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm"]
    assert q.get_list("value") == ["mean", "Q0.05", "Q0.5", "Q0.95"]
    assert p.superficial == pytest.approx(40.0)
    assert soilgrids.PROPRIEDADES == ("clay", "sand", "silt", "soc", "phh2o", "bdod", "cec")  # textura primeiro


def test_respeita_o_intervalo_minimo_entre_pedidos():
    agora = [0.0]
    c, pedidos, esperas = cliente(relogio=lambda: agora[0])
    c.espera = lambda s: (esperas.append(s), agora.__setitem__(0, agora[0] + s))[0]  # a espera faz o relógio andar
    for nome in soilgrids.PROPRIEDADES:
        c.propriedade(-17.64, -51.08, nome)
    assert len(pedidos) == 7 and esperas == [soilgrids.INTERVALO_MINIMO_ENTRE_PEDIDOS_S] * 6  # respostas instantâneas: espera o intervalo todo


def test_pedido_que_demorou_mais_que_o_intervalo_nao_espera_mais():
    agora = [0.0]
    c, _, esperas = cliente(relogio=lambda: agora[0])
    original = c.http.get
    c.http.get = lambda *a, **k: (agora.__setitem__(0, agora[0] + 40.0), original(*a, **k))[1]  # cada pedido leva 40 s
    for nome in soilgrids.PROPRIEDADES:
        c.propriedade(-17.64, -51.08, nome)
    assert esperas == []


@pytest.mark.parametrize("falha", [httpx.Response(429), httpx.Response(504), httpx.Response(503), httpx.ReadTimeout("lento")])
def test_uma_nova_tentativa_depois_de_429_5xx_ou_timeout(falha):
    c, pedidos, esperas = cliente(falha)
    assert c.propriedade(-17.64, -51.08, "clay").superficial is not None
    assert len(pedidos) == 2
    assert soilgrids.ESPERA_ENTRE_TENTATIVAS_S in esperas


def test_depois_da_nova_tentativa_desiste_com_erro_proprio():
    c, pedidos, _ = cliente(httpx.Response(504), httpx.Response(504))
    with pytest.raises(ErroSoilGrids, match="HTTP 504"):
        c.propriedade(-17.64, -51.08, "clay")
    assert len(pedidos) == soilgrids.NOVAS_TENTATIVAS + 1


def test_recusa_do_servidor_nao_insiste():
    c, pedidos, _ = cliente(httpx.Response(404))
    with pytest.raises(ErroSoilGrids, match="HTTP 404"):
        c.propriedade(-17.64, -51.08, "clay")
    assert len(pedidos) == 1


def test_resposta_que_nao_e_json_e_erro_proprio():
    c, _, _ = cliente(httpx.Response(200, text="<html>oops</html>"))
    with pytest.raises(ErroSoilGrids, match="não é JSON"):
        c.propriedade(-17.64, -51.08, "clay")


def test_ponto_urbano_pelo_cliente_vira_sem_dado():
    c, _, _ = cliente(corpo=resposta_urbana())
    assert c.propriedade(-23.5505, -46.6333, "clay").sem_dado is True


# --- respostas reais da API (guardadas em 15/11/2026) ---
FIXTURES = Path(__file__).parent / "fixtures"


def test_resposta_real_de_rio_verde_textura_de_0_a_30_cm():
    # argila 36,4 / 37,6 / 42,7 %, areia 40,3 / 41,8 / 38,4 %, silte 23,2 / 20,5 / 18,9 % em 0–5 / 5–15 / 15–30 cm
    a = interpretar(json.loads((FIXTURES / "soilgrids_rio_verde_textura.json").read_text(encoding="utf-8")))
    v = a.superficial.valores
    assert v["clay"] == pytest.approx((5 * 36.4 + 10 * 37.6 + 15 * 42.7) / 30, abs=0.1)
    assert v["sand"] == pytest.approx((5 * 40.3 + 10 * 41.8 + 15 * 38.4) / 30, abs=0.1)
    assert v["silt"] == pytest.approx((5 * 23.2 + 10 * 20.5 + 15 * 18.9) / 30, abs=0.1)
    assert v["clay"] + v["sand"] + v["silt"] == pytest.approx(100.0, abs=0.5)
    assert a.superficial.incerteza["clay"] > 1  # o intervalo de 90 % é maior que a própria mediana: confiança baixa


def test_resposta_real_de_area_urbana_tem_valores_nulos_e_vira_sem_dado():
    corpo = json.loads((FIXTURES / "soilgrids_sao_paulo_urbano.json").read_text(encoding="utf-8"))
    assert corpo["properties"]["layers"][0]["depths"][0]["values"] == {"Q0.5": None, "mean": None}
    assert interpretar(corpo).sem_dado is True
