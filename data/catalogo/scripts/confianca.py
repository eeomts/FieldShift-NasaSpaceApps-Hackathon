"""Recalcula `confianca_parametros` a partir do campo `origem` das evidências.

Regra (ver data/catalogo/evidencias/README.md): conta as colunas do filtro do
motor cuja origem é estudo_unico, calculo, proxy, convencao_sem_fonte ou
vazio_nao_sei. 0 = alta, 1-2 = media, 3 ou mais = baixa.

Uso (na raiz do repositório):
    python3 -I data/catalogo/scripts/confianca.py                         # Brasil, só mostra
    python3 -I data/catalogo/scripts/confianca.py --catalogo data/catalogo/eua --apply

Com --apply grava `confianca_calculo`, `valores.confianca_parametros` e uma
linha em `mudancas` quando o nível muda (idempotente). O CSV é atualizado se
existir; no catálogo dos EUA, rode depois o montar_csv.py.
"""
import argparse
import csv
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
FILTRO = ("temp_base_c", "ciclo_dias_min", "ciclo_dias_max", "graus_dia_ciclo_min", "graus_dia_ciclo_max",
          "agua_ciclo_mm_min", "agua_ciclo_mm_max", "kc_inicial", "kc_medio", "kc_final", "profundidade_raiz_m")
LACUNA = {"estudo_unico", "calculo", "proxy", "convencao_sem_fonte", "vazio_nao_sei"}
TIPOS = LACUNA | {"medido", "publicado", "convencao_com_fonte", "vazio_nao_se_aplica"}
REGRA = ("conta colunas do filtro (inclui graus_dia_ciclo_min/max) com origem estudo_unico, calculo, proxy, "
         "convencao_sem_fonte ou vazio_nao_sei: 0 = alta, 1-2 = media, 3+ = baixa")


def nivel(n):
    return "alta" if n == 0 else ("media" if n <= 2 else "baixa")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--catalogo", default=os.path.join(ROOT, "data", "catalogo"), help="pasta do catálogo")
    ap.add_argument("--apply", action="store_true", help="grava o resultado")
    args = ap.parse_args()
    ev_dir = os.path.join(args.catalogo, "evidencias")
    csv_path = os.path.join(args.catalogo, "culturas.csv")

    erros = 0
    resultado = {}
    for p in sorted(glob.glob(os.path.join(ev_dir, "*.json"))):
        with open(p, encoding="utf-8") as f:
            ev = json.load(f)
        origem = ev.get("origem", {})
        faltam = [c for c in FILTRO if c not in origem]
        invalidos = [c for c, v in origem.items() if v.get("tipo") not in TIPOS]
        if faltam or invalidos:
            erros += 1
            print(f"{ev['id']:18} ERRO: origem sem {faltam or '-'}; tipos inválidos {invalidos or '-'}")
            continue
        lac = [c for c in FILTRO if origem[c]["tipo"] in LACUNA]
        novo = nivel(len(lac))
        antes = ev.get("valores", {}).get("confianca_parametros", "")
        resultado[ev["id"]] = novo
        marca = "" if novo == antes else f"  ({antes or 'vazio'} -> {novo})"
        print(f"{ev['id']:18} {novo:6} {len(lac)} lacuna(s): {', '.join(lac) or '-'}{marca}")
        if args.apply:
            ev["confianca_calculo"] = {"regra": REGRA, "contagem": len(lac), "colunas": lac}
            if novo != antes:
                ev.setdefault("mudancas", []).append({
                    "coluna": "confianca_parametros", "antes": antes, "depois": novo,
                    "motivo": "Regra de confiança: " + (", ".join(f"{c} ({origem[c]['tipo']})" for c in lac) or "nenhuma lacuna")})
                ev.setdefault("valores", {})["confianca_parametros"] = novo
            with open(p, "w", encoding="utf-8") as f:
                json.dump(ev, f, ensure_ascii=False, indent=2)
                f.write("\n")

    if args.apply and os.path.exists(csv_path) and resultado:
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        cols = list(rows[0].keys())
        for r in rows:
            if r["id"] in resultado:
                r["confianca_parametros"] = resultado[r["id"]]
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    if erros:
        raise SystemExit(f"{erros} arquivo(s) com origem incompleta.")


if __name__ == "__main__":
    main()
