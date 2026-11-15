"""Os testes rodam num Postgres de teste (variáveis em .env.test), nunca no banco da VPS."""
import os
from pathlib import Path

for linha in (Path(__file__).parents[1] / ".env.test").read_text().splitlines():
    if "=" in linha and not linha.startswith("#"):
        k, v = linha.split("=", 1)
        os.environ[k] = v
os.environ.pop("GEMINI_API_KEY", None)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.db import get_engine  # noqa: E402
from app.main import app  # noqa: E402

assert os.environ["DB_HOST"] in ("127.0.0.1", "localhost"), "testes só rodam em banco local"


@pytest.fixture(autouse=True)
def limpa_banco():
    with get_engine().begin() as c:
        c.execute(text("TRUNCATE usuario, documento, busca_log, clima_celula, relevo_ponto, solo_ponto CASCADE"))  # trecho e clima_mensal caem em cascata
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth(client) -> dict:
    r = client.post("/auth/register", json={"nome": "Marta", "email": "marta@exemplo.com", "senha": "segredo123"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture(autouse=True)
def cliente_solo(monkeypatch):
    """O SoilGrids nunca vai à rede nos testes: a tarefa em segundo plano usa este cliente falso (muda `.resposta` para variar)."""
    from solo_helpers import ClienteFalso

    cliente = ClienteFalso()
    monkeypatch.setattr("app.services.solo.processamento.get_cliente", lambda: cliente)
    return cliente
