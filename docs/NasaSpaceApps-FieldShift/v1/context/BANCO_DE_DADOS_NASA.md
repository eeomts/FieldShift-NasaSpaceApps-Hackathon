# Banco de Dados NASA — Field Shift Brasil

Referência dos dados e ferramentas da NASA que podem ser usados no desafio **Field Shift: Adapting Farms with NASA Data** (NASA Space Apps Challenge 2026), com escopo no Brasil inteiro.

> **Atenção:** resoluções, cobertura e links devem ser confirmados nas páginas oficiais antes do uso.

---

## 1. Datasets da NASA da lista do desafio (cobertura global)

| Dataset | O que fornece | Uso na ferramenta |
| --- | --- | --- |
| NASA POWER | Temperatura, umidade, radiação e indicadores agroclimáticos | Série climática base, risco de geada, estação de cultivo, demanda hídrica |
| GPM IMERG | Taxa e acumulado de precipitação | Regularidade da chuva, veranicos, eventos extremos, risco de erosão |
| SMAP | Umidade do solo superficial (cerca de 5 cm), a cada 2–3 dias | Estresse hídrico, disponibilidade de água, infiltração |
| ECOSTRESS | Temperatura de superfície e evapotranspiração em alta resolução | Pontos de calor e de estresse hídrico, demanda de água da cultura |
| Landsat (30 m, NASA/USGS) | Reflectância, NDVI, índices de vegetação | Vigor da cultura, solo descoberto, transições de estação |
| MODIS/VIIRS (250–1000 m) | NDVI e índices de vegetação | Séries longas de vegetação em escala regional |
| GRACE e GRACE-FO | Tendência de água armazenada | Contexto de longo prazo da disponibilidade hídrica nas grandes bacias e regiões do país |
| SRTM | Elevação | Declividade, escoamento, risco de erosão, baixadas sujeitas a geada |
| GLDAS | Temperatura, chuva, umidade do solo e radiação em séries contínuas | Início de secas, déficits de umidade, transições de estação |
| GEDI | Biomassa e estrutura da vegetação | Contexto da paisagem ao redor das lavouras |

## 2. Datasets complementares da NASA

| Dataset | Por que usar |
| --- | --- |
| SMAP L4 (umidade da zona radicular) | O SMAP comum mede só os 5 cm superficiais. O L4 estima a umidade até cerca de 1 m, que é o que a raiz usa. É muito mais útil para estresse hídrico. |
| HLS (Harmonized Landsat Sentinel-2) | Landsat e Sentinel-2 já harmonizados em 30 m, com revisita de 2 a 3 dias. Resolve parte da harmonização e aumenta as chances de imagem sem nuvem. |
| MERRA-2 | Reanálise climática da própria NASA. Serve de alternativa ou comparação ao ERA5 no nível de confiança. |
| MODIS Land Cover (MCD12Q1) | Cobertura do solo anual, global. |
| FIRMS (focos de fogo, MODIS/VIIRS) | Queimadas na seca são comuns no Cerrado, no Pantanal e na borda da Amazônia e indicam risco e degradação do solo. |

## 3. Ferramentas da NASA

| Ferramenta | Para que serve no projeto |
| --- | --- |
| NASA POWER (API e Data Access Viewer) | Baixar dados climáticos e agroclimáticos por ponto ou região, já em formato simples (CSV/JSON). É a porta de entrada mais fácil e já é usada no app em Streamlit. |
| Earthdata Search | Encontrar e baixar quase todos os datasets da NASA (SMAP, IMERG, GLDAS, HLS, ECOSTRESS). Exige login gratuito no Earthdata. |
| AppEEARS | Extrair séries temporais de MODIS, VIIRS, Landsat, SMAP e ECOSTRESS para pontos ou polígonos, sem baixar imagens inteiras. Ideal para as regiões de demonstração. |
| Giovanni | Visualizar e analisar online IMERG, GLDAS e MERRA-2: médias, anomalias, séries e mapas. Bom para confirmar rapidamente as hipóteses de cada região. |
| Worldview | Navegar visualmente por imagens de satélite quase em tempo real. Útil para conferir solo descoberto ou fumaça em datas específicas e para gerar imagens para a apresentação. |
| earthaccess (biblioteca Python) | Buscar e baixar dados do Earthdata direto no código. Combina bem com Streamlit. |
| Harmony / OPeNDAP | Recortar por área e variável antes de baixar, o que economiza tempo e espaço. |
| NASA Harvest | Programa de agricultura e segurança alimentar da NASA com atuação global, incluindo o Brasil. Referência de metodologia e para citar no pitch. |
| ARSET (treinamentos) | Cursos gratuitos de sensoriamento remoto aplicado (agricultura, água, solo), com scripts prontos. Ótimo para a equipe aprender rápido durante o hackathon. |

---

## Anexo: fontes complementares (não NASA)

Não são da NASA, mas são abertas e reforçam os dados acima.

### Globais

| Dataset | Por que usar |
| --- | --- |
| Sentinel-2 (ESA, 10–20 m) | Imagens multiespectrais para NDVI/EVI e solo descoberto no nível do talhão. |
| Sentinel-1 (radar, ESA) | Enxerga através das nuvens, então permite acompanhar a lavoura na estação chuvosa. |
| ERA5 (ECMWF) | Variáveis climáticas horárias, incluindo temperatura do solo. Preenche lacunas das séries. |
| FAO GAEZ | Aptidão agroclimática por cultura, restrições de solo e água disponível. |
| SoilGrids (ISRIC, 250 m) | Textura, carbono orgânico, pH e densidade do solo em grade global. Substitui em parte o SSURGO. |
| CHIRPS | Chuva diária em cerca de 5 km, combinando satélite e estações. Funciona bem no Brasil e reforça o IMERG. |
| Copernicus DEM (30 m) | Elevação mais recente e precisa que o SRTM, boa para declividade. |
| ESA WorldCover (10 m) | Mapa de uso do solo detalhado. |

### Brasileiros (fecham as lacunas dos datasets dos EUA)

| Lacuna (dataset dos EUA) | Equivalente brasileiro | Por que usar |
| --- | --- | --- |
| Histórico de culturas (CDL) | MapBiomas | Uso do solo anual desde 1985, em 30 m, separando soja, café, pastagem, cana e outras culturas. Mostra a rotação real de uma área. |
| Estatísticas agrícolas (NASS) | IBGE PAM (via SIDRA) | Área, produção, produtividade e valor por cultura e município, todo ano. |
| Preços e mercado (AMS) | CONAB e CEPEA/ESALQ | Preços, custos de produção e acompanhamento de safra. |
| Solo detalhado (SSURGO) | Embrapa Solos (mapa de solos do Brasil, PronaSolos) | Classes de solo (latossolos, argissolos etc.), mais fiéis à realidade local. |
| Chuva medida em campo (CoCoRaHS) | INMET e CEMADEN | Estações meteorológicas e pluviômetros. Validam IMERG, POWER e CHIRPS. |
| Rios e poços (NWIS) | ANA HidroWeb | Séries de chuva e vazão. Contexto de disponibilidade de água e outorga. |
| Calendário e risco por cultura | ZARC (MAPA/Embrapa) | Janelas de plantio de menor risco por município. Serve para validar as estratégias sugeridas. |
| Relevo (complemento) | TOPODATA (INPE) | Declividade derivada do SRTM, já processada para o Brasil. |
