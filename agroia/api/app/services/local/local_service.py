"""Busca de lugar e informações de um ponto (hemisfério, zona climática, país, geada no histórico).

Cada parte é opcional: se um serviço externo falhar, o campo vem None (nunca erro 500).
Mandamos aos serviços externos coordenadas arredondadas a 2 casas (~1 km): basta para o clima e protege a privacidade.
"""
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import Depends

from app.repositories.clima_repository import ClimaRepository
from app.schemas.local import InfoLocal, LugarBusca
from app.services.clima.celula import id_da_celula
from app.services.integracao.nominatim import ClienteNominatim, get_nominatim
from app.services.integracao.power_climatologia import ClientePowerClimatologia, get_power_climatologia
from app.services.local.koppen import chuva_mensal_mm, koppen

log = logging.getLogger(__name__)


def hemisferio_de(lat: float) -> str:
    return "S" if lat < 0 else "N"


class LocalService:
    def __init__(
        self,
        nominatim: ClienteNominatim = Depends(get_nominatim),
        power: ClientePowerClimatologia = Depends(get_power_climatologia),
        clima: ClimaRepository = Depends(),
    ):
        self.nominatim = nominatim
        self.power = power
        self.clima = clima

    def buscar(self, q: str, idioma: str) -> list[LugarBusca]:
        try:
            return [LugarBusca(**l) for l in self.nominatim.buscar(q.strip(), idioma)]
        except Exception as e:  # Nominatim fora do ar: a tela segue sem sugestões
            log.warning("Busca de lugar falhou: %s", type(e).__name__)
            return []

    def info(self, lat: float, lon: float, idioma: str) -> InfoLocal:
        lat, lon = round(lat, 2), round(lon, 2)
        hemisferio = hemisferio_de(lat)
        with ThreadPoolExecutor(max_workers=2) as pool:
            zona = pool.submit(self._zona, lat, lon, hemisferio)
            lugar = pool.submit(self._lugar, lat, lon, idioma)
            zona, lugar = zona.result(), lugar.result()
        return InfoLocal(
            hemisferio=hemisferio, zona_climatica=zona, lugar=lugar.get("nome"), pais=lugar.get("pais"),
            pais_codigo=lugar.get("pais_codigo"), geada_no_historico=self._geada(lat, lon),
        )

    def _lugar(self, lat: float, lon: float, idioma: str) -> dict:
        try:
            return self.nominatim.reverso(lat, lon, idioma) or {}
        except Exception as e:
            log.warning("Lugar do ponto não obtido: %s", type(e).__name__)
            return {}

    def _zona(self, lat: float, lon: float, hemisferio: str) -> str | None:
        """Köppen aproximado pela climatologia do POWER; mês sem dado (-999) deixa tudo sem zona."""
        try:
            c = self.power.mensal(lat, lon)
            if None in c.temp_c or None in c.chuva_mm_dia:
                return None
            return koppen(c.temp_c, chuva_mensal_mm(c.chuva_mm_dia), hemisferio)
        except Exception as e:
            log.warning("Zona climática não calculada: %s", type(e).__name__)
            return None

    def _geada(self, lat: float, lon: float) -> bool | None:
        """True se algum mês do clima já guardado da célula teve dia de geada; None se não há clima guardado."""
        celula_id = id_da_celula(lat, lon)
        if self.clima.celula_por_id(celula_id) is None:
            return None
        dias = [m.dias_geada for m in self.clima.meses(celula_id) if m.dias_geada is not None]
        if not dias:
            return None
        return any(d > 0 for d in dias)
