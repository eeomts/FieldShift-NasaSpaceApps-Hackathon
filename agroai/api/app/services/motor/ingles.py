"""Tradução para inglês das frases que o motor monta em português (nomes, por que, alertas, lacunas, evidências).

O motor continua gerando português (e os testes dele conferem esse texto). A tradução acontece só na saída da rota,
quando a conta está em inglês. Ordem: regras de frase (com os nomes ainda em português), depois os nomes de culturas
e máquinas, os meses entre parênteses e a vírgula decimal. `test_estrategias_ingles.py` falha se sobrar português.
"""
import re
from collections.abc import Callable
from functools import lru_cache

from app.services import catalogo as base
from app.services.motor import catalogo as catalogo_motor
from app.services.motor.parametros import MESES_POR_EXTENSO

_MESES_PT = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
_MESES_EN = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
_MES = "|".join(_MESES_PT)
_MES_POR_EXTENSO_EN = dict(zip(
    MESES_POR_EXTENSO,
    ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"),
    strict=True,
))  # fmt: skip

_CLASSES = {
    "baixo": "low", "baixa": "low", "medio": "medium", "media": "medium", "médio": "medium", "média": "medium",
    "alto": "high", "alta": "high", "nenhum": "none", "sim": "yes", "não": "no", "nao": "no",
}  # fmt: skip
_ERODIBILIDADE = {"baixa": "low", "média": "medium", "alta": "high"}
_RELEVO = {
    "plano": "flat", "suave ondulado": "gently rolling", "ondulado": "rolling",
    "forte ondulado": "steep", "montanhoso": "mountainous",
}  # fmt: skip
_ETAPA = {"plantio": "planting", "colheita": "harvest"}
_UNIDADES = {"meses": "months", "classe": "class", "culturas": "crops"}

_FRASES = {
    # por que
    "Gasta menos água": "Uses less water",
    "Cuida melhor da terra (cobertura, palha e nitrogênio)": "Takes better care of the soil (cover, straw and nitrogen)",
    "Protege mais o solo da erosão": "Protects the soil better from erosion",
    "Alterna mais as famílias de plantas, o que ajuda contra pragas": "Rotates more plant families, which helps against pests",
    "Tem mais culturas para vender": "Has more crops to sell",
    "Dá mais comida para os animais": "Gives more feed for the animals",
    # onde piora
    "Usa mais água": "Uses more water",
    "Cuida menos da terra": "Takes less care of the soil",
    "Protege menos o solo da erosão": "Protects the soil less from erosion",
    "Alterna menos as famílias de plantas": "Rotates fewer plant families",
    "Tem menos culturas para vender": "Has fewer crops to sell",
    "Dá menos comida para os animais": "Gives less feed for the animals",
}

_Regra = tuple[re.Pattern, str | Callable[[re.Match], str]]

_MILHAR = "\x00"  # vírgula de milhar em inglês: só vira "," no fim, depois da troca da vírgula decimal
_FASE_FRIO_CALOR = {
    "na emergência das plantas": "during emergence", "no crescimento das plantas": "during plant growth",
    "na florada": "at flowering", "na floração": "at flowering", "no enchimento dos grãos": "during grain fill",
    "em todo o ciclo": "over the whole cycle", "na fase sensível": "in the sensitive stage", "ao longo do ano": "through the year",
}  # fmt: skip


def _milhar(numero: str) -> str:
    """'1.148' (milhar em português) vira '1,148'; número sem milhar passa igual."""
    return numero.replace(".", _MILHAR) if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", numero) else numero


def _meses_a(intervalo: str | None) -> str:
    """'nov a jan' vira ' (Nov to Jan)'."""
    if not intervalo:
        return ""
    for pt, en in zip(_MESES_PT, _MESES_EN, strict=True):
        intervalo = re.sub(rf"(?<![a-z]){pt}(?![a-z])", en, intervalo)
    return f" ({intervalo.replace(' a ', ' to ')})"


