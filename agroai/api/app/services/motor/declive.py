"""Fator de declive da nota de erosão: LS da RUSLE (USDA AH 703) da declividade medida, com teto 1."""
import math

from app.services.motor.parametros import RAMPA_PADRAO_M, RAMPA_TIPICA_M


def ls_rusle(declividade_pct: float, rampa_m: float = RAMPA_TIPICA_M) -> float:
    """LS da RUSLE, razão moderada entre sulco e entressulco (AH 703, eqs. 4-1 a 4-5): L = (λ/72,6 pés)^m, S por trechos.

    m = β/(1+β), β = (sen θ / 0,0896) / (3 (sen θ)^0,8 + 0,56); S = 10,8 sen θ + 0,03 abaixo de 9 %, 16,8 sen θ − 0,50 de 9 % em diante.
    Vale 1 na parcela-padrão da USLE (72,6 pés ≈ 22,1 m, 9 % de declive).
    """
    seno = math.sin(math.atan(max(declividade_pct, 0.0) / 100))
    beta = (seno / 0.0896) / (3 * seno**0.8 + 0.56)
    m = beta / (1 + beta)
    s = 10.8 * seno + 0.03 if declividade_pct < 9 else 16.8 * seno - 0.50
    return (rampa_m / RAMPA_PADRAO_M) ** m * s


def fator_do_declive(declividade_pct: float) -> float:
    """Fator que multiplica a parte descoberta: mín(1; LS), com a rampa típica (escolha de produto: acima da parcela-padrão não separa)."""
    return min(1.0, ls_rusle(declividade_pct))
