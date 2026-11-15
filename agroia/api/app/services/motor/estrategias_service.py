"""Comparação de rotações para a rota: roda o motor na fazenda do usuário e converte a análise no schema."""
from fastapi import Depends

from app.core.erros import ErroDeNegocio
from app.models import Usuario
from app.schemas import estrategias as s
from app.services import catalogo
from app.services.integracao.nasa_power import ErroNasaPower
from app.services.motor import modelo as m
from app.services.motor.motor_service import MotorService

MSG_SEM_FAZENDA = "Fazenda não encontrada."
MSG_NASA_FORA = "Não consegui os dados de clima da NASA agora. Tente de novo em alguns minutos."


def _item(i: m.ItemRotacao, idioma: str) -> s.ItemEstrategia:
    cultura = catalogo.culturas().get(i.cultura_id) if i.cultura_id else None
    nome = catalogo.nome_exibicao(cultura, idioma) if cultura else i.texto  # fora do catálogo: o texto do produtor
    return s.ItemEstrategia(cultura_id=i.cultura_id, nome=nome, inicio_mes=i.inicio_mes, fim_mes=i.fim_mes, perene=i.perene)


def _resultado(r: m.ResultadoEstrategia, idioma: str) -> s.Resultado:
    return s.Resultado(
        id=r.estrategia.id,
        nome=r.estrategia.nome,
        origem=r.estrategia.origem,
        itens=[_item(i, idioma) for i in r.estrategia.itens],
        nota_final=r.nota_final,
        notas=[
            s.NotaCriterio(
                criterio=c,
                nota=r.notas[c].nota,
                explicacao=r.notas[c].explicacao,
                evidencias=[s.Evidencia(**vars(e)) for e in r.notas[c].evidencias],
            )
            for c in m.CRITERIOS
        ],
        por_que=r.por_que,
        onde_piora=r.onde_piora,
        alertas=[s.Alerta(codigo=a.codigo, texto=a.texto) for a in r.alertas],
        confianca=r.confianca,
        lacunas=r.lacunas,
    )


def analise_para_saida(a: m.Analise, idioma: str = "pt") -> s.Analise:
    """Único lugar que converte a análise do motor (dataclass) no schema da rota."""
    return s.Analise(
        pais=a.pais,
        atual_e_a_melhor=a.atual_e_a_melhor,
        pesos={c: a.pesos[c] for c in m.CRITERIOS},
        atual=_resultado(a.atual, idioma),
        melhores=[_resultado(r, idioma) for r in a.melhores],
        eliminadas=[s.Eliminada(nome=e.estrategia.nome, motivos=e.motivos) for e in a.eliminadas],
        fontes=a.fontes,
        gerado_em=a.gerado_em,
    )


class EstrategiasService:
    def __init__(self, motor: MotorService = Depends()):
        self.motor = motor

    def comparar(self, u: Usuario) -> s.Analise:
        if u.fazenda is None:
            raise ErroDeNegocio(404, MSG_SEM_FAZENDA)
        try:
            analise = self.motor.analisar(u.fazenda)
        except ErroNasaPower:
            raise ErroDeNegocio(503, MSG_NASA_FORA) from None
        return analise_para_saida(analise, u.idioma or "pt")
