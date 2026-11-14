# CONTEXTO DO PROJETO — Field Shift: Adapting Farms with NASA Data

> **Para a IA que ler este arquivo:** este documento é o contexto completo do problema que a equipe está resolvendo no **NASA Space Apps Challenge 2026**. Use-o como referência principal para entender requisitos, dados disponíveis, restrições e o que é esperado da solução. Itens marcados com **[verificar]** são informações que não foram confirmadas na fonte oficial e devem ser checadas antes de virar código ou afirmação na apresentação.

---

## 1. Resumo executivo

| Item | Valor |
|---|---|
| Evento | NASA Space Apps Challenge 2026 (hackathon global, ~48 h) |
| Desafio | **Field Shift: Adapting Farms with NASA Data** (slug: `adapting-farms-with-nasa-data`) |
| Dificuldade | Intermediária / Avançada |
| Áreas | Earth Science, Software, Arts & Multimedia |
| Usuário-alvo | Agricultores (pouca experiência técnica/geoespacial) e, secundariamente, técnicos agrícolas |
| Entregável central | **Ferramenta de apoio à decisão** (app, modelo, mapa interativo ou similar) para explorar **estratégias de rotação de culturas** |
| Insumos obrigatórios em espírito | Observações da Terra da NASA + informações locais de solo + características das culturas + prioridades do agricultor |
| Saída esperada | Comparação de **≥ 3 estratégias de rotação, incluindo a atual**, cada uma com justificativa, evidência, benefícios, lacunas de informação e riscos |
| Princípio inegociável | A ferramenta **apoia**, não substitui, o julgamento do agricultor e a expertise agronômica local |

**Problema em uma frase:** mudanças de temperatura, chuva irregular, escassez de água, eventos extremos e degradação do solo tornam difícil escolher rotações de culturas que protejam o campo, economizem água e aumentem a resiliência; a NASA tem décadas de dados ambientais que podem orientar essa escolha, mas eles não chegam ao agricultor de forma utilizável.

---

## 2. Texto original do desafio (referência literal)

> Farmers around the world navigate shifting temperatures, changing rainfall patterns, water shortages, extreme weather, and declining soil health. These pressures make it difficult to choose crop rotations that protect fields, conserve water, and support long‑term resilience. Your challenge is to create a decision‑support tool that uses NASA Earth observations along with local soil information, crop characteristics, and farmer priorities to help farmers explore rotation strategies that could strengthen soil health and adapt their farms to changing conditions.

### Background
> Farmers face increasingly complex decisions as temperatures shift, rainfall becomes less predictable, and soil health declines across many regions. Water shortages, erosion, nutrient depletion, and extreme weather events add further uncertainty. Selecting new crops to add to a rotation can be difficult, because a crop that improves soil health in one place may consume too much water, introduce disease, conflict with local markets, or fall outside expected growing seasons somewhere else.
>
> This challenge is inspired in part by multigenerational farming experience — many families have lived through seasons where better tools for tracking changing conditions could have helped identify healthier, more resilient rotation choices. Today, NASA's long‑term environmental datasets offer new ways to understand local growing conditions, and SI techniques open opportunities to translate that data into practical, farmer‑friendly insights.

### Objectives
> You may consider combining NASA Earth observations with local agricultural information to create an app, model, interactive map, or other decision‑support tool. The goal is to help farmers explore crop‑rotation options that may improve soil health and strengthen resilience to changing weather and water conditions.
>
> You may explore NASA datasets such as SMAP, ECOSTRESS, GPM, Landsat, MODIS, NASA POWER, GRACE and GRACE‑FO, and SRTM or other NASA elevation products. Using these datasets, you may analyze patterns in temperature, heat stress, rainfall, soil moisture, evaporation, frost risk, extreme precipitation, vegetation stress, and long‑term water trends. You may also consider local soil information, crop characteristics, and farmer priorities—such as water use, forage value, nitrogen‑fixing potential, erosion reduction, organic matter improvement, or market suitability.
>
> Your tool may highlight times when fields are typically bare, seasons when current crops appear more vulnerable, or opportunities for rotations that could interrupt pest cycles, reduce water demand, improve infiltration, or add supplemental income. You may compare at least three rotation strategies, including the existing rotation. For each strategy, you may explain why it was suggested, what evidence supports it, what benefits it may offer, where information gaps exist, and any risks that would need local review by farmers or agricultural experts.
>
> The intended outcome is a supportive tool — one that helps identify patterns and possibilities, but does not replace farmer judgment or local agricultural expertise.

### Potential Considerations (opcionais)

**Understanding Conditions & Data**
> - Explore how changes in temperature, soil moisture, rainfall, evaporation, and vegetation stress relate to crop vulnerability and soil health.
> - Consider explaining scientific terms such as evapotranspiration, soil moisture anomalies, vegetation indices (e.g., NDVI), frost risk, and water‑balance indicators.
> - Clarify how satellite observations differ from ground‑based measurements, and how combining both may improve accuracy.

**SI, Modeling, and Data Fusion**
> - You may compare different SI or statistical approaches for identifying patterns in historical climate and soil conditions.
> - Consider how SI could highlight seasonal transitions, bare‑field periods, or times when current crops show increased stress.
> - Explain how the model interprets uncertainty and where local expertise would be needed to validate results.
> - You may consider harmonizing datasets with different spatial and temporal resolutions by downsampling, aggregating, or resampling them to a common analysis grid. Harmonizing resolution can help the SI combine SMAP soil moisture, ECOSTRESS land‑surface temperature, GPM precipitation, Landsat/MODIS vegetation indices, GEDI biomass, and soil datasets into coherent features that support clear, explainable rotation‑strategy comparisons.

