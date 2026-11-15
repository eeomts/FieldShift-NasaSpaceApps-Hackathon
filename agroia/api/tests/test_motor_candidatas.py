"""Candidatas: atual, janela vazia, troca da principal por tolerante à seca e leguminosa."""
from app.services.motor.calendario import maior_janela_vazia, meses_do_periodo, meses_necessarios, partes_por_terco
from app.services.motor.candidatas import chave, gerar_candidatas
from app.services.motor.catalogo import catalogo_do_pais
from app.services.motor.modelo import Estrategia
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


def test_nao_ha_limite_de_candidatas():
    muitas = {
        f"c{i}": cultura(f"c{i}", tipos=("comercial", "tolerante_seca", "fixadora_n"), fixa_nitrogenio=True, ciclo_dias_min=30)
        for i in range(60)
    }
    muitas["milho"] = cultura("milho")
    a = atual(item("milho", 10, 2), item("trigo", 3, 6))
    c = gerar_candidatas(a, muitas, [7, 8, 9])
    assert len(c) == 180 > 30  # 60 na janela, 60 trocas da principal por tolerante à seca e 60 trocas do trigo por leguminosa
    assert len({x.id for x in c}) == len(c)  # sem corte e sem repetir


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


# --- regra 12: coberturas só entram onde a janela de semeadura e a cultura anterior permitem
def cob(id_, inicio, fim, condicao=("apos_colheita_graos",), ciclo=45, **mais):
    ini, fi = (tuple(int(p) for p in x.split("-")) if x else None for x in (inicio, fim))
    mais.setdefault("tipos", ("cobertura",))
    return cultura(id_, ciclo_dias_min=ciclo, semeadura_inicio=ini, semeadura_fim=fi, condicao_semeadura=condicao, **mais)


def leg(id_, inicio, fim, ciclo=56):
    return cob(id_, inicio, fim, ciclo=ciclo, tipos=("cobertura", "fixadora_n"), fixa_nitrogenio=True)


def cands(catalogo, a, vazios, origem="janela"):
    return {x.id: x for x in gerar_candidatas(a, {c.id: c for c in catalogo}, vazios) if x.origem == origem}


def periodo(x, pos=-1):
    return (x.itens[pos].inicio_mes, x.itens[pos].fim_mes)


def test_aveia_e_nabo_dos_eua_nao_entram_depois_de_milho_ou_soja_colhidos_em_outubro():
    us = catalogo_do_pais("US")
    cat = [us["soja"], us["milho"], us["aveia"], us["nabo_forrageiro"]]  # semeadura em agosto e setembro
    for x in ("milho", "soja"):
        c = cands(cat, atual(item(x, 5, 10)), [11, 12, 1, 2, 3, 4])
        assert "janela:aveia" not in c and "janela:nabo_forrageiro" not in c, x


def test_aveia_dos_eua_serve_depois_de_trigo_e_nao_depois_de_milho():
    us = catalogo_do_pais("US")
    cat = [us["trigo"], us["milho"], us["aveia"]]
    depois_do_trigo = cands(cat, atual(item("trigo", 2, 7)), [8, 9, 10, 11, 12, 1])  # trigo colhido em julho
    assert periodo(depois_do_trigo["janela:aveia"]) == (8, 10) and depois_do_trigo["janela:aveia"].alertas == ()
    assert "janela:aveia" not in cands(cat, atual(item("milho", 2, 7)), [8, 9, 10, 11, 12, 1])


def test_centeio_dos_eua_cabe_em_outubro_depois_de_soja_colhida_em_setembro():
    us = catalogo_do_pais("US")
    cat = [us["soja"], us["centeio"]]
    assert periodo(cands(cat, atual(item("soja", 4, 9)), [10, 11, 12, 1, 2, 3])["janela:centeio"]) == (10, 3)  # 178 dias: 6 meses livres
    assert "janela:centeio" not in cands(cat, atual(item("soja", 4, 9)), [10, 11, 12, 1, 2])  # 5 meses: o ciclo não cabe


def test_cobertura_e_empurrada_para_o_inicio_da_janela_de_semeadura_se_ainda_cabe():
    c = cands([cultura("trigo"), cob("aveia", "08-01", "09-15")], atual(item("trigo", 1, 6)), [7, 8, 9, 10, 11, 12])
    assert periodo(c["janela:aveia"]) == (8, 9)  # livre desde julho, semeadura só em ago-set: 45 dias = 2 meses a partir de agosto
    assert not cands([cultura("trigo"), cob("aveia", "12-01", "12-31")], atual(item("trigo", 1, 6)), [7, 8, 9])  # nenhum mês livre na janela
    assert not cands([cultura("trigo"), cob("aveia", "09-01", "09-30", ciclo=100)], atual(item("trigo", 1, 6)), [7, 8, 9])  # empurrada, o ciclo não cabe


