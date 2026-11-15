"""Candidatas: atual, janela vazia, troca da principal por tolerante à seca e leguminosa."""
from app.services.motor.calendario import maior_janela_vazia, meses_do_periodo, meses_necessarios, partes_por_terco
from app.services.motor.candidatas import _mes_na_janela_de_semeadura, chave, gerar_candidatas
from app.services.motor.motor_service import analisar_entradas
from app.services.motor.modelo import Estrategia
from app.services.motor.parametros import MAX_CANDIDATAS
from motor_helpers import cultura, entradas, item


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


# --- regra 12: janela de semeadura e condição das coberturas
def cobertura(id_="nabo", inicio="04-01", fim="05-31", condicao="apos_colheita_graos", ciclo=60, **mais):
    mais.setdefault("tipos", ("cobertura",))
    return cultura(id_, ciclo_dias_min=ciclo, semeadura_inicio=inicio, semeadura_fim=fim, condicao_semeadura=condicao, **mais)


def so_janela(a, c, vazios, id_="nabo"):
    """A candidata de janela da cobertura `id_` (ou None): (inicio, fim, lacunas)."""
    cat = {x.id: x for x in [cultura("soja"), cultura("trigo", ciclo_dias_min=105), cultura("aveia", ciclo_dias_min=100), c]}
    achada = [x for x in gerar_candidatas(a, cat, vazios) if x.id == f"janela:{id_}"]
    if not achada:
        return None
    i = achada[0].itens[-1]
    return i.inicio_mes, i.fim_mes, list(achada[0].lacunas)


def test_mes_na_janela_de_semeadura_conta_o_mes_que_toca_a_janela_e_a_que_vira_o_ano():
    nabo = cobertura()  # 01/04 a 31/05
    assert [m for m in range(1, 13) if _mes_na_janela_de_semeadura(nabo, m)] == [4, 5]
    crotalaria = cobertura("c", "10-01", "03-31")  # vira o ano
    assert [m for m in range(1, 13) if _mes_na_janela_de_semeadura(crotalaria, m)] == [1, 2, 3, 10, 11, 12]
    milheto = cobertura("m", "01-21", "04-15")  # janeiro entra: a janela começa no dia 21
    assert [m for m in range(1, 13) if _mes_na_janela_de_semeadura(milheto, m)] == [1, 2, 3, 4]
    assert _mes_na_janela_de_semeadura(cobertura("x", None, None), 4) is None and _mes_na_janela_de_semeadura(cobertura("x", "abc", "05-31"), 4) is None


def test_nabo_nao_entra_numa_janela_vazia_de_janeiro_a_marco():
    a = atual(item("soja", 8, 12), item("trigo", 4, 7))  # vazio: jan-mar
    assert so_janela(a, cobertura(), [1, 2, 3]) is None


def test_nabo_entra_numa_janela_vazia_de_abril_a_julho_no_primeiro_mes_da_janela_de_semeadura():
    a = atual(item("soja", 8, 3))
    assert so_janela(a, cobertura(), [4, 5, 6, 7]) == (4, 5, [])  # 60 dias = 2 meses, plantado em abril
    a = atual(item("soja", 8, 2))
    assert so_janela(a, cobertura(), [3, 4, 5, 6]) == (4, 5, [])  # março não é época: começa em abril, ainda cabe


def test_cobertura_nao_entra_se_o_ciclo_minimo_nao_cabe_depois_do_inicio_da_semeadura():
    a = atual(item("soja", 8, 2))
    assert so_janela(a, cobertura(), [3, 4]) is None  # começaria em abril: sobra 1 mês (30 dias) para 60 dias de ciclo


def test_janela_de_semeadura_que_vira_o_ano():
    crot = cobertura("crot", "10-01", "03-31", ciclo=56)
    a = atual(item("soja", 1, 6))
    assert so_janela(a, crot, [7, 8, 9, 10, 11], "crot") == (10, 11, [])  # começa em outubro; 2 meses cobrem 56 dias
    assert so_janela(a, crot, [7, 8, 9, 10], "crot") is None  # só outubro sobra: 30 dias < 56
    a = atual(item("soja", 5, 11))
    assert so_janela(a, crot, [12, 1, 2, 3], "crot") == (12, 1, [])  # janela vazia que também vira o ano


def test_apos_cereal_inverno_depois_de_soja_nao_gera_e_depois_de_trigo_gera():
    aveia = cobertura("aveia", "08-15", "09-15", "apos_cereal_inverno", ciclo=61)
    assert so_janela(atual(item("soja", 1, 7)), aveia, [8, 9, 10, 11], "aveia") is None
    assert so_janela(atual(item("trigo", 1, 7)), aveia, [8, 9, 10, 11], "aveia") == (8, 10, [])


