"""Os testes rodam num Postgres de teste (variáveis em .env.test), nunca no banco da VPS."""
import os
from pathlib import Path

for linha in (Path(__file__).parents[1] / ".env.test").read_text().splitlines():
    if "=" in linha and not linha.startswith("#"):
        k, v = linha.split("=", 1)
        os.environ[k] = v
os.environ["EARTHDATA_TOKEN"] = ""  # testes nunca usam o token real nem a rede
os.environ["GEMINI_API_KEY"] = ""  # vazio vence o .env (o pop deixava a chave real vazar para os testes)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.db import get_engine  # noqa: E402
from app.main import app  # noqa: E402

assert os.environ["DB_HOST"] in ("127.0.0.1", "localhost"), "testes só rodam em banco local"


@pytest.fixture(autouse=True)
def limpa_banco():
    with get_engine().begin() as c:
        c.execute(text("TRUNCATE usuario, documento, busca_log, clima_celula, relevo_ponto CASCADE"))  # trecho e clima_mensal caem em cascata
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth(client) -> dict:
    r = client.post("/auth/register", json={"nome": "Marta", "email": "marta@exemplo.com", "senha": "segredo123"})
    return {"Authorization": f"Bearer {r.json()['token']}"}