def test_cobertura_so_a_lanco_nunca_e_sugerida_e_silagem_sozinha_tambem_nao():
    for cond in (("a_lanco_lavoura_em_pe",), ("apos_silagem",), ("apos_silagem", "a_lanco_lavoura_em_pe")):
        assert not cands([cultura("milho"), cob("aveia", "07-01", "09-30", cond)], atual(item("milho", 1, 6)), [7, 8, 9]), cond
    assert not cands([cob("aveia", "07-01", "09-30", ("a_lanco_lavoura_em_pe",))], atual(item(None, 1, 6, texto="x")), [7, 8, 9])  # nem sem cultura anterior
    assert cands([cultura("milho"), cob("aveia", "07-01", "09-30", ("apos_silagem", "apos_colheita_graos"))], atual(item("milho", 1, 6)), [7, 8, 9])  # outra condição serve


def test_cobertura_sem_condicao_nao_e_restringida_pela_cultura_anterior():
    c = cands([cultura("pasto", tipos=("forrageira",)), cob("aveia", "07-01", "09-30", ())], atual(item("pasto", 1, 6)), [7, 8, 9])
    assert "janela:aveia" in c and c["janela:aveia"].alertas == ()


def test_apos_colheita_de_graos_exige_comercial_nao_perene():
    pasto, mandioca = cultura("pasto", tipos=("forrageira",)), cultura("mandioca", perene=True)
    aveia = cob("aveia", "07-01", "09-30")
    assert not cands([pasto, aveia], atual(item("pasto", 1, 6)), [7, 8, 9])  # a anterior não é grão
    assert not cands([mandioca, aveia], atual(item("mandioca", 1, 6)), [7, 8, 9])  # nem perene
    assert "janela:aveia" in cands([cultura("milho"), aveia], atual(item("milho", 1, 6)), [7, 8, 9])


def test_cobertura_sem_janela_e_sugerida_com_alerta_de_janela_nao_confirmada():
    x = cands([cultura("milho"), cob("milheto", None, None, ())], atual(item("milho", 1, 6)), [7, 8, 9])["janela:milheto"]
    assert periodo(x) == (7, 8) and [a.codigo for a in x.alertas] == ["janela_nao_confirmada"]
    assert x.alertas[0].texto == "Milheto: a época de semeadura ainda não foi confirmada para a sua região."


def test_cultura_anterior_fora_do_catalogo_sugere_com_alerta_para_conferir():
    x = cands([cob("aveia", "03-01", "05-31")], atual(item(None, 10, 2, texto="amendoim")), [3, 4, 5])["janela:aveia"]
    assert [a.codigo for a in x.alertas] == ["janela_nao_confirmada"]
    assert x.alertas[0].texto == "Aveia: confira se dá para semear depois de amendoim."


def test_janela_que_cruza_o_ano_out_a_mar():
    cro, milho = cob("crotalaria", "10-01", "03-31", ciclo=56), cultura("milho")
    assert periodo(cands([milho, cro], atual(item("milho", 5, 12)), [1, 2, 3])["janela:crotalaria"]) == (1, 2)  # janeiro está na janela
    assert periodo(cands([milho, cro], atual(item("milho", 5, 9)), [10, 11, 12])["janela:crotalaria"]) == (10, 11)
    assert not cands([milho, cro], atual(item("milho", 11, 4)), [5, 6, 7])  # mai-jul fica fora (colheita em abril)


def test_troca_por_cobertura_respeita_a_janela_e_empurra_o_inicio():
    milho, trigo = cultura("milho", ciclo_dias_max=145), cultura("trigo")
    a = atual(item("milho", 10, 2), item("trigo", 3, 6))  # principal: milho; a leguminosa entra no lugar do trigo (mar-jun)
    dentro = cands([milho, trigo, leg("crotalaria", "03-01", "05-31")], a, [], "leguminosa")["leguminosa:trigo->crotalaria"]
    assert periodo(dentro, 1) == (3, 6) and dentro.alertas == ()
    empurrada = cands([milho, trigo, leg("crotalaria", "05-01", "05-31")], a, [], "leguminosa")["leguminosa:trigo->crotalaria"]
    assert periodo(empurrada, 1) == (5, 6)  # semeada em maio, quando a janela dela abre
    assert "leguminosa:trigo->crotalaria" not in cands([milho, trigo, leg("crotalaria", "08-01", "09-30")], a, [], "leguminosa")


def test_troca_da_principal_por_cobertura_tolerante_a_seca_tambem_segue_a_janela():
    a = atual(item("soja", 10, 2), item("milho", 2, 6))
    soja, milho = cultura("soja", ciclo_dias_max=140), cultura("milho", ciclo_dias_max=145)

    def milheto(ini, fim):
        return cob("milheto", ini, fim, tipos=("cobertura", "tolerante_seca"))

    assert "tolerante_seca:milho->milheto" in cands([soja, milho, milheto("02-01", "03-31")], a, [], "tolerante_seca")
    assert "tolerante_seca:milho->milheto" not in cands([soja, milho, milheto("09-01", "10-31")], a, [], "tolerante_seca")


def test_cultura_comercial_ignora_a_janela_de_semeadura_das_colunas():
    sorgo = cultura("sorgo", tipos=("comercial", "tolerante_seca"), ciclo_dias_min=90, semeadura_inicio=(1, 1), semeadura_fim=(1, 31), condicao_semeadura=("apos_cereal_inverno",))
    r = cands([cultura("milho"), sorgo], atual(item("milho", 1, 6)), [7, 8, 9])
    assert periodo(r["janela:sorgo"]) == (7, 9) and r["janela:sorgo"].alertas == ()
