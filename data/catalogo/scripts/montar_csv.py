"""Monta o culturas.csv de um catálogo a partir das evidências e valida o resultado.

No catálogo dos EUA (data/catalogo/eua/) a fonte da verdade são os arquivos
evidencias/<id>.json: cada agente escreve só o arquivo da sua cultura, e este
script junta tudo no CSV, sem conflito entre agentes. As colunas seguem o
cabeçalho do catálogo do Brasil (data/catalogo/culturas.csv) mais as colunas
extras do país (EXTRAS).

Uso (na raiz do repositório):
    python3 -I data/catalogo/scripts/montar_csv.py --catalogo data/catalogo/eua            # só valida
    python3 -I data/catalogo/scripts/montar_csv.py --catalogo data/catalogo/eua --apply    # grava o CSV
    python3 -I data/catalogo/scripts/montar_csv.py --comparar     # frio igual na mesma espécie (BR x EUA)

Não rode --apply no catálogo do Brasil: as evidências de lá não têm nome,
nome_cientifico e familia_botanica, e o CSV do Brasil é sincronizado à mão.

Validações: id existe em agroia/base/culturas.json; todas as colunas presentes
(as de janela, região e texto para o produtor são opcionais: ausente = vazio);
números válidos; mínimo <= máximo; kc_medio <= 1,25; categorias da régua;
tipos coerentes com fixa_nitrogenio e raiz_profunda; fontes preenchidas; nenhum
caminho temporário; datas MM-DD e listas das colunas de janela; colunas de dano por
frio (README, "Dano por frio": fase e frações coerentes, ciclo_todo = 0 e 1, perene
sem frações, limiar de -10 a 20 °C, dias seguidos >= 2, efeito, e cada coluna com
entrada em evidencias e origem); janela de
semeadura obrigatória nas coberturas (sem `comercial`); lacuna_informacao e
risco_revisao_local obrigatórios com confiança `baixa`.
"""
import argparse
import csv
import glob
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
BASE_BR = os.path.join(ROOT, "data", "catalogo", "culturas.csv")
CATALOGO_APP = os.path.join(ROOT, "agroia", "base", "culturas.json")
EXTRAS = ["codigo_nass", "calendario_usda"]
FIXAS = {"id", "nome", "nome_cientifico", "familia_botanica"}
NUM = ["ciclo_dias_min", "ciclo_dias_max", "graus_dia_ciclo_min", "graus_dia_ciclo_max", "temp_base_c",
       "temp_otima_min_c", "temp_otima_max_c", "tmax_critica_c", "tmin_critica_c", "agua_ciclo_mm_min", "agua_ciclo_mm_max",
       "kc_inicial", "kc_medio", "kc_final", "profundidade_raiz_m"]
PARES = [("ciclo_dias_min", "ciclo_dias_max"), ("graus_dia_ciclo_min", "graus_dia_ciclo_max"),
         ("agua_ciclo_mm_min", "agua_ciclo_mm_max"), ("temp_otima_min_c", "temp_otima_max_c")]
ENUMS = {"perene": {"true", "false"}, "sensivel_geada": {"true", "false"}, "fixa_nitrogenio": {"true", "false"},
         "raiz_profunda": {"true", "false"}, "cobertura_solo": {"baixa", "media", "alta", ""},
         "aporte_biomassa": {"baixo", "medio", "alto", ""}, "valor_forrageiro": {"nenhum", "baixo", "medio", "alto", ""},
         "confianca_parametros": {"baixa", "media", "alta"}}
TIPOS = {"comercial", "cobertura", "forrageira", "fixadora_n", "raiz_profunda", "tolerante_seca"}
# Dano por frio (README de evidências, "Dano por frio"): opcionais na leitura.
FRIO = ["tmin_critica_c", "fase_sensivel_frio", "fase_frio_inicio_frac", "fase_frio_fim_frac",
        "tmin_dias_seguidos", "tmin_efeito"]
FASES_FRIO = {"emergencia", "vegetativo", "floracao", "enchimento_grao", "ciclo_todo", ""}
EFEITOS_FRIO = {"elimina", "aviso", ""}
TMIN_FAIXA = (-10.0, 20.0)
# Chave de `origem` que cobre cada coluna de frio (README, "Dano por frio").
ORIGEM_FRIO = {"tmin_critica_c": "tmin_critica_c", "tmin_efeito": "tmin_critica_c",
               "fase_sensivel_frio": "fase_frio_frac", "fase_frio_inicio_frac": "fase_frio_frac",
               "fase_frio_fim_frac": "fase_frio_frac", "tmin_dias_seguidos": "tmin_dias_seguidos"}
