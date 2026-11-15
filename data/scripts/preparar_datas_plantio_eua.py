"""Gera as datas usuais de plantio e colheita por estado dos EUA, o equivalente das janelas do ZARC.

Uso, da raiz do repositório:

    python data/scripts/preparar_datas_plantio_eua.py

Só biblioteca padrão.

Fonte: USDA NASS, "Field Crops Usual Planting and Harvesting Dates" (Agricultural Handbook 628,
29/10/2010, a edição mais recente). O zip com os CSVs é baixado para data/brutos/eua_nass/ se ainda
não estiver lá. São usadas as tabelas por estado (19 a 62), as únicas que trazem o feijão.

Entrada:  data/eua/nass/mapa_culturas_nass.csv   cultura_id -> nome no NASS (vários separados por "|")
Saída:    data/eua/nass/datas_plantio.csv        uma linha por cultura, nome no NASS e estado

Diferenças em relação ao ZARC: a escala é o estado (não o município), não há risco em % nem tipo de solo
ou ciclo, e as datas são "usuais" (o que os produtores fazem), não a recomendação de menor risco.
"""
import csv
import io
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BRUTO = RAIZ / "data" / "brutos" / "eua_nass" / "planting-10-29-2010.zip"
URL = ("https://esmis.nal.usda.gov/sites/default/release-files/vm40xr56k/dv13zw65p/p5547v35k/"
       "planting-10-29-2010.zip")
MAPA = RAIZ / "data" / "eua" / "nass" / "mapa_culturas_nass.csv"
SAIDA = RAIZ / "data" / "eua" / "nass" / "datas_plantio.csv"
TABELAS_POR_ESTADO = range(19, 63)

ESTADOS = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maryland": "MD", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}
# A tabela "New England" junta 6 estados; a única cultura da base nela (aveia) tem a nota "1/ Maine only".
NOTA_MAINE = "1/"

MESES = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
         "Sep": 9, "Sept": 9, "Oct": 10, "Nov": 11, "Dec": 12}
COLUNAS = ["cultura_id", "nome_nass", "uf", "area_colhida_2009_mil_acres",
           "plantio_inicio", "plantio_pico_inicio", "plantio_pico_fim", "plantio_fim",
           "colheita_inicio", "colheita_pico_inicio", "colheita_pico_fim", "colheita_fim"]


def data(texto):
    """'Mar 25' -> '03-25' (mês-dia, como o inicio_data do ZARC). '(NA)' ou vazio -> ''."""
    texto = texto.strip()
    if not texto or texto == "(NA)":
        return ""
    m = re.fullmatch(r"([A-Z][a-z]{2,3})\.? (\d{1,2})", texto)
    if not m or m.group(1) not in MESES:
        sys.exit(f"Data que não entendi na tabela do NASS: {texto!r}")
    return f"{MESES[m.group(1)]:02d}-{int(m.group(2)):02d}"


def intervalo(texto):
    """'Apr 25 - May 18' -> ('04-25', '05-18')."""
    texto = texto.strip()
    if not texto or texto == "(NA)":
        return "", ""
    partes = [p.strip() for p in texto.split("-")]
    if len(partes) != 2:
        sys.exit(f"Intervalo que não entendi na tabela do NASS: {texto!r}")
    return data(partes[0]), data(partes[1])


def baixar_se_preciso():
    if BRUTO.exists():
        return
    BRUTO.parent.mkdir(parents=True, exist_ok=True)
    print(f"Baixando {URL}")
    pedido = urllib.request.Request(URL, headers={"User-Agent": "fieldshift-dados"})
    tmp = BRUTO.with_name(BRUTO.name + ".part")
    tmp.write_bytes(urllib.request.urlopen(pedido, timeout=300).read())
    tmp.replace(BRUTO)


def ler_tabelas():
    with zipfile.ZipFile(BRUTO) as z:
        texto = z.read("fcda_all_tables.csv").decode("latin-1")  # o NASS grava em Windows-1252
    estado, linhas = None, []
    for r in csv.reader(io.StringIO(texto)):
        if len(r) < 3 or not r[0].isdigit() or int(r[0]) not in TABELAS_POR_ESTADO:
            continue
        if r[1] == "t" and "by Crop" in r[2]:
            estado = r[2].split("by Crop", 1)[1].strip(" \x96\u2013-")  # "by Crop – Iowa" (travessão)
        elif r[1] == "d" and len(r) >= 10 and r[2].strip():
            linhas.append((estado, r[2:10]))
    return linhas


def main():
    baixar_se_preciso()
    with open(MAPA, encoding="utf-8") as f:
        nomes = {n: l["cultura_id"] for l in csv.DictReader(f) for n in l["nome_nass"].split("|") if n}

    saida, achados = [], set()
    for estado, (nome, area, p_ini, p_pico, p_fim, c_ini, c_pico, c_fim) in ler_tabelas():
        nome_limpo = re.sub(r"\s+\d/(\s+\d/)*$", "", nome).strip()  # tira notas "1/", "2/ 3/"
        if nome_limpo == "Winter, wheat":  # erro de digitação numa tabela do NASS
            nome_limpo = "Wheat, winter"
        if nome_limpo not in nomes:
            continue
        if estado == "New England":
            if NOTA_MAINE not in nome:
                print(f"AVISO: {nome!r} em New England sem estado definido; ignorado", file=sys.stderr)
                continue
            uf = "ME"
        elif estado in ESTADOS:
            uf = ESTADOS[estado]
        else:
            sys.exit(f"Estado que não conheço na tabela do NASS: {estado!r}")
        pp_ini, pp_fim = intervalo(p_pico)
        cp_ini, cp_fim = intervalo(c_pico)
        saida.append([nomes[nome_limpo], nome_limpo, uf, area.strip(), data(p_ini), pp_ini, pp_fim,
                      data(p_fim), data(c_ini), cp_ini, cp_fim, data(c_fim)])
        achados.add(nome_limpo)

    faltando = sorted(set(nomes) - achados)
    if faltando:
        sys.exit(f"Nomes do mapa que não aparecem nas tabelas do NASS: {faltando}. Nada foi gravado.")
    saida.sort(key=lambda l: (l[0], l[1], l[2]))
    tmp = SAIDA.with_name(SAIDA.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUNAS)
        w.writerows(saida)
    tmp.replace(SAIDA)
    print(f"{SAIDA.relative_to(RAIZ)}: {len(saida)} linhas, {len({l[0] for l in saida})} culturas")


if __name__ == "__main__":
    main()
