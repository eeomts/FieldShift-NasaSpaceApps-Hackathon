"""Recorta da Tábua de Risco do ZARC as janelas de plantio das culturas da base, para o Brasil inteiro.

Uso, da raiz do repositório:

    python data/scripts/preparar_zarc.py

Só biblioteca padrão.

Fonte: MAPA, Tábua de Risco do Zoneamento Agrícola de Risco Climático (dados abertos), baixada à mão para
data/brutos/zarc/ (fora do Git; ver data/FONTES.md):
    tabua-2025-2026.csv                    safra 2025/2026
    tabua-perene-olericola-sem-safra.csv   culturas sem safra (aqui só entra o arroz irrigado)

Entrada:  data/brasil/zarc/mapa_culturas_zarc.csv   cultura_id -> nome no ZARC (vários separados por "|")
Saídas (data/brasil/zarc/):
    janelas.csv.gz  uma linha por cultura × época × município × solo × ciclo × nível de manejo × safra
    portarias.csv   a portaria do MAPA de cada cultura × época × UF × safra (a fonte de cada linha)

Colunas do janelas.csv.gz (CSV comum comprimido; leia com gzip.open(..., "rt") ou pandas/DuckDB direto):
    cultura_id, epoca, municipio_id, uf, tipo_solo, ciclo, nivel_manejo, safra, riscos
    - epoca: a posição do nome no mapa. 1 = a safra principal (milho e sorgo de verão, feijão das águas);
      2 = a 2ª safra (safrinha, feijão da seca). Culturas com um nome só têm sempre 1.
    - tipo_solo: como no ZARC. "Arenoso", "Textura Média" e "Argiloso" (milho, sorgo, algodão, arroz,
      girassol, caupi) ou "AD1" a "AD6", a classe de água disponível do solo (soja, feijão, trigo, aveia).
    - ciclo: "Grupo I" a "Grupo IV", o grupo de cultivar do ZARC (Cod_Ciclo 20 a 24 no dicionário).
    - nivel_manejo: vazio na linha comum; 1 a 4 (NM1 a NM4) nas linhas da soja por Nível de Manejo, em que
      um manejo de solo melhor dá risco menor. Por padrão, use as linhas vazias.
    - safra: "2025/2026", ou "sem safra" para o arroz irrigado da tábua de perenes.
    - riscos: 36 caracteres, um por decêndio, do 1 (1 a 10 de janeiro) ao 36 (21 a 31 de dezembro).
      "2" = risco de 20 %, "3" = 30 %, "4" = 40 %, "0" = plantio não indicado. Uma janela que passa do
      decêndio 36 para o 1 atravessa o ano. Para virar data, use decendio_para_datas() deste arquivo.

Regras:
    - Manejo: o motor é de sequeiro, então só entram as linhas "Sequeiro" (Cod_Outros_Manejos = 1). A única
      exceção é o arroz_irrigado, que usa "Irrigado" (2). O arroz de terras altas e o irrigado têm o mesmo
      nome no ZARC; quem separa é o manejo.
    - Decêndio: o ano tem 36, três por mês (dias 1-10, 11-20 e 21 ao fim). O dicionário de dados só diz
      "decêndios de 1 a 36". Falta conferir duas janelas no Painel de Indicação de Riscos do ZARC
      (TODO 05 da Pessoa 2).
    - Decêndio vazio na tábua vira "0" (não indicado) e é contado no aviso do fim; valor fora de 0/20/30/40
      para o script sem gravar nada.
    - Linha repetida (mesma chave) com riscos iguais é gravada uma vez; com riscos diferentes, para o script.

Formato compacto de propósito: uma linha por janela daria ~1,4 milhão de linhas e ~100 MB. Com os 36
decêndios numa coluna são ~550 mil linhas e 47 MB de texto, que o gzip leva a ~2,5 MB. O gzip é gravado com
mtime = 0: a mesma tábua gera sempre o mesmo arquivo, e o git só vê mudança quando o dado muda.
"""
import calendar
import csv
import gzip
import io
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BRUTOS = RAIZ / "data" / "brutos" / "zarc"
TABUAS = [  # (arquivo, rótulo da safra quando a tábua não traz ano)
    (BRUTOS / "tabua-2025-2026.csv", None),
    (BRUTOS / "tabua-perene-olericola-sem-safra.csv", "sem safra"),
]
PASTA = RAIZ / "data" / "brasil" / "zarc"
MAPA = PASTA / "mapa_culturas_zarc.csv"
LIMITE_MB = 20  # do arquivo comprimido; acima disso, avisa

