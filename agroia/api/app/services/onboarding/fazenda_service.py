"""Salva e lê o questionário da fazenda."""
from fastapi import Depends

from app.core.erros import ErroDeNegocio
from app.models import CalendarioItem, Fazenda, Usuario
from app.repositories.fazenda_repository import FazendaRepository
from app.schemas.fazenda import FazendaOut, SalvarFazenda
from app.schemas.onboarding import Respostas
from app.services.onboarding import perfil


def fazenda_para_saida(f: Fazenda) -> FazendaOut:
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


class FazendaService:
    def __init__(self, fazendas: FazendaRepository = Depends()):
        self.fazendas = fazendas

    def ler(self, u: Usuario) -> FazendaOut:
        if u.fazenda is None:
            raise ErroDeNegocio(404, "Fazenda ainda não cadastrada.")
        return fazenda_para_saida(u.fazenda)

    def salvar(self, u: Usuario, dados: SalvarFazenda) -> FazendaOut:
        """Salva o questionário (parcial ou completo). Com concluir=true, exige o local do campo."""
        r = dados.respostas
        if dados.concluir and r.q5_local is None:
            raise ErroDeNegocio(422, "Marque no mapa onde fica o campo para concluir.")

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
        return fazenda_para_saida(self.fazendas.salvar(f))
