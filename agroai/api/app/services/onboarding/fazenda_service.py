"""Salva e lê o questionário da fazenda."""
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, Depends

from app.core.erros import ErroDeNegocio
from app.models import CalendarioItem, Fazenda, Usuario
from app.repositories.fazenda_repository import FazendaRepository
from app.schemas.fazenda import FazendaOut, RetratoSolo, SalvarFazenda
from app.schemas.onboarding import Respostas
from app.schemas.solo import SoloPonto
from app.services.motor.local import pais_e_codigo
from app.services.onboarding import perfil
from app.services.solo.processamento import processar_solo
from app.services.solo.retrato import montar_retrato
from app.services.solo.solo_service import utilizavel

# "processando" há mais que isso = a busca morreu (ex.: o servidor reiniciou): o GET mostra `erro` e a próxima gravação reagenda.
PROCESSANDO_PRESO = timedelta(minutes=15)
# Busca que falhou há menos que isso: a gravação seguinte não insiste (o questionário grava a cada passo).
ERRO_RECENTE = timedelta(minutes=10)


def fazenda_para_saida(f: Fazenda) -> FazendaOut:
    r = Respostas.model_validate(f.respostas or {})
    status = f.status_processamento
    if status == "processando" and not _recente(f.atualizado_em, PROCESSANDO_PRESO):
        status = "erro"
    return FazendaOut(
        id=str(f.id),
        respostas=r,
        passo_atual=f.passo_atual,
        onboarding_concluido=f.onboarding_concluido,
        status_processamento=status,
        perfil=f.perfil,
        papel=f.papel,
        modificadores={"irrigacao": f.irrigacao, "animais": f.animais},
        retrato_solo=RetratoSolo.model_validate(f.retrato_solo or {}),
        proximos_passos=f.proximos_passos or [],
        meses_sem_cobertura=perfil.meses_sem_cobertura(r.q8_culturas),
    )


def _atualiza_local(f: Fazenda, local) -> None:
    """Grava lat/lon e, quando o ponto muda ou ainda não tem país, calcula país e código; sem local, limpa tudo."""
    if local is None:
        f.lat = f.lon = f.pais = f.codigo_local = None
        return
    if (f.lat, f.lon) != (local.lat, local.lon) or f.pais is None:
        f.pais, f.codigo_local = pais_e_codigo(local.lat, local.lon)
    f.lat, f.lon = local.lat, local.lon


def _recente(quando: datetime | None, prazo: timedelta) -> bool:
    return quando is not None and datetime.now(timezone.utc) - quando < prazo


class FazendaService:
    def __init__(self, fazendas: FazendaRepository = Depends()):
        self.fazendas = fazendas

    def ler(self, u: Usuario) -> FazendaOut:
        if u.fazenda is None:
            raise ErroDeNegocio(404, "Fazenda ainda não cadastrada.")
        return fazenda_para_saida(u.fazenda)

    def salvar(self, u: Usuario, dados: SalvarFazenda, tarefas: BackgroundTasks) -> FazendaOut:
        """Salva o questionário (parcial ou completo). Com concluir=true, exige o local do campo.

        Com local novo (ou sem o mapa de solo ainda), o SoilGrids é buscado em segundo plano: a resposta sai com
        `processando` e o retrato só do produtor; a tarefa refaz o retrato e marca `pronto` (ou `erro`).
        """
        r = dados.respostas
        if dados.concluir and r.q5_local is None:
            raise ErroDeNegocio(422, "Marque no mapa onde fica o campo para concluir.")

        f = u.fazenda or Fazenda(usuario=u)
        local_antes, status_antes, atualizado_antes = (f.lat, f.lon), f.status_processamento, f.atualizado_em
        guardado = (f.retrato_solo or {}).get("soilgrids")
        f.respostas = r.model_dump(mode="json")
        f.passo_atual = dados.passo_atual
        _atualiza_local(f, r.q5_local)
        mudou_local = local_antes != (f.lat, f.lon)
        solo = SoloPonto.model_validate(guardado) if guardado and not mudou_local else None
        f.nome_local = r.q5_local.nome if r.q5_local else None
        f.irrigacao = r.q6_irrigacao
        f.animais = None if r.q4_animais is None else r.q4_animais == "sim"
        f.terreno = r.q7_terreno
        f.prioridades = list(r.q25_prioridades)
        f.culturas_excluidas = [c.model_dump() for c in r.q26a_excluidas]
        f.equipamentos = [e.model_dump() for e in r.q26b_equipamentos]
        f.perfil = perfil.calcula_perfil(r)
        f.papel = perfil.calcula_papel(r)
        f.retrato_solo = montar_retrato(r, solo)
        f.proximos_passos = perfil.proximos_passos(r)
        f.calendario = [
            CalendarioItem(ordem=i, cultura_id=c.cultura_id, texto_original=c.texto_original, inicio_mes=c.inicio_mes,
                           fim_mes=c.fim_mes, perene=c.perene, consorcio_com=c.consorcio_com, ocupa=c.ocupa)
            for i, c in enumerate(r.q8_culturas)
        ]
        if dados.concluir:
            f.onboarding_concluido = True
        buscar = False
        if f.lat is None:
            f.status_processamento = "pendente"
        elif solo is not None and utilizavel(solo):
            f.status_processamento = "pronto"  # já tem a textura deste local (ou já se sabe que não há dado)
        elif not mudou_local and (
            (status_antes == "processando" and _recente(atualizado_antes, PROCESSANDO_PRESO))
            or (status_antes == "erro" and _recente(atualizado_antes, ERRO_RECENTE))
        ):
            pass  # a busca deste local já está andando, ou falhou há pouco: não insiste a cada passo do questionário
        else:
            f.status_processamento = "processando"
            buscar = True
        salva = self.fazendas.salvar(f)
        if buscar:
            tarefas.add_task(processar_solo, salva.id, salva.lat, salva.lon)
        return fazenda_para_saida(salva)
