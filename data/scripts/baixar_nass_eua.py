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

# cultura_id -> componentes somados por condado e ano. Cada componente é
# (short_desc da área plantada, da área colhida, da produção, kg por unidade da produção).
# O short_desc é o nome exato da série no Quick Stats (conferido por condado com get_counts).
# Milho e sorgo: área plantada inclui a silagem (o NASS não separa), colhida e produção são só grão.
SERIES = {
    "milho": [("CORN - ACRES PLANTED", "CORN, GRAIN - ACRES HARVESTED",
               "CORN, GRAIN - PRODUCTION, MEASURED IN BU", 56 * KG_POR_LB)],
    "soja": [("SOYBEANS - ACRES PLANTED", "SOYBEANS - ACRES HARVESTED",
              "SOYBEANS - PRODUCTION, MEASURED IN BU", 60 * KG_POR_LB)],
    # Por condado o NASS só publica o trigo separado: inverno + primavera (sem o durum, outra espécie)
    "trigo": [("WHEAT, WINTER - ACRES PLANTED", "WHEAT, WINTER - ACRES HARVESTED",
               "WHEAT, WINTER - PRODUCTION, MEASURED IN BU", 60 * KG_POR_LB),
              ("WHEAT, SPRING, (EXCL DURUM) - ACRES PLANTED", "WHEAT, SPRING, (EXCL DURUM) - ACRES HARVESTED",
               "WHEAT, SPRING, (EXCL DURUM) - PRODUCTION, MEASURED IN BU", 60 * KG_POR_LB)],
    "arroz": [("RICE - ACRES PLANTED", "RICE - ACRES HARVESTED",
               "RICE - PRODUCTION, MEASURED IN CWT", 100 * KG_POR_LB)],
    # Upland = algodão herbáceo (Gossypium hirsutum), o da base. O Pima (G. barbadense) fica de fora.
    "algodao": [("COTTON, UPLAND - ACRES PLANTED", "COTTON, UPLAND - ACRES HARVESTED",
                 "COTTON, UPLAND - PRODUCTION, MEASURED IN 480 LB BALES", 480 * KG_POR_LB)],  # pluma
    "sorgo": [("SORGHUM - ACRES PLANTED", "SORGHUM, GRAIN - ACRES HARVESTED",
               "SORGHUM, GRAIN - PRODUCTION, MEASURED IN BU", 56 * KG_POR_LB)],
    "girassol": [("SUNFLOWER, OIL TYPE - ACRES PLANTED", "SUNFLOWER, OIL TYPE - ACRES HARVESTED",
                  "SUNFLOWER, OIL TYPE - PRODUCTION, MEASURED IN LB", KG_POR_LB),
                 ("SUNFLOWER, NON-OIL TYPE - ACRES PLANTED", "SUNFLOWER, NON-OIL TYPE - ACRES HARVESTED",
                  "SUNFLOWER, NON-OIL TYPE - PRODUCTION, MEASURED IN LB", KG_POR_LB)],
    "aveia": [("OATS - ACRES PLANTED", "OATS - ACRES HARVESTED",
               "OATS - PRODUCTION, MEASURED IN BU", 32 * KG_POR_LB)],
    "feijao": [("BEANS, DRY EDIBLE, INCL CHICKPEAS - ACRES PLANTED",
                "BEANS, DRY EDIBLE, INCL CHICKPEAS - ACRES HARVESTED",
                "BEANS, DRY EDIBLE, INCL CHICKPEAS - PRODUCTION, MEASURED IN CWT", 100 * KG_POR_LB)],
}
LIMITE_API = 50000  # registros por consulta no Quick Stats
ESCONDIDO = object()  # valor que o NASS não publica: o total do condado fica vazio
SEM_DADO = {"(D)", "(NA)", "(X)", "(Z)", "(S)", ""}  # (Z) é "menos que meia unidade": vazio, não 0


def numero(texto):
    texto = texto.strip()
    if texto in SEM_DADO:
        return None
    return float(texto.replace(",", ""))


def chamar(sessao, metodo, params):
    """Chama a API sem deixar a chave aparecer em mensagem de erro."""
    try:
        r = sessao.get(API.replace("api_GET", metodo), params=params, timeout=300)
    except requests.RequestException as e:
        sys.exit(f"Falha de rede no NASS ({type(e).__name__}).")
    if r.status_code in (401, 403):
        sys.exit("O NASS recusou a chave: confira a NASS_API_KEY.")
    if not r.ok:
        sys.exit(f"O NASS devolveu HTTP {r.status_code} para {params.get('short_desc')!r}: {r.text[:200]}")
    return r.json()


def consultar(sessao, chave, short_desc, ano_inicial):
    params = {
        "key": chave, "format": "JSON", "source_desc": "SURVEY", "agg_level_desc": "COUNTY",
        "freq_desc": "ANNUAL", "reference_period_desc": "YEAR", "domain_desc": "TOTAL",
        "short_desc": short_desc, "year__GE": ano_inicial,
    }
    total = int(chamar(sessao, "get_counts", params)["count"])
    if total == 0:
        return []
    if total > LIMITE_API:
        sys.exit(f"{short_desc!r} tem {total} registros, acima do limite de {LIMITE_API} por consulta.")
    return chamar(sessao, "api_GET", params).get("data", [])


def main():
    sys.stdout.reconfigure(line_buffering=True)
    chave = os.environ.get("NASS_API_KEY")
    if not chave:
        sys.exit("Defina NASS_API_KEY (chave gratuita em https://quickstats.nass.usda.gov/api).")
    ano_inicial = dt.date.today().year - ANOS
    sessao = requests.Session()

    linhas = defaultdict(dict)  # (condado_id, cultura_id, ano) -> colunas
    for cultura, componentes in SERIES.items():
        for plantada, colhida, producao, kg_por_unidade in componentes:
            for coluna, serie, fator in (("area_plantada_ha", plantada, HA_POR_ACRE),
                                         ("area_colhida_ha", colhida, HA_POR_ACRE),
                                         ("producao_t", producao, kg_por_unidade / 1000)):
                dados = consultar(sessao, chave, serie, ano_inicial)
                print(f"{cultura}: {serie}: {len(dados)} registros")
                if not dados:
                    print(f"AVISO: nenhum dado por condado para {serie!r}", file=sys.stderr)
                for d in dados:
                    if d.get("county_code") in ("", "998"):  # 998 = "outros condados" somados pelo NASS
                        continue
                    condado = d["state_fips_code"].zfill(2) + d["county_code"].zfill(3)
                    celulas = linhas[(condado, cultura, int(d["year"]))]
                    valor = numero(d["Value"])
                    if valor is None or celulas.get(coluna) is ESCONDIDO:
                        celulas[coluna] = ESCONDIDO
                    else:
                        celulas[coluna] = celulas.get(coluna, 0) + valor * fator

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
            plantada, colhida, producao = (None if v.get(c) is ESCONDIDO else v.get(c)
                                           for c in ("area_plantada_ha", "area_colhida_ha", "producao_t"))
            rendimento = round(producao * 1000 / colhida) if colhida and producao is not None else None
            w.writerow([condado, cultura, ano, *("" if x is None else round(x, 1) for x in (
                plantada, colhida, producao)), "" if rendimento is None else rendimento])
    tmp.replace(SAIDA)
    print(f"{SAIDA.relative_to(RAIZ)}: {len(linhas)} linhas, {SAIDA.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
