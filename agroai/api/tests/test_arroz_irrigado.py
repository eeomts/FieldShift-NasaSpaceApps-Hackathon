"""arroz_irrigado em agroai/base/culturas.json: id novo, sem colidir com os nomes do arroz de terras altas."""
from app.services import catalogo as base


def ids(texto: str) -> list[str]:
    return [c["id"] for c in base.casa_texto(texto, base.culturas())]


def test_arroz_irrigado_tem_o_formato_dos_outros_itens():
    c = base.culturas()["arroz_irrigado"]
    assert (c["familia"], c["grupo"], c["perene"], c["tipos"]) == ("graminea", "graos", False, [])
    assert set(c["nomes"]) == {"pt", "en", "es"}


def test_nao_colide_com_arroz():
    assert ids("arroz") == ["arroz"] and ids("rice") == ["arroz"]
    assert ids("arroz irrigado") == ["arroz_irrigado"] and ids("arroz de várzea") == ["arroz_irrigado"]
    assert ids("paddy rice") == ["arroz_irrigado"] and ids("arroz de riego") == ["arroz_irrigado"]
    assert ids("soja e arroz irrigado, depois arroz") == ["soja", "arroz_irrigado", "arroz"]


def test_nomes_do_arroz_irrigado_nao_sao_de_outra_cultura():
    outros = {base.normaliza(n) for i, c in base.culturas().items() if i != "arroz_irrigado" for ns in c["nomes"].values() for n in ns}
    proprios = {base.normaliza(n) for ns in base.culturas()["arroz_irrigado"]["nomes"].values() for n in ns}
    assert not proprios & outros
