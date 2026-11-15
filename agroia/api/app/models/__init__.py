"""Models do banco; importar daqui registra todas as tabelas."""
from app.models.agente import BuscaLog
from app.models.conhecimento import Documento, Trecho
from app.models.fazenda import CalendarioItem, Fazenda
from app.models.usuario import Usuario

__all__ = ["BuscaLog", "CalendarioItem", "Documento", "Fazenda", "Trecho", "Usuario"]
