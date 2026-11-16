"""Baixa do IBGE a lista e os polígonos dos municípios brasileiros.

Uso, da raiz do repositório:

    python data/scripts/baixar_malha_municipal.py

Dependências fora da biblioteca padrão: requests

Saídas (sobrescritas a cada execução):
    data/brasil/municipios/municipios.csv       municipio_id (7 dígitos), nome, uf
    data/brasil/municipios/municipios.geojson   polígonos em qualidade mínima, com municipio_id em properties

O backend usa os dois para descobrir o município da fazenda pelo ponto no mapa, o que liga o
produtor à PAM e ao ZARC.
"""
import csv
import json
import sys
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "data" / "brasil" / "municipios"
URL_LISTA = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
URL_MALHA = ("https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR"
             "?intrarregiao=municipio&formato=application/vnd.geo+json&qualidade=minima")
MINIMO_MUNICIPIOS = 5000  # menos que isso é resposta incompleta da API


def baixar_json(url):
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    return r.json()


def uf_de(m):
    """Sigla da UF. Municípios novos podem vir sem microrregião; nesse caso usa a região imediata."""
    if m.get("microrregiao"):
        return m["microrregiao"]["mesorregiao"]["UF"]["sigla"]
    if m.get("regiao-imediata"):
        return m["regiao-imediata"]["regiao-intermediaria"]["UF"]["sigla"]
    sys.exit(f"Sem UF para o município {m['id']} ({m['nome']}): o IBGE não informou a região.")


def gravar(destino, escrever):
    """Escreve num .tmp e troca de uma vez: o arquivo final nunca fica pela metade."""
    tmp = destino.with_name(destino.name + ".tmp")
    escrever(tmp)
    tmp.replace(destino)


def main():
    sys.stdout.reconfigure(line_buffering=True)

    # Baixa e confere as duas fontes antes de escrever qualquer arquivo.
    print("Baixando a lista de municípios...")
    lista = baixar_json(URL_LISTA)
    print("Baixando os polígonos (qualidade mínima)...")
    malha = baixar_json(URL_MALHA)
    if len(lista) < MINIMO_MUNICIPIOS or len(malha.get("features", [])) < MINIMO_MUNICIPIOS:
        sys.exit(f"Resposta incompleta do IBGE: {len(lista)} municípios na lista e "
                 f"{len(malha.get('features', []))} polígonos. Nada foi gravado.")

    linhas = sorted(({"municipio_id": str(m["id"]), "nome": m["nome"], "uf": uf_de(m)} for m in lista),
                    key=lambda l: l["municipio_id"])
    for feature in malha["features"]:
        feature["properties"] = {"municipio_id": str(feature["properties"]["codarea"])}
    malha["features"].sort(key=lambda ft: ft["properties"]["municipio_id"])

    SAIDA.mkdir(parents=True, exist_ok=True)

    def escrever_csv(caminho):
        with open(caminho, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["municipio_id", "nome", "uf"])
            w.writeheader()
            w.writerows(linhas)

    def escrever_geojson(caminho):
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(malha, f, ensure_ascii=False, separators=(",", ":"))

    gravar(SAIDA / "municipios.csv", escrever_csv)
    gravar(SAIDA / "municipios.geojson", escrever_geojson)

    ids_lista = {l["municipio_id"] for l in linhas}
    ids_malha = {ft["properties"]["municipio_id"] for ft in malha["features"]}
    tamanho_mb = (SAIDA / "municipios.geojson").stat().st_size / 1e6
    print(f"municipios.csv: {len(ids_lista)} municípios")
    print(f"municipios.geojson: {len(ids_malha)} polígonos, {tamanho_mb:.1f} MB")
    nomes = {l["municipio_id"]: f'{l["nome"]} ({l["uf"]})' for l in linhas}
    for codigo in sorted(ids_lista - ids_malha):
        print(f"AVISO: {codigo} {nomes[codigo]} está na lista, mas ainda não tem polígono na malha do IBGE")
    for codigo in sorted(ids_malha - ids_lista):
        print(f"AVISO: {codigo} tem polígono, mas não está na lista de municípios")


if __name__ == "__main__":
    main()