SEQUEIRO, IRRIGADO = "1", "2"
MANEJO = {"arroz_irrigado": IRRIGADO}  # as demais culturas são de sequeiro

SOLOS = {"1": "Arenoso", "2": "Textura Média", "3": "Argiloso",
         "11": "AD1", "12": "AD2", "13": "AD3", "14": "AD4", "15": "AD5", "16": "AD6"}
CICLOS = {"20": "Grupo I", "21": "Grupo II", "22": "Grupo III", "24": "Grupo IV",
          "25": "Grupo V", "26": "Grupo VI"}
RISCO = {"0": "0", "20": "2", "30": "3", "40": "4"}
COLUNAS = ["cultura_id", "epoca", "municipio_id", "uf", "tipo_solo", "ciclo", "nivel_manejo", "safra", "riscos"]


def decendio_para_datas(decendio):
    """Decêndio 1-36 -> ("MM-DD" do início, "MM-DD" do fim). Fevereiro termina no dia 28."""
    if not 1 <= decendio <= 36:
        raise ValueError(f"decêndio fora de 1-36: {decendio}")
    mes, parte = divmod(decendio - 1, 3)
    mes += 1
    inicio = 1 + 10 * parte
    fim = calendar.monthrange(2025, mes)[1] if parte == 2 else inicio + 9  # 2025 não é bissexto
    return f"{mes:02d}-{inicio:02d}", f"{mes:02d}-{fim:02d}"


