"""Conta em inglês: nenhuma frase da comparação de rotações pode sair em português (NASA POWER e SRTM falsos)."""
import re

import pytest

from app.main import app
from app.services.integracao import srtm
from app.services.integracao.nasa_power import get_cliente
from app.services.motor.ingles import traduzir
from test_chat import IRECE, ClienteFalso, SrtmFalso

URL = "/fazenda/estrategias"

# Letras e palavras que só aparecem em português (nomes científicos e siglas passam).
_PT = re.compile(
    r"[ãõçáéíóúâêôà]|\b(de|da|do|dos|das|que|não|sem|para|com|sua|seu|nota|contra|rotação|cultura|culturas|chuva|água|"
    r"terra|planta|palha|meses|classe|ano|anos|período|você|máquina|geada|fev|abr|mai|ago|set|out|dez)\b",
    re.IGNORECASE,
)


@pytest.fixture(autouse=True)
def externos():
    app.dependency_overrides[get_cliente] = lambda: ClienteFalso()
    app.dependency_overrides[srtm.get_cliente] = lambda: SrtmFalso()
    yield
    app.dependency_overrides.clear()


def textos(analise: dict) -> list[str]:
    """Todas as frases que o produtor lê (nomes das culturas no calendário ficam fora: vêm do catálogo)."""
    out = list(analise["fontes"])
    for e in analise["eliminadas"]:
        out += [e["nome"], *e["motivos"]]
    for r in [analise["atual"], *analise["melhores"]]:
        out += [r["nome"], *r["por_que"], *r["onde_piora"], *r["lacunas"], *(a["texto"] for a in r["alertas"])]
        for n in r["notas"]:
            out.append(n["explicacao"])
            for ev in n["evidencias"]:
                out += [ev["texto"], ev["fonte"], ev["periodo"] or "", ev["unidade"] or ""]
                if isinstance(ev["valor"], str):
                    out.append(ev["valor"])
    return [t for t in out if t]


def em_ingles(client, auth, respostas: dict) -> dict:
    assert client.patch("/me", headers=auth, json={"idioma": "en"}).status_code == 200
    assert client.put("/fazenda", headers=auth, json={"respostas": respostas}).status_code == 200
    r = client.get(URL, headers=auth)
    assert r.status_code == 200, r.text
    return r.json()


CENARIOS = {
    "irece": IRECE,
    "irece_restricoes": {
        **IRECE,
        "q6_irrigacao": "parte",
        "q25_prioridades": ["agua", "animais", "terra"],
        "q26a_excluidas": [{"cultura_id": "sorgo", "texto_original": "sorgo", "motivo": "mercado"}],
        "q26b_equipamentos": [{"equipamento_id": "trator", "texto_original": "trator"}],
    },
    "cultura_fora_da_base": {
        **IRECE,
        "q8_culturas": [*IRECE["q8_culturas"], {"cultura_id": None, "texto_original": "maxixe", "inicio_mes": 4, "fim_mes": 6}],
    },
    "eua": {
        "q1_quem": "produtor", "q4_animais": "sim", "q6_irrigacao": "nao", "q7_terreno": "leve",
        "q5_local": {"lat": 42.03, "lon": -93.62, "nome": "Story County, IA"},
        "q8_texto": "corn and soybeans",
        "q8_culturas": [{"cultura_id": "milho", "texto_original": "corn", "inicio_mes": 5, "fim_mes": 10}],
    },  # fmt: skip
}


@pytest.mark.parametrize("nome", list(CENARIOS))
def test_nada_em_portugues(client, auth, nome):
    analise = em_ingles(client, auth, CENARIOS[nome])
    sobrou = [t for t in textos(analise) if _PT.search(t.replace("maxixe", ""))]
    assert not sobrou, "\n".join(sobrou)
    assert analise["atual"]["nome"] == "Your current rotation"


def test_em_portugues_nao_muda(client, auth):
    assert client.put("/fazenda", headers=auth, json={"respostas": IRECE}).status_code == 200
    r = client.get(URL, headers=auth).json()
    assert r["atual"]["nome"] == "Sua rotação atual"


@pytest.mark.parametrize(
    ("pt", "en"),
    [
        ("Gasta menos água: nota 0,83 contra 0,66 da sua rotação atual.", "Uses less water: score 0.83 vs. 0.66 for your current rotation."),
        ("Plantar Milheto no período vazio (mar–abr)", "Plant Pearl millet in the empty period (Mar–Apr)"),
        ("Feijão: em 30% dos anos houve geada na fase de floração (set–out) e ela é sensível.",
         "Bean: in 30% of the years there was frost during flowering (Sep–Oct), and it is sensitive."),
        ("Milho: água no limite, a chuva do período (420 mm) cobre 70% do que ela usa (600 mm); faltam cerca de 180 mm; só fecha na parte irrigada.",
         "Corn: water at the limit, the period's rain (420 mm) covers 70% of what it uses (600 mm); about 180 mm short; it only works on the irrigated part."),
        ("12% dos dias de chuva forte caem em meses com planta no campo; terreno forte ondulado.",
         "12% of heavy-rain days fall in months with plants in the field; steep terrain."),
    ],
)  # fmt: skip
def test_frases_soltas(pt, en):
    assert traduzir(pt) == en


