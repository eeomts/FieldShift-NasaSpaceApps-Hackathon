> Descartado em 15/11/2026 (ver D-009 em DECISOES.md): arquivo histórico.

# Field Shift Brasil — Tratamento de dados e arquitetura da base única

Nov 14, 2026 · @Yury Turatti · Revisado em 14/11/2026: alinhado com `application/architecture/`, com o `tools/comparative/COMPARATIVO_FINAL.md` e com os arquivos reais de `data/`.

## Visão geral

O pipeline transforma seis fontes (mais duas opcionais) numa base única organizada por **ponto de análise × mês × indicador**, que o motor de análise lê pronta.

O tratamento de cada fonte é escrito **uma vez só**, como funções Python, e roda de dois jeitos:

- **Em lote, antes da demo:** os scripts do pipeline processam os pontos da demonstração (`data/demo/pontos_demo.csv`) e, numa fase posterior, a amostra nacional. Nada disso é chamado ao vivo na apresentação.
- **Sob demanda, para o ponto do produtor:** quando o produtor marca o campo (pergunta 5 do onboarding), os conectores da integração de dados (`application/architecture/INTEGRACAO-DE-DADOS.md`) chamam **as mesmas funções** para aquele ponto, com cache por célula.

Nos dois casos o resultado vai para o **PostgreSQL + PostGIS** do app (`application/architecture/BANCO-DE-DADOS.md`), no mesmo formato longo. Assim existe um único tratamento, e o motor não sabe se o dado veio do lote ou da coleta na hora.

O escopo é o **Brasil inteiro** (D-008), construído em duas fases:

- **Fase 1 (MVP, hackathon):** só os pontos da demonstração, em regiões contrastantes (Q-01), mais o ponto que o produtor marcar. São poucas dezenas de pontos, então as APIs públicas bastam.
- **Fase 2 (depois do hackathon):** a amostra nacional para o mapa do Brasil.

A Fase 2 tem 5.570 municípios, 27 UFs, quatro fusos horários e regiões com calendários agrícolas diferentes. Essa escala muda três coisas no pipeline. O volume de chamadas obriga a trocar algumas APIs públicas por arquivos e instâncias próprias. A amostragem de pontos precisa acompanhar municípios que vão de menos de 5 km² a mais de 150 mil km². E o ano agrícola não começa no mesmo mês em todo o país.

A base responde a três perguntas da ferramenta. O que plantar e quando vem do ZARC e da base de culturas. Como clima, solo e relevo se comportam em cada mês vem do NASA POWER, do SoilGrids e do SRTM. O que de fato acontece no campo e no município vem do NDVI e do IBGE PAM.

O princípio central: cada fonte é tratada sozinha até virar uma tabela padronizada com as mesmas chaves (`ponto_id`, `cod_ibge`, `ano`, `mes`, `cultura_id`). Só então as fontes se cruzam para gerar indicadores. Assim, acrescentar SMAP ou IMERG depois não quebra nada do que já existe.

Resoluções, limites de API, nomes de camadas e códigos de tabela citados aqui são aproximados ou de memória. Cada um precisa ser conferido na página oficial antes de virar código.

## As fontes

Cada fonte responde a uma parte diferente da pergunta e chega num formato, numa escala e num ritmo próprios. A tabela resume o que cada uma traz e qual é o seu papel.

| Fonte | O que entrega | Escala e ritmo | Acesso | Papel na ferramenta |
| --- | --- | --- | --- | --- |
| Base de culturas + ZARC | Janelas de plantio por município, cultura, classe de solo, ciclo e risco (20, 30 ou 40%), em decêndios; parâmetros agronômicos de cada cultura | Município; uma tábua por safra | Tábua de risco nos dados abertos do MAPA (CSV); planilha própria da equipe | Calendário de plantio, aptidão oficial, parâmetros das notas |
| NASA POWER | Temperatura máx. e mín., chuva, umidade, radiação, vento | Célula de \~0,5° × 0,625° (\~50 km); diário desde 1981 | API REST, JSON ou CSV, sem login | Clima base, geada, calor, ET0, balanço hídrico |
| SoilGrids | Argila, areia, silte, carbono, pH, densidade, CTC e nitrogênio em 6 profundidades, com incerteza | 250 m; estático | API REST do ISRIC ou arquivos COG | Classe de solo do ZARC, água disponível, erodibilidade |
| SRTM via OpenTopoData | Elevação | 30 m; estático (2000) | API pública ou instância própria em Docker | Declividade, baixadas, exposição, erosão |
| NDVI MODIS + VIIRS via AppEEARS | NDVI com camadas de qualidade | 250 m (MODIS) e 500 m (VIIRS); composições de 16 dias, MODIS desde 2000, VIIRS desde 2012 | API do AppEEARS, login Earthdata | Cobertura do solo, solo descoberto, fenologia, conferência do calendário |
| IBGE PAM | Área plantada e colhida, produção, rendimento e valor por cultura | Município; anual | API SIDRA | Culturas relevantes, estabilidade de rendimento, contexto econômico |
| SMAP L4 (opcional) | Umidade do solo de 0–5 cm e da zona de raízes (0–100 cm), modelada com assimilação de satélite | 9 km; a cada 3 horas desde 2015 | AppEEARS, mesmo fluxo do NDVI | Validar ou reforçar o balanço hídrico |
| GPM IMERG (opcional) | Chuva | 0,1° (\~11 km); 30 min e diário desde 2000 | GES DISC, login Earthdata | Chuva mais fina, extremos, segunda fonte para a confiança |

Duas fontes de apoio não estão na lista, mas o pipeline depende delas para ligar tudo. A malha municipal do IBGE (API de malhas ou pacote `geobr`) diz em que município cai cada ponto. A tabela de localidades do IBGE dá nomes, códigos e regiões de cada município.

## Arquitetura em camadas

O pipeline tem quatro camadas, e cada uma só lê a anterior. Assim, um erro numa fonte fica preso na tabela daquela fonte e não contamina as outras.

```
 Camada 0 · Dimensões   municípios · pontos · culturas · calendário
                                    │ chaves comuns
 Camada 1 · Bruto       ZARC  SRTM  SoilGrids  POWER  NDVI  PAM   (uma pasta por fonte)
                          │     │       │        │      │     │
 Camada 2 · Padronizado  uma tabela por fonte, mesmas chaves e unidades
                                    │ (cruzamento pelas chaves)
 Camada 3 · Indicadores  déficit hídrico · geada · erosão · graus-dia · janela · cobertura
                                    │ validação
 Camada 4 · Base final   tabelas que o motor lê (PostgreSQL + PostGIS)
```

Entre as camadas 1 e 2 há uma seta por fonte, porque cada fonte é tratada isoladamente. Entre as camadas 2 e 3 há uma seta só: é ali que as tabelas se cruzam pelas chaves comuns.