# Espécies em que o frio pode diferir entre linhas, com fonte que diga a diferença (--comparar).
EXCECOES_FRIO = {
    "oryza sativa": "grupo de cultivar: japônica do sul dos EUA tolera mais o frio que as cultivares do RS "
                    "(Arkansas MP192; SOSBAI); arroz de terras altas e irrigado são sistemas diferentes",
}
COMPARAR_FRIO = ["tmin_critica_c", "fase_sensivel_frio", "tmin_dias_seguidos", "tmin_efeito"]
# Colunas de janela, região e texto para o produtor (README de evidências): opcionais na leitura.
DATAS = ["semeadura_inicio", "semeadura_fim", "manejo_inicio", "manejo_fim"]
TEXTOS = ["lacuna_informacao", "risco_revisao_local"]
OPCIONAIS = set(DATAS + TEXTOS + FRIO + ["tipo_manejo", "condicao_semeadura", "estados_validos"])
TIPO_MANEJO = {"dessecacao", "morte_pelo_frio", "rolagem", "corte", ""}
CONDICOES = {"apos_colheita_graos", "apos_cereal_inverno", "apos_silagem", "a_lanco_lavoura_em_pe"}
MM_DD = re.compile(r"^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")
SIGLA = re.compile(r"^[A-Z]{2}$")


def validar_frio(r, ev, erro):
    """Colunas de dano por frio (README de evidências, "Dano por frio")."""
    fase = r["fase_sensivel_frio"]
    if fase not in FASES_FRIO:
        erro(f"fase_sensivel_frio inválida: {fase!r}")
    fracs = []
    for c in ("fase_frio_inicio_frac", "fase_frio_fim_frac"):
        try:
            if r[c]:
                v = float(r[c])
                fracs.append(v)
                if not 0 <= v <= 1:
                    erro(f"{c} fora de 0 a 1: {r[c]!r}")
        except ValueError:
            erro(f"{c} não numérico: {r[c]!r}")
    if len(fracs) == 2 and fracs[0] > fracs[1]:
        erro("fase_frio_inicio_frac > fase_frio_fim_frac")
    if fracs and not fase:
        erro("fração da fase de frio sem fase_sensivel_frio")
    if fase and not r["tmin_critica_c"]:
        erro("fase_sensivel_frio sem tmin_critica_c")
    if r["tmin_critica_c"] and not fase:
        erro("tmin_critica_c sem fase_sensivel_frio")
    if r["perene"] == "true" and fracs:
        erro("perene com fase_frio_inicio_frac/fim_frac (devem ficar vazias)")
    if fase and r["perene"] != "true" and len(fracs) != 2:
        erro("fase_sensivel_frio sem fase_frio_inicio_frac/fim_frac (cultura anual)")
    if fase == "ciclo_todo" and len(fracs) == 2 and fracs != [0.0, 1.0]:
        erro("ciclo_todo exige fase_frio_inicio_frac = 0 e fase_frio_fim_frac = 1")
    if r["tmin_critica_c"]:
        try:
            if not TMIN_FAIXA[0] <= float(r["tmin_critica_c"]) <= TMIN_FAIXA[1]:
                erro(f"tmin_critica_c fora de {TMIN_FAIXA[0]:g} a {TMIN_FAIXA[1]:g} °C: {r['tmin_critica_c']!r}")
        except ValueError:
            pass  # já acusado em NUM
    if r["tmin_dias_seguidos"]:
        if not r["tmin_dias_seguidos"].isdigit() or int(r["tmin_dias_seguidos"]) < 2:
            erro(f"tmin_dias_seguidos deve ser inteiro >= 2 (vazio = 1 dia): {r['tmin_dias_seguidos']!r}")
        if not r["tmin_critica_c"]:
            erro("tmin_dias_seguidos sem tmin_critica_c")
    if r["tmin_efeito"] not in EFEITOS_FRIO:
        erro(f"tmin_efeito inválido: {r['tmin_efeito']!r}")
    if r["tmin_efeito"] and not r["tmin_critica_c"]:
        erro("tmin_efeito sem tmin_critica_c")
    citadas = {c for e in ev.get("evidencias", []) for c in (e.get("colunas") or [])}
    origem = ev.get("origem", {})
    for c in FRIO:
        if r[c] and c not in citadas:
            erro(f"{c} preenchida sem entrada em evidencias[].colunas")
        if r[c] and ORIGEM_FRIO[c] not in origem:
            erro(f"{c} preenchida sem origem.{ORIGEM_FRIO[c]}")
    if not r["tmin_critica_c"] and "tmin_critica_c" in origem:
        if origem["tmin_critica_c"].get("tipo") not in {"vazio_nao_sei", "vazio_nao_se_aplica"}:
            erro("tmin_critica_c vazia com origem que não é vazio_nao_sei/vazio_nao_se_aplica")


