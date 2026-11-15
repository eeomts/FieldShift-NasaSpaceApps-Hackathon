"""Seis critérios de 0 a 1 (água, terra, erosão, pragas, renda, animais), cada um com explicação e evidências."""
from app.services.motor.catalogo import CulturaMotor
from app.services.motor.declive import fator_do_declive
from app.services.motor.entradas import EntradasMotor
from app.services.motor.formatos import classe_da_palha_texto, classe_forrageira_texto, num, pct
from app.services.motor.hidrico import etc_mensal
from app.services.motor.modelo import CRITERIOS, Estrategia, Evidencia, ItemRotacao, NotaCriterio
from app.services.motor.parametros import (
    CLASSE_BIOMASSA,
    CLASSE_FORRAGEIRO,
    FATOR_DECLIVE,
    FATOR_DECLIVE_SEM_DADO,
    FATOR_K_SEM_DADO,
    K_LIMITE_BAIXA,
    K_LIMITE_MEDIA,
    K_REFERENCIA,
    RENDA_MAXIMA,
    RENDA_POR_COMERCIAIS,
    TERRA_PESO_BIOMASSA,
    TERRA_PESO_COBERTURA,
    TERRA_PESO_FIXADORA,
)

FONTE_BASE = "Base de culturas do Field Shift"
FONTE_CALENDARIO = "Calendário informado pelo produtor"
Par = tuple[ItemRotacao, CulturaMotor]
Saida = tuple[NotaCriterio, list[str]]  # nota e lacunas


def fonte_da_base(c: CulturaMotor, e: EntradasMotor) -> str:
    """Fonte dos números da cultura; com arranjo regional aplicado (regra 13), diz para qual estado e arranjo."""
    if c.arranjo_aplicado is None:
        return FONTE_BASE
    return f"{FONTE_BASE} (números para {e.estado}, arranjo {c.arranjo_aplicado})"


def _faixa_da_palha(c: CulturaMotor) -> tuple[str, str] | None:
    """Regra 15: ('2,1–9,8', '2,1 a 9,8') quando a classe da palha depende da época e a faixa é conhecida."""
    f = c.faixa_palhada
    if not c.depende_da_epoca.get("aporte_biomassa") or f is None or f.minimo is None or f.maximo is None:
        return None
    return f"{num(f.minimo, 1)}–{num(f.maximo, 1)}", f"{num(f.minimo, 1)} a {num(f.maximo, 1)}"


def _com_avisos(texto: str, pares: list[Par], coluna: str) -> str:
    """Regra 16: o aviso da régua junto da explicação (sem repetir o "Atenção" que o próprio texto já traz)."""
    for c in dict.fromkeys(c for _, c in pares):
        aviso = c.avisos.get(coluna)
        if aviso and getattr(c, coluna) is not None:
            texto += f" ({aviso})" if aviso.startswith("Atenção") else f" (Atenção: {aviso})"
    return texto


def classe_do_k(k: float) -> str:
    return "baixa" if k < K_LIMITE_BAIXA else "media" if k < K_LIMITE_MEDIA else "alta"


def _limita(v: float) -> float:
    return max(0.0, min(1.0, v))


def _sem_dado(criterio: str, explicacao: str, lac: list[str]) -> Saida:
    return NotaCriterio(criterio, None, explicacao, []), lac


def _meses_com_planta(itens: tuple[ItemRotacao, ...]) -> set[int]:
    return {m for i in itens for m in i.meses()}  # inclui culturas fora do catálogo: o campo está ocupado


def _lista_nomes(pares: list[Par]) -> str:
    return ", ".join(dict.fromkeys(c.nome for _, c in pares))


