import pytest

from app.services import catalogo as base
from app.services import interpretacao as mod


def test_casamento_por_sinonimos():
    achados = base.casa_texto("planto milho e feijão juntos, depois macaxeira e um capim pras vacas", base.culturas())
    assert [a["id"] for a in achados] == ["milho", "feijao", "mandioca", "pastagem"]
    assert base.casa_texto("feijão de porco na entressafra", base.culturas())[0]["id"] == "feijao_de_porco"
    eq = base.casa_texto("tenho trator pequeno e plantadeira, colheita é na mão", base.equipamentos())
    assert [a["id"] for a in eq] == ["trator", "plantadeira_graos", "manual"]


def test_sem_chave_usa_lista(client, auth):
    r = client.post("/onboarding/interpretar", headers=auth, json={"campo": "culturas", "texto": "soja e milho safrinha"})
    assert r.status_code == 200
    assert r.json()["fonte"] == "lista"
    assert [i["id"] for i in r.json()["itens"]] == ["soja", "milho"]


def test_ia_nao_inventa_itens(monkeypatch):
    """Ids fora da base viram 'não encontrado'; meses inválidos viram null; baixa confiança vem primeiro."""
    monkeypatch.setattr(mod, "get_settings", lambda: type("S", (), {"gemini_api_key": "x", "gemini_model": "m"})())
    monkeypatch.setattr(mod, "_via_gemini", lambda campo, texto, *_: [
        mod._ItemIA(texto_original="milho", id="milho", inicio_mes=10, fim_mes=2, consorcio_com=["feijao", "inventada"], confianca="alta"),
        mod._ItemIA(texto_original="jambu", id="jambu", confianca="alta"),
        mod._ItemIA(texto_original="café", id="cafe", inicio_mes=14, confianca="media"),
    ])
    out = mod.interpretar("culturas", "qualquer")
    assert out["fonte"] == "ia"
    jambu, cafe, milho = out["itens"]
    assert jambu == {"texto_original": "jambu", "id": None, "encontrado": False, "confianca": "baixa",
                     "inicio_mes": None, "fim_mes": None, "perene": False, "consorcio_com": []}
    assert cafe["perene"] is True and cafe["inicio_mes"] is None
    assert milho["consorcio_com"] == ["feijao"]


def test_ia_fora_do_ar_cai_na_lista(monkeypatch):
    monkeypatch.setattr(mod, "get_settings", lambda: type("S", (), {"gemini_api_key": "x"})())
    def quebra(*_):
        raise TimeoutError
    monkeypatch.setattr(mod, "_via_gemini", quebra)
    out = mod.interpretar("excluidas", "não planto soja")
    assert out["fonte"] == "lista" and out["itens"][0]["id"] == "soja"


def test_listas(client):
    assert any(c["id"] == "milheto" for c in client.get("/culturas").json())
    assert len(client.get("/equipamentos").json()) == 10  # nomes em inglês: test_onboarding_v3.py


# --- lista reserva (sem Gemini): meses, estações, consórcio, motivo ---


def reserva(campo, texto, hemisferio="S", idioma="pt"):
    out = mod.interpretar(campo, texto, hemisferio, idioma)
    assert out["fonte"] == "lista"
    return {i["id"]: i for i in out["itens"]}


def test_reserva_frase_do_contrato(client, auth):
    texto = "Planto milho e feijão juntos na estação chuvosa e, depois da colheita, o campo fica parado na seca."
    r = client.post("/onboarding/interpretar", headers=auth, json={"campo": "culturas", "texto": texto})
    assert r.status_code == 200 and r.json()["fonte"] == "lista"
    itens = {i["id"]: i for i in r.json()["itens"]}
    assert set(itens) == {"milho", "feijao"}
    for item in itens.values():
        assert (item["inicio_mes"], item["fim_mes"]) == (10, 4)  # chuvas começam em out; "parado na seca" -> fim = mai - 1
    assert itens["milho"]["consorcio_com"] == ["feijao"] and itens["feijao"]["consorcio_com"] == ["milho"]


def test_reserva_meses_por_nome_em_pt():
    it = reserva("culturas", "Planto soja de outubro a março")["soja"]
    assert (it["inicio_mes"], it["fim_mes"]) == (10, 3)
    it = reserva("culturas", "soja de set a jan")["soja"]
    assert (it["inicio_mes"], it["fim_mes"]) == (9, 1)
    it = reserva("culturas", "soja em mai e jun")["soja"]
    assert (it["inicio_mes"], it["fim_mes"]) == (5, 6)


def test_reserva_meses_so_valem_no_idioma_certo():
    en = reserva("culturas", "I plant corn from May to September", idioma="en")["milho"]
    assert (en["inicio_mes"], en["fim_mes"]) == (5, 9)
    assert reserva("culturas", "I plant corn from March to June", idioma="en")["milho"]["inicio_mes"] == 3
    # "may" não é mês em pt, nem "out" em en
    assert reserva("culturas", "planto soja may", idioma="pt")["soja"]["inicio_mes"] is None
    assert reserva("culturas", "I plant soy and then go out", idioma="en")["soja"]["inicio_mes"] is None


def test_reserva_dez_numero_nao_e_dezembro():
    assert reserva("culturas", "Tenho dez hectares de soja")["soja"]["inicio_mes"] is None
    assert reserva("culturas", "soja de agosto até dez")["soja"]["fim_mes"] == 12