**Rotation Strategy Exploration**
> - Compare rotation scenarios by examining nutrient cycling, erosion risk, organic matter contributions, pest‑cycle disruption, water use, forage potential, or market considerations.
> - You may consider mapping which rotation ideas best align with farmer priorities—such as conserving water, generating supplemental income, or improving soil structure.
> - Include brief explanations of how nitrogen‑fixing crops, cover crops, deep‑rooting crops, or drought‑tolerant crops contribute to long‑term soil health.

**Geospatial Mapping & Visualization**
> - Consider whether interactive maps could help users explore trends over time such as long‑term soil moisture, heat waves, or water‑storage declines.
> - Explore ways to visualize field‑level vulnerabilities (e.g., zones of erosion risk, water stress hotspots, frost‑prone areas).
> - You may include optional add‑ons such as timelines, overlays comparing datasets, or scenario sliders that adjust rainfall or temperature patterns.

**Farmer‑Centered Design**
> - Consider how to make the tool easily interpretable for farmers who may have limited technical or geospatial experience.
> - Think about ways to allow farmers to input their own priorities or constraints, such as water availability, equipment limitations, or market preferences.
> - Share reminders that the tool is intended to support—not replace—local expertise, and highlight where human judgment is particularly important.

> **Nota sobre "SI":** o texto oficial usa "SI techniques". Pelo contexto, significa inteligência artificial / técnicas estatísticas e de aprendizado de máquina. **[verificar]** com os organizadores no Space Apps Connect se há um significado específico.

> **Nota:** a aba **Resources** da página do desafio contém links oficiais de dados e tutoriais e pode receber novos itens durante o evento. Consulte-a.

---

## 3. Requisitos estruturados

Interpretação do texto em níveis de prioridade. Nenhum item é formalmente obrigatório ("You may…"), mas os marcados como **NÚCLEO** são o coração do desafio e quase certamente serão avaliados.

### 3.1 NÚCLEO (fazer)
- **R1.** Usar **pelo menos um conjunto de dados de observação da Terra da NASA** como fonte de evidência.
- **R2.** Receber a **localização** do campo (ponto ou polígono).
- **R3.** Receber a **rotação atual** do agricultor.
- **R4.** Receber **prioridades e restrições** do agricultor (ex.: economia de água, renda extra, melhoria do solo, forragem, disponibilidade de água, equipamento, mercado).
- **R5.** Considerar **solo local** e **características das culturas**.
- **R6.** Gerar e comparar **≥ 3 estratégias de rotação, incluindo a atual**.
- **R7.** Para **cada** estratégia, apresentar:
  1. **Por que foi sugerida** (motivação ligada aos dados e às prioridades)
  2. **Evidência** que a sustenta (qual dado, período, fonte)
  3. **Benefícios** esperados
  4. **Lacunas de informação** (o que não sabemos)
  5. **Riscos que exigem revisão local** (agricultor/agrônomo)
- **R8.** Interface **compreensível para agricultores** sem formação técnica.
- **R9.** **Avisos explícitos** de que a ferramenta apoia e não substitui o julgamento humano.

### 3.2 DIFERENCIAIS (fazer se der tempo)
- **D1.** Identificar **períodos de solo descoberto** (bare field) a partir de índices de vegetação.
- **D2.** Identificar **estações de maior vulnerabilidade** da cultura atual (calor, seca, geada, chuva extrema).
- **D3.** Indicar oportunidades de **quebra de ciclo de pragas**, **redução de demanda hídrica**, **melhoria de infiltração** e **renda suplementar**.
- **D4.** **Mapa interativo** com tendências de longo prazo (umidade do solo, ondas de calor, queda de armazenamento de água).
- **D5.** **Mapa de vulnerabilidade intra-talhão**: zonas de risco de erosão, hotspots de estresse hídrico, áreas propensas a geada.
- **D6.** **Linha do tempo**, **sobreposição de camadas** comparando datasets.
- **D7.** **Sliders de cenário** ("e se chover −20%?", "e se +2 °C?").
- **D8.** **Glossário/explicações** de termos científicos (evapotranspiração, anomalia de umidade, NDVI, risco de geada, balanço hídrico).
- **D9.** Explicar **diferença entre satélite e medição em solo** e como a fusão melhora a precisão.
- **D10.** **Comparar abordagens de IA/estatística** e explicar como o modelo trata **incerteza**.
- **D11.** **Harmonizar** datasets com resoluções diferentes em uma **grade comum**.
- **D12.** Explicações curtas sobre **fixadoras de nitrogênio, plantas de cobertura, raízes profundas e culturas tolerantes à seca**.

### 3.3 Requisitos não funcionais
- **Explicabilidade** acima de precisão bruta: cada número mostrado deve ter origem rastreável.
- **Transparência de incerteza**: níveis de confiança visíveis (ex.: alta/média/baixa).
- **Linguagem simples**, sem jargão ou com jargão explicado na hora.
- **Funcionar ao vivo na demonstração** (preferir dados pré-baixados/cache para a região de demo).
- Respeitar termos de uso dos dados (dados NASA são abertos; alguns exigem login gratuito no Earthdata).

---

## 4. Personas e casos de uso

