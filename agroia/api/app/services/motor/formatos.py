"""Texto em português para as frases do motor: números com vírgula, meses por extenso curto."""

MESES = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")


def num(v: float, casas: int = 2) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def pct(v: float) -> str:
    return f"{v * 100:.0f}%"


def periodo_texto(inicio: int | None, fim: int | None, perene: bool) -> str:
    if perene:
        return "o ano todo"
    if inicio is None or fim is None:
        return "sem meses definidos"
    return MESES[inicio - 1] if inicio == fim else f"{MESES[inicio - 1]}–{MESES[fim - 1]}"