def nota_agua(itens: tuple[ItemRotacao, ...], pares: list[Par], e: EntradasMotor) -> Saida:
    lac: list[str] = []
    chuvas = [e.clima.chuva_mm.get(m) for m in range(1, 13)]
    if any(v is None for v in chuvas):
        return _sem_dado("agua", "Sem dados suficientes de chuva do local.", ["Chuva do local incompleta: sem nota de água."])
    chuva_ano = sum(chuvas)
    etc_por_mes: dict[int, float] = {}  # consórcio: vale o componente que mais usa água no mês (regra 4)
    com_dado: list[Par] = []
    for item, c in pares:
        mensal = etc_mensal(item, c, e.clima)
        if mensal is None:
            lac.append(f"{c.nome}: sem Kc ou ET0 para calcular a água.")
            continue
        com_dado.append((item, c))
        for mes, v in mensal.items():
            etc_por_mes[mes] = max(etc_por_mes.get(mes, 0.0), v)
    if not com_dado:
        return _sem_dado("agua", "Sem dados suficientes para calcular a água da rotação.", lac)
    etc_ano = sum(etc_por_mes.values())
    nota = 0.0 if chuva_ano <= 0 else _limita(1 - etc_ano / chuva_ano)
    texto = f"A rotação usa cerca de {num(etc_ano, 0)} mm de água por ano e a chuva média do local é de {num(chuva_ano, 0)} mm."
    if e.irrigacao == "sim":
        texto += " Como você irriga, a irrigação cobre a falta de chuva."
    elif e.irrigacao == "parte":
        texto += " A irrigação cobre só parte do campo."
    evid = [
        Evidencia("Água que as culturas usam no ano (Kc x ET0)", round(etc_ano, 1), "mm", f"{FONTE_BASE} (Kc, FAO-56) e ET0 do NASA POWER", e.clima.periodo),
        Evidencia("Chuva do ano", round(chuva_ano, 1), "mm", e.clima.fonte, e.clima.periodo),
    ]
    baixas = [c for _, c in com_dado if c.confianca_parametros == "baixa" and c.agua_ciclo_mm_min and c.agua_ciclo_mm_max]
    for c in dict.fromkeys(baixas):  # regra 10: confiança baixa mostra a faixa, não um número só
        evid.append(Evidencia(f"Água que {c.nome} usa no ciclo (faixa da literatura, confiança baixa)", f"{num(c.agua_ciclo_mm_min, 0)}–{num(c.agua_ciclo_mm_max, 0)}", "mm", fonte_da_base(c, e), None))
    if baixas:
        texto += f" Os dados de água de {_lista_nomes([(i, c) for i, c in com_dado if c in baixas])} têm confiança baixa: a estimativa pode errar."
    return NotaCriterio("agua", nota, texto, evid), lac


def nota_terra(itens: tuple[ItemRotacao, ...], pares: list[Par], e: EntradasMotor) -> Saida:
    lac: list[str] = []
    cobertos = len(_meses_com_planta(itens))
    classes: list[tuple[float, CulturaMotor, str]] = []
    for _, c in pares:
        if c.aporte_biomassa is None:
            lac.append(f"{c.nome}: sem a classe de palha na base.")
        elif c.aporte_biomassa not in CLASSE_BIOMASSA:
            lac.append(f"{c.nome}: classe de palha desconhecida ({c.aporte_biomassa}).")
        else:
            classes.append((CLASSE_BIOMASSA[c.aporte_biomassa], c, c.aporte_biomassa))
    if not classes:
        return _sem_dado("terra", "Sem dados suficientes de palha das culturas.", lac)
    biomassa, cultura_palha, classe = max(classes, key=lambda x: x[0])
    fixadoras = [c for _, c in pares if c.fixa_nitrogenio]
    if not fixadoras and any(c.fixa_nitrogenio is None for _, c in pares):
        lac.append("Algumas culturas sem informação se fixam nitrogênio.")
    nota = _limita(TERRA_PESO_COBERTURA * cobertos / 12 + TERRA_PESO_BIOMASSA * biomassa + TERRA_PESO_FIXADORA * (1 if fixadoras else 0))
    fix_texto = f"tem {_lista_nomes([(i, c) for i, c in pares if c in fixadoras])}, que fixa nitrogênio" if fixadoras else "não tem planta que fixa nitrogênio"
    faixa = _faixa_da_palha(cultura_palha)
    palha_texto = classe_da_palha_texto(classe)
    classe_texto = f"palhada {palha_texto}, de {faixa[1]} t/ha conforme a data de manejo" if faixa else f"classe {palha_texto}"
    texto = f"O campo tem planta em {cobertos} dos 12 meses, a maior palhada é a de {cultura_palha.nome} ({classe_texto}) e a rotação {fix_texto}."
    texto = _com_avisos(texto, pares, "aporte_biomassa")
    if faixa:  # regra 15: a classe vem junto da faixa
        palha = Evidencia(f"Palhada de {cultura_palha.nome}: palhada {palha_texto}, de {faixa[1]} t/ha conforme a data de manejo (depende da época)", faixa[0], "t/ha", fonte_da_base(cultura_palha, e), None)
    else:
        palha = Evidencia(f"Palha que fica no campo (maior da rotação: {cultura_palha.nome})", palha_texto, "classe", fonte_da_base(cultura_palha, e), None)
    evid = [
        Evidencia("Meses do ano com planta no campo", cobertos, "meses", FONTE_CALENDARIO, None),
        palha,
        Evidencia("Planta que fixa nitrogênio na rotação", "sim" if fixadoras else "não", None, FONTE_BASE, None),
    ]
    return NotaCriterio("terra", nota, texto, evid), lac


