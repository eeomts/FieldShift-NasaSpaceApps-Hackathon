"""Configuração lida do ambiente (.env). Nenhuma credencial fica no código."""
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Banco (produção: VPS 2.24.30.217:5433). Sem valor padrão para host e senha.
    db_host: str
    db_port: int = 5433
    db_name: str = "agricultura"
    db_user: str = "agricultura_app"
    db_password: str
    db_sslmode: str = "prefer"

    # Autenticação
    jwt_secret: str = Field(min_length=32)
    jwt_expires_min: int = 60 * 24 * 7

    # IA (opcional: sem chave, o onboarding usa a lista reserva)
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"

    # Front-end permitido (CORS), separado por vírgula
    cors_origins: str = "http://localhost:5173"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{quote_plus(self.db_user)}:{quote_plus(self.db_password)}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?sslmode={self.db_sslmode}"
        )

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
