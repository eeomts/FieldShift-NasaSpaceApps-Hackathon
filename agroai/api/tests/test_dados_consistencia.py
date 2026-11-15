"""Consistência entre os arquivos de dados: catálogos BR e EUA, culturas.json, tabelas NASS e evidências.

Não usa banco. Quem muda um CSV, uma evidência ou o culturas.json e quebra algum teste daqui está
deixando duas fontes se contradizerem.
"""
import csv
import importlib.util
import json
from pathlib import Path

from app.core.caminhos import RAIZ_REPO
from app.services.motor.catalogo import CSV_POR_PAIS, catalogo_do_pais

DIR_CATALOGO = RAIZ_REPO / "data" / "catalogo"
DIR_NASS = RAIZ_REPO / "data" / "eua" / "nass"
CULTURAS_JSON = RAIZ_REPO / "agroai" / "base" / "culturas.json"
SCRIPT_MONTAR = DIR_CATALOGO / "scripts" / "montar_csv.py"
EXTRAS_EUA = ["codigo_nass", "calendario_usda"]
TOTAL_CULTURAS_EUA = 18


def _carrega_montar():
    spec = importlib.util.spec_from_file_location("montar_csv_dados", SCRIPT_MONTAR)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _linhas(caminho: Path) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _cabecalho(caminho: Path) -> list[str]:
    with caminho.open(encoding="utf-8", newline="") as f:
        return next(csv.reader(f))


def _ids_json() -> set[str]:
    return {c["id"] for c in json.loads(CULTURAS_JSON.read_text(encoding="utf-8"))["culturas"]}


def test_catalogo_eua_tem_18_ids_no_culturas_json_e_as_colunas_do_br_mais_as_extras():
    linhas = _linhas(CSV_POR_PAIS["US"])
    ids = [l["id"] for l in linhas]
    assert len(ids) == TOTAL_CULTURAS_EUA and len(set(ids)) == TOTAL_CULTURAS_EUA
    assert set(ids) <= _ids_json()
    assert _cabecalho(CSV_POR_PAIS["US"]) == _cabecalho(CSV_POR_PAIS["BR"]) + EXTRAS_EUA


def test_producao_e_datas_de_plantio_nass_so_usam_ids_do_catalogo_dos_eua():
    ids_eua = {l["id"] for l in _linhas(CSV_POR_PAIS["US"])}
    for nome in ("producao_condado.csv", "datas_plantio.csv"):
        usados = {l["cultura_id"] for l in _linhas(DIR_NASS / nome)}
        assert usados, nome
        assert usados <= ids_eua, f"{nome}: ids fora do catálogo dos EUA: {sorted(usados - ids_eua)}"


def test_mapa_de_culturas_nass_so_usa_ids_do_culturas_json():
    usados = {l["cultura_id"] for l in _linhas(DIR_NASS / "mapa_culturas_nass.csv")}
    assert usados
    assert usados <= _ids_json(), f"ids fora do culturas.json: {sorted(usados - _ids_json())}"


def test_tmin_critica_c_e_lida_como_numero_nos_dois_paises():
    for pais in ("BR", "US"):
        catalogo_do_pais.cache_clear()
        catalogo = catalogo_do_pais(pais)
        com_valor = [l for l in _linhas(CSV_POR_PAIS[pais]) if l["tmin_critica_c"].strip()]
        assert com_valor, f"{pais}: nenhuma cultura com tmin_critica_c"
        for l in com_valor:
            lido = catalogo[l["id"]].tmin_critica_c
            assert isinstance(lido, float), f"{pais} {l['id']}: {lido!r}"
            assert lido == float(l["tmin_critica_c"])
        for l in _linhas(CSV_POR_PAIS[pais]):
            if not l["tmin_critica_c"].strip():
                assert catalogo[l["id"]].tmin_critica_c is None  # vazio é None, nunca 0
    catalogo_do_pais.cache_clear()


def _blocos_por_pais() -> dict[str, dict[str, dict]]:
    """{id: por_pais} do culturas.json, só dos ids que têm bloco."""
    culturas = json.loads(CULTURAS_JSON.read_text(encoding="utf-8"))["culturas"]
    return {c["id"]: c["por_pais"] for c in culturas if c.get("por_pais")}


def test_todo_id_do_csv_tem_por_pais_igual_ao_csv():
    blocos = _blocos_por_pais()
    for pais in ("BR", "US"):
        for linha in _linhas(CSV_POR_PAIS[pais]):
            bloco = blocos.get(linha["id"], {}).get(pais)
            assert bloco is not None, f"{pais} {linha['id']}: falta por_pais.{pais} no culturas.json"
            assert bloco["perene"] is (linha["perene"] == "true"), f"{pais} {linha['id']}: perene"
            assert set(bloco["tipos"]) == set(filter(None, linha["tipos"].split("|"))), f"{pais} {linha['id']}: tipos"
            assert len(bloco["tipos"]) == len(set(bloco["tipos"]))


def test_todo_bloco_por_pais_tem_id_no_csv_daquele_pais():
    ids_csv = {pais: {l["id"] for l in _linhas(CSV_POR_PAIS[pais])} for pais in ("BR", "US")}
    for cid, por_pais in _blocos_por_pais().items():
        assert set(por_pais) <= set(ids_csv), f"{cid}: país desconhecido em por_pais: {sorted(set(por_pais) - set(ids_csv))}"
        for pais in por_pais:
            assert cid in ids_csv[pais], f"{cid}: por_pais.{pais} sem linha no CSV do país"


def test_montar_csv_recusa_csv_diferente_do_por_pais():
    montar = _carrega_montar()
    culturas = json.loads(CULTURAS_JSON.read_text(encoding="utf-8"))["culturas"]
    linhas = _linhas(CSV_POR_PAIS["BR"])
    assert montar.conferir_por_pais(linhas, culturas, "BR") == []
    mandioca = next(l for l in linhas if l["id"] == "mandioca")
    assert any("perene" in p for p in montar.conferir_por_pais([{**mandioca, "perene": "false"}], culturas, "BR"))
    assert any("tipos" in p for p in montar.conferir_por_pais([{**mandioca, "tipos": "comercial|cobertura"}], culturas, "BR"))
    assert any("falta por_pais" in p for p in montar.conferir_por_pais([mandioca], culturas, "US"))


def test_csvs_gerados_das_evidencias_sao_identicos_aos_versionados(tmp_path):
    montar = _carrega_montar()
    for nome, catalogo, versionado in (
        ("br.csv", DIR_CATALOGO, CSV_POR_PAIS["BR"]),
        ("eua.csv", DIR_CATALOGO / "eua", CSV_POR_PAIS["US"]),
    ):
        colunas, linhas, problemas, _avisos = montar.montar(str(catalogo))
        assert not problemas, f"{nome}: {problemas}"
        gerado = tmp_path / nome
        montar.gravar_csv(gerado, colunas, linhas)
        assert gerado.read_bytes() == versionado.read_bytes(), (
            f"{versionado} difere do gerado pelas evidências: rode "
            f"`python3 -I data/catalogo/scripts/montar_csv.py --catalogo {catalogo.relative_to(RAIZ_REPO)} --apply`"
        )
