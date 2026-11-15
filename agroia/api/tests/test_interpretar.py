import pytest

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
    monkeypatch.setattr(mod, "_via_gemini", lambda campo, texto, *_: [
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
    monkeypatch.setattr(mod, "_via_gemini", lambda campo, texto, *_: [
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
    assert len(client.get("/equipamentos").json()) == 14  # nomes em inglês: test_onboarding_v3.py


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


def test_casamento_dos_equipamentos_de_feno_amendoim_e_mandioca():
    def ids(texto):
        return [a["id"] for a in base.casa_texto(texto, base.equipamentos())]

    assert ids("enfardadeira") == ["enfardadeira"]
    assert ids("peanut digger") == ["arrancador_amendoim"]
    assert ids("plantadeira de manivas") == ["plantadeira_manivas"]
    assert ids("afofador de mandioca") == ["afofador_mandioca"]
    assert ids("plantadeira") == ["plantadeira_graos"]
    assert ids("colhedora") == ["colhedora"]
    assert ids("combine") == ["colhedora"]
    assert ids("cassava harvester") == ["afofador_mandioca"]


def test_nenhum_sinonimo_em_dois_equipamentos():
    donos: dict[str, set[str]] = {}
    for item_id, item in base.equipamentos().items():
        for nomes in item["nomes"].values():
            for n in nomes:
                donos.setdefault(base.normaliza(n), set()).add(item_id)
    assert {n: ids for n, ids in donos.items() if len(ids) > 1} == {}