| Camada | O que guarda | Regra |
| --- | --- | --- |
| 0 · Dimensões | Municípios, pontos, culturas, calendário | Criada antes de tudo; todas as outras camadas usam suas chaves |
| 1 · Bruto | Arquivos exatamente como vieram, com um JSON de metadados da chamada | Nunca editar; para corrigir, baixar de novo |
| 2 · Padronizado | Uma tabela por fonte, com unidades padrão, qualidade aplicada e chaves comuns | Uma fonte não lê outra; a única exceção é a elevação do SRTM usada na ET0 do POWER |
| 3 · Indicadores | Resultados dos cruzamentos, por ponto e mês ou por ponto | Calcular no ponto antes de resumir no município |
| 4 · Base final | As tabelas que o motor lê, no PostgreSQL + PostGIS | Publicada só depois de passar pela validação |

SMAP L4 e GPM IMERG, se entrarem, ganham pasta e tabela próprias nas camadas 1 e 2 e alimentam a camada 3 sem mudar o resto.

## As chaves comuns

As fontes só conversam se compartilharem três chaves: **onde** (ponto e município), **quando** (ano e mês) e **qual cultura**. Toda tabela padronizada carrega essas chaves, e nenhuma fonte se cruza com outra antes de tê-las.

### Onde: dois níveis espaciais

ZARC e PAM existem só por município. POWER, SoilGrids, SRTM e NDVI são consultados em coordenadas. Por isso o pipeline trabalha em dois níveis ligados entre si.

O **ponto de análise** é uma coordenada (lat, lon) onde se consultam as fontes de satélite e de grade. Cada ponto recebe, uma única vez, o código do município em que cai (cruzamento com a malha do IBGE) e o identificador da célula do POWER que o contém.

O **município** é a unidade do mapa nacional (5.570 no Brasil, de menos de 5 km² a mais de 150 mil km²). O valor municipal de um indicador vem dos pontos de dentro dele: calcula-se o indicador em cada ponto e depois se resume (mediana, percentis 10 e 90). Nunca se faz a média das entradas para calcular o indicador uma vez só.

Os pontos saem de três origens: os **pontos da demonstração**, escolhidos à mão em `data/demo/pontos_demo.csv` (Fase 1); o **ponto que o produtor marcar** no app (Fase 1, sob demanda); e uma **amostra dentro da área agrícola** de cada município para o mapa nacional (Fase 2).

Na Fase 2, um número fixo de pontos por município não funciona: Altamira (PA) tem mais de 150 mil km², quase todos de floresta, e Santa Cruz de Minas (MG) tem menos de 5 km². A regra sugerida é sortear pontos só dentro da área agrícola, com densidade fixa (por exemplo, 1 ponto a cada 100 km² de lavoura), mínimo de 3 e máximo de 30 por município. Isso dá algo na ordem de 20 a 30 mil pontos.

A área agrícola da Fase 2 vem do próprio NDVI (amplitude sazonal alta). O MapBiomas seria mais preciso, mas ficou fora da lista de ferramentas no `COMPARATIVO_FINAL.md`; só volta se a Fase 2 for feita e a máscara por NDVI não bastar. Na Fase 1 não há máscara: os pontos são escolhidos à mão.

### Quando: dia, decêndio, mês e ano agrícola

O passo de tempo da base final é o **mês**. As fontes chegam em ritmos diferentes e cada uma desce ou sobe até ele por uma regra própria.

| Fonte | Ritmo original | Como chega ao mês |
| --- | --- | --- |
| POWER, IMERG | Diário | Indicadores diários primeiro (geada, chuva extrema, ET0), depois soma, média ou contagem no mês |
| NDVI | Composição de 16 dias | Cada valor vai para o mês do dia real do pixel; mediana das observações válidas |
| ZARC | Decêndio (36 por ano) | Decêndio d cai no mês ⌈d/3⌉; guarda-se a fração do mês indicada para plantio |
| PAM | Ano | Fica anual, ligado ao ano agrícola da colheita |
| SoilGrids, SRTM | Estático | Sem tempo; vão para a tabela de atributos estáticos |

O **ano agrícola** ganha uma coluna própria (`ano_agricola`, por exemplo 2024/25), mas não começa no mesmo mês em todo o país. No Centro-Sul, o padrão julho a junho funciona. No litoral leste do Nordeste, as chuvas vêm entre abril e agosto; em Roraima, ao norte do Equador, o período chuvoso vai de abril a setembro.

A sugestão é definir o mês de início do ano agrícola por município a partir da climatologia do POWER (o mês seguinte ao mais seco) e guardá-lo em `municipio.inicio_ano_agricola`. As janelas do ZARC continuam dando as datas reais de plantio.

Períodos sugeridos: clima normal de 1991 a 2020 para POWER, anos recentes até o último ano completo, NDVI desde 2001 e PAM desde 2000.

### Qual cultura: um dicionário único

Cada fonte escreve o nome da cultura de um jeito. O ZARC separa milho de 1ª e 2ª safra; a PAM usa nomes como "Café (em grão) Arábica". A base de culturas (`data/catalogo/culturas.csv`) mantém o identificador e a tradução para cada fonte. No CSV a coluna se chama `id`; nas outras tabelas ela aparece como `cultura_id`.

| cultura\_id (`id` no CSV) | Nome | `nome_zarc` | `codigo_pam` / nome na PAM | Família |
| --- | --- | --- | --- | --- |
| soja | Soja | Soja | Soja (em grão) | Fixadora de N |
| milho\_2 | Milho 2ª safra | Milho 2ª safra | Milho, 2ª safra (tabela 839, por safra) | — |
| sorgo | Sorgo | Sorgo | Sorgo (em grão) | Tolerante à seca |
| cafe\_arabica | Café arábica | Café arábica | Café (em grão) Arábica | Perene |
| braquiaria | Braquiária | conferir | não consta | Cobertura, raiz profunda |

Hoje o `culturas.csv` tem só `milho`; é preciso acrescentar `milho_2` (safrinha), porque o ZARC e a PAM separam as duas safras. Os nomes exatos de cada fonte precisam ser copiados dos arquivos reais: `nome_zarc` vem de `data/brasil/zarc/mapa_culturas_zarc.csv`. Plantas de cobertura como braquiária e crotalária podem não ter ZARC nem PAM; nesse caso só a base de culturas as descreve, e a confiança da recomendação cai.

No Brasil inteiro o dicionário cresce bastante: entram trigo e outras culturas de inverno do Sul, arroz irrigado, cana, algodão, mandioca e perenes do Norte e do Nordeste, como cacau e frutas.

### Resumo das chaves