def _frio_ou_calor(m: re.Match) -> str:
    """Frio (regra 17) e calor por dias seguidos: 'em P% dos anos (1991–2020) a mínima ficou abaixo de L °C ...'."""
    nome, pct, periodo = m.group(1), m.group(2), m.group(3)
    fase = _FASE_FRIO_CALOR[m.group("fase")] + _meses_a(m.group("meses"))
    if "limiar" in m.groupdict() and m.groupdict().get("limiar") is not None:
        dias = f" for {m.group('dias')} days in a row" if m.group("dias") else ""
        dano = "frost" if m.group("dano") == "a geada" else "cold"
        return f"{nome}: in {pct} of the years ({periodo}) the low fell below {m.group('limiar')} °C{dias} {fase}; {dano} in this stage cuts yield."
    return f"{nome}: in {pct} of the years ({periodo}) the temperature went above {m.group('maxima')} °C for {m.group('dias_calor')} days in a row {fase}; heat in this stage can cut yield."

# Regra 17 (frio por fase, filtro._frio): termo, onde (parametros.FASES_FRIO_TEXTO, FASE_FRIO_PADRAO e FASE_FRIO_PERENE) e o limiar.
_TERMO_FRIO = {"geada": "frost", "frio": "cold"}
_ONDE_FRIO = {
    "na emergência das plantas": "during emergence", "no crescimento das plantas": "during plant growth",
    "na florada": "during flowering", "no enchimento dos grãos": "during grain fill",
    "em todo o ciclo": "over the whole cycle", "ao longo do ano": "through the year",
    "na fase sensível": "in the sensitive stage",
}  # fmt: skip
_QUANTO_FRIO = re.compile(r"^mínima abaixo de (\S+) °C(?: por (\d+) dias seguidos)?$")


def _quanto_frio(texto: str) -> str:
    m = _QUANTO_FRIO.match(texto)
    if not m:
        return texto
    return f"low below {m.group(1)} °C" + (f" for {m.group(2)} days in a row" if m.group(2) else "")


def _classe(m: re.Match, g: int = 1) -> str:
    v = m.group(g)
    return _CLASSES.get(v, v)


