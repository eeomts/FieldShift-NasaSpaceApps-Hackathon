"""Célula da grade do NASA POWER: o centro e o id de um ponto."""
import pytest

from app.services.clima.celula import centro_da_celula, id_da_celula


def test_ponto_vira_o_centro_da_celula():
    assert centro_da_celula(-11.314537, -41.814958) == (-11.5, -41.875)  # Irecê
    assert centro_da_celula(-17.644301, -51.080503) == (-17.5, -51.25)  # Rio Verde


def test_vizinhos_dividem_a_mesma_celula():
    assert id_da_celula(-11.4, -41.7) == id_da_celula(-11.6, -42.0)


def test_id_tem_lat_e_lon_do_centro():
    assert id_da_celula(-11.314537, -41.814958) == "-11.5_-41.875"


def test_negativos_e_positivos():
    assert centro_da_celula(48.86, 2.35) == (49.0, 2.5)
    assert centro_da_celula(-33.9, 151.2) == (-34.0, 151.25)


def test_centro_exato_fica_na_propria_celula():
    assert centro_da_celula(-11.5, -41.875) == (-11.5, -41.875)


def test_meio_exato_vai_para_o_lado_de_cima():
    assert centro_da_celula(0.25, 0.3125) == (0.5, 0.625)
    assert centro_da_celula(-0.25, -0.3125) == (0.0, 0.0)  # sem -0.0
    assert id_da_celula(-0.25, -0.3125) == "0.0_0.0"


@pytest.mark.parametrize("lat,esperado", [(90.0, 90.0), (-90.0, -90.0), (89.9, 90.0), (-89.9, -90.0)])
def test_bordas_de_latitude(lat, esperado):
    assert centro_da_celula(lat, 0.0)[0] == esperado


@pytest.mark.parametrize("lon,esperado", [(-180.0, -180.0), (180.0, -180.0), (179.9, -180.0), (179.1, 179.375)])
def test_bordas_de_longitude_dao_a_volta(lon, esperado):
    assert centro_da_celula(0.0, lon)[1] == esperado
