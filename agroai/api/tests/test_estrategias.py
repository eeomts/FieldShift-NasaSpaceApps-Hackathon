"""Rota GET /fazenda/estrategias com NASA POWER e SRTM falsos (sem rede): contrato, erros e ordem das notas."""
import pytest

from app.core.erros import ErroDeNegocio
from app.main import app
from app.services.integracao import srtm
from app.services.integracao.nasa_power import get_cliente
from app.services.motor.entradas import MSG_SEM_CATALOGO
from app.services.motor.motor_service import MotorService
from test_chat import IRECE, ClienteFalso, SrtmFalso

URL = "/fazenda/estrategias"
CRITERIOS = ["agua", "terra", "erosao", "pragas", "renda", "animais"]
MSG_NASA = "Não consegui os dados de clima da NASA agora. Tente de novo em alguns minutos."


@pytest.fixture(autouse=True)
def externos():
    app.dependency_overrides[get_cliente] = lambda: ClienteFalso()
    app.dependency_overrides[srtm.get_cliente] = lambda: SrtmFalso()
    yield
    app.dependency_overrides.clear()


def salvar(client, auth, **respostas):
    r = client.put("/fazenda", headers=auth, json={"respostas": {**IRECE, **respostas}})
    assert r.status_code == 200


def confere_resultado(r: dict):
    assert set(r) == {"id", "nome", "origem", "itens", "nota_final", "notas", "por_que", "onde_piora", "alertas", "confianca", "lacunas"}
    assert r["origem"] in ("atual", "janela", "tolerante_seca", "leguminosa") and r["confianca"] in ("alta", "media", "baixa")
    assert r["nota_final"] is None or 0 <= r["nota_final"] <= 1
    assert [n["criterio"] for n in r["notas"]] == CRITERIOS
    for n in r["notas"]:
        assert set(n) == {"criterio", "nota", "explicacao", "evidencias"} and isinstance(n["explicacao"], str)
        for e in n["evidencias"]:
            assert set(e) == {"texto", "valor", "unidade", "fonte", "periodo"}
    for i in r["itens"]:
        assert set(i) == {"cultura_id", "nome", "inicio_mes", "fim_mes", "perene"} and i["nome"]
    for a in r["alertas"]:
        assert set(a) == {"codigo", "texto"}


def test_exige_token(client):
    assert client.get(URL).status_code == 401


def test_analise_no_formato_do_contrato(client, auth):
    salvar(client, auth, q25_prioridades=["agua", "animais", "terra"])
    r = client.get(URL, headers=auth)
    assert r.status_code == 200
    c = r.json()
    assert set(c) == {"pais", "atual_e_a_melhor", "pesos", "atual", "melhores", "eliminadas", "fontes", "gerado_em"}
    assert c["pais"] == "BR" and isinstance(c["atual_e_a_melhor"], bool)
    assert list(c["pesos"]) == CRITERIOS and abs(sum(c["pesos"].values()) - 1) < 1e-6
    assert c["gerado_em"].endswith(("Z", "+00:00")) and c["fontes"]
    confere_resultado(c["atual"])
    assert c["atual"]["origem"] == "atual" and c["atual"]["id"] == "atual"
    assert [i["nome"] for i in c["atual"]["itens"]] == ["Milho", "Feijão"]  # nome de exibição, não o texto original
    assert len(c["melhores"]) <= 2
    for m in c["melhores"]:
        confere_resultado(m)
    for e in c["eliminadas"]:
        assert set(e) == {"nome", "motivos"} and e["motivos"]


def test_nome_fora_do_catalogo_fica_com_o_texto_original(client, auth):
    salvar(client, auth, q8_culturas=[{"cultura_id": None, "texto_original": "jabuticaba", "inicio_mes": 1, "fim_mes": 12, "perene": True}])
    r = client.get(URL, headers=auth)
    assert r.status_code == 200
    assert r.json()["atual"]["itens"][0] == {"cultura_id": None, "nome": "jabuticaba", "inicio_mes": 1, "fim_mes": 12, "perene": True}


def test_sem_fazenda_da_404(client, auth):
    r = client.get(URL, headers=auth)
    assert r.status_code == 404 and r.json() == {"detail": "Fazenda não encontrada."}


def test_sem_local_da_422(client, auth):
    salvar(client, auth, q5_local=None)
    r = client.get(URL, headers=auth)
    assert r.status_code == 422 and r.json() == {"detail": "Marque o local da fazenda para comparar rotações."}


def test_sem_calendario_da_422(client, auth):
    salvar(client, auth, q8_culturas=[])
    r = client.get(URL, headers=auth)
    assert r.status_code == 422 and r.json() == {"detail": "Cadastre o que você planta para comparar rotações."}


def test_sem_culturas_da_regiao_da_422(client, auth):
    class MotorSemBase:
        def analisar(self, f):
            raise ErroDeNegocio(422, MSG_SEM_CATALOGO)

    salvar(client, auth)
    app.dependency_overrides[MotorService] = lambda: MotorSemBase()
    r = client.get(URL, headers=auth)
    assert r.status_code == 422 and r.json() == {"detail": "Ainda não temos as culturas desta região na base."}


def test_nasa_power_fora_do_ar_da_503(client, auth):
    app.dependency_overrides[get_cliente] = lambda: ClienteFalso(erro=True)
    salvar(client, auth)
    r = client.get(URL, headers=auth)
    assert r.status_code == 503 and r.json() == {"detail": MSG_NASA}
