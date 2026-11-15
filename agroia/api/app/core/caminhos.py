"""Raiz do repositório (no Docker o layout é o mesmo, sob /app)."""
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parents[4]
