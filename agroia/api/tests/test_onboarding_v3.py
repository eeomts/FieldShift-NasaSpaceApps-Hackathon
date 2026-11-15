"""Questionário v3: local com país e zona, correção do solo (múltipla), novas perdas e equipamentos em inglês."""
import pytest
from pydantic import ValidationError
from sqlalchemy import text

from app.core.db import get_engine
from app.schemas.onboarding import Respostas
from app.services.onboarding.perfil import retrato_solo

BASE = {"q5_local": {"lat": -12.1, "lon": -45.79, "nome": "Luís Eduardo Magalhães, Bahia"}}


def salvar(client, auth, **respostas):
    return client.put("/fazenda", headers=auth, json={"respostas": respostas})


def test_local_com_pais_e_zona(client, auth):
    local = {"lat": -12.1, "lon": -45.79, "nome": "LEM", "pais": "br", "zona_climatica": "Aw"}
    r = salvar(client, auth, q5_local=local)
    assert r.status_code == 200
    assert r.json()["respostas"]["q5_local"] == local | {"pais": "BR"}  # país sempre maiúsculo
    # o formato antigo (sem país e zona) continua valendo
    assert salvar(client, auth, **BASE).json()["respostas"]["q5_local"]["pais"] is None


@pytest.mark.parametrize("campo", [{"pais": "BRA"}, {"pais": "B1"}, {"zona_climatica": "Cfa-x"}])
def test_local_invalido(client, auth, campo):
    assert salvar(client, auth, q5_local={"lat": 1, "lon": 1} | campo).status_code == 422


def test_correcao_do_solo_multipla(client, auth):
    r = salvar(client, auth, q21_correcao=["calcario", "gesso", "outra"], q21_correcao_outra="cinza de madeira")
    assert r.status_code == 200
    assert r.json()["respostas"]["q21_correcao"] == ["calcario", "gesso", "outra"]
    assert r.json()["respostas"]["q21_correcao_outra"] == "cinza de madeira"
    assert salvar(client, auth, q21_correcao=["nao"]).status_code == 200
    assert salvar(client, auth, q21_correcao=["nao_sei"]).status_code == 200
    assert salvar(client, auth).json()["respostas"]["q21_correcao"] == []


@pytest.mark.parametrize("lista", [["nao", "calcario"], ["gesso", "nao_sei"], ["nao", "nao_sei"],
                                   ["calcario", "calcario"], ["xyz"]])
def test_correcao_exclusivas_repetidos_e_invalidos(client, auth, lista):
    assert salvar(client, auth, q21_correcao=lista).status_code == 422


@pytest.mark.parametrize("antigo,novo", [("sim", ["calcario"]), ("nao", ["nao"]), ("nao_sei", ["nao_sei"])])
def test_formato_antigo_q21_calcario(antigo, novo):
    assert Respostas.model_validate({"q21_calcario": antigo}).q21_correcao == novo
    # se já veio no formato novo, o novo vence
    assert Respostas.model_validate({"q21_calcario": "sim", "q21_correcao": ["gesso"]}).q21_correcao == ["gesso"]


def test_fazenda_antiga_no_banco_abre(client, auth):
    """Respostas salvas antes da mudança (JSONB com q21_calcario) continuam abrindo."""
    salvar(client, auth, **BASE)
    with get_engine().begin() as c:
        c.execute(text("UPDATE fazenda SET respostas = respostas || '{\"q21_calcario\": \"sim\"}'::jsonb"))
    r = client.get("/fazenda", headers=auth)
    assert r.status_code == 200
    assert r.json()["respostas"]["q21_correcao"] == ["calcario"]
    assert "q21_calcario" not in r.json()["respostas"]


def test_retrato_do_solo_usa_a_correcao():
    def por_atributo(**r):
        return {i["atributo"]: i for i in retrato_solo(Respostas(**r))["indicadores"]}

    ind = por_atributo(q21_correcao=["calcario", "gesso", "outra"], q21_correcao_outra="cinza")
    assert ind["correcao_acidez"]["valor"] == "feita" and ind["correcao_salinidade"]["valor"] == "feita"
    assert ind["correcao_outra"]["texto"] == "Outra correção: cinza"
    assert por_atributo(q21_correcao=["nao"])["correcao_solo"]["valor"] == "nao"
    assert por_atributo(q21_correcao=["nao_sei"]) == {}  # não sei nunca vira valor


def test_novas_perdas(client, auth):
    perdas = {"alagamento": {"resposta": "sim", "ano": 2020}, "granizo": {"resposta": "nao"},
              "salinidade": {"resposta": "nao_sei"}, "geada": {"resposta": "sim", "ano": 2021}}
    r = salvar(client, auth, q24_perdas=perdas)
    assert r.status_code == 200
    saida = r.json()["respostas"]["q24_perdas"]
    assert saida["alagamento"] == {"resposta": "sim", "ano": 2020}
    assert saida["granizo"] == {"resposta": "nao", "ano": None}
    assert saida["salinidade"]["resposta"] == "nao_sei"
    assert saida["seca"] == {"resposta": None, "ano": None}
    assert salvar(client, auth, q24_perdas={"granizo": {"resposta": "sim", "ano": 1900}}).status_code == 422


def test_equipamentos_por_idioma(client):
    pt = client.get("/equipamentos").json()
    en = client.get("/equipamentos?idioma=en").json()
    assert client.get("/equipamentos?idioma=pt").json() == pt
    assert [e["id"] for e in en] == [e["id"] for e in pt]
    assert {e["id"]: e["nome"] for e in pt}["colhedora"] == "Colheitadeira"
    assert {e["id"]: e["nome"] for e in en}["colhedora"] == "Combine harvester"
    assert all(e["nome"] for e in en)
    assert client.get("/equipamentos?idioma=fr").status_code == 422
