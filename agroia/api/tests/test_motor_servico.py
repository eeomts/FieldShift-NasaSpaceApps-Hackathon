"""Motor completo sobre fazendas e climas sintéticos: entradas, erros de negócio, atual, melhores e eliminadas."""
from dataclasses import replace

import pytest

from app.core.erros import ErroDeNegocio
from app.models import CalendarioItem, Fazenda
from app.services.clima.agregacao import LinhaMensal
from app.services.motor.entradas import ClimaDoServico, clima_de_linhas, montar_entradas
from app.services.motor.motor_service import analisar_entradas
from motor_helpers import PLANO, clima, cultura, entradas, item

# Fazenda de Rio Verde (GO): dentro da malha do IBGE
LAT, LON = -17.644301, -51.080503


class ClimaFalso:
    def __init__(self, c):
        self.c, self.chamadas = c, []

    def do_local(self, lat, lon):
        self.chamadas.append((lat, lon))
        return self.c


class RelevoFalso:
    def __init__(self, r=PLANO):
        self.r = r

    def declividade_da_fazenda(self, f):
        return self.r


def fazenda(calendario=(("soja", 10, 2), ("milho", 2, 6)), **campos) -> Fazenda:
    f = Fazenda(lat=LAT, lon=LON, pais="BR", irrigacao="nao", prioridades=[], culturas_excluidas=[], equipamentos=[])
    f.calendario = [CalendarioItem(ordem=i, cultura_id=c, texto_original=c or "outra", inicio_mes=a, fim_mes=b, perene=False) for i, (c, a, b) in enumerate(calendario)]
    for k, v in campos.items():
        setattr(f, k, v)
    return f


def montar(f, catalogo=None, c=None):
    catalogo = catalogo if catalogo is not None else {x.id: x for x in CULTURAS}
    return montar_entradas(f, ClimaFalso(c or clima()), RelevoFalso(), catalogo_por_pais=lambda p: catalogo, equipamentos={})


CULTURAS = [
    cultura("soja", tipos=("comercial", "fixadora_n"), fixa_nitrogenio=True, familia_botanica="Fabaceae", aporte_biomassa="medio"),
    cultura("milho", ciclo_dias_max=145, aporte_biomassa="alto"),
    cultura("sorgo", tipos=("comercial", "tolerante_seca"), ciclo_dias_min=90, valor_forrageiro="medio"),
    cultura("milheto", tipos=("cobertura", "tolerante_seca"), ciclo_dias_min=45, valor_forrageiro="alto", aporte_biomassa="alto", confianca_parametros="baixa"),
    cultura("crotalaria", tipos=("cobertura", "fixadora_n"), fixa_nitrogenio=True, familia_botanica="Fabaceae", ciclo_dias_min=56, aporte_biomassa="alto", confianca_parametros="media"),
]


# --- erros de negócio
def test_sem_local_pede_para_marcar_o_local():
    with pytest.raises(ErroDeNegocio) as e:
        montar(fazenda(lat=None, lon=None, pais=None))
    assert e.value.status_code == 422 and e.value.mensagem == "Marque o local da fazenda para comparar rotações."


def test_pais_fora_de_br_e_us_nao_gera_analise():
    with pytest.raises(ErroDeNegocio) as e:
        montar(fazenda(lat=48.85, lon=2.35, pais=None))  # Paris
    assert "Brasil" in e.value.mensagem


def test_catalogo_vazio_do_pais_avisa_que_nao_tem_as_culturas():
    with pytest.raises(ErroDeNegocio) as e:
        montar(fazenda(pais="US"), catalogo={})
    assert e.value.mensagem == "Ainda não temos as culturas desta região na base."


def test_sem_calendario_pede_o_que_o_produtor_planta():
    with pytest.raises(ErroDeNegocio) as e:
        montar(fazenda(calendario=()))
    assert "planta" in e.value.mensagem


