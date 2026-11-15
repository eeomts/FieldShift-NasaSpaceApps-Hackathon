"""Köppen-Geiger a partir de séries mensais sintéticas (sem rede)."""
import pytest

from app.services.local.koppen import chuva_mensal_mm, koppen

# (temperatura média por mês jan..dez, chuva em mm por mês jan..dez, hemisfério, classe esperada)
CASOS = {
    "Aw": ([25] * 12, [150, 150, 170, 95, 25, 3, 0.3, 3, 10, 75, 160, 175], "S"),
    "As": ([25] * 12, [5, 10, 30, 80, 150, 200, 200, 150, 100, 60, 30, 10], "S"),
    "Af": ([26] * 12, [200] * 12, "S"),
    "Am": ([26] * 12, [350, 350, 300, 250, 200, 100, 60, 50, 100, 150, 250, 300], "S"),
    "BWh": ([20, 22, 25, 30, 34, 36, 37, 36, 33, 29, 24, 20], [5] * 12, "N"),
    "BSh": ([26] * 12, [80, 70, 60, 20, 10, 5, 5, 5, 10, 30, 50, 60], "S"),
    "BSk": ([0, 2, 6, 11, 16, 20, 24, 23, 18, 12, 5, 1], [21] * 12, "N"),
    "Cfa": ([24, 23.5, 22, 18.5, 15, 12.5, 12, 13.5, 15.5, 18, 20.5, 22.5], [130] * 12, "S"),
    "Csa": ([10, 11, 13, 16, 20, 24, 27, 27, 23, 18, 13, 10], [70, 60, 50, 40, 20, 5, 2, 5, 25, 60, 80, 80], "N"),
    "Cwa": ([14, 16, 20, 24, 27, 28, 28, 28, 27, 24, 20, 15], [10, 15, 30, 60, 150, 250, 300, 300, 200, 60, 20, 10], "N"),
    "Dfa": ([-6, -3, 3, 10, 17, 22, 25, 24, 19, 12, 4, -3], [70] * 12, "N"),
    "Dfb": ([-8, -6, 0, 6, 12, 17, 20, 18, 13, 7, 0, -6], [70] * 12, "N"),
    "Dwc": ([-30, -25, -15, -3, 5, 11, 13, 10, 3, -8, -22, -30], [3, 2, 3, 10, 25, 50, 70, 60, 40, 12, 6, 4], "N"),
    "ET": ([-20, -18, -12, -5, 0, 3, 5, 4, 1, -6, -14, -19], [20] * 12, "N"),
    "EF": ([-30, -28, -25, -20, -12, -5, -3, -6, -15, -22, -27, -30], [10] * 12, "S"),
}


@pytest.mark.parametrize("esperada", CASOS)
def test_classes(esperada):
    temp, chuva, hemisferio = CASOS[esperada]
    assert koppen(temp, chuva, hemisferio) == esperada


def test_hemisferio_inverte_o_verao():
    """A mesma série vira outra zona no outro hemisfério: o verão chuvoso do Cwa de lá é o inverno daqui."""
    temp, chuva, _ = CASOS["Cwa"]
    assert koppen(temp, chuva, "N") == "Cwa"
    assert koppen(temp, chuva, "S") != "Cwa"


def test_chuva_de_mm_por_dia_para_mm_no_mes():
    mm = chuva_mensal_mm([1.0] * 12)
    assert mm[0] == 31 and mm[1] == 28 and mm[3] == 30
    assert sum(mm) == 365


def test_precisa_de_12_meses():
    with pytest.raises(ValueError):
        koppen([20] * 11, [50] * 11, "S")