| Chave | Formato | Exemplo | Usada por |
| --- | --- | --- | --- |
| `ponto_id` | texto | MG-3106200-03 | POWER, SoilGrids, SRTM, NDVI, SMAP, IMERG |
| `cod_ibge` | 7 dígitos | 3106200 | ZARC, PAM, malha, mapa estadual |
| `power_cell_id` | lat\_lon do centro da célula | -19.75\_-43.75 | POWER (evita chamadas repetidas) |
| `ano`, `mes`, `ano_agricola` | inteiros; texto | 2024, 8, 2024/25 | Todas as tabelas com tempo |
| `decendio` | 1 a 36 | 28 | ZARC |
| `cultura_id` | texto curto (`id` no `culturas.csv`) | soja | ZARC, PAM, base de culturas |

Toda tabela também leva a `uf` (os dois primeiros dígitos do `cod_ibge`). Ela não liga fontes, mas divide downloads e processamento em lotes por estado, o que é indispensável na escala nacional.

## Tratamento fonte a fonte

Cada fonte passa pelos mesmos quatro passos: baixar e guardar o bruto intacto, limpar (sem-dado, qualidade), converter unidades e escalas, e gravar uma tabela padronizada com as chaves comuns. O que muda é o detalhe de cada passo.

### 1. Base de culturas e ZARC

**Acesso.** A tábua de risco do ZARC é publicada por safra nos dados abertos do Ministério da Agricultura, em CSV. A API Agritec da Embrapa também expõe o zoneamento e serve como alternativa. A base de culturas é o arquivo `data/catalogo/culturas.csv`, que a equipe monta e mantém (dono: Pessoa 1, ver `data/README.md`).

**Como chega.** Uma linha por município × cultura × classe de solo × ciclo ou grupo × nível de risco, com os decêndios indicados para plantio. Os decêndios podem vir como 36 colunas de 0 e 1 ou como lista. Culturas e classes vêm como texto livre.

**Tratamento.**

1. Registrar a UF de cada linha pelos dois primeiros dígitos do `cod_ibge` e processar a tábua em lotes por UF.
2. Trocar o nome da cultura por `cultura_id` usando o dicionário. Nomes sem correspondência vão para um relatório, nunca são descartados em silêncio.
3. Passar para formato longo: uma linha por município × cultura × classe de solo × ciclo × risco × decêndio indicado.
4. Ligar decêndio a mês: o decêndio d cai no mês ⌈d/3⌉ (1 a 10, 11 a 20 e 21 ao fim do mês). Calcular `fracao_mes_apta` = decêndios indicados no mês ÷ 3.
5. Guardar safra e portaria de origem em cada linha.
6. Tratar ausência como informação: cultura sem linha para o município significa "não zoneada" e entra como restrição, não como dado faltante.

**Classe de solo.** O ZARC atual classifica o solo pela água disponível, em classes AD1 a AD6 derivadas da textura; versões antigas usavam Tipo 1, 2 e 3. É preciso confirmar qual sistema vale na safra usada, porque é por essa classe que o SoilGrids escolhe a linha certa do ZARC para cada ponto.

**Base de culturas.** Uma linha por cultura em `data/catalogo/culturas.csv`. As colunas abaixo são as que o pipeline usa, com os nomes reais do arquivo; as marcadas como **a acrescentar** ainda não existem no CSV e precisam ser criadas:

| Coluna no CSV | Exemplo | Uso no pipeline |
| --- | --- | --- |
| `id` | soja | Chave (`cultura_id` nas outras tabelas) |
| `familia_botanica`, `tipos` | Fabaceae; comercial | Família de estratégia e alternância de famílias (pragas) |
| `perene` | false | Separa o caso do café |
| `ciclo_dias_min`, `ciclo_dias_max` | 100, 130 | Encaixe no calendário |
| `temp_base_c` | 10 | **Graus-dia** do ciclo (filtro do motor) |
| `graus_dia_ciclo_min`, `graus_dia_ciclo_max` | 1600, 2050 | Exigência de graus-dia da semeadura à maturação (ou ao manejo, nas coberturas), com a `temp_base_c` da linha e sem teto; a cultura que não alcança o mínimo na janela é eliminada, entre mínimo e máximo é "no limite" |
| `kc_inicial`, `kc_medio`, `kc_final` | valores da FAO-56 | Demanda de água: ETc = Kc × ET0 |
| `profundidade_raiz_m` | 1,0 | Tamanho do "balde" do balanço hídrico |
| `agua_ciclo_mm_min`, `agua_ciclo_mm_max` | 450, 700 | Filtro "precisa de mais água do que há" |
| `sensivel_geada` | true | Marca a cultura no risco de geada |
| `tmin_critica_c` (**a acrescentar**) | 2 | Limite de dano por frio; sem ele, só dá para dizer "sensível" |
| `tolerancia_seca` (**a acrescentar**) | 1 a 5 | Critério água |
| `fixa_nitrogenio`, `raiz_profunda`, `cobertura_solo`, `aporte_biomassa` | true; false; media; alto | Critérios terra e erosão |
| `valor_forrageiro` | medio | Critério forragem |
| `codigo_pam`, `nome_zarc` | 40124; Soja | Dicionário de nomes |
| `fontes`, `confianca_parametros` | FAO-56 \| Embrapa; media | Referência e confiança de cada linha |

Os valores devem vir de fontes citadas (FAO-56 para Kc, publicações da Embrapa para o resto), registradas na coluna `fontes`.

**Saída.** `cultura` (dimensão) e `zarc_janela` com `cod_ibge`, `cultura_id`, `classe_solo`, `ciclo`, `risco_pct`, `decendio`, `mes`, `fracao_mes_apta`, `safra`.

### 2. NASA POWER

**Acesso.** Endpoint diário por ponto (`/api/temporal/daily/point`), comunidade AG, parâmetros `T2M_MAX`, `T2M_MIN`, `T2M`, `PRECTOTCORR`, `RH2M`, `ALLSKY_SFC_SW_DWN` e `WS2M`. Uma chamada cobre o período inteiro de um ponto.

**Como chega.** JSON com uma série por parâmetro, datas no formato AAAAMMDD, unidades no cabeçalho e −999 onde não há dado.

**Tratamento.**

1. Agrupar pontos por célula antes de chamar a API. Pontos da mesma célula de \~50 km recebem exatamente os mesmos valores, então basta uma chamada por `power_cell_id`. O Brasil tem cerca de 2,5 mil células, contra dezenas de milhares de pontos. Ainda são milhares de chamadas: rodar em lotes por UF, com pausa entre chamadas e cache, ao longo de várias horas.
2. Trocar −999 por nulo e converter as datas.
3. Conferir unidades no cabeçalho: temperatura em °C, chuva em mm/dia e radiação em MJ/m²/dia na comunidade AG.
4. Calcular a ET0 diária pelo método FAO-56 Penman-Monteith (bibliotecas `pyet` ou `refet`), usando a elevação do ponto vinda do SRTM.
5. Gerar marcadores diários antes de agregar: dia de geada provável (Tmin abaixo do limite), dia de calor (Tmax acima do limite) e dia de chuva extrema. Os limites ficam no `limiares.yaml`.
6. Guardar a temperatura média diária para os **graus-dia**: GD = max(0, Tmed − `temp_base_c`) por cultura. Como a temperatura base muda por cultura, a soma mensal é feita na camada 3, por ponto × mês × cultura.
7. Agregar por mês: chuva e ET0 somadas, temperaturas em média, marcadores contados.
8. Calcular a climatologia de 1991 a 2020 por mês e as anomalias de cada mês em relação a ela.

