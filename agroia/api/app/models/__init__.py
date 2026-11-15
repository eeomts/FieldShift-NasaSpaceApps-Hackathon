"""Models do banco; importar daqui registra todas as tabelas."""
from app.models.agente import BuscaLog, Conversa, Mensagem
from app.models.clima import ClimaCelula, ClimaMensal
from app.models.conhecimento import Documento, Trecho
from app.models.fazenda import CalendarioItem, Fazenda
from app.models.relevo import RelevoPonto
from app.models.solo import SoloPontoCache
from app.models.usuario import Usuario

__all__ = [
    "BuscaLog",
    "CalendarioItem",
    "ClimaCelula",
    "ClimaMensal",
    "Conversa",
    "Documento",
    "Fazenda",
    "Mensagem",
    "RelevoPonto",
    "SoloPontoCache",
    "Trecho",
    "Usuario",
]
