"""Pesos das prioridades, nota final, desempate e escolha das duas melhores."""
import pytest

from app.services.motor.modelo import CRITERIOS, Alerta, Estrategia, NotaCriterio, ResultadoEstrategia
from app.services.motor.pontuacao import melhores, nota_final, ordenar, pesos_das_prioridades
from motor_helpers import item


def notas(**valores) -> dict[str, NotaCriterio]:
    return {c: NotaCriterio(c, valores.get(c), "") for c in CRITERIOS}


def resultado(id_, final, terra=0.5, alertas=0, itens=None) -> ResultadoEstrategia:
    itens = itens if itens is not None else (item(id_, 1, 3),)
    return ResultadoEstrategia(
        Estrategia(id_, id_, "janela", itens), notas(terra=terra), final, {}, [], [Alerta("x", "x")] * alertas, "alta", []
    )


def test_sem_prioridade_vale_um_sexto_cada():
    p = pesos_das_prioridades([])
    assert set(p) == set(CRITERIOS) and all(v == pytest.approx(1 / 6) for v in p.values())


def test_uma_prioridade_fica_com_075():
    p = pesos_das_prioridades(["agua"])
    assert p["agua"] == pytest.approx(0.75)
    assert all(p[c] == pytest.approx(0.05) for c in CRITERIOS if c != "agua") and sum(p.values()) == pytest.approx(1)


def test_duas_prioridades_ja_somam_08_sem_mudar():
    p = pesos_das_prioridades(["renda", "terra"])
    assert p["renda"] == pytest.approx(0.5) and p["terra"] == pytest.approx(0.3)
    assert p["agua"] == 0.05 and sum(p.values()) == pytest.approx(1)


def test_tres_prioridades_somam_085_mais_os_tres_nao_escolhidos():
    p = pesos_das_prioridades(["agua", "terra", "renda"])
    assert (p["agua"], p["terra"], p["renda"]) == pytest.approx((0.425, 0.255, 0.17))
    assert p["erosao"] == p["pragas"] == p["animais"] == 0.05 and sum(p.values()) == pytest.approx(1)


def test_prioridade_repetida_ou_desconhecida_e_ignorada():
    assert pesos_das_prioridades(["agua", "agua", "xis"]) == pesos_das_prioridades(["agua"])


def test_criterio_sem_dado_redistribui_o_peso_na_proporcao():
    base = pesos_das_prioridades(["agua", "terra", "renda"])
    n = notas(agua=1.0, terra=0.0, erosao=0.0, pragas=0.0, renda=0.0, animais=None)
    final, efetivos = nota_final(n, base)
    assert "animais" not in efetivos and sum(efetivos.values()) == pytest.approx(1)
    assert efetivos["agua"] == pytest.approx(0.425 / 0.95) and final == pytest.approx(0.425 / 0.95, abs=1e-4)


def test_nenhum_criterio_com_dado_nao_tem_nota():
    assert nota_final(notas(), pesos_das_prioridades([])) == (None, {})


def test_ordem_pela_nota_final_e_empate_pela_terra_depois_pelos_alertas():
    a, b = resultado("a", 0.7), resultado("b", 0.8, terra=0.2)
    c, d = resultado("c", 0.8, terra=0.9), resultado("d", 0.8, terra=0.9, alertas=1)
    assert [r.estrategia.id for r in ordenar([a, d, b, c])] == ["c", "d", "b", "a"]


def test_sem_nota_fica_por_ultimo():
    assert [r.estrategia.id for r in ordenar([resultado("x", None), resultado("y", 0.1)])] == ["y", "x"]


def test_duas_melhores_sao_diferentes_da_atual_e_entre_si():
    atual = resultado("atual", 0.5, itens=(item("soja", 1, 3),))
    igual_a_atual = resultado("clone", 0.99, itens=(item("soja", 1, 3),))
    b1, b2, b3 = resultado("b1", 0.8), resultado("b2", 0.7), resultado("b3", 0.6)
    repetida = resultado("b1_de_novo", 0.75, itens=b1.estrategia.itens)
    top = melhores(atual, [igual_a_atual, b3, repetida, b2, b1])
    assert [r.estrategia.id for r in top] == ["b1", "b2"]


def test_sem_candidatas_nao_ha_melhores():
    assert melhores(resultado("atual", 0.5), []) == []
