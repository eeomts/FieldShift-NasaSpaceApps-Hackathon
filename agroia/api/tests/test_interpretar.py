from app.services import catalogo as base
from app.services import interpretacao as mod


def test_casamento_por_sinonimos():
    achados = base.casa_texto("planto milho e feijão juntos, depois macaxeira e um capim pras vacas", base.culturas())
    assert [a["id"] for a in achados] == ["milho", "feijao", "mandioca", "pastagem"]
    assert base.casa_texto("feijão de porco na entressafra", base.culturas())[0]["id"] == "feijao_de_porco"
    eq = base.casa_texto("tenho trator pequeno e plantadeira, colheita é na mão", base.equipamentos())
    assert [a["id"] for a in eq] == ["trator", "plantadeira_graos", "manual"]


def test_arroz_irrigado_e_de_terras_altas():
    def ids(texto):
        return [a["id"] for a in base.casa_texto(texto, base.culturas())]

    for texto in ("arroz irrigado", "arroz de banhado", "arroz alagado", "arroz de várzea", "lowland rice", "flooded rice"):
        assert ids(texto) == ["arroz_irrigado"], texto
    for texto in ("arroz", "upland rice", "arroz de sequeiro", "rice"):
        assert ids(texto) == ["arroz"], texto
    assert len(ids("rice and rice paddy")) == 1
    assert base.nome_exibicao(base.culturas()["arroz"]) == "Arroz de terras altas"
    assert base.nome_exibicao(base.culturas()["arroz"], "en") == "Upland rice"


def test_batata_x_batata_doce():
    def ids(texto):
        return [a["id"] for a in base.casa_texto(texto, base.culturas())]

    assert ids("batata") == ["batata"] and ids("batata inglesa") == ["batata"] and ids("potato") == ["batata"]
    for texto in ("batata doce", "batata-doce", "camote", "boniato", "sweet potato"):
        assert ids(texto) == ["batata_doce"], texto
        assert base.alternativas("batata_doce", texto) == []
    assert base.alternativas("batata", "Batata") == ["batata", "batata_doce"]
    assert base.alternativas("batata", "batata inglesa") == []


def test_nenhum_sinonimo_em_duas_culturas():
    donos: dict[str, set[str]] = {}
    for item_id, item in base.culturas().items():
        for nomes in item["nomes"].values():
            for n in nomes:
                donos.setdefault(base.normaliza(n), set()).add(item_id)
    repetidos = {n: ids for n, ids in donos.items() if len(ids) > 1}
    assert repetidos == {}


def test_alternativas_so_para_nome_ambiguo():
    assert base.alternativas("arroz", "arroz") == ["arroz", "arroz_irrigado"]
    assert base.alternativas("arroz", " Rice. ") == ["arroz", "arroz_irrigado"]
    assert base.alternativas("arroz", "arroz de sequeiro") == []
    assert base.alternativas("arroz_irrigado", "arroz") == []
    assert base.alternativas("soja", "soja") == []
    assert base.alternativas("inexistente", "arroz") == []


def test_so_arroz_pela_lista_reserva_pede_escolha(client, auth):
    r = client.post("/onboarding/interpretar", headers=auth, json={"campo": "culturas", "texto": "rice e soja"})
    assert r.status_code == 200 and r.json()["fonte"] == "lista"
    arroz, soja = r.json()["itens"]  # baixa confiança vem primeiro
    assert arroz["id"] == "arroz" and arroz["confianca"] == "baixa" and arroz["alternativas"] == ["arroz", "arroz_irrigado"]
    assert soja["id"] == "soja" and soja["alternativas"] == []
    r = client.post("/onboarding/interpretar", headers=auth, json={"campo": "culturas", "texto": "batata e batata doce"})
    batata, doce = r.json()["itens"]
    assert batata["id"] == "batata" and batata["confianca"] == "baixa" and batata["alternativas"] == ["batata", "batata_doce"]
    assert doce["id"] == "batata_doce" and doce["alternativas"] == []
    r = client.post("/onboarding/interpretar", headers=auth, json={"campo": "culturas", "texto": "arroz irrigado"})
    assert r.json()["itens"][0]["id"] == "arroz_irrigado" and r.json()["itens"][0]["alternativas"] == []


def test_so_arroz_pela_ia_pede_escolha(monkeypatch):
    monkeypatch.setattr(mod, "get_settings", lambda: type("S", (), {"gemini_api_key": "x", "gemini_model": "m"})())
    monkeypatch.setattr(mod, "_via_gemini", lambda campo, texto: [
        mod._ItemIA(texto_original="rice", id="arroz", confianca="alta"),
        mod._ItemIA(texto_original="arroz", id="arroz_irrigado", confianca="alta"),  # palpite da IA é mantido
        mod._ItemIA(texto_original="arroz de várzea", id="arroz_irrigado", confianca="alta"),
        mod._ItemIA(texto_original="soja", id="soja", confianca="alta"),
        mod._ItemIA(texto_original="batata", id="batata", confianca="alta"),
        mod._ItemIA(texto_original="batata", id="batata_doce", confianca="media"),
        mod._ItemIA(texto_original="camote", id="batata_doce", confianca="alta"),
    ])
    out = mod.interpretar("culturas", "qualquer")
    assert out["fonte"] == "ia"
    pares = [(i["texto_original"], i["id"], i["confianca"], i["alternativas"]) for i in out["itens"]]
    assert pares == [  # baixa confiança primeiro, na ordem em que vieram
        ("rice", "arroz", "baixa", ["arroz", "arroz_irrigado"]),
        ("arroz", "arroz_irrigado", "baixa", ["arroz", "arroz_irrigado"]),
        ("batata", "batata", "baixa", ["batata", "batata_doce"]),
        ("batata", "batata_doce", "baixa", ["batata", "batata_doce"]),
        ("arroz de várzea", "arroz_irrigado", "alta", []),
        ("soja", "soja", "alta", []),
        ("camote", "batata_doce", "alta", []),
    ]
    excluidas = mod._valida("excluidas", [mod._ItemIA(texto_original="arroz", id="arroz", motivo="mercado", confianca="alta")])
    assert excluidas[0]["alternativas"] == ["arroz", "arroz_irrigado"] and excluidas[0]["confianca"] == "baixa"
    equip = mod._valida("equipamentos", [mod._ItemIA(texto_original="trator", id="trator", confianca="alta")])
    assert equip[0]["alternativas"] == []


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
                     "inicio_mes": None, "fim_mes": None, "perene": False, "consorcio_com": [], "alternativas": []}
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
