"""Previsão dos próximos 7 dias da fazenda (Open-Meteo, D-014), com cache de 1 hora por ponto."""
from datetime import UTC, datetime

from fastapi import Depends

from app.services.integracao.cache import CacheLru
from app.services.integracao.open_meteo import ClienteOpenMeteo, DiaPrevisao, get_cliente

FONTE = "Open-Meteo"
LICENCA = "CC BY 4.0"
_cache = CacheLru(tamanho=500)


class PrevisaoService:
    def __init__(self, cliente: ClienteOpenMeteo = Depends(get_cliente)):
        self.cliente = cliente
        self.agora = lambda: datetime.now(UTC)  # os testes trocam

    def obter(self, lat: float, lon: float) -> list[DiaPrevisao]:
        agora = self.agora()
        chave = (round(lat, 2), round(lon, 2), agora.strftime("%Y%m%d%H"))
        dias = _cache.pegar(chave)
        if dias is None:
            dias = self.cliente.previsao(lat, lon)
            _cache.guardar(chave, dias)
        return dias


def limpar_cache() -> None:
    _cache.limpar()