def test_pais_nulo_com_local_dentro_do_brasil_e_descoberto_pela_malha():
    e = montar(fazenda(pais=None))
    assert e.pais == "BR"


# --- entradas montadas da fazenda
def test_entradas_lidas_da_fazenda():
    f = fazenda(
        prioridades=["agua", "terra"], irrigacao="parte",
        culturas_excluidas=[{"cultura_id": "sorgo", "texto_original": "sorgo"}, {"cultura_id": None, "texto_original": "x"}],
        equipamentos=[{"equipamento_id": "manual", "texto_original": "m"}, {"equipamento_id": None, "texto_original": "?"}],
    )
    c = ClimaFalso(clima())
    e = montar_entradas(f, c, RelevoFalso(), catalogo_por_pais=lambda p: {x.id: x for x in CULTURAS})
    assert c.chamadas == [(LAT, LON)] and e.meses_vazios == [7, 8, 9] and e.irrigacao == "parte"
    assert e.excluidas == {"sorgo"} and e.equipamentos == {"manual"} and e.prioridades == ["agua", "terra"]
    assert [(i.cultura_id, i.inicio_mes, i.fim_mes) for i in e.atual] == [("soja", 10, 2), ("milho", 2, 6)]


def test_produtor_sem_equipamento_reconhecido_conta_como_nao_respondeu():
    e = montar(fazenda(equipamentos=[{"equipamento_id": None, "texto_original": "?"}]))
    assert e.equipamentos is None
    assert montar(fazenda(equipamentos=[])).equipamentos is None


def test_clima_de_linhas_media_gd_geada_por_ano_e_ignora_fora_da_base():
    def linha(ano, mes, gd, geada, chuva=100.0):
        return LinhaMensal(ano, mes, chuva, 50.0, 20.0, 28.0, 14.0, 35.0, 5.0, geada, 0, 2, 3, 30, gd)

    todos = [{str(tb): float(max(0, 20 - tb)) for tb in range(21)}, {str(tb): float(max(0, 24 - tb)) for tb in range(21)}]
    linhas = [linha(1991, 1, todos[0], 0), linha(1992, 1, todos[1], 2), linha(1993, 1, {}, None), linha(2021, 1, todos[1], 9, chuva=999.0)]
    c = clima_de_linhas(linhas, "fonte", "1991–2020")
    assert c.gd_por_tb_medio[1]["10"] == 12.0 and 2 not in c.gd_por_tb_medio  # média de 10 e 14; {} fica fora; mês sem dado fica ausente
    assert c.geada_por_ano == {1991: {1: 0}, 1992: {1: 2}, 1993: {1: None}}  # 2021 está fora de 1991–2020
    assert c.chuva_mm[1] == 100.0 and c.chuva_mm[2] is None and c.et0_mm[1] == 50.0 and c.dias_chuva_forte[1] == 2.0


def test_clima_do_servico_monta_do_servico_de_clima():
    class ServicoFalso:
        def obter(self, lat, lon):
            return "celula"

        def climatologia(self, celula):
            class C:
                fonte, periodo = "NASA POWER, média", "1991–2020"

            return C()

        def linhas(self, celula):
            return []

    c = ClimaDoServico(ServicoFalso()).do_local(LAT, LON)
    assert c.fonte == "NASA POWER, média" and c.gd_por_tb_medio == {} and c.chuva_mm[1] is None


# --- análise
def analisar(f=None, **mudancas):
    e = montar(f or fazenda())
    for k, v in mudancas.items():
        setattr(e, k, v)
    return analisar_entradas(e)


def test_analise_traz_atual_ate_duas_melhores_eliminadas_pesos_e_fontes():
    a = analisar(fazenda(prioridades=["terra", "erosao", "animais"]))
    assert a.pais == "BR" and a.atual.estrategia.origem == "atual" and a.atual.estrategia.id == "atual"
    assert 1 <= len(a.melhores) <= 2
    assert sum(a.pesos.values()) == pytest.approx(1) and a.pesos["terra"] == pytest.approx(0.425)
    assert any("NASA POWER" in f for f in a.fontes) and any("Calendário" in f for f in a.fontes)
    assert a.gerado_em is not None