**Saída.** `clima_diario` (`power_cell_id`, `data`, `tmax_c`, `tmin_c`, `tmed_c`, `chuva_mm`, `ur_pct`, `rad_mj_m2`, `vento_m_s`, `et0_mm`) e `clima_mensal` com os totais, médias e contagens.

### 3. SoilGrids

**Acesso.** Na **Fase 1** (pontos da demo e ponto do produtor), a API REST do ISRIC (`/soilgrids/v2.0/properties/query`) com as propriedades, profundidades e estatísticas desejadas, sempre com cache: a API tem limite de uso justo de poucas chamadas por minuto e uma chamada já levou 17 s. Na **Fase 2**, com milhares de pontos, o caminho é ler os arquivos COG publicados pelo ISRIC recortados para o Brasil, ou lidos direto do servidor só nos pixels dos pontos (GDAL com `/vsicurl/`) e amostrar localmente com `rasterio`, sem limite.

**O que pedir.** Propriedades `clay`, `sand`, `silt`, `soc`, `phh2o`, `bdod`, `cec`, `nitrogen` e `cfvo`, nas profundidades 0–5, 5–15, 15–30, 30–60 e 60–100 cm, com média e quantis 0,05, 0,50 e 0,95.

**Como chega.** Números inteiros em "unidades mapeadas", que precisam de fator de conversão. Esquecer essa conversão é o erro mais comum com o SoilGrids.

| Propriedade | Unidade mapeada | Divide por | Unidade padrão |
| --- | --- | --- | --- |
| clay, sand, silt | g/kg | 10 | % |
| soc | dg/kg | 10 | g/kg |
| phh2o | pH × 10 | 10 | pH |
| bdod | cg/cm³ | 100 | g/cm³ |
| cec | mmol(c)/kg | 10 | cmol(c)/kg |
| nitrogen | cg/kg | 100 | g/kg |
| cfvo | cm³/dm³ | 10 | % |

**Tratamento.**

1. Aplicar os fatores de conversão.
2. Conferir se argila + areia + silte dá 100% (± 2) e renormalizar quando não der.
3. Juntar as profundidades por média ponderada pela espessura, em duas camadas: superficial (0–30 cm) e zona de raízes (0–100 cm).
4. Derivar a classe textural, a água disponível por função de pedotransferência (de preferência a mesma usada pelo ZARC para definir as classes AD) e a classe de solo do ZARC.
5. Derivar a erodibilidade K da equação de perda de solo a partir de areia, silte, argila e carbono (método de Williams, usado no modelo EPIC).
6. Calcular a incerteza relativa (Q0,95 − Q0,05) ÷ Q0,50 de cada propriedade; ela alimenta o nível de confiança.
7. Pontos em área urbana ou água ficam sem valor e saem marcados.

A média ponderada da camada superficial, por exemplo:

```latex
\bar{v}_{0\text{-}30} = \frac{5\,v_{0\text{-}5} + 10\,v_{5\text{-}15} + 15\,v_{15\text{-}30}}{30}
```

Se o produtor informar uma análise de solo, ela substitui o SoilGrids naquele ponto e a confiança passa a alta.

**Saída.** `solo_ponto` com `ponto_id`, `camada`, `argila_pct`, `areia_pct`, `silte_pct`, `carbono_g_kg`, `ph`, `densidade_g_cm3`, `ctc_cmol_kg`, `classe_textural`, `ad_mm`, `classe_solo_zarc`, `k_usle`, `incerteza_rel`, `origem` (SoilGrids ou análise do produtor).

### 4. SRTM via OpenTopoData

**Acesso.** `/v1/srtm30m?locations=lat,lon|lat,lon` na API pública do OpenTopoData. Os limites públicos são da ordem de 100 locais por requisição, 1 requisição por segundo e 1.000 por dia. Para volume maior, roda-se uma instância própria em Docker com os blocos do SRTM baixados, sem limite.

**Como chega.** JSON com a elevação em metros de cada local pedido, e nulo onde não há dado.

**O ponto-chave.** O OpenTopoData só devolve elevação, não declividade. A declividade e a posição no relevo são calculadas pela equipe a partir de uma vizinhança de pontos pedida junto com cada ponto de análise.

**Tratamento.**

1. Para cada ponto, pedir uma grade 3 × 3 com espaçamento de 30 m e calcular declividade e exposição pelo método de Horn. As distâncias vão em metros: 1° de latitude ≈ 111,32 km e 1° de longitude ≈ 111,32 km × cos(latitude).
2. Pedir também um anel de 8 pontos a cerca de 500 m e calcular o índice de posição topográfica (TPI) = elevação do ponto − média do anel. TPI negativo indica baixada, onde o ar frio se acumula e a geada é mais forte.
3. Classificar a declividade pelas classes de relevo da Embrapa: plano (0–3%), suave ondulado (3–8%), ondulado (8–20%), forte ondulado (20–45%), montanhoso (45–75%) e escarpado (> 75%).
4. Registrar a exposição: ao sul do Equador, encostas voltadas para o sul recebem menos sol e são mais frias no inverno; perto do Equador o efeito quase some, e ao norte dele (Roraima, Amapá) se inverte.
5. Derivar o fator LS da equação de perda de solo a partir da declividade, assumindo um comprimento de rampa padrão (marcado como suposição).

Um ponto de análise com grade 3 × 3 e anel de 8 pede 17 elevações. Com 25 mil pontos no Brasil, são cerca de 425 mil elevações, ou 4.250 requisições: mais de quatro dias no limite da API pública.

Na Fase 1, com poucas dezenas de pontos, a API pública basta (algumas centenas de elevações). Na Fase 2, a instância própria do OpenTopoData em Docker é obrigatória; os blocos do SRTM 30 m do Brasil somam dezenas de GB. Uma alternativa mais leve é usar o SRTM 90 m (`srtm90m`) no mapa nacional e o de 30 m só nos pontos de demonstração e no ponto do usuário.

Em cafezais e matas, o SRTM mede parte da copa, não só o chão. Isso pesa pouco na declividade, mas entra como ressalva na confiança.

**Saída.** `relevo_ponto` com `ponto_id`, `elevacao_m`, `declividade_pct`, `classe_relevo`, `exposicao_graus`, `tpi_m`, `posicao_relevo` (topo, encosta, baixada), `fator_ls`.

### 5. NDVI MODIS + VIIRS via AppEEARS

