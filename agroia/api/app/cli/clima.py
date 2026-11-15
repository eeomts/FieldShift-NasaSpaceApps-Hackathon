"""Comandos do clima do NASA POWER (rode de dentro de agroia/api).

    python -m app.cli.clima baixar --lat -11.31 --lon -41.81
    python -m app.cli.clima mostrar --lat -11.31 --lon -41.81
    python -m app.cli.clima demo
"""
import argparse
import csv
import logging

from sqlalchemy.orm import Session

from app.core.caminhos import RAIZ_REPO
from app.core.db import get_engine
from app.core.erros import ErroDeNegocio
from app.repositories.clima_repository import ClimaRepository
from app.services.clima.celula import id_da_celula
from app.services.clima.clima_service import ClimaService
from app.services.integracao.nasa_power import ClienteNasaPower, ErroNasaPower

PONTOS_DEMO = RAIZ_REPO / "data" / "demo" / "pontos_demo.csv"
MESES = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
# (título, atributo, casas decimais)
COLUNAS = (
    ("chuva mm", "chuva_mm", 0),
    ("ET0 mm", "et0_mm", 0),
    ("Tméd", "tmed_c", 1),
    ("Tmax", "tmax_media_c", 1),
    ("Tmin", "tmin_media_c", 1),
    ("geada d", "dias_geada", 1),
    ("calor d", "dias_calor", 1),
    ("forte d", "dias_chuva_forte", 1),
    ("seca máx d", "maior_seq_seca_dias", 1),
)


def _num(valor: float | None, casas: int) -> str:
    return "—" if valor is None else f"{valor:.{casas}f}"


def baixar(lat: float, lon: float) -> str:
    with Session(get_engine(), expire_on_commit=False) as db:
        celula = ClimaService(ClimaRepository(db), ClienteNasaPower()).obter(lat, lon)
        print(f"célula {celula.id}: {celula.inicio} a {celula.fim}, elevação {_num(celula.elevacao_m, 0)} m")
        print(f"limite de chuva forte (P95, 1991–2020): {_num(celula.limite_chuva_forte_mm, 1)} mm/dia")
        return celula.id


def mostrar(lat: float, lon: float) -> None:
    with Session(get_engine(), expire_on_commit=False) as db:
        repo = ClimaRepository(db)
        celula = repo.celula_por_id(id_da_celula(lat, lon))
        if celula is None:
            raise SystemExit("erro: esta célula ainda não foi baixada. Rode 'baixar' antes.")
        c = ClimaService(repo, ClienteNasaPower()).climatologia(celula)
    print(f"Fonte: {c.fonte}")
    print(f"Período: {c.periodo} (dados baixados de {celula.inicio} a {celula.fim})")
    print(f"Elevação da célula: {_num(c.elevacao_m, 0)} m | limite de chuva forte: {_num(c.limite_chuva_forte_mm, 1)} mm/dia\n")
    print("mês  " + " ".join(f"{titulo:>10}" for titulo, _, _ in COLUNAS) + "  anos")
    for m in c.meses:
        celulas = " ".join(f"{_num(getattr(m, attr), casas):>10}" for _, attr, casas in COLUNAS)
        print(f"{MESES[m.mes - 1]:4} {celulas}  {m.anos_com_dado:4}")
    chuva = [m.chuva_mm for m in c.meses if m.chuva_mm is not None]
    et0 = [m.et0_mm for m in c.meses if m.et0_mm is not None]
    if len(chuva) == 12 and len(et0) == 12:
        print(f"\nTotal por ano: chuva {sum(chuva):.0f} mm | ET0 {sum(et0):.0f} mm")
    for nota in c.notas:
        print(f"Nota: {nota}")


def demo() -> None:
    with PONTOS_DEMO.open(encoding="utf-8", newline="") as f:
        pontos = list(csv.DictReader(f))
    for p in pontos:
        lat, lon = float(p["latitude"]), float(p["longitude"])
        print(f"\n== {p['municipio']}-{p['uf']} ({p['regiao']}) ==")
        baixar(lat, lon)
        mostrar(lat, lon)


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="aviso: %(message)s")
    parser = argparse.ArgumentParser(description="Clima do NASA POWER por célula da grade")
    sub = parser.add_subparsers(dest="comando", required=True)
    for nome, ajuda in (("baixar", "baixa e guarda o clima da célula do ponto"), ("mostrar", "climatologia mensal da célula")):
        p = sub.add_parser(nome, help=ajuda)
        p.add_argument("--lat", type=float, required=True)
        p.add_argument("--lon", type=float, required=True)
    sub.add_parser("demo", help="baixa e mostra os pontos de data/demo/pontos_demo.csv")

    args = parser.parse_args()
    try:
        if args.comando == "baixar":
            baixar(args.lat, args.lon)
        elif args.comando == "mostrar":
            mostrar(args.lat, args.lon)
        else:
            demo()
    except (ErroNasaPower, ErroDeNegocio) as e:
        raise SystemExit(f"erro: {e}")


if __name__ == "__main__":
    main()