@pytest.mark.parametrize(
    "pt",
    [
        # regra 17 (filtro._frio): eliminação, aviso e lacuna
        "Soja: em 40% dos anos houve geada no enchimento dos grãos (mínima abaixo de -2,2 °C) e ela é sensível.",
        "Trigo: em 35% dos anos houve geada na florada (mínima abaixo de -2 °C) e ela é sensível.",
        "Arroz irrigado: frio na florada em 45% dos anos (mínima abaixo de 15 °C por 3 dias seguidos); o dano é parcial, validar localmente.",
        "Pasto: em 60% dos anos houve geada ao longo do ano (mínima abaixo de -3 °C) e ela é sensível.",
        "Soja: não temos a temperatura mínima de cada dia do seu local, então não checamos o frio no enchimento dos grãos.",
        "Milho: não temos a temperatura mínima de cada dia do seu local, então não checamos o frio em todo o ciclo.",
        "Trigo: não temos a temperatura mínima de cada dia do seu local, então não checamos o frio na emergência das plantas.",
        "Aveia: não temos a temperatura mínima de cada dia do seu local, então não checamos o frio no crescimento das plantas.",
        "Pasto: não temos a temperatura mínima de cada dia do seu local, então não checamos o frio ao longo do ano.",
        "Feijão: não temos a temperatura mínima de cada dia do seu local, então não checamos o frio na fase sensível.",
        "Arroz irrigado: o frio na florada foi checado em só 24 dos 30 anos, por falta de temperatura mínima do local; poucos para decidir.",
        "Soja: sem o ciclo na base, não checamos o frio.",
        # regra 2 na cobertura: só aviso
        "Centeio: pode não completar o ciclo antes do manejo; o calor do período dá 800 graus-dia na metade dos anos (2001–2020) e ela precisa de pelo menos 1.200.",
        # A1: cobertura semeada no mês da colheita
        "Plantar Centeio logo depois da colheita (out–abr)",
        "Centeio: a semeadura é em outubro, logo depois da colheita de Milho e Soja; depende da data da sua colheita.",
        "Trevo: a semeadura é em março, logo depois da colheita de Soja; depende da data da sua colheita.",
        # M8: nenhuma cobertura serve para o período sem planta
        "Nenhuma planta de cobertura da nossa base serve para o seu período sem planta (jul–set) na sua região, pela época de semear ou pelo clima. Confirme com seu agrônomo.",
        # renda: frase acrescentada à explicação
        "A rotação tem 2 cultura(s) para vender: Milho, Feijão. Contamos as culturas de venda; preço e produção da sua região ainda não entram nesta nota.",
        # regra 12 (candidatas): lacunas da janela de semeadura
        "Nabo forrageiro: ainda não confirmamos a melhor época para semear esta cobertura. Confirme com seu agrônomo.",
        "Milheto: não conseguimos confirmar depois de qual cultura esta cobertura pode ser semeada. Confirme com seu agrônomo.",
        "Aveia: esta cobertura só serve depois de uma cultura colhida para silagem, e não sabemos se a sua é. Confirme antes de semear.",
    ],
)
def test_frases_da_revisao_de_dados_sem_portugues(pt):
    en = traduzir(pt)
    assert en != pt
    assert not _PT.search(en), en


def test_frases_novas_da_revisao_em_ingles_exatas():
    assert traduzir("Centeio: a semeadura é em outubro, logo depois da colheita de Milho e Soja; depende da data da sua colheita.") == (
        "Rye: sowing is in October, right after the harvest of Corn and Soybean; it depends on your harvest date."
    )
    assert traduzir("Plantar Centeio logo depois da colheita (out–abr)") == "Plant Rye right after the harvest (Oct–Apr)"
    assert traduzir("Milho: não temos a temperatura mínima de cada dia do seu local, então não checamos o frio em todo o ciclo.") == (
        "Corn: we don't have the daily minimum temperature for your location, so we did not check the cold over the whole cycle."
    )
    assert traduzir("Arroz irrigado: o frio na florada foi checado em só 24 dos 30 anos, por falta de temperatura mínima do local; poucos para decidir.") == (
        "Irrigated rice: the cold during flowering was checked in only 24 of 30 years, for lack of the local minimum temperature; too few to decide."
    )
    assert traduzir("Nenhuma planta de cobertura da nossa base serve para o seu período sem planta (jul–set) na sua região, pela época de semear ou pelo clima. Confirme com seu agrônomo.") == (
        "No cover crop in our database fits your period without plants (Jul–Sep) in your region, because of sowing time or climate. Check with your agronomist."
    )


def test_nomes_de_exibicao_em_portugues_viram_o_nome_em_ingles_do_json():
    """O motor usa o nome do culturas.json (sem o "(inglês)" do CSV); a conta em inglês troca esse nome pelo da tela."""
    assert traduzir("Soja: sem Kc nem faixa de água na base, não checamos a água.") == "Soybean: no Kc or water range in our database, so we did not check water."
    assert traduzir("Pasto: sem exigência de graus-dia na base, não checamos o calor do ciclo.").startswith("Pasture: ")
    assert traduzir("Plantar Aveia no período vazio (jul–set)") == "Plant Oat in the empty period (Jul–Sep)"