### Persona principal — agricultor familiar
- Planta a mesma rotação há anos (ex.: milho no verão, campo vazio no inverno).
- Sente efeitos do clima (secas em fases críticas, poço mais baixo, solo compactado), mas não tem dados para comparar alternativas.
- Usa celular; pouca familiaridade com mapas técnicos.
- Quer respostas do tipo: "o que posso plantar a mais/diferente, quando, e o que ganho/arrisco?".

### Persona secundária — técnico/agrônomo/extensionista
- Usa a ferramenta como ponto de partida para conversar com o agricultor.
- Quer ver a evidência, a fonte e a incerteza.

### Caso de uso principal (fluxo)
1. Agricultor marca o campo no mapa (ponto ou polígono).
2. Informa rotação atual (culturas + meses de plantio/colheita).
3. Ajusta prioridades (pesos) e restrições (água disponível, equipamento, mercado, culturas que não aceita).
4. Sistema busca/consulta dados NASA + solo para o local.
5. Sistema mostra **diagnóstico do campo** (clima histórico, tendências, períodos de solo descoberto, vulnerabilidades sazonais, relevo/erosão, água subterrânea).
6. Sistema gera **≥ 3 estratégias** (atual + alternativas), pontua conforme prioridades e exibe comparação lado a lado.
7. Para cada estratégia: justificativa, evidência, benefícios, lacunas, riscos, nível de confiança.
8. Agricultor exporta/compartilha o relatório para discutir com o técnico local.

### Caso inspirador citado na página
A imagem do desafio mostra uma agricultora de **Nevada (EUA) em campos de alfafa** — região semiárida, irrigação e escassez de água. Bom exemplo de demo nos EUA; para o Brasil, regiões como o Cerrado (soja/milho safrinha) ou o semiárido nordestino são alternativas.

---

## 5. Conceitos de domínio

### 5.1 Agronomia
| Conceito | Definição operacional para o sistema |
|---|---|
| Rotação de culturas | Sequência de culturas no mesmo talhão ao longo de estações/anos. Representar como lista de `{cultura, mês_início, mês_fim}` em um ciclo de N anos. |
| Sucessão / safrinha | Duas culturas no mesmo ano agrícola (ex.: soja → milho safrinha no Brasil). |
| Planta de cobertura (cover crop) | Cultura não necessariamente colhida, cultivada para proteger e melhorar o solo em janelas sem cultura comercial. |
| Fixadora de nitrogênio (leguminosa) | Soja, feijão, ervilha, alfafa, trevo, crotalária, feijão-de-porco, ervilhaca. Reduz necessidade de adubo nitrogenado para a cultura seguinte. |
| Raiz profunda | Nabo forrageiro, alfafa, guandu, girassol. Rompe compactação, melhora infiltração, recicla nutrientes de camadas profundas. |
| Tolerante à seca | Sorgo, milheto, girassol, guandu, algumas forrageiras. Menor demanda hídrica ou maior resiliência ao déficit. |
| Forrageira | Cultura para alimentação animal (alfafa, braquiária, aveia, sorgo forrageiro). Valor de renda e integração lavoura-pecuária. |
| Quebra de ciclo de pragas/doenças | Alternar famílias botânicas (ex.: gramínea ↔ leguminosa ↔ brássica) para interromper pragas/patógenos específicos de hospedeiro. |
| Saúde do solo | Matéria orgânica, estrutura/agregação, infiltração, atividade biológica, fertilidade, baixa erosão. |
| Erosão | Perda de solo superficial por água ou vento; maior em solo descoberto, declive alto e chuva intensa. |
| Coeficiente de cultura (Kc) | Fator (FAO-56) que converte evapotranspiração de referência (ET0) em demanda hídrica da cultura (ETc = Kc × ET0), por fase de desenvolvimento. |
| Graus-dia (GDD) | Acúmulo térmico acima de uma temperatura base; indica se a estação tem calor suficiente para completar o ciclo. |

### 5.2 Ciência da Terra / sensoriamento remoto
| Conceito | Definição operacional |
|---|---|
| Evapotranspiração (ET) | Evaporação do solo + transpiração das plantas. ET0 = referência (grama hipotética), ETc = da cultura, ETa = real (estimada por satélite, ex.: ECOSTRESS/MODIS). |
| Umidade do solo | Conteúdo volumétrico de água (m³/m³). Superficial (~0–5 cm, SMAP L3) ou zona radicular (~0–100 cm, SMAP L4). |
| Anomalia de umidade do solo | Desvio em relação à climatologia do mesmo período (dia do ano/mês). Usar z-score: `(x − média_clim) / desvio_clim`. |
| NDVI | `(NIR − Red) / (NIR + Red)`, de −1 a 1. Solo nu ≈ 0,1–0,2; vegetação densa ≥ 0,6. Alternativas: EVI (satura menos), NDMI (umidade da vegetação). |
| Estresse de vegetação | Queda anômala de NDVI/EVI, aumento de LST, razão ETa/ETp baixa (Evaporative Stress Index). |
| Risco de geada | Probabilidade de Tmin ≤ 0 °C (ou ≤ 2 °C a 2 m como proxy para geada no dossel) em cada semana/mês; datas típicas de última/primeira geada. |
| Estresse térmico | Dias com Tmax acima de limiar crítico da cultura (ex.: ~35 °C em florescimento para muitas culturas; ajustar por cultura). |
| Precipitação extrema | Dias acima do percentil 95/99 local ou acima de limiar fixo (ex.: > 50 mm/dia). |
| Balanço hídrico | `P − ETc` (ou `P − ETc − escoamento`) acumulado por período; negativo = déficit. |
| Armazenamento de água terrestre (TWS) | Soma de água em superfície, solo, subsolo e neve; GRACE mede anomalias mensais em larga escala. |
| Satélite × solo | Satélite: cobertura global, histórico longo, resolução limitada, afetado por nuvens/algoritmos. Estação em solo: preciso no ponto, cobertura esparsa. Fusão: calibrar/validar satélite com estações, ou downscaling. |
| Harmonização | Reprojetar e reamostrar para grade comum (espacial) e agregar para passo comum (temporal: semanal/mensal). Média para variáveis contínuas, moda para categóricas; documentar a perda de detalhe. |

