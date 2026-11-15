"""Baixa do USDA NASS Quick Stats a produção por condado e por estado dos EUA, o equivalente da PAM do IBGE.

Uso, da raiz do repositório:

    NASS_API_KEY=... python data/scripts/baixar_nass_eua.py

Dependências fora da biblioteca padrão: requests

Chave (nunca no código): variável de ambiente NASS_API_KEY. É gratuita e pessoal, pedida em
https://quickstats.nass.usda.gov/api (chega por e-mail na hora).

Saídas (data/eua/nass/), no mesmo formato da PAM (data/brasil/pam/producao_municipal.csv), já em hectare
e tonelada, últimos 10 anos:
    producao_condado.csv    condado_id, cultura_id, ano, area_plantada_ha, area_colhida_ha, producao_t, rendimento_kg_ha
    producao_estado.csv     uf no lugar de condado_id. Serve onde o condado não tem dado; em Connecticut, os
                            condados atuais (planning regions 09110-09190) não existem no NASS e a fazenda usa o estado.
    fator_algodao_caroco.csv  uf, ano, fator, origem: fator que leva a pluma ao algodão em caroço

Regras:
    - O NASS esconde o número quando poucos produtores o identificariam ("(D)" e outros códigos entre
      parênteses): fica vazio, nunca 0. Se um dos componentes somados vier escondido, o total fica vazio.
    - A soma considera só os componentes publicados: se o NASS não publicar uma linha de um componente
      (ex.: trigo de primavera num condado do Kansas), o total é o dos componentes que existem.
    - Ano sem dado fica sem linha; nada é copiado de um ano para outro.
    - O rendimento é calculado (produção / área colhida) para todas as culturas terem a mesma unidade.
    - Algodão: o NASS publica a pluma (fardos de 480 lb). A PAM usa o algodão em caroço, então a produção é
      multiplicada por (pluma + caroço) / pluma do estado e do ano, das séries do próprio NASS
      (COTTON 480 LB BALES e COTTONSEED TONS). Sem o estado, usa o nacional do ano; sem o ano, a média
      nacional. O resultado fica um pouco abaixo do caroço bruto da PAM, que também conta o resíduo do
      descaroçamento, e o caroço do estado inclui o Pima.
    - O NASS não publica valor da produção por condado (sem valor_mil_reais).
"""
import csv
import datetime as dt
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "data" / "eua" / "nass"
API = "https://quickstats.nass.usda.gov/api/api_GET/"
ANOS = 10
HA_POR_ACRE = 0.40468564224
KG_POR_LB = 0.45359237
KG_POR_SHORT_TON = 907.18474

