"""País e município/condado dos pontos (malhas IBGE e Census), com os pontos da demo."""
import csv

import pytest

from app.core.caminhos import RAIZ_REPO
from app.services.motor.local import pais_e_codigo

DEMO = RAIZ_REPO / "data" / "demo"


def pontos(arquivo: str) -> list[dict]:
    with (DEMO / arquivo).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


ESPERADO_BR = {"cerrado_1": "5218805", "sul_1": "4314100", "semiarido_1": "2914604"}
ESPERADO_US = {"cornbelt_1": "19169", "plains_1": "20135", "south_1": "13277"}


@pytest.mark.parametrize("p", pontos("pontos_demo.csv"), ids=lambda p: p["id"])
def test_pontos_demo_do_brasil(p):
    assert pais_e_codigo(float(p["latitude"]), float(p["longitude"])) == ("BR", ESPERADO_BR[p["id"]])


@pytest.mark.parametrize("p", pontos("pontos_demo_eua.csv"), ids=lambda p: p["id"])
def test_pontos_demo_dos_eua(p):
    assert pais_e_codigo(float(p["latitude"]), float(p["longitude"])) == ("US", ESPERADO_US[p["id"]])


def test_codigos_tem_7_e_5_digitos():
    assert len(pais_e_codigo(-12.09, -45.79)[1]) == 7  # Luís Eduardo Magalhães
    assert len(pais_e_codigo(42.07, -93.45)[1]) == 5


@pytest.mark.parametrize("lat,lon", [(0.0, -30.0), (-33.0, -40.0), (35.0, 0.0)], ids=["atlantico", "mar_sul", "europa"])
def test_oceano_e_outros_paises_sem_pais(lat, lon):
    assert pais_e_codigo(lat, lon) == (None, None)
