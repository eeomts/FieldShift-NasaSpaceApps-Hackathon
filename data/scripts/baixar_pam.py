"""Baixa do SIDRA (IBGE) a Produção Agrícola Municipal (PAM, tabela 5457) das culturas da base.

Uso, da raiz do repositório:

    python3 data/scripts/baixar_pam.py

Outras opções: --anos N (padrão 10), --culturas soja,milho (recorte) e --saida (outro arquivo, ex.: fora do Git).

Dependências fora da biblioteca padrão: requests

Entrada: data/catalogo/culturas.csv, coluna codigo_pam (classificação 782 da tabela 5457). Cultura sem código
fica de fora. Duas culturas com o mesmo código (arroz e arroz_irrigado: a PAM não separa o arroz irrigado)
recebem as mesmas linhas, cada uma com o seu cultura_id.

Saída: data/brasil/pam/producao_municipal.csv, uma linha por município × cultura × ano, últimos 10 anos
publicados (lidos da API de agregados, não do relógio):
    municipio_id, cultura_id, ano, area_plantada_ha, area_colhida_ha, producao_t, rendimento_kg_ha,
    valor_mil_reais

Símbolos do SIDRA: "-" é zero absoluto -> 0; "..", "..." e "X" (não se aplica, não disponível, omitido
por sigilo) -> vazio, nunca 0. Qualquer outro texto não numérico interrompe o script sem gravar.

Limite da API (medido em 15/11/2026): até 100.000 valores por consulta; acima disso ela devolve HTTP 400
"Quantidade de valores solicitados: N excedeu o limite: 100000". Uma cultura × um ano × 5 variáveis × 5.564
municípios = 27.820 valores (~4 MB de JSON no formato /f/c, ~5 s). Por isso o script faz uma chamada por
cultura e por ano, com pausa entre as chamadas e novas tentativas com espera crescente.
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[2]
CATALOGO = RAIZ / "data" / "catalogo" / "culturas.csv"
BASE = RAIZ / "agroai" / "base" / "culturas.json"
SAIDA = RAIZ / "data" / "brasil" / "pam" / "producao_municipal.csv"
TABELA = 5457
API = "https://apisidra.ibge.gov.br/values"
PERIODOS = f"https://servicodados.ibge.gov.br/api/v3/agregados/{TABELA}/periodos"
ANOS = 10
LIMITE_VALORES = 100000  # por consulta (ver docstring)
LIMITE_MB = 20
PAUSA_S = 1.0  # entre chamadas, para não sobrecarregar o SIDRA
ESPERAS_S = (10, 30, 90)  # novas tentativas depois de erro de rede ou HTTP 5xx/429
MUNICIPIOS_MAX = 5600  # folga sobre os 5.570 municípios, só para conferir o limite antes de chamar

# variável do SIDRA -> coluna da saída (a ordem é a das colunas)
VARIAVEIS = {
    "8331": "area_plantada_ha",  # área plantada ou destinada à colheita (ha)
    "216": "area_colhida_ha",    # área colhida (ha)
    "214": "producao_t",         # quantidade produzida (t)
    "112": "rendimento_kg_ha",   # rendimento médio da produção (kg/ha)
    "215": "valor_mil_reais",    # valor da produção (mil R$)
}
COLUNAS = ["municipio_id", "cultura_id", "ano", *VARIAVEIS.values()]
ZERO = {"-"}                    # zero absoluto, não resultante de arredondamento
SEM_DADO = {"..", "...", "X"}   # não se aplica, não disponível, omitido para não identificar o informante


def valor(texto):
    """Texto do SIDRA -> texto da célula do CSV ("" = sem dado)."""
    texto = texto.strip()
    if texto in ZERO:
        return "0"
    if texto in SEM_DADO:
        return ""
    float(texto)  # ValueError se vier símbolo novo: melhor parar do que gravar lixo
    return texto


def ler_codigos(filtro):
    """codigo_pam -> [cultura_id], só das culturas com código e (se houver filtro) das pedidas."""
    with open(BASE, encoding="utf-8") as f:
        ids_base = {c["id"] for c in json.load(f)["culturas"]}
    codigos = {}
    with open(CATALOGO, encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            cultura, codigo = linha["id"].strip(), linha["codigo_pam"].strip()
            if not codigo or (filtro and cultura not in filtro):
                continue
            if cultura not in ids_base:
                sys.exit(f"{cultura!r} está em {CATALOGO.relative_to(RAIZ)} mas não em {BASE.relative_to(RAIZ)}.")
            codigos.setdefault(codigo, []).append(cultura)
    faltando = filtro - {c for lista in codigos.values() for c in lista} if filtro else set()
    if faltando:
        sys.exit(f"Sem codigo_pam no catálogo: {', '.join(sorted(faltando))}.")
    if not codigos:
        sys.exit("Nenhuma cultura com codigo_pam no catálogo.")
    return codigos


def get(sessao, url, descricao):
    """GET com novas tentativas; devolve o JSON. Erro 4xx (fora 429) não se repete: é pedido errado."""
    for tentativa, espera in enumerate((*ESPERAS_S, None), start=1):
        try:
            r = sessao.get(url, timeout=300)
            if r.ok:
                return r.json()
            if r.status_code != 429 and r.status_code < 500:
                sys.exit(f"O SIDRA devolveu HTTP {r.status_code} para {descricao}: {r.text[:200]}")
            erro = f"HTTP {r.status_code}"
        except (requests.RequestException, ValueError) as e:
            erro = type(e).__name__
        if espera is None:
            sys.exit(f"Falha em {descricao} depois de {tentativa} tentativas ({erro}).")
        print(f"  {descricao}: {erro}; nova tentativa em {espera} s", file=sys.stderr)
        time.sleep(espera)


def ultimos_anos(sessao, n):
    anos = sorted(int(p["id"]) for p in get(sessao, PERIODOS, "períodos da tabela"))
    return anos[-n:]


def baixar(sessao, codigo, ano):
    """Uma cultura num ano: lista de (municipio_id, {coluna: texto})."""
    assert len(VARIAVEIS) * MUNICIPIOS_MAX <= LIMITE_VALORES
    url = (f"{API}/t/{TABELA}/n6/all/v/{','.join(VARIAVEIS)}/p/{ano}/c782/{codigo}/f/c")
    dados = get(sessao, url, f"produto {codigo}, {ano}")
    por_municipio = {}
    for d in dados[1:]:  # a 1ª linha é o cabeçalho descritivo
        municipio = d["D1C"]
        if len(municipio) != 7 or not municipio.isdigit():
            sys.exit(f"Código de município inesperado: {municipio!r} (produto {codigo}, {ano}).")
        if d["D3C"] != str(ano) or d["D4C"] != codigo or d["D2C"] not in VARIAVEIS:
            sys.exit(f"Resposta fora do pedido (produto {codigo}, {ano}): {d}")
        try:
            por_municipio.setdefault(municipio, {})[VARIAVEIS[d["D2C"]]] = valor(d["V"])
        except ValueError:
            sys.exit(f"Valor desconhecido {d['V']!r} (município {municipio}, produto {codigo}, {ano}).")
    return por_municipio


def main():
    sys.stdout.reconfigure(line_buffering=True)
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--anos", type=int, default=ANOS, help=f"últimos N anos publicados (padrão {ANOS})")
    p.add_argument("--culturas", help="ids separados por vírgula (padrão: todas com codigo_pam)")
    p.add_argument("--saida", type=Path, default=SAIDA)
    args = p.parse_args()
    filtro = {c.strip() for c in args.culturas.split(",")} if args.culturas else set()

    codigos = ler_codigos(filtro)
    sessao = requests.Session()
    anos = ultimos_anos(sessao, args.anos)
    print(f"Tabela {TABELA}, anos {anos[0]}-{anos[-1]}, culturas: "
          + ", ".join(f"{'+'.join(c)} ({k})" for k, c in codigos.items()))

    linhas = []
    for codigo, culturas in codigos.items():
        for ano in anos:
            por_municipio = baixar(sessao, codigo, ano)
            com_area = sum(1 for v in por_municipio.values() if v.get("area_plantada_ha") not in ("", "0", None))
            print(f"{'+'.join(culturas)} {ano}: {len(por_municipio)} municípios, {com_area} com área plantada")
            for municipio, v in por_municipio.items():
                for cultura in culturas:
                    linhas.append((municipio, cultura, ano, *(v.get(c, "") for c in VARIAVEIS.values())))
            time.sleep(PAUSA_S)

    if not linhas:
        sys.exit("Nenhum dado retornado. Nada foi gravado.")
    linhas.sort(key=lambda l: (l[0], l[1], l[2]))
    saida = args.saida.resolve()
    saida.parent.mkdir(parents=True, exist_ok=True)
    tmp = saida.with_name(saida.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUNAS)
        w.writerows(linhas)
    tmp.replace(saida)
    mb = saida.stat().st_size / 1e6
    nome = saida.relative_to(RAIZ) if saida.is_relative_to(RAIZ) else saida
    print(f"{nome}: {len(linhas)} linhas, {mb:.1f} MB")
    if mb > LIMITE_MB:
        print(f"AVISO: passou de {LIMITE_MB} MB; não deixe este arquivo no Git (use --saida em data/brutos/pam/).",
              file=sys.stderr)


if __name__ == "__main__":
    main()
