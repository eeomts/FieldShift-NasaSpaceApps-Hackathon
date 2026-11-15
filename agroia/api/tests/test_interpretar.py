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
    monkeypatch.setattr(mod, "_via_gemini", lambda campo, texto: [
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
    assert len(client.get("/equipamentos").json()) == 10
