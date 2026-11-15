"""Texto -> vetor (embedding) com o Gemini; o vetor é normalizado (L2) aqui, não pela API."""
import math
from functools import lru_cache
from typing import Protocol

from app.core.config import get_settings
from app.models.conhecimento import EMBEDDING_DIM

TAMANHO_LOTE = 50  # a API aceita até 100 textos por chamada


class Embedder(Protocol):
    def documentos(self, textos: list[str]) -> list[list[float]]: ...
    def consulta(self, texto: str) -> list[float]: ...


def normalizar(vetor: list[float]) -> list[float]:
    """Com menos de 3072 dimensões a API não devolve o vetor normalizado."""
    norma = math.sqrt(sum(x * x for x in vetor))
    if norma == 0:
        raise ValueError("A API devolveu um vetor zerado.")
    return [x / norma for x in vetor]


class EmbedderGemini:
    def __init__(self, chave: str | None, modelo: str):
        if not chave:
            raise RuntimeError("GEMINI_API_KEY não configurada: defina no .env para gerar embeddings.")
        from google import genai
        from google.genai import types

        self._types = types
        self._client = genai.Client(api_key=chave, http_options=types.HttpOptions(timeout=60_000))
        self._modelo = modelo

    def _embutir(self, textos: list[str], tarefa: str) -> list[list[float]]:
        config = self._types.EmbedContentConfig(task_type=tarefa, output_dimensionality=EMBEDDING_DIM)
        vetores: list[list[float]] = []
        for i in range(0, len(textos), TAMANHO_LOTE):
            lote = textos[i : i + TAMANHO_LOTE]
            resp = self._client.models.embed_content(model=self._modelo, contents=lote, config=config)
            valores = [e.values for e in resp.embeddings or []]
            if len(valores) != len(lote) or any(v is None or len(v) != EMBEDDING_DIM for v in valores):
                raise RuntimeError(f"Resposta de embedding inesperada (esperado {len(lote)} vetores de {EMBEDDING_DIM}).")
            vetores.extend(normalizar(v) for v in valores)
        return vetores

    def documentos(self, textos: list[str]) -> list[list[float]]:
        return self._embutir(textos, "RETRIEVAL_DOCUMENT") if textos else []

    def consulta(self, texto: str) -> list[float]:
        return self._embutir([texto], "RETRIEVAL_QUERY")[0]


@lru_cache
def get_embedder() -> Embedder:
    s = get_settings()
    return EmbedderGemini(s.gemini_api_key, s.gemini_embedding_model)