def nota_erosao(itens: tuple[ItemRotacao, ...], pares: list[Par], e: EntradasMotor) -> Saida:
    lac: list[str] = []
    forte = {m: v for m, v in e.clima.dias_chuva_forte.items() if v is not None}
    if not forte:
        return _sem_dado("erosao", "Sem dados suficientes de chuva forte do local.", ["Chuva forte do local sem dados: sem nota de erosão."])
    cobertos = _meses_com_planta(itens)
    total = sum(forte.values())
    parcela = 1.0 if total <= 0 else sum(v for m, v in forte.items() if m in cobertos) / total
    medida = e.relevo.declividade_pct if e.relevo is not None else None
    if medida is not None:  # declividade medida (SRTM): LS da RUSLE, com teto 1
        fator = fator_do_declive(medida)
    else:  # só a classe (resposta q7), ou nada
        fator = FATOR_DECLIVE.get(e.relevo.classe) if e.relevo is not None else None
    if fator is None:
        fator = FATOR_DECLIVE_SEM_DADO
        lac.append("Sem declividade do terreno: usamos um valor médio para a erosão." if e.relevo is None else f"Classe de declive desconhecida ({e.relevo.classe}): usamos um valor médio para a erosão.")
    classe_k = None
    fator_k = FATOR_K_SEM_DADO
    if e.erodibilidade is None:
        lac.append("Sem a erodibilidade do solo (mapa global de solo): contamos um valor médio para a erosão.")
    else:
        classe_k = classe_do_k(e.erodibilidade.k_usle)
        fator_k = e.erodibilidade.k_usle / K_REFERENCIA  # proporcional ao K, como na USLE; o fator do declive multiplica (nota limitada a 0-1)
    nota = _limita(1 - (1 - parcela) * fator * fator_k)
    terreno = "sem dado de declive" if e.relevo is None else f"terreno {e.relevo.classe.replace('_', ' ')}"
    if medida is not None:
        terreno += f", declividade de {num(medida, 1)}% medida por satélite (SRTM)"
    texto = f"{pct(parcela)} dos dias de chuva forte caem em meses com planta no campo; {terreno}."
    if classe_k is not None:
        texto += f" O solo tem erodibilidade {classe_k.replace('media', 'média')}, estimada pelo mapa global de solo."
    evid = [Evidencia("Dias de chuva forte que caem em meses com planta", round(parcela * 100, 1), "%", e.clima.fonte, e.clima.periodo)]
    if e.relevo is not None:
        valor = e.relevo.declividade_pct if e.relevo.declividade_pct is not None else e.relevo.classe.replace("_", " ")
        evid.append(Evidencia("Declividade do terreno", valor, "%" if e.relevo.declividade_pct is not None else "classe", e.relevo.fonte, None))
    if e.erodibilidade is not None:
        evid.append(Evidencia(f"Erodibilidade do solo (K da USLE, classe {classe_k.replace('media', 'média')}, estimada pelo mapa global de solo)", e.erodibilidade.k_usle, "t·ha·h/(ha·MJ·mm)", e.erodibilidade.fonte, None))
    return NotaCriterio("erosao", nota, texto, evid), lac


