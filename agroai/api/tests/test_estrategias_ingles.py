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
        "Centeio: o calor do período dá 800 graus-dia e ela precisa de pelo menos 1.200; pode não completar o ciclo antes do manejo.",
        # A1: cobertura semeada no mês da colheita
        "Plantar Centeio logo depois da colheita (out–abr)",
        "Centeio: a semeadura é em outubro, logo depois da colheita de Milho e Soja; depende da data da sua colheita.",
        "Trevo: a semeadura é em março, logo depois da colheita de Soja; depende da data da sua colheita.",
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