# Frases inteiras ou trechos, na ordem em que são aplicadas. Nomes de cultura ficam em (.+?) e são trocados depois.
_REGRAS: list[_Regra] = [
    (re.compile(p), r)
    for p, r in [
        # nomes das estratégias
        (r"^Sua rotação atual$", "Your current rotation"),
        (r"^Plantar (.+?) no período vazio \((.+?)\)$", r"Plant \1 in the empty period (\2)"),
        (r"^Plantar (.+?) logo depois da colheita \((.+?)\)$", r"Plant \1 right after the harvest (\2)"),
        (r"^Trocar (.+?) por (.+)$", r"Swap \1 for \2"),
        # por que / onde piora
        (r"^(.+?): nota (\S+) contra (\S+) da sua rotação atual\.$", lambda m: f"{_FRASES.get(m.group(1), m.group(1))}: score {m.group(2)} vs. {m.group(3)} for your current rotation."),
        # confiança
        (r"^(.+?): confiança dos parâmetros não informada; tratada como baixa\.$", r"\1: parameter confidence not given; treated as low."),
        (r"^Nenhuma cultura da rotação está na base: confiança baixa\.$", "No crop in this rotation is in our database: low confidence."),
        # filtro: máquinas
        (r"^Sem lista de máquinas para (.+?): não checamos seus equipamentos\.$", r"No machinery list for \1: we did not check your equipment."),
        (r"^Sem lista de máquinas de (\w+) para (.+?): não checamos seus equipamentos\.$", lambda m: f"No {_ETAPA.get(m.group(1), m.group(1))} machinery list for {m.group(2)}: we did not check your equipment."),
        (r"^(.+?): falta máquina para o (\w+); serve (.+)\.$", lambda m: f"{m.group(1)}: missing machinery for {_ETAPA.get(m.group(2), m.group(2))}; any of these works: {m.group(3).replace(' ou ', ', ')}."),
        # filtro: região
        (r"^(.+?): não sabemos o estado da fazenda, então não checamos se a base dela vale para sua região\.$", r"\1: we don't know the farm's state, so we did not check whether its data applies to your region."),
        (r"^(.+?): sem dado para sua região \((.+?)\); a base dela vale para (.+)\.$", r"\1: no data for your region (\2); its data applies to \3."),
        # filtro: calor
        (r"^(.+?): sem exigência de graus-dia na base, não checamos o calor do ciclo\.$", r"\1: no degree-day requirement in our database, so we did not check the season's heat."),
        (r"^(.+?): sem graus-dia do clima do local para o período, não checamos o calor do ciclo\.$", r"\1: no local degree-days for this period, so we did not check the season's heat."),
        (r"o calor do período dá (\S+) graus-dia na metade dos anos \((\S+)\) e ela precisa de pelo menos (\S+?)(?=;|\.$|$)",
         lambda m: f"the period's heat gives {_milhar(m.group(1))} degree-days in half of the years ({m.group(2)}) and it needs at least {_milhar(m.group(3))}"),
        (r"; não fecha o ciclo\.$", "; it cannot finish its cycle."),
        (r"^(.+?): no limite térmico, validar localmente; ", r"\1: at its heat limit, check locally; "),
        (r"^(.+?): pode não completar o ciclo antes do manejo; ", r"\1: may not finish its cycle before termination; "),
        (r"^(.+?): em ano frio pode não completar o ciclo; em 1 a cada 10 anos \((\S+)\) o calor do período fica em (\S+) graus-dia, e ela precisa de pelo menos (\S+)\.$",
         lambda m: f"{m.group(1)}: in a cold year it may not finish its cycle; in 1 of every 10 years ({m.group(2)}) the period's heat is only {_milhar(m.group(3))} degree-days, and it needs at least {_milhar(m.group(4))}."),
        (r"^(.+?): sem anos suficientes de clima para checar o calor do ciclo\.$", r"\1: not enough years of climate data to check the season's heat."),
        (r"^(.+?): sem anos suficientes de clima para checar o risco de calor\.$", r"\1: not enough years of climate data to check heat risk."),
        (r"^(.+?): sem dados diários de temperatura máxima do local, não checamos o risco de calor\.$", r"\1: no local daily maximum temperature data, so we did not check heat risk."),
        # filtro: frio por cultura (regra 17) e calor por dias seguidos (regra 11)
        (r"^(.+?): em (\S+) dos anos \((\S+)\) a mínima ficou abaixo de (?P<limiar>\S+) °C(?: por (?P<dias>\d+) dias seguidos)? "
         r"(?P<fase>na emergência das plantas|no crescimento das plantas|na florada|no enchimento dos grãos|em todo o ciclo|na fase sensível|ao longo do ano)(?: \((?P<meses>.+?)\))?; "
         r"(?P<dano>a geada|o frio) nessa fase tira produção\.$", _frio_ou_calor),
        (r"^(.+?): em (\S+) dos anos \((\S+)\) a temperatura passou de (?P<maxima>\S+) °C por (?P<dias_calor>\d+) dias seguidos "
         r"(?P<fase>na floração|ao longo do ano)(?: \((?P<meses>.+?)\))?; o calor nessa fase pode reduzir a produção\.$", _frio_ou_calor),
        # filtro: água
        (r"^(.+?): sem chuva do clima do local para o período, não checamos a água\.$", r"\1: no local rainfall for this period, so we did not check water."),
        (r"^(.+?): sem Kc nem faixa de água na base, não checamos a água\.$", r"\1: no Kc or water range in our database, so we did not check water."),
        (r"^(.+?): água no limite, ", r"\1: water at the limit, "),
        (r"^(.+?): a chuva do período \((\S+) mm\) cobre só (\S+) da água que a cultura (usa|precisa) \((\S+) mm\); sem irrigação não fecha\.$",
         lambda m: f"{m.group(1)}: the period's rain ({m.group(2)} mm) covers only {m.group(3)} of the water the crop {'uses' if m.group(4) == 'usa' else 'needs'} ({m.group(5)} mm); without irrigation it cannot finish."),
        (r"a chuva do período \((\S+) mm\) cobre (\S+) do que ela usa \((\S+) mm\)", r"the period's rain (\1 mm) covers \2 of what it uses (\3 mm)"),
        (r"a chuva do período \((\S+) mm\) fica abaixo do que ela precisa \((\S+) a (\S+) mm\)", r"the period's rain (\1 mm) is below what it needs (\2 to \3 mm)"),
        (r"; faltam cerca de (\S+) mm", r"; about \1 mm short"),
        (r"; só fecha na parte irrigada", "; it only works on the irrigated part"),
        # filtro: geada e restrições
        (r"^(.+?): sem dados de geada do local para a floração, não checamos o risco de geada\.$", r"\1: no local frost data for flowering, so we did not check frost risk."),
        (r"^(.+?): em (\S+) dos anos houve geada na fase de floração \((.+?)\) e ela é sensível\.$", r"\1: in \2 of the years there was frost during flowering (\3), and it is sensitive."),
        (r"^(.+?): em (\S+) dos anos houve (geada|frio) (.+?) \((mínima abaixo de .+?)\) e ela é sensível\.$",
         lambda m: f"{m.group(1)}: in {m.group(2)} of the years there was {_TERMO_FRIO[m.group(3)]} {_ONDE_FRIO.get(m.group(4), m.group(4))} "
                   f"({_quanto_frio(m.group(5))}), and it is sensitive."),
        (r"^(.+?): (geada|frio) (.+?) em (\S+) dos anos \((mínima abaixo de .+?)\); o dano é parcial, validar localmente\.$",
         lambda m: f"{m.group(1)}: {_TERMO_FRIO[m.group(2)]} {_ONDE_FRIO.get(m.group(3), m.group(3))} in {m.group(4)} of the years "
                   f"({_quanto_frio(m.group(5))}); the damage is partial, check locally."),
        (r"^(.+?): não temos a temperatura mínima de cada dia do seu local, então não checamos o frio (.+?)\.$",
         lambda m: f"{m.group(1)}: we don't have the daily minimum temperature for your location, so we did not check the cold {_ONDE_FRIO.get(m.group(2), m.group(2))}."),
        (r"^(.+?): o frio (.+?) foi checado em só (\d+) dos (\d+) anos, por falta de temperatura mínima do local; poucos para decidir\.$",
         lambda m: f"{m.group(1)}: the cold {_ONDE_FRIO.get(m.group(2), m.group(2))} was checked in only {m.group(3)} of {m.group(4)} years, "
                   "for lack of the local minimum temperature; too few to decide."),
        (r"^(.+?): sem o ciclo na base, não checamos o frio\.$", r"\1: no cycle in our database, so we did not check the cold."),
        (r"^Você disse que não planta (.+)\.$", r"You said you don't grow \1."),
        (r"^(.+?) só entra com irrigação ou várzea e você não marcou irrigação\.$", r"\1 only works with irrigation or flooded lowland, and you did not mark irrigation."),
        (r"^(.+?): sem os meses de plantio, não checamos clima, água e geada\.$", r"\1: without the planting months, we did not check climate, water and frost."),
        # critérios: água
        (r"^Sem dados suficientes de chuva do local\.$", "Not enough local rainfall data."),
        (r"^Chuva do local incompleta: sem nota de água\.$", "Local rainfall is incomplete: no water score."),
        (r"^(.+?): sem Kc ou ET0 para calcular a água\.$", r"\1: no Kc or ET0 to calculate water."),
        (r"^Sem dados suficientes para calcular a água da rotação\.$", "Not enough data to calculate this rotation's water use."),
        (r"A rotação usa cerca de (\S+) mm de água por ano e a chuva média do local é de (\S+) mm\.", r"The rotation uses about \1 mm of water a year, and the local average rainfall is \2 mm."),
        (r" Como você irriga, a irrigação cobre a falta de chuva\.", " Since you irrigate, irrigation covers the rain shortfall."),
        (r" A irrigação cobre só parte do campo\.", " Irrigation covers only part of the field."),
        (r" Os dados de água de (.+?) têm confiança baixa: a estimativa pode errar\.", r" The water data for \1 has low confidence: the estimate may be off."),
        (r"^Água que as culturas usam no ano \(Kc x ET0\)$", "Water the crops use in a year (Kc x ET0)"),
        (r"^Chuva do ano$", "Rain in a year"),
        (r"^Água que (.+?) usa no ciclo \(faixa da literatura, confiança baixa\)$", r"Water \1 uses per cycle (range from the literature, low confidence)"),
        # critérios: terra
        (r"^(.+?): sem a classe de palha na base\.$", r"\1: no straw class in our database."),
        (r"^(.+?): classe de palha desconhecida \((.+?)\)\.$", r"\1: unknown straw class (\2)."),
        (r"^Sem dados suficientes de palha das culturas\.$", "Not enough straw data for the crops."),
        (r"^Algumas culturas sem informação se fixam nitrogênio\.$", "Some crops have no information on nitrogen fixing."),
        (r"O campo tem planta em (\d+) dos 12 meses, a maior palhada é a de (.+?) \(palhada (\w+), de (\S+) a (\S+) t/ha conforme a data de manejo\) e a rotação ",
         lambda m: f"The field has plants in {m.group(1)} of the 12 months, the most straw comes from {m.group(2)} ({_classe(m, 3)} straw, {m.group(4)} to {m.group(5)} t/ha depending on the management date), and the rotation "),
        (r"^Palhada de (.+?): palhada (\w+), de (\S+) a (\S+) t/ha conforme a data de manejo \(depende da época\)$",
         lambda m: f"Straw of {m.group(1)}: {_classe(m, 2)}, {m.group(3)} to {m.group(4)} t/ha depending on the management date (depends on the season)"),
        (r"O campo tem planta em (\d+) dos 12 meses, a maior palhada é a de (.+?) \(classe (\w+)\) e a rotação ",
         lambda m: f"The field has plants in {m.group(1)} of the 12 months, the most straw comes from {m.group(2)} ({_classe(m, 3)} class), and the rotation "),
        (r"tem (.+?), que fixa nitrogênio\.$", r"has \1, which fixes nitrogen."),
        (r"não tem planta que fixa nitrogênio\.$", "has no nitrogen-fixing plant."),
        (r"^Meses do ano com planta no campo$", "Months of the year with plants in the field"),
        (r"^Palha que fica no campo \(maior da rotação: (.+?)\)$", r"Straw left in the field (most in the rotation: \1)"),
        (r"^Planta que fixa nitrogênio na rotação$", "Nitrogen-fixing plant in the rotation"),
        # critérios: erosão
        (r"^Sem dados suficientes de chuva forte do local\.$", "Not enough local heavy-rain data."),
        (r"^Chuva forte do local sem dados: sem nota de erosão\.$", "No local heavy-rain data: no erosion score."),
        (r"^Sem declividade do terreno: usamos um valor médio para a erosão\.$", "No slope data: we used an average value for erosion."),
        (r"^Classe de declive desconhecida \((.+?)\): usamos um valor médio para a erosão\.$", r"Unknown slope class (\1): we used an average value for erosion."),
        (r"(\S+) dos dias de chuva forte caem em meses com planta no campo; ", r"\1 of heavy-rain days fall in months with plants in the field; "),
        (r" O solo tem erodibilidade (baixa|média|alta), estimada pelo mapa global de solo\.$", lambda m: f" The soil has {_ERODIBILIDADE[m.group(1)]} erodibility, estimated from the global soil map."),
        (r" O solo tem erodibilidade (baixa|média|alta)\.$", lambda m: f" The soil has {_ERODIBILIDADE[m.group(1)]} erodibility."),
        (r"terreno ([a-z ]+), declividade de (\S+)% medida por satélite \(SRTM\)\.(?=\s|$)",
         lambda m: f"{_RELEVO.get(m.group(1), m.group(1))} terrain, slope of {m.group(2)}% measured by satellite (SRTM)."),
        (r"sem dado de declive\.(?=\s|$)", "no slope data."),
        (r"terreno ([a-z ]+)\.(?=\s|$)", lambda m: f"{_RELEVO.get(m.group(1), m.group(1))} terrain."),
        (r"^Sem a erodibilidade do solo \(mapa global de solo\): contamos um valor médio para a erosão\.$",
         "No soil erodibility (global soil map): we used an average value for erosion."),
        (r"^Erodibilidade do solo \(K da USLE, classe (baixa|média|alta)(?:, estimada pelo mapa global de solo)?\)$",
         lambda m: f"Soil erodibility (USLE K, {_ERODIBILIDADE[m.group(1)]} class" + (", estimated from the global soil map)" if "estimada" in m.group(0) else ")")),
        (r"^Dias de chuva forte que caem em meses com planta$", "Heavy-rain days that fall in months with plants"),
        (r"^Declividade do terreno$", "Slope of the land"),
        # critérios: pragas
        (r"^(.+?): sem família botânica na base\.$", r"\1: no botanical family in our database."),
        (r"^Sem dados suficientes de família botânica das culturas\.$", "Not enough botanical family data for the crops."),
        (r"^Só há uma cultura na rotação: nada quebra o ciclo de pragas e doenças\.$", "There is only one crop in the rotation: nothing breaks the pest and disease cycle."),
        (r"^A rotação tem (\d+) família\(s\) de plantas em (\d+) culturas, com (\d+) par\(es\) seguido\(s\) da mesma família\.$",
         r"The rotation has \1 plant family(ies) across \2 crops, with \3 back-to-back pair(s) from the same family."),
        (r"^(\d+) de (\d+) trocas de cultura mudam de família de planta\.$", r"\1 of \2 crop changes switch to a different plant family."),
        (r"^Famílias botânicas na rotação$", "Botanical families in the rotation"),
        # critérios: renda
        (r"^Sem dados suficientes das culturas para contar as que dão renda\.$", "Not enough crop data to count the ones that bring income."),
        (r"^A rotação tem (\d+) cultura\(s\) para vender", r"The rotation has \1 crop(s) to sell"),
        (r" Contamos as culturas de venda; preço e produção da sua região ainda não entram nesta nota\.$",
         " We count the crops to sell; prices and production in your region are not part of this score yet."),
        (r"^Culturas comerciais na rotação$", "Cash crops in the rotation"),
        # candidatas: janela de semeadura das coberturas (regra 12)
        (r"^(.+?): ainda não confirmamos a melhor época para semear esta cobertura\. Confirme com seu agrônomo\.$",
         r"\1: we have not confirmed the best time to sow this cover crop yet. Check with your agronomist."),
        (r"^(.+?): não conseguimos confirmar depois de qual cultura esta cobertura pode ser semeada\. Confirme com seu agrônomo\.$",
         r"\1: we could not confirm after which crop this cover crop can be sown. Check with your agronomist."),
        (r"^(.+?): esta cobertura só serve depois de uma cultura colhida para silagem, e não sabemos se a sua é\. Confirme antes de semear\.$",
         r"\1: this cover crop only fits after a crop harvested for silage, and we don't know if yours is. Check before sowing."),
        (r"^(.+?): a época de semeadura ainda não foi confirmada para a sua região\.$", r"\1: the sowing time has not been confirmed for your region yet."),
        (r"^(.+?): confira se dá para semear depois de (.+)\.$", r"\1: check whether it can be sown after \2."),
        (r"^(.+?): a semeadura é em (\w+), logo depois da colheita de (.+?); depende da data da sua colheita\.$",
         lambda m: f"{m.group(1)}: sowing is in {_MES_POR_EXTENSO_EN.get(m.group(2), m.group(2))}, right after the harvest of "
                   f"{m.group(3).replace(' e ', ' and ')}; it depends on your harvest date."),
        (r"^Nenhuma planta de cobertura da nossa base serve para o seu período sem planta \((.+?)\) na sua região, pela época de semear ou pelo clima\. Confirme com seu agrônomo\.$",
         r"No cover crop in our database fits your period without plants (\1) in your region, because of sowing time or climate. Check with your agronomist."),
        # critérios: animais
        (r"^(.+?): valor forrageiro desconhecido \((.+?)\)\.$", r"\1: unknown forage value (\2)."),
        (r"^Sem dado de comida para os animais nas culturas desta rotação\.$", "No animal-feed data for the crops in this rotation."),
        (r"^Sem valor forrageiro: critério de animais ignorado\.$", "No forage value: the animals criterion was skipped."),
        (r"^A melhor comida para os animais da rotação é a de (.+?) \(classe (\w+)\)\.$", lambda m: f"The best animal feed in the rotation comes from {m.group(1)} ({_classe(m, 2)} class)."),
        (r"^Valor forrageiro \(maior da rotação: (.+?)\)$", r"Forage value (highest in the rotation: \1)"),
        # crops fora da base
        (r"^Sem dados suficientes de (.+?): ela entra na rotação, mas não tem nota própria\.$", r"Not enough data on \1: it stays in the rotation, but has no score of its own."),
        # fontes
        (r"^Base de culturas do Field Shift \(números para (\S+), arranjo (.+)\)$", r"Field Shift crop database (figures for \1, regional arrangement \2)"),
        (r"^Base de culturas do Field Shift \(Kc, FAO-56\) e ET0 do NASA POWER$", "Field Shift crop database (Kc, FAO-56) and ET0 from NASA POWER"),
        (r"^Base de culturas do Field Shift$", "Field Shift crop database"),
        (r"^Calendário informado pelo produtor$", "Calendar given by the farmer"),
        (r"^Prioridades e restrições informadas pelo produtor$", "Priorities and limits given by the farmer"),
        (r"^Resposta do produtor \(pergunta 7\)$", "Farmer's answer (question 7)"),
        (r"^NASA POWER, média (\S+), célula ~50 km centrada em (.+)$", r"NASA POWER, \1 average, ~50 km cell centered at \2"),
        (r"^NASA POWER, (\d{4}), célula ~50 km centrada em (.+)$", r"NASA POWER, \1, ~50 km cell centered at \2"),
        # períodos
        (r"\bo ano todo\b", "all year"),
        (r"\bsem meses definidos\b", "no months set"),
    ]
]

