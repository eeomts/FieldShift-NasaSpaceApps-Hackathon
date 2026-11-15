"""Régua das colunas qualitativas de data/catalogo/culturas.csv.

Calcula `aporte_biomassa`, `cobertura_solo` e `valor_forrageiro` a partir do
bloco `regua` de cada data/catalogo/evidencias/<id>.json. A regra e as fontes
de cada limite estão em data/catalogo/evidencias/README.md.

Uso (na raiz do repositório):
    python3 -I data/catalogo/scripts/regua.py            # só mostra a comparação
    python3 -I data/catalogo/scripts/regua.py --apply    # grava CSV e evidências

O --apply é idempotente: rodar duas vezes dá o mesmo resultado.
"""
import csv
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CSV_PATH = os.path.join(ROOT, "data/catalogo/culturas.csv")
EV_DIR = os.path.join(ROOT, "data/catalogo/evidencias")

# Limites da régua. As fontes estão no README.md de evidencias/.
CORTE_BAIXO_T_HA = 2.3  # abaixo: "baixo" (50% de cobertura, Lopes, Cogo & Levien 1987; Cruz et al. 2001)
CORTE_ALTO_T_HA = 6.0  # a partir daqui: "alto" (palhada adequada ao SPD, Alvarenga et al. 2001)
HORIZONTE_COBERTURA_DIAS = 60  # até a cultura seguinte cobrir 50% do solo (USDA AH 537; De Maria 1995)
DIGESTIBILIDADE_MIN_PCT = 60.0
# Só estas métricas medem digestibilidade e podem rebaixar o "alto".
METRICAS_DIGESTIBILIDADE = {"DIVMS", "DIVMO", "DMS", "DMO", "DMD"}

USO = {"principal": "alto", "com_restricao": "medio", "residual": "baixo", "nao_serve": "nenhum"}
COLUNAS = ("aporte_biomassa", "cobertura_solo", "valor_forrageiro")
MOTIVO = "Régua das colunas qualitativas (ver evidencias/README.md)"


def classe_massa(ms, rotulos):
    if ms is None:
        return None
    if ms < CORTE_BAIXO_T_HA:
        return rotulos[0]
    return rotulos[1] if ms < CORTE_ALTO_T_HA else rotulos[2]


def remanescente(ms, k_dia):
    if ms is None or k_dia is None:
        return None
    return ms * math.exp(-k_dia * HORIZONTE_COBERTURA_DIAS)


def forrageiro(regua):
    uso = regua.get("uso_forrageiro")
    if uso is None:
        return None
    classe = USO[uso]
    dig = regua.get("digestibilidade_pct") or {}
    valor = dig.get("valor")
    # Só a sigla conta: "DIVMO (digestibilidade in vitro...)" -> "DIVMO".
    partes = (dig.get("tipo") or "").split()
    tipo = partes[0].strip("(,;").upper() if partes else ""
    if classe == "alto" and valor is not None and tipo in METRICAS_DIGESTIBILIDADE and valor < DIGESTIBILIDADE_MIN_PCT:
        return "medio"
    if classe == "medio" and valor is None:
        return ""  # com restrição e sem digestibilidade: "não sei"
    return classe


def calcular(regua):
    ms = regua.get("ms_palhada_t_ha") or {}
    tipico, mn, mx = ms.get("tipico"), ms.get("min"), ms.get("max")
    k = (regua.get("k_dia") or {}).get("valor")
    bio = ("baixo", "medio", "alto")
    cob = ("baixa", "media", "alta")
    rem = remanescente(tipico, k)
    resultado = {
        "aporte_biomassa": classe_massa(tipico, bio),
        "cobertura_solo": classe_massa(rem, cob),
        "valor_forrageiro": forrageiro(regua),
    }
    detalhe = {
        "ms_tipico_t_ha": tipico,
        "ms_remanescente_t_ha": None if rem is None else round(rem, 2),
        "depende_da_epoca": {
            "aporte_biomassa": classe_massa(mn, bio) != classe_massa(mx, bio) if mn is not None and mx is not None else None,
            "cobertura_solo": classe_massa(remanescente(mn, k), cob) != classe_massa(remanescente(mx, k), cob)
            if mn is not None and mx is not None and k is not None else None,
        },
    }
    for col, exc in (regua.get("excecoes") or {}).items():
        resultado[col] = exc["valor"]
        detalhe.setdefault("excecoes_aplicadas", []).append(col)
    return resultado, detalhe


def main():
    apply = "--apply" in sys.argv
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cols = list(rows[0].keys())

    print(f"{'id':16}{'MS':>6}{'rem':>6}  {'biomassa':16}{'cobertura':16}{'forrageiro':16}aviso")
    for row in rows:
        ev_path = os.path.join(EV_DIR, f"{row['id']}.json")
        with open(ev_path, encoding="utf-8") as f:
            ev = json.load(f)
        regua = ev.get("regua")
        if not regua:
            print(f"{row['id']:16} SEM BLOCO regua")
            continue
        novo, detalhe = calcular(regua)

        def show(c):
            n = novo[c]
            if n is None:
                return f"{row[c]} (sem dado)"
            n = n or "não sei"
            return n if n == row[c] else f"{row[c] or 'vazio'}->{n}"

        aviso = ",".join(c.split("_")[0] for c, v in detalhe["depende_da_epoca"].items() if v)
        aviso = f"depende da época: {aviso}" if aviso else ""
        if detalhe.get("excecoes_aplicadas"):
            aviso += (" | " if aviso else "") + "exceção: " + ",".join(detalhe["excecoes_aplicadas"])
        fmt = lambda x: "-" if x is None else f"{x:g}"
        print(f"{row['id']:16}{fmt(detalhe['ms_tipico_t_ha']):>6}{fmt(detalhe['ms_remanescente_t_ha']):>6}  "
              f"{show('aporte_biomassa'):16}{show('cobertura_solo'):16}{show('valor_forrageiro'):16}{aviso}")

        if not apply:
            continue
        mudancas = ev.setdefault("mudancas", [])
        for c in COLUNAS:
            n = novo[c]
            if n is None or n == row[c]:
                continue
            mudancas.append({"coluna": c, "antes": row[c], "depois": n, "motivo": MOTIVO})
            row[c] = n
        regua["resultado"] = {c: row[c] for c in COLUNAS}
        regua["detalhe"] = detalhe
        ev["valores"].update({c: row[c] for c in COLUNAS})
        with open(ev_path, "w", encoding="utf-8") as f:
            json.dump(ev, f, ensure_ascii=False, indent=2)
            f.write("\n")

    if apply:
        with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print("APLICADO")


if __name__ == "__main__":
    main()