---

## 6. Catálogo de dados

> **Atualização (14/11/2026, D-009 em `DECISOES.md`):** esta seção é o levantamento inicial. As fontes que o projeto usa de fato são as do núcleo em `tools/` (NASA POWER, GPM IMERG, MODIS NDVI, HLS, SRTM, GLDAS, SMAP L4, ERA5, FAO GAEZ, SoilGrids, MapBiomas, ZARC, INMET/CEMADEN, IBGE PAM, Earthdata Search, earthaccess e AppEEARS), mais as opcionais em `tools/extras/` (FIRMS, Sentinel-1 e Embrapa Solos). As demais fontes citadas aqui ficaram fora do MVP.

### 6.1 Datasets NASA citados no desafio

> Resoluções e períodos aproximados. Confirmar nos produtos exatos escolhidos **[verificar]**.

| Dataset | Variáveis úteis | Resolução espacial | Resolução temporal | Período | Uso no projeto |
|---|---|---|---|---|---|
| **NASA POWER** | Temperatura (T2M, T2M_MAX, T2M_MIN), precipitação (PRECTOTCORR), umidade relativa (RH2M), vento (WS2M), radiação solar (ALLSKY_SFC_SW_DWN), umidade do solo (GWETTOP, GWETROOT, GWETPROF) | ~0,5° × 0,625° (meteorologia, MERRA-2); ~1° (solar) | Horária, diária, mensal, climatologia | 1981– (meteorologia) | **Base do MVP.** Clima histórico, GDD, geada, calor, ET0, balanço hídrico. API simples por ponto, sem login. |
| **SMAP** | Umidade do solo superficial (L3, ex.: SPL3SMP_E) e zona radicular (L4, SPL4SMGP) | 9 km (L3 enhanced, L4) | Diária (L3), 3-horária (L4) | 2015– | Anomalias de umidade, secas agrícolas, padrão sazonal de água no solo. |
| **ECOSTRESS** | Temperatura da superfície (LST), evapotranspiração (ET), índice de estresse evaporativo (ESI) | ~70 m | Irregular (a bordo da ISS), revisita de dias | 2018– | Estresse térmico/hídrico em escala de talhão. |
| **GPM (IMERG)** | Precipitação | 0,1° (~10 km) | 30 min, diária, mensal | 2000– | Padrão de chuva, chuva extrema, mudança de sazonalidade. |
| **Landsat (5/7/8/9)** | Reflectância → NDVI/EVI/NDMI, LST térmico | 30 m (térmico 100 m reamostrado) | 16 dias por satélite (~8 dias com L8+L9) | 1984– (TM); 1972– (MSS) | Fenologia do talhão, períodos de solo descoberto, histórico longo. **HLS** (Harmonized Landsat Sentinel-2): 30 m, revisita ~2–3 dias. |
| **MODIS (Terra/Aqua)** | NDVI/EVI (MOD13Q1), ET (MOD16A2), LST (MOD11A2), cobertura do solo (MCD12Q1) | 250 m (NDVI), 500 m (ET), 1 km (LST) | 16 dias (NDVI), 8 dias (ET/LST) | 2000– | Séries temporais longas e limpas de vegetação/ET; detecção de safras e períodos de solo nu em escala regional. |
| **GRACE / GRACE-FO** | Anomalia de armazenamento de água terrestre (TWS) | ~300 km efetiva (mascons ~0,5° como produto) | Mensal | 2002–2017 (GRACE); 2018– (GRACE-FO); lacuna 2017–2018 | Tendência de longo prazo de água regional/subterrânea. Escala grossa: usar como contexto regional, nunca no nível de talhão. |
| **SRTM / NASADEM** | Elevação → declividade, aspecto, fator LS, acúmulo de fluxo | 30 m | Estática (2000) | — | Risco de erosão, áreas de acúmulo de ar frio (geada), drenagem. |
| **GEDI** | Altura de dossel, biomassa acima do solo | Pegadas de ~25 m (amostral, não contínuo) | Amostral | 2019–2023 (com retomada posterior **[verificar]**); só entre ~51,6° N e S | Opcional; biomassa/estrutura de vegetação. Pouco relevante para MVP agrícola. |

### 6.2 Dados complementares (não NASA)
| Tipo | Fontes sugeridas | Observação |
|---|---|---|
| Solo (textura, carbono orgânico, pH, densidade, CTC) | **SoilGrids (ISRIC)** global 250 m; **SSURGO/gNATSGO** (EUA); **Embrapa / PronaSolos** (Brasil) | SoilGrids tem API REST por ponto. |
| Uso e cobertura do solo / culturas | **USDA Cropland Data Layer** (EUA, 30 m, anual); **MapBiomas** (Brasil, 30 m, anual); ESA WorldCover (10 m) | Inferir rotação histórica do talhão quando o usuário não souber. |
| Parâmetros de culturas | **FAO-56** (Kc, duração das fases, profundidade radicular); **FAO ECOCROP** (faixas de temperatura/chuva/pH); literatura de extensão rural (Embrapa, USDA NRCS) | Montar tabela própria `culturas.csv`. |
| Estações meteorológicas (validação) | INMET (Brasil), NOAA GHCN-Daily (EUA) | Para comparar satélite × solo (D9). |
| Mercado / preços | CONAB, CEPEA (Brasil); USDA NASS (EUA) | Opcional; maior lacuna de dados. |

