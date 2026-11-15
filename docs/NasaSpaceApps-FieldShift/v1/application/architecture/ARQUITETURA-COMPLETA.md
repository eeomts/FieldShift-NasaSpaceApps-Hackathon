# Field Shift: arquitetura completa, passo a passo

## Como cada fonte de dados se comunica com o aplicativo e como isso ajuda o agricultor

> Projeto: Field Shift (NASA Space Apps Challenge 2026)
> Documento compilado em 14/11/2026
> Documentos relacionados: `NASA_POWER.md`, `NASA_HARVEST_PORTAL_API.md`, `NASA_POWER_X_HARVEST_PORTAL.md`, `fluxo-aplicativo-power-harvest-mcp.md` e os documentos de cada fonte em `tools/`

---

## Sumário

1. [Visão geral em uma página](#1-visão-geral-em-uma-página)
2. [As peças e como se comunicam](#2-as-peças-e-como-se-comunicam)
3. [Passo 0: preparo antes da demo](#3-passo-0-preparo-antes-da-demo)
4. [Passo 1: login e cadastro](#4-passo-1-login-e-cadastro)
5. [Passo 2: coleta dos dados do talhão](#5-passo-2-coleta-dos-dados-do-talhão)
6. [Passo 3: harmonização](#6-passo-3-harmonização)
7. [Passo 4: diagnóstico do campo atual](#7-passo-4-diagnóstico-do-campo-atual)
8. [Passo 5: filtro climático e de campo](#8-passo-5-filtro-climático-e-de-campo)
9. [Passo 6: nota de mercado](#9-passo-6-nota-de-mercado)
10. [Passo 7: montagem e comparação das estratégias](#10-passo-7-montagem-e-comparação-das-estratégias)
11. [Passo 8: tela de resultados](#11-passo-8-tela-de-resultados)
12. [Passo 9: chat com o assistente (MCP)](#12-passo-9-chat-com-o-assistente-mcp)
13. [Passo 10: relatório e decisão](#13-passo-10-relatório-e-decisão)
14. [Mapa: cada dataset, cada passo, cada benefício](#14-mapa-cada-dataset-cada-passo-cada-benefício)
15. [Falhas e plano B](#15-falhas-e-plano-b)
16. [Prioridades para as 48 horas](#16-prioridades-para-as-48-horas)
17. [Referências](#17-referências)

---

## Nível de verificação

- Endpoints do NASA POWER e do Harvest Portal vêm dos documentos de API do projeto.
- Para os datasets de satélite (GPM, SMAP, ECOSTRESS, Landsat, MODIS, GRACE, SRTM), **os nomes exatos de produtos, camadas e serviços de acesso estão marcados com ⚠️**. Confirme nos documentos de cada fonte e no Earthdata antes de programar.
- Limiares, pesos, notas e regras são **proposta da equipe** e precisam de revisão agronômica.
- **Todos os números e exemplos com o agricultor são fictícios.**

---

## 1. Visão geral em uma página

**O que o aplicativo faz:** ajuda o agricultor a montar uma rotação de culturas mais resistente ao clima, que proteja o solo e tenha mercado. Ele compara pelo menos três estratégias, incluindo a atual, e explica cada uma com evidências.

**Como faz, em quatro perguntas:**

| Pergunta | Quem responde | Datasets |
|---|---|---|
| **Como é o clima aqui?** | Camada de clima | NASA POWER, GPM IMERG, ECOSTRESS, GRACE |
| **Como está o meu campo?** | Camada de campo | MODIS/Landsat (NDVI), SMAP, SRTM |
| **O que dá para plantar e quando?** | Regras do aplicativo + ficha das culturas | Resultado das duas camadas acima |
| **Vale a pena plantar?** | Camada de mercado | Harvest Portal (API e MCP) |

```
                               AGRICULTOR
                                   │  login, talhão, culturas, prioridades
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             APLICATIVO                                  │
│                                                                         │
│   CAMADA DE CLIMA          CAMADA DE CAMPO           CAMADA DE MERCADO  │
│   NASA POWER (API)         MODIS / Landsat NDVI      Harvest Portal     │
│   GPM IMERG                SMAP                      (API)              │
│   ECOSTRESS                SRTM                                         │
│   GRACE                                                                 │
│        │                        │                          │            │
│        └────────────┬───────────┘                          │            │
│                     ▼                                      │            │
│            Harmonização (passo mensal / decendial)         │            │
│                     ▼                                      │            │
│            Diagnóstico do campo atual                      │            │
│                     ▼                                      │            │
│            Filtro climático e de campo ───────────────────►│            │
│                     ▼                                      ▼            │
│            Montagem de 3+ estratégias ◄──────────── nota de mercado     │
│                     ▼                                                   │
│            Tela de comparação + evidências + aviso                      │
│                     │                                                   │
│                     │ resumo pronto                                     │
│                     ▼                                                   │
│            Chat: IA ──── MCP ────► Harvest Portal                       │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                   Relatório → técnico e cooperativa → DECISÃO DO AGRICULTOR
```

---

## 2. As peças e como se comunicam

### 2.1 Tabela de comunicação

| Fonte | Como o aplicativo acessa | Login | Formato | Resolução | Atualização | Cache |
|---|---|---|---|---|---|---|
| **NASA POWER** | API REST, `GET /api/temporal/daily/point` | Nenhum | JSON / CSV | ~55 km, diário | 2 a 7 dias de atraso | Por célula de 0,5° |
| **GPM IMERG** | Serviço da NASA (GES DISC) ou recorte pré-processado ⚠️ | Earthdata Login | NetCDF / HDF5 → CSV | ~10 km, diário | Final: meses de atraso | Série por talhão |
| **SMAP** | AppEEARS (amostra por ponto) ⚠️ | Earthdata Login | CSV | ~9 km, 2 a 3 dias | Dias | Série por talhão |
| **ECOSTRESS** | AppEEARS (amostra por ponto) ⚠️ | Earthdata Login | CSV | ~70 m, irregular | Irregular | Médias mensais |
| **MODIS NDVI** | AppEEARS (amostra por ponto) ⚠️ | Earthdata Login | CSV | 250 m, 16 dias | Semanas | Série por talhão |
| **Landsat / HLS** | AppEEARS ou serviço USGS ⚠️ | Earthdata / USGS | CSV / GeoTIFF | 30 m, 8 a 16 dias | Dias | Série por talhão |
| **GRACE / GRACE-FO** | Arquivo de mascons (PO.DAAC / JPL) ⚠️ | Earthdata Login | NetCDF | ~300 km, mensal | Meses | Uma tendência por região |
| **SRTM** | Arquivo de elevação (LP DAAC) ⚠️ | Earthdata Login | GeoTIFF | 30 m, fixo | Não muda | Declividade por talhão |
| **Harvest Portal (API)** | API CKAN, `datastore_search` | Nenhum | JSON | País, anual | Varia | Tabela por cultura |
| **Harvest Portal (MCP)** | IA do chat via `https://mcp.harvestportal.org/mcp` | Nenhum | — | País | — | — |
| **Banco do aplicativo** | Interno | Login do agricultor | — | — | — | — |

> **Aviso de 15/11/2026: o AppEEARS foi descartado** (decisão do usuário; nota datada na D-009 do `DECISOES.md`). As linhas de SMAP, ECOSTRESS, MODIS NDVI e Landsat / HLS acima que dizem "AppEEARS" são o plano antigo, e o app **não** usa o AppEEARS. O clima do app vem do NASA POWER, baixado por célula.

### 2.2 Três jeitos de falar com os dados

| Jeito | Usado em | Por quê |
|---|---|---|
| **Ao vivo, pela API** | NASA POWER, Harvest Portal | APIs simples, sem login e rápidas |
| **Pré-processado e guardado** | GPM, SMAP, ECOSTRESS, MODIS, Landsat, GRACE, SRTM | Exigem login no Earthdata, arquivos grandes e processamento. Para a demo, a equipe baixa antes |
| **Pela IA, com MCP** | Harvest Portal no chat | Para perguntas livres que o aplicativo não programou |

---

## 3. Passo 0: preparo antes da demo

**Quem faz:** a equipe, antes da apresentação.

| # | Tarefa | Ferramenta |
|---|---|---|
| 0.1 | Escolher a região da demo e alguns talhões de exemplo | Mapa |
| 0.2 | Baixar MODIS NDVI, SMAP, SRTM e, se der, GPM e ECOSTRESS desses talhões (**o AppEEARS foi descartado em 15/11/2026**; a ferramenta desta tarefa está em aberto) | Earthdata |
| 0.3 | Baixar e guardar a série do NASA POWER dos mesmos talhões | API do POWER |
| 0.4 | Descobrir no Harvest Portal os `resource_id`, colunas e códigos das culturas | **MCP no Claude** e depois API |
| 0.5 | Baixar as tabelas de mercado | API do Harvest |
| 0.6 | Montar a ficha das culturas candidatas (ciclo, temperatura base, Kc, tolerância à seca e à geada, cobertura do solo, fixação de nitrogênio, código de mercado) | Literatura agronômica |

**Como ajuda o agricultor:** a demo não trava se algum serviço cair, e os números exibidos são reais.

---

## 4. Passo 1: login e cadastro

**O que o agricultor faz:**

1. Entra no aplicativo.
2. **Marca o talhão no mapa.**
3. **Cadastra a rotação atual**, com os meses: *soja de outubro a fevereiro, milho safrinha de fevereiro a julho, pousio de agosto a outubro.*
4. **Informa as restrições:** sem irrigação, só máquinas de grãos, só culturas com comprador na região.
5. **Ajusta as prioridades (0 a 5):** reduzir risco de seca, proteger o solo, renda/mercado, forragem, fixação de nitrogênio.

**Comunicação:**

```
Agricultor ──► Aplicativo ──► Banco do aplicativo
                              (usuário, coordenada, rotação, restrições, pesos)
```

**Como ajuda o agricultor:** tudo o que vem depois é sobre **o campo dele**, a **rotação dele** e as **prioridades dele**, não uma recomendação genérica.

---

## 5. Passo 2: coleta dos dados do talhão

**Quando acontece:** quando o agricultor toca em **"Analisar meu campo"**.

**Comunicação:**

```
Aplicativo
   │
   ├── API NASA POWER ─────────► clima diário 1991–2025       (ao vivo ou cache)
   ├── cache GPM IMERG ────────► chuva diária ~10 km           (pré-processado)
   ├── cache MODIS/Landsat ────► série de NDVI do talhão       (pré-processado)
   ├── cache SMAP ─────────────► umidade do solo               (pré-processado)
   ├── cache ECOSTRESS ────────► temperatura de superfície, ET (pré-processado)
   ├── cache SRTM ─────────────► elevação → declividade         (pré-processado)
   └── cache GRACE ────────────► tendência de água armazenada  (pré-processado)
```

### 5.1 Chamada ao NASA POWER

```
GET https://power.larc.nasa.gov/api/temporal/daily/point
    ?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M,PS
    &community=AG&latitude=<lat>&longitude=<lon>
    &start=19910101&end=20251231
    &time-standard=LST&site-elevation=<altitude do SRTM>
    &format=JSON&user=fieldshift
```

O SRTM entra aqui: a altitude do talhão vai no parâmetro `site-elevation`.

### 5.2 O que cada fonte entrega neste passo

| Fonte | Variável | Para quê |
|---|---|---|
| NASA POWER | Temperatura, chuva, umidade, radiação, vento, pressão | Base de todos os indicadores climáticos |
| GPM IMERG | Chuva diária | Chuva mais fina que a do POWER: veranicos e extremos |
| MODIS / Landsat | NDVI | O que está crescendo no campo e quando |
| SMAP | Umidade do solo superficial | Se o solo fica seco na janela da cultura |
| ECOSTRESS | Temperatura de superfície, evapotranspiração | Pontos de calor e estresse hídrico |
| SRTM | Elevação | Declividade, erosão, baixadas frias |
| GRACE | Anomalia de água armazenada | A região está perdendo água ao longo dos anos? |

**Como ajuda o agricultor:** em segundos, o aplicativo reúne mais de 30 anos de clima e o histórico real do campo dele, sem que ele precise baixar nada.

---

## 6. Passo 3: harmonização

**O problema:** cada fonte tem uma resolução e uma frequência diferentes.

| Fonte | Espaço | Tempo |
|---|---|---|
| POWER | ~55 km | Diário |
| GPM | ~10 km | Diário |
| SMAP | ~9 km | 2 a 3 dias |
| MODIS | 250 m | 16 dias |
| ECOSTRESS | 70 m | Irregular |
| SRTM | 30 m | Fixo |
| GRACE | ~300 km | Mensal |

**O que o aplicativo faz:**

1. **Espaço:** usa o valor do ponto do talhão em cada fonte (ou a média do polígono, para MODIS, Landsat e SRTM).
2. **Tempo:** agrega tudo para **passo mensal** (ou decendial, de 10 em 10 dias): soma para chuva e médias para temperatura, NDVI e umidade.
3. **Ausentes:** converte `-999` e máscaras de nuvem em "sem dado" e preenche lacunas curtas de NDVI por interpolação.
4. **Escala:** guarda junto de cada número a escala original, para mostrar na tela.

```
fontes com resolução diferente ──► tabela única: talhão × mês × variável (+ escala de origem)
```

**Como ajuda o agricultor:** ele vê um único calendário coerente, em vez de sete fontes que não conversam.

---

## 7. Passo 4: diagnóstico do campo atual

**Pergunta:** *"Onde a rotação atual sofre?"*

| Diagnóstico | Fonte | Como |
|---|---|---|
| **Rotação real do campo** | MODIS/Landsat NDVI | Detecta as safras na curva de NDVI (o `crop-cycle-detection` do NASA Harvest faz isso pronto) e compara com o que o agricultor cadastrou |
| **Período de solo descoberto** | MODIS/Landsat NDVI | Meses com NDVI baixo (ex.: < 0,25) |
| **Fim da estação chuvosa** | NASA POWER + GPM | Climatologia da chuva |
| **Veranicos na safrinha** | GPM (ou POWER) | Sequências de 10+ dias sem chuva |
| **Risco de geada** | NASA POWER + SRTM | % de anos com mínima ≤ 2 °C; baixadas pioram |
| **Calor na floração** | NASA POWER + ECOSTRESS | Dias acima do limite da cultura |
| **Déficit hídrico** | POWER (ET₀) + GPM + SMAP | Chuva − demanda da cultura; SMAP confirma solo seco |
| **Risco de erosão** | SRTM + GPM + NDVI | Declividade alta + chuva forte + solo descoberto |
| **Tendência de água** | GRACE | Perda de água armazenada na região ao longo dos anos |

**Resultado (fictício):**

> 🔴 Milho safrinha enche grão em maio, quando a chuva já acabou (déficit de ~180 mm).
> 🟠 Geada em junho em 3 de cada 10 anos.
> 🔴 Campo descoberto de agosto a outubro, com chuvas fortes caindo sobre solo nu na parte inclinada.

**Como ajuda o agricultor:** ele vê **por que** a rotação dele sofre, com números e fontes. Isso atende diretamente o pedido do desafio de mostrar "quando os campos ficam descobertos" e "quando as culturas atuais ficam mais vulneráveis".

---

## 8. Passo 5: filtro climático e de campo

**Pergunta:** *"Quais culturas aguentam este lugar?"*

O aplicativo compara a **ficha de cada cultura candidata** com o diagnóstico:

| Regra (proposta) | Fonte | A cultura é eliminada se... |
|---|---|---|
| Geada | POWER, SRTM | Risco de geada na fase sensível > 30% dos anos |
| Água | POWER, GPM, SMAP | Déficit no ciclo > tolerância da cultura |
| Ciclo | POWER | Graus-dia na janela < exigência da cultura |
| Calor | POWER, ECOSTRESS | Dias de calor extremo na floração > limite |
| Restrições do agricultor | Cadastro | Exige irrigação, máquina ou mercado que ele não tem |

**Resultado (fictício):**

| Cultura | Resultado | Motivo |
|---|---|---|
| Sorgo | ✅ | Tolera o fim de chuva |
| Milho | ✅ com risco | Déficit em maio |
| Milheto | ✅ | Muito tolerante à seca; cobre o solo |
| Braquiária (consórcio) | ✅ | Cobre o solo na seca |
| Feijão | ❌ | Geada na fase sensível |
| Trigo | ❌ | Chuva insuficiente |

**Nota de clima (0 a 5):** calculada para as aprovadas a partir dos riscos hídrico, de geada e de calor.

**Como ajuda o agricultor:** ele não perde tempo nem dinheiro com culturas que o clima do lugar dele não sustenta.

---

## 9. Passo 6: nota de mercado

**Pergunta:** *"Das culturas aprovadas, quais têm mercado?"*

**Comunicação:**

```
Aplicativo ──► API Harvest Portal
   POST /api/3/action/datastore_search
   { "resource_id": "<tabela de produção>",
     "filters": { "<país>": "<código do país>", "<cultura>": "<código>" },
     "sort": "<ano> desc", "limit": 15 }
◄── produção por ano
```

Uma chamada por cultura aprovada (ou consulta à tabela já baixada no Passo 0).

**Indicadores:** tamanho da produção, tendência de 10 anos e estabilidade. Viram a **nota de mercado (0 a 5)**. Sem dado = **"mercado não verificado"**, nunca zero.

**Como ajuda o agricultor:** evita trocar uma cultura arriscada por outra que ninguém compra.

---

## 10. Passo 7: montagem e comparação das estratégias

**Pergunta:** *"Quais rotações completas eu posso comparar?"*

O aplicativo encaixa as culturas aprovadas no calendário do agricultor e monta **pelo menos três estratégias**, incluindo a atual:

| Critério | Fonte | **A) Atual:** soja → milho → pousio | **B)** Soja → milho + braquiária | **C)** Soja precoce → sorgo |
|---|---|---|---|---|
| Risco climático | POWER, GPM, SMAP, ECOSTRESS | 🔴 Alto | 🟠 Médio-alto | 🟢 Médio-baixo |
| Proteção do solo / erosão | NDVI, SRTM, GPM | 🔴 Solo exposto ago–out | 🟢 Coberto o ano todo | 🟠 Parcial |
| Uso de água | POWER (ET₀), GPM | 🟠 | 🟠 | 🟢 |
| Mercado | Harvest Portal | 🟢 4,5 | 🟢 4,5 | 🟠 3,0 |
| Forragem | Ficha da cultura | 🔴 Nenhuma | 🟢 Pasto na seca | 🟠 Restos |
| Quebra de ciclo de pragas | Ficha da cultura | 🔴 | 🔴 | 🟠 |
| **Nota com os pesos do agricultor** | — | 2,1 | **3,8** | 3,5 |
| **Confiança** | Escala e validação dos dados | Alta | Média | Média |

*(Valores fictícios.)*

**Nota final:** média ponderada das notas pelos pesos que o agricultor escolheu no Passo 1. Se ele mudar os pesos, o ranking é recalculado na hora, sem chamar nenhuma API.

**Como ajuda o agricultor:** ele compara a rotação atual com alternativas lado a lado, **pelos critérios que importam para ele**.

---

## 11. Passo 8: tela de resultados

| Bloco da tela | Conteúdo | Fontes exibidas |
|---|---|---|
| **Raio-x do campo** | Cartões: "a chuva acaba em meados de abril", "campo descoberto de agosto a outubro", "parte inclinada com risco de erosão" | POWER, GPM, MODIS, SRTM |
| **Calendário de 12 meses** | Faixas de estação chuvosa, déficit hídrico, geada e solo descoberto, com as culturas por cima | POWER, GPM, MODIS |
| **Comparar estratégias** | Tabela do Passo 7 | Todas |
| **Detalhe da estratégia** | Por que foi sugerida, evidências, benefícios, lacunas e riscos para revisão local | Todas |
| **Selo de confiança** | Escala de cada dado e o que não foi validado | Todas |
| **Aviso fixo** | "Sugestões para conversar com seu técnico. Confirme na cooperativa se há comprador na sua região." | — |
| **Botões** | "Mudar prioridades", "Perguntar ao assistente", "Salvar relatório" | — |

**Exemplo de evidência no detalhe da estratégia B (fictício):**

> **Por que foi sugerida:** o campo fica descoberto por cerca de 3 meses e você deu peso alto para proteger o solo.
> **Evidências:**
> - NDVI abaixo de 0,25 de agosto a outubro (MODIS, 2001–2025, 250 m).
> - Média de 2 chuvas acima de 40 mm por ano em outubro e novembro (GPM IMERG, ~10 km).
> - Parte do talhão com declividade acima de 8% (SRTM, 30 m).
>
> **Lacunas:** a ferramenta não conhece as pragas do talhão nem tem análise de solo.
> **Riscos para revisão local:** competição da braquiária com o milho; dessecação antes da soja.

**Como ajuda o agricultor:** cada número tem fonte e escala. Ele sabe **o que** a ferramenta sugere, **por quê** e **onde ela pode errar**.

---

## 12. Passo 9: chat com o assistente (MCP)

**Quando acontece:** o agricultor toca em **"Perguntar ao assistente"** e faz uma pergunta livre.

**Comunicação:**

```
Agricultor ── "E gergelim, vale a pena?" ──► Aplicativo
                                                │ envia à IA:
                                                │ • a pergunta
                                                │ • resumo do diagnóstico (Passo 4)
                                                │ • notas e estratégias (Passo 7)
                                                │ • regras de segurança
                                                ▼
                                             IA (LLM) ── MCP ──► Harvest Portal
                                                │                (mercado do gergelim)
                                                ▼
Agricultor ◄── resposta com fontes e aviso ── Aplicativo
```

**Ponto importante:** o MCP do Harvest **só acessa o Harvest Portal**. Os dados de clima, campo e satélite vêm **prontos do aplicativo**, já calculados nos passos anteriores. A IA só explica e cruza; não recalcula números.

**Exemplo (fictício):**

> 🧑‍🌾 **Agricultor:** E gergelim, vale a pena aqui?
>
> 🤖 **Assistente:** O gergelim aguenta bem a seca, então combina com o fim de chuva em meados de abril aqui (NASA POWER e GPM). No Harvest Portal, a produção dele no país é pequena, mas vem crescendo. Ele cobre pouco o solo, então não resolve o problema de erosão de agosto a outubro (MODIS e SRTM). Converse com seu técnico e pergunte na cooperativa se compram gergelim na sua região.

**Regras de segurança da IA:** usar só os dados recebidos e os encontrados no portal; citar sempre a fonte e a escala; dizer "não encontrei" quando faltar dado; não recomendar agrotóxico ou dose; terminar com o lembrete do técnico e da cooperativa.

**Como ajuda o agricultor:** ele pergunta do jeito dele sobre qualquer cultura, inclusive as que o aplicativo não tinha na lista.

---

## 13. Passo 10: relatório e decisão

1. O agricultor toca em **"Salvar relatório"**.
2. O aplicativo gera um resumo com: o diagnóstico, as três estratégias, as evidências com fontes, as lacunas e as **perguntas para levar ao técnico** (ex.: *"Qual cultivar de braquiária usar? Vale ajustar a época do milho pelo zoneamento de risco do município?"*).
3. O agricultor leva o relatório ao técnico e à cooperativa.
4. **A decisão é dele.**

**Como ajuda o agricultor:** ele chega à conversa com o técnico com dados organizados e perguntas certas, em vez de só uma impressão.

---

## 14. Mapa: cada dataset, cada passo, cada benefício

| Dataset | Passos | Benefício para o agricultor |
|---|---|---|
| **NASA POWER** | 2, 4, 5, 7, 8, 9 | Sabe como o clima do lugar dele se comporta há mais de 30 anos: chuva, geada, calor, demanda de água |
| **GPM IMERG** | 2, 4, 5, 7, 8 | Vê veranicos e chuvas fortes com mais detalhe que o POWER |
| **SMAP** | 2, 4, 5 | Confirma se o solo costuma ficar seco na época crítica |
| **ECOSTRESS** | 2, 4, 5 | Identifica calor e estresse hídrico em escala fina |
| **MODIS NDVI** | 2, 4, 7, 8 | Vê quando o campo fica descoberto e qual rotação realmente acontece |
| **Landsat (30 m)** | 2, 4, 8 | Mesmo do MODIS, com mais detalhe dentro do talhão |
| **GRACE / GRACE-FO** | 2, 4, 8 | Entende se a água da região está diminuindo ao longo dos anos |
| **SRTM** | 2, 4, 5, 7, 8 | Sabe onde o talhão é inclinado (erosão) e onde a geada pega mais |
| **Harvest Portal (API)** | 6, 7, 8 | Sabe se a cultura sugerida tem produção e comércio no país |
| **Harvest Portal (MCP)** | 9 | Pergunta sobre qualquer cultura e recebe resposta com fonte |
| **Cadastro do agricultor** | 1, 5, 7, 10 | A recomendação respeita as restrições e prioridades dele |

### Fluxo em uma linha

```
Cadastro → coleta (NASA) → harmonização → diagnóstico → filtro → mercado (Harvest)
        → 3+ estratégias → tela com evidências → chat (MCP) → relatório → decisão do agricultor
```

---

## 15. Falhas e plano B

| Falha | Passo | Plano B |
|---|---|---|
| API do NASA POWER fora do ar | 2 | Usa a série em cache; se não houver, avisa e não gera recomendação climática |
| Dataset de satélite sem dado para o talhão (nuvem, lacuna) | 2, 4 | Mostra o indicador como "sem dado" e reduz o selo de confiança |
| GPM ou SMAP não pré-processados | 4, 5 | Usa a chuva e a umidade do POWER e informa a escala mais grosseira |
| Harvest Portal fora do ar ou sem a cultura | 6 | Ranking só pelo clima e campo, com "mercado não verificado" |
| IA ou MCP fora do ar | 9 | Chat indisponível; o resto do aplicativo funciona normalmente |
| Limiares da ficha da cultura incertos | 5 | Exibir "valores de referência; confirme com seu técnico" |

**Princípio:** o aplicativo funciona **sem a IA**. A recomendação vem dos Passos 1 a 8, com regras e dados. O chat é um extra.

---

## 16. Prioridades para as 48 horas

| Prioridade | O que implementar | Datasets |
|---|---|---|
| 🟢 **Essencial** | Passos 1, 2, 4, 5, 7, 8 com clima e solo descoberto | **NASA POWER**, **MODIS NDVI** |
| 🟢 **Essencial** | Passo 6 com tabela de mercado baixada | **Harvest Portal (API)** |
| 🟡 **Se der tempo** | Erosão e chuva mais precisa | **SRTM**, **GPM IMERG** |
| 🟡 **Se der tempo** | Passo 9 (chat) | **Harvest Portal (MCP)** + IA |
| ⚪ **Pitch / próximo passo** | Umidade do solo, calor fino, água de longo prazo, NDVI de 30 m | **SMAP**, **ECOSTRESS**, **GRACE**, **Landsat** |

**Frase para o pitch:**

> "O Field Shift cruza mais de 30 anos de clima do NASA POWER com o que os satélites da NASA veem no campo do agricultor (quando o solo fica descoberto, onde o terreno é inclinado, quando falta chuva) e com dados de mercado do NASA Harvest. A ferramenta mostra por que a rotação atual sofre, compara alternativas pelos critérios que o agricultor escolhe e explica cada sugestão com fonte e escala. Se ele quiser saber de outra cultura, pergunta no chat. A decisão continua sendo dele, junto com o técnico."

---

## 17. Referências

**Documentos do projeto**
- `NASA_POWER.md`: API do NASA POWER
- `NASA_HARVEST_PORTAL_API.md`: API do Harvest Portal
- `NASA_POWER_X_HARVEST_PORTAL.md`: integração clima + mercado
- `fluxo-aplicativo-power-harvest-mcp.md`: fluxos A (API) e B (MCP)
- `GPM_IMERG.md`, `SMAP_L4.md`, `HLS.md`, `MODIS_VIIRS.md`, `SRTM.md`, `comunicacao-entre-apis.md`

**Fontes externas**
- NASA POWER Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- Harvest Portal API: https://data.harvestportal.org/api-docs
- Harvest Portal MCP: https://data.harvestportal.org/mcp-docs
- NASA Harvest `crop-cycle-detection` (safras e solo descoberto a partir do NDVI): https://github.com/nasaharvest/crop-cycle-detection
- NASA Earthdata (login e acesso aos datasets de satélite): https://www.earthdata.nasa.gov/
