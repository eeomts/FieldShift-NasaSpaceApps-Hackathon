"""Prepara as janelas de plantio do ZARC (data/brasil/zarc/janelas.csv) a partir das tábuas de risco do MAPA.

Uso, da raiz do repositório (gera o janelas.csv do repositório: GO, RS e BA):

    python3 -I data/scripts/preparar_zarc.py

Outras opções: --ufs GO,MT (outro recorte), --todas (Brasil inteiro), --mapa, --saida e --tabuas.

Entrada: as tábuas de risco (CSV do portal dados.agricultura.gov.br, separador ';', UTF-8 com BOM) guardadas em
data/brutos/zarc/ (padrão: todas as dados-abertos-tabua-de-risco-safra-*.csv, ou seja, as de safra, como
2025-2026 e 2026-2027, e a perene-olericola-sem-safra) e o mapa data/brasil/zarc/mapa_culturas_zarc.csv
(cultura_id -> nome no ZARC; cultura com nome_zarc vazio não entra).

Escolha da safra POR MUNICÍPIO: para cada cultura, nome no ZARC e município (geocodigo), vale só a tábua de
safra mais recente que tem esse município (ex.: 2026/2027 > 2025/2026). A tábua "Perene, Olerícola e Sem Safra"
(safra "SEM SAFRA" ou "PERENE") só entra onde nenhuma tábua de safra tem o município. A coluna safra diz de
onde veio cada linha. Atenção: um município que a portaria nova tirou continua com a janela da safra anterior
(ex.: milho 1ª safra no semiárido da BA); o stderr mostra, por cultura e UF, quantos municípios vieram de
cada safra.

Saída: uma linha por trecho contínuo de decêndios com o mesmo risco (20, 30 ou 40 %), por cultura, época
(1 = 1º nome do mapa; 2 = 2º nome, a 2ª safra), município, tipo de solo, ciclo (grupo de cultivar) e nível de
manejo (NM1-NM4, só onde o ZARC o usa). Um trecho que passa de dezembro para janeiro (decêndio 36 -> 1) vira
uma linha só, com inicio_decendio > fim_decendio.

Decêndios (tabela "períodos de semeadura" das portarias do ZARC): 36 por ano, 3 por mês, dias 1-10, 11-20 e
21-fim do mês (fevereiro termina em 28). Decêndio 1 = 1 a 10 de janeiro; 36 = 21 a 31 de dezembro.

Sai com código 1 se a mesma chave (cultura, nome no ZARC, município, solo, ciclo, NM, safra) aparecer com
riscos diferentes. Avisa (sem falhar) se o arquivo passar de 20 MB.

Medição de 15/11/2026 (tábuas 2025/2026, 2026/2027 e perenes/sem safra; mapa sem aveia): GO, RS e BA dão
363.514 janelas e 24,4 MB; o Brasil inteiro (--todas) dá 1.815.506 janelas e 122,4 MB (~70 s, ~1,7 GB de
memória), grande demais para o Git.

Só biblioteca padrão; lê as tábuas em streaming (cada uma tem centenas de MB), em duas passadas (~1 min).
"""
import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MAPA = RAIZ / "data" / "brasil" / "zarc" / "mapa_culturas_zarc.csv"
SAIDA = RAIZ / "data" / "brasil" / "zarc" / "janelas.csv"
BRUTOS = RAIZ / "data" / "brutos" / "zarc"
PADRAO_TABUAS = "dados-abertos-tabua-de-risco-safra-*.csv"
UFS_PADRAO = "GO,RS,BA"
LIMITE_MB = 20

# Manejo (coluna Nome_Outros_Manejos da tábua) que cada cultura da base usa. O motor é de sequeiro; só o
# arroz irrigado usa as linhas "Irrigado". Ver a coluna observacao do mapa.
MANEJO_PADRAO = "Sequeiro"
MANEJO_POR_CULTURA = {"arroz_irrigado": "Irrigado"}

# Dicionário de dados da tábua de risco (MAPA, 2026).
SOLO = {"1": "Arenoso", "2": "Textura Média", "3": "Argiloso",
        "11": "AD1", "12": "AD2", "13": "AD3", "14": "AD4", "15": "AD5", "16": "AD6"}
CICLO = {"13": "Perene", "19": "Semiperene", "20": "Grupo I", "21": "Grupo II", "22": "Grupo III",
         "24": "Grupo IV", "25": "Grupo V", "26": "Grupo VI"}
NIVEL_MANEJO = {"1": "NM1", "2": "NM2", "3": "NM3", "4": "NM4"}
RISCOS = {"20", "30", "40"}

COLUNAS = ["cultura_id", "epoca", "municipio_id", "uf", "tipo_solo", "ciclo", "nivel_manejo", "safra",
           "risco_pct", "inicio_decendio", "fim_decendio", "inicio_data", "fim_data"]