### 6.3 Formas de acesso
| Ferramenta | Para quê |
|---|---|
| **NASA POWER API** (`https://power.larc.nasa.gov/api/temporal/{hourly,daily,monthly,climatology}/point`) | Séries por ponto em JSON/CSV, sem login. Parâmetro `community=AG`. |
| **NASA Earthdata Login** | Conta gratuita necessária para baixar a maioria dos produtos (SMAP, ECOSTRESS, GPM, MODIS, HLS). |
| **AppEEARS** (LP DAAC) | Extração de séries temporais por ponto/polígono de MODIS, Landsat/HLS, SMAP, ECOSTRESS, SRTM sem baixar cenas inteiras. Muito útil em hackathon (tem API; pedidos são assíncronos e podem demorar). |
| **`earthaccess`** (Python) | Busca e download programático de produtos Earthdata. |
| **NASA CMR / CMR-STAC** | Catálogo/busca de granulos. |
| **Giovanni** (GES DISC) | Visualização e séries temporais rápidas de GPM, MERRA-2 etc. via web. |
| **Google Earth Engine** | Catálogo com Landsat, MODIS, SMAP, GPM, SRTM, GRACE já processados; processamento na nuvem (requer conta). |
| **Worldview** (NASA) | Visualização rápida de imagens para demo/screenshot. |
| **SoilGrids REST API** | Propriedades de solo por ponto. |

> **Recomendação para 48 h:** pré-baixar e cachear os dados de 1–3 regiões de demonstração. Chamadas ao vivo a AppEEARS/Earthdata podem ser lentas ou falhar na apresentação.

---

## 7. Indicadores derivados (features)

> **Atualização (14/11/2026, D-009 em `DECISOES.md`):** esta seção é o levantamento inicial. As fontes que o projeto usa de fato são as do núcleo em `tools/` (NASA POWER, GPM IMERG, MODIS NDVI, HLS, SRTM, GLDAS, SMAP L4, ERA5, FAO GAEZ, SoilGrids, MapBiomas, ZARC, INMET/CEMADEN, IBGE PAM, Earthdata Search, earthaccess e AppEEARS), mais as opcionais em `tools/extras/` (FIRMS, Sentinel-1 e Embrapa Solos). As demais fontes citadas aqui ficaram fora do MVP.

Calcular por local, por mês (ou semana) do ano, com climatologia (ex.: 1991–2020 ou o período disponível) e tendência recente.

| Indicador | Fórmula / método | Fonte | Para que serve |
|---|---|---|---|
| Normal climática mensal | Média de T, P por mês | POWER | Calendário agrícola, janelas de plantio |
| Tendência | Sen's slope + teste de Mann-Kendall nas séries anuais | POWER, GPM, GRACE | "Está ficando mais quente/seco?" |
| Graus-dia (GDD) | `Σ max(0, (Tmax+Tmin)/2 − Tbase)` | POWER | Viabilidade de ciclo por cultura |
| Risco de geada | `P(Tmin ≤ 0 °C)` por semana/mês; datas de última/primeira geada | POWER (+ relevo SRTM para baixadas) | Janela de plantio, culturas sensíveis |
| Dias de calor extremo | Contagem `Tmax > limiar_cultura` por mês | POWER, ECOSTRESS LST | Vulnerabilidade sazonal |
| ET0 | Penman-Monteith FAO-56 (ou Hargreaves se faltar dado) | POWER | Demanda hídrica |
| Demanda da cultura | `ETc = Kc(fase) × ET0` | POWER + FAO-56 | Uso de água por estratégia |
| Balanço hídrico | `P_efetiva − ETc` por mês, acumulado no ciclo | POWER/GPM | Déficit/necessidade de irrigação |
| Índice de seca | SPI (3/6 meses) ou SPEI | POWER/GPM | Frequência de seca |
| Anomalia de umidade do solo | z-score vs. climatologia do mês | SMAP, POWER GWET* | Estresse hídrico, período crítico |
| Chuva extrema | Dias > p95 local ou > 50 mm | GPM | Risco de erosão e encharcamento |
| Fenologia / solo descoberto | Séries NDVI suavizadas (ex.: Savitzky-Golay); meses com `NDVI < ~0,2–0,25` = solo nu | Landsat/HLS, MODIS | Janelas para cobertura (D1) |
| Estresse de vegetação | Anomalia de NDVI/EVI vs. climatologia; ESI | MODIS, ECOSTRESS | Estações vulneráveis (D2) |
| Risco de erosão | Aproximação RUSLE: `A = R × K × LS × C × P` — R de chuva (GPM), K de textura/carbono (SoilGrids), LS de declividade (SRTM), C por estratégia (cobertura ao longo do ano) | GPM, SoilGrids, SRTM | Comparar estratégias; mapa intra-talhão (D5) |
| Tendência hídrica regional | Inclinação da anomalia TWS | GRACE/GRACE-FO | Contexto de escassez de água |

---

## 8. Modelo de dados sugerido