_MESES_RE = re.compile(rf"\((?:{_MES})(?:–(?:{_MES}))?\)")
_DECIMAL = re.compile(r"(?<=\d),(?=\d)")


@lru_cache
def _nomes_en() -> list[tuple[re.Pattern, str]]:
    """Nomes em português (culturas dos dois catálogos e máquinas) -> inglês, do mais longo para o mais curto."""
    pares: dict[str, str] = {}
    exibicao = base.culturas()
    for pais in catalogo_motor.CSV_POR_PAIS:
        for c in catalogo_motor.catalogo_do_pais(pais).values():
            en = None
            if c.id in exibicao:
                en = base.nome_exibicao(exibicao[c.id], "en")  # `c.nome` já é o nome de exibição em português
            if not en or en == c.nome:
                m = re.search(r"\(([^)]+)\)\s*$", c.nome_base or c.nome)  # cultura fora do JSON: "Algodão (upland cotton)" -> "Upland cotton"
                en = (m.group(1)[:1].upper() + m.group(1)[1:]) if m else en
            if en and en != c.nome:
                pares[c.nome] = en
    for e in base.equipamentos().values():
        if e.get("nome_en") and e["nome_en"] != e["nome"]:
            pares[e["nome"]] = e["nome_en"]
    return [(re.compile(rf"(?<!\w){re.escape(pt)}(?!\w)"), en) for pt, en in sorted(pares.items(), key=lambda p: -len(p[0]))]


