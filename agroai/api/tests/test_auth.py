def test_cadastro_login_me(client):
    r = client.post("/auth/register", json={"nome": "Marta", "email": "Marta@Exemplo.com", "senha": "segredo123"})
    assert r.status_code == 201
    assert r.json()["usuario"]["email"] == "marta@exemplo.com"
    assert r.json()["usuario"]["onboarding_concluido"] is False

    r = client.post("/auth/login", json={"email": "marta@exemplo.com", "senha": "segredo123"})
    assert r.status_code == 200
    token = r.json()["token"]
    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert r.json()["nome"] == "Marta"


def test_email_repetido(client, auth):
    r = client.post("/auth/register", json={"nome": "Outra", "email": "marta@exemplo.com", "senha": "segredo123"})
    assert r.status_code == 409


def test_senha_errada_e_email_inexistente_dao_a_mesma_resposta(client, auth):
    a = client.post("/auth/login", json={"email": "marta@exemplo.com", "senha": "errada123"})
    b = client.post("/auth/login", json={"email": "ninguem@exemplo.com", "senha": "errada123"})
    assert a.status_code == b.status_code == 401
    assert a.json() == b.json()


def test_senha_curta(client):
    r = client.post("/auth/register", json={"nome": "X", "email": "x@exemplo.com", "senha": "123"})
    assert r.status_code == 422


def test_sem_token_e_token_invalido(client):
    assert client.get("/me").status_code == 401
    assert client.get("/me", headers={"Authorization": "Bearer abc"}).status_code == 401


def test_apagar_conta(client, auth):
    client.put("/fazenda", headers=auth, json={"respostas": {"q5_local": {"lat": -12, "lon": -45}}})
    assert client.delete("/me", headers=auth).status_code == 204
    assert client.get("/me", headers=auth).status_code == 401


def test_trocar_idioma(client, auth):
    assert client.get("/me", headers=auth).json()["idioma"] == "pt"
    r = client.patch("/me", headers=auth, json={"idioma": "en"})
    assert r.status_code == 200
    assert r.json()["idioma"] == "en" and r.json()["email"] == "marta@exemplo.com"
    assert client.get("/me", headers=auth).json()["idioma"] == "en"  # ficou gravado


def test_trocar_idioma_valida_e_exige_login(client, auth):
    assert client.patch("/me", headers=auth, json={"idioma": "fr"}).status_code == 422
    assert client.patch("/me", headers=auth, json={}).status_code == 422
    assert client.patch("/me", json={"idioma": "en"}).status_code == 401