**Acesso.** API do AppEEARS (NASA LP DAAC), com login Earthdata. O fluxo tem quatro chamadas: `POST /login` devolve um token; `POST /task` envia uma tarefa do tipo ponto com datas, camadas e a lista de coordenadas (cada uma com `id` = `ponto_id`); `GET /task/{id}` acompanha até o status "done"; `GET /bundle/{id}` lista os arquivos para baixar. Uma tarefa de pontos devolve um CSV único com todos os pontos.

**Produtos e camadas.**

| Produto | Satélite | Resolução | Camadas a pedir |
| --- | --- | --- | --- |
| MOD13Q1 (v061) | MODIS Terra | 250 m, 16 dias | NDVI, pixel\_reliability, VI\_Quality, composite\_day\_of\_the\_year |
| MYD13Q1 (v061) | MODIS Aqua | 250 m, 16 dias | as mesmas |
| VNP13A1 | VIIRS | 500 m, 16 dias | NDVI, pixel\_reliability, composite\_day\_of\_the\_year |

Os nomes exatos das camadas e a versão do VIIRS disponível devem ser lidos em `GET /product/{produto}`. Terra e Aqua são defasados em 8 dias, o que dobra as chances de imagem sem nuvem. O VIIRS garante a continuidade da série, porque o MODIS está no fim da vida útil; a sobreposição desde 2012 permite calibrar um contra o outro.

Com dezenas de milhares de pontos, a extração precisa ser dividida em várias tarefas (por exemplo, uma por UF), conferindo o limite de pontos por tarefa e o tempo de fila do AppEEARS.

**Como chega.** CSV com uma linha por ponto × data de composição e uma coluna por camada, mais colunas de qualidade já decodificadas pelo AppEEARS. Conferir se o NDVI já vem entre −1 e 1 ou como inteiro que precisa ser multiplicado por 0,0001.

**Tratamento.**

1. Aplicar a escala, se necessário, e descartar valores fora de −0,2 a 1.
2. Filtrar por qualidade: manter `pixel_reliability` = 0 (bom); manter 1 (marginal) com marcação; descartar 3 (nuvem) e −1 (sem dado).
3. Usar a data real do pixel (`composite_day_of_the_year`), não a data de início da composição, para decidir em que mês cada valor cai.
4. Intercalibrar o VIIRS com o MODIS: no período de sobreposição, ajustar NDVI\_MODIS = a + b × NDVI\_VIIRS e aplicar a correção ao VIIRS. Guardar o sensor de origem em cada linha.
5. Montar a série mensal: mediana das observações válidas do mês, com `n_obs`. Lacunas de até um mês podem ser interpoladas e ficam marcadas; lacunas maiores ficam vazias.
6. Suavizar a série (Savitzky-Golay) só para extrair a fenologia, nunca para gravar o valor mensal.
7. Derivar, por ano agrícola: meses de solo descoberto (NDVI abaixo de um limiar, sugestão inicial 0,3, a calibrar), início do verdejamento, pico, senescência, número de picos e amplitude anual.

Um pixel MODIS de 250 m cobre 6,25 ha, e um do VIIRS cobre 25 ha. Em talhões pequenos, o pixel mistura lavoura, estrada e mata. Isso precisa aparecer na confiança, principalmente onde há muitas pequenas propriedades, como em boa parte do Sul e do Nordeste, e em relevo acidentado.

Na Amazônia e em parte do litoral, a nebulosidade persistente deixa muitos meses sem observação válida na estação chuvosa. Nesses lugares o NDVI mensal terá confiança baixa com frequência, e a ferramenta deve dizer isso em vez de interpolar lacunas longas.

**Saída.** `ndvi_obs` (`ponto_id`, `data_pixel`, `sensor`, `ndvi`, `qualidade`) e `ndvi_mensal` (`ponto_id`, `ano`, `mes`, `ndvi_mediana`, `n_obs`, `solo_descoberto`, `interpolado`), mais `fenologia` por ponto e ano agrícola.

### 6. IBGE PAM

**Acesso.** API SIDRA, no formato `/values/t/<tabela>/n6/in n3 31/v/<variáveis>/p/<anos>/c<classificação>/<produtos>`: `n6` pede municípios e `in n3 31` restringe a uma UF (31 é Minas Gerais). Para o Brasil, a consulta se repete para as 27 UFs, o que também respeita o limite de valores por consulta. A tabela 5457 reúne lavouras temporárias e permanentes; milho e feijão por safra ficam em tabelas próprias. O pacote `sidrapy` facilita as chamadas. Códigos de tabela, variável e produto devem ser conferidos nos metadados do SIDRA.

**Variáveis.** Área plantada (ha), área colhida (ha), quantidade produzida (t), rendimento médio (kg/ha) e valor da produção (mil R$).

**Como chega.** JSON com a primeira linha de cabeçalho, números como texto e símbolos especiais do IBGE no lugar de alguns valores.

| Símbolo | Significado | Vira |
| --- | --- | --- |
| - | Zero absoluto | 0 |
| .. | Não se aplica | nulo, marcado |
| ... | Dado não disponível | nulo, marcado |
| X | Omitido por sigilo | nulo, marcado |

**Tratamento.**

1. Trocar os símbolos conforme a tabela acima e converter texto em número.
2. Trocar o nome do produto por `cultura_id` pelo dicionário.
3. Conferir a unidade de cada produto; a maioria vem em toneladas, mas há exceções.
4. Deflacionar o valor da produção pelo IPCA para reais de um ano-base e calcular o **valor por hectare** (valor ÷ área colhida). É a **evidência do critério renda** do motor (`COMPARATIVO_FINAL.md`, §2.1): mostra que a cultura tem produção e valor no município. A ferramenta continua sem estimar preço, e cultura sem dado na PAM (como as de cobertura) fica "sem dado de mercado", nunca zero.
5. Ligar o ano da PAM ao ano agrícola: o dado de 2024 corresponde, na maioria das culturas de verão, à safra 2023/24.
6. Derivar, por município e cultura: área média dos últimos 5 anos, participação na área agrícola do município, tendência do rendimento, coeficiente de variação do rendimento e anomalia de cada ano em relação à tendência.

**Saída.** `pam_municipal` com `cod_ibge`, `ano`, `ano_agricola`, `cultura_id`, `area_plantada_ha`, `area_colhida_ha`, `producao_t`, `rendimento_kg_ha`, `valor_mil_reais_deflac`, `flag`.

## Como as ferramentas se comunicam

Nenhuma fonte sozinha responde à pergunta do produtor; cada indicador da ferramenta nasce do cruzamento de duas a quatro tabelas padronizadas, sempre pelas chaves comuns. A tabela mostra quem conversa com quem.