def _meses(m: re.Match) -> str:
    texto = m.group(0)
    for pt, en in zip(_MESES_PT, _MESES_EN, strict=True):
        texto = re.sub(rf"(?<![a-z]){pt}(?![a-z])", en, texto)
    return texto


def traduzir(texto: str | None) -> str | None:
    if not texto:
        return texto
    for padrao, troca in _REGRAS:
        texto = padrao.sub(troca, texto)
    for padrao, en in _nomes_en():
        texto = padrao.sub(en, texto)
    texto = _MESES_RE.sub(_meses, texto)
    return _DECIMAL.sub(".", texto).replace(_MILHAR, ",")


def traduzir_valor(valor):
    """Valor de evidência: classes e sim/não viram inglês; números e faixas trocam a vírgula decimal."""
    if not isinstance(valor, str):
        return valor
    return _CLASSES.get(valor, traduzir(valor))


def traduzir_unidade(unidade: str | None) -> str | None:
    return _UNIDADES.get(unidade, unidade) if unidade else unidade


@lru_cache
def _textos_do_catalogo() -> frozenset[str]:
    """lacuna_informacao e risco_revisao_local de todas as culturas: textos do catálogo, só em português."""
    return frozenset(
        t
        for pais in catalogo_motor.CSV_POR_PAIS
        for c in catalogo_motor.catalogo_do_pais(pais).values()
        for t in (c.lacuna_informacao, c.risco_revisao_local)
        if t
    )


def lacunas_em_ingles(lacunas: list[str]) -> list[str]:
    """Traduz as lacunas; os textos do catálogo (que ainda não têm versão em inglês) ficam de fora."""
    return [traduzir(t) for t in lacunas if t.partition(": ")[2] not in _textos_do_catalogo()]
