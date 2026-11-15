"""Baixa do Censo dos EUA (TIGERweb) a lista e os polígonos dos condados, o equivalente da malha municipal do IBGE.

Uso, da raiz do repositório:

    python data/scripts/baixar_condados_eua.py

Dependências fora da biblioteca padrão: requests

Saídas (sobrescritas a cada execução):
    data/eua/condados/condados.csv       condado_id (FIPS de 5 dígitos), nome, uf (sigla do estado)
    data/eua/condados/condados.geojson   polígonos simplificados (~1 km), com condado_id em properties

Só os 50 estados e o Distrito de Colúmbia (territórios como Porto Rico ficam de fora).
O condado faz nos EUA o papel do município: liga a fazenda ao NASS (produção) e às datas de plantio.
"""
import csv
import json
import sys
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "data" / "eua" / "condados"
URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query"
POR_PAGINA = 200
SIMPLIFICACAO_GRAUS = 0.01  # ~1 km: basta para achar o condado de um ponto e deixa o arquivo pequeno
MINIMO_CONDADOS = 3100      # menos que isso é resposta incompleta

# FIPS do estado -> sigla (50 estados + DC). Tabela fixa do padrão FIPS 5-2.
ESTADOS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
    "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
    "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
    "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
    "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}


def baixar_pagina(sessao, inicio):
    params = {
        "where": "1=1", "outFields": "GEOID,NAME,STATE", "f": "geojson", "outSR": 4326,
        "maxAllowableOffset": SIMPLIFICACAO_GRAUS, "geometryPrecision": 4, "orderByFields": "GEOID",
        "resultOffset": inicio, "resultRecordCount": POR_PAGINA,
    }
    for tentativa in range(5):
        try:
            r = sessao.get(URL, params=params, timeout=300)
            r.raise_for_status()
            dados = r.json()
            if "features" not in dados:
                raise ValueError(f"resposta sem features: {str(dados)[:200]}")
            return dados["features"]
        except (requests.RequestException, ValueError) as e:
            print(f"  página {inicio}: tentativa {tentativa + 1} falhou ({e})", file=sys.stderr)
    sys.exit(f"O TIGERweb não respondeu a página {inicio}. Nada foi gravado.")


def gravar(destino, escrever):
    """Escreve num .tmp e troca de uma vez: o arquivo final nunca fica pela metade."""
    tmp = destino.with_name(destino.name + ".tmp")
    escrever(tmp)
    tmp.replace(destino)


def main():
    sys.stdout.reconfigure(line_buffering=True)
    sessao = requests.Session()
    sessao.headers["User-Agent"] = "fieldshift-dados"

    print("Baixando os condados do TIGERweb...")
    features, inicio = [], 0
    while True:
        pagina = baixar_pagina(sessao, inicio)
        features += pagina
        if len(pagina) < POR_PAGINA:
            break
        inicio += POR_PAGINA

    vistos, condados = set(), []
    for ft in features:
        p = ft["properties"]
        if p["STATE"] not in ESTADOS or p["GEOID"] in vistos or not ft.get("geometry"):
            continue
        vistos.add(p["GEOID"])
        ft["properties"] = {"condado_id": p["GEOID"]}
        condados.append((p, ft))
    if len(condados) < MINIMO_CONDADOS:
        sys.exit(f"Resposta incompleta do TIGERweb: {len(condados)} condados. Nada foi gravado.")
    condados.sort(key=lambda c: c[0]["GEOID"])

    SAIDA.mkdir(parents=True, exist_ok=True)

    def escrever_csv(caminho):
        with open(caminho, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["condado_id", "nome", "uf"])
            for p, _ in condados:
                w.writerow([p["GEOID"], p["NAME"], ESTADOS[p["STATE"]]])

    def escrever_geojson(caminho):
        malha = {"type": "FeatureCollection", "features": [ft for _, ft in condados]}
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(malha, f, ensure_ascii=False, separators=(",", ":"))

    gravar(SAIDA / "condados.csv", escrever_csv)
    gravar(SAIDA / "condados.geojson", escrever_geojson)
    tamanho_mb = (SAIDA / "condados.geojson").stat().st_size / 1e6
    print(f"condados.csv e condados.geojson: {len(condados)} condados, {tamanho_mb:.1f} MB")


if __name__ == "__main__":
    main()