def test_melhores_sao_diferentes_da_atual_e_entre_si_e_ordenadas():
    a = analisar()
    chaves = [frozenset((i.cultura_id, i.inicio_mes, i.fim_mes) for i in r.estrategia.itens) for r in a.melhores]
    atual = frozenset((i.cultura_id, i.inicio_mes, i.fim_mes) for i in a.atual.estrategia.itens)
    assert len(set(chaves)) == len(chaves) and atual not in chaves
    assert [r.nota_final for r in a.melhores] == sorted((r.nota_final for r in a.melhores), reverse=True)


def test_por_que_so_aparece_para_criterio_que_ganha_da_atual_por_0_1_ou_mais():
    a = analisar()
    assert a.atual.por_que == []
    for r in a.melhores:
        ganhos = [c for c, n in r.notas.items() if n.nota is not None and a.atual.notas[c].nota is not None and n.nota - a.atual.notas[c].nota >= 0.1 - 1e-9]
        assert len(r.por_que) == min(3, len(ganhos))


def test_atual_nunca_e_eliminada_mesmo_com_tudo_errado():
    cl = clima(chuva=1.0, tmed=5.0, geada={m: 30 for m in range(1, 13)})
    ruins = [cultura("soja", sensivel_geada=True, graus_dia_ciclo_min=9000), cultura("milho", sensivel_geada=True, graus_dia_ciclo_min=9000)]
    f = fazenda(culturas_excluidas=[{"cultura_id": "soja", "texto_original": "soja"}])
    a = analisar_entradas(montar(f, {c.id: c for c in ruins}, cl))
    assert a.atual.estrategia.id == "atual" and a.eliminadas == [] and a.melhores == []
    assert {x.codigo for x in a.atual.alertas} >= {"graus_dia", "agua_no_limite", "geada"}


def test_candidata_so_e_avaliada_pelo_que_tem_de_novo():
    # a soja da atual está no limite térmico e com geada; a candidata que a mantém não é eliminada por ela
    problematicas = [cultura("soja", sensivel_geada=True, graus_dia_ciclo_min=9000, tipos=("comercial", "fixadora_n"), fixa_nitrogenio=True), *CULTURAS[1:]]
    a = analisar_entradas(montar(fazenda(), {c.id: c for c in problematicas}, clima(geada={11: 30})))
    assert a.melhores and all(any(i.cultura_id == "soja" for i in r.estrategia.itens) for r in a.melhores)


def test_eliminadas_trazem_o_motivo_em_portugues():
    a = analisar(fazenda(culturas_excluidas=[{"cultura_id": "sorgo", "texto_original": "sorgo"}]))
    sorgo = [x for x in a.eliminadas if "Sorgo" in x.estrategia.nome]
    assert sorgo and all("Você disse que não planta Sorgo." in x.motivos for x in sorgo)
    assert all(x.motivos for x in a.eliminadas)


def test_filtro_de_geada_elimina_candidata_de_janela_com_motivo():
    sensiveis = [*CULTURAS[:2], cultura("sorgo", tipos=("comercial", "tolerante_seca"), ciclo_dias_min=90, sensivel_geada=True), *CULTURAS[3:]]
    a = analisar_entradas(montar(fazenda(), {c.id: c for c in sensiveis}, clima(geada={7: 15, 8: 15, 9: 15})))
    janela = next(x for x in a.eliminadas if x.estrategia.id == "janela:sorgo")
    assert any("geada" in m for m in janela.motivos)


def test_cultura_fora_do_catalogo_na_atual_vira_lacuna_sem_quebrar():
    a = analisar(fazenda(calendario=(("soja", 10, 2), (None, 2, 6))))
    assert any("Sem dados suficientes de" in l for l in a.atual.lacunas)
    assert a.atual.nota_final is not None


