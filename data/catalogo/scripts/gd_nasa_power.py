"""Graus-dia de um ciclo com temperatura diária do NASA POWER.

Calcula a soma de graus-dia (GD) entre a semeadura e o fim do ciclo, ano a ano,
no mesmo método das colunas `graus_dia_ciclo_min/max` do catálogo:
GD = soma de max(0, Tmed - Tb), com Tmed = (T2M_MAX + T2M_MIN) / 2, SEM teto.
Serve para pôr uma exigência da literatura "na régua do POWER" (a régua que o
motor usa), refazendo a soma nas datas e no local do ensaio.

Uso (na raiz do repositório):
    python3 -I data/catalogo/scripts/gd_nasa_power.py --cenarios data/catalogo/eua/cenarios/milho_gd.json
    python3 -I data/catalogo/scripts/gd_nasa_power.py --cenarios <arquivo> --cultura milho --por-ano

Formato do arquivo de cenários (mesmos `locais` de etc_cenarios.json):
    {"locais": {"ames": {"nome": "Ames-IA", "lat": 42.03, "lon": -93.62, "elevacao_m": 300}},
     "cenarios": [{"nome": "milho_ames_0501_rm110", "cultura": "milho", "local": "ames",
                   "semeadura": "05-01", "dias": 130, "tb": 10, "anos": [2001, 2020],
                   "referencia": {"estatistica": "mediana", "valor": 1500, "nota": "..."}}]}
Use "dias" (duração do ciclo) ou "fim" ("MM-DD", no mesmo ano ou no seguinte).

Conversão de exigência com teto (ex.: GDD 86/50 em °F das fontes dos EUA): em vez
de "dias"/"fim", dê "alvo_com_teto": {"valor": 2700, "unidade": "F", "tb": 50, "teto": 86}.
Para cada ano, o script acumula o GDD da fonte (Tmax limitada ao teto, Tmin elevada
à Tb, média menos Tb), acha o dia em que o alvo é atingido (até 250 dias; senão o ano fica de fora) e soma o GD do catálogo
(sem teto, com a "tb" do cenário) nas mesmas datas. A saída mostra os dias e o GD
convertido; use o GD convertido em graus_dia_ciclo_min/max (origem: calculo).

Download e cache: os mesmos de etc_nasa_power.py (data/brutos/nasa_power/).
Só usa a biblioteca padrão do Python 3.
"""
import argparse
import datetime as dt
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from etc_nasa_power import CACHE_PADRAO, baixar_power, dias_power  # noqa: E402


MAX_DIAS = 250  # sem atingir o alvo nesse prazo, o ano conta como "não atingido"


def para_c(valor, unidade):
    return (valor - 32) / 1.8 if unidade.upper() == "F" else valor


def dias_ate_alvo(cen, serie, inicio):
    """Dias da semeadura até atingir o GDD da fonte (método com teto); None se não atinge."""
    a = cen["alvo_com_teto"]
    un = a.get("unidade", "C")
    tb, teto = para_c(a["tb"], un), para_c(a["teto"], un)
    alvo = a["valor"] / 1.8 if un.upper() == "F" else a["valor"]
    total, d, n = 0.0, inicio, 0
    while total < alvo:
        v = serie.get(d)
        if not v or v["T2M_MAX"] is None or v["T2M_MIN"] is None or n >= MAX_DIAS:
            return None
        tmax = min(max(v["T2M_MAX"], tb), teto)
        tmin = min(max(v["T2M_MIN"], tb), teto)
        total += (tmax + tmin) / 2 - tb
        d += dt.timedelta(days=1)
        n += 1
    return n


def janela(cen, ano, serie=None):
    mes, dia = (int(x) for x in cen["semeadura"].split("-"))
    inicio = dt.date(ano, mes, dia)
    if "alvo_com_teto" in cen:
        if serie is None:  # só para dimensionar o download
            return inicio, inicio + dt.timedelta(days=300)
        n = dias_ate_alvo(cen, serie, inicio)
        return (inicio, None) if n is None else (inicio, inicio + dt.timedelta(days=n - 1))
    if "dias" in cen:
        return inicio, inicio + dt.timedelta(days=cen["dias"] - 1)
    mes_f, dia_f = (int(x) for x in cen["fim"].split("-"))
    fim = dt.date(ano, mes_f, dia_f)
    if fim < inicio:
        fim = dt.date(ano + 1, mes_f, dia_f)
    return inicio, fim