| Indicador | Fontes que se cruzam | Como se calcula | Onde aparece |
| --- | --- | --- | --- |
| Janela de plantio do ponto | SoilGrids → ZARC; base de culturas | A classe de solo do ponto escolhe, entre as linhas do ZARC do município, a que vale ali; resulta na janela por cultura e nível de risco | Calendário; filtro das alternativas |
| Déficit hídrico mensal | SoilGrids (água disponível), POWER (chuva, ET0), SRTM (elevação para a ET0), base de culturas (Kc, raiz) | Balanço hídrico diário tipo "balde" (fórmula abaixo); déficit quando o balde esvazia | Vulnerabilidade; critério água |
| Risco de geada local | POWER (Tmin), SRTM (TPI, exposição), base de culturas (Tmin crítica) | Dias com Tmin abaixo do limite da cultura, agravados em baixada e encosta voltada ao sul | Vulnerabilidade |
| Risco de erosão relativo | POWER ou IMERG (chuva intensa), SoilGrids (K), SRTM (LS), NDVI (cobertura) | Lógica da equação universal de perda de solo, como índice relativo entre estratégias | Critério erosão |
| Calendário de cobertura | NDVI, ZARC | Meses de solo descoberto; confere se o verdejamento começa dentro da janela do ZARC | Calendário de cobertura |
| Rotação provável | NDVI (picos por ano), PAM (culturas do município) | Um pico = safra única; dois picos = safra e safrinha; amplitude baixa = pasto ou perene; a PAM diz quais culturas são plausíveis | Conferir a rotação informada |
| Sensibilidade à seca | PAM (anomalia de rendimento), POWER (déficit nos meses críticos) | Correlação entre quebras de rendimento e déficit hídrico dentro da janela da cultura | Evidência no cartão |
| Relevância da cultura | PAM, ZARC, entrada do produtor | Cultura zoneada, com área no município e com mercado para o produtor | Filtro das alternativas |
| Graus-dia na janela | POWER (Tmed diária), base de culturas (`temp_base_c`, `graus_dia_ciclo_min/max`), ZARC (janela) | Soma dos graus-dia do plantio ao fim do ciclo; a cultura que não completa o ciclo na janela é eliminada | Filtro das alternativas |
| Evidência de renda | PAM (valor por hectare, área no município) | Valor deflacionado por hectare e presença da cultura na microrregião | Critério renda |
| Nitrogênio, forragem, raiz | Base de culturas | Atributos fixos da cultura | Notas por critério |

### Três cruzamentos que merecem atenção

**SoilGrids escolhe a linha do ZARC.** O ZARC dá janelas diferentes para o mesmo município conforme a classe de solo. Sem o SoilGrids, a ferramenta não sabe qual linha usar. Por isso a confiança da janela de plantio herda a incerteza da textura do SoilGrids, a não ser que o produtor informe a análise de solo.

**Balanço hídrico junta solo, clima e cultura.** O balde tem tamanho igual à água disponível do solo na profundidade da raiz. Cada dia entra a chuva e sai a evapotranspiração da cultura. Quando o balde não cobre a demanda, a diferença é déficit.

```latex
CAD = AD \times z_{raiz} \qquad ETc = K_c \times ET_0 \qquad A_t = \min(CAD,\ \max(0,\ A_{t-1} + P_t - ETc_t))
```

Aqui CAD é a capacidade de água do balde (mm), AD a água disponível por profundidade (mm/m), A o armazenamento do dia e P a chuva. A versão simples é suficiente para comparar estratégias; não serve para manejo de irrigação.

**Erosão usa quatro fontes.** Cada fator da equação universal de perda de solo vem de uma ferramenta diferente, e o fator de práticas de conservação vem do produtor.

```latex
A = R \times K \times LS \times C \times P
```

R (erosividade da chuva) vem do POWER ou do IMERG, K (erodibilidade) do SoilGrids, LS (declive e rampa) do SRTM, C (cobertura) do NDVI e de cada estratégia, P (práticas) do produtor. Como os fatores vêm de escalas diferentes e sem calibração local, o resultado é usado só para ordenar estratégias, nunca como toneladas por hectare.

### Regras de cruzamento

1. **Calcular no ponto, resumir no município.** Indicadores são calculados em cada ponto de análise e só depois resumidos por município.
2. **O mais grosso manda na escala.** Um indicador que usa clima de 50 km e relevo de 30 m é regional no clima e local no relevo, e a base registra as duas resoluções.
3. **O elo mais fraco manda na confiança.** A confiança de um indicador cruzado é a menor entre as confianças das entradas.
4. **Ordem de dependência.** SRTM vem antes da ET0 do POWER; SoilGrids vem antes do ZARC por ponto; todos vêm antes dos indicadores cruzados.

## Esquema da base final

A base final tem dez tabelas, todas ligadas pelas chaves comuns. Na **Fase 1** elas ficam no **PostgreSQL + PostGIS** do app: `indicador_mensal` é a tabela `indicador` do `BANCO-DE-DADOS.md`, `cultura` é a mesma tabela de culturas do app, e a geometria do município usa o PostGIS. O motor lê essas tabelas e não refaz o tratamento. Na **Fase 2**, as tabelas nacionais grandes podem ser exportadas também em Parquet (municípios em GeoParquet) para gerar o mapa.

| Tabela | Uma linha por | Colunas principais |
| --- | --- | --- |
| `municipio` | município | `cod_ibge`, `nome`, `uf`, `regiao`, `regiao_intermediaria`, `area_km2`, `fuso_utc`, `inicio_ano_agricola`, `geometria` |
| `ponto` | ponto de análise | `ponto_id`, `lat`, `lon`, `cod_ibge`, `uf`, `power_cell_id`, `origem` (amostra, demo, usuário) |
| `cultura` | cultura | carga de `data/catalogo/culturas.csv`: `id` (`cultura_id`), `nome`, `familia_botanica`, parâmetros agronômicos, `codigo_pam`, `nome_zarc`, `fontes` |
| `zarc_janela` | município × cultura × classe de solo × ciclo × risco × decêndio | `fracao_mes_apta`, `mes`, `safra` |
| `indicador_mensal` | ponto × ano × mês × indicador | `valor`, `unidade`, `fonte`, `resolucao_origem_m`, `n_obs`, `confianca` |
| `climatologia_mensal` | ponto × mês × indicador | `normal`, `p10`, `p90`, `periodo` |
| `atributo_estatico` | ponto × atributo | solo e relevo: `valor`, `unidade`, `fonte`, `resolucao_origem_m`, `confianca` |
| `pam_municipal` | município × ano × cultura | área, produção, rendimento, valor deflacionado, valor por hectare, `flag` |
| `resumo_municipal` | município × mês × indicador | `mediana`, `p10`, `p90`, `n_pontos` (alimenta o mapa nacional) |
| `metadados_fonte` | fonte | versão, data do download, parâmetros, URL, licença |

A tabela principal, `indicador_mensal`, fica em formato longo: um indicador novo é só mais um valor na coluna `indicador`, sem mudar o esquema. Exemplo:

