MARTA = {
    "q1_quem": "produtor", "q2_area": "20_200", "q3_tecnico": "as_vezes", "q4_animais": "nao",
    "q5_local": {"lat": -12.09, "lon": -45.79, "nome": "Luís Eduardo Magalhães, BA"},
    "q6_irrigacao": "nao", "q7_terreno": "leve",
    "q8_texto": "soja de novembro a março",
    "q8_culturas": [{"cultura_id": "soja", "texto_original": "soja", "inicio_mes": 11, "fim_mes": 3}],
    "q13_textura": "nao_sei", "q19_cor": "vermelha", "q19_jeito": "gruda",
    "q24_perdas": {"seca": {"resposta": "sim", "ano": 2021}},
    "q25_prioridades": ["erosao", "terra", "agua"],
    "q26a_excluidas": [{"cultura_id": "algodao", "texto_original": "algodão", "motivo": "mercado"}],
}


def test_sem_fazenda_da_404(client, auth):
    assert client.get("/fazenda", headers=auth).status_code == 404


def test_salvar_parcial_e_concluir(client, auth):
    r = client.put("/fazenda", headers=auth, json={"respostas": {"q1_quem": "produtor"}, "passo_atual": 1})
    assert r.status_code == 200 and r.json()["onboarding_concluido"] is False

    r = client.put("/fazenda", headers=auth, json={"respostas": {"q1_quem": "produtor"}, "concluir": True})
    assert r.status_code == 422  # sem local não conclui

    r = client.put("/fazenda", headers=auth, json={"respostas": MARTA, "passo_atual": 8, "concluir": True})
    assert r.status_code == 200
    f = r.json()
    assert f["onboarding_concluido"] is True
    assert f["perfil"] == "A"
    assert f["papel"] == "produtor"
    assert f["modificadores"] == {"irrigacao": "nao", "animais": False}
    assert f["meses_sem_cobertura"] == [4, 5, 6, 7, 8, 9, 10]
    assert f["retrato_solo"]["figuras"]["leitura"] == "Argilosa e bem drenada"
    assert f["proximos_passos"][0]["id"] == "teste_tato"
    assert client.get("/me", headers=auth).json()["onboarding_concluido"] is True

    # salvar de novo substitui o calendário em vez de duplicar
    MARTA2 = MARTA | {"q8_culturas": MARTA["q8_culturas"] + [{"cultura_id": "milheto", "texto_original": "milheto", "inicio_mes": 4, "fim_mes": 7}]}
    f = client.put("/fazenda", headers=auth, json={"respostas": MARTA2, "concluir": True}).json()
    assert f["meses_sem_cobertura"] == [8, 9, 10]
    assert len(client.get("/fazenda", headers=auth).json()["respostas"]["q8_culturas"]) == 2


def test_validacoes(client, auth):
    ruim = [
        {"q25_prioridades": ["agua", "terra", "erosao", "renda"]},
        {"q25_prioridades": ["agua", "agua"]},
        {"q5_local": {"lat": 120, "lon": 0}},
        {"q8_culturas": [{"cultura_id": "batata_marciana", "texto_original": "x"}]},
        {"q8_culturas": [{"cultura_id": "soja", "texto_original": "soja", "inicio_mes": 13}]},
    ]
    for respostas in ruim:
        assert client.put("/fazenda", headers=auth, json={"respostas": respostas}).status_code == 422, respostas


def test_cultura_fora_da_base_e_aceita_sem_id(client, auth):
    r = client.put("/fazenda", headers=auth, json={"respostas": {"q8_culturas": [{"cultura_id": None, "texto_original": "jambu"}]}})
    assert r.status_code == 200


def _local_salvo(usuario_email: str) -> tuple[str | None, str | None]:
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from app.core.db import get_engine
    from app.models import Fazenda, Usuario

    with Session(get_engine()) as s:
        f = s.scalars(select(Fazenda).join(Usuario).where(Usuario.email == usuario_email)).one()
        return f.pais, f.codigo_local


def test_salvar_preenche_pais_e_codigo_do_local_e_limpa_quando_sai(client, auth):
    salvar = lambda local: client.put("/fazenda", headers=auth, json={"respostas": MARTA | {"q5_local": local}})  # noqa: E731
    assert salvar({"lat": -17.644301, "lon": -51.080503}).status_code == 200
    assert _local_salvo("marta@exemplo.com") == ("BR", "5218805")  # Rio Verde-GO

    assert salvar({"lat": 42.07, "lon": -93.45}).status_code == 200  # mudou de ponto: recalcula
    assert _local_salvo("marta@exemplo.com") == ("US", "19169")  # Story-IA

    assert salvar({"lat": 0.0, "lon": -30.0}).status_code == 200  # oceano: sem país
    assert _local_salvo("marta@exemplo.com") == (None, None)

    assert salvar({"lat": -28.310532, "lon": -52.412854}).status_code == 200
    assert client.put("/fazenda", headers=auth, json={"respostas": {"q1_quem": "produtor"}}).status_code == 200  # sem local
    assert _local_salvo("marta@exemplo.com") == (None, None)


def test_saida_da_fazenda_nao_ganhou_campos(client, auth):
    f = client.put("/fazenda", headers=auth, json={"respostas": MARTA}).json()
    assert "pais" not in f and "codigo_local" not in f
