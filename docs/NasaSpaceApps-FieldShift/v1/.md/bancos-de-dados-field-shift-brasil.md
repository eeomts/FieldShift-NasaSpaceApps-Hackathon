# Bancos de dados para o Field Shift Brasil

*14 de novembro de 2026 · Gui*

Seis datasets são obrigatórios para a ferramenta funcionar no Brasil inteiro e três são complementares (classificação revista na D-009). Todos têm cobertura global; a classificação considera o que cada um entrega para comparar estratégias de rotação e as limitações de escala.

## Obrigatórios

Sem estes seis, a ferramenta não consegue calcular os indicadores básicos de clima, chuva, umidade, cobertura do solo, relevo e aptidão das culturas.

| Dataset | Resolução e período | Por que é importante | Limitação |
|---|---|---|---|
| **NASA POWER** | Grade de 0,5°; meteorologia desde 1981, radiação desde 1984; horário a climatologia | Série climática base: temperatura, umidade, radiação, risco de geada, estação de cultivo e demanda de água. Tem API REST pronta | Célula grande: um município pequeno pode cair numa única célula |
| **GPM IMERG** | 0,1° (cerca de 10 km), a cada 30 min, desde junho de 2000 | Regularidade da chuva, eventos extremos e risco de erosão. A versão Final inclui pluviômetros e é a melhor para séries históricas | Menor acerto em relevo complexo (serras do Sudeste e do Sul, Serra do Mar) |
| **SMAP L4** | Grade de 9 km, a cada 3 horas, desde março de 2015 | Umidade na zona das raízes (até cerca de 1 m): estresse hídrico e quantos dias o solo aguenta sem chuva | Zona das raízes estimada por modelo; série começa em 2015 |
| **MODIS NDVI (MOD13Q1)** | 250 m, a cada 16 dias, desde fevereiro de 2000 | Calendário de cobertura: mostra quando o campo fica descoberto e quando a cultura está estressada, para o país todo | Pixel de 250 m mistura talhões pequenos |
| **SRTM** | Cerca de 30 m, cobertura global | Declividade, escoamento, risco de erosão e baixadas sujeitas a geada | Retrato de 2000; não muda com o tempo |
| **FAO GAEZ v5** | Cerca de 1 km; linha de base 2020; cenários até 2100 | Checa se a cultura sugerida é adequada ao clima e solo do local. É o substituto global mais próximo do SSURGO para o Brasil | Dados de solo regionais, não do talhão |

> Usar a versão 5 do GAEZ, não a 4: a v5 atualizou a linha de base de 2010 para 2020 e melhorou a resolução.

## Complementares

Estes três não são indispensáveis, mas melhoram a precisão, preenchem lacunas e permitem medir a confiança dos indicadores.

| Dataset | Resolução e período | Por que é importante | Limitação |
|---|---|---|---|
| **HLS** | 30 m, revisita de 2 a 3 dias; Landsat desde 2013 e Sentinel-2 desde 2015 | Detalhe do talhão quando o produtor escolhe um local: calendário de cobertura e solo descoberto, com Landsat e Sentinel-2 já harmonizados | Nuvens na estação chuvosa; inviável para o país inteiro em 30 m |
| **GLDAS** | 0,25°, desde 2000, 36 variáveis | Umidade em camadas mais profundas e evapotranspiração contínuas; ajuda a detectar início de secas | Resultado de modelo, não observação direta |
| **ERA5** | 0,25°, horário, desde 1940 | Preenche lacunas e serve de comparação com POWER e IMERG, o que alimenta o nível de confiança | Reanálise: suaviza eventos locais |

## Fora do escopo

Doze datasets da lista cobrem apenas os Estados Unidos e não servem para o Brasil: Web Soil Survey, SSURGO/STATSGO2, CDL (CropScape), PRISM, NAIP, NLCD, CoCoRaHS, NWIS, USDA AMS Market News, NASS QuickStats, OpenET e LANDFIRE.

O OpenET foi ampliado e hoje cobre os 48 estados contíguos dos EUA, mas continua sem dados para o Brasil. O USDA Ag Data Commons deve ser verificado caso a caso, pois pode conter algum estudo aplicável.

A ausência desses dados gera lacunas em solo detalhado, histórico de culturas e preços, que a ferramenta deve mostrar ao produtor em vez de esconder.

## Fontes

- NASA POWER e manual do cliente da API
- GPM IMERG v7 (CEDA) e IMERG Final diário (UCAR)
- SMAP L4 SPL4SMGP (NSIDC)
- MODIS MOD13Q1 V6.1
- SRTM 1 Arc-Second Global (USGS)
- FAO GAEZ
- HLS HLSL30 e HLSS30 v2.0 (LP DAAC)
- GLDAS Noah 0,25°
- ERA5 (Copernicus CDS)
- Expansão do OpenET
