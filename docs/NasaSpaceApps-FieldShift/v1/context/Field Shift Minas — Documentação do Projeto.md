# Field Shift Minas — Documentação do Projeto

Nov 13, 2026 · @Gui

## Visão geral

Vamos construir uma ferramenta de apoio à decisão que compara pelo menos três estratégias de rotação de culturas para produtores de Minas Gerais, usando observações da NASA, dados de solo, características das culturas e as prioridades do produtor.

O desafio é o **Field Shift: Adapting Farms with NASA Data**, do NASA Space Apps Challenge 2026. Ele parte de um problema concreto: temperaturas mudando, chuvas menos previsíveis, falta de água, eventos extremos e solos se degradando tornam difícil escolher uma rotação que proteja o campo, economize água e dê resiliência no longo prazo.

A ferramenta não substitui o produtor nem o agrônomo. Ela mostra padrões e possibilidades, explica de onde vem cada sugestão e aponta o que precisa de validação local.

## Escopo: Minas Gerais

O foco é o estado de Minas Gerais como um todo, não uma única fazenda ou região.

Isso vira um diferencial: Minas tem regiões com clima, relevo e solo muito diferentes, então a mesma ferramenta deve gerar recomendações diferentes para lugares diferentes. Mostrar isso com dados é a forma mais clara de provar que a ferramenta responde às condições locais.

O foco em Minas tem duas consequências práticas:

- só os datasets globais da lista do desafio servem; os exclusivos dos EUA ficam de fora (ver *Lacunas*);
- onde a cultura principal é perene, como o café, "rotação" vira cobertura nas entrelinhas e manejo do solo, não troca de cultura. A ferramenta trata esse caso à parte.

## Objetivos do desafio e como atendemos

Cada pedido do texto do desafio tem uma parte correspondente na ferramenta.

| O que o desafio pede | Como a ferramenta atende |
| --- | --- |
| Comparar pelo menos três estratégias, incluindo a rotação atual | Tela de comparação com a rotação atual + duas alternativas, lado a lado |
| Explicar por que cada estratégia foi sugerida, com evidências | Cartão de cada estratégia lista a justificativa e os dados que a apoiam |
| Mostrar benefícios, lacunas de informação e riscos | Campos fixos no cartão: benefícios, lacunas, riscos para revisão local |
| Destacar quando o campo fica descoberto | Calendário de cobertura a partir da série de NDVI |
| Mostrar estações em que a cultura atual é mais vulnerável | Indicadores de calor, geada, déficit hídrico e chuva extrema por mês |
| Considerar prioridades do produtor | Sliders: água, solo, nitrogênio, erosão, forragem, renda |
| Explicar termos científicos | Glossário em linguagem simples (NDVI, evapotranspiração, anomalia de umidade, balanço hídrico) |
| Mostrar incerteza e onde a expertise local é necessária | Nível de confiança por indicador e avisos de validação em cada recomendação |
| Harmonizar dados de resoluções diferentes | Grade comum de análise (ver *Metodologia*) |

## Fontes de dados para Minas

Treze datasets da lista do desafio têm cobertura global e servem para Minas. As descrições abaixo seguem o texto do desafio; resoluções e cobertura de cada um devem ser confirmadas nas páginas oficiais antes do uso.

