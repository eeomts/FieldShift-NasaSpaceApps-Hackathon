"""Respostas do SoilGrids no formato real (REST /properties/query) e um cliente falso, sem rede."""
from app.services.integracao.soilgrids import (
    AmostraSoilGrids,
    ClienteSoilGrids,
    ErroSoilGrids,
    PropriedadeSolo,
    interpretar,
    interpretar_propriedade,
)

PROFUNDIDADES = [("0-5cm", 0, 5), ("5-15cm", 5, 15), ("15-30cm", 15, 30), ("30-60cm", 30, 60), ("60-100cm", 60, 100)]
UNIDADES = {"clay": ("g/kg", "%", 10), "sand": ("g/kg", "%", 10), "silt": ("g/kg", "%", 10), "soc": ("dg/kg", "g/kg", 10),
            "phh2o": ("pH*10", "pH", 10), "bdod": ("cg/cm^3", "kg/dm^3", 100), "cec": ("mmol(c)/kg", "cmol(c)/kg", 10),
            "nitrogen": ("cg/kg", "g/kg", 100), "cfvo": ("cm^3/dm^3", "cm3/100cm3 (vol%)", 10)}  # fmt: skip


def camada(nome: str, medias: list[int | None], q05: int | None = None, q50: int | None = None, q95: int | None = None) -> dict:
    """Uma propriedade com as 5 profundidades. `medias` em unidades mapeadas (None = sem dado). Quantis iguais em todas."""
    mapeada, alvo, fator = UNIDADES[nome]
    return {
        "name": nome,
        "unit_measure": {"d_factor": fator, "mapped_units": mapeada, "target_units": alvo, "uncertainty_unit": ""},
        "depths": [
            {
                "range": {"top_depth": topo, "bottom_depth": base, "unit_depth": "cm"},
                "label": rotulo,
                "values": {"Q0.05": None if m is None else q05, "Q0.5": None if m is None else q50, "Q0.95": None if m is None else q95, "mean": m},
            }
            for (rotulo, topo, base), m in zip(PROFUNDIDADES, medias)
        ],
    }


def resposta(*camadas: dict) -> dict:
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-51.080503, -17.644301]},
            "properties": {"layers": list(camadas)}, "query_time_s": 1.3}  # fmt: skip


def resposta_argilosa() -> dict:
    """Perto de Rio Verde (GO): argila ~40 %, areia ~40 %, silte ~20 %, carbono ~2 %, pH 5,5 (valores redondos, não os do mapa)."""
    return resposta(
        camada("clay", [400] * 5, q05=100, q50=400, q95=700),
        camada("sand", [400] * 5, q05=150, q50=400, q95=700),
        camada("silt", [200] * 5, q05=50, q50=200, q95=450),
        camada("soc", [200] * 5, q05=100, q50=200, q95=300),
        camada("phh2o", [55] * 5, q05=50, q50=55, q95=60),
        camada("bdod", [120] * 5, q05=100, q50=120, q95=140),
        camada("cec", [100] * 5, q05=60, q50=100, q95=150),
        camada("nitrogen", [150] * 5, q05=100, q50=150, q95=200),
        camada("cfvo", [20] * 5, q05=10, q50=20, q95=40),
    )


def resposta_urbana() -> dict:
    """Área urbana ou água: o mapa devolve tudo nulo."""
    return resposta(*(camada(n, [None] * 5) for n in UNIDADES))


def amostra(corpo: dict | None = None) -> AmostraSoilGrids:
    return interpretar(corpo or resposta_argilosa())


class ClienteFalso(ClienteSoilGrids):
    """Responde cada propriedade a partir de `resposta` (corpo no formato real) ou lança (se for exceção).

    `falhas`: propriedades que lançam ErroSoilGrids. `chamadas`: (lat, lon, propriedade) de cada pedido. Sem rede.
    """

    def __init__(self, resposta: dict | Exception | None = None, falhas=()):
        self.resposta = resposta_argilosa() if resposta is None else resposta
        self.falhas = set(falhas)
        self.chamadas: list[tuple[float, float, str]] = []

    @property
    def pontos(self) -> list[tuple[float, float]]:
        """Pontos distintos pedidos, na ordem."""
        return list(dict.fromkeys((lat, lon) for lat, lon, _ in self.chamadas))

    def propriedade(self, lat: float, lon: float, nome: str) -> PropriedadeSolo:
        self.chamadas.append((lat, lon, nome))
        if isinstance(self.resposta, Exception):
            raise self.resposta
        if nome in self.falhas:
            raise ErroSoilGrids(f"fora do ar em {nome} (teste)")
        return interpretar_propriedade(self.resposta, nome)

    def pedidas(self) -> list[str]:
        return [n for _, _, n in self.chamadas]


ERRO = ErroSoilGrids("fora do ar (teste)")
