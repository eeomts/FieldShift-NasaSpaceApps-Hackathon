"""Baixa do USDA NASS Quick Stats a produção por condado dos EUA, o equivalente da PAM do IBGE.

Uso, da raiz do repositório:

    NASS_API_KEY=... python data/scripts/baixar_nass_eua.py

Dependências fora da biblioteca padrão: requests

Chave (nunca no código): variável de ambiente NASS_API_KEY. É gratuita e pessoal, pedida em
https://quickstats.nass.usda.gov/api (chega por e-mail na hora).

Saída: data/eua/nass/producao_condado.csv, no mesmo formato da PAM (data/brasil/pam/producao_municipal.csv),
já convertido para hectare e tonelada. Uma linha por condado × cultura × ano, últimos 10 anos.
    condado_id, cultura_id, ano, area_plantada_ha, area_colhida_ha, producao_t, rendimento_kg_ha

Diferenças em relação à PAM: o NASS não publica valor da produção por condado (sem valor_mil_reais),
e esconde o número quando poucos produtores o identificariam ("(D)"): esse caso fica vazio, nunca 0.
O rendimento é calculado (produção / área colhida) para todas as culturas terem a mesma unidade.
"""
import csv
import datetime as dt
import os
import sys
from collections import defaultdict
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "data" / "eua" / "nass" / "producao_condado.csv"
API = "https://quickstats.nass.usda.gov/api/api_GET/"
ANOS = 10
HA_POR_ACRE = 0.40468564224
KG_POR_LB = 0.45359237

# cultura_id -> (short_desc da área plantada, da área colhida, da produção, kg por unidade da produção)
# O short_desc é o nome exato da série no Quick Stats. Milho e sorgo usam só o grão (sem silagem).
SERIES = {
    "milho": ("CORN - ACRES PLANTED", "CORN, GRAIN - ACRES HARVESTED",
              "CORN, GRAIN - PRODUCTION, MEASURED IN BU", 56 * KG_POR_LB),
    "soja": ("SOYBEANS - ACRES PLANTED", "SOYBEANS - ACRES HARVESTED",
             "SOYBEANS - PRODUCTION, MEASURED IN BU", 60 * KG_POR_LB),
    "trigo": ("WHEAT - ACRES PLANTED", "WHEAT - ACRES HARVESTED",
              "WHEAT - PRODUCTION, MEASURED IN BU", 60 * KG_POR_LB),
    "arroz": ("RICE - ACRES PLANTED", "RICE - ACRES HARVESTED",
              "RICE - PRODUCTION, MEASURED IN CWT", 100 * KG_POR_LB),
    "algodao": ("COTTON - ACRES PLANTED", "COTTON - ACRES HARVESTED",
                "COTTON - PRODUCTION, MEASURED IN 480 LB BALES", 480 * KG_POR_LB),  # pluma
    "sorgo": ("SORGHUM - ACRES PLANTED", "SORGHUM, GRAIN - ACRES HARVESTED",
              "SORGHUM, GRAIN - PRODUCTION, MEASURED IN BU", 56 * KG_POR_LB),
    "girassol": ("SUNFLOWER - ACRES PLANTED", "SUNFLOWER - ACRES HARVESTED",
                 "SUNFLOWER - PRODUCTION, MEASURED IN LB", KG_POR_LB),
    "aveia": ("OATS - ACRES PLANTED", "OATS - ACRES HARVESTED",
              "OATS - PRODUCTION, MEASURED IN BU", 32 * KG_POR_LB),
    "feijao": ("BEANS, DRY EDIBLE, INCL CHICKPEAS - ACRES PLANTED",
               "BEANS, DRY EDIBLE, INCL CHICKPEAS - ACRES HARVESTED",
               "BEANS, DRY EDIBLE, INCL CHICKPEAS - PRODUCTION, MEASURED IN CWT", 100 * KG_POR_LB),
}
SEM_DADO = {"(D)", "(NA)", "(X)", "(Z)", "(S)", ""}  # (Z) é "menos que meia unidade": vazio, não 0


def numero(texto):
    texto = texto.strip()
    if texto in SEM_DADO:
        return None
    return float(texto.replace(",", ""))


def consultar(sessao, chave, short_desc, ano_inicial):
    params = {
        "key": chave, "format": "JSON", "source_desc": "SURVEY", "agg_level_desc": "COUNTY",
        "freq_desc": "ANNUAL", "reference_period_desc": "YEAR", "domain_desc": "TOTAL",
        "short_desc": short_desc, "year__GE": ano_inicial,
    }
    r = sessao.get(API, params=params, timeout=300)
    if r.status_code == 400 and "no data" in r.text.lower():
        return []
    if r.status_code in (401, 403):
        sys.exit("O NASS recusou a chave: confira a NASS_API_KEY.")
    r.raise_for_status()
    return r.json().get("data", [])


def main():
    sys.stdout.reconfigure(line_buffering=True)
    chave = os.environ.get("NASS_API_KEY")
    if not chave:
        sys.exit("Defina NASS_API_KEY (chave gratuita em https://quickstats.nass.usda.gov/api).")
    ano_inicial = dt.date.today().year - ANOS
    sessao = requests.Session()

    linhas = defaultdict(dict)  # (condado_id, cultura_id, ano) -> colunas
    for cultura, (plantada, colhida, producao, kg_por_unidade) in SERIES.items():
        for coluna, serie, fator in (("area_plantada_ha", plantada, HA_POR_ACRE),
                                     ("area_colhida_ha", colhida, HA_POR_ACRE),
                                     ("producao_t", producao, kg_por_unidade / 1000)):
            dados = consultar(sessao, chave, serie, ano_inicial)
            print(f"{cultura}: {serie}: {len(dados)} registros")
            if not dados:
                print(f"AVISO: nenhum dado para {serie!r}; confira o nome da série", file=sys.stderr)
            for d in dados:
                if d.get("county_code") in ("", "998"):  # 998 = "outros condados" somados pelo NASS
                    continue
                condado = d["state_fips_code"].zfill(2) + d["county_code"].zfill(3)
                valor = numero(d["Value"])
                chave_linha = (condado, cultura, int(d["year"]))
                linhas[chave_linha][coluna] = None if valor is None else round(valor * fator, 1)

    if not linhas:
        sys.exit("Nenhum dado retornado. Nada foi gravado.")
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tmp = SAIDA.with_name(SAIDA.name + ".tmp")
    colunas = ["condado_id", "cultura_id", "ano", "area_plantada_ha", "area_colhida_ha",
               "producao_t", "rendimento_kg_ha"]
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(colunas)
        for (condado, cultura, ano), v in sorted(linhas.items()):
            colhida, producao = v.get("area_colhida_ha"), v.get("producao_t")
            rendimento = round(producao * 1000 / colhida) if colhida and producao is not None else None
            w.writerow([condado, cultura, ano, *("" if x is None else x for x in (
                v.get("area_plantada_ha"), colhida, producao, rendimento))])
    tmp.replace(SAIDA)
    print(f"{SAIDA.relative_to(RAIZ)}: {len(linhas)} linhas, {SAIDA.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