| Dataset | O que fornece | Uso na ferramenta |
| --- | --- | --- |
| NASA POWER | Temperatura, umidade, radiação e indicadores agroclimáticos | Série climática base, risco de geada, estação de cultivo, demanda hídrica |
| GPM IMERG | Taxa e acumulado de precipitação | Regularidade da chuva, eventos extremos, risco de erosão |
| SMAP | Umidade do solo superficial, a cada 2–3 dias | Estresse hídrico, disponibilidade de água, infiltração |
| ECOSTRESS | Temperatura de superfície e evapotranspiração em alta resolução | Pontos de calor e de estresse hídrico, demanda de água da cultura |
| Landsat (30 m) | Reflectância, NDVI, índices de vegetação | Vigor da cultura, solo descoberto, transições de estação |
| MODIS/VIIRS (250–1000 m) | NDVI e índices de vegetação | Séries longas de vegetação em escala regional |
| Sentinel-2 (10–20 m) | Imagens multiespectrais com bandas para vegetação | NDVI/EVI e solo descoberto no nível do talhão |
| GRACE e GRACE-FO | Tendência de água armazenada | Contexto de longo prazo da disponibilidade hídrica no estado |
| SRTM | Elevação | Declividade, escoamento, risco de erosão, baixadas sujeitas a geada |
| GLDAS | Temperatura, chuva, umidade do solo, radiação em séries contínuas | Início de secas, déficits de umidade, transições de estação |
| ERA5 | Variáveis climáticas horárias, incluindo temperatura do solo | Preencher lacunas e reforçar séries históricas |
| FAO GAEZ | Aptidão agroclimática por cultura, restrições de solo, água disponível | Checar se a cultura sugerida é adequada ao clima e solo do local |
| GEDI | Biomassa e estrutura da vegetação | Contexto da paisagem ao redor das lavouras |

## Lacunas de dados e como tratamos

Doze datasets da lista cobrem só os EUA e ficam fora: Web Soil Survey, SSURGO/STATSGO2, CDL (CropScape), PRISM, NAIP, NLCD, CoCoRaHS, NWIS, USDA AMS Market News, NASS QuickStats, OpenET e LANDFIRE. O USDA Ag Data Commons deve ser verificado caso a caso, pois pode ter algum estudo aplicável.

Isso abre quatro lacunas, que a ferramenta mostra em vez de esconder:

| Lacuna | O que perdemos | Como tratamos |
| --- | --- | --- |
| Solo detalhado do talhão | Textura, matéria orgânica, drenagem e erodibilidade no nível do campo (SSURGO) | Usar restrições de solo do GAEZ e permitir que o produtor informe o tipo de solo ou resultados de análise |
| Histórico de culturas plantadas | Rotação real por ano (CDL) | O produtor informa a rotação atual; o calendário de NDVI ajuda a conferir |
| Mercado e preços | Preços e demanda por cultura (AMS, QuickStats) | O produtor indica quais culturas têm mercado para ele; a ferramenta não estima preço |
| Validação em solo | Chuva medida em campo e poços (CoCoRaHS, NWIS) | Comparar fontes de satélite e reanálise entre si e marcar a confiança de cada indicador |

O próprio desafio pede para mostrar lacunas e pontos de validação local, então tratá-las abertamente conta a favor.

## Estrutura da ferramenta

O uso segue quatro etapas, do panorama do estado até a comparação das estratégias para um local.

&#91;embedded content: fluxo da ferramenta · 4 etapas e os dados de cada uma\]

As etapas 1 e 2 usam dados de satélite e reanálise; a etapa 3 depende do que o produtor informa; a etapa 4 combina tudo nas notas e no nível de confiança.

## Metodologia

A recomendação sai de uma pontuação transparente, com regras e pesos visíveis, em vez de um modelo caixa-preta.

**1. Harmonização dos dados.** Os datasets têm resoluções muito diferentes, de 10 m (Sentinel-2) a centenas de km (GRACE). Como o desafio sugere, reamostramos e agregamos tudo para uma grade comum e para passos de tempo mensais. Cada indicador guarda a resolução de origem, para a ferramenta avisar quando um valor é regional e não do talhão.

**2. Indicadores por local e mês.** A partir da grade, calculamos indicadores como: temperatura máxima e mínima, risco de geada, chuva acumulada e eventos extremos, anomalia de umidade do solo, evapotranspiração, NDVI (cobertura e solo descoberto), declividade e tendência de água armazenada.

**3. Pontuação das estratégias.** Cada estratégia recebe uma nota por critério: uso de água, melhoria do solo, fixação de nitrogênio, redução de erosão, forragem e renda. As regras ligam indicadores a critérios; por exemplo, declividade alta + chuva extrema aumentam o peso de culturas que cobrem o solo. Os sliders do produtor definem os pesos da nota final.