def gd_ano(cen, serie, ano):
    """Soma de graus-dia no ano; None se faltar algum dia."""
    inicio, fim = janela(cen, ano, serie)
    if fim is None:
        return None
    total, d = 0.0, inicio
    while d <= fim:
        v = serie.get(d)
        if not v or v["T2M_MAX"] is None or v["T2M_MIN"] is None:
            return None
        total += max(0.0, (v["T2M_MAX"] + v["T2M_MIN"]) / 2 - cen["tb"])
        d += dt.timedelta(days=1)
    return total


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("nomes", nargs="*", help="nomes de cenários (padrão: todos)")
    ap.add_argument("--cenarios", required=True, help="arquivo JSON de cenários")
    ap.add_argument("--cultura", help="só os cenários desta cultura")
    ap.add_argument("--cache", default=CACHE_PADRAO, help="pasta do cache do POWER")
    ap.add_argument("--sem-cache", action="store_true", help="não lê nem grava cache")
    ap.add_argument("--por-ano", action="store_true", help="imprime a soma de cada ano")
    args = ap.parse_args()

    with open(args.cenarios, encoding="utf-8") as f:
        config = json.load(f)
    cenarios = [c for c in config["cenarios"]
                if (not args.nomes or c["nome"] in args.nomes)
                and (not args.cultura or c["cultura"] == args.cultura)]
    if not cenarios:
        raise SystemExit("Nenhum cenário com esses filtros.")
    cache = None if args.sem_cache else args.cache

    hoje = dt.date.today()
    periodos = {}
    for c in cenarios:
        ini = janela(c, c["anos"][0])[0]
        fim = janela(c, c["anos"][1])[1]
        a, b = periodos.get(c["local"], (ini, fim))
        periodos[c["local"]] = (min(a, ini), max(b, fim))
    series = {}
    for chave, (ini, fim) in periodos.items():
        loc = config["locais"][chave]
        dados = baixar_power(loc["lat"], loc["lon"], dt.date(ini.year, 1, 1),
                             min(dt.date(fim.year, 12, 31), hoje - dt.timedelta(days=7)), cache)
        series[chave] = dias_power(dados)

    for c in cenarios:
        loc = config["locais"][c["local"]]
        serie = series[c["local"]]
        res = [(ano, g) for ano in range(c["anos"][0], c["anos"][1] + 1)
               if (g := gd_ano(c, serie, ano)) is not None]
        if "alvo_com_teto" in c:
            a = c["alvo_com_teto"]
            dias = [(janela(c, ano, serie)[1] - janela(c, ano, serie)[0]).days + 1 for ano, _ in res]
            duracao = (f"até atingir {a['valor']} GDD {a.get('unidade', 'C')} com teto"
                       f" ({a['tb']}/{a['teto']}); dias: mediana {st.median(dias):.0f}, {min(dias)}-{max(dias)}"
                       if dias else "alvo não atingido")
        else:
            duracao = f"{c['dias']} d" if "dias" in c else f"até {c['fim']}"
        print(f"\n== {c['nome']} ({c['cultura']})")
        print(f"   {loc['nome']} ({loc['lat']}, {loc['lon']}); semeadura {c['semeadura']}, {duracao};"
              f" Tb {c['tb']} °C, sem teto; anos {c['anos'][0]}-{c['anos'][1]}")
        if not res:
            print("   sem nenhum ano completo")
            continue
        g = [x[1] for x in res]
        p = st.quantiles(g, n=10) if len(g) >= 2 else [g[0]] * 9
        s = {"media": st.mean(g), "mediana": st.median(g), "min": min(g), "max": max(g), "p10": p[0], "p90": p[-1]}
        print(f"   n = {len(g)} anos | GD (°C·dia): média {s['media']:.0f} | mediana {s['mediana']:.0f}"
              f" | mín {s['min']:.0f} | máx {s['max']:.0f} | P10 {s['p10']:.0f} | P90 {s['p90']:.0f}")
        ref = c.get("referencia")
        if ref:
            atual = s[ref["estatistica"]]
            print(f"   referência ({ref['estatistica']}): {ref['valor']} -> POWER {atual:.0f}"
                  f" ({100 * (atual - ref['valor']) / ref['valor']:+.1f}%)")
        if args.por_ano:
            print("   " + " ".join(f"{a}:{x:.0f}" for a, x in res))


if __name__ == "__main__":
    main()