# cultura_id -> componentes somados por local e ano. Cada componente é
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
    # Quase todo o arroz dos EUA é irrigado por inundação: entra como arroz_irrigado, não como o de terras altas
    "arroz_irrigado": [("RICE - ACRES PLANTED", "RICE - ACRES HARVESTED",
                        "RICE - PRODUCTION, MEASURED IN CWT", 100 * KG_POR_LB)],
    # Upland = algodão herbáceo (Gossypium hirsutum), o da base. O Pima (G. barbadense) fica de fora.
    # Produção em pluma aqui; convertida para caroço em main() com o fator do estado.
    "algodao": [("COTTON, UPLAND - ACRES PLANTED", "COTTON, UPLAND - ACRES HARVESTED",
                 "COTTON, UPLAND - PRODUCTION, MEASURED IN 480 LB BALES", 480 * KG_POR_LB)],
    "sorgo": [("SORGHUM - ACRES PLANTED", "SORGHUM, GRAIN - ACRES HARVESTED",
               "SORGHUM, GRAIN - PRODUCTION, MEASURED IN BU", 56 * KG_POR_LB)],
    "girassol": [("SUNFLOWER, OIL TYPE - ACRES PLANTED", "SUNFLOWER, OIL TYPE - ACRES HARVESTED",
                  "SUNFLOWER, OIL TYPE - PRODUCTION, MEASURED IN LB", KG_POR_LB),
                 ("SUNFLOWER, NON-OIL TYPE - ACRES PLANTED", "SUNFLOWER, NON-OIL TYPE - ACRES HARVESTED",
                  "SUNFLOWER, NON-OIL TYPE - PRODUCTION, MEASURED IN LB", KG_POR_LB)],
    "aveia": [("OATS - ACRES PLANTED", "OATS - ACRES HARVESTED",
               "OATS - PRODUCTION, MEASURED IN BU", 32 * KG_POR_LB)],
    # O NASS trocou a série do feijão: "INCL CHICKPEAS" até 2018 e "(EXCL CHICKPEAS)" a partir de 2020
    # (2019 não tem nenhuma). Os anos não se sobrepõem; main() confere e para se algum ano vier nas duas.
    "feijao": [("BEANS, DRY EDIBLE, INCL CHICKPEAS - ACRES PLANTED",
                "BEANS, DRY EDIBLE, INCL CHICKPEAS - ACRES HARVESTED",
                "BEANS, DRY EDIBLE, INCL CHICKPEAS - PRODUCTION, MEASURED IN CWT", 100 * KG_POR_LB),
               ("BEANS, DRY EDIBLE, (EXCL CHICKPEAS) - ACRES PLANTED",
                "BEANS, DRY EDIBLE, (EXCL CHICKPEAS) - ACRES HARVESTED",
                "BEANS, DRY EDIBLE, (EXCL CHICKPEAS) - PRODUCTION, MEASURED IN CWT", 100 * KG_POR_LB)],
}
ALGODAO_PLUMA = "COTTON - PRODUCTION, MEASURED IN 480 LB BALES"   # pluma, upland + Pima
ALGODAO_CAROCO = "COTTON, COTTONSEED - PRODUCTION, MEASURED IN TONS"  # caroço (semente), short tons
FAIXA_FATOR = (2.0, 3.5)  # (pluma + caroço) / pluma fica perto de 2,2-2,3 no NASS; fora disso é dado estranho

LIMITE_API = 50000  # registros por consulta no Quick Stats
PAUSA_S = 1.0  # entre consultas: o firewall do NASS bloqueia (403) rajadas de chamadas
TENTATIVAS = 4  # por consulta, com espera de 30, 60, 90 e 120 s antes de desistir
ESCONDIDO = object()  # valor que o NASS não publica: o total fica vazio
COLUNAS = ["area_plantada_ha", "area_colhida_ha", "producao_t"]


def numero(texto, desconhecidos):
    """Número do NASS, ou None quando não publicado. Todo código entre parênteses ("(D)", "(Z)", "(H)"...)
    é "sem dado"; os que não estão na lista conhecida são contados para o aviso no fim."""
    texto = texto.strip()
    if not texto or texto.startswith("("):
        if texto not in {"", "(D)", "(NA)", "(X)", "(Z)", "(S)"}:
            desconhecidos[texto] += 1
        return None
    return float(texto.replace(",", ""))


def chamar(sessao, metodo, params):
    """Chama a API sem deixar a chave aparecer em mensagem de erro.

    O firewall do NASS devolve 403 em HTML (e às vezes 429/5xx) quando chegam muitas consultas seguidas:
    nesse caso espera e tenta de novo. Chave inválida é o 401 com {"error": ["unauthorized"]}."""
    time.sleep(PAUSA_S)
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            r = sessao.get(API.replace("api_GET", metodo), params=params, timeout=300)
        except requests.RequestException as e:
            r, erro = None, type(e).__name__
        if r is not None and r.status_code == 401:
            sys.exit("O NASS recusou a chave: confira a NASS_API_KEY.")
        if r is not None and r.ok:
            return r.json()
        if r is not None and r.status_code not in (403, 429, 500, 502, 503, 504):
            sys.exit(f"O NASS devolveu HTTP {r.status_code} para {params.get('short_desc')!r}: {r.text[:200]}")
        motivo = f"HTTP {r.status_code}" if r is not None else erro
        espera = 30 * tentativa
        print(f"  NASS ocupado ({motivo}); nova tentativa {tentativa}/{TENTATIVAS} em {espera} s", file=sys.stderr)
        time.sleep(espera)
    sys.exit(f"O NASS não respondeu depois de {TENTATIVAS} tentativas ({params.get('short_desc')!r}). "
             "Nada foi gravado; rode de novo mais tarde.")


