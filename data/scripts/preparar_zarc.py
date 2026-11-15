"""Prepara as janelas de plantio do ZARC (data/brasil/zarc/janelas.csv) a partir das tábuas de risco do MAPA.

Entrada: uma ou mais tábuas de risco (CSV do portal dados.agricultura.gov.br, separador ';', UTF-8 com BOM),
guardadas em data/brutos/zarc/, e o mapa data/brasil/zarc/mapa_culturas_zarc.csv (cultura_id -> nome no ZARC).

Várias tábuas: para cada cultura, nome no ZARC e UF, vale só a tábua de safra mais recente que tem essa
combinação (ex.: 2026/2027 > 2025/2026). A tábua "Perene, Olerícola e Sem Safra" (safra "SEM SAFRA" ou
"PERENE") só entra onde nenhuma tábua de safra tem a combinação.

Saída: uma linha por trecho contínuo de decêndios com o mesmo risco (20, 30 ou 40 %), por cultura, época
(1 = 1º nome do mapa; 2 = 2º nome, a 2ª safra), município, tipo de solo, ciclo (grupo de cultivar) e nível de
manejo (NM1-NM4, só onde o ZARC o usa). Um trecho que passa de dezembro para janeiro (decêndio 36 -> 1) vira
uma linha só, com inicio_decendio > fim_decendio.

Decêndios (tabela "períodos de semeadura" das portarias do ZARC): 36 por ano, 3 por mês, dias 1-10, 11-20 e
21-fim do mês (fevereiro termina em 28). Decêndio 1 = 1 a 10 de janeiro; 36 = 21 a 31 de dezembro.

Uso:
    python3 -I data/scripts/preparar_zarc.py MAPA SAIDA TABUA [TABUA ...] [--ufs GO,RS,BA]
Exemplo (o janelas.csv do repositório):
    python3 -I data/scripts/preparar_zarc.py data/brasil/zarc/mapa_culturas_zarc.csv \\
        data/brasil/zarc/janelas.csv \\
        data/brutos/zarc/dados-abertos-tabua-de-risco-safra-2025-2026.csv \\
        data/brutos/zarc/dados-abertos-tabua-de-risco-safra-perene-olericola-sem-safra.csv \\
        --ufs GO,RS,BA
Sem --ufs sai o Brasil inteiro (~110 MB, 1,58 milhão de janelas): grande demais para o Git.

Só biblioteca padrão; lê as tábuas em streaming (cada uma tem centenas de MB), em duas passadas (~1 min).
"""
import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

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

FIM_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def decendio_para_data(dec: int, fim: bool) -> str:
    """Decêndio 1-36 -> 'MM-DD' do primeiro (fim=False) ou do último (fim=True) dia."""
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
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mapa", type=Path, help="data/brasil/zarc/mapa_culturas_zarc.csv")
    p.add_argument("saida", type=Path, help="CSV de saída (janelas.csv)")
    p.add_argument("tabuas", type=Path, nargs="+", help="CSV(s) da tábua de risco do ZARC")
    p.add_argument("--ufs", default="", help="UFs a manter, separadas por vírgula (vazio = todas)")
    a = p.parse_args()

    por_nome, epoca = ler_mapa(a.mapa)
    ufs = {u.strip().upper() for u in a.ufs.split(",") if u.strip()}

    # 1ª passada: qual safra vence para cada (cultura, nome no ZARC, UF).
    vencedora: dict[tuple[str, str, str], str] = {}
    for tabua in a.tabuas:
        for cultura_id, lin in linhas_da_tabua(tabua, por_nome, ufs):
            chave = (cultura_id, lin["Nome_cultura"], lin["UF"])
            safra = safra_de(lin)
            atual = vencedora.get(chave)
            if atual is None or prioridade(safra) > prioridade(atual):
                vencedora[chave] = safra

    # 2ª passada: só as linhas da safra vencedora viram janelas.
    linhas = []
    vistos: dict[tuple, list[str]] = {}
    duplicadas = divergentes = 0
    combinacoes = Counter()
    for tabua in a.tabuas:
        for cultura_id, lin in linhas_da_tabua(tabua, por_nome, ufs):
            safra = safra_de(lin)
            if vencedora[(cultura_id, lin["Nome_cultura"], lin["UF"])] != safra:
                continue
            solo = SOLO.get(lin["Cod_Solo"], lin["Cod_Solo"])
            ciclo = CICLO.get(lin["Cod_Ciclo"], lin["Cod_Ciclo"])
            nm = NIVEL_MANEJO.get(lin["Cod_NM"].strip(), "")
            riscos = [lin[f"dec{i}"].strip() for i in range(1, 37)]
            chave = (cultura_id, lin["Nome_cultura"], lin["geocodigo"], solo, ciclo, nm, safra)
            if chave in vistos:
                duplicadas += 1
                divergentes += vistos[chave] != riscos
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

    linhas.sort(key=lambda t: t[0])
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    with a.saida.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUNAS)
        w.writerows(t[1] for t in linhas)

    print(f"UFs: {','.join(sorted(ufs)) or 'todas'}", file=sys.stderr)
    for (cid, nome, safra), n in sorted(combinacoes.items()):
        print(f"  {cid:16s} {nome:30s} {safra:10s} {n:7d} combinações município×solo×ciclo×NM", file=sys.stderr)
    sem = sorted({c for v in por_nome.values() for c, _ in v} - {c for c, _, _ in combinacoes})
    if sem:
        print(f"  sem linhas nas tábuas: {', '.join(sem)}", file=sys.stderr)
    if duplicadas:
        print(f"  AVISO: {duplicadas} linhas repetidas (mesma chave) ignoradas, {divergentes} com riscos diferentes"
              " da 1ª (vale a 1ª)", file=sys.stderr)
    print(f"{len(linhas)} janelas gravadas em {a.saida}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