**4. Incerteza.** Cada indicador recebe um nível de confiança (alto, médio, baixo) conforme a resolução, a extensão da série e a concordância entre fontes; por exemplo, chuva do GPM comparada com POWER, GLDAS e ERA5. Quando a confiança é baixa, o cartão da estratégia diz isso e indica o que validar com o agrônomo.

**Por que não um modelo caixa-preta:** sem dados locais de produtividade e rotação para treinar, um modelo complexo seria difícil de validar. Regras explícitas permitem explicar cada recomendação, que é o que o desafio pede.

## Comparação das estratégias

A tela principal mostra três estratégias lado a lado: a rotação atual do produtor e duas alternativas geradas pela ferramenta.

As alternativas partem de quatro famílias de culturas que o desafio cita, escolhidas conforme os indicadores do local:

- **Fixadoras de nitrogênio** (leguminosas): reduzem a necessidade de adubo nitrogenado;
- **Culturas de cobertura**: protegem o solo nos períodos em que ele ficaria descoberto e reduzem erosão;
- **Raiz profunda**: melhoram a estrutura do solo e a infiltração;
- **Tolerantes à seca**: reduzem a demanda de água onde o déficit hídrico é recorrente.

Cada estratégia tem um cartão com os mesmos campos:

| Campo | O que mostra |
| --- | --- |
| Por que foi sugerida | Os indicadores do local que motivaram a escolha |
| Evidências | Quais dados sustentam a sugestão, com o nível de confiança |
| Benefícios | Notas por critério: água, solo, nitrogênio, erosão, forragem, renda |
| Lacunas | O que não sabemos (solo detalhado, mercado, histórico) |
| Riscos para revisão local | O que o produtor ou agrônomo precisa conferir: doenças, mercado, calendário, maquinário |

Quais culturas específicas entram em cada família para Minas ainda precisa ser definido pela equipe, com apoio do GAEZ para checar a aptidão.

## Design centrado no produtor

A ferramenta precisa ser usada por quem tem pouca experiência com tecnologia ou mapas.

- **Linguagem simples:** cada termo técnico tem uma explicação curta ao lado (por exemplo, NDVI como "medida de quão verde e vigorosa está a vegetação").
- **Entradas do produtor:** rotação atual, prioridades, disponibilidade de água ou irrigação, maquinário e culturas com mercado para ele.
- **Poucos números, mais comparação:** notas visuais por critério e um resumo de uma frase por estratégia.
- **Diferença entre satélite e campo:** explicar que satélites medem grandes áreas de forma indireta e que medições locais ajudam a confirmar.
- **Avisos de validação:** cada recomendação lembra que a decisão final é do produtor e destaca onde o julgamento humano é mais importante.

## Regiões de demonstração (em debate)

A proposta é demonstrar a ferramenta em três ou quatro pontos de regiões bem diferentes do estado, para mostrar recomendações que mudam conforme o local.

| Região candidata | O que queremos mostrar com os dados |
| --- | --- |
| Triângulo / Alto Paranaíba | Rotação de grãos e a janela de solo descoberto na seca |
| Norte de Minas | Déficit hídrico e culturas tolerantes à seca |
| Sul de Minas | Café perene: cobertura nas entrelinhas |
| Zona da Mata | Relevo acidentado e risco de erosão |

As características de cada região são hipóteses de partida. Elas precisam ser confirmadas pelos dados (NDVI, POWER, SMAP, SRTM) antes de entrar na apresentação.

## Questões em aberto

- [ ] Tecnologia e formato do protótipo (adaptar o app em Streamlit com NASA POWER ou outra stack) — em debate na equipe
- [ ] Quais regiões entram na demonstração
- [ ] Quais culturas específicas compõem cada família de estratégia em Minas
- [ ] Tamanho da grade comum de análise e período histórico usado
- [ ] Pesos padrão dos critérios antes de o produtor ajustar
- [ ] Verificar no USDA Ag Data Commons se há estudos aplicáveis a Minas
- [ ] Confirmar nas páginas oficiais a resolução e a cobertura de cada dataset

*Base deste documento: texto do desafio Field Shift e descrições dos datasets da lista de recursos do desafio.*