def consultar(sessao, chave, short_desc, ano_inicial, nivel):
    params = {
        "key": chave, "format": "JSON", "source_desc": "SURVEY", "agg_level_desc": nivel,
        "freq_desc": "ANNUAL", "reference_period_desc": "YEAR", "domain_desc": "TOTAL",
        "short_desc": short_desc, "year__GE": ano_inicial,
    }
    total = int(chamar(sessao, "get_counts", params)["count"])
    if total == 0:
        return []
    if total > LIMITE_API:
        sys.exit(f"{short_desc!r} tem {total} registros, acima do limite de {LIMITE_API} por consulta.")
    return chamar(sessao, "api_GET", params).get("data", [])


def local(d, nivel):
    """condado_id (FIPS de 5 dígitos) no nível COUNTY, sigla do estado no STATE, "US" no NATIONAL."""
    if nivel == "COUNTY":
        if d.get("county_code") in ("", "998"):  # 998 = "outros condados" somados pelo NASS
            return None
        return d["state_fips_code"].zfill(2) + d["county_code"].zfill(3)
    if nivel == "STATE":
        return d["state_alpha"]
    return "US"


def coletar(sessao, chave, ano_inicial, nivel, desconhecidos):
    """(local, cultura_id, ano) -> {coluna: valor}, somando os componentes de cada cultura."""
    linhas = defaultdict(dict)
    componente_do_ano = defaultdict(set)  # (cultura, local, ano) -> componentes com dado (checa o feijão)
    for cultura, componentes in SERIES.items():
        for i, (plantada, colhida, producao, kg_por_unidade) in enumerate(componentes):
            for coluna, serie, fator in (("area_plantada_ha", plantada, HA_POR_ACRE),
                                         ("area_colhida_ha", colhida, HA_POR_ACRE),
                                         ("producao_t", producao, kg_por_unidade / 1000)):
                dados = consultar(sessao, chave, serie, ano_inicial, nivel)
                print(f"[{nivel}] {cultura}: {serie}: {len(dados)} registros")
                if not dados:
                    print(f"AVISO: nenhum dado ({nivel}) para {serie!r}", file=sys.stderr)
                for d in dados:
                    onde = local(d, nivel)
                    if onde is None:
                        continue
                    ano = int(d["year"])
                    componente_do_ano[(cultura, onde, ano)].add(i)
                    celulas = linhas[(onde, cultura, ano)]
                    valor = numero(d["Value"], desconhecidos)
                    if valor is None or celulas.get(coluna) is ESCONDIDO:
                        celulas[coluna] = ESCONDIDO
                    else:
                        celulas[coluna] = celulas.get(coluna, 0) + valor * fator
    duplos = [k for k, v in componente_do_ano.items() if k[0] == "feijao" and len(v) > 1]
    if duplos:
        sys.exit(f"Feijão com as séries INCL e EXCL CHICKPEAS no mesmo ano ({nivel}): {duplos[:5]}. "
                 "Somar duplicaria a produção. Nada foi gravado.")
    return linhas


def fatores_algodao(sessao, chave, ano_inicial, desconhecidos):
    """(uf, ano) -> (fator, origem), com (pluma + caroço) / pluma do NASS."""
    def serie(short_desc, kg_por_unidade, nivel):
        valores = {}
        for d in consultar(sessao, chave, short_desc, ano_inicial, nivel):
            v = numero(d["Value"], desconhecidos)
            if v is not None:
                valores[(local(d, nivel), int(d["year"]))] = v * kg_por_unidade
        return valores

    fatores = {}
    for nivel in ("STATE", "NATIONAL"):
        pluma = serie(ALGODAO_PLUMA, 480 * KG_POR_LB, nivel)
        caroco = serie(ALGODAO_CAROCO, KG_POR_SHORT_TON, nivel)
        for chave_local, kg_pluma in pluma.items():
            if chave_local in caroco and kg_pluma > 0:
                fator = (kg_pluma + caroco[chave_local]) / kg_pluma
                if FAIXA_FATOR[0] <= fator <= FAIXA_FATOR[1]:
                    fatores[chave_local] = (fator, "estado" if nivel == "STATE" else "nacional")
                else:
                    print(f"AVISO: fator do algodão fora da faixa em {chave_local}: {fator:.2f}; ignorado",
                          file=sys.stderr)
    nacionais = [f for (onde, _), (f, _) in fatores.items() if onde == "US"]
    if not nacionais:
        sys.exit("Sem fator nacional do algodão (pluma e caroço do NASS). Nada foi gravado.")
    media = sum(nacionais) / len(nacionais)
    return fatores, media


