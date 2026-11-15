"""Estado (UF no Brasil, sigla USPS nos EUA) do local da fazenda, pelos 2 primeiros dígitos do código do município/condado."""

# IBGE, Tabela de códigos de UF (os 2 primeiros dígitos do código do município, de 7 dígitos)
UF_POR_CODIGO_IBGE = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
    "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA",
    "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
    "41": "PR", "42": "SC", "43": "RS",
    "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}  # fmt: skip

# Census Bureau, códigos FIPS de estado (os 2 primeiros dígitos do FIPS do condado, de 5 dígitos) -> sigla USPS
USPS_POR_CODIGO_FIPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC",
    "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT",
    "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
    "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY",
    "60": "AS", "66": "GU", "69": "MP", "72": "PR", "78": "VI",
}  # fmt: skip

TABELA_POR_PAIS = {"BR": UF_POR_CODIGO_IBGE, "US": USPS_POR_CODIGO_FIPS}


def estado_do_local(pais: str | None, codigo_local: str | None) -> str | None:
    """Sigla do estado, ou None se faltar o país ou o código, ou se o código não for de um estado conhecido."""
    tabela = TABELA_POR_PAIS.get(pais or "")
    if tabela is None or not codigo_local:
        return None
    return tabela.get(codigo_local.strip()[:2])
