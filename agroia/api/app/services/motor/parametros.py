"""Números do motor de rotação: cada constante diz a fonte ou 'proposta, validar com o Yury'."""

DIAS_POR_MES = 30.4  # 365 / 12, arredondado

# Arranjos de regua.arranjos que são consórcio (regra 4 do README do catálogo), não região (regra 13)
ARRANJOS_DE_CONSORCIO = frozenset({"consorcio_milho_safrinha", "braquiaria_solteira"})

# Candidatas
MAX_CANDIDATAS = 30  # proposta, validar com o Yury

# Filtro de graus-dia (regra 2, Yury 14/11)
GD_ELIMINA_ABAIXO = 0.90  # abaixo de 90 % do mínimo da cultura elimina
GD_ALERTA_ABAIXO = 1.00  # entre 90 % e 100 %: "no limite térmico"

# Filtro de água (regra 1): chuva do período ÷ ETc do período. A água nunca elimina: só avisa "água no limite"
AGUA_MUITO_ABAIXO = 0.50  # abaixo disto, com irrigação em parte da área, o aviso diz que só fecha na parte irrigada
AGUA_ALERTA_ABAIXO = 0.80  # proposta, validar com o Yury

# Filtro de geada (ARQUITETURA-COMPLETA.md: risco na fase sensível > 30 % dos anos)
GEADA_MAX_FRACAO_DE_ANOS = 0.30
GEADA_MIN_DIAS_NO_ANO = 1  # o ano conta se algum mês da fase sensível teve pelo menos 1 dia de geada
GEADA_FASE_SENSIVEL = "terco_medio"  # proposta, validar com o Yury (floração): o terço do meio do ciclo, onde o Kc é médio

# Pesos das prioridades (decisão do usuário, 15/11)
PESOS_PRIORIDADE = (0.5, 0.3, 0.2)  # 1ª, 2ª e 3ª escolha, reescalados para sobrar PESO_NAO_ESCOLHIDO aos demais
PESO_NAO_ESCOLHIDO = 0.05

# Critérios 0-1: todas as fórmulas abaixo são proposta do coordenador, validar com o Yury
TERRA_PESO_COBERTURA = 0.4
TERRA_PESO_BIOMASSA = 0.3
TERRA_PESO_FIXADORA = 0.3
# Classe do aporte de biomassa e do valor forrageiro (escala do CSV; masculino e feminino por segurança)
CLASSE_BIOMASSA = {"baixo": 0.33, "baixa": 0.33, "medio": 0.66, "media": 0.66, "alto": 1.0, "alta": 1.0}
CLASSE_FORRAGEIRO = {"nenhum": 0.0, "baixo": 0.3, "medio": 0.6, "alto": 1.0}  # "nenhum" vem da régua do README
FATOR_DECLIVE = {"plano": 0.25, "suave_ondulado": 0.5, "ondulado": 0.75, "forte_ondulado": 1.0, "montanhoso": 1.0}
FATOR_DECLIVE_SEM_DADO = 0.5
# Erodibilidade K da USLE (t·ha·h/(ha·MJ·mm), SoilGrids pelo método de Williams): classes e fatores são proposta, validar com o Yury.
K_LIMITE_BAIXA = 0.02  # abaixo disso: baixa
K_LIMITE_MEDIA = 0.035  # abaixo disso: média; daí em diante: alta
FATOR_K = {"baixa": 0.75, "media": 1.0, "alta": 1.25}  # multiplica o fator de declive; média = neutro
FATOR_K_SEM_DADO = 1.0
PRAGAS_DESCONTO_MESMA_FAMILIA = 0.2  # por par seguido da mesma família
RENDA_POR_COMERCIAIS = {0: 0.0, 1: 0.5, 2: 0.8}  # 3 ou mais: RENDA_MAXIMA
RENDA_MAXIMA = 1.0

# Explicação
DIFERENCA_MINIMA_POR_QUE = 0.1  # critério entra no "por que" se ganha da atual por pelo menos isto
MAX_FRASES_POR_QUE = 3
MAX_MELHORES = 2
ORDEM_CONFIANCA = ("baixa", "media", "alta")  # da pior para a melhor