# Fevereiro com 28 dias, como na tabela de períodos de semeadura das portarias (item 3.3): o decêndio 6 vai de
# 21/02 a 28/02 (fim_data "02-28"). Em ano bissexto, o dia 29/02 pertence ao decêndio 6; quem usar as datas
# deve tratar 29/02 como parte do decêndio 6, não como dia fora de janela.
FIM_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def decendio_para_data(dec: int, fim: bool) -> str:
    """Decêndio 1-36 -> 'MM-DD' do primeiro (fim=False) ou do último (fim=True) dia (29/02: ver FIM_MES)."""
    if not 1 <= dec <= 36:
        raise ValueError(f"decêndio fora de 1-36: {dec}")
    mes, parte = divmod(dec - 1, 3)
    dia = (10, 20, FIM_MES[mes])[parte] if fim else (1, 11, 21)[parte]
    return f"{mes + 1:02d}-{dia:02d}"


def trechos(riscos: list[str]) -> list[tuple[int, int, int]]:
    """36 riscos ('0', '20', ...) -> [(risco, dec_ini, dec_fim)], juntando o trecho que vira o ano."""
    saida: list[list[int]] = []
    for i, v in enumerate(riscos, start=1):
        if v not in RISCOS:
            continue
        r = int(v)
        if saida and saida[-1][0] == r and saida[-1][2] == i - 1:
            saida[-1][2] = i
        else:
            saida.append([r, i, i])
    # Trecho que termina no decêndio 36 e outro, com o mesmo risco, que começa no 1: é a mesma janela.
    if len(saida) > 1 and saida[0][1] == 1 and saida[-1][2] == 36 and saida[0][0] == saida[-1][0]:
        primeiro = saida.pop(0)
        saida[-1][2] = primeiro[2]
    return [tuple(t) for t in saida]


def safra_de(lin: dict) -> str:
    """'2025/2026'; nas tábuas sem safra, o rótulo da coluna SafraFin ('SEM SAFRA', 'PERENE', 'OLERÍCOLA')."""
    return f"{lin['SafraIni']}/{lin['SafraFin']}" if lin["SafraIni"].strip() else lin["SafraFin"].strip()


def prioridade(safra: str) -> int:
    """Maior = mais recente. Tábuas sem safra ficam abaixo de qualquer safra."""
    return int(safra[:4]) if safra[:4].isdigit() else 0


def ler_mapa(caminho: Path) -> tuple[dict[str, list[tuple[str, str]]], dict[tuple[str, str], int]]:
    """(nome_zarc -> [(cultura_id, manejo)], (cultura_id, nome_zarc) -> época 1/2). Um nome pode servir a mais
    de uma cultura (Arroz -> arroz sequeiro e arroz_irrigado)."""
    por_nome: dict[str, list[tuple[str, str]]] = {}
    epoca: dict[tuple[str, str], int] = {}
    with caminho.open(newline="", encoding="utf-8") as f:
        for lin in csv.DictReader(f):
            nomes = [n.strip() for n in (lin["nome_zarc"] or "").split("|") if n.strip()]
            for i, nome in enumerate(nomes):
                manejo = MANEJO_POR_CULTURA.get(lin["cultura_id"], MANEJO_PADRAO)
                por_nome.setdefault(nome, []).append((lin["cultura_id"], manejo))
                epoca[(lin["cultura_id"], nome)] = i + 1
    return por_nome, epoca