def test_confianca_da_estrategia_e_a_menor_das_culturas():
    a = analisar()
    assert a.atual.confianca == "alta"
    com_milheto = [r for r in a.melhores if any(i.cultura_id == "milheto" for i in r.estrategia.itens)]
    assert all(r.confianca == "baixa" for r in com_milheto)


def test_sem_prioridade_todos_os_pesos_valem_um_sexto():
    a = analisar()
    assert all(v == pytest.approx(1 / 6) for v in a.pesos.values())


def test_criterio_sem_dado_na_atual_sai_dos_pesos_efetivos():
    cs = {c.id: c for c in CULTURAS}
    for k in ("soja", "milho"):
        cs[k] = replace(cs[k], valor_forrageiro=None)
    a = analisar_entradas(montar(fazenda(prioridades=["animais"]), cs))
    assert a.atual.notas["animais"].nota is None and "animais" not in a.atual.pesos
    assert sum(a.atual.pesos.values()) == pytest.approx(1) and a.pesos["animais"] == pytest.approx(0.75)


def test_falta_de_agua_nao_elimina_candidata_e_vira_aviso_sem_irrigacao():
    seco = clima(chuva=1.0)
    sem = analisar_entradas(montar(fazenda(irrigacao="nao"), c=seco))
    com = analisar_entradas(montar(fazenda(irrigacao="sim"), c=seco))
    assert not any("água" in m for x in sem.eliminadas for m in x.motivos)
    assert any(a.codigo == "agua_no_limite" for r in [sem.atual, *sem.melhores] for a in r.alertas)
    assert not any(a.codigo == "agua_no_limite" for r in [com.atual, *com.melhores] for a in r.alertas)


def test_analise_com_a_entrada_direta_dos_helpers():
    e = entradas([item("soja", 10, 2), item("milho", 2, 6)], CULTURAS, prioridades=["renda"])
    a = analisar_entradas(e)
    assert a.atual.notas["renda"].nota == 0.8 and a.pesos["renda"] == pytest.approx(0.75)


def test_atual_e_a_melhor_quando_nenhuma_das_melhores_a_supera():
    # ano todo coberto, palha alta no milho: a única troca possível (milho por sorgo) perde em terra
    cs = {
        "soja": CULTURAS[0],
        "milho": CULTURAS[1],
        "sorgo": cultura("sorgo", tipos=("comercial", "tolerante_seca"), aporte_biomassa="baixo"),
    }
    a = analisar_entradas(montar(fazenda(calendario=(("soja", 10, 3), ("milho", 4, 9))), cs))
    assert a.melhores and all(r.nota_final < a.atual.nota_final for r in a.melhores)
    assert a.atual_e_a_melhor is True
    assert any("Cuida menos da terra" in f for f in a.melhores[0].onde_piora)  # e a tela pode dizer onde piora


def test_atual_nao_e_a_melhor_quando_uma_candidata_a_supera():
    # a atual sem cobertura nem leguminosa: incluir cultura no vazio melhora a nota
    cs = {c.id: c for c in CULTURAS}
    a = analisar_entradas(montar(fazenda(calendario=(("milho", 10, 2),)), cs))
    assert a.melhores and a.melhores[0].nota_final > a.atual.nota_final and a.atual_e_a_melhor is False


def test_onde_piora_nas_melhores_e_vazio_na_atual():
    a = analisar()
    assert a.atual.onde_piora == []
    for r in a.melhores:
        perdas = [c for c, n in r.notas.items() if n.nota is not None and a.atual.notas[c].nota is not None and a.atual.notas[c].nota - n.nota >= 0.1 - 1e-9]
        assert len(r.onde_piora) == min(3, len(perdas))
        assert all("contra" in f for f in r.onde_piora)
