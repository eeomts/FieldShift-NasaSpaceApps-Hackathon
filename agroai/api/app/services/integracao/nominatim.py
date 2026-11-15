"""Cliente do Nominatim (OpenStreetMap): busca de lugar pelo nome e lugar de uma coordenada.

Política de uso do servidor público: identificar o app (User-Agent), ~1 pedido por segundo, sem uso pesado.
Para produção, usar instância própria. https://operations.osmfoundation.org/policies/nominatim/
"""
import logging

import httpx

from app.services.integracao.cache import CacheLru

log = logging.getLogger(__name__)

URL_BUSCA = "https://nominatim.openstreetmap.org/search"
URL_REVERSO = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "AgroAI/0.1 (NASA Space Apps 2026 hackathon prototype)"
TIMEOUT_S = 8.0
_CIDADE = ("city", "town", "village", "municipality", "county")

_cache_busca = CacheLru()
_cache_reverso = CacheLru()


class ErroNominatim(Exception):
    """Nominatim fora do ar ou com resposta inesperada."""


def _nome(endereco: dict, item: dict) -> str | None:
    """"Cidade, Estado" (ou só o que existir)."""
    cidade = next((endereco[c] for c in _CIDADE if endereco.get(c)), None)
    partes = [p for p in (cidade, endereco.get("state")) if p]
    if partes:
        return ", ".join(partes)
    return item.get("name") or item.get("display_name")


def _lugar(item: dict) -> dict:
    endereco = item.get("address") or {}
    codigo = endereco.get("country_code")
    return {
        "nome": _nome(endereco, item),
        "pais": endereco.get("country"),
        "pais_codigo": codigo.upper() if codigo else None,
    }


class ClienteNominatim:
    def __init__(self, http: httpx.Client | None = None):
        self.http = http or httpx.Client(timeout=httpx.Timeout(TIMEOUT_S), headers={"User-Agent": USER_AGENT})

    def _get(self, url: str, params: dict):
        try:
            r = self.http.get(url, params=params, headers={"User-Agent": USER_AGENT})
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPError, ValueError) as e:
            raise ErroNominatim(f"{type(e).__name__}") from e

    def buscar(self, q: str, idioma: str, limite: int = 5) -> list[dict]:
        """Até `limite` lugares: [{nome, pais, pais_codigo, lat, lon}]. Lança ErroNominatim se falhar."""
        chave = (q.strip().lower(), idioma, limite)
        if (guardado := _cache_busca.pegar(chave)) is not None:
            return guardado
        corpo = self._get(URL_BUSCA, {"q": q, "format": "jsonv2", "addressdetails": 1, "limit": limite,
                                      "accept-language": idioma})
        if not isinstance(corpo, list):
            raise ErroNominatim("resposta inesperada")
        lugares, vistos = [], set()
        for item in corpo:
            try:
                lat, lon = float(item["lat"]), float(item["lon"])
            except (KeyError, TypeError, ValueError):
                continue
            lugar = _lugar(item)
            if not lugar["nome"] or (lugar["nome"], lugar["pais_codigo"]) in vistos:
                continue  # mesmo nome duas vezes (ex.: município e cidade) só atrapalha a escolha
            vistos.add((lugar["nome"], lugar["pais_codigo"]))
            lugares.append(lugar | {"lat": lat, "lon": lon})
        _cache_busca.guardar(chave, lugares)
        return lugares

    def reverso(self, lat: float, lon: float, idioma: str) -> dict | None:
        """{nome, pais, pais_codigo} do ponto (zoom 10 = cidade), ou None se não há lugar (mar, deserto)."""
        chave = (lat, lon, idioma)
        if (guardado := _cache_reverso.pegar(chave)) is not None:
            return guardado or None
        corpo = self._get(URL_REVERSO, {"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 10,
                                        "addressdetails": 1, "accept-language": idioma})
        if not isinstance(corpo, dict):
            raise ErroNominatim("resposta inesperada")
        lugar = None if "error" in corpo else _lugar(corpo)
        _cache_reverso.guardar(chave, lugar or {})
        return lugar


def get_nominatim() -> ClienteNominatim:
    return ClienteNominatim()