```csv
ponto_id,ano,mes,indicador,valor,unidade,fonte,resolucao_origem_m,n_obs,confianca
MG-3170404-02,2024,8,chuva_mm,3.1,mm,POWER,50000,31,media
MG-3170404-02,2024,8,dias_geada,0,dias,POWER+SRTM,50000,31,media
MG-3170404-02,2024,8,ndvi_mediana,0.27,adimensional,MODIS+VIIRS,250,4,alta
MG-3170404-02,2024,8,solo_descoberto,1,sim_nao,MODIS+VIIRS,250,4,alta
MG-3170404-02,2024,8,deficit_hidrico_mm,82,mm,POWER+SoilGrids,50000,31,media
```

Os valores do exemplo são ilustrativos, não dados reais.

**Volume na Fase 2.** Com 25 mil pontos, 35 anos, 12 meses e uns 15 indicadores, `indicador_mensal` passa de 150 milhões de linhas. O app não deve carregar isso inteiro. A solução é gravar essa tabela particionada por UF e carregar só o estado ou o município escolhido; o mapa nacional lê `resumo_municipal` e `climatologia_mensal`, que somam poucos milhões de linhas.

### Unidades e convenções padrão

| Grandeza | Unidade padrão |
| --- | --- |
| Temperatura | °C |
| Chuva, ET0, ETc, déficit | mm (total do período indicado no nome) |
| Radiação | MJ/m²/dia |
| Umidade do ar | % |
| Umidade do solo (SMAP) | m³/m³ |
| Vento | m/s |
| Elevação | m |
| Declividade | % |
| Argila, areia, silte | % |
| Carbono orgânico | g/kg |
| Densidade do solo | g/cm³ |
| CTC | cmol(c)/kg |
| Água disponível | mm na camada |
| NDVI | adimensional, −1 a 1 |
| Área | ha |
| Produção | t |
| Rendimento | kg/ha |
| Valor | mil R$ deflacionados, ano-base no metadado |

As coordenadas ficam em graus decimais WGS 84 (EPSG:4326). Distâncias e áreas são calculadas numa projeção métrica, como SIRGAS 2000 / Brazil Polyconic (EPSG:5880). Os nomes de colunas seguem `snake_case` com a unidade no final (`chuva_mm`, `tmin_c`), para que ninguém precise adivinhar a unidade.

## Confiança e validação

Cada valor da base sai com um nível de confiança (alta, média ou baixa) calculado por regra explícita, e o pipeline só publica a base depois de passar por checagens automáticas. Os limites abaixo são pontos de partida, a calibrar com os dados reais.

### Regras de confiança por fonte

| Fonte ou indicador | Alta | Média | Baixa |
| --- | --- | --- | --- |
| POWER | Padrões sazonais e regionais | Indicadores locais (geada, déficit), por ser célula de \~50 km | Série com muitos nulos |
| Chuva com IMERG disponível | POWER e IMERG diferem < 20% no mês | 20% a 40% | > 40% |
| SoilGrids | Incerteza relativa < 0,5, ou análise do produtor | 0,5 a 1 | > 1 |
| SRTM | Elevação | Declividade sob copa densa ou relevo muito acidentado | Pixel sem dado |
| NDVI | 2 ou mais observações válidas no mês | 1 observação, ou pixel misto em talhão pequeno | Valor interpolado |
| ZARC | Classe de solo com confiança alta | Herda a confiança média do SoilGrids | Cultura sem zoneamento |
| PAM | Contexto municipal | Uso como evidência local | Muitos valores sigilosos ou ausentes |
| Indicadores cruzados | Menor confiança entre as entradas | — | — |

### Checagens automáticas

O script de validação roda depois de cada execução e gera um relatório. Uma falha grave impede a publicação da base final.

1. **Faixas físicas:** Tmin ≤ Tmax, chuva ≥ 0, NDVI entre −0,2 e 1, textura somando 100 ± 2, declividade ≥ 0.
2. **Resíduos de sem-dado:** nenhum −999, −9999 ou símbolo do SIDRA sobrevive na base.
3. **Chaves completas:** todo ponto tem `cod_ibge` e `power_cell_id`; todo nome de cultura do ZARC e da PAM tem `cultura_id`. Nomes sem correspondência vão para o relatório.
4. **Cobertura:** porcentagem de meses com NDVI válido por ponto, pontos sem solo, municípios sem pontos.
5. **Coerência entre fontes:** o verdejamento do NDVI cai perto da janela do ZARC? Municípios com muita área de grãos na PAM mostram amplitude alta de NDVI? A chuva do POWER bate com a do IMERG?
6. **Reprodutibilidade:** rodar duas vezes com o mesmo bruto gera a mesma base, e cada tabela final aponta para os metadados das fontes usadas.

**Confiança mostrada ao produtor.** A confiança desta base é a do **dado**. O motor combina essa confiança com a concordância entre o que o produtor disse e o que os dados mostram ("você disse × os dados", `COMPARATIVO_FINAL.md` §4) para chegar ao selo que aparece no cartão.

A checagem 5 é também material para a apresentação: mostra que as fontes independentes concordam, ou expõe onde não concordam e por quê.

## Estrutura do projeto e execução

O pipeline é uma sequência de scripts numerados, um por fonte, que leem `config.yaml` e gravam em pastas separadas por camada dentro de `data/`. As funções de tratamento de cada fonte ficam num módulo que o backend também importa, para os conectores da integração sob demanda.

```
(raiz do repositório)
├── config.yaml              # período, UFs, nº de pontos, credenciais (fora do git)
├── data/
│   ├── catalogo/
│   │   ├── culturas.csv     # base de culturas + dicionário de nomes (já existe)
│   │   └── limiares.yaml    # geada, calor, chuva extrema, NDVI de solo descoberto (a criar)
│   ├── demo/pontos_demo.csv # pontos da Fase 1 (já existe)
│   ├── brasil/zarc/         # mapa de nomes e recortes do ZARC (já existe)
│   ├── brutos/<fonte>/      # como baixado, nunca editado, fora do git (já existe)
│   ├── padronizado/         # uma tabela por fonte (a criar)
│   └── indicadores/         # resultados dos cruzamentos (a criar)
├── pipeline/
│   ├── 00_dimensoes.py      # municípios, pontos, células POWER, culturas
│   ├── 01_zarc.py
│   ├── 02_srtm.py
│   ├── 03_soilgrids.py
│   ├── 04_power.py
│   ├── 05_ndvi_appeears.py
│   ├── 06_pam.py
│   ├── 07_indicadores.py
│   ├── 08_base_final.py
│   └── 09_validacao.py
└── app/                     # backend Python + FastAPI e frontend PWA (application/architecture/README.md)
```

A base final da Fase 1 não é uma pasta: é carregada no PostgreSQL + PostGIS pelo `08_base_final.py`.