### 8.1 Cultura (`culturas.csv` / JSON)
```yaml
id: "sorgo_granifero"
nome: "Sorgo granífero"
familia_botanica: "Poaceae"          # para regra de quebra de ciclo de pragas
tipo: ["comercial", "tolerante_seca"] # comercial | cobertura | forrageira | fixadora_n | raiz_profunda | tolerante_seca
ciclo_dias: [100, 130]
temp_otima_c: [25, 32]
temp_min_crescimento_c: 10
temp_base_gdd_c: 10
sensivel_geada: true
tmax_critico_florescimento_c: 38
demanda_agua_ciclo_mm: [400, 600]
kc: { inicial: 0.35, medio: 1.0, final: 0.55 }   # FAO-56
profundidade_raiz_m: 1.5
fixa_nitrogenio: false
aporte_biomassa: "alto"               # baixo | medio | alto  (proxy de matéria orgânica)
cobertura_solo: "media"               # efeito no fator C da erosão
valor_forrageiro: "medio"
pragas_doencas_principais: ["lagarta-do-cartucho"]
ph_ideal: [5.5, 7.5]
textura_preferida: ["média", "argilosa"]
equipamento: ["plantadeira_graos", "colhedora_graos"]
fontes: ["FAO ECOCROP", "Embrapa"]
confianca_parametros: "media"
```

### 8.2 Entrada do agricultor
```yaml
local: { tipo: "ponto" | "poligono", geometria: GeoJSON }
rotacao_atual:
  - { cultura: "milho", inicio_mes: 10, fim_mes: 2 }
  - { cultura: null, inicio_mes: 3, fim_mes: 9 }   # pousio / solo descoberto
irrigacao: "nenhuma" | "parcial" | "total"
agua_disponivel: "baixa" | "media" | "alta"
equipamentos: ["trator", "plantadeira_graos"]
culturas_excluidas: ["algodao"]
mercados_acessiveis: ["graos", "leite"]
prioridades (pesos 0–5):
  economizar_agua: 5
  renda_extra: 3
  melhorar_solo: 4
  reduzir_erosao: 4
  forragem: 1
  quebrar_pragas: 2
```

### 8.3 Saída por estratégia
```yaml
nome: "Milho + cobertura de inverno (aveia + ervilhaca)"
sequencia: [...]
eh_atual: false
pontuacao_total: 0.0–1.0
pontuacao_por_criterio:
  uso_agua: ...
  saude_solo: ...
  erosao: ...
  pragas: ...
  renda: ...
  forragem: ...
viabilidade_climatica: { gdd_ok: true, risco_geada: "baixo", risco_calor: "medio", deficit_hidrico_mm: 120 }
por_que_sugerida: "texto curto ligado aos dados"
evidencias: [{ indicador, valor, periodo, fonte_dataset }]
beneficios: [...]
lacunas_informacao: [...]
riscos_revisao_local: [...]
confianca: "alta" | "media" | "baixa"
```

---

## 9. Abordagem de modelagem recomendada

### 9.1 Princípio
**Explicável primeiro.** Um sistema de regras + análise multicritério transparente, alimentado por indicadores calculados dos dados NASA, é mais defensável (e mais alinhado ao desafio) do que um modelo "caixa-preta". IA entra para detectar padrões e para redigir explicações, sempre ancorada nos números calculados.

### 9.2 Pipeline

> **Atualização (14/11/2026, D-009 em `DECISOES.md`):** esta seção é o levantamento inicial. As fontes que o projeto usa de fato são as do núcleo em `tools/` (NASA POWER, GPM IMERG, MODIS NDVI, HLS, SRTM, GLDAS, SMAP L4, ERA5, FAO GAEZ, SoilGrids, MapBiomas, ZARC, INMET/CEMADEN, IBGE PAM, Earthdata Search, earthaccess e AppEEARS), mais as opcionais em `tools/extras/` (FIRMS, Sentinel-1 e Embrapa Solos). As demais fontes citadas aqui ficaram fora do MVP.
1. **Ingestão**: buscar séries por local (POWER, SMAP, GPM, NDVI via MODIS/HLS, SRTM, GRACE, SoilGrids).
2. **Harmonização**: agregar tudo para **passo mensal** (ou semanal) e para o **ponto/polígono do talhão** (valor do pixel que contém o ponto ou média ponderada por área). Registrar a resolução original de cada variável para comunicar incerteza.
3. **Features**: calcular indicadores da seção 7 (climatologia + tendência + anomalias).
4. **Diagnóstico**: detectar períodos de solo descoberto, meses de maior vulnerabilidade, tendências relevantes.
5. **Geração de candidatas**: a partir de uma biblioteca de culturas, montar sequências que (a) cabem nas janelas climáticas (GDD, geada, calor, água), (b) respeitam restrições do usuário (equipamento, mercado, exclusões), (c) preenchem janelas de solo descoberto, (d) alternam famílias botânicas.
6. **Filtro de viabilidade** (regras duras): descartar o que não fecha ciclo, tem risco de geada alto em fase sensível, ou excede água disponível.
7. **Pontuação multicritério (MCDA)**: cada critério normalizado 0–1; soma ponderada pelos pesos do agricultor (ou TOPSIS). Sempre incluir a rotação atual na comparação como linha de base.
8. **Seleção**: atual + top-N (N ≥ 2) mais diversas entre si (evitar 3 variações da mesma ideia).
9. **Explicação**: gerar justificativa/evidência/benefícios/lacunas/riscos a partir de templates preenchidos com os indicadores; opcionalmente um LLM reescreve em linguagem simples, **sem inventar números**.
10. **Incerteza**: atribuir confiança por estratégia com base em: resolução dos dados, tamanho do histórico, confiança dos parâmetros da cultura, dispersão entre fontes (ex.: chuva POWER vs. GPM), sensibilidade da pontuação a mudanças de peso.

