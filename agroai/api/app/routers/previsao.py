"""Rota da previsão do tempo da fazenda (Dashboard)."""
from dataclasses import asdict
from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from app.core.erros import ErroDeNegocio
from app.core.security import usuario_atual
from app.models import Usuario
from app.schemas.previsao import Previsao
from app.services.integracao.open_meteo import ErroOpenMeteo
from app.services.previsao.previsao_service import FONTE, LICENCA, PrevisaoService

router = APIRouter(tags=["previsao"])


@router.get("/fazenda/previsao", response_model=Previsao)
def previsao(u: Usuario = Depends(usuario_atual), servico: PrevisaoService = Depends()) -> Previsao:
    """Máxima, mínima, chuva e chance de chuva dos próximos 7 dias no ponto da fazenda (Open-Meteo)."""
    f = u.fazenda
    if f is None:
        raise ErroDeNegocio(404, "Fazenda ainda não cadastrada.")
    if f.lat is None or f.lon is None:
        raise ErroDeNegocio(422, "Marque no mapa onde fica o campo para ver a previsão.")
    try:
        dias = servico.obter(f.lat, f.lon)
    except ErroOpenMeteo:
        raise ErroDeNegocio(503, "Não consegui a previsão do tempo agora. Tente de novo em alguns minutos.") from None
    return Previsao(fonte=FONTE, licenca=LICENCA, dias=[asdict(d) for d in dias], gerado_em=datetime.now(UTC))
