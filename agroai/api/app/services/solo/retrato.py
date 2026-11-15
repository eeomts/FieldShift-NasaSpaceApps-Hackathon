"""Retrato do solo completo: o que o produtor contou (perfil.py) + síntese por fusão + solo do SoilGrids."""
from app.schemas.onboarding import Respostas
from app.schemas.solo import SoloPonto
from app.services.onboarding import perfil
from app.services.solo import fusao


def montar_retrato(r: Respostas, solo: SoloPonto | None) -> dict:
    """`indicadores` e `figuras` como sempre; `sintese` (fusão) e `soilgrids` (None enquanto não há mapa) são acréscimos."""
    retrato = perfil.retrato_solo(r)
    retrato["sintese"] = [a.model_dump(mode="json") for a in fusao.sintese(retrato, solo)]
    retrato["soilgrids"] = None if solo is None else solo.model_dump(mode="json")
    return retrato
