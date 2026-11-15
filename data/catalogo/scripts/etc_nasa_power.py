"""ETc de uma cultura (Kc x ET0) com ET0 FAO-56 Penman-Monteith diária do NASA POWER.

Reproduz as colunas `agua_ciclo_mm_min/max` de data/catalogo/culturas.csv que vêm
de cálculo próprio (milheto, nabo_forrageiro, aveia, guandu e crotalaria). Cada
cenário (cultura, local, semeadura, fases, Kc, anos) está em `etc_cenarios.json`,
ao lado deste arquivo.

Uso (na raiz do repositório):
    python3 -I data/catalogo/scripts/etc_nasa_power.py                   # todos os cenários
    python3 -I data/catalogo/scripts/etc_nasa_power.py guandu_max_rioverde_1510_150d
    python3 -I data/catalogo/scripts/etc_nasa_power.py --cultura milheto
    python3 -I data/catalogo/scripts/etc_nasa_power.py --sem-cache       # sempre baixa de novo
    python3 -I data/catalogo/scripts/etc_nasa_power.py --cenarios outro.json --cache /tmp/power

Só usa a biblioteca padrão do Python 3. Na primeira execução baixa uma série por
local da API diária do NASA POWER (comunidade AG) e guarda a resposta em
data/brutos/nasa_power/ (pasta ignorada pelo Git); as execuções seguintes leem
dali. Apague a pasta, ou use --sem-cache, para baixar a versão atual do POWER.

Método (FAO-56, Allen et al. 1998):
- ET0 diária pela eq. 6 (Penman-Monteith), G = 0. Pressão pela eq. 7 com a
  elevação do cenário; ea pelo ponto de orvalho (T2MDEW, eq. 14), ou pela UR
  média (RH2M, eq. 19) se faltar T2MDEW; Ra pela eq. 21; Rso pela eq. 37;
  Rn = 0,77 Rs - Rnl (eqs. 38-40). ET0 negativa vira 0.
- Curva de Kc em 4 fases (inicial, desenvolvimento, média, final): Kc ini
  constante, subida linear até Kc mid (eq. 66, dia contado a partir de 1), Kc
  mid constante, descida linear até Kc end. Coberturas manejadas no
  florescimento usam fase final de 0 dias (a janela termina no manejo).
- Com `altura_m` no cenário, Kc mid é ajustado ao clima local pela eq. 62,
  com u2 (WS2M) e URmín = 100 ea / e°(Tmax) médios da fase média de cada ano;
  Kc end >= 0,45 é ajustado igual (eq. 65) com as médias da fase final.
- ETc do ano = soma diária de Kc x ET0 na janela. A janela começa na
  semeadura + `inicio_apos_semeadura_dias` (para contar da emergência).
  Um ano entra só se todos os dias da janela têm dados.
- Saída por cenário: n de anos, ET0 e chuva (PRECTOTCORR) medianas, Kc mid
  usado (média), e média, mediana, mínimo, máximo, P10 e P90 da ETc entre os
  anos (P10/P90 por statistics.quantiles, método "exclusive"). Se o cenário
  tem `referencia`, imprime também a diferença em relação ao valor de lá.

Formato de etc_cenarios.json:
    {
      "locais": {"<chave>": {"nome": "...", "lat": -17.8, "lon": -50.92, "elevacao_m": 625.31}},
      "cenarios": [
        {"nome": "...", "cultura": "<id do culturas.csv>", "local": "<chave>",
         "semeadura": "MM-DD", "inicio_apos_semeadura_dias": 0,
         "fases_dias": [ini, des, med, fin],
         "kc": {"ini": 0.3, "mid": 1.0, "end": 1.0},
         "altura_m": 1.5,                       # ou null para não usar a eq. 62
         "anos": [2001, 2020],                  # anos da semeadura, inclusive
         "referencia": {"estatistica": "media", "valor": 83, "nota": "..."}}
    "estatistica" pode ser media, mediana, min, max, p10, p90, et0, chuva ou kc_mid.
      ]
    }
"""
import argparse
import datetime as dt
import json
import math
import os
import statistics as st
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
CENARIOS_PADRAO = os.path.join(AQUI, "etc_cenarios.json")
CACHE_PADRAO = os.path.join(ROOT, "data", "brutos", "nasa_power")

API = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETROS = ("T2M_MAX", "T2M_MIN", "T2MDEW", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN", "PRECTOTCORR")
FALTANTE = -999.0


# ---------------------------------------------------------------- NASA POWER

def baixar_power(lat, lon, inicio, fim, cache_dir):
    """Série diária do POWER (JSON da API) para um ponto, com cache opcional."""
    nome = f"power_{lat:+.4f}_{lon:+.4f}_{inicio:%Y%m%d}_{fim:%Y%m%d}.json"
    caminho = os.path.join(cache_dir, nome) if cache_dir else None
    if caminho and os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    query = urllib.parse.urlencode({
        "parameters": ",".join(PARAMETROS), "community": "AG",
        "latitude": f"{lat}", "longitude": f"{lon}",
        "start": f"{inicio:%Y%m%d}", "end": f"{fim:%Y%m%d}", "format": "JSON",
    })
    url = f"{API}?{query}"
    print(f"  baixando {url}", file=sys.stderr)
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                bruto = r.read()
            break
        except (urllib.error.URLError, TimeoutError) as erro:
            if tentativa == 2:
                raise SystemExit(f"Falha ao baixar o NASA POWER: {erro}")
            time.sleep(10 * (tentativa + 1))
    dados = json.loads(bruto)
    if caminho:
        os.makedirs(cache_dir, exist_ok=True)
        with open(caminho, "wb") as f:
            f.write(bruto)
    return dados


def dias_power(dados):
    """{data: {parametro: valor}}, com None no lugar de -999."""
    p = dados["properties"]["parameter"]
    serie = {}
    for chave in p["T2M_MAX"]:
        d = dt.date(int(chave[:4]), int(chave[4:6]), int(chave[6:8]))
        serie[d] = {v: (None if p[v][chave] is None or p[v][chave] <= FALTANTE + 1 else p[v][chave])
                    for v in p}
    return serie


# ---------------------------------------------------------------- FAO-56

def e_sat(t):
    """Pressão de saturação do vapor, kPa (eq. 11)."""
    return 0.6108 * math.exp(17.27 * t / (t + 237.3))


def ra_extraterrestre(lat_graus, dia_juliano):
    """Radiação extraterrestre diária, MJ m-2 d-1 (eqs. 21-25)."""
    phi = math.radians(lat_graus)
    dr = 1 + 0.033 * math.cos(2 * math.pi * dia_juliano / 365)
    dec = 0.409 * math.sin(2 * math.pi * dia_juliano / 365 - 1.39)
    ws = math.acos(max(-1.0, min(1.0, -math.tan(phi) * math.tan(dec))))
    return (24 * 60 / math.pi * 0.0820 * dr
            * (ws * math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.sin(ws)))


def et0_dia(data, v, lat, elevacao):
    """ET0 (mm/d), u2 (m/s), URmín (%) e chuva (mm) de um dia; None se faltar dado."""
    tmax, tmin, u2, rs = v.get("T2M_MAX"), v.get("T2M_MIN"), v.get("WS2M"), v.get("ALLSKY_SFC_SW_DWN")
    if None in (tmax, tmin, u2, rs):
        return None
    esat = (e_sat(tmax) + e_sat(tmin)) / 2                        # eq. 12
    if v.get("T2MDEW") is not None:
        ea = e_sat(v["T2MDEW"])                                   # eq. 14
    elif v.get("RH2M") is not None:
        ea = v["RH2M"] / 100 * esat                               # eq. 19
    else:
        return None
    t = (tmax + tmin) / 2
    pressao = 101.3 * ((293 - 0.0065 * elevacao) / 293) ** 5.26  # eq. 7
    gama = 0.000665 * pressao                                     # eq. 8
    delta = 4098 * e_sat(t) / (t + 237.3) ** 2                    # eq. 13
    ra = ra_extraterrestre(lat, data.timetuple().tm_yday)
    rso = (0.75 + 2e-5 * elevacao) * ra                           # eq. 37
    rns = 0.77 * rs                                               # eq. 38, albedo 0,23
    rnl = (4.903e-9 * ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2
           * (0.34 - 0.14 * math.sqrt(ea)) * (1.35 * min(rs / rso, 1.0) - 0.35))  # eq. 39
    rn = rns - rnl                                                # eq. 40
    et0 = ((0.408 * delta * rn + gama * 900 / (t + 273) * u2 * (esat - ea))
           / (delta + gama * (1 + 0.34 * u2)))                    # eq. 6, G = 0
    ur_min = min(100.0, 100 * ea / e_sat(tmax))
    return max(et0, 0.0), u2, ur_min, v.get("PRECTOTCORR") or 0.0


def ajuste_clima(kc, u2, ur_min, altura):
    """Eqs. 62 e 65: Kc da condição padrão (u2 2 m/s, URmín 45%) para o clima local."""
    return kc + (0.04 * (u2 - 2) - 0.004 * (ur_min - 45)) * (altura / 3) ** 0.3


def kc_do_dia(i, fases, kc_ini, kc_mid, kc_end):
    """Kc do dia i (contado a partir de 1) na curva de 4 fases (eq. 66)."""
    l_ini, l_des, l_med, l_fin = fases
    if i <= l_ini:
        return kc_ini
    if i <= l_ini + l_des:
        return kc_ini + (i - l_ini) / l_des * (kc_mid - kc_ini)
    if i <= l_ini + l_des + l_med:
        return kc_mid
    return kc_mid + (i - l_ini - l_des - l_med) / l_fin * (kc_end - kc_mid)


# ---------------------------------------------------------------- cenários

def janela(cen, ano):
    mes, dia = (int(x) for x in cen["semeadura"].split("-"))
    inicio = dt.date(ano, mes, dia) + dt.timedelta(days=cen.get("inicio_apos_semeadura_dias", 0))
    return inicio, inicio + dt.timedelta(days=sum(cen["fases_dias"]) - 1)


def etc_ano(cen, serie, inicio, lat, elevacao):
    """ETc, ET0, chuva e Kc mid usado num ano; None se faltar algum dia."""
    fases = cen["fases_dias"]
    n = sum(fases)
    dias = []
    for k in range(n):
        d = inicio + dt.timedelta(days=k)
        r = et0_dia(d, serie[d], lat, elevacao) if d in serie else None
        if r is None:
            return None
        dias.append(r)
    kc = cen["kc"]
    kc_mid, kc_end = kc["mid"], kc.get("end", kc["mid"])
    h = cen.get("altura_m")
    if h:
        a, b = fases[0] + fases[1], fases[0] + fases[1] + fases[2]
        meio = dias[a:b] or dias[-10:]
        kc_mid = ajuste_clima(kc_mid, st.mean(x[1] for x in meio), st.mean(x[2] for x in meio), h)
        if fases[3] > 0 and kc_end >= 0.45:
            fim = dias[b:]
            kc_end = ajuste_clima(kc_end, st.mean(x[1] for x in fim), st.mean(x[2] for x in fim), h)
    etc = sum(kc_do_dia(k + 1, fases, kc["ini"], kc_mid, kc_end) * dias[k][0] for k in range(n))
    return etc, sum(x[0] for x in dias), sum(x[3] for x in dias), kc_mid


def rodar_cenario(cen, local, serie):
    anos = range(cen["anos"][0], cen["anos"][1] + 1)
    resultados = []
    for ano in anos:
        r = etc_ano(cen, serie, janela(cen, ano)[0], local["lat"], local["elevacao_m"])
        if r is not None:
            resultados.append((ano,) + r)
    return resultados


def resumo(resultados):
    etc = [r[1] for r in resultados]
    p = st.quantiles(etc, n=10) if len(etc) >= 2 else [etc[0]] * 9
    return {
        "anos": len(etc), "media": st.mean(etc), "mediana": st.median(etc),
        "min": min(etc), "max": max(etc), "p10": p[0], "p90": p[-1],
        "et0": st.median(r[2] for r in resultados), "chuva": st.median(r[3] for r in resultados),
        "kc_mid": st.mean(r[4] for r in resultados),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("nomes", nargs="*", help="nomes de cenários (padrão: todos)")
    ap.add_argument("--cenarios", default=CENARIOS_PADRAO, help="arquivo JSON de cenários")
    ap.add_argument("--cultura", help="só os cenários desta cultura")
    ap.add_argument("--cache", default=CACHE_PADRAO, help="pasta do cache do POWER")
    ap.add_argument("--sem-cache", action="store_true", help="não lê nem grava cache")
    ap.add_argument("--por-ano", action="store_true", help="imprime a ETc de cada ano")
    args = ap.parse_args()

    with open(args.cenarios, encoding="utf-8") as f:
        config = json.load(f)
    cenarios = [c for c in config["cenarios"]
                if (not args.nomes or c["nome"] in args.nomes)
                and (not args.cultura or c["cultura"] == args.cultura)]
    if not cenarios:
        raise SystemExit("Nenhum cenário com esses filtros.")
    cache = None if args.sem_cache else args.cache

    # Um download por local, cobrindo todas as janelas dos cenários dele.
    hoje = dt.date.today()
    periodos = {}
    for c in cenarios:
        ini, _ = janela(c, c["anos"][0])
        _, fim = janela(c, c["anos"][1])
        a, b = periodos.get(c["local"], (ini, fim))
        periodos[c["local"]] = (min(a, ini), max(b, fim))
    series, versoes = {}, {}
    for chave, (ini, fim) in periodos.items():
        loc = config["locais"][chave]
        ini = dt.date(ini.year, 1, 1)
        fim = min(dt.date(fim.year, 12, 31), hoje - dt.timedelta(days=7))
        dados = baixar_power(loc["lat"], loc["lon"], ini, fim, cache)
        series[chave] = dias_power(dados)
        versoes[chave] = (dados.get("header", {}).get("api", {}).get("version", "?"),
                          dados["geometry"]["coordinates"][2])

    for c in cenarios:
        loc = config["locais"][c["local"]]
        res = rodar_cenario(c, loc, series[c["local"]])
        versao, z_power = versoes[c["local"]]
        f = c["fases_dias"]
        print(f"\n== {c['nome']} ({c['cultura']})")
        print(f"   {loc['nome']} ({loc['lat']}, {loc['lon']}; {loc['elevacao_m']} m, célula POWER {z_power:.0f} m;"
              f" POWER {versao}); semeadura {c['semeadura']}"
              f"{' + %d d' % c['inicio_apos_semeadura_dias'] if c.get('inicio_apos_semeadura_dias') else ''};"
              f" fases {f[0]}/{f[1]}/{f[2]}/{f[3]} = {sum(f)} d; Kc {c['kc']['ini']} -> {c['kc']['mid']}"
              f"{' (eq. 62, h = %s m)' % c['altura_m'] if c.get('altura_m') else ''}; anos {c['anos'][0]}-{c['anos'][1]}")
        if not res:
            print("   sem nenhum ano completo")
            continue
        s = resumo(res)
        print(f"   n = {s['anos']} anos | ET0 mediana {s['et0']:.0f} mm | chuva mediana {s['chuva']:.0f} mm"
              f" | Kc mid usado {s['kc_mid']:.3f}")
        print(f"   ETc (mm): média {s['media']:.0f} | mediana {s['mediana']:.0f} | mín {s['min']:.0f}"
              f" | máx {s['max']:.0f} | P10 {s['p10']:.0f} | P90 {s['p90']:.0f}")
        ref = c.get("referencia")
        if ref:
            atual = s[ref["estatistica"]]
            dif = 100 * (atual - ref["valor"]) / ref["valor"]
            casas = 3 if abs(ref["valor"]) < 10 else 0
            print(f"   referência ({ref['estatistica']}): {ref['valor']} -> reproduzido {atual:.{casas}f} ({dif:+.1f}%)")
        if args.por_ano:
            print("   " + " ".join(f"{r[0]}:{r[1]:.0f}" for r in res))


if __name__ == "__main__":
    main()
