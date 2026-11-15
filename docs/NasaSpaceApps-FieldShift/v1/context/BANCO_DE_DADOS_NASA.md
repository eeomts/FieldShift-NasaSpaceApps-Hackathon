# Banco de Dados NASA — Field Shift Brasil

Referência dos dados e ferramentas usados no desafio **Field Shift: Adapting Farms with NASA Data** (NASA Space Apps Challenge 2026), com escopo no Brasil inteiro. A lista segue a decisão D-009 em `DECISOES.md`: só entram as fontes que têm um papel que nenhuma outra cobre. Cada uma tem uma nota própria em `tools/` (núcleo) ou `tools/extras/` (opcionais).

> **Atenção:** resoluções, cobertura e links devem ser confirmados nas páginas oficiais antes do uso.

> **Dados usados na versão atual do app (15/11/2026):** NASA POWER (clima), SRTM (relevo) e SoilGrids (solo). A umidade do solo (SMAP L4, GLDAS), o NDVI (MODIS, VIIRS, HLS) e a chuva de satélite (GPM IMERG) ficaram fora desta versão, e o AppEEARS foi descartado em 15/11/2026 (ver D-009 em `DECISOES.md`). As tabelas abaixo são o levantamento e o plano: a coluna "Uso na ferramenta" diz o que cada dataset poderia fazer, não o que o app faz hoje.

---

## 1. Datasets da NASA da lista do desafio (cobertura global)

| Dataset | O que fornece | Uso na ferramenta |
| --- | --- | --- |
| NASA POWER | Temperatura, umidade, radiação e indicadores agroclimáticos | Série climática base, risco de geada, estação de cultivo, demanda hídrica |
| GPM IMERG | Taxa e acumulado de precipitação | Regularidade da chuva, veranicos, eventos extremos, risco de erosão |
| MODIS/VIIRS (250–1000 m) | NDVI e índices de vegetação | Séries longas de vegetação no panorama nacional |
| SRTM | Elevação | Declividade, escoamento, risco de erosão, baixadas sujeitas a geada |
| GLDAS | Temperatura, chuva, umidade do solo e radiação em séries contínuas | Início de secas, déficits de umidade, transições de estação |

## 2. Datasets complementares da NASA

| Dataset | Por que usar |
| --- | --- |
| SMAP L4 (umidade da zona radicular) | Estima a umidade até cerca de 1 m, que é o que a raiz usa, em 9 km e sem buracos entre passagens. Substitui o SMAP de superfície no projeto. |
| HLS (Harmonized Landsat Sentinel-2) | Landsat e Sentinel-2 já harmonizados em 30 m, com revisita de 2 a 3 dias. É a fonte do talhão: calendário de cobertura e solo descoberto. |

## 3. Ferramentas da NASA

| Ferramenta | Para que serve no projeto |
| --- | --- |
| NASA POWER (API e Data Access Viewer) | Baixar dados climáticos e agroclimáticos por ponto ou região, já em formato simples (CSV/JSON). É a porta de entrada mais fácil. |
| Earthdata Search | Encontrar os datasets da NASA (SMAP L4, IMERG, GLDAS, HLS, MODIS) e criar o login gratuito no Earthdata, exigido pelas outras ferramentas. |
| AppEEARS | Extrair séries temporais de MODIS, HLS e SMAP L4 para pontos ou polígonos, sem baixar imagens inteiras. Ideal para as regiões de demonstração. |
| earthaccess (biblioteca Python) | Buscar e baixar dados do Earthdata direto no código. É o que viabiliza o pré-cálculo do panorama nacional. |

---

## Anexo: fontes complementares (não NASA)

Não são da NASA, mas são abertas e reforçam os dados acima.

### Globais

| Dataset | Por que usar |
| --- | --- |
| ERA5 (ECMWF) | Variáveis climáticas horárias, incluindo temperatura do solo. É a segunda opinião independente sobre o clima do POWER. |
| FAO GAEZ v5 | Aptidão agroclimática por cultura, restrições de solo e cenários futuros. |
| SoilGrids (ISRIC, 250 m) | Textura, carbono orgânico, pH e densidade do solo em grade global. Substitui em parte o SSURGO. |

### Brasileiros (fecham as lacunas dos datasets dos EUA)

| Lacuna (dataset dos EUA) | Equivalente brasileiro | Por que usar |
| --- | --- | --- |
| Histórico de culturas (CDL) | MapBiomas | Uso do solo anual desde 1985, em 30 m, separando soja, café, pastagem, cana e outras culturas. Mostra a rotação real de uma área. |
| Estatísticas agrícolas e renda (NASS, AMS) | IBGE PAM (via SIDRA) | Área, produção, produtividade e valor da produção por cultura e município, todo ano. Também é a referência do critério de renda. |
| Chuva medida em campo (CoCoRaHS) | INMET e CEMADEN | Estações meteorológicas e pluviômetros. Validam IMERG, POWER e ERA5. |
| Calendário e risco por cultura | ZARC (MAPA/Embrapa) | Janelas de plantio de menor risco por município. Serve para validar as estratégias sugeridas. |

### Opcionais (`tools/extras/`)

| Fonte | Quando entra |
| --- | --- |
| FIRMS (focos de fogo, NASA) | Se a demo tiver Cerrado ou borda da Amazônia, onde as queimadas na seca afetam as estratégias com palhada. |
| Sentinel-1 (radar, ESA) | Só se a demo tiver uma região muito nublada na safra, onde o HLS fica sem imagem limpa. |
| Embrapa Solos (mapa de solos do Brasil, PronaSolos) | Depende da escolha da fonte de solo (Q-07). Dá as classes de solo brasileiras. |
