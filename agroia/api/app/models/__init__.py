"""Models do banco; importar daqui registra todas as tabelas."""
from app.models.agente import BuscaLog
from app.models.clima import ClimaCelula, ClimaMensal
from app.models.conhecimento import Documento, Trecho
from app.models.fazenda import CalendarioItem, Fazenda
from app.models.usuario import Usuario

__all__ = [
    "BuscaLog",
    "CalendarioItem",
    "ClimaCelula",
    "ClimaMensal",
    "Documento",
    "Fazenda",
    "Trecho",
    "Usuario",
]