@pytest.mark.parametrize("hemisferio,esperado", [("S", (12, 3)), ("N", (6, 9))])
def test_reserva_uma_estacao_depende_do_hemisferio(hemisferio, esperado):
    it = reserva("culturas", "planto soja no verão", hemisferio)["soja"]
    assert (it["inicio_mes"], it["fim_mes"]) == esperado


def test_reserva_estacoes():
    assert (lambda i: (i["inicio_mes"], i["fim_mes"]))(reserva("culturas", "trigo no inverno")["trigo"]) == (6, 9)
    # duas estações: da primeira à segunda; com "parado", termina um mês antes da segunda
    it = reserva("culturas", "milho na estação chuvosa até a seca")["milho"]
    assert (it["inicio_mes"], it["fim_mes"]) == (10, 5)
    it = reserva("culturas", "milho nas chuvas, depois o campo fica vazio na seca")["milho"]
    assert (it["inicio_mes"], it["fim_mes"]) == (10, 4)
    it = reserva("culturas", "corn in the rainy season, then the field sits idle in the dry season", "N", "en")["milho"]
    assert (it["inicio_mes"], it["fim_mes"]) == (6, 10)  # Norte: chuvas 6, seca 11, fim = 11 - 1


def test_reserva_mes_citado_vale_mais_que_estacao():
    it = reserva("culturas", "planto milho em novembro, no verão")["milho"]
    assert (it["inicio_mes"], it["fim_mes"]) == (11, None)


def test_reserva_frase_a_frase():
    itens = reserva("culturas", "Planto milho em outubro. Feijão de março a junho!")
    assert itens["milho"]["inicio_mes"] == 10 and itens["milho"]["fim_mes"] is None
    assert (itens["feijao"]["inicio_mes"], itens["feijao"]["fim_mes"]) == (3, 6)
    assert itens["milho"]["consorcio_com"] == [] and itens["feijao"]["consorcio_com"] == []


def test_reserva_mesma_cultura_em_duas_epocas():
    out = mod.interpretar("culturas", "Milho de outubro a fevereiro. Depois milho de abril a junho.")
    milhos = [(i["inicio_mes"], i["fim_mes"]) for i in out["itens"] if i["id"] == "milho"]
    assert milhos == [(10, 2), (4, 6)]


def test_reserva_consorcio_em_ingles_e_junto_sem_2_culturas():
    itens = reserva("culturas", "I grow corn and beans together in summer", "S", "en")
    assert itens["milho"]["consorcio_com"] == ["feijao"] and itens["feijao"]["consorcio_com"] == ["milho"]
    assert (itens["milho"]["inicio_mes"], itens["milho"]["fim_mes"]) == (12, 3)
    assert reserva("culturas", "Planto soja junto com a vizinha")["soja"]["consorcio_com"] == []
    assert reserva("culturas", "milho e feijão consorciados")["milho"]["consorcio_com"] == ["feijao"]


def test_reserva_ano_todo_vira_perene_so_com_uma_cultura():
    it = reserva("culturas", "Tenho soja o ano todo")["soja"]
    assert it["perene"] is True and it["inicio_mes"] is None
    assert reserva("culturas", "corn all year round", idioma="en")["milho"]["perene"] is True
    assert reserva("culturas", "milho e soja o ano todo")["soja"]["perene"] is False


@pytest.mark.parametrize("texto,idioma,esperado", [
    ("Não planto soja porque o mercado paga pouco", "pt", "mercado"),
    ("Não vendo milho aqui, é pra vender longe. Soja não.", "pt", "mercado"),
    ("I would not grow soy, no market for it", "en", "mercado"),
    ("Não planto feijão, é costume da família", "pt", "costume"),
    ("No soy, it is our custom", "en", "costume"),
    ("Soja não, deu errado na última vez", "pt", "deu_errado"),
    ("Perdi tudo com o milho", "pt", "deu_errado"),
    ("Corn failed last year, never again", "en", "deu_errado"),
    ("Não planto soja", "pt", None),
])
def test_reserva_motivo_das_excluidas(texto, idioma, esperado):
    out = mod.interpretar("excluidas", texto, "S", idioma)
    assert out["fonte"] == "lista" and out["itens"][0]["motivo"] == esperado


def test_reserva_motivo_por_frase():
    itens = reserva("excluidas", "Soja não, o mercado é ruim. Milho não, é costume.")
    assert itens["soja"]["motivo"] == "mercado" and itens["milho"]["motivo"] == "costume"


def test_ia_recebe_hemisferio_e_idioma(monkeypatch):
    visto = {}
    monkeypatch.setattr(mod, "get_settings", lambda: type("S", (), {"gemini_api_key": "x", "gemini_model": "m"})())
    monkeypatch.setattr(mod, "_via_gemini", lambda campo, texto, hemisferio, idioma: visto.update(h=hemisferio, i=idioma) or [])
    mod.interpretar("culturas", "corn in summer", "N", "en")
    assert visto == {"h": "N", "i": "en"}


def test_interpretar_aceita_so_hemisferio_e_idioma_validos(client, auth):
    corpo = {"campo": "culturas", "texto": "soja"}
    assert client.post("/onboarding/interpretar", headers=auth, json=corpo | {"hemisferio": "N", "idioma": "en"}).status_code == 200
    assert client.post("/onboarding/interpretar", headers=auth, json=corpo | {"hemisferio": "L"}).status_code == 422
    assert client.post("/onboarding/interpretar", headers=auth, json=corpo | {"idioma": "fr"}).status_code == 422