def especie(nome_cientifico):
    """'Glycine max (L.) Merr.' -> 'glycine max' (gênero e espécie)."""
    return " ".join(nome_cientifico.lower().replace("×", " ").split()[:2])


def comparar():
    """Frio igual na mesma espécie nos dois catálogos (e entre linhas do mesmo catálogo)."""
    por_especie = {}
    for pais, caminho in (("BR", BASE_BR), ("EUA", os.path.join(ROOT, "data", "catalogo", "eua", "culturas.csv"))):
        with open(caminho, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("nome_cientifico"):
                    por_especie.setdefault(especie(r["nome_cientifico"]), []).append((pais, r))
    problemas = 0
    for sp, linhas in sorted(por_especie.items()):
        if len(linhas) < 2:
            continue
        valores = {tuple(r.get(c, "") for c in COMPARAR_FRIO) for _, r in linhas}
        if len(valores) < 2:
            continue
        quem = "; ".join(f"{pais} {r['id']}: " + ", ".join(f"{c}={r.get(c, '')!r}" for c in COMPARAR_FRIO)
                         for pais, r in linhas)
        if sp in EXCECOES_FRIO:
            print(f"  EXCEÇÃO {sp} ({EXCECOES_FRIO[sp]}): {quem}")
        else:
            problemas += 1
            print(f"  PROBLEMA {sp}: frio diferente na mesma espécie: {quem}")
    print(f"{sum(len(v) > 1 for v in por_especie.values())} espécie(s) em mais de uma linha, {problemas} problema(s)")
    if problemas:
        raise SystemExit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--catalogo", help="pasta do catálogo (ex.: data/catalogo/eua)")
    ap.add_argument("--apply", action="store_true", help="grava o culturas.csv")
    ap.add_argument("--comparar", action="store_true", help="compara o frio da mesma espécie nos dois CSVs")
    args = ap.parse_args()
    if args.comparar:
        return comparar()
    if not args.catalogo:
        ap.error("informe --catalogo ou --comparar")

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
        faltam = [c for c in colunas if c not in ev.get("valores", {}) and c not in FIXAS | OPCIONAIS and c not in EXTRAS]
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
        for c in DATAS:
            if r[c] and not MM_DD.match(r[c]):
                erro(f"{c} fora do formato MM-DD: {r[c]!r}")
        validar_frio(r, ev, erro)
        if r["tipo_manejo"] not in TIPO_MANEJO:
            erro(f"tipo_manejo inválido: {r['tipo_manejo']!r}")
        condicoes = set(filter(None, r["condicao_semeadura"].split("|")))
        if not condicoes <= CONDICOES:
            erro(f"condicao_semeadura inválida: {sorted(condicoes - CONDICOES)}")
        estados = list(filter(None, r["estados_validos"].split("|")))
        if any(not SIGLA.match(e) for e in estados):
            erro(f"estados_validos com sigla inválida: {estados}")
        if "comercial" not in tipos and not (r["semeadura_inicio"] and r["semeadura_fim"]):
            erro("cobertura sem janela de semeadura (semeadura_inicio/fim)")
        for col, txt in (ev.get("regua", {}).get("avisos") or {}).items():
            if not isinstance(txt, str) or not txt.strip() or len(txt) > 200:
                erro(f"regua.avisos.{col} vazio ou com mais de 200 caracteres")
        for c in TEXTOS:
            if len(r[c]) > 300:
                erro(f"{c} com mais de 300 caracteres")
            if r["confianca_parametros"] == "baixa" and not r[c]:
                erro(f"confiança baixa sem {c}")
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
