"""Números do motor de rotação: cada constante diz a fonte ou 'escolha de produto'; 'proposta, validar com o Yury' = ainda em decisão."""

DIAS_POR_MES = 30.4  # 365 / 12, arredondado

# Arranjos de regua.arranjos que são consórcio (regra 4 do README do catálogo), não região (regra 13)
ARRANJOS_DE_CONSORCIO = frozenset({"consorcio_milho_safrinha", "braquiaria_solteira"})

# Classe da palhada pela massa seca em t/ha (régua do README do catálogo; usada quando um arranjo regional traz o típico)
PALHADA_ALTA_T_HA = 6.0  # Alvarenga et al. 2001, Informe Agropecuário 22(208): 6 t/ha é quantidade adequada ao plantio direto
PALHADA_MEDIA_T_HA = 2.3  # Lopes, Cogo & Levien 1987, RBCS 11:71-75: massa que dá 50 % de cobertura do solo

# Candidatas (sem limite: todas são avaliadas, a conta é barata; decisão do usuário em 15/11)
CEREAIS_INVERNO = frozenset({"trigo", "cevada", "centeio", "aveia"})  # regra 12, apos_cereal_inverno: proposta, validar com o Yury

# Filtro de graus-dia (regra 2 do README do catálogo, Yury 14/11, revista em 15/11)
GD_ELIMINA_ABAIXO = 0.90  # abaixo de 90 % do mínimo da cultura elimina (só grãos)
GD_ALERTA_ABAIXO = 1.00  # entre 90 % e 100 %: "no limite térmico"; coberturas: abaixo de 100 % só avisa
GD_ANO_INICIO = 2001  # regra 2: mediana de 2001–2020, a mesma régua do mínimo do catálogo
GD_ANO_FIM = 2020
GD_PERCENTIL_ANO_FRIO = 10  # regra 2: P10 das safras; abaixo de 90 % do mínimo avisa "em ano frio"
GD_MIN_SAFRAS = 10  # proposta, validar com o Yury: com menos safras completas o filtro não decide

# Filtro de água (regra 1): chuva do período ÷ ETc do período. Entre 50 % e 80 % só avisa "água no limite"; a rotação atual nunca é eliminada
AGUA_ELIMINA_SUGESTAO_ABAIXO = 0.50  # sugestão nova abaixo disto é eliminada (sem irrigação "sim"); decisão do usuário em 15/11; FAO-56 eq. 90 com Ky do FAO-33: perda esperada acima de ~40 %; validar com o Yury
AGUA_MUITO_ABAIXO = 0.50  # abaixo disto, com irrigação em parte da área, o aviso diz que só fecha na parte irrigada
AGUA_ALERTA_ABAIXO = 0.80  # ok pela ordem de grandeza (VALIDACAO-PARAMETROS-MOTOR.md 2.1): FAO-56 eq. 90 e Tab. 24 (Ky do FAO-33), ~15–25 % de perda com 80 % da água

# Filtro de geada (ARQUITETURA-COMPLETA.md: risco na fase sensível > 30 % dos anos)
GEADA_MAX_FRACAO_DE_ANOS = 0.30
GEADA_MIN_DIAS_NO_ANO = 1  # o ano conta se algum mês da fase sensível teve pelo menos 1 dia de geada
GEADA_FASE_SENSIVEL = "terco_medio"  # ok como reserva para cultura sem tmin_critica_c (FAO Frost protection, Tab. 4.5; FAO-56 cap. 6); a regra 17 substitui quando houver limiar

# Fases do ciclo em dias (regra 17 do README do catálogo; decisões do usuário em 15/11)
DIA_DA_SEMEADURA = 15  # a semeadura é no dia 15 do mês de início do item (proposta, validar com o Yury)

# Frio por cultura (regra 17): com tmin_critica_c, a fase e os dias seguidos vêm do catálogo; > 30 % dos anos = GEADA_MAX_FRACAO_DE_ANOS
FRIO_MIN_ANOS_COM_DADO = 25  # proposta, validar com o Yury: com menos anos de fase completa (dos 30) o frio não decide, vira lacuna
# Fase sensível ao frio, como aparece na frase e na lacuna do frio. Sem jargão. As chaves são as fases aceitas por
# data/catalogo/scripts/montar_csv.py (FASES_FRIO); um teste confere.
FASES_FRIO_TEXTO = {
    "emergencia": "na emergência das plantas",
    "vegetativo": "no crescimento das plantas",
    "floracao": "na florada",
    "enchimento_grao": "no enchimento dos grãos",
    "ciclo_todo": "em todo o ciclo",
}
FASE_FRIO_PADRAO = "na fase sensível"  # fase com nome que ainda não conhecemos
FASE_FRIO_PERENE = "ao longo do ano"  # perene: o ano todo

