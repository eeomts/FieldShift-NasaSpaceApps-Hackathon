"""Chamada ao Gemini (generate_content, sem chamada automática de função); injetável para os testes usarem um modelo falso."""
from functools import lru_cache
from typing import Protocol

from google.genai import types

from app.core.config import get_settings

TIMEOUT_MS = 60_000
# Pico de demanda do Gemini (503) e limite de uso (429) costumam passar em segundos.
REPETIR = types.HttpRetryOptions(attempts=3, initial_delay=1.0, max_delay=8.0, http_status_codes=[429, 503])
TEMPERATURA = 0.3


class ModeloIndisponivel(Exception):
    """Sem chave configurada."""


class ModeloIA(Protocol):
    def gerar(
        self, contents: list[types.Content], instrucao: str, ferramentas: list[types.Tool]
    ) -> types.GenerateContentResponse: ...


class ModeloGemini:
    def __init__(self, chave: str | None, modelo: str):
        self._chave = chave
        self._modelo = modelo
        self._client = None

    def gerar(
        self, contents: list[types.Content], instrucao: str, ferramentas: list[types.Tool]
    ) -> types.GenerateContentResponse:
        if not self._chave:
            raise ModeloIndisponivel("GEMINI_API_KEY não configurada")
        if self._client is None:  # criado na primeira chamada: sem chave, a API sobe e o chat responde 503
            from google import genai

            self._client = genai.Client(api_key=self._chave, http_options=types.HttpOptions(timeout=TIMEOUT_MS, retry_options=REPETIR))
        config = types.GenerateContentConfig(
            system_instruction=instrucao,
            tools=ferramentas,
            temperature=TEMPERATURA,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        return self._client.models.generate_content(model=self._modelo, contents=contents, config=config)


@lru_cache
def get_modelo() -> ModeloIA:
    s = get_settings()
    return ModeloGemini(s.gemini_api_key, s.gemini_model)
