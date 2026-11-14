from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import CalendarioItem, Fazenda, Usuario
from app.onboarding import perfil
from app.onboarding.schemas import Respostas
from app.security import usuario_atual

router = APIRouter(tags=["fazenda"])


class SalvarFazenda(BaseModel):
    respostas: Respostas
    passo_atual: int = Field(default=0, ge=0, le=50)
    concluir: bool = False


class FazendaOut(BaseModel):
    id: str
    respostas: Respostas
    passo_atual: int
    onboarding_concluido: bool
    status_processamento: str
    perfil: str | None
    papel: str | None
    modificadores: dict
    retrato_solo: dict
    proximos_passos: list[dict]
    meses_sem_cobertura: list[int]


def _out(f: Fazenda) -> FazendaOut:
    r = Respostas.model_validate(f.respostas or {})
    return FazendaOut(
        id=str(f.id),
        respostas=r,
        passo_atual=f.passo_atual,
        onboarding_concluido=f.onboarding_concluido,
        status_processamento=f.status_processamento,
        perfil=f.perfil,
        papel=f.papel,
        modificadores={"irrigacao": f.irrigacao, "animais": f.animais},
        retrato_solo=f.retrato_solo or {},
        proximos_passos=f.proximos_passos or [],
        meses_sem_cobertura=perfil.meses_sem_cobertura(r.q8_culturas),
    )


@router.get("/fazenda", response_model=FazendaOut)
def ler(u: Usuario = Depends(usuario_atual)) -> FazendaOut:
    if u.fazenda is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fazenda ainda não cadastrada.")
    return _out(u.fazenda)


@router.put("/fazenda", response_model=FazendaOut)
def salvar(dados: SalvarFazenda, u: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)) -> FazendaOut:
    """Salva o questionário (parcial ou completo). Com concluir=true, exige o local do campo."""
    r = dados.respostas
    if dados.concluir and r.q5_local is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Marque no mapa onde fica o campo para concluir.")

    f = u.fazenda or Fazenda(usuario=u)
    f.respostas = r.model_dump(mode="json")
    f.passo_atual = dados.passo_atual
    f.lat = r.q5_local.lat if r.q5_local else None
    f.lon = r.q5_local.lon if r.q5_local else None
    f.nome_local = r.q5_local.nome if r.q5_local else None
    f.irrigacao = r.q6_irrigacao
    f.animais = None if r.q4_animais is None else r.q4_animais == "sim"
    f.terreno = r.q7_terreno
    f.prioridades = list(r.q25_prioridades)
    f.culturas_excluidas = [c.model_dump() for c in r.q26a_excluidas]
    f.equipamentos = [e.model_dump() for e in r.q26b_equipamentos]
    f.perfil = perfil.calcula_perfil(r)
    f.papel = perfil.calcula_papel(r)
    f.retrato_solo = perfil.retrato_solo(r)
    f.proximos_passos = perfil.proximos_passos(r)
    f.calendario = [
        CalendarioItem(ordem=i, cultura_id=c.cultura_id, texto_original=c.texto_original, inicio_mes=c.inicio_mes,
                       fim_mes=c.fim_mes, perene=c.perene, consorcio_com=c.consorcio_com, ocupa=c.ocupa)
        for i, c in enumerate(r.q8_culturas)
    ]
    if dados.concluir:
        f.onboarding_concluido = True
        # O processamento inicial (dados NASA) é a parte 3; por enquanto fica na fila.
        f.status_processamento = "pendente"
    db.add(f)
    db.commit()
    db.refresh(f)
    return _out(f)