def nota_pragas(itens: tuple[ItemRotacao, ...], pares: list[Par], e: EntradasMotor) -> Saida:
    lac: list[str] = []
    ordenados = sorted((p for p in pares), key=lambda p: (p[0].inicio_mes is None, p[0].inicio_mes or 0))
    familias: list[str] = []
    for _, c in ordenados:
        if c.familia_botanica is None:
            lac.append(f"{c.nome}: sem família botânica na base.")
        else:
            familias.append(c.familia_botanica)
    n = len(familias)
    if n == 0:
        return _sem_dado("pragas", "Sem dados suficientes de família botânica das culturas.", lac)
    if n < 2:
        nota = 0.0
        texto = "Só há uma cultura na rotação: nada quebra o ciclo de pragas e doenças."
    else:
        # Embrapa Soja (alternar espécies); VALIDACAO-PARAMETROS-MOTOR.md 2.7: nota = 1 − trocas sem mudar de família ÷ trocas.
        # Sem número escolhido e sem premiar nem punir o total de culturas. Consórcio (itens no mesmo mês) segue a ordem do calendário.
        seguidos = [(familias[i], familias[i + 1]) for i in range(n - 1)]
        if n >= 3:
            seguidos.append((familias[-1], familias[0]))  # a rotação é um ciclo: a última volta para a primeira
        mudam = sum(a != b for a, b in seguidos)
        nota = _limita(mudam / len(seguidos))
        texto = f"{mudam} de {len(seguidos)} trocas de cultura mudam de família de planta."
    evid = [Evidencia("Famílias botânicas na rotação", ", ".join(dict.fromkeys(familias)), None, FONTE_BASE, None)]
    return NotaCriterio("pragas", nota, texto, evid), lac


def nota_renda(itens: tuple[ItemRotacao, ...], pares: list[Par], e: EntradasMotor) -> Saida:
    if not pares:
        return _sem_dado("renda", "Sem dados suficientes das culturas para contar as que dão renda.", [])
    comerciais = [(i, c) for i, c in pares if c.tem_tipo("comercial")]
    n = len(comerciais)
    nota = RENDA_POR_COMERCIAIS.get(n, RENDA_MAXIMA)
    texto = f"A rotação tem {n} cultura(s) para vender" + (f": {_lista_nomes(comerciais)}." if n else ".")
    evid = [Evidencia("Culturas comerciais na rotação", n, "culturas", FONTE_BASE, None)]
    return NotaCriterio("renda", nota, texto, evid), []


def nota_animais(itens: tuple[ItemRotacao, ...], pares: list[Par], e: EntradasMotor) -> Saida:
    lac: list[str] = []
    valores: list[tuple[float, CulturaMotor, str]] = []
    for _, c in pares:
        if c.valor_forrageiro is None:
            continue  # "não sei" (regra 5): essa cultura não entra, sem chute
        if c.valor_forrageiro not in CLASSE_FORRAGEIRO:
            lac.append(f"{c.nome}: valor forrageiro desconhecido ({c.valor_forrageiro}).")
            continue
        valores.append((CLASSE_FORRAGEIRO[c.valor_forrageiro], c, c.valor_forrageiro))
    if not valores:
        return _sem_dado("animais", "Sem dado de comida para os animais nas culturas desta rotação.", lac + ["Sem valor forrageiro: critério de animais ignorado."])
    nota, c, classe = max(valores, key=lambda x: x[0])
    texto = _com_avisos(f"A melhor comida para os animais da rotação é a de {c.nome} (classe {classe_forrageira_texto(classe)}).", pares, "valor_forrageiro")
    return NotaCriterio("animais", nota, texto, [Evidencia(f"Valor forrageiro (maior da rotação: {c.nome})", classe_forrageira_texto(classe), "classe", fonte_da_base(c, e), None)]), lac


def calcular_notas(estrategia: Estrategia, e: EntradasMotor) -> tuple[dict[str, NotaCriterio], list[str]]:
    """Notas dos seis critérios e as lacunas. Cultura fora do catálogo entra no calendário, mas não nas notas."""
    itens = estrategia.itens
    pares = [(i, e.catalogo[i.cultura_id]) for i in itens if i.cultura_id in e.catalogo]
    lacunas = [f"Sem dados suficientes de {i.texto}: ela entra na rotação, mas não tem nota própria." for i in itens if i.cultura_id not in e.catalogo]
    funcoes = {"agua": nota_agua, "terra": nota_terra, "erosao": nota_erosao, "pragas": nota_pragas, "renda": nota_renda, "animais": nota_animais}
    notas: dict[str, NotaCriterio] = {}
    for criterio in CRITERIOS:
        nota, lac = funcoes[criterio](itens, pares, e)
        notas[criterio] = nota
        lacunas += [l for l in lac if l not in lacunas]
    return notas, lacunas
