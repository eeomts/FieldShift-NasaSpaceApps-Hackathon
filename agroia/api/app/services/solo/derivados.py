"""Derivados do solo a partir dos números do SoilGrids: classe textural, matéria orgânica, acidez e erodibilidade K (funções puras)."""
import math

from app.services.onboarding.perfil import (
    FAIXAS_ACIDEZ,
    FAIXAS_MATERIA_ORGANICA,
    classe_da_faixa,
)

FATOR_MO_POR_CARBONO = 1.724  # matéria orgânica = carbono orgânico × 1,724 (van Bemmelen)
K_US_PARA_SI = 0.1317  # t·ac·h/(100 ac·ft·tonf·in) → t·ha·h/(ha·MJ·mm)

# Grupamentos texturais da Embrapa (SiBCS, Santos et al. 2018; triângulo textural como o do USDA).
ARGILA_MUITO_ARGILOSA_PCT = 60  # acima disso: muito argilosa; de 35 a 60: argilosa
ARGILA_ARGILOSA_PCT = 35
AREIA_SILTOSA_PCT = 15  # abaixo disso (e argila < 35): siltosa
# Classes "areia" e "areia franca" do triângulo: silte + 2·argila < 30 (areia pura: silte + 1,5·argila < 15).
AREIA_FRANCA_LIMITE = 30


def classe_textural(argila_pct: float | None, areia_pct: float | None, silte_pct: float | None) -> str | None:
    """Arenosa, média, argilosa, muito_argilosa ou siltosa (Embrapa, SiBCS 2018). Sem um dos três: None."""
    if argila_pct is None or areia_pct is None or silte_pct is None:
        return None
    if argila_pct > ARGILA_MUITO_ARGILOSA_PCT:
        return "muito_argilosa"
    if argila_pct >= ARGILA_ARGILOSA_PCT:
        return "argilosa"
    if areia_pct < AREIA_SILTOSA_PCT:
        return "siltosa"
    if silte_pct + 2 * argila_pct < AREIA_FRANCA_LIMITE:  # cobre areia (silte + 1,5·argila < 15) e areia franca
        return "arenosa"
    return "media"


def textura_simples(classe: str | None) -> str | None:
    """Agrupa nas três classes do questionário: muito argilosa vira argilosa; siltosa vira média."""
    return {"muito_argilosa": "argilosa", "siltosa": "media"}.get(classe, classe)


def materia_organica_g_kg(carbono_g_kg: float | None) -> float | None:
    return None if carbono_g_kg is None else carbono_g_kg * FATOR_MO_POR_CARBONO


def classe_acidez(ph: float | None) -> str | None:
    """Mesmas faixas do laudo (perfil.py): alta (< 5), média (< 6), adequada (< 7), alcalino."""
    return None if ph is None else classe_da_faixa(ph, *FAIXAS_ACIDEZ)


def classe_materia_organica(mo_g_kg: float | None, densidade_g_cm3: float | None = None) -> str | None:
    """Mesmas faixas do laudo, que vêm em g/dm³: o g/kg do mapa é multiplicado pela densidade do solo."""
    if mo_g_kg is None:
        return None
    em_g_dm3 = mo_g_kg * densidade_g_cm3 if densidade_g_cm3 else mo_g_kg
    return classe_da_faixa(em_g_dm3, *FAIXAS_MATERIA_ORGANICA)


def erodibilidade_k(argila_pct: float | None, areia_pct: float | None, silte_pct: float | None, carbono_g_kg: float | None) -> float | None:
    """K da USLE pelo método de Williams (modelo EPIC; Sharpley e Williams, 1990), em t·ha·h/(ha·MJ·mm).

    K = f_csand · f_cl-si · f_orgC · f_hisand, com areia, silte e argila em % e carbono orgânico em %:
      f_csand  = 0,2 + 0,3·exp(−0,256·areia·(1 − silte/100))
      f_cl-si  = (silte/(argila + silte))^0,3
      f_orgC   = 1 − 0,25·C/(C + exp(3,72 − 2,95·C))
      f_hisand = 1 − 0,7·(1 − areia/100)/((1 − areia/100) + exp(−5,51 + 22,9·(1 − areia/100)))
    A fórmula dá K em unidades americanas; × 0,1317 converte para o SI.
    """
    if argila_pct is None or areia_pct is None or silte_pct is None or carbono_g_kg is None:
        return None
    if argila_pct + silte_pct <= 0:
        return None
    c = carbono_g_kg / 10  # g/kg → %
    sa = areia_pct
    f_areia_grossa = 0.2 + 0.3 * math.exp(-0.256 * sa * (1 - silte_pct / 100))
    f_argila_silte = (silte_pct / (argila_pct + silte_pct)) ** 0.3
    f_carbono = 1 - 0.25 * c / (c + math.exp(3.72 - 2.95 * c))
    resto = 1 - sa / 100
    f_areia_alta = 1 - 0.7 * resto / (resto + math.exp(-5.51 + 22.9 * resto))
    return round(f_areia_grossa * f_argila_silte * f_carbono * f_areia_alta * K_US_PARA_SI, 4)