Bibliotecas principais: `requests`, `pandas`, `pyarrow`, `duckdb`, `geopandas`, `shapely`, `rasterio`, `geobr`, `pyet`, `sidrapy` e, se o IMERG entrar, `earthaccess` e `xarray`.

### Ordem de execução

1. **Submeter a tarefa do AppEEARS primeiro.** Ela entra em fila e pode levar horas; o resto do pipeline roda enquanto isso.
2. `00_dimensoes`: baixar a malha municipal, sortear os pontos, ligar cada ponto ao município e à célula do POWER, carregar a base de culturas.
3. `01_zarc`, `02_srtm`, `03_soilgrids` e `06_pam`: independentes entre si, podem rodar em paralelo.
4. `04_power`: depois do SRTM, porque a ET0 usa a elevação.
5. `05_ndvi_appeears`: baixar e tratar quando a tarefa terminar.
6. `07_indicadores`: os cruzamentos, depois de todas as tabelas padronizadas existirem.
7. `08_base_final` e `09_validacao`: montar as tabelas finais e checar antes de liberar para o app.

Todos os scripts recebem no `config.yaml` uma lista de pontos ou de UFs. Na Fase 1 a lista é o `pontos_demo.csv`; na Fase 2, as UFs, sem mudar código.

### Cache e reprodutibilidade

Cada script de download calcula uma assinatura dos parâmetros da chamada (fonte, coordenadas, período, variáveis). Se o arquivo bruto com aquela assinatura já existe, não chama a API de novo. Ao lado de cada bruto fica um JSON com URL, parâmetros, data e versão do produto, que alimenta `metadados_fonte`.

### Limites e acesso

| Fonte | Login | Limite conhecido (conferir) | Estratégia |
| --- | --- | --- | --- |
| NASA POWER | Não | Uso razoável | Uma chamada por célula, com cache |
| SoilGrids (REST) | Não | Poucas chamadas por minuto | REST com cache na Fase 1; arquivos COG na Fase 2 |
| OpenTopoData público | Não | 100 locais por requisição, 1 por segundo, 1.000 por dia | API pública na Fase 1; instância própria ou SRTM 90 m na Fase 2 |
| AppEEARS | Earthdata | Tarefas em fila, podem levar horas | Uma tarefa grande de pontos, submetida primeiro |
| SIDRA | Não | Limite de valores por consulta | Uma consulta por UF, dividindo também por ano ou produto se preciso |
| ZARC | Não | Arquivos grandes | Baixar uma vez e processar por UF |
| GPM IMERG | Earthdata | Arquivos diários globais | Recorte do Brasil via `earthaccess` |

Vale criar as contas do Earthdata no primeiro dia: AppEEARS, SMAP e IMERG dependem dela.

## Integração opcional: SMAP L4 e GPM IMERG

As duas fontes entram sem mudar o esquema: cada uma grava sua tabela padronizada com as mesmas chaves, acrescenta indicadores em `indicador_mensal` e reforça a confiança dos indicadores que já existem.

### SMAP L4

**Acesso.** O produto SPL4SMGP (umidade do solo a cada 3 horas, 9 km) está disponível no AppEEARS. Basta acrescentar o produto à mesma tarefa de pontos do NDVI, com as camadas `sm_surface` (0–5 cm) e `sm_rootzone` (0–100 cm), em m³/m³.

**Tratamento.** Média diária das oito leituras, média mensal, climatologia e anomalia de 2015 em diante. O SMAP L4 é um modelo que assimila medições de satélite, não uma medição pura, e isso fica registrado no metadado.

**Comunicação com o resto.** O principal uso é validar o balanço hídrico: se a anomalia da zona de raízes do SMAP anda junto com a do balde calculado com POWER e SoilGrids, a confiança do déficit hídrico sobe para alta. Se divergirem, o cartão avisa. A série começa em 2015, então a climatologia do SMAP é curta e isso também aparece na confiança.

### GPM IMERG

**Acesso.** O produto diário Final Run (GPM\_3IMERGDF, versão 07), 0,1°, em mm/dia, pelo GES DISC com `earthaccess` e `xarray`, recortando a caixa do Brasil (cerca de 5,3° N a 33,8° S e de 74° O a 34,8° O). O Final Run sai com alguns meses de atraso; para os meses mais recentes existe o Late Run.

**Tratamento.** Cada ponto recebe um `imerg_cell_id` em `00_dimensoes`. O dia do produto diário segue o horário UTC, de duas a cinco horas à frente dos quatro fusos do Brasil (o fuso de cada município fica na tabela municipio); para totais mensais isso pesa pouco, mas para contar dias de chuva extrema o rigor pede o produto de 30 minutos agregado no dia local, que é bem mais pesado. Depois, soma mensal e contagem de dias acima do limite de chuva extrema.

**Comunicação com o resto.** O IMERG entra de três formas. Vira a segunda fonte de chuva, e a diferença entre ele e o POWER define a confiança (seção de confiança). Melhora a erosividade R da erosão, por ter célula de 11 km em vez de 50 km. E pode substituir o POWER como entrada de chuva do balanço hídrico onde as duas fontes divergem muito.

## Decisões em aberto e pontos a confirmar

Estas escolhas precisam ser fechadas pela equipe antes de rodar o pipeline completo; as primeiras três afetam todas as outras.

- [x] ~~Rodar o Brasil inteiro já no hackathon~~ → **proposta:** Fase 1 com os pontos da demo; Brasil inteiro na Fase 2 (confirmar e registrar no `DECISOES.md`)
- [ ] Pontos e regiões da demo (Q-01), em `data/demo/pontos_demo.csv`
- [ ] Fase 2: densidade de pontos por km² de lavoura e máscara agrícola por NDVI
- [ ] Período climatológico (sugestão: 1991 a 2020) e último ano incluído
- [ ] Regra do mês de início do ano agrícola por município
- [ ] Safra do ZARC usada e sistema de classes de solo vigente (AD1 a AD6 ou Tipo 1 a 3)
- [ ] Função de pedotransferência para água disponível e classe de solo do ZARC
- [ ] Limiares iniciais em `limiares.yaml`: geada (Tmin), calor (Tmax), chuva extrema e **um único** limiar de NDVI de solo descoberto (este documento sugere 0,3; algumas notas de `tools/` usam 0,25)
- [ ] Lista de culturas da base, seus parâmetros e o dicionário de nomes ZARC ↔ PAM
- [ ] Acrescentar ao `culturas.csv` as colunas `tmin_critica_c` e `tolerancia_seca` e a linha `milho_2`
- [ ] Fase 2: SRTM 30 m em instância própria ou 90 m no mapa nacional
- [ ] Versão do VIIRS no AppEEARS, nomes exatos das camadas e limite de pontos por tarefa
- [ ] Códigos de tabelas, variáveis e produtos no SIDRA
- [ ] Limites atuais das APIs do SoilGrids, OpenTopoData e SIDRA
- [ ] Se SMAP L4 e GPM IMERG entram na primeira versão
