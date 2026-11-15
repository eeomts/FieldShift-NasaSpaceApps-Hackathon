"""Tarefa em segundo plano: busca o solo no SoilGrids e refaz o retrato da fazenda (sessão de banco própria)."""
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.db import get_engine
from app.models import Fazenda
from app.repositories.solo_repository import SoloRepository
from app.schemas.onboarding import Respostas
from app.services.integracao.soilgrids import get_cliente
from app.services.solo.retrato import montar_retrato
from app.services.solo.solo_service import SoloService, utilizavel

log = logging.getLogger(__name__)


def processar_solo(fazenda_id: UUID, lat: float, lon: float) -> None:
    """Solo do ponto -> retrato com a fusão -> `pronto` (veio ao menos a textura). Senão `erro`; o que veio fica guardado no cache."""
    with Session(get_engine(), expire_on_commit=False) as db:
        try:
            solo = SoloService(SoloRepository(db), get_cliente()).obter(lat, lon)
        except Exception as e:  # a tarefa nunca deixa a fazenda presa em "processando"
            log.warning("Solo da fazenda: %s", type(e).__name__)
            db.rollback()
            solo = None
        f = db.get(Fazenda, fazenda_id)
        if f is None or (f.lat, f.lon) != (lat, lon):  # apagada ou mudou de local: a tarefa do novo local cuida
            return
        if solo is not None:  # mesmo parcial: a síntese usa o que existir (ex.: só o pH dá a acidez)
            f.retrato_solo = montar_retrato(Respostas.model_validate(f.respostas or {}), solo)  # respostas mais recentes
        f.status_processamento = "pronto" if solo is not None and utilizavel(solo) else "erro"
        db.commit()