### 9.3 Técnicas de IA/estatística possíveis (para D10)
| Técnica | Uso | Explicabilidade |
|---|---|---|
| Climatologia + anomalias (z-score) | Detectar meses anômalos | Alta |
| Decomposição STL / suavização Savitzky-Golay | Separar sazonalidade/tendência; fenologia NDVI | Alta |
| Mann-Kendall + Sen's slope | Tendências significativas | Alta |
| Clustering (k-means) de perfis mensais | Agrupar anos "secos/quentes/normais" ou zonas do talhão | Média |
| Detecção de mudança (BFAST, change point) | Transições sazonais, mudanças de regime | Média |
| Random Forest / Gradient Boosting + SHAP | Prever NDVI/estresse a partir do clima; mostrar fatores | Média (com SHAP) |
| MCDA (soma ponderada, AHP, TOPSIS) | Ranquear estratégias por prioridades | Alta |
| LLM com contexto estruturado | Explicar em linguagem simples, responder perguntas do agricultor | Depende de ancoragem nos dados |

### 9.4 Cenários (D7)
Aplicar deltas às séries climáticas (ex.: `P × (1 − 0,2)`, `T + 2 °C`), recalcular indicadores e pontuações, e mostrar como o ranking das estratégias muda. Deixar claro que é um teste de sensibilidade, não uma previsão.

---

## 10. Interface e UX

### Telas sugeridas
1. **Onde fica seu campo?** — mapa com busca/clique/desenho.
2. **O que você planta hoje?** — calendário visual de 12 meses com blocos arrastáveis por cultura.
3. **O que é mais importante para você?** — sliders/ícones de prioridades + restrições.
4. **Raio-x do seu campo** — cartões simples: "Seu campo fica sem cobertura de maio a setembro", "Janeiro ficou mais quente nos últimos 10 anos", "Chuva forte em dezembro aumenta risco de erosão na parte inclinada". Cada cartão com "de onde vem esse dado?" e "o que isso significa?".
5. **Comparar estratégias** — 3+ colunas lado a lado, ícones/semáforo por critério, calendário de cada rotação, selo de confiança.
6. **Detalhe da estratégia** — por que, evidência, benefícios, lacunas, riscos, perguntas para levar ao técnico.
7. **Mapa e linha do tempo (extra)** — camadas NDVI, umidade, risco de erosão, geada; slider temporal.
8. **Simulador (extra)** — sliders de chuva/temperatura.

### Diretrizes
- Linguagem do agricultor; termos técnicos com tooltip de uma frase.
- Ícones e cores consistentes (água = azul, solo = marrom, calor = vermelho, geada = azul-claro).
- Evitar mapas e gráficos densos na tela principal; detalhe sob demanda.
- Funcionar bem em celular.
- Rótulo fixo/visível: "Sugestões para discussão. Confirme com seu técnico agrícola e com sua experiência."
- Destacar onde o julgamento humano é crítico: mercado/preço, pragas locais, logística, sementes disponíveis, legislação, crédito/seguro agrícola.
- Suporte a idioma do usuário (PT/EN; ES opcional).

---

## 11. Limitações, lacunas e riscos (devem aparecer no produto e no pitch)

- **Escala:** SMAP (9 km), GPM (~10 km), POWER (~50 km) e GRACE (~300 km) são muito maiores que um talhão. Variações locais (microclima, baixadas, irrigação) não são capturadas.
- **Nuvens e lacunas:** imagens ópticas (Landsat/MODIS) têm falhas em períodos nublados; ECOSTRESS tem revisita irregular; GRACE tem lacuna 2017–2018.
- **Histórico curto** para alguns produtos (SMAP 2015–, ECOSTRESS 2018–) limita climatologias.
- **Parâmetros de culturas genéricos:** variedades locais diferem; Kc e limiares são aproximados.
- **Não observável por satélite:** pragas e doenças locais, preços/mercado, mão de obra, equipamento, regras de crédito/seguro, preferências culturais e conhecimento tradicional.
- **Dados de solo modelados** (SoilGrids) podem diferir muito da análise de solo real; recomendar análise laboratorial.
- **Mudança climática futura:** dados históricos não garantem o futuro; cenários são de sensibilidade.
- **Risco ético:** recomendação errada pode custar uma safra. A ferramenta deve comunicar confiança e nunca soar prescritiva.

---

## 12. Submissão e avaliação no Space Apps

> **[verificar]** regras e critérios exatos da edição 2026 no site oficial.

Historicamente, a submissão no Space Apps inclui:
- Página do projeto com **título**, **resumo** e descrição detalhada (o que faz, como funciona, benefícios, ferramentas usadas, **dados da NASA usados**, outros dados/recursos usados, uso de IA).
- **Demo**: vídeo curto (~30 s) **ou** apresentação curta (até ~7 slides).
- **Link final do projeto** (repositório/app).

Critérios de avaliação historicamente usados: **Impacto**, **Criatividade**, **Validade (técnica/científica)**, **Relevância** (aderência ao desafio e uso de dados NASA) e **Apresentação**.

Implicações para o projeto:
- Citar explicitamente cada dataset NASA usado e para quê.
- Mostrar um caso real concreto do início ao fim.
- Declarar como IA foi usada (no produto e no desenvolvimento), se exigido.
- Demonstrar honestidade sobre incerteza e limitações (pesa em validade).

