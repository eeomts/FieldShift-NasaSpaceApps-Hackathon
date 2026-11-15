"""Monta o culturas.csv de um catálogo a partir das evidências e valida o resultado.

No catálogo dos EUA (data/catalogo/eua/) a fonte da verdade são os arquivos
evidencias/<id>.json: cada agente escreve só o arquivo da sua cultura, e este
script junta tudo no CSV, sem conflito entre agentes. As colunas seguem o
cabeçalho do catálogo do Brasil (data/catalogo/culturas.csv) mais as colunas
extras do país (EXTRAS).

Uso (na raiz do repositório):
    python3 -I data/catalogo/scripts/montar_csv.py --catalogo data/catalogo/eua            # só valida
    python3 -I data/catalogo/scripts/montar_csv.py --catalogo data/catalogo/eua --apply    # grava o CSV

Validações: id existe em agroia/base/culturas.json; todas as colunas presentes;
números válidos; mínimo <= máximo; kc_medio <= 1,25; categorias da régua;
tipos coerentes com fixa_nitrogenio e raiz_profunda; fontes preenchidas; nenhum
caminho temporário.
"""
import argparse
import csv
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
BASE_BR = os.path.join(ROOT, "data", "catalogo", "culturas.csv")
CATALOGO_APP = os.path.join(ROOT, "agroia", "base", "culturas.json")
EXTRAS = ["codigo_nass", "calendario_usda"]
FIXAS = {"id", "nome", "nome_cientifico", "familia_botanica"}
NUM = ["ciclo_dias_min", "ciclo_dias_max", "graus_dia_ciclo_min", "graus_dia_ciclo_max", "temp_base_c",
       "temp_otima_min_c", "temp_otima_max_c", "tmax_critica_c", "agua_ciclo_mm_min", "agua_ciclo_mm_max",
       "kc_inicial", "kc_medio", "kc_final", "profundidade_raiz_m"]
PARES = [("ciclo_dias_min", "ciclo_dias_max"), ("graus_dia_ciclo_min", "graus_dia_ciclo_max"),
         ("agua_ciclo_mm_min", "agua_ciclo_mm_max"), ("temp_otima_min_c", "temp_otima_max_c")]
ENUMS = {"perene": {"true", "false"}, "sensivel_geada": {"true", "false"}, "fixa_nitrogenio": {"true", "false"},
         "raiz_profunda": {"true", "false"}, "cobertura_solo": {"baixa", "media", "alta", ""},
         "aporte_biomassa": {"baixo", "medio", "alto", ""}, "valor_forrageiro": {"nenhum", "baixo", "medio", "alto", ""},
         "confianca_parametros": {"baixa", "media", "alta"}}
TIPOS = {"comercial", "cobertura", "forrageira", "fixadora_n", "raiz_profunda", "tolerante_seca"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--catalogo", required=True, help="pasta do catálogo (ex.: data/catalogo/eua)")
    ap.add_argument("--apply", action="store_true", help="grava o culturas.csv")
    args = ap.parse_args()

    with open(BASE_BR, encoding="utf-8") as f:
        colunas = next(csv.reader(f)) + EXTRAS
    with open(CATALOGO_APP, encoding="utf-8") as f:
        ids_app = {c["id"] for c in json.load(f)["culturas"]}

    linhas, problemas = [], []
    for p in sorted(glob.glob(os.path.join(args.catalogo, "evidencias", "*.json"))):
        with open(p, encoding="utf-8") as f:
            texto = f.read()
        ev = json.loads(texto)
        cid = ev["id"]
        r = {c: str(ev.get("valores", {}).get(c, ev.get(c, ""))).strip() for c in colunas}
        r["id"] = cid
        for c in FIXAS - {"id"}:
            r[c] = str(ev.get(c, ev.get("valores", {}).get(c, ""))).strip()

        def erro(msg):
            problemas.append(f"{cid}: {msg}")

        if cid not in ids_app:
            erro("id não existe em agroia/base/culturas.json")
        faltam = [c for c in colunas if c not in ev.get("valores", {}) and c not in FIXAS and c not in EXTRAS]
        if faltam:
            erro(f"valores sem {faltam}")
        for c in NUM:
            if r[c]:
                try:
                    float(r[c])
                except ValueError:
                    erro(f"{c} não numérico: {r[c]!r}")
        for a, b in PARES:
            try:
                if r[a] and r[b] and float(r[a]) > float(r[b]):
                    erro(f"{a} > {b}")
            except ValueError:
                pass
        try:
            if r["kc_medio"] and float(r["kc_medio"]) > 1.25:
                erro("kc_medio > 1,25 (limite do FAO-56 eq. 72)")
        except ValueError:
            pass
        for c, ok in ENUMS.items():
            if r[c] not in ok:
                erro(f"{c} inválido: {r[c]!r}")
        tipos = set(filter(None, r["tipos"].split("|")))
        if not tipos <= TIPOS:
            erro(f"tipos inválidos: {sorted(tipos - TIPOS)}")
        if ("fixadora_n" in tipos) != (r["fixa_nitrogenio"] == "true"):
            erro("tipos x fixa_nitrogenio incoerentes")
        if ("raiz_profunda" in tipos) != (r["raiz_profunda"] == "true"):
            erro("tipos x raiz_profunda incoerentes")
        if not r["fontes"] or "RASCUNHO" in r["fontes"]:
            erro("fontes vazia ou rascunho")
        if "scratchpad" in texto or "/tmp/" in texto:
            erro("caminho temporário no arquivo de evidência")
        linhas.append(r)

    print(f"{len(linhas)} cultura(s), {len(colunas)} colunas")
    for p in problemas:
        print("  PROBLEMA", p)
    if args.apply:
        if problemas:
            raise SystemExit("CSV não gravado: corrija os problemas acima.")
        with open(os.path.join(args.catalogo, "culturas.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=colunas, lineterminator="\n")
            w.writeheader()
            w.writerows(linhas)
        print("culturas.csv gravado")
    elif problemas:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
