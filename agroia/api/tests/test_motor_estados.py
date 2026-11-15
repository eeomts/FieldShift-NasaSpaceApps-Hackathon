"""Estado da fazenda pelo código do local e a regra 13 (estados_validos) no filtro e nas candidatas."""
import pytest

from app.services.motor.candidatas import gerar_candidatas
from app.services.motor.estados import estado_do_local
from app.services.motor.filtro import avaliar
from app.services.motor.modelo import Estrategia
from motor_helpers import cultura, entradas, item


@pytest.mark.parametrize(
    "pais, codigo, estado",
    [("US", "19169", "IA"), ("US", "19001", "IA"), ("US", "20135", "KS"), ("US", "13277", "GA"), ("BR", "5107925", "MT"),
     ("BR", "5218805", "GO"), ("BR", "4314100", "RS"), ("BR", "5300108", "DF"), ("BR", "5107925 ", "MT")],
)  # fmt: skip
def test_estado_pelo_codigo_do_condado_ou_do_municipio(pais, codigo, estado):
    assert estado_do_local(pais, codigo) == estado


def test_estado_desconhecido_vira_none():
    assert estado_do_local("US", None) is None and estado_do_local("BR", "") is None
    assert estado_do_local(None, "19169") is None and estado_do_local("AR", "19169") is None
    assert estado_do_local("US", "99999") is None and estado_do_local("BR", "99") is None


def test_o_mesmo_prefixo_vale_estado_diferente_em_cada_pais():
    assert estado_do_local("US", "51001") == "VA" and estado_do_local("BR", "5100000") == "MT"


# --- candidatas: cultura fora dos estados válidos não é sugerida
def atual_com(*itens) -> Estrategia:
    return Estrategia("atual", "Sua rotação atual", "atual", tuple(itens))


def catalogo():
    cs = [
        cultura("soja", tipos=("comercial", "fixadora_n"), fixa_nitrogenio=True, ciclo_dias_max=140),
        cultura("milho", ciclo_dias_max=145),
        cultura("trevo", tipos=("cobertura", "fixadora_n"), fixa_nitrogenio=True, ciclo_dias_min=56, estados_validos=("GA",)),
        cultura("aveia", tipos=("cobertura",), ciclo_dias_min=56),
    ]
    return {c.id: c for c in cs}


def ids_de(candidatas):
    return {c.id for c in candidatas}


def test_cultura_de_ga_nao_e_candidata_em_fazenda_de_ia():
    a = atual_com(item("soja", 10, 2), item("milho", 2, 6))
    com_ia = ids_de(gerar_candidatas(a, catalogo(), [7, 8, 9], "IA"))
    assert "janela:aveia" in com_ia and not any("trevo" in i for i in com_ia)


def test_cultura_de_ga_e_candidata_em_ga_e_sem_estado_conhecido():
    a = atual_com(item("soja", 10, 2), item("milho", 2, 6))
    assert "janela:trevo" in ids_de(gerar_candidatas(a, catalogo(), [7, 8, 9], "GA"))
    assert "janela:trevo" in ids_de(gerar_candidatas(a, catalogo(), [7, 8, 9], None))
    assert "janela:trevo" in ids_de(gerar_candidatas(a, catalogo(), [7, 8, 9]))


def test_cultura_sem_estados_validos_nao_muda_com_o_estado():
    a = atual_com(item("soja", 10, 2), item("milho", 2, 6))
    sem_lista = {k: v for k, v in catalogo().items() if k != "trevo"}
    assert ids_de(gerar_candidatas(a, sem_lista, [7, 8, 9], "IA")) == ids_de(gerar_candidatas(a, sem_lista, [7, 8, 9], None))


def test_cultura_fora_da_regiao_na_atual_continua_nas_contas_das_candidatas():
    # a principal (soja, só GA) está na atual: a troca da principal por tolerante à seca continua sendo gerada em IA
    cs = catalogo()
    cs["soja"] = cultura("soja", tipos=("comercial", "fixadora_n"), fixa_nitrogenio=True, ciclo_dias_max=140, estados_validos=("GA",))
    cs["sorgo"] = cultura("sorgo", tipos=("comercial", "tolerante_seca"), ciclo_dias_min=90)
    a = atual_com(item("soja", 10, 2))
    assert "tolerante_seca:soja->sorgo" in ids_de(gerar_candidatas(a, cs, [], "IA"))


# --- filtro: aviso na rotação atual e lacuna sem estado
RESP = (10, 12)


def e_trevo(**mudancas):
    c = cultura("trevo", estados_validos=("GA",))
    return c, entradas([item("trevo", *RESP)], [c], **mudancas)


def test_atual_fora_da_regiao_continua_com_aviso_sem_dado_para_a_regiao():
    c, e = e_trevo(estado="IA")
    r = avaliar([item("trevo", *RESP)], e, eliminar=False)
    assert not r.eliminada and [a.codigo for a in r.alertas] == ["sem_dado_regiao"]
    assert "sem dado para sua região" in r.alertas[0].texto and "IA" in r.alertas[0].texto and "GA" in r.alertas[0].texto


def test_nunca_elimina_por_regiao():
    c, e = e_trevo(estado="IA")
    assert not avaliar([item("trevo", *RESP)], e, eliminar=True).eliminada


def test_dentro_da_regiao_sem_aviso_nem_lacuna():
    c, e = e_trevo(estado="GA")
    r = avaliar([item("trevo", *RESP)], e, eliminar=True)
    assert not r.alertas and not any("estado" in l for l in r.lacunas)


def test_estado_desconhecido_nao_filtra_mas_registra_lacuna():
    c, e = e_trevo(estado=None)
    r = avaliar([item("trevo", *RESP)], e, eliminar=True)
    assert not r.eliminada and not r.alertas
    assert any("não sabemos o estado da fazenda" in l for l in r.lacunas)


def test_sem_estados_validos_nao_muda_nada():
    c = cultura("milho")
    for estado in ("IA", None):
        r = avaliar([item("milho", *RESP)], entradas([item("milho", *RESP)], [c], estado=estado), eliminar=True)
        assert not r.alertas and not r.lacunas
