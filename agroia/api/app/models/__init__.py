"""Tabelas do banco (≈ Models do Eloquent). Um arquivo por domínio.

Importar daqui registra todas as tabelas no metadata (o Alembic depende disso).
"""
from app.models.fazenda import CalendarioItem, Fazenda
from app.models.usuario import Usuario

__all__ = ["CalendarioItem", "Fazenda", "Usuario"]