def fator_para(fatores, media, uf, ano):
    if (uf, ano) in fatores:
        return fatores[(uf, ano)]
    if ("US", ano) in fatores:
        return fatores[("US", ano)][0], "nacional"
    return media, "media_nacional"


def gravar(caminho, cabecalho, linhas):
    """Escreve num .tmp e troca de uma vez: o arquivo final nunca fica pela metade."""
    tmp = caminho.with_name(caminho.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cabecalho)
        w.writerows(linhas)
    tmp.replace(caminho)


def linhas_csv(dados, uf_de, fatores, media, usados):
    saida = []
    for (onde, cultura, ano), v in sorted(dados.items()):
        plantada, colhida, producao = (None if v.get(c) is ESCONDIDO else v.get(c) for c in COLUNAS)
        if cultura == "algodao" and producao is not None:
            fator, origem = fator_para(fatores, media, uf_de(onde), ano)
            usados[(uf_de(onde), ano)] = (fator, origem)
            producao *= fator  # pluma -> caroço
        rendimento = round(producao * 1000 / colhida) if colhida and producao is not None else None
        saida.append([onde, cultura, ano, *("" if x is None else round(x, 1) for x in (plantada, colhida, producao)),
                      "" if rendimento is None else rendimento])
    return saida


def main():
    sys.stdout.reconfigure(line_buffering=True)
    chave = os.environ.get("NASS_API_KEY")
    if not chave:
        sys.exit("Defina NASS_API_KEY (chave gratuita em https://quickstats.nass.usda.gov/api).")
    ano_inicial = dt.date.today().year - ANOS
    sessao = requests.Session()
    desconhecidos = Counter()

    # Coleta tudo antes de gravar qualquer arquivo.
    condados = coletar(sessao, chave, ano_inicial, "COUNTY", desconhecidos)
    estados = coletar(sessao, chave, ano_inicial, "STATE", desconhecidos)
    if not condados or not estados:
        sys.exit("Nenhum dado retornado. Nada foi gravado.")
    fatores, media = fatores_algodao(sessao, chave, ano_inicial, desconhecidos)

    # FIPS do estado (2 primeiros dígitos do condado) -> sigla, da malha de condados (baixar_condados_eua.py)
    with open(RAIZ / "data" / "eua" / "condados" / "condados.csv", encoding="utf-8") as f:
        fips_uf = {l["condado_id"][:2]: l["uf"] for l in csv.DictReader(f)}

    usados = {}
    cab = ["area_plantada_ha", "area_colhida_ha", "producao_t", "rendimento_kg_ha"]
    l_condado = linhas_csv(condados, lambda c: fips_uf.get(c[:2], ""), fatores, media, usados)
    l_estado = linhas_csv(estados, lambda uf: uf, fatores, media, usados)

    PASTA.mkdir(parents=True, exist_ok=True)
    gravar(PASTA / "producao_condado.csv", ["condado_id", "cultura_id", "ano", *cab], l_condado)
    gravar(PASTA / "producao_estado.csv", ["uf", "cultura_id", "ano", *cab], l_estado)
    gravar(PASTA / "fator_algodao_caroco.csv", ["uf", "ano", "fator", "origem"],
           [[uf, ano, round(f, 3), o] for (uf, ano), (f, o) in sorted(usados.items())])

    for nome, linhas in (("producao_condado.csv", l_condado), ("producao_estado.csv", l_estado)):
        print(f"data/eua/nass/{nome}: {len(linhas)} linhas, {(PASTA / nome).stat().st_size / 1e6:.1f} MB")
    # Anos com dado por cultura: mostra as lacunas do próprio NASS (ex.: feijão sem 2019)
    anos = defaultdict(Counter)
    for l in l_condado:
        anos[l[1]][l[2]] += 1
    for cultura in sorted(anos):
        faltam = [a for a in range(ano_inicial, dt.date.today().year) if a not in anos[cultura]]
        print(f"  {cultura}: {dict(sorted(anos[cultura].items()))}" + (f"  SEM DADO: {faltam}" if faltam else ""))
    if desconhecidos:
        print(f"AVISO: códigos do NASS fora da lista, tratados como sem dado: {dict(desconhecidos)}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
