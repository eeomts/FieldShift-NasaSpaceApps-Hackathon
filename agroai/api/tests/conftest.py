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
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.pool import NullPool  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.db import get_engine  # noqa: E402
from app.main import app  # noqa: E402

assert os.environ["DB_HOST"] in ("127.0.0.1", "localhost"), "testes só rodam em banco local"


CHAVE_TRAVA_BANCO = 7_150_126  # qualquer inteiro fixo: todo processo de pytest usa o mesmo


@pytest.fixture(scope="session", autouse=True)
def trava_do_banco():
    """Um segundo pytest espera o primeiro terminar: sem isto, os dois truncam o mesmo banco ao mesmo tempo.

    A trava fica numa conexão só dela (sem pool). Se o processo morrer, o Postgres solta a trava ao fechar a conexão."""
    engine = create_engine(get_settings().database_url, poolclass=NullPool)
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as c:
        c.execute(text("SELECT pg_advisory_lock(:k)"), {"k": CHAVE_TRAVA_BANCO})
        try:
            yield
        finally:
            c.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": CHAVE_TRAVA_BANCO})
    engine.dispose()


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
