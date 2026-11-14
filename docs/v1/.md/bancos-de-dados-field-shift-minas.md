# Bancos de dados para o Field Shift Minas

*14 de novembro de 2026 · Gui*

Seis datasets são obrigatórios para a ferramenta funcionar em Minas Gerais, seis são complementares e um é opcional. Todos vêm da lista de recursos do desafio e têm cobertura global; a classificação considera o que cada um entrega para comparar estratégias de rotação e as limitações de escala.

## Obrigatórios

Sem estes seis, a ferramenta não consegue calcular os indicadores básicos de clima, chuva, umidade, cobertura do solo, relevo e aptidão das culturas.

| Dataset | Resolução e período | Por que é importante | Limitação |
|---|---|---|---|
| **NASA POWER** | Grade de 0,5°; meteorologia desde 1981, radiação desde 1984; horário a climatologia | Série climática base: temperatura, umidade, radiação, risco de geada, estação de cultivo e demanda de água. Tem API REST pronta | Célula grande: um município pequeno pode cair numa única célula |
| **GPM IMERG** | 0,1° (cerca de 10 km), a cada 30 min, desde junho de 2000 | Regularidade da chuva, eventos extremos e risco de erosão. A versão Final inclui pluviômetros e é a melhor para séries históricas | Menor acerto em relevo complexo (Zona da Mata, serras do Sul de Minas) |
| **SMAP** | Grade de 9 km (nativa 36 km), diária, desde março de 2015 | Umidade do solo superficial (0–5 cm): estresse hídrico, disponibilidade de água, sinais precoces de estresse | Só a camada superficial; série começa em 2015 |
| **MODIS NDVI (MOD13Q1)** | 250 m, a cada 16 dias, desde fevereiro de 2000 | Calendário de cobertura: mostra quando o campo fica descoberto e quando a cultura está estressada, para o estado todo | Pixel de 250 m mistura talhões pequenos |
| **SRTM** | Cerca de 30 m, cobertura global | Declividade, escoamento, risco de erosão e baixadas sujeitas a geada | Retrato de 2000; não muda com o tempo |
| **FAO GAEZ v5** | Cerca de 1 km; linha de base 2020; cenários até 2100 | Checa se a cultura sugerida é adequada ao clima e solo do local. É o substituto mais próximo do SSURGO para Minas | Dados de solo regionais, não do talhão |

> Usar a versão 5 do GAEZ, não a 4: a v5 atualizou a linha de base de 2010 para 2020 e melhorou a resolução.

## Complementares

Estes seis não são indispensáveis, mas melhoram a precisão, preenchem lacunas e permitem medir a confiança dos indicadores.

| Dataset | Resolução e período | Por que é importante | Limitação |
|---|---|---|---|
| **Sentinel-2** | 10–20 m, revisita de 5 dias | Detalhe do talhão quando o produtor escolhe um local: NDVI fino, solo descoberto, bandas red-edge para estresse | Nuvens na estação chuvosa; volume de dados alto |
| **Landsat 8/9** | 30 m, revisita de 8 dias com os dois satélites | Alternativa ao Sentinel-2 quando há nuvem; série histórica longa de reflectância | Resolução menor que a do Sentinel-2 |
| **ECOSTRESS** | 70 m, entre 52° N e 52° S, desde 2018 | Temperatura de superfície e evapotranspiração: mapas de pontos de calor e estresse hídrico no talhão | Passagens irregulares (órbita da ISS); não serve para séries regulares |
| **GLDAS** | 0,25°, desde 2000, 36 variáveis | Umidade em camadas mais profundas e evapotranspiração contínuas; ajuda a detectar início de secas | Resultado de modelo, não observação direta |
| **ERA5** | 0,25°, horário, desde 1940 | Preenche lacunas e serve de comparação com POWER e IMERG, o que alimenta o nível de confiança | Reanálise: suaviza eventos locais |
| **GRACE/GRACE-FO** | Grade de 0,5°, mas resolução real de 3°; mensal desde 2002 | Tendência de longo prazo da água armazenada no estado: contexto para o "shift" de disponibilidade hídrica | Só vale na escala do estado, nunca no município |

> O GRACE entra aqui, e não no núcleo, porque responde à pergunta "a água está diminuindo em Minas?", mas não muda a recomendação para um local específico.

## Opcional

O GEDI só vale a pena se sobrar tempo, para dar contexto da paisagem ao redor das lavouras.

| Dataset | Resolução e período | Por que é importante | Limitação |
|---|---|---|---|
| **GEDI L4A** | Amostras de cerca de 25 m em faixas, entre 51,6° N e S, desde 2019 | Biomassa e estrutura da vegetação alta: matas, cerrado e áreas perenes perto das lavouras | Focado em vegetação alta, cobertura em faixas e sem dados de março de 2023 a abril de 2024 |

## Fora do escopo

Doze datasets da lista cobrem apenas os Estados Unidos e não servem para Minas: Web Soil Survey, SSURGO/STATSGO2, CDL (CropScape), PRISM, NAIP, NLCD, CoCoRaHS, NWIS, USDA AMS Market News, NASS QuickStats, OpenET e LANDFIRE.

O OpenET foi ampliado e hoje cobre os 48 estados contíguos dos EUA, mas continua sem dados para o Brasil. O USDA Ag Data Commons deve ser verificado caso a caso, pois pode conter algum estudo aplicável.

A ausência desses dados gera lacunas em solo detalhado, histórico de culturas e preços, que a ferramenta deve mostrar ao produtor em vez de esconder.

## Fontes

- NASA POWER e manual do cliente da API
- GPM IMERG v7 (CEDA) e IMERG Final diário (UCAR)
- SMAP SPL3SMP_E (NSIDC)
- MODIS MOD13Q1 V6.1
- SRTM 1 Arc-Second Global (USGS)
- FAO GAEZ
- Sentinel-2 (ESA)
- Landsat 8/9 Level-2 (USGS) e Sentinel Hub
- ECOSTRESS (Earthdata) e ECOSTRESS ESI L4
- GLDAS Noah 0,25°
- ERA5 (Copernicus CDS)
- JPL GRACE Mascons
- GEDI L4A V3 (ORNL DAAC)
- Expansão do OpenET
