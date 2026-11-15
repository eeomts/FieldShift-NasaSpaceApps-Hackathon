"""Pré-carga do cache do solo (SoilGrids) para a demo abrir na hora (rode de dentro de agroia/api).

    python -m app.cli.solo baixar --lat -17.64 --lon -51.08
    python -m app.cli.solo demo

Respeita o intervalo mínimo entre pedidos e retoma de onde parou: o que já está no cache não é pedido de novo.
"""
import argparse
import csv
import logging
from collections.abc import Callable, Iterable
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.caminhos import RAIZ_REPO
from app.core.db import get_engine
from app.core.erros import ErroDeNegocio
from app.repositories.solo_repository import SoloRepository
from app.services.integracao.soilgrids import get_cliente
from app.services.solo.solo_service import CAMPOS, SoloService

PONTOS_DEMO = (RAIZ_REPO / "data" / "demo" / "pontos_demo.csv", RAIZ_REPO / "data" / "demo" / "pontos_demo_eua.csv")


def ler_pontos(arquivos: Iterable[Path]) -> list[tuple[str, float, float]]:
    """(nome, lat, lon) de cada linha dos CSVs de demo; arquivo que não existe é pulado."""
    pontos = []
    for arquivo in arquivos:
        if not arquivo.exists():
            continue
        with arquivo.open(encoding="utf-8", newline="") as f:
            for p in csv.DictReader(f):
                pontos.append((f"{p['municipio']}-{p['uf']}", float(p["latitude"]), float(p["longitude"])))
    return pontos


def baixar_pontos(pontos: list[tuple[str, float, float]], servico: SoloService, escrever: Callable[[str], None] = print) -> dict[str, str]:
    """Busca e guarda o solo de cada ponto. Devolve nome -> `completo`, `parcial`, `sem dado` ou `falhou`."""
    resultado = {}
    for nome, lat, lon in pontos:
        solo = servico.obter(lat, lon)
        if solo is None:
            estado, detalhe = "falhou", "nada obtido; rode de novo para continuar"
        elif solo.sem_dado:
            estado, detalhe = "sem dado", "área urbana ou água"
        else:
            faltam = [prop for prop, campo in CAMPOS.items() if getattr(solo, campo) is None]
            estado = "parcial" if faltam else "completo"
            detalhe = f"faltam {', '.join(faltam)}; rode de novo para continuar" if faltam else f"{solo.classe_textural}, K {solo.k_usle}"
        resultado[nome] = estado
        escrever(f"{nome} ({lat:.4f}, {lon:.4f}): {estado} ({detalhe})")
    return resultado


def _executar(pontos: list[tuple[str, float, float]]) -> None:
    with Session(get_engine(), expire_on_commit=False) as db:
        baixar_pontos(pontos, SoloService(SoloRepository(db), get_cliente()))


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="aviso: %(message)s")
    parser = argparse.ArgumentParser(description="Solo do SoilGrids por ponto, guardado no cache")
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("baixar", help="busca e guarda o solo de um ponto")
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    sub.add_parser("demo", help="busca e guarda os pontos de data/demo/pontos_demo.csv e pontos_demo_eua.csv")
    args = parser.parse_args()
    try:
        _executar([("ponto", args.lat, args.lon)] if args.comando == "baixar" else ler_pontos(PONTOS_DEMO))
    except ErroDeNegocio as e:
        raise SystemExit(f"erro: {e}")


if __name__ == "__main__":
    main()