def test_apos_colheita_de_graos_exige_cultura_comercial_antes():
    depois_de_cobertura = atual(item("aveia", 8, 3))  # a aveia deste catálogo é só cobertura (não é grão de venda)
    cat = {"aveia": cobertura("aveia", "03-01", "03-31", ciclo=100), "nabo": cobertura()}
    assert not [x for x in gerar_candidatas(depois_de_cobertura, cat, [4, 5, 6, 7]) if x.id == "janela:nabo"]
    assert so_janela(atual(item("soja", 8, 3)), cobertura(), [4, 5, 6, 7]) == (4, 5, [])


def test_a_lanco_na_lavoura_em_pe_nunca_vira_sugestao_mas_a_outra_condicao_vale():
    a = atual(item("soja", 8, 3))
    assert so_janela(a, cobertura(condicao="a_lanco_lavoura_em_pe"), [4, 5, 6, 7]) is None
    assert so_janela(a, cobertura(condicao="apos_colheita_graos|a_lanco_lavoura_em_pe"), [4, 5, 6, 7]) == (4, 5, [])
    sem_a_lanco = atual(item("trigo", 8, 3))
    assert so_janela(sem_a_lanco, cobertura(condicao="apos_cereal_inverno|a_lanco_lavoura_em_pe"), [4, 5, 6, 7]) == (4, 5, [])


def test_apos_silagem_gera_com_lacuna_em_linguagem_simples():
    a = atual(item("soja", 8, 3))
    r = so_janela(a, cobertura(condicao="apos_cereal_inverno|apos_silagem"), [4, 5, 6, 7])
    assert r[:2] == (4, 5) and len(r[2]) == 1 and "silagem" in r[2][0] and r[2][0].startswith("Nabo: ")
    # com a condição verificável atendida, a lacuna da silagem não aparece
    assert so_janela(atual(item("trigo", 8, 3)), cobertura(condicao="apos_cereal_inverno|apos_silagem"), [4, 5, 6, 7])[2] == []


def test_valor_de_condicao_desconhecido_e_cultura_anterior_desconhecida_geram_com_lacuna():
    a = atual(item("soja", 8, 3))
    r = so_janela(a, cobertura(condicao="depois_de_algo_novo"), [4, 5, 6, 7])
    assert r[:2] == (4, 5) and "não conseguimos confirmar" in r[2][0]
    fora = atual(item(None, 8, 3, texto="amendoim"))
    r = so_janela(fora, cobertura(), [4, 5, 6, 7])
    assert r[:2] == (4, 5) and "não conseguimos confirmar" in r[2][0]


def test_cobertura_sem_janela_no_catalogo_gera_com_lacuna_e_grao_nao_tem_lacuna():
    a = atual(item("soja", 8, 3))
    sem = cultura("nabo", tipos=("cobertura",), ciclo_dias_min=60)
    inicio, fim, lacunas = so_janela(a, sem, [1, 2, 3, 4])
    assert (inicio, fim) == (1, 2)  # sem janela segue como antes: no início da janela vazia
    assert len(lacunas) == 1 and "ainda não confirmamos a melhor época" in lacunas[0]
    cat = {"soja": cultura("soja"), "sorgo": cultura("sorgo", ciclo_dias_min=60)}
    graos = [x for x in gerar_candidatas(a, cat, [4, 5, 6, 7]) if x.id == "janela:sorgo"]
    assert graos and graos[0].lacunas == ()


def test_troca_por_cobertura_tambem_respeita_a_janela_de_semeadura():
    a = atual(item("soja", 10, 2), item("milho", 6, 9))  # a principal (milho) começa em junho
    fora = cobertura("nabo", ciclo=60, tipos=("cobertura", "tolerante_seca"))
    catalogo = {"soja": cultura("soja", ciclo_dias_max=140), "milho": cultura("milho", ciclo_dias_max=145), "nabo": fora}
    assert "tolerante_seca:milho->nabo" not in ids(gerar_candidatas(a, catalogo, []))  # junho: fora de 01/04 a 31/05
    a = atual(item("soja", 10, 2), item("milho", 4, 7))
    assert "tolerante_seca:milho->nabo" in ids(gerar_candidatas(a, catalogo, []))


def test_lacuna_da_candidata_chega_ao_resultado_da_analise():
    sem_janela = cultura("milheto", tipos=("cobertura", "tolerante_seca"), ciclo_dias_min=45)
    e = entradas([item("soja", 10, 2), item("milho", 2, 6)], [cultura("soja"), cultura("milho", ciclo_dias_max=145), sem_janela])
    a = analisar_entradas(e)
    achadas = [r for r in a.melhores if any(i.cultura_id == "milheto" for i in r.estrategia.itens)]
    assert achadas and all("ainda não confirmamos a melhor época" in " ".join(r.lacunas) for r in achadas)
    assert "ainda não confirmamos a melhor época" not in " ".join(a.atual.lacunas)
