"""Relevo de um ponto: declividade do SRTM (com cache no banco) e, se falhar, a resposta q7 do produtor."""
import logging
from dataclasses import dataclass

from fastapi import Depends

from app.core.erros import ErroDeNegocio
from app.models import Fazenda
from app.repositories.relevo_repository import RelevoRepository
from app.services.integracao.srtm import ClienteSrtm, ErroSrtm, get_cliente

log = logging.getLogger(__name__)

FONTE_Q7 = "Resposta do produtor (pergunta 7)"
CLASSE_POR_Q7 = {"plano": "plano", "leve": "suave_ondulado", "inclinado": "ondulado"}


@dataclass(frozen=True)
class Relevo:
    classe: str
    declividade_pct: float | None  # None quando vem da resposta q7 (não há número medido)
    fonte: str


def chave_do_ponto(lat: float, lon: float) -> str:
    """Ponto arredondado a 4 casas (~11 m): pontos vizinhos dividem a mesma linha do cache."""
    return f"{lat:.4f}_{lon:.4f}"


def relevo_da_resposta(q7_terreno: str | None) -> Relevo | None:
    classe = CLASSE_POR_Q7.get(q7_terreno or "")
    return None if classe is None else Relevo(classe=classe, declividade_pct=None, fonte=FONTE_Q7)


class RelevoService:
    def __init__(
        self,
        repositorio: RelevoRepository = Depends(),
        cliente: ClienteSrtm = Depends(get_cliente),
    ):
        self.repositorio = repositorio
        self.cliente = cliente

    def declividade_da_fazenda(self, f: Fazenda) -> Relevo | None:
        """Relevo da fazenda: SRTM no ponto dela; sem ponto ou com SRTM fora do ar, a resposta q7."""
        if f.lat is None or f.lon is None:
            return relevo_da_resposta(f.terreno)
        return self.obter(f.lat, f.lon, f.terreno)

    def obter(self, lat: float, lon: float, q7_terreno: str | None = None) -> Relevo | None:
        """SRTM (cache primeiro). Falhou: classe da resposta q7 com a fonte marcada; sem q7, None (lacuna)."""
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ErroDeNegocio(422, "Latitude deve estar entre -90 e 90 e longitude entre -180 e 180.")
        chave = chave_do_ponto(lat, lon)
        guardado = self.repositorio.por_chave(chave)
        if guardado is not None:
            return Relevo(guardado.classe, guardado.declividade_pct, guardado.fonte)
        try:
            d = self.cliente.declividade(lat, lon)
        except ErroSrtm as e:
            log.warning("SRTM falhou (%s); usando a resposta q7.", e)
            return relevo_da_resposta(q7_terreno)
        self.repositorio.gravar(chave, d.percentual, d.classe, d.fonte)
        return Relevo(d.classe, d.percentual, d.fonte)