def ler_mapa():
    """nome no ZARC -> [(cultura_id, epoca)]. O mesmo nome pode servir a mais de uma cultura (Arroz)."""
    nomes = defaultdict(list)
    with open(MAPA, encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            for epoca, nome in enumerate(filter(None, linha["nome_zarc"].split("|")), start=1):
                nomes[nome.strip()].append((linha["cultura_id"], epoca))
    if not nomes:
        sys.exit(f"{MAPA.relative_to(RAIZ)} não tem nenhum nome do ZARC preenchido.")
    return nomes


def riscos(linha, vazios):
    texto = []
    for i in range(1, 37):
        valor = linha[f"dec{i}"].strip()
        if valor == "":
            vazios[linha["Nome_cultura"]] += 1
            valor = "0"
        if valor not in RISCO:
            sys.exit(f"Risco desconhecido {valor!r} no dec{i} ({linha['Nome_cultura']}, {linha['geocodigo']}). "
                     "Nada foi gravado.")
        texto.append(RISCO[valor])
    return "".join(texto)


def main():
    nomes = ler_mapa()
    faltando = [str(p.relative_to(RAIZ)) for p, _ in TABUAS if not p.exists()]
    if faltando:
        sys.exit(f"Faltam as tábuas do ZARC: {faltando}. Baixe-as (ver data/FONTES.md). Nada foi gravado.")

    janelas = {}      # chave -> riscos
    portarias = {}    # (cultura_id, epoca, uf, safra) -> set de portarias
    vazios, repetidas, sem_janela = Counter(), Counter(), Counter()
    encontrados = set()
    for caminho, safra_fixa in TABUAS:
        with open(caminho, encoding="utf-8-sig", newline="") as f:
            for linha in csv.DictReader(f, delimiter=";"):
                destinos = nomes.get(linha["Nome_cultura"])
                if not destinos:
                    continue
                safra = safra_fixa or f"{linha['SafraIni']}/{linha['SafraFin']}"
                for cultura, epoca in destinos:
                    if linha["Cod_Outros_Manejos"] != MANEJO.get(cultura, SEQUEIRO):
                        continue
                    solo, ciclo = SOLOS.get(linha["Cod_Solo"]), CICLOS.get(linha["Cod_Ciclo"])
                    if solo is None or ciclo is None:
                        sys.exit(f"Solo {linha['Cod_Solo']!r} ou ciclo {linha['Cod_Ciclo']!r} fora do dicionário "
                                 f"({linha['Nome_cultura']}, {linha['geocodigo']}). Nada foi gravado.")
                    nm = linha["Cod_NM"].strip()
                    nm = "" if nm in ("", "0") else nm
                    r = riscos(linha, vazios)
                    encontrados.add((cultura, epoca))
                    if set(r) == {"0"}:
                        sem_janela[cultura] += 1
                        continue
                    chave = (cultura, epoca, linha["geocodigo"], linha["UF"], solo, ciclo, nm, safra)
                    if chave in janelas:
                        if janelas[chave] != r:
                            sys.exit(f"Linha repetida com riscos diferentes: {chave}. Nada foi gravado.")
                        repetidas[cultura] += 1
                        continue
                    janelas[chave] = r
                    portarias.setdefault((cultura, epoca, linha["UF"], safra), set()).add(linha["Portaria"].strip())

    esperados = {d for ds in nomes.values() for d in ds}
    for cultura, epoca in sorted(esperados - encontrados):
        print(f"AVISO: {cultura} (época {epoca}) não apareceu na tábua com o manejo esperado", file=sys.stderr)
    if not janelas:
        sys.exit("Nenhuma janela encontrada. Nada foi gravado.")

    PASTA.mkdir(parents=True, exist_ok=True)
    gravar(PASTA / "janelas.csv.gz", COLUNAS, ([*k, r] for k, r in sorted(janelas.items())), comprimir=True)
    gravar(PASTA / "portarias.csv", ["cultura_id", "epoca", "uf", "safra", "portaria"],
           ([*k, p] for k, ps in sorted(portarias.items()) for p in sorted(ps)))

    tamanho = (PASTA / "janelas.csv.gz").stat().st_size / 1e6
    print(f"data/brasil/zarc/janelas.csv.gz: {len(janelas)} linhas, {tamanho:.1f} MB comprimido")
    por_cultura = Counter((k[0], k[1]) for k in janelas)
    for (cultura, epoca), n in sorted(por_cultura.items()):
        ufs = len({k[3] for k in janelas if k[0] == cultura and k[1] == epoca})
        print(f"  {cultura} (época {epoca}): {n} linhas, {ufs} UFs")
    if sem_janela:
        print(f"  sem nenhum decêndio indicado (não gravadas): {dict(sem_janela)}")
    if repetidas:
        print(f"  repetidas na tábua, gravadas uma vez: {dict(repetidas)}")
    if vazios:
        print(f"AVISO: decêndios vazios na tábua, tratados como não indicados: {dict(vazios)}", file=sys.stderr)
    if tamanho > LIMITE_MB:
        print(f"AVISO: janelas.csv.gz passou de {LIMITE_MB} MB", file=sys.stderr)


def gravar(caminho, cabecalho, linhas, comprimir=False):
    """Escreve num .tmp e troca de uma vez: o arquivo final nunca fica pela metade."""
    tmp = caminho.with_name(caminho.name + ".tmp")
    with open(tmp, "wb") as bruto:
        destino = gzip.GzipFile(filename="", mode="wb", fileobj=bruto, mtime=0) if comprimir else bruto
        with io.TextIOWrapper(destino, encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(cabecalho)
            w.writerows(linhas)
    tmp.replace(caminho)


if __name__ == "__main__":
    main()
