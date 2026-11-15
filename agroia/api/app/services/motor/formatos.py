"""Texto em português para as frases do motor: números com vírgula, meses por extenso curto."""

MESES = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")


# Classe do CSV em português de produtor (as chaves internas, como CLASSE_BIOMASSA, não mudam)
EXIBE_PALHADA = {"baixo": "baixa", "baixa": "baixa", "medio": "média", "media": "média", "alto": "alta", "alta": "alta"}
EXIBE_FORRAGEIRO = {"nenhum": "nenhum", "baixo": "baixo", "medio": "médio", "alto": "alto"}


def classe_da_palha_texto(classe: str) -> str:
    return EXIBE_PALHADA.get(classe, classe)


def classe_forrageira_texto(classe: str) -> str:
    return EXIBE_FORRAGEIRO.get(classe, classe)


def num(v: float, casas: int = 2) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def inteiro(v: float) -> str:
    """Inteiro com ponto de milhar: 1150 vira '1.150'."""
    return f"{v:,.0f}".replace(",", ".")


def pct(v: float) -> str:
    return f"{v * 100:.0f}%"


def periodo_texto(inicio: int | None, fim: int | None, perene: bool) -> str:
    if perene:
        return "o ano todo"
    if inicio is None or fim is None:
        return "sem meses definidos"
    return MESES[inicio - 1] if inicio == fim else f"{MESES[inicio - 1]}–{MESES[fim - 1]}"
