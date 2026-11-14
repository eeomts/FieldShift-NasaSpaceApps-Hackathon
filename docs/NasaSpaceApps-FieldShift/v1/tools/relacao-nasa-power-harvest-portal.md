# Relação entre NASA POWER e NASA Harvest Portal no Field Shift

> Projeto: Field Shift (NASA Space Apps Challenge 2026)
> Documento compilado em 14/11/2026
> Documentos relacionados: `nasa-power-api-daily.md` e `harvest-portal-api.md`

---

## Sumário

1. [Decisão da equipe](#1-decisão-da-equipe)
2. [Quem responde o quê](#2-quem-responde-o-quê)
3. [Fluxo completo](#3-fluxo-completo)
4. [Etapa 1: filtro climático (NASA POWER)](#4-etapa-1-filtro-climático-nasa-power)
5. [Etapa 2: nota de mercado (Harvest Portal)](#5-etapa-2-nota-de-mercado-harvest-portal)
6. [Etapa 3: combinação das notas](#6-etapa-3-combinação-das-notas)
7. [Como os dados se conectam](#7-como-os-dados-se-conectam)
8. [O que aparece na tela](#8-o-que-aparece-na-tela)
9. [Exemplo: o caso do Seu Joãozinho](#9-exemplo-o-caso-do-seu-joãozinho)
10. [Esboço de implementação](#10-esboço-de-implementação)
11. [Diferenças entre as duas fontes](#11-diferenças-entre-as-duas-fontes)
12. [Riscos e cuidados](#12-riscos-e-cuidados)
13. [Como apresentar no pitch](#13-como-apresentar-no-pitch)

---

## Nível de verificação

- Os endpoints e parâmetros vêm dos dois documentos de API do projeto.
- **Os limiares climáticos, os pesos e as fórmulas de nota são uma proposta** para o protótipo. Não vêm de nenhuma fonte oficial e precisam ser revisados pela equipe e, se possível, por alguém de agronomia.
- Todos os números do exemplo (seção 9) são **fictícios**.

---

## 1. Decisão da equipe

| Item | Decisão |
|---|---|
| Fonte climática | **NASA POWER**: filtra as culturas pelo clima do local |
| Fonte de mercado | **NASA Harvest Portal**: dá a nota de mercado das culturas que passaram no filtro |
| Ordem | **Primeiro o clima, depois o mercado** |
| Papel da ferramenta | Apoia a decisão, não decide. A palavra final é do agricultor |

**Em uma frase:** o clima diz **o que dá para plantar**, e o mercado diz **se vale a pena plantar**.

---

## 2. Quem responde o quê

| Pergunta do agricultor | Fonte | Escala do dado |
|---|---|---|
| "Essa cultura aguenta a seca daqui?" | NASA POWER | Célula de ~55 km |
| "Tem risco de geada na fase sensível?" | NASA POWER | Célula de ~55 km |
| "Quanta água ela vai precisar?" | NASA POWER (ET₀ FAO-56) | Célula de ~55 km |
| "Tem produção e comércio dessa cultura?" | Harvest Portal (FAO, OECD) | País inteiro |
| "O mercado está crescendo ou caindo?" | Harvest Portal | País inteiro |
| "Tem comprador perto de mim?" | **Nenhuma das duas.** Cooperativa e agricultor | Local |

---

## 3. Fluxo completo

```
 Agricultor marca o talhão no mapa
 e escolhe as prioridades
              │
              ▼
┌───────────────────────────────┐
│ ETAPA 1 · NASA POWER          │   GET /api/temporal/daily/point
│ Indicadores climáticos        │   (chuva, temperatura, ET₀, geada)
│ do local                      │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ FILTRO CLIMÁTICO              │   Cultura cabe na janela de chuva?
│ Elimina o que não aguenta     │   Risco de geada na fase sensível?
│ + nota de clima (0 a 5)       │   Déficit hídrico aceitável?
└───────────────┬───────────────┘
                │  só as culturas aprovadas
                ▼
┌───────────────────────────────┐
│ ETAPA 2 · HARVEST PORTAL      │   package_search → package_show
│ Produção e comércio no país   │   → datastore_search
│ + nota de mercado (0 a 5)     │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ ETAPA 3 · COMBINAÇÃO          │   Nota final = peso_clima × clima
│ Ordena as culturas pelas      │              + peso_mercado × mercado
│ prioridades do agricultor     │
└───────────────┬───────────────┘
                ▼
 Tela: ranking + motivos + fontes + aviso
 "confirme com seu técnico e sua cooperativa"
```

**Por que o clima vem primeiro:** não adianta mostrar o mercado de uma cultura que vai morrer de seca ou de geada. O filtro climático também reduz o número de consultas ao Harvest Portal.

---

## 4. Etapa 1: filtro climático (NASA POWER)

### 4.1 Chamada

```
GET https://power.larc.nasa.gov/api/temporal/daily/point
    ?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M,PS
    &community=AG
    &latitude=<lat>&longitude=<lon>
    &start=19910101&end=20251231
    &time-standard=LST
    &format=JSON
    &user=fieldshift
```

Uma chamada por talhão (ou por célula de 0,5°), guardada em cache.

### 4.2 Indicadores calculados

| Indicador | Parâmetro do POWER | Cálculo |
|---|---|---|
| Fim da estação chuvosa | `PRECTOTCORR` | Mês em que a chuva média cai abaixo de um limite |
| Veranico | `PRECTOTCORR` | Sequências de 10+ dias com < 1 mm na janela da cultura |
| Risco de geada | `T2M_MIN` | % de anos com `T2M_MIN` ≤ 2 °C na fase sensível |
| Calor extremo | `T2M_MAX` | Dias acima do limite da cultura |
| Graus-dia | `T2M_MAX`, `T2M_MIN` | Soma de (média − temperatura base) no ciclo |
| ET₀ | `T2M_MAX`, `T2M_MIN`, `RH2M`, `ALLSKY_SFC_SW_DWN`, `WS2M`, `PS` | FAO-56 Penman-Monteith |
| Balanço hídrico | `PRECTOTCORR` e ET₀ | Chuva − (ET₀ × Kc da cultura) no ciclo |

### 4.3 Regras do filtro (proposta)

Cada cultura candidata tem uma "ficha" com suas exigências (ciclo, temperatura base, tolerância à seca, sensibilidade à geada, Kc). A ficha vem de literatura agronômica e deve ser revisada.

| Regra | A cultura é **eliminada** se... |
|---|---|
| Geada | Risco de geada na fase sensível > 30% dos anos |
| Água | Déficit hídrico no ciclo > tolerância da cultura |
| Ciclo | Graus-dia disponíveis na janela < graus-dia exigidos |
| Calor | Dias de calor extremo na floração > limite da cultura |

### 4.4 Nota de clima (0 a 5)

Para as culturas que passaram:

```
nota_clima = 5 × (1 − risco_combinado)

risco_combinado = média ponderada de:
    risco_hídrico   (0 a 1)
    risco_geada     (0 a 1)
    risco_calor     (0 a 1)
```

Cada risco é a fração de anos, na série de 1991 a 2025, em que o problema aconteceu na janela da cultura.

---

## 5. Etapa 2: nota de mercado (Harvest Portal)

### 5.1 Chamadas

```
1. GET .../api/3/action/package_search?q=crop production&fq=organization:<org>&rows=5
2. GET .../api/3/action/package_show?id=<dataset>
3. GET .../api/3/action/datastore_search?resource_id=<id>&limit=0         (colunas)
4. POST .../api/3/action/datastore_search                                 (dados)
   { "resource_id": "<id>",
     "filters": { "<coluna_país>": "BRA", "<coluna_cultura>": "<cultura>" },
     "sort": "<coluna_ano> desc", "limit": 15 }
```

Os passos 1 a 3 são feitos **uma vez**, no preparo dos dados. Na hora de usar, só o passo 4 é repetido para cada cultura aprovada no filtro climático. Melhor ainda: baixar a tabela inteira antes da demo e consultar localmente.

⚠️ Os nomes de dataset, organização e colunas precisam ser confirmados na API. Os do exemplo são fictícios.

### 5.2 Indicadores de mercado

| Indicador | Cálculo | O que mostra |
|---|---|---|
| Tamanho | Produção média dos últimos 3 anos, comparada à maior cultura da lista | Se há volume (e, portanto, compradores) |
| Tendência | Variação da produção em 10 anos | Se o mercado cresce ou encolhe |
| Estabilidade | Variação ano a ano | Se o mercado é previsível |

### 5.3 Nota de mercado (0 a 5)

```
nota_mercado = 5 × (0,5 × tamanho_normalizado
                  + 0,3 × tendência_normalizada
                  + 0,2 × estabilidade_normalizada)
```

Cada termo vai de 0 a 1, comparando as culturas candidatas entre si.

**Se o país não tiver dado** para a cultura, a nota fica **"sem dado"**. Não use zero, porque zero pareceria "mercado ruim", e o problema é só falta de informação.

---

## 6. Etapa 3: combinação das notas

### 6.1 Fórmula

```
nota_final = peso_clima × nota_clima + peso_mercado × nota_mercado
             ─────────────────────────────────────────────────────
                         peso_clima + peso_mercado
```

Os pesos vêm dos sliders de prioridade do agricultor (0 a 5):
- "Reduzir risco de falta de água / clima" → `peso_clima`
- "Estabilidade de renda / mercado" → `peso_mercado`

### 6.2 Regras extras

| Situação | Comportamento |
|---|---|
| Cultura reprovada no filtro climático | Não aparece no ranking, mas aparece na lista "descartadas", com o motivo |
| Mercado "sem dado" | Ordenar só pelo clima e mostrar o selo "mercado não verificado" |
| Notas finais muito próximas (diferença < 0,3) | Mostrar como empate técnico |
| Agricultor muda os pesos | Ranking recalculado na hora, sem novas chamadas às APIs |

### 6.3 Exemplo de efeito dos pesos (fictício)

| Cultura | Clima | Mercado | Pesos 4/3 (clima/mercado) | Pesos 2/5 |
|---|---|---|---|---|
| Sorgo | 4,5 | 3,0 | **3,9** (1º) | 3,4 (2º) |
| Milho | 2,5 | 4,5 | 3,4 (2º) | **3,9** (1º) |
| Milheto | 4,8 | 1,2 | 3,3 (3º) | 2,2 (3º) |

Um agricultor preocupado com a seca vê o sorgo em primeiro. Um agricultor que prioriza renda vê o milho em primeiro.

---

## 7. Como os dados se conectam

As duas fontes não compartilham identificadores. A ligação é feita pela **ficha da cultura**, criada pela equipe:

| Campo da ficha | Usado por | Exemplo |
|---|---|---|
| `nome_exibido` | Tela | "Sorgo" |
| `ciclo_dias`, `temp_base`, `kc`, `tolerancia_seca`, `sensivel_geada` | Filtro climático (POWER) | 110 dias, 10 °C... |
| `janela_plantio` | Filtro climático (POWER) | fev–mar |
| `codigo_mercado` | Consulta no Harvest Portal | `SORGHUM` (código da coluna de cultura) |
| `pais` | Consulta no Harvest Portal | `BRA` |

```
                 ficha da cultura
        ┌───────────────┴───────────────┐
        ▼                               ▼
  exigências climáticas           código de mercado
        │                               │
        ▼                               ▼
   NASA POWER                     Harvest Portal
 (lat, lon, datas)            (país, cultura, anos)
        │                               │
        ▼                               ▼
   nota_clima                      nota_mercado
        └───────────────┬───────────────┘
                        ▼
                   nota_final
```

O **país** é deduzido da coordenada que o agricultor marcou no mapa. A mesma coordenada vai para o POWER.

---

## 8. O que aparece na tela

| Bloco | Fonte | Conteúdo |
|---|---|---|
| **1. Filtro do clima** | NASA POWER | Resumo do clima local ("a chuva acaba em meados de abril") e culturas aprovadas ✓ ou descartadas ✗, com o motivo |
| **2. Clima + mercado** | POWER + Harvest | Um cartão por cultura, com duas barras (clima e mercado), a nota e uma frase de explicação |
| **Rodapé de fontes** | Ambas | "Clima: NASA POWER, 1991–2025, grade de ~55 km" · "Mercado: OECD/FAO via NASA Harvest Portal, dado do país" |
| **Aviso fixo** | — | "Sugestões para conversar com seu técnico. Confirme na cooperativa se há comprador na sua região." |
| **Botões** | — | "Mudar prioridades" (recalcula sem chamar as APIs) e "Salvar relatório" |

---

## 9. Exemplo: o caso do Seu Joãozinho

> ⚠️ Tudo nesta seção é fictício.

**Situação:** o Seu Joãozinho planta soja e depois milho safrinha. O milho sofre quando a chuva acaba cedo. Ele quer saber o que plantar na safrinha.

**Etapa 1, NASA POWER:**
- A chuva costuma acabar em meados de abril.
- Há geada em junho em 3 de cada 10 anos.
- Resultado do filtro: **feijão descartado** (geada), **trigo descartado** (pouca chuva). **Sorgo, milho e milheto aprovados.**

**Etapa 2, Harvest Portal:**
- Milho: produção grande e crescendo, nota de mercado **4,5**.
- Sorgo: produção pequena, mas quase triplicou em 10 anos, nota **3,0**.
- Milheto: pouca produção e comércio, nota **1,2**.

**Etapa 3, combinação (pesos do Seu Joãozinho: clima 4, mercado 3):**

| Posição | Cultura | Clima | Mercado | Final |
|---|---|---|---|---|
| 1º | Sorgo | 4,5 | 3,0 | 3,9 |
| 2º | Milho | 2,5 | 4,5 | 3,4 |
| 3º | Milheto | 4,8 | 1,2 | 3,3 |

**Desfecho:** o Seu Joãozinho liga para a cooperativa, confirma que há comprador de sorgo e decide testar em um talhão. **A decisão foi dele.**

---

## 10. Esboço de implementação

```python
import requests

POWER = "https://power.larc.nasa.gov/api/temporal/daily/point"
HARVEST = "https://data.harvestportal.org/api/3/action"

FICHAS = {
    "sorgo":   {"codigo_mercado": "SORGHUM", "sensivel_geada": 0.3, "tolerancia_seca": 0.8},
    "milho":   {"codigo_mercado": "MAIZE",   "sensivel_geada": 0.6, "tolerancia_seca": 0.4},
    "milheto": {"codigo_mercado": "MILLET",  "sensivel_geada": 0.3, "tolerancia_seca": 0.9},
}

# ---------- Etapa 1: clima ----------
def baixar_clima(lat, lon):
    params = dict(parameters="T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M,PS",
                  community="AG", latitude=lat, longitude=lon,
                  start="19910101", end="20251231", time_standard="LST",
                  format="JSON", user="fieldshift")
    params["time-standard"] = params.pop("time_standard")
    r = requests.get(POWER, params=params, timeout=120)
    r.raise_for_status()
    return r.json()["properties"]["parameter"]

def avaliar_clima(serie, ficha):
    # calcula risco_hidrico, risco_geada, risco_calor (0 a 1) a partir da série
    # ... (indicadores da seção 4.2)
    riscos = {"hidrico": 0.2, "geada": 0.1, "calor": 0.1}   # placeholder
    eliminada = riscos["geada"] > 0.3 or riscos["hidrico"] > ficha["tolerancia_seca"]
    nota = 5 * (1 - sum(riscos.values()) / len(riscos))
    return eliminada, round(nota, 1), riscos

# ---------- Etapa 2: mercado ----------
def consultar_mercado(resource_id, pais, codigo):
    body = {"resource_id": resource_id,
            "filters": {"LOCATION": pais, "SUBJECT": codigo},   # ⚠️ confirmar colunas
            "sort": "TIME desc", "limit": 15}
    r = requests.post(f"{HARVEST}/datastore_search", json=body, timeout=60)
    data = r.json()
    if not data.get("success"):
        return None
    return data["result"]["records"]

# ---------- Etapa 3: combinação ----------
def nota_final(clima, mercado, peso_clima, peso_mercado):
    if mercado is None:                      # sem dado de mercado
        return clima
    return (peso_clima * clima + peso_mercado * mercado) / (peso_clima + peso_mercado)
```

O esboço mostra a estrutura. Os cálculos de risco e de nota de mercado precisam ser preenchidos com os indicadores das seções 4 e 5.

---

## 11. Diferenças entre as duas fontes

| | NASA POWER | NASA Harvest Portal |
|---|---|---|
| O que entrega | **O dado** (série diária de clima) | **O catálogo** e, em tabelas, o dado |
| Escala | Ponto (célula de ~55 km) | País |
| Tempo | Diário, desde 1981 | Anual, na maioria das tabelas |
| Plataforma | API própria da NASA Langley | CKAN |
| Autenticação | Nenhuma | Nenhuma (para dados públicos) |
| Formato | JSON, CSV, NetCDF, ICASA | JSON (DataStore), CSV, XLSX, SHP, TIFF... |
| Está na lista do desafio | **Sim** | **Não** |
| Papel no Field Shift | Base científica, filtro e nota de clima | Complemento, nota de mercado |

---

## 12. Riscos e cuidados

| Risco | Cuidado |
|---|---|
| Mercado nacional ≠ mercado local | Aviso fixo na tela e na ficha de evidência |
| Harvest Portal sem dado da cultura ou do país | Mostrar "mercado não verificado" e não usar nota zero |
| Nomes de colunas e códigos de cultura diferentes do esperado | Chamar `datastore_search` com `limit=0` e montar a ficha a partir das colunas reais |
| Licença do dataset de mercado | Usar só datasets com `license_id` aberto e citar a organização de origem |
| Portal fora do ar na demo | Baixar as tabelas antes e usar cache |
| Limiares e pesos sem validação | Deixar explícito no pitch que são valores de protótipo |
| Clima em grade de ~55 km | Selo de confiança com a escala do dado |

---

## 13. Como apresentar no pitch

> "O Field Shift usa dados da NASA em duas camadas. O **NASA POWER**, um dos datasets indicados no desafio, analisa mais de 30 anos de clima do local e elimina as culturas que não aguentam a seca, a geada ou o calor dali. Depois, dados de mercado do **NASA Harvest Portal**, o repositório do programa oficial de agricultura da NASA, mostram quais culturas aprovadas têm produção e comércio fortes. O agricultor ajusta o peso de cada camada, e a ferramenta explica cada sugestão, com fonte e escala. A decisão continua sendo dele."

**Três mensagens-chave:**
1. **Clima primeiro:** não adianta recomendar uma cultura que não sobrevive no local.
2. **Duas fontes da NASA, papéis diferentes:** o POWER é a base científica, e o Harvest dá o contexto econômico.
3. **Transparência:** cada nota mostra de onde veio e em que escala.
