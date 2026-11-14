# NASA POWER API — Análise e documentação

## Foco: Daily · Single Point (`GET /api/temporal/daily/point`)

> Projeto: Field Shift (NASA Space Apps Challenge 2026)
> Documento compilado em 14/11/2026

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [O menu "Select a definition"](#2-o-menu-select-a-definition)
3. [Arquitetura da API](#3-arquitetura-da-api)
4. [Endpoint principal: Daily Single Point](#4-endpoint-principal-daily-single-point)
5. [Parâmetros da requisição](#5-parâmetros-da-requisição)
6. [Comunidades (AG, RE, SB)](#6-comunidades-ag-re-sb)
7. [Formatos de saída](#7-formatos-de-saída)
8. [Estrutura da resposta](#8-estrutura-da-resposta)
9. [Outros endpoints Daily: Regional](#9-outros-endpoints-daily-regional)
10. [Como testar a API](#10-como-testar-a-api)
11. [Códigos de erro](#11-códigos-de-erro)
12. [Limitações](#12-limitações)
13. [Boas práticas](#13-boas-práticas)
14. [Parâmetros úteis para o Field Shift](#14-parâmetros-úteis-para-o-field-shift)
15. [Como e por que usar o NASA POWER no Field Shift](#15-como-e-por-que-usar-o-nasa-power-no-field-shift)
16. [Caso hipotético: a ferramenta na prática](#16-caso-hipotético-a-ferramenta-na-prática)
17. [Referências](#17-referências)

---

## Nível de verificação

- As informações vêm das páginas oficiais de documentação do POWER (`power.larc.nasa.gov/docs/...`), do arquivo `llms.txt` do site e do código do pacote R oficial-comunitário `nasapower` (rOpenSci).
- **A própria página Swagger (`/api/pages/`) e as especificações `openapi.json` não puderam ser lidas diretamente**: o site bloqueia leitura automatizada dessas páginas.
- **Nenhuma requisição foi executada ao vivo** neste documento pelo mesmo motivo. A seção [10](#10-como-testar-a-api) mostra como você mesmo testa em menos de um minuto.
- Itens marcados com ⚠️ têm divergência entre fontes ou não estão descritos na documentação pública. Confirme na página Swagger.

---

## 1. Visão geral

**POWER** (Prediction Of Worldwide Energy Resources) é um projeto da NASA Langley que distribui dados solares e meteorológicos globais, prontos para análise (*Analysis Ready Data*, ARD).

| Item | Valor |
|---|---|
| Cobertura | Global |
| Parâmetros | 300+ |
| Níveis temporais | Horário, diário, mensal, anual, climatologia |
| Dados meteorológicos | Desde 1981 (modelo MERRA-2 + GEOS FP-IT perto do tempo real) |
| Dados solares | Desde 1984 (GEWEX SRB → CERES SYN1deg → CERES FLASHFlux) |
| Latência | Cerca de 2 a 7 dias atrás do tempo real |
| Resolução | 0,5° × 0,625° (meteorologia) e 1° × 1° (solar) |
| Licença | CC BY 4.0 |
| Autenticação | **Nenhuma**. Sem login, sem chave de API |
| Base URL | `https://power.larc.nasa.gov` |

**Formas de acesso:** API REST (este documento), Data Access Viewer (DAV, interface com mapa), serviços geoespaciais ArcGIS e o Registry of Open Data na AWS.

---

## 2. O menu "Select a definition"

A página da API (`https://power.larc.nasa.gov/api/pages/`) é uma interface **Swagger UI**. Swagger é uma ferramenta que transforma uma especificação OpenAPI em uma página interativa, onde cada endpoint aparece com seus parâmetros e um botão para testar.

O menu **"Select a definition"** escolhe **qual especificação OpenAPI** (qual microsserviço) a página mostra. Cada item é uma API independente, com seus próprios endpoints. Ao trocar o item, a página recarrega com outro conjunto de endpoints.

As definições pertencem a três categorias:

| Categoria | Função |
|---|---|
| **Temporal** | Entregam os dados em si (séries temporais e climatologias) |
| **Application** | Geram relatórios e produtos calculados a partir das APIs temporais |
| **System** | Fornecem configuração e informação de apoio a todas as APIs |

### 2.1 Definições do grupo Temporal

| Definição | Caminho | O que retorna | Point | Regional |
|---|---|---|---|---|
| **Hourly** | `/api/temporal/hourly` | Médias por hora, desde 01/01/2001 | Sim | Não |
| **Daily** | `/api/temporal/daily` | Valores diários (média, máxima e/ou mínima), desde 01/01/1981 | Sim | Sim |
| **Monthly & Annual** | `/api/temporal/monthly` | Média de cada mês e do ano, para cada ano do período | Sim | Sim |
| **Climatology** | `/api/temporal/climatology` | Média de longo prazo de cada mês (ex.: "janeiro típico") | Sim | Sim |

**Diferença entre Monthly e Climatology:** Monthly devolve "março de 2015, março de 2016, março de 2017…" separadamente. Climatology devolve **um único** "março típico", média de todos os anos do período. A climatologia padrão usa um período pré-definido; para um período personalizado, envie `start` e `end` (anos).

### 2.2 Definições do grupo Application

| Definição | Caminho | O que faz |
|---|---|---|
| **Indicators** | `/api/application/indicators` | Relatório de indicadores climáticos no estilo ASHRAE (normas de climatização de edificações) para um local e período. Calcula mais de 120 parâmetros em três níveis temporais. Períodos entre 1990 e 2014 são pré-processados e respondem mais rápido |
| **Windrose** | `/api/application/windrose` | Tabela de rosa dos ventos: percentual do tempo em que o vento sopra de cada uma de 16 direções, dividido em 8 classes de potência eólica baseadas no NREL |
| **Zones** | `/api/application/zones` | Zonas térmicas e termo-úmidas (classificação climática de edificações), por ponto, região ou globo |

### 2.3 Definições do grupo System

| Definição | Caminho | O que faz |
|---|---|---|
| **Manager** | `/api/system/manager` | Catálogo de parâmetros: lista quais parâmetros existem para cada comunidade e nível temporal, seus nomes longos e unidades. Também lista os apelidos de superfície para correção do vento. **Responde só em JSON** |
| **Resources** | `/api/system/resources` | Tarefas auxiliares do site: métricas de uso, disponibilidade de dados, gráficos dos painéis (*dashboards*) e metadados das fontes |

### 2.4 Outras definições

| Definição | O que é |
|---|---|
| **Climate Projection** | Projeções climáticas futuras. Segundo apresentações da equipe POWER, usa projeções regionalizadas (*downscaled*) do NEX-GDDP-CMIP6, de 22 modelos climáticos em grade de 25 km, com 9 parâmetros meteorológicos e de radiação de 2015 a 2100 e 3 cenários de emissão (SSP1-2.6, SSP2-4.5, SSP3-7.0). ⚠️ A página de documentação pública da API não descreve os endpoints; confira na Swagger |
| **PRUVE** | *PaRameter Uncertainty ViEwer*. Ferramenta de validação que compara os dados do POWER com medições de superfície: estações meteorológicas da NOAA e radiação da rede BSRN. Serve para avaliar a incerteza do dado num local. A definição na Swagger expõe a API usada por essa ferramenta. ⚠️ Endpoints não documentados nas páginas públicas |
| **Toolkit** | ⚠️ Não está descrito nas páginas públicas de documentação nem no `llms.txt` do site. Pelo nome e pela organização do menu, parece agrupar utilitários de apoio às demais APIs. **Abra a definição na Swagger para ver os endpoints reais antes de usar** |

### 2.5 Qual definição usar no Field Shift

| Necessidade | Definição |
|---|---|
| Série histórica diária de chuva, temperatura, radiação | **Daily** |
| Detalhe dentro do dia (ondas de calor horárias, geada de madrugada) | **Hourly** |
| Comparar anos (ano seco × ano chuvoso) | **Monthly & Annual** |
| Calendário agrícola "típico" do local | **Climatology** |
| Descobrir nomes e unidades de parâmetros | **Manager** |
| Avaliar a confiabilidade do dado no local | **PRUVE** |
| Cenários futuros para os sliders de clima | **Climate Projection** |
| Indicators, Windrose, Zones | Pouco relevantes (foco em edificações e energia eólica) |

---

## 3. Arquitetura da API

- **REST com GET**: todos os parâmetros vão na URL (*query string*).
- **Microsserviços**: cada definição do menu é um serviço separado, com sua própria especificação `openapi.json`.
- **Um formato por requisição**: na versão 2 da API não é mais possível pedir vários formatos de uma vez. A resposta é o próprio arquivo, enviado diretamente.
- **Ordem dos argumentos não importa** depois do `?`.
- **Listas** (como vários parâmetros) usam vírgula `,` ou `%2C`.

Especificações OpenAPI disponíveis:

```
https://power.larc.nasa.gov/api/temporal/hourly/openapi.json
https://power.larc.nasa.gov/api/temporal/daily/openapi.json
https://power.larc.nasa.gov/api/temporal/monthly/openapi.json
https://power.larc.nasa.gov/api/temporal/climatology/openapi.json
https://power.larc.nasa.gov/api/application/indicators/openapi.json
https://power.larc.nasa.gov/api/application/windrose/openapi.json
```

Esses arquivos podem ser importados no Postman, Insomnia ou em geradores de cliente (`openapi-generator`).

---

## 4. Endpoint principal: Daily Single Point

```
GET https://power.larc.nasa.gov/api/temporal/daily/point
```

**O que faz:** devolve uma série temporal **diária** de um ou mais parâmetros para **uma coordenada** (latitude e longitude), no intervalo de datas pedido.

**Valores:** média, máxima e/ou mínima por dia, conforme o parâmetro (ex.: `T2M` é a média, `T2M_MAX` a máxima).

**Disponibilidade:** de **01/01/1981** até perto do tempo real.

**Fontes dos dados:**

| Tipo | Fonte | Período |
|---|---|---|
| Solar | GEWEX SRB R4-IP | 01/01/1984 – 31/12/2000 |
| Solar | CERES SYN1deg | 01/01/2001 – alguns meses atrás |
| Solar | CERES FLASHFlux | Fim do CERES – cerca de 7 dias atrás |
| Meteorologia | MERRA-2 (GMAO) | 01/01/1981 – alguns meses atrás |
| Meteorologia | GEOS 5.12.4 FP-IT | Fim do MERRA-2 – alguns dias atrás |

> **Importante:** os dados mais recentes (perto do tempo real) vêm de fontes provisórias. Entre 2 e 3 meses depois, são **substituídos** por dados de qualidade climática. Se você baixar dados recentes hoje, eles podem mudar.

### Exemplo mínimo

```
https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M&community=AG&longitude=-47.5&latitude=-18.7&start=20240101&end=20240131&format=JSON
```

### Exemplo para o Field Shift

```
https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M,GWETROOT&community=AG&longitude=-47.5&latitude=-18.7&start=20000101&end=20251231&format=CSV
```

---

## 5. Parâmetros da requisição

| Parâmetro | Obrigatório | Tipo / formato | Descrição |
|---|---|---|---|
| `parameters` | Sim | Lista separada por vírgula | Nomes curtos dos parâmetros (ex.: `T2M,PRECTOTCORR`). **Máximo de 20** |
| `community` | Sim | `AG`, `RE` ou `SB` | Comunidade de usuários; define unidades e o conjunto de parâmetros (ver seção 6) |
| `longitude` | Sim | Número decimal, -180 a 180 | Longitude do ponto (oeste é negativo) |
| `latitude` | Sim | Número decimal, -90 a 90 | Latitude do ponto (sul é negativo) |
| `start` | Sim | `YYYYMMDD` | Data inicial (não antes de 19810101) |
| `end` | Sim | `YYYYMMDD` | Data final (não depois de hoje) |
| `format` | Não | `JSON`, `CSV`, `ASCII`, `NETCDF`, `ICASA` | Formato da resposta (ver seção 7). Padrão: JSON |
| `time-standard` | Não | `LST` ou `UTC` | Padrão de tempo (ver abaixo) |
| `site-elevation` | Não | Metros | Altitude do local; o POWER corrige a pressão atmosférica para essa altitude. Só no modo Point |
| `wind-elevation` | Não | Metros, entre **10 e 300** | Altura para a qual a velocidade do vento será recalculada. Só no modo Point |
| `wind-surface` | Não | Apelido de superfície | Tipo de superfície usado no cálculo do vento (ex.: `SeaIce`, `openwater`, `airportgrass`). Se usar, inclua também `wind-elevation`. A lista vem do Manager |
| `user` | Não | Texto | Identificação da sua aplicação (ex.: `fieldshift`). Recomendado pela NASA para acompanhar o uso |
| `header` | Não | `true` / `false` | ⚠️ Inclui ou não o cabeçalho de metadados em CSV/ASCII. Confirme na Swagger |
| `units` | Não | `metric` / `imperial` | ⚠️ Sistema de unidades. Confirme na Swagger |

### Explicação detalhada de cada parâmetro

Na URL, cada parâmetro aparece como `nome=valor`, separados por `&`, depois do `?`:

```
.../daily/point?parameters=T2M&community=AG&longitude=-47.5&latitude=-18.7&start=20240101&end=20240131&format=JSON
```

A ordem dos parâmetros não importa.

---

#### `parameters` — quais dados você quer

**O que é:** a lista de variáveis a baixar, usando o **nome curto** de cada uma (ex.: `T2M` = temperatura a 2 metros, `PRECTOTCORR` = precipitação corrigida).

**Como escrever:**
- Um parâmetro: `parameters=T2M`
- Vários: `parameters=T2M,T2M_MIN,PRECTOTCORR` (separados por vírgula ou `%2C`, que é a vírgula codificada para URL)

**Regras:**
- **Máximo de 20 parâmetros** por requisição. Esse limite não vale para parâmetros que a própria API precisa buscar internamente para calcular outro.
- O nome precisa existir **na comunidade escolhida e no nível diário**. Um parâmetro disponível no Hourly pode não existir no Daily, e vice-versa.

**Como descobrir os nomes:** pelo Parameter Dictionary (`https://power.larc.nasa.gov/parameters/`) ou pelo Manager:
```
https://power.larc.nasa.gov/api/system/manager/parameters?community=ag&temporal=daily
```

**Erro comum:** escrever o nome longo (`Temperature at 2 Meters`) em vez do curto (`T2M`).

---

#### `community` — para qual tipo de usuário

**O que é:** a "comunidade" de usuários. O POWER organiza os dados em três pacotes, cada um pensado para um setor:

| Valor | Comunidade | Feito para |
|---|---|---|
| `AG` | Agroclimatology | Agricultura e modelos de cultura (DSSAT) |
| `RE` | Renewable Energy | Energia solar e eólica |
| `SB` | Sustainable Infrastructure | Projeto de edificações |

**Por que importa:** a comunidade muda **quais parâmetros estão disponíveis** e pode mudar **as unidades** do mesmo dado. Por isso, sempre leia as unidades no campo `parameters` da resposta.

**Para o Field Shift:** use sempre `community=AG`. Além de ser a comunidade agrícola, é a única que libera o formato ICASA.

---

#### `longitude` e `latitude` — onde

**O que são:** as coordenadas geográficas do ponto, em **graus decimais**.

| | Faixa | Sinal |
|---|---|---|
| `latitude` | -90 a 90 | Positivo = Norte, **negativo = Sul** |
| `longitude` | -180 a 180 | Positivo = Leste, **negativo = Oeste** |

**Exemplo:** Monte Carmelo (MG) fica aproximadamente em `latitude=-18.7` e `longitude=-47.5`. Todo o Brasil tem longitude negativa, e quase todo o território tem latitude negativa.

**Atenção à resolução:** o POWER não devolve o valor exato da coordenada; devolve o valor da **célula da grade** que contém o ponto (0,5° × 0,625° para meteorologia, cerca de 55 × 65 km). Duas coordenadas na mesma célula devolvem **exatamente os mesmos dados**. A resposta informa as coordenadas e a altitude da célula em `geometry.coordinates`.

**Erros comuns:**
- Trocar latitude e longitude.
- Esquecer o sinal negativo (o ponto vai parar no Hemisfério Norte ou na Ásia).
- Usar vírgula como separador decimal (`-18,7`). Use **ponto**: `-18.7`.
- Usar graus/minutos/segundos (18°42'S). Converta para decimal: graus + minutos/60 + segundos/3600, com sinal negativo para Sul/Oeste.

---

#### `start` e `end` — quando

**O que são:** as datas inicial e final do período, **inclusive** (os dois dias entram no resultado).

**Formato:** `YYYYMMDD`, sem traços nem barras.
- 1º de janeiro de 2024 → `20240101`
- 31 de dezembro de 2025 → `20251231`

**Regras:**
- `start` não pode ser anterior a **19810101** (início dos dados meteorológicos).
- `end` não pode ser uma data futura.
- `start` deve ser igual ou anterior a `end`.

**Detalhes importantes:**
- **Dados solares** só existem a partir de **1984**. Se você pedir radiação para 1981–1983, virá `-999` (ausente).
- **Os dias mais recentes** podem vir como `-999`, porque os dados chegam com cerca de 2 a 7 dias de atraso.
- Os **últimos 2 a 3 meses são provisórios** e depois são substituídos por dados de melhor qualidade.
- Períodos longos com muitos parâmetros deixam a resposta mais lenta. Para 40 anos de dados, uma requisição por ponto ainda funciona, mas pode levar alguns segundos.

**Comparação com outras definições:** no Monthly, `start` e `end` são **anos** (`2016`); no Climatology, são opcionais e servem para pedir uma climatologia personalizada.

---

#### `format` — em que formato receber

**O que é:** o tipo de arquivo da resposta. Só é possível escolher **um** formato por requisição.

| Valor | Quando usar |
|---|---|
| `JSON` | Aplicações web e JavaScript; fácil de ler em Python |
| `CSV` | Excel, Google Sheets, pandas. Vem com um bloco de metadados antes da tabela |
| `ASCII` | Texto simples tabulado |
| `NETCDF` | Ferramentas científicas (xarray, Panoply, QGIS) |
| `ICASA` | Entrada direta no modelo de culturas DSSAT. **Só com `community=AG`** |

**Para o Field Shift:** `JSON` se o app for web; `CSV` para análise exploratória.

**Sobre o ICASA:** basta pedir pelo menos um parâmetro, e a API completa sozinha os que o DSSAT exige. Para incluir a amplitude térmica mensal, o período precisa ter pelo menos dois meses. O arquivo sai sempre em hora solar local.

---

#### `time-standard` — qual relógio usar

**O que é:** define em qual padrão de horário os dias são contados.

| Valor | Significado |
|---|---|
| `UTC` | Tempo Universal Coordenado: o mesmo relógio no mundo todo |
| `LST` | Hora Solar Local: o planeta é dividido em faixas de 15° de longitude, e o meio-dia solar fica no centro da faixa |

**Por que importa:** "um dia" em UTC não começa no mesmo instante que um dia no horário local. No horário de Brasília (UTC-3), o dia UTC vai das 21h de um dia às 21h do dia seguinte, no horário local. Com o escopo nacional, isso varia: o Brasil tem quatro fusos (UTC-2 em Fernando de Noronha, UTC-3 na maior parte do país, UTC-4 em MT, MS, RO, RR e boa parte do AM, e UTC-5 no Acre e no oeste do AM). Isso pode jogar a chuva de uma tempestade noturna no "dia errado" e mudar a temperatura mínima registrada.

**Recomendação:** use **LST** para análises agrícolas, porque o dia acompanha o ciclo do sol que a planta vive. No nível diário, os dois padrões estão disponíveis desde 1981.

---

#### `site-elevation` — altitude real do local

**O que é:** a altitude da sua fazenda, **em metros**.

**Por que existe:** a célula da grade tem uma **altitude média**, que pode ser bem diferente da altitude do talhão, principalmente em regiões de relevo acidentado. Ao informar a altitude real, o POWER **corrige a pressão atmosférica** para esse valor.

**Exemplo:** `site-elevation=890`

**Regras e limites:**
- Só funciona no modo **Point** (não no Regional).
- Corrige **a pressão**; **não** corrige a temperatura nem a chuva.

**Utilidade no projeto:** a pressão entra no cálculo da evapotranspiração de referência (FAO-56 Penman-Monteith). Você pode pegar a altitude do talhão no **SRTM** e passar aqui.

---

#### `wind-elevation` — altura do vento

**O que é:** a altura, **em metros**, para a qual você quer a velocidade do vento recalculada.

**Por que existe:** o POWER fornece o vento em alturas fixas (2 m, 10 m e 50 m). Se você precisa do vento em outra altura (por exemplo, na altura de um quebra-vento ou de um aerogerador), a API extrapola usando um perfil de vento.

**Regras:**
- Valor entre **10 e 300 metros**.
- Só no modo **Point**.

**Exemplo:** `wind-elevation=50`

**Para o Field Shift:** normalmente **não é necessário**. A evapotranspiração FAO-56 usa o vento a **2 metros**, que já existe pronto no parâmetro `WS2M`.

---

#### `wind-surface` — tipo de terreno para o vento

**O que é:** o tipo de superfície do entorno, usado para ajustar o cálculo do vento. Superfícies mais rugosas (floresta, cidade) freiam mais o vento perto do chão do que superfícies lisas (água, gelo).

**Como funciona:** cada superfície tem um **expoente de rugosidade**. A API usa esse expoente para recalcular o vento na altura definida em `wind-elevation`.

**Exemplos de valores (apelidos):** `SeaIce` (gelo marinho), `openwater` (água aberta), `airportice` (aeroporto com gelo/neve), `airportgrass` (aeroporto com grama rasteira). A lista completa e os expoentes vêm do Manager.

**Regras:**
- Só no modo **Point**.
- **Se usar `wind-surface`, informe também `wind-elevation`.**

**Exemplo:** `wind-surface=airportgrass&wind-elevation=50`

**Para o Field Shift:** pouco relevante.

---

#### `user` — quem está pedindo

**O que é:** um texto que identifica a sua aplicação.

**Por que existe:** permite à equipe do POWER acompanhar o uso da API. O tutorial oficial de primeiros passos orienta substituir o valor de `user` pelo nome do seu serviço ao copiar um link gerado pelo Data Access Viewer.

**Exemplo:** `user=fieldshift`

**Observação:** não é login nem senha; a API é aberta. Não coloque e-mail ou dados pessoais aqui.

---

#### `header` ⚠️

**O que deve fazer:** controlar se o bloco de metadados (fonte, unidades, valor de preenchimento) aparece no início dos arquivos CSV/ASCII. Com `header=false`, o CSV começaria direto na tabela, mais fácil de abrir no Excel.

**Situação:** não está descrito nas páginas de documentação lidas. Confirme na Swagger se o parâmetro existe e quais valores aceita.

**Alternativa segura:** no pandas, ignore as linhas de cabeçalho com `skiprows` (procure a linha `-END HEADER-`).

---

#### `units` ⚠️

**O que deve fazer:** escolher o sistema de unidades (métrico ou imperial).

**Situação:** não está descrito nas páginas de documentação lidas. Confirme na Swagger. Se não existir, os dados vêm no sistema métrico, que é o que o projeto precisa.

---

### Resumo: o que é obrigatório e o que usar no Field Shift

| Parâmetro | Obrigatório | Valor recomendado no Field Shift |
|---|---|---|
| `parameters` | Sim | `T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M,PS` |
| `community` | Sim | `AG` |
| `longitude` | Sim | Coordenada do talhão (negativa no Brasil) |
| `latitude` | Sim | Coordenada do talhão (negativa no Brasil) |
| `start` | Sim | `20000101` ou anterior, para ter série longa |
| `end` | Sim | Pelo menos alguns meses antes de hoje, para evitar dados provisórios |
| `format` | Não | `JSON` (app) ou `CSV` (análise) |
| `time-standard` | Não | `LST` |
| `site-elevation` | Não | Altitude do talhão, vinda do SRTM |
| `wind-elevation` | Não | Não usar |
| `wind-surface` | Não | Não usar |
| `user` | Não | `fieldshift` |

---

## 6. Comunidades (AG, RE, SB)

| Comunidade | Nome | Para quem |
|---|---|---|
| **AG** | Agroclimatology | Ferramentas agrícolas, como o modelo de culturas **DSSAT** |
| **RE** | Renewable Energy | Dimensionamento de painéis solares, baterias, fogões solares |
| **SB** | Sustainable Infrastructure (antes "Sustainable Buildings") | Projeto preliminar de edificações e escolha de local |

A comunidade muda **unidades** e **quais parâmetros** estão disponíveis. Por exemplo, as unidades de radiação diferem entre comunidades: a AG costuma usar MJ/m²/dia, comum em modelos agrícolas, enquanto a RE usa kWh/m²/dia. ⚠️ Confirme a unidade de cada parâmetro no Manager ou no campo `parameters` da resposta, porque a página de comunidades não lista unidades.

**Para o Field Shift, use `community=AG`.** Ela também é a única que permite o formato ICASA.

---

## 7. Formatos de saída

| Formato | Daily | Observação |
|---|---|---|
| `JSON` | Sim | Melhor para aplicações web; estrutura GeoJSON (ver seção 8) |
| `CSV` | Sim | Melhor para planilhas e pandas; tem um cabeçalho de metadados antes da tabela |
| `ASCII` | Sim | Texto tabulado |
| `NETCDF` | Sim | Formato científico multidimensional (xarray, Panoply) |
| `ICASA` | **Só com AG** | Formato de entrada do DSSAT. A API completa sozinha os parâmetros exigidos, mas é preciso enviar pelo menos um. A amplitude mensal só aparece com período de 2+ meses. Sai em hora solar local (LST) |
| `EPW` | Não | Só no Hourly (arquivo climático de simulação de edificações) |
| `GeoTIFF` | Não | Previsto para versão futura |

---

## 8. Estrutura da resposta

A resposta JSON segue o formato **GeoJSON Feature**. Estrutura típica:

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [-47.5, -18.7, 925.3]
  },
  "properties": {
    "parameter": {
      "T2M": {
        "20240101": 23.41,
        "20240102": 22.87
      },
      "PRECTOTCORR": {
        "20240101": 12.3,
        "20240102": 0.0
      }
    }
  },
  "header": {
    "title": "NASA/POWER ... Daily Data",
    "api": { "version": "...", "name": "POWER Daily API" },
    "sources": ["MERRA2", "..."],
    "fill_value": -999.0,
    "time_standard": "LST",
    "start": "20240101",
    "end": "20240131"
  },
  "messages": [],
  "parameters": {
    "T2M": { "units": "C", "longname": "Temperature at 2 Meters" }
  },
  "times": { "data": 0.5, "process": 0.1 }
}
```

> Os valores numéricos acima são ilustrativos. Os campos podem variar ligeiramente por versão da API.

**Pontos importantes:**

- `geometry.coordinates` traz longitude, latitude e a **altitude** da célula da grade (não da sua fazenda).
- `properties.parameter` é um dicionário **parâmetro → {data: valor}**, com a data em `YYYYMMDD`.
- `parameters` traz **unidades** e **nome longo** de cada parâmetro. Leia daqui em vez de supor.
- **Valor de preenchimento: `-999`** (às vezes `-99` ou `-999.0`). Significa "dado ausente". **Converta para nulo antes de calcular médias**, senão uma única falha estraga a estatística.
- `messages` traz avisos (ex.: parâmetros ignorados).

**Lendo em Python:**

```python
import requests, pandas as pd

url = "https://power.larc.nasa.gov/api/temporal/daily/point"
params = {
    "parameters": "T2M,T2M_MIN,PRECTOTCORR",
    "community": "AG",
    "longitude": -47.5, "latitude": -18.7,
    "start": "20200101", "end": "20241231",
    "format": "JSON", "user": "fieldshift",
}
r = requests.get(url, params=params, timeout=120)
r.raise_for_status()
data = r.json()

df = pd.DataFrame(data["properties"]["parameter"])
df.index = pd.to_datetime(df.index, format="%Y%m%d")
df = df.replace([-999, -999.0, -99, -99.0], pd.NA)   # remove valores ausentes
print(data["parameters"])                            # unidades
print(df.describe())
```

---

## 9. Outros endpoints Daily: Regional

```
GET https://power.larc.nasa.gov/api/temporal/daily/regional
```

Devolve a série diária para **todas as células da grade dentro de um retângulo**.

| Parâmetro | Descrição |
|---|---|
| `latitude-min`, `latitude-max` | Limites sul e norte |
| `longitude-min`, `longitude-max` | Limites oeste e leste |
| `parameters` | **Apenas 1 parâmetro** por requisição |
| `community`, `start`, `end`, `format`, `time-standard`, `user` | Iguais ao Point |

**Não aceita** `site-elevation`, `wind-elevation` nem `wind-surface` (só existem no Point).

**Tamanho máximo:** segundo a documentação do pacote `nasapower`, a área máxima processada é de cerca de **4,5° × 4,5° (100 pontos de grade)**. ⚠️ Confirme na Swagger, pois o limite pode mudar.

Exemplo:
```
https://power.larc.nasa.gov/api/temporal/daily/regional?latitude-min=-19.5&latitude-max=-17.5&longitude-min=-48.5&longitude-max=-46.5&parameters=PRECTOTCORR&community=AG&start=20240101&end=20240131&format=CSV
```

---

## 10. Como testar a API

### 10.1 Pelo navegador (mais simples)

Cole a URL do [exemplo mínimo](#exemplo-mínimo) na barra de endereços. Com `format=JSON`, o navegador mostra o JSON; com `format=CSV`, baixa o arquivo.

### 10.2 Pela página Swagger (interface oficial)

1. Abra `https://power.larc.nasa.gov/api/pages/`.
2. Em **Select a definition**, escolha **Daily**.
3. Abra a seção **Data Requests** e clique em `GET /api/temporal/daily/point`.
4. Clique em **Try it out**.
5. Preencha `parameters`, `community`, `longitude`, `latitude`, `start`, `end` e `format`.
6. Clique em **Execute**.
7. A página mostra três coisas úteis:
   - **Request URL**: a URL pronta, para copiar para o seu código.
   - **Curl**: o comando equivalente no terminal.
   - **Server response**: código HTTP e corpo da resposta.

Essa é a forma recomendada pela própria NASA para montar e testar requisições.

### 10.3 Pelo Data Access Viewer (sem código)

No DAV (`https://power.larc.nasa.gov/data-access-viewer/`), escolha o ponto no mapa, a comunidade, o período e os parâmetros. A ferramenta oferece o link da API correspondente para copiar. Troque o valor de `user` pelo nome da sua aplicação.

### 10.4 Pelo terminal (curl)

```bash
curl -s "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR&community=AG&longitude=-47.5&latitude=-18.7&start=20240101&end=20240107&format=JSON&user=fieldshift"
```

### 10.5 Roteiro de testes sugerido

| # | Teste | Resultado esperado |
|---|---|---|
| 1 | Requisição mínima válida | HTTP 200 e dados |
| 2 | Remover `community` | Erro de validação listando o parâmetro ausente |
| 3 | `start` posterior a `end` | Erro de validação |
| 4 | `start=19700101` | Erro: antes de 1981 |
| 5 | 21 parâmetros | Erro: acima do limite de 20 |
| 6 | Parâmetro inexistente (`XYZ`) | Erro ou aviso em `messages` |
| 7 | `format=ICASA` com `community=RE` | Erro: ICASA só existe em AG |
| 8 | `wind-elevation=5` | Erro: precisa estar entre 10 e 300 |
| 9 | Dois pontos a 10 km de distância | Valores idênticos (mesma célula de 0,5°) |
| 10 | Período recente (últimos 7 dias) | Alguns valores `-999` ou ausentes |
| 11 | Mesma requisição em `time-standard=UTC` e `LST` | Valores diários ligeiramente diferentes |
| 12 | Regional com 2 parâmetros | Erro: Regional aceita 1 parâmetro |

O teste 9 é especialmente importante para o projeto: ele mostra que o POWER **não diferencia talhões vizinhos**.

### 10.6 Teste automatizado em Python

```python
import requests

BASE = "https://power.larc.nasa.gov/api/temporal/daily/point"
OK = dict(parameters="T2M", community="AG", longitude=-47.5, latitude=-18.7,
          start="20240101", end="20240107", format="JSON", user="fieldshift")

def test(nome, **mudancas):
    p = {**OK, **mudancas}
    p = {k: v for k, v in p.items() if v is not None}
    r = requests.get(BASE, params=p, timeout=60)
    print(f"{nome:<35} HTTP {r.status_code}  {r.text[:120]!r}")

test("válida")
test("sem community", community=None)
test("datas invertidas", start="20240107", end="20240101")
test("antes de 1981", start="19700101")
test("21 parâmetros", parameters=",".join(["T2M"] * 21))
test("ICASA fora do AG", community="RE", format="ICASA")
```

---

## 11. Códigos de erro

| Código | Significado | Ação |
|---|---|---|
| 200 | Sucesso | — |
| 400 | Requisição inválida (entradas incorretas) | Leia o corpo: ele **lista todas as violações** |
| 401 | Não autorizado | Raro (a API é aberta) |
| 404 | Serviço indisponível | Verifique a URL e a página de status |
| 422 | Erro de validação | ⚠️ Versões mais recentes da documentação listam 422 para erros de sintaxe e parâmetros, no lugar do 400. Trate os dois |
| 429 | Requisições demais | Reduza a frequência e espere antes de tentar de novo |
| 450 | Arquivo de dados do POWER inacessível | Tente mais tarde |
| 460 | Serviços da API inacessíveis | Tente mais tarde |
| 500, 502, 504 | Erro do servidor / gateway | Se persistir, abra chamado com a equipe POWER |
| 550 | Erro ao ler os dados do POWER | Se persistir, abra chamado |

Status em tempo real: `https://power.larc.nasa.gov/status/api/`

---

## 12. Limitações

### 12.1 Limites técnicos

| Limite | Valor |
|---|---|
| Parâmetros por requisição (Point) | **20** (Hourly: **15**) |
| Parâmetros por requisição (Regional) | **1** |
| Área regional | ~4,5° × 4,5° (100 células) ⚠️ |
| Formatos por requisição | 1 |
| `wind-elevation` | Entre 10 e 300 m |
| Data inicial (Daily) | 01/01/1981 |
| Data inicial (Hourly) | 01/01/2001 |
| Data final | Não pode ser futura |
| Hourly | Sem modo Regional |
| ICASA | Só Daily e só AG |
| Taxa de requisições | Existe limite (HTTP 429), mas **não há número publicado**; varia por API e pode mudar |

### 12.2 Limitações científicas (importantes para o projeto)

1. **Resolução grosseira.** Meteorologia em 0,5° × 0,625° (~55 × 65 km no Equador) e radiação em 1° × 1° (~110 km). **Toda a fazenda, e muitas vezes o município inteiro, cai numa única célula.** O POWER não enxerga microclimas, baixadas frias nem efeito de relevo.
2. **É modelo, não medição.** Os dados meteorológicos vêm de reanálise (MERRA-2), que combina modelo e observações. Podem ter viés em relação a uma estação local, principalmente em chuva.
3. **Chuva é a variável mais fraca.** Chuva convectiva localizada (comum no verão do Cerrado) é mal representada numa grade de 50 km. Para chuva, compare com o IMERG (0,1°).
4. **Dados recentes são provisórios.** Os últimos 2–3 meses são substituídos por versões de qualidade climática. Não trate esses dados como definitivos.
5. **Altitude da célula ≠ altitude da fazenda.** Afeta temperatura e pressão. Use `site-elevation` para corrigir a pressão; a temperatura não é corrigida.
6. **A umidade do solo (`GWETTOP`, `GWETROOT`) é de modelo** e expressa fração de saturação (0 a 1), não umidade volumétrica como o SMAP L4.
7. **O arquivo muda com o tempo.** Correções de viés e atualizações de modelo podem alterar dados antigos. Registre a data de download.

### 12.3 Limitações operacionais

- A **página Swagger e os endpoints bloqueiam robôs** (`robots.txt`). Uso por aplicações via código é permitido, mas raspagem automatizada da documentação não é.
- Pedir **o mesmo local repetidamente** pode resultar em bloqueio, segundo a própria documentação.
- Requisições Regional e Application são **bem mais lentas** que Point.
- Quanto mais parâmetros e maior o período, mais lenta a resposta.

---

## 13. Boas práticas

1. **Não peça resolução maior que a do dado.** Pontos mais próximos que 0,5° retornam a mesma célula; pedir cada um é desperdício e pode levar a bloqueio. Faça **uma requisição por célula**.
2. **Agrupe parâmetros** numa só requisição (até 20), em vez de uma requisição por parâmetro.
3. **Faça cache local.** Dados históricos não mudam com frequência; salve em arquivo e reutilize.
4. **Respeite o 429:** espere e tente de novo com intervalo crescente (*exponential backoff*).
5. **Inclua `user=nome-da-sua-app`.**
6. **Trate `-999` como ausente** em todo cálculo.
7. **Leia as unidades da resposta** (`parameters`), nunca suponha.
8. **Para baixar o arquivo mensal inteiro**, a NASA recomenda o Registry of Open Data na AWS, não a API.
9. **Cite o POWER** conforme `https://power.larc.nasa.gov/docs/referencing/` (licença CC BY 4.0 exige atribuição).

---

## 14. Parâmetros úteis para o Field Shift

> Confirme a disponibilidade e as unidades na comunidade AG pelo Manager:
> `https://power.larc.nasa.gov/api/system/manager/parameters?community=ag&temporal=daily`

| Parâmetro | Significado | Uso no projeto |
|---|---|---|
| `T2M` | Temperatura média do ar a 2 m | Graus-dia, aptidão da cultura |
| `T2M_MAX` | Temperatura máxima | Ondas de calor, estresse térmico |
| `T2M_MIN` | Temperatura mínima | **Risco de geada** |
| `T2M_RANGE` | Amplitude térmica diária | Estresse, qualidade de grãos |
| `T2MDEW` | Ponto de orvalho | Umidade, risco de doenças fúngicas |
| `RH2M` | Umidade relativa | Doenças, evapotranspiração |
| `PRECTOTCORR` | Precipitação corrigida | Balanço hídrico, janelas de plantio |
| `ALLSKY_SFC_SW_DWN` | Radiação solar na superfície | Evapotranspiração, produtividade potencial |
| `WS2M` | Vento a 2 m | Evapotranspiração (Penman-Monteith) |
| `PS` | Pressão na superfície | Evapotranspiração |
| `GWETTOP` | Umidade do solo superficial (modelo) | Comparar com SMAP L4 |
| `GWETROOT` | Umidade da zona radicular (modelo) | Estresse hídrico de culturas de raiz profunda |
| `EVPTRNS` | Evapotranspiração (modelo) | Demanda hídrica |

Com `T2M_MAX`, `T2M_MIN`, `RH2M`, `ALLSKY_SFC_SW_DWN`, `WS2M` e `PS`, é possível calcular a **evapotranspiração de referência (ET₀)** pelo método FAO-56 Penman-Monteith, base para estimar a demanda de água de cada cultura da rotação.

### Exemplos de indicadores que dá para derivar

| Indicador | Cálculo |
|---|---|
| Dias de risco de geada | Dias com `T2M_MIN` < 2 °C (limiar ajustável por cultura) |
| Dias de estresse térmico | Dias com `T2M_MAX` > 35 °C |
| Veranico | Sequência de dias com `PRECTOTCORR` < 1 mm dentro da estação chuvosa |
| Chuva extrema | Dias com `PRECTOTCORR` acima do percentil 95 histórico |
| Balanço hídrico simples | Soma de `PRECTOTCORR` − ET₀ por decêndio |
| Anomalia | Valor do mês − média climatológica do mesmo mês |

---

## 15. Como e por que usar o NASA POWER no Field Shift

> Esta seção parte do contexto atual do projeto, registrado no repositório da equipe (`docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md` e `CONTEXTO-DESAFIO.md`): escopo no **Brasil inteiro** (D-008, que substituiu o foco inicial em Minas Gerais da D-001), NASA POWER entre os **6 datasets obrigatórios** (D-002, proposto), a ferramenta **apoia e não decide** (D-006) e **explicável antes de preciso** (D-007, a confirmar).

### 15.1 Por que o NASA POWER

| Motivo | Por que importa para o projeto |
|---|---|
| **Cobre o Brasil** | Com o escopo nacional (D-008), 12 datasets do desafio ficam de fora por serem só dos EUA (D-003), inclusive o PRISM, que seria a fonte de clima local. O POWER é global e preenche essa lacuna |
| **Sem login e com API simples** | Uma URL devolve JSON ou CSV. Não exige Earthdata Login, fila de pedidos nem manipulação de imagens. Em 48 horas, isso é decisivo |
| **Série longa (desde 1981)** | Mais de 40 anos permitem calcular **normais climáticas, tendências e frequência de eventos** ("em quantos anos de cada 10 faltou chuva em abril?"). O SMAP L4 (desde 2015) não tem histórico suficiente para isso |
| **Feito para agricultura** | A comunidade `AG` entrega os parâmetros nas unidades usadas por modelos de cultura e até no formato ICASA, do DSSAT |
| **Alimenta quase todos os indicadores do MVP** | Dos indicadores listados no `CONTEXTO-DESAFIO.md` §7, a maioria depende só do POWER: normal climática, tendência, graus-dia, risco de geada, dias de calor, ET₀, demanda da cultura, balanço hídrico e índice de seca |
| **Ecossistema completo** | Além dos dados históricos, o POWER tem **Climate Projection** (cenários até 2100, para os sliders de cenário) e **PRUVE** (validação contra estações, para mostrar a incerteza). Tudo no mesmo padrão de API |
| **Dados contínuos** | Por ser modelo e reanálise, não tem falhas por nuvem como os satélites ópticos. Todo dia tem valor (exceto os dias mais recentes) |

### 15.2 Onde ele entra no pipeline do produto

O `CONTEXTO-DESAFIO.md` §9.2 define um pipeline de 10 etapas. O papel do POWER em cada uma:

| Etapa | Papel do NASA POWER | Endpoint |
|---|---|---|
| 1. Ingestão | Baixar, por talhão, a climatologia e a série diária desde 1981 | `climatology/point`, `daily/point` |
| 2. Harmonização | Já vem diário e por ponto; basta agregar para o passo mensal ou decendial | — |
| 3. Indicadores | Calcular graus-dia, geada, calor, ET₀, balanço hídrico, veranicos, SPI e tendências | `daily/point`, `monthly/point` |
| 4. Diagnóstico | Apontar os meses de maior vulnerabilidade da rotação atual (ex.: fim das chuvas durante a safrinha) | Resultado da etapa 3 |
| 5. Candidatas | Verificar se cada cultura **cabe na janela climática** (ciclo em graus-dia, geada, chuva) | Resultado da etapa 3 |
| 6. Filtro de viabilidade | Descartar o que tem risco alto de geada em fase sensível ou déficit hídrico grande demais | Resultado da etapa 3 |
| 7. Pontuação (MCDA) | Fornecer as notas dos critérios **uso de água** e **risco climático** de cada estratégia | Resultado da etapa 3 |
| 8. Seleção | — | — |
| 9. Explicação | Ser a **evidência citável** ("em 7 de 10 anos, abril teve menos de 50 mm"), sempre com fonte | — |
| 10. Incerteza | Comparar a chuva do POWER com a do IMERG; validar contra estações; informar a resolução de ~55 km | `PRUVE`, `daily/point` |
| Cenários (D7) | Aplicar `chuva × 0,8` ou `temperatura + 2 °C` às séries, ou usar projeções reais | `daily/point`, `projection/...` |

### 15.3 Onde ele aparece para o agricultor

Ligando às telas sugeridas no `CONTEXTO-DESAFIO.md` §10:

| Tela | O que o POWER mostra |
|---|---|
| **Raio-x do seu campo** | Cartões como "a chuva costuma acabar em meados de abril", "em 3 dos últimos 10 anos houve geada em junho", "os dias acima de 34 °C aumentaram desde 2000" |
| **Calendário de 12 meses** | Faixas de fundo com a estação chuvosa, o período de déficit hídrico e a janela de risco de geada, sobre as quais o agricultor arrasta suas culturas |
| **Comparar estratégias** | Critérios "uso de água" e "risco climático" de cada coluna |
| **Detalhe da estratégia** | Bloco "evidência", com o número, o período e a fonte |
| **Simulador (extra)** | Sliders de chuva e temperatura recalculando os indicadores |
| **Selo de confiança** | "Dado climático em grade de ~55 km, de modelo (MERRA-2); confira com a estação mais próxima" |

### 15.4 O que o NASA POWER **não** resolve

Ele é a base climática, mas não substitui as outras fontes obrigatórias (D-002):

| Pergunta | Por que o POWER não responde | Fonte certa |
|---|---|---|
| Quando o campo fica descoberto? | Não observa a vegetação | **MODIS NDVI** (MOD13Q1) |
| Qual é o solo do talhão? | Não tem dados de solo | **GAEZ v5** / SoilGrids / Embrapa Solos (Q-07) |
| O talhão é inclinado? Há baixadas frias? | Não tem relevo fino | **SRTM** |
| Choveu forte num talhão específico? | Grade de ~55 km suaviza chuvas locais | **GPM IMERG** (~10 km) |
| O solo está seco agora? | Sua umidade do solo é de modelo e grosseira | **SMAP L4** |
| Há mercado para a cultura? Pragas locais? | Não é dado climático | Agricultor, técnico, IBGE PAM (valor da produção) |

### 15.5 Recomendações de implementação

1. **Uma requisição por talhão e por tipo de dado**, guardada em cache. Os dados históricos não mudam com frequência.
2. **Pré-processar a região da demo** antes da apresentação, para não depender da API ao vivo.
3. **Usar `community=AG` e `time-standard=LST`** em todas as chamadas.
4. **Pedir 8 parâmetros numa só chamada diária** (`T2M`, `T2M_MAX`, `T2M_MIN`, `PRECTOTCORR`, `RH2M`, `ALLSKY_SFC_SW_DWN`, `WS2M`, `PS`): já permitem calcular todos os indicadores climáticos e a ET₀ pelo FAO-56.
5. **Cortar a série no fim do ano anterior** (ou alguns meses antes de hoje) para evitar dados provisórios.
6. **Exibir sempre a origem e a escala** do dado ao lado do número (D-006).

---

## 16. Caso hipotético: a ferramenta na prática

> ⚠️ **Tudo nesta seção é fictício**: o produtor, a fazenda e **todos os números**. Os valores servem para ilustrar o formato e o raciocínio; os reais virão da API. A região escolhida é uma das opções da pergunta em aberto **Q-01** e **não** representa uma decisão da equipe.

### 16.1 O produtor

| Item | Informação (hipotética) |
|---|---|
| Nome | Sr. José |
| Local | Região do Alto Paranaíba (MG), cerca de 950 m de altitude |
| Área | 300 ha de lavoura em sequeiro (sem irrigação) e um pequeno rebanho de gado de corte |
| Solo | Latossolo vermelho argiloso, plantio direto há 12 anos |
| Rotação atual | **Soja** (out–fev) → **milho safrinha** (fev–jul) → **pousio** (ago–out) |
| Equipamentos | Plantadeira e colheitadeira para grãos |
| Mercado | Vende soja e milho para uma cooperativa da região, que também compra sorgo |

**Problemas que ele relata:**
- "Em dois dos últimos cinco anos o milho safrinha rendeu bem menos porque a chuva parou cedo."
- "Teve um ano com geada que queimou o milho que ainda estava enchendo grão."
- "De agosto a outubro a terra fica descoberta e, nas primeiras chuvas, aparecem sulcos de erosão na parte mais inclinada."
- "No fim da seca falta pasto para o gado."

### 16.2 Passo 1 — Entradas na ferramenta

**Tela "Onde fica seu campo?"** — Sr. José marca o talhão no mapa. A ferramenta registra a coordenada (exemplo: `latitude=-18.9`, `longitude=-46.9`).

**Tela "O que você planta hoje?"** — ele arrasta os blocos no calendário: soja de outubro a fevereiro, milho de fevereiro a julho, nada de agosto a outubro.

**Tela "O que é mais importante para você?"** (sliders de 0 a 5):

| Prioridade | Peso |
|---|---|
| Estabilidade de renda | 5 |
| Reduzir risco de falta de água | 4 |
| Proteger o solo e reduzir erosão | 4 |
| Forragem para o gado | 3 |
| Fixação de nitrogênio | 1 |

**Restrições (caixas de marcar):** ☑ sem irrigação · ☑ só máquinas de grãos · ☑ só culturas com comprador na região.

### 16.3 Passo 2 — O que a ferramenta busca no NASA POWER

Nos bastidores, quatro chamadas:

**1. Climatologia (calendário típico):**
```
https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR&community=AG&longitude=-46.9&latitude=-18.9&format=JSON&user=fieldshift
```

**2. Série diária de 1991 a 2025 (indicadores e ET₀):**
```
https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M,PS&community=AG&longitude=-46.9&latitude=-18.9&start=19910101&end=20251231&format=JSON&time-standard=LST&site-elevation=950&user=fieldshift
```
A altitude de 950 m viria do SRTM.

**3. Série mensal (comparar anos):**
```
https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=PRECTOTCORR,T2M_MIN&community=AG&longitude=-46.9&latitude=-18.9&start=1991&end=2025&format=JSON&user=fieldshift
```

**4. Projeção climática (opcional, para o simulador):** `/api/projection/daily/point` com o cenário escolhido (parâmetros a confirmar na Swagger).

### 16.4 Passo 3 — Indicadores calculados a partir do POWER

| Indicador | Como é calculado | Resultado (fictício) |
|---|---|---|
| Fim típico da estação chuvosa | Climatologia de `PRECTOTCORR` | Meados de abril |
| Chuva de abril | Série mensal | Mediana de 55 mm; abaixo de 40 mm em 4 de cada 10 anos |
| Veranico na safrinha | Sequências de 10+ dias com `PRECTOTCORR` < 1 mm entre março e maio | Ocorreu em 6 de cada 10 anos |
| Balanço hídrico de abril a junho | Chuva − ETc do milho (ET₀ FAO-56 × Kc) | Déficit acumulado de ~180 mm na fase de enchimento de grão |
| Risco de geada | Dias com `T2M_MIN` ≤ 2 °C em junho e julho | Pelo menos 1 dia em 3 de cada 10 anos |
| Calor extremo | Dias com `T2M_MAX` > 34 °C em janeiro e fevereiro | Média de 4 dias por ano, com tendência de alta desde 2000 |
| Tendência de temperatura | Mann-Kendall + Sen nas médias anuais de `T2M` | +0,3 °C por década |
| Erosividade no início das chuvas | Dias com `PRECTOTCORR` > 40 mm em outubro e novembro | Média de 2 eventos por ano, caindo sobre solo descoberto |

Com o NDVI do MODIS (outra fonte obrigatória), a ferramenta confirma: **NDVI abaixo de 0,25 de agosto a outubro** na maioria dos anos, ou seja, cerca de **3 meses de solo exposto**.

### 16.5 Passo 4 — "Raio-x do seu campo"

O que o Sr. José vê, em cartões simples:

> 🌧️ **A chuva costuma acabar em meados de abril.** Seu milho safrinha ainda precisa de água em maio e junho, quando chove pouco. Em 6 de cada 10 anos houve 10 dias seguidos ou mais sem chuva durante a safrinha.
> *De onde vem: NASA POWER, 1991–2025, grade de ~55 km.*

> ❄️ **Geada em junho e julho não é rara aqui.** Em 3 de cada 10 anos a temperatura mínima chegou perto de 0 °C. Milho plantado depois de meados de março pode estar enchendo grão nessa época.
> *De onde vem: NASA POWER. Baixadas da fazenda podem ser mais frias que a média da região.*

> 🟫 **Seu campo fica descoberto de agosto a outubro.** As primeiras chuvas fortes caem sobre o solo nu, o que explica os sulcos de erosão.
> *De onde vem: MODIS NDVI e NASA POWER.*

> 🌡️ **Janeiro e fevereiro estão ficando mais quentes.** A soja enfrenta mais dias acima de 34 °C do que há 20 anos.
> *De onde vem: NASA POWER, tendência 1991–2025.*

### 16.6 Passo 5 — Comparar estratégias

A ferramenta gera a rotação atual e duas alternativas que respeitam as restrições (sequeiro, máquinas de grãos, comprador na região):

| Critério | **A) Atual:** soja → milho safrinha → pousio | **B)** Soja → milho safrinha **consorciado com braquiária** | **C)** Soja precoce → **sorgo granífero** |
|---|---|---|---|
| Risco hídrico na safrinha | 🔴 Alto | 🟠 Médio-alto (igual ao milho, mas a braquiária segue cobrindo o solo) | 🟢 Médio-baixo (sorgo tolera mais o déficit) |
| Risco de geada | 🟠 Médio | 🟠 Médio | 🟢 Menor (com soja precoce, a safrinha é plantada mais cedo) |
| Proteção do solo / erosão | 🔴 Solo exposto ago–out | 🟢 Solo coberto o ano todo | 🟠 Palhada de sorgo, mas cobertura parcial em set–out |
| Forragem | 🔴 Nenhuma | 🟢 Pasto de braquiária na seca | 🟠 Restos de cultura |
| Renda | Base | Base + forragem | Sorgo vale menos que milho, porém com menos quebra |
| Pragas | Ciclo contínuo de milho | Ciclo de milho mantido | Quebra parcial do ciclo do milho |
| **Pontuação com os pesos do Sr. José** | 2,1 / 5 | **3,8 / 5** | 3,5 / 5 |
| **Confiança** | Alta | Média | Média |

As notas são fictícias e servem só para mostrar o formato.

### 16.7 Passo 6 — Detalhe da estratégia B

**Por que foi sugerida:** o solo fica descoberto por cerca de 3 meses e o Sr. José deu peso alto para proteger o solo e para forragem. A braquiária semeada junto com o milho continua crescendo depois da colheita, cobre o solo na seca e serve de pasto.

**Evidências:**
- NDVI abaixo de 0,25 de agosto a outubro (MODIS, 2001–2025).
- Média de 2 chuvas acima de 40 mm por ano em outubro e novembro, caindo sobre solo nu (NASA POWER).
- Parte do talhão com declividade acima de 8% (SRTM).

**Benefícios:** menos erosão nas primeiras chuvas, palhada para o plantio direto da soja, pasto no fim da seca e mais matéria orgânica com o tempo.

**Lacunas de informação:**
- A ferramenta não conhece a infestação de pragas e plantas daninhas do talhão.
- O desempenho da braquiária varia com a cultivar e com a densidade de semeadura.
- O dado climático é de uma grade de ~55 km.

**Riscos para revisão local:**
- A braquiária pode competir com o milho se o manejo não for bem feito.
- A dessecação antes da soja precisa ser planejada.
- O risco hídrico da safrinha **continua** existindo; a estratégia B protege o solo, mas não resolve a falta de chuva em abril.

**Perguntas para levar ao técnico:** qual cultivar e densidade de braquiária usar? Vale ajustar a época de plantio do milho de acordo com o zoneamento de risco (ZARC) do município?

### 16.8 Passo 7 — Simulador de cenário

O Sr. José move o slider **"chuva de março a maio: −20%"**. A ferramenta recalcula os indicadores com a série do POWER ajustada:

| | Antes | Com −20% de chuva |
|---|---|---|
| Anos com veranico na safrinha | 6 em 10 | 8 em 10 |
| Estratégia mais bem pontuada | B | **C** (sorgo passa à frente por tolerar mais a seca) |

A tela deixa claro: *"Este é um teste de sensibilidade, não uma previsão."* Com a definição Climate Projection, o mesmo teste poderia usar cenários de modelos climáticos para 2050.

### 16.9 Passo 8 — Confiança e próximo passo

**Selo de confiança da estratégia B: Média**, porque:
- O clima vem de uma grade de ~55 km (NASA POWER), e a chuva de abril do POWER difere da do IMERG em 15% neste local (valor fictício).
- O PRUVE indica que a estação de referência mais próxima fica a 40 km (valor fictício), então a validação é parcial.
- Não há dados locais de pragas nem análise de solo do talhão.

**Aviso fixo na tela:** *"Sugestões para discussão. Confirme com seu técnico agrícola e com sua experiência."*

**Resultado:** o Sr. José exporta o relatório (as três estratégias, as evidências e as perguntas) e leva para a conversa com o agrônomo da cooperativa. **A decisão continua sendo dele.**

### 16.10 O papel do NASA POWER neste caso

| Etapa do caso | Contribuição do NASA POWER |
|---|---|
| Raio-x | 3 dos 4 cartões dependem diretamente dele |
| Comparação | Notas de risco hídrico, risco de geada e calor |
| Evidência | Números citáveis com período e fonte |
| Simulador | Série base para o ajuste de chuva |
| Confiança | Comparação com IMERG e validação via PRUVE |

O que **não** veio do POWER: solo exposto (MODIS NDVI), declividade (SRTM), solo (GAEZ v5 ou outra fonte), mercado e restrições (o próprio agricultor).

---

## 17. Referências

- Visão geral das APIs e códigos de erro: https://power.larc.nasa.gov/docs/services/api/
- APIs temporais: https://power.larc.nasa.gov/docs/services/api/temporal/
- Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- Hourly API: https://power.larc.nasa.gov/docs/services/api/temporal/hourly/
- Monthly API: https://power.larc.nasa.gov/docs/services/api/temporal/monthly/
- Climatology API: https://power.larc.nasa.gov/docs/services/api/temporal/climatology/
- Application APIs: https://power.larc.nasa.gov/docs/services/api/application/
- Indicators: https://power.larc.nasa.gov/docs/services/api/application/indicators/
- Windrose: https://power.larc.nasa.gov/docs/services/api/application/windrose/
- Zones: https://power.larc.nasa.gov/docs/services/api/application/zones/
- Manager: https://power.larc.nasa.gov/docs/services/api/system/manager/
- Resources: https://power.larc.nasa.gov/docs/services/api/system/resources/
- Comunidades: https://power.larc.nasa.gov/docs/methodology/communities/
- Tutorial de requisições: https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/
- Primeiros passos com a API: https://power.larc.nasa.gov/docs/tutorials/api-getting-started/
- Guia de download de séries globais: https://power.larc.nasa.gov/docs/tutorials/
- Página Swagger: https://power.larc.nasa.gov/api/pages/
- Resumo do site (llms.txt): https://power.larc.nasa.gov/llms.txt
- PRUVE (Earthdata, dez/2025): https://earthdata.nasa.gov/news/blog/nasa-powers-pruve-tool-streamlines-data-validation
- Projeções climáticas do POWER (NTRS): https://ntrs.nasa.gov/citations/20240000860
- Pacote R `nasapower` (limites e estrutura das requisições): https://rdrr.io/cran/nasapower/src/R/get_power.R

**Contexto do projeto (repositório da equipe, `eeomts/FieldShift-NasaSpaceApps-Hackatnon`)**
- Registro de decisões: `docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md`
- Contexto do desafio (indicadores, pipeline, telas, MVP): `docs/NasaSpaceApps-FieldShift/v1/context/CONTEXTO-DESAFIO.md`
