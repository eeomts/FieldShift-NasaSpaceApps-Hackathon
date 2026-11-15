"""Motor de rotação: junta entradas, candidatas, filtro, notas, pesos e explicação numa Analise."""
from datetime import datetime, timezone

from fastapi import Depends

from app.models import Fazenda
from app.services.clima.clima_service import ClimaService
from app.services.motor.candidatas import gerar_candidatas
from app.services.motor.criterios import FONTE_BASE, FONTE_CALENDARIO, calcular_notas
from app.services.motor.entradas import ClimaDoServico, EntradasMotor, montar_entradas
from app.services.motor.explicacao import confianca, onde_piora, por_que
from app.services.motor.filtro import ResultadoFiltro, avaliar
from app.services.motor.modelo import Analise, Eliminada, Estrategia, ResultadoEstrategia
from app.services.motor.pontuacao import melhores, nota_final, pesos_das_prioridades
from app.services.motor.relevo_service import RelevoService


def _resultado(estrategia: Estrategia, e: EntradasMotor, pesos: dict[str, float], filtro: ResultadoFiltro) -> ResultadoEstrategia:
    notas, lac_notas = calcular_notas(estrategia, e)
    nota, efetivos = nota_final(notas, pesos)
    conf, lac_conf = confianca(estrategia.itens, e.catalogo)
    lacunas = list(dict.fromkeys(filtro.lacunas + lac_notas + lac_conf))
    return ResultadoEstrategia(estrategia, notas, nota, efetivos, [], filtro.alertas, conf, lacunas)


def analisar_entradas(e: EntradasMotor, agora: datetime | None = None) -> Analise:
    """Análise pura sobre entradas prontas (sem banco nem rede)."""
    pesos = pesos_das_prioridades(e.prioridades)
    estrategia_atual = Estrategia("atual", "Sua rotação atual", "atual", e.atual)
    atual = _resultado(estrategia_atual, e, pesos, avaliar(e.atual, e, eliminar=False))  # a atual nunca é eliminada

    eliminadas: list[Eliminada] = []
    sobreviventes: list[ResultadoEstrategia] = []
    for cand in gerar_candidatas(estrategia_atual, e.catalogo, e.meses_vazios, e.estado):
        novos = [i for i in cand.itens if i not in e.atual]  # o que já está na atual não reprova a candidata
        filtro = avaliar(novos, e, eliminar=True)
        if filtro.eliminada:
            eliminadas.append(Eliminada(cand, filtro.motivos))
        else:
            sobreviventes.append(_resultado(cand, e, pesos, filtro))

    top = melhores(atual, sobreviventes)
    for r in top:
        r.por_que = por_que(r.notas, atual.notas, r.pesos)
        r.onde_piora = onde_piora(r.notas, atual.notas, r.pesos)
    fontes = [FONTE_BASE, e.clima.fonte, FONTE_CALENDARIO, "Prioridades e restrições informadas pelo produtor"]
    if e.relevo is not None:
        fontes.insert(2, e.relevo.fonte)
    # sem nota da atual não dá para dizer; senão, ela é a melhor se nenhuma das melhores a supera
    atual_e_a_melhor = atual.nota_final is not None and not any(r.nota_final is not None and r.nota_final > atual.nota_final for r in top)
    return Analise(e.pais, atual, top, eliminadas, pesos, fontes, agora or datetime.now(timezone.utc), atual_e_a_melhor)


class MotorService:
    def __init__(self, clima: ClimaService = Depends(), relevo: RelevoService = Depends()):
        self.clima = ClimaDoServico(clima)
        self.relevo = relevo

    def analisar(self, f: Fazenda) -> Analise:
        """Compara a rotação atual da fazenda com alternativas. Sem local, país sem base ou sem calendário: erro de negócio."""
        return analisar_entradas(montar_entradas(f, self.clima, self.relevo))