def linhas_da_tabua(caminho: Path, por_nome: dict, ufs: set[str]):
    """Gera (cultura_id, linha) das linhas da tábua que interessam (cultura do mapa, manejo e UF)."""
    with caminho.open(newline="", encoding="utf-8-sig") as f:
        for lin in csv.DictReader(f, delimiter=";"):
            destinos = por_nome.get(lin["Nome_cultura"])
            if not destinos or (ufs and lin["UF"] not in ufs):
                continue
            for cultura_id, manejo in destinos:
                if lin["Nome_Outros_Manejos"] == manejo:
                    yield cultura_id, lin


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mapa", type=Path, default=MAPA,
                   help="mapa cultura_id -> nome no ZARC (padrão: data/brasil/zarc/mapa_culturas_zarc.csv)")
    p.add_argument("--saida", type=Path, default=SAIDA, help="CSV de saída (padrão: data/brasil/zarc/janelas.csv)")
    p.add_argument("--tabuas", type=Path, nargs="+", default=None,
                   help=f"CSV(s) da tábua de risco (padrão: data/brutos/zarc/{PADRAO_TABUAS})")
    recorte = p.add_mutually_exclusive_group()
    recorte.add_argument("--ufs", default=UFS_PADRAO, help="UFs a manter, separadas por vírgula (padrão: %(default)s)")
    recorte.add_argument("--todas", action="store_true", help="Brasil inteiro (não vai para o Git: grande demais)")
    a = p.parse_args()

    tabuas = a.tabuas or sorted(BRUTOS.glob(PADRAO_TABUAS))
    if not tabuas:
        sys.exit(f"Nenhuma tábua em {BRUTOS}/{PADRAO_TABUAS} (ver data/brutos/README.md).")
    por_nome, epoca = ler_mapa(a.mapa)
    ufs = set() if a.todas else {u.strip().upper() for u in a.ufs.split(",") if u.strip()}

    # 1ª passada: qual safra vence para cada (cultura, nome no ZARC, município).
    vencedora: dict[tuple[str, str, str], str] = {}
    uf_do_municipio: dict[str, str] = {}
    for tabua in tabuas:
        for cultura_id, lin in linhas_da_tabua(tabua, por_nome, ufs):
            chave = (cultura_id, lin["Nome_cultura"], lin["geocodigo"])
            uf_do_municipio[lin["geocodigo"]] = lin["UF"]
            safra = safra_de(lin)
            atual = vencedora.get(chave)
            if atual is None or prioridade(safra) > prioridade(atual):
                vencedora[chave] = safra

    # 2ª passada: só as linhas da safra vencedora no município viram janelas.
    linhas = []
    vistos: dict[tuple, list[str]] = {}
    duplicadas = 0
    divergentes: list[tuple] = []
    combinacoes = Counter()
    for tabua in tabuas:
        for cultura_id, lin in linhas_da_tabua(tabua, por_nome, ufs):
            safra = safra_de(lin)
            if vencedora[(cultura_id, lin["Nome_cultura"], lin["geocodigo"])] != safra:
                continue
            solo = SOLO.get(lin["Cod_Solo"], lin["Cod_Solo"])
            ciclo = CICLO.get(lin["Cod_Ciclo"], lin["Cod_Ciclo"])
            nm = NIVEL_MANEJO.get(lin["Cod_NM"].strip(), "")
            riscos = [lin[f"dec{i}"].strip() for i in range(1, 37)]
            chave = (cultura_id, lin["Nome_cultura"], lin["geocodigo"], solo, ciclo, nm, safra)
            if chave in vistos:
                duplicadas += 1
                if vistos[chave] != riscos:
                    divergentes.append(chave)
                continue
            vistos[chave] = riscos
            combinacoes[(cultura_id, lin["Nome_cultura"], safra)] += 1
            ep = epoca[(cultura_id, lin["Nome_cultura"])]
            ordem = (cultura_id, ep, lin["UF"], lin["geocodigo"], int(lin["Cod_Solo"] or 0),
                     int(lin["Cod_Ciclo"] or 0), nm)
            for risco, ini, fim in trechos(riscos):
                linhas.append((ordem + (ini, risco), (
                    cultura_id, ep, lin["geocodigo"], lin["UF"], solo, ciclo, nm, safra, risco,
                    ini, fim, decendio_para_data(ini, False), decendio_para_data(fim, True))))

    print(f"UFs: {','.join(sorted(ufs)) or 'todas'}; tábuas: {', '.join(t.name for t in tabuas)}", file=sys.stderr)
    if divergentes:
        print(f"ERRO: {len(divergentes)} chaves repetidas com riscos diferentes (nada foi gravado). Exemplos:",
              file=sys.stderr)
        for chave in divergentes[:10]:
            print(f"  {chave}", file=sys.stderr)
        return 1

    linhas.sort(key=lambda t: t[0])
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    with a.saida.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUNAS)
        w.writerows(t[1] for t in linhas)

    print("Combinações município×solo×ciclo×NM por cultura, nome no ZARC e safra:", file=sys.stderr)
    for (cid, nome, safra), n in sorted(combinacoes.items()):
        print(f"  {cid:16s} {nome:30s} {safra:10s} {n:7d}", file=sys.stderr)
    sem = sorted({c for v in por_nome.values() for c, _ in v} - {c for c, _, _ in combinacoes})
    if sem:
        print(f"  sem linhas nas tábuas: {', '.join(sem)}", file=sys.stderr)

    # Municípios por safra onde a mesma cultura e UF mistura safras (o município ficou fora da tábua mais nova).
    por_uf: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    for (cid, nome, geo), safra in vencedora.items():
        por_uf[(cid, nome, uf_do_municipio[geo])][safra] += 1
    mistas = {k: v for k, v in por_uf.items() if len(v) > 1}
    if mistas:
        print("Cultura e UF com municípios de mais de uma safra (vale a mais recente que tem o município):",
              file=sys.stderr)
        for (cid, nome, uf), cont in sorted(mistas.items()):
            partes = ", ".join(f"{s} {n}" for s, n in sorted(cont.items(), key=lambda t: -prioridade(t[0])))
            print(f"  {cid:16s} {nome:30s} {uf}  municípios: {partes}", file=sys.stderr)

    print("Janelas por cultura, UF e safra:", file=sys.stderr)
    contagem = Counter((t[1][0], t[1][3], t[1][7]) for t in linhas)
    for (cid, uf, safra), n in sorted(contagem.items()):
        print(f"  {cid:16s} {uf}  {safra:10s} {n:8d}", file=sys.stderr)

    if duplicadas:
        print(f"  {duplicadas} linhas repetidas (mesma chave e mesmos riscos) ignoradas", file=sys.stderr)
    mb = a.saida.stat().st_size / 1e6
    print(f"{len(linhas)} janelas gravadas em {a.saida} ({mb:.1f} MB)", file=sys.stderr)
    if mb > LIMITE_MB:
        print(f"AVISO: {a.saida.name} passou de {LIMITE_MB} MB ({mb:.1f} MB)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