---

## 13. Escopo sugerido para o MVP (hackathon)

> **Atualização (14/11/2026, D-009 em `DECISOES.md`):** esta seção é o levantamento inicial. As fontes que o projeto usa de fato são as do núcleo em `tools/` (NASA POWER, GPM IMERG, MODIS NDVI, HLS, SRTM, GLDAS, SMAP L4, ERA5, FAO GAEZ, SoilGrids, MapBiomas, ZARC, INMET/CEMADEN, IBGE PAM, Earthdata Search, earthaccess e AppEEARS), mais as opcionais em `tools/extras/` (FIRMS, Sentinel-1 e Embrapa Solos). As demais fontes citadas aqui ficaram fora do MVP.

**Mínimo demonstrável:**
1. Entrada: ponto no mapa + rotação atual + 3–5 sliders de prioridade.
2. Dados: **NASA POWER** (clima diário/mensal 1981–) + **MODIS NDVI** ou **HLS NDVI** para 1 região de demo pré-processada + **SRTM** (declividade) + **SoilGrids** (textura/carbono).
3. Indicadores: climatologia mensal, tendência de temperatura/chuva, risco de geada, dias de calor, ET0/balanço hídrico, períodos de solo descoberto, declividade.
4. Biblioteca de ~10–15 culturas com parâmetros básicos.
5. Motor de regras + MCDA gerando **3 estratégias** (atual + 2), com os 5 blocos de explicação e nível de confiança.
6. UI simples (web responsiva) com tela de comparação e aviso de apoio à decisão.

**Se sobrar tempo:** SMAP (anomalias de umidade), GPM (chuva extrema), GRACE (tendência regional), ECOSTRESS (estresse em talhão), mapa de erosão intra-talhão, simulador de cenário, LLM para perguntas em linguagem natural.

**Exemplo de chamada NASA POWER (mensal, ponto):**
```
https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,GWETROOT&community=AG&longitude=-47.9&latitude=-15.8&start=2005&end=2024&format=JSON
```
**[verificar]** nomes de parâmetros e limites de datas na documentação da API antes de usar.

---

## 14. Exemplo de saída esperada (referência de formato)

**Local:** Cerrado, GO (exemplo). **Rotação atual:** soja (out–fev) → pousio (mar–set).

| | A) Atual: soja → pousio | B) Soja → milheto (cobertura) | C) Soja → milho safrinha + braquiária consorciada |
|---|---|---|---|
| Uso de água | Baixo | Baixo (milheto tolera seca) | Médio-alto (risco de déficit em abr–mai) |
| Saúde do solo | Piora (7 meses descoberto) | Melhora (biomassa, raiz) | Melhora muito (palhada + raiz de braquiária) |
| Erosão | Alta no início das chuvas | Baixa | Baixa |
| Pragas | Ciclo da soja contínuo | Quebra parcial | Quebra parcial |
| Renda | Base | +pouco (palhada/grão opcional) | +safrinha +forragem |
| Confiança | Alta | Média | Média (depende de chuva tardia) |

**Estratégia B — explicação:**
- **Por que:** o NDVI (MODIS 2001–2024) fica abaixo de 0,25 de abril a setembro na maioria dos anos → solo descoberto por ~6 meses; a chuva de outubro–novembro cai em solo nu.
- **Evidência:** NDVI MODIS MOD13Q1; precipitação mensal NASA POWER/GPM; declividade SRTM.
- **Benefícios:** cobertura do solo, menos erosão no início das chuvas, mais palha para o plantio direto da soja.
- **Lacunas:** sem dados locais de pragas; disponibilidade de sementes de milheto não verificada.
- **Riscos para revisão local:** semeadura tardia pode não estabelecer se as chuvas pararem cedo; confirmar manejo de dessecação com o técnico.

*(Valores e afirmações acima são ilustrativos de formato, não resultados reais.)*

---

## 15. Glossário rápido

| Termo | Significado |
|---|---|
| AppEEARS | Ferramenta NASA para extrair séries de satélite por ponto/área. |
| Balanço hídrico | Chuva − evapotranspiração (− escoamento). |
| Cover crop | Planta de cobertura. |
| ECOSTRESS | Sensor na ISS: temperatura de superfície e ET a ~70 m. |
| ET0 / ETc / ETa | Evapotranspiração de referência / da cultura / real. |
| GDD | Graus-dia de crescimento. |
| GPM / IMERG | Missão/produto de precipitação global. |
| GRACE / GRACE-FO | Satélites que medem variação de água armazenada (gravimetria). |
| HLS | Harmonized Landsat Sentinel-2 (30 m, revisita frequente). |
| Kc | Coeficiente de cultura (FAO-56). |
| LST | Land Surface Temperature (temperatura da superfície). |
| MCDA | Análise de decisão multicritério. |
| MODIS | Sensor dos satélites Terra/Aqua, imagens diárias de 250 m–1 km. |
| NASA POWER | Serviço de dados meteorológicos/solares por ponto, voltado a agricultura e energia. |
| NDVI / EVI / NDMI | Índices de vegetação / umidade da vegetação. |
| RUSLE | Equação de perda de solo (erosão). |
| SMAP | Satélite de umidade do solo. |
| SoilGrids | Mapas globais de propriedades do solo (ISRIC). |
| SPI / SPEI | Índices padronizados de seca. |
| SRTM / NASADEM | Modelos digitais de elevação (30 m). |
| TWS | Terrestrial Water Storage (armazenamento total de água). |
