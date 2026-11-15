"""Embedder do Gemini: sem chave dá erro claro e o vetor sai normalizado (sem chamar a API)."""
import math

import pytest

from app.core.config import get_settings
from app.services.rag.embeddings import EmbedderGemini, get_embedder, normalizar


def test_sem_chave_da_erro_claro_e_nunca_inventa_vetor():
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY não configurada"):
        EmbedderGemini(None, "gemini-embedding-001")
    get_embedder.cache_clear()
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY não configurada"):
        get_embedder()


def test_normalizar_deixa_norma_1():
    v = normalizar([3.0, 4.0])
    assert v == [0.6, 0.8]
    assert math.isclose(math.sqrt(sum(x * x for x in v)), 1.0)


def test_vetor_zerado_e_rejeitado():
    with pytest.raises(ValueError):
        normalizar([0.0, 0.0])
