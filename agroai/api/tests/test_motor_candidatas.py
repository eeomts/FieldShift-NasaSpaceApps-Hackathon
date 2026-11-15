"""Candidatas: atual, janela vazia, troca da principal por tolerante à seca e leguminosa."""
from app.services.motor.calendario import maior_janela_vazia, meses_do_periodo, meses_necessarios, partes_por_terco
from app.services.motor.candidatas import chave, gerar_candidatas
from app.services.motor.modelo import Estrategia
from app.services.motor.parametros import MAX_CANDIDATAS
from motor_helpers import cultura, item


def atual(*itens) -> Estrategia:
    return Estrategia("atual", "Sua rotação atual", "atual", tuple(itens))


CATALOGO = {
    c.id: c
    for c in [
        cultura("soja", tipos=("comercial", "fixadora_n"), fixa_nitrogenio=True, ciclo_dias_max=140),
        cultura("milho", ciclo_dias_max=145),
        cultura("sorgo", tipos=("comercial", "tolerante_seca"), ciclo_dias_min=90),
        cultura("milheto", tipos=("cobertura", "tolerante_seca"), ciclo_dias_min=45),
        cultura("caupi", tipos=("comercial", "fixadora_n", "tolerante_seca"), fixa_nitrogenio=True, ciclo_dias_min=60),
        cultura("crotalaria", tipos=("cobertura", "fixadora_n"), fixa_nitrogenio=True, ciclo_dias_min=56),
        cultura("trigo", ciclo_dias_min=105),
        cultura("pastagem", tipos=("forrageira", "tolerante_seca", "fixadora_n"), perene=True, ciclo_dias_min=None),
        cultura("mandioca", tipos=("comercial", "tolerante_seca"), perene=True, ciclo_dias_min=180),
    ]
}


def ids(candidatas, origem=None):
    return {c.id for c in candidatas if origem is None or c.origem == origem}


def test_meses_do_periodo_com_virada_de_ano_e_perene():
    assert meses_do_periodo(11, 2, False) == [11, 12, 1, 2] and meses_do_periodo(None, 3, False) == []
    assert meses_do_periodo(3, 3, False) == [3] and meses_do_periodo(5, 6, True) == list(range(1, 13))


def test_maior_janela_vazia_continua_inclusive_entre_dezembro_e_janeiro():
    assert maior_janela_vazia([7, 8, 9]) == (7, 3)
    assert maior_janela_vazia([1, 2, 11, 12, 5]) == (11, 4)
    assert maior_janela_vazia([4, 5, 9, 10, 11]) == (9, 3)
    assert maior_janela_vazia([]) is None


def test_meses_necessarios_e_tercos():
    assert meses_necessarios(90) == 3 and meses_necessarios(91.2) == 3 and meses_necessarios(92) == 4
    for partes in partes_por_terco(5):
        assert abs(sum(f for _, f in partes) - 1) < 1e-9
    assert [t for t, _ in partes_por_terco(3)[0]] == [0] and [t for t, _ in partes_por_terco(1)[0]] == [0, 1, 2]


def test_janela_so_com_cultura_cujo_ciclo_minimo_cabe_e_perene_fora():
    a = atual(item("soja", 10, 2), item("milho", 2, 6))  # vazio: jul-set (3 meses = 91,2 dias)
    c = gerar_candidatas(a, CATALOGO, [7, 8, 9])
    janela = {x.id: x for x in c if x.origem == "janela"}
    assert set(janela) == {"janela:sorgo", "janela:milheto", "janela:caupi", "janela:crotalaria"}  # soja, milho e trigo (>= 100 d) não cabem
    sorgo = janela["janela:sorgo"].itens[-1]
    assert (sorgo.cultura_id, sorgo.inicio_mes, sorgo.fim_mes) == ("sorgo", 7, 9)
    milheto = janela["janela:milheto"].itens[-1]
    assert (milheto.inicio_mes, milheto.fim_mes) == (7, 8)  # 45 dias = 2 meses, plantado no início
    assert not any("pastagem" in x or "mandioca" in x for x in janela)