# Calor na fase sensível (regra 11 revista; decisão do usuário em 15/11, validar com o Yury): só avisa, nunca elimina
CALOR_MAX_FRACAO_DE_ANOS = 0.30  # acima de 30 % dos anos com a sequência de dias quentes
CALOR_DIAS_SEGUIDOS = 3  # o ano conta com 3 dias seguidos de máxima acima de tmax_critica_c
CALOR_FASE_INICIO_FRAC = 1 / 3  # fase = terço do meio do ciclo, em dias a partir da semeadura (perene: o ano todo)
CALOR_FASE_FIM_FRAC = 2 / 3

# Mês por extenso (frases da regra 12 com o mês da colheita)
MESES_POR_EXTENSO = (
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
)  # fmt: skip

# Pesos das prioridades (decisão do usuário, 15/11)
PESOS_PRIORIDADE = (0.5, 0.3, 0.2)  # 1ª, 2ª e 3ª escolha, reescalados para sobrar PESO_NAO_ESCOLHIDO aos demais
PESO_NAO_ESCOLHIDO = 0.05

# Nota Terra: pesos são escolha de produto (VALIDACAO-PARAMETROS-MOTOR.md 2.3, sem fonte); a estrutura segue os 3 princípios da Agricultura de Conservação da FAO
TERRA_PESO_COBERTURA = 0.4
TERRA_PESO_BIOMASSA = 0.3
TERRA_PESO_FIXADORA = 0.3
# Classe do aporte de biomassa e do valor forrageiro (escala do CSV; masculino e feminino por segurança)
# Palha: ok (VALIDACAO-PARAMETROS-MOTOR.md 2.4a), ≈ cobertura do solo pela curva de Lopes, Cogo & Levien (1987) na palha típica da classe; alto = 6 t/ha ou mais (Alvarenga et al. 2001)
CLASSE_BIOMASSA = {"baixo": 0.33, "baixa": 0.33, "medio": 0.66, "media": 0.66, "alto": 1.0, "alta": 1.0}
# Forragem: escolha de produto, mantida pelo usuário em 15/11 (VALIDACAO-PARAMETROS-MOTOR.md 2.4b); "nenhum" vem da régua do README
CLASSE_FORRAGEIRO = {"nenhum": 0.0, "baixo": 0.3, "medio": 0.6, "alto": 1.0}
# Declive: fator = mín(1; LS da RUSLE), LS do USDA Agriculture Handbook 703 (tabelas de razão moderada, NRCS) e AH 537 (LS = 1 na
# parcela-padrão de 72,6 pés e 9 %). Decisão do usuário e do Yury (VALIDACAO-PARAMETROS-MOTOR.md, 2.5): usar a declividade medida do SRTM.
RAMPA_TIPICA_M = 46  # 150 pés: comprimento de rampa típico declarado (o guia do NRCS diz que a enxurrada se concentra em menos de 122 m)
RAMPA_PADRAO_M = 22.13  # 72,6 pés: rampa da parcela-padrão da USLE
# Sem declividade medida (só a classe, da resposta q7): LS no meio de cada classe com rampa de 46 m (1,5 %, 5,5 % e 14 % dão 0,22, 0,84 e 2,76), teto 1
FATOR_DECLIVE = {"plano": 0.22, "suave_ondulado": 0.84, "ondulado": 1.0, "forte_ondulado": 1.0, "montanhoso": 1.0}
FATOR_DECLIVE_SEM_DADO = 0.5  # escolha de produto (VALIDACAO-PARAMETROS-MOTOR.md): entre o plano e o suave ondulado
# Erodibilidade K da USLE (t·ha·h/(ha·MJ·mm), SoilGrids pelo método de Williams). Classes de Mannigel et al. 2002 (Acta Scientiarum 24(5)):
# baixa < 0,015, média de 0,015 a < 0,030, alta daí em diante. A classe só aparece no texto; a conta usa o K inteiro.
K_LIMITE_BAIXA = 0.015
K_LIMITE_MEDIA = 0.030
K_REFERENCIA = 0.0225  # centro da classe "média" de Mannigel et al. 2002 (0,015 a 0,030): fator = K / K_REFERENCIA, como na USLE (A = R·K·LS·C·P, AH 537)
FATOR_K_SEM_DADO = 1.0  # escolha de produto (VALIDACAO-PARAMETROS-MOTOR.md): neutro, a classe média
# Pragas: sem constante; a nota é a fração de trocas de cultura que mudam de família (Embrapa Soja; VALIDACAO-PARAMETROS-MOTOR.md 2.7)
# Renda: escolha de produto (VALIDACAO-PARAMETROS-MOTOR.md 2.8); é contagem de culturas comerciais, não lucro; calibrar depois com o valor da produção da PAM (IBGE)
RENDA_POR_COMERCIAIS = {0: 0.0, 1: 0.5, 2: 0.8}  # 3 ou mais: RENDA_MAXIMA
RENDA_MAXIMA = 1.0

# Explicação
DIFERENCA_MINIMA_POR_QUE = 0.1  # critério entra no "por que" se ganha da atual por pelo menos isto
MAX_FRASES_POR_QUE = 3
MAX_MELHORES = 2
ORDEM_CONFIANCA = ("baixa", "media", "alta")  # da pior para a melhor