def test_frio_traduz_limiar_e_dias_seguidos():
    assert traduzir("Arroz irrigado: frio na florada em 45% dos anos (mínima abaixo de 15 °C por 3 dias seguidos); "
                    "o dano é parcial, validar localmente.") == (
        "Irrigated rice: cold during flowering in 45% of the years (low below 15 °C for 3 days in a row); "
        "the damage is partial, check locally."
    )


# --- frases do motor revisado (graus-dia pela mediana, erosão, pragas, água que elimina, janela, frio e calor por dias seguidos)
@pytest.mark.parametrize(
    ("pt", "en"),
    [
        ("Algodão: o calor do período dá 1.148 graus-dia na metade dos anos (2001–2020) e ela precisa de pelo menos 1.400; não fecha o ciclo.",
         "Cotton: the period's heat gives 1,148 degree-days in half of the years (2001–2020) and it needs at least 1,400; it cannot finish its cycle."),
        ("Soja: no limite térmico, validar localmente; o calor do período dá 1.350 graus-dia na metade dos anos (2001–2020) e ela precisa de pelo menos 1.500.",
         "Soybean: at its heat limit, check locally; the period's heat gives 1,350 degree-days in half of the years (2001–2020) and it needs at least 1,500."),
        ("Milho: em ano frio pode não completar o ciclo; em 1 a cada 10 anos (2001–2020) o calor do período fica em 1.215 graus-dia, e ela precisa de pelo menos 1.300.",
         "Corn: in a cold year it may not finish its cycle; in 1 of every 10 years (2001–2020) the period's heat is only 1,215 degree-days, and it needs at least 1,300."),
        ("Milho: sem anos suficientes de clima para checar o calor do ciclo.", "Corn: not enough years of climate data to check the season's heat."),
        ("Algodão: a chuva do período (104 mm) cobre só 22% da água que a cultura usa (474 mm); sem irrigação não fecha.",
         "Cotton: the period's rain (104 mm) covers only 22% of the water the crop uses (474 mm); without irrigation it cannot finish."),
        ("Trigo: em 40% dos anos (1991–2020) a mínima ficou abaixo de 1 °C na florada (dez a jan); o frio nessa fase tira produção.",
         "Wheat: in 40% of the years (1991–2020) the low fell below 1 °C at flowering (Dec to Jan); cold in this stage cuts yield."),
        ("Soja: em 40% dos anos (1991–2020) a mínima ficou abaixo de -2,2 °C por 3 dias seguidos no enchimento dos grãos (nov a fev); a geada nessa fase tira produção.",
         "Soybean: in 40% of the years (1991–2020) the low fell below -2.2 °C for 3 days in a row during grain fill (Nov to Feb); frost in this stage cuts yield."),
        ("Milho: em 40% dos anos (1991–2020) a temperatura passou de 33 °C por 3 dias seguidos na floração (nov a jan); o calor nessa fase pode reduzir a produção.",
         "Corn: in 40% of the years (1991–2020) the temperature went above 33 °C for 3 days in a row at flowering (Nov to Jan); heat in this stage can cut yield."),
        ("2 de 3 trocas de cultura mudam de família de planta.", "2 of 3 crop changes switch to a different plant family."),
        ("12% dos dias de chuva forte caem em meses com planta no campo; terreno suave ondulado, declividade de 5,5% medida por satélite (SRTM).",
         "12% of heavy-rain days fall in months with plants in the field; gently rolling terrain, slope of 5.5% measured by satellite (SRTM)."),
        ("Palhada de Milho: palhada média, de 2,1 a 9,8 t/ha conforme a data de manejo (depende da época)",
         "Straw of Corn: medium, 2.1 to 9.8 t/ha depending on the management date (depends on the season)"),
        ("Base de culturas do Field Shift (números para GA, arranjo sudeste)", "Field Shift crop database (figures for GA, regional arrangement sudeste)"),
        ("Milheto: a época de semeadura ainda não foi confirmada para a sua região.", "Pearl millet: the sowing time has not been confirmed for your region yet."),
    ],
)  # fmt: skip
def test_frases_do_motor_revisado_em_ingles(pt, en):
    assert traduzir(pt) == en
    assert not _PT.search(en), en


def test_textos_do_catalogo_ficam_fora_das_lacunas_em_ingles():
    from app.services.motor.catalogo import catalogo_do_pais
    from app.services.motor.ingles import lacunas_em_ingles

    crot = catalogo_do_pais("BR")["crotalaria"]
    lacunas = [f"{crot.nome}: {crot.lacuna_informacao}", f"{crot.nome}: {crot.risco_revisao_local}", "Milho: sem anos suficientes de clima para checar o calor do ciclo."]
    assert lacunas_em_ingles(lacunas) == ["Corn: not enough years of climate data to check the season's heat."]