def test_sem_janela_vazia_nao_ha_candidata_de_janela():
    a = atual(item("soja", 1, 12), item("milho", 1, 12))
    assert not [x for x in gerar_candidatas(a, CATALOGO, []) if x.origem == "janela"]


def test_principal_e_a_comercial_de_ciclo_mais_longo_e_e_trocada_por_tolerante_a_seca():
    a = atual(item("soja", 10, 2), item("milho", 2, 6))  # milho 145 d > soja 140 d
    c = [x for x in gerar_candidatas(a, CATALOGO, [7, 8, 9]) if x.origem == "tolerante_seca"]
    assert ids(c) == {"tolerante_seca:milho->sorgo", "tolerante_seca:milho->milheto", "tolerante_seca:milho->caupi"}
    troca = next(x for x in c if x.id.endswith("sorgo"))
    assert [(i.cultura_id, i.inicio_mes, i.fim_mes) for i in troca.itens] == [("soja", 10, 2), ("sorgo", 2, 6)]  # mesmo período


def test_troca_nao_repete_cultura_que_ja_esta_na_rotacao():
    a = atual(item("milho", 10, 2), item("sorgo", 3, 6))
    assert "tolerante_seca:milho->sorgo" not in ids(gerar_candidatas(a, CATALOGO, [7, 8, 9]))


def test_leguminosa_no_lugar_de_cultura_nao_principal_e_nunca_no_lugar_de_leguminosa():
    a = atual(item("milho", 10, 2), item("trigo", 3, 6))  # principal: milho; trigo é o não principal
    legumes = ids(gerar_candidatas(a, CATALOGO, [7, 8, 9]), "leguminosa")
    assert {"leguminosa:trigo->caupi", "leguminosa:trigo->crotalaria", "leguminosa:trigo->soja"} <= legumes
    assert not any(i.startswith("leguminosa:milho->") for i in legumes)  # a principal fica
    com_soja = atual(item("milho", 10, 2), item("soja", 3, 6))
    assert not any(i.startswith("leguminosa:soja->") for i in ids(gerar_candidatas(com_soja, CATALOGO, []), "leguminosa"))


def test_sem_duplicata_e_sem_a_propria_atual():
    a = atual(item("soja", 10, 2), item("milho", 2, 6))
    c = gerar_candidatas(a, CATALOGO, [7, 8, 9])
    chaves = [chave(x) for x in c]
    assert len(chaves) == len(set(chaves)) and chave(a) not in chaves
    assert "leguminosa:janela:caupi" not in ids(c)  # a fixadora na janela já veio da regra 1


def test_no_maximo_30_candidatas():
    muitas = {
        f"c{i}": cultura(f"c{i}", tipos=("comercial", "tolerante_seca", "fixadora_n"), fixa_nitrogenio=True, ciclo_dias_min=30)
        for i in range(60)
    }
    muitas["milho"] = cultura("milho")
    a = atual(item("milho", 10, 2), item("trigo", 3, 6))
    assert len(gerar_candidatas(a, muitas, [7, 8, 9])) == MAX_CANDIDATAS


def test_cultura_fora_do_catalogo_na_atual_nao_quebra_e_nao_e_principal():
    a = atual(item(None, 10, 2, texto="amendoim"), item("milho", 2, 6))
    c = gerar_candidatas(a, CATALOGO, [7, 8, 9])
    assert "tolerante_seca:milho->sorgo" in ids(c)
    assert any(x.id.startswith("leguminosa:0->") for x in c)  # pode trocar a cultura fora do catálogo por uma leguminosa


def test_meses_do_terco_medio_sao_os_meses_inteiros_que_tocam_o_terco():
    from app.services.motor.calendario import meses_do_terco_medio

    assert meses_do_terco_medio([10, 11, 12]) == [11]
    assert meses_do_terco_medio([6, 7, 8, 9, 10]) == [7, 8, 9]
    assert meses_do_terco_medio([3]) == [3] and meses_do_terco_medio([3, 4]) == [3, 4]
    assert meses_do_terco_medio([11, 12, 1, 2, 3, 4]) == [1, 2]
