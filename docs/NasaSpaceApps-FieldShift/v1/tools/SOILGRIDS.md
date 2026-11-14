# SoilGrids no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o SoilGrids, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o SoilGrids aos outros datasets.

## O que é o SoilGrids

O SoilGrids é um mapa global de **propriedades do solo** feito pelo ISRIC (World Soil Information), na Holanda. Não é da NASA, mas é aberto.

Ele não mede o solo por satélite. Usa centenas de milhares de perfis de solo coletados em campo no mundo todo e um modelo de aprendizado de máquina que liga esses perfis a clima, relevo, vegetação e geologia. O modelo então **prevê** as propriedades onde ninguém coletou.

A versão 2.0 tem:

- **Resolução de 250 m**, com versões agregadas em 1 km e 5 km.
- **Seis profundidades:** 0–5, 5–15, 15–30, 30–60, 60–100 e 100–200 cm.
- **Incerteza por pixel:** além da média, traz os quantis de 5% e 95%. Isso mostra o quanto o modelo está seguro.

## Por que usar

**1. Fecha parte da lacuna do SSURGO.** Os mapas detalhados de solo dos EUA não cobrem o Brasil (D-003). O SoilGrids dá textura, carbono e pH em todo o país, numa grade fina.

**2. Valor por ponto.** O GAEZ v5 diz se uma cultura é apta (cerca de 1 km). O mapa de solos da Embrapa dá a **classe** do solo (Latossolo, Argissolo...). O SoilGrids dá **números**: quanto de argila, quanto de carbono. São esses números que mudam a água disponível e o risco de erosão.

**3. Mostra a própria incerteza.** Onde há poucos perfis, como em boa parte da Amazônia, o intervalo fica largo. A ferramenta pode usar isso direto no nível de confiança.

**4. Ajuda a decidir a Q-07.** O registro de decisões aponta uma inconsistência (I-1): um documento usa SoilGrids para solo, outro usa GAEZ. Este texto mostra o papel de cada um. A decisão continua com a equipe.

## Como entra no projeto

### Harmonização

- **Acesso:** API REST do ISRIC (consulta por ponto, ainda em fase beta), arquivos COG por WebDAV, WCS ou Google Earth Engine.
- **Processamento:** para o talhão, consultar o ponto ou a média dos pixels de 250 m dentro do polígono. Para o panorama nacional, usar a versão agregada de 1 km ou 5 km, mais leve. Converter os valores inteiros para unidades usuais (ver tabela) e resumir 0–30 cm e 30–100 cm.

| Variável | O que é | Uso |
| --- | --- | --- |
| `clay`, `sand`, `silt` | Argila, areia e silte (g/kg; dividir por 10 dá %) | Textura, retenção de água, erosão |
| `soc` | Carbono orgânico (dg/kg; dividir por 10 dá g/kg) | Saúde do solo |
| `phh2o` | pH em água (×10) | Acidez, necessidade de calagem |
| `cec` | Capacidade de troca de cátions | Fertilidade |
| `bdod` | Densidade do solo | Compactação |
| `nitrogen` | Nitrogênio total | Fertilidade |
| `wv0033`, `wv1500` | Água retida a 33 kPa e a 1500 kPa | Água disponível para a planta |

> Confirmar nas páginas oficiais a situação atual da API REST (limites de consulta e se continua em beta), a disponibilidade das camadas de retenção de água (`wv*`) para o Brasil e os fatores de conversão de cada variável.

### Indicadores calculados

- **Textura dominante:** argilosa, média ou arenosa, de 0 a 30 cm.
- **Água disponível:** diferença entre `wv0033` e `wv1500`, até 100 cm.
- **Carbono de 0 a 30 cm:** comparado com a média do bioma.
- **Faixa de incerteza:** largura do intervalo entre os quantis de 5% e 95%.

### Nível de confiança

A confiança vem de três lugares:

- **A própria incerteza do SoilGrids.** Intervalo largo, confiança baixa.
- **Concordância com a Embrapa.** Se a textura bate com a classe do mapa de solos, a confiança sobe. A independência é **parcial**: parte dos perfis que treinam o SoilGrids vem de levantamentos brasileiros.
- **Sinal na vegetação.** Se o NDVI do HLS mostra lavoura mais fraca justamente na mancha que o SoilGrids aponta como diferente, é uma evidência de outra natureza.

A análise de solo do produtor vale mais que qualquer mapa. Quando ela existe, substitui o SoilGrids.

## Onde o produtor vê isso

**Etapa 1, perfil do local.** "Solo provavelmente argiloso, com carbono baixo", com a faixa de incerteza.

**Cartão da estratégia, em "Lacunas".** Quando a incerteza é alta: "não temos certeza sobre a textura; se tiver análise de solo, informe aqui."

**Mapa do talhão.** Manchas de textura diferente aparecem quando o talhão é grande o bastante para vários pixels de 250 m.

## Caso hipotético: SoilGrids junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Edson planta grãos perto de Paragominas, no nordeste do Pará, na borda da Amazônia. As lavouras foram abertas sobre pastagens degradadas há cerca de 15 anos.

- **Rotação atual:** soja (dezembro a abril) e milho safrinha (abril a julho) em todos os quatro talhões.
- **Irrigação:** não tem.
- **Prioridades:** solo e renda altas; erosão média.
- **Mercado:** soja, milho e venda de pasto para pecuaristas vizinhos.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **SoilGrids** | Talhões 1 a 3: 55 a 65% de argila de 0 a 30 cm. Talhão 4: cerca de 20% de argila e 70% de areia, com intervalo largo (de 15 a 45% de argila). Carbono baixo e pH ácido em todos. |
| **SoilGrids (retenção)** | Água disponível no talhão 4 cerca de metade da dos outros. |
| Embrapa Solos | Latossolo Amarelo em toda a área; a escala do mapa não separa o talhão 4. |
| FAO GAEZ v5 | Aptidão boa para soja e braquiária; média para milho safrinha. |
| HLS + Sentinel-1 | No talhão 4, pico do milho 30% mais baixo em 4 dos últimos 5 anos. Nuvens de dezembro a março exigem o radar. |
| GPM IMERG | Chuva até maio; seca de junho a novembro. |
| GLDAS / SMAP L4 | Zona das raízes seca a partir de junho na região. |
| SRTM | Talhão 4 em encosta de 5 a 7%. |
| MapBiomas | Pastagem até cerca de 2010, soja depois. |

### Onde os dados se completam

**O SoilGrids acha a mancha que o mapa não mostra.** O mapa da Embrapa, em escala nacional, coloca toda a fazenda no mesmo solo. O SoilGrids, em 250 m, aponta o talhão 4 como bem mais arenoso.

**A lavoura confirma.** O HLS mostra milho mais fraco justamente no talhão 4, quase todo ano. É uma evidência independente do solo: satélite óptico e radar, não modelo de solo.

**Por que o milho sofre ali.** O GLDAS usa parâmetros de solo genéricos e não vê a diferença entre talhões. O SoilGrids mostra que o talhão 4 guarda metade da água. Quando a chuva acaba em maio, ali a água acaba antes.

**Mas a incerteza é alta.** O intervalo de argila no talhão 4 vai de 15 a 45%. A Amazônia tem poucos perfis de solo. Confiança **média**: o padrão é coerente, mas o número exato precisa de análise de solo.

### Regras ativadas

- **Textura arenosa e pouca água disponível** reduzem o peso do milho safrinha naquele talhão.
- **Carbono baixo e encosta** aumentam o peso de culturas de cobertura com muita raiz.
- **Diferença forte entre talhões** ativa a opção de manejo por talhão.

### Comparação das estratégias

| Critério | A: atual (soja → milho em tudo) | B: soja → milho + braquiária em tudo | C: por talhão (argilosos: soja → milho + braquiária; arenoso: soja → braquiária) |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●●○○ |
| Solo | ●○○○○ | ●●●●○ | ●●●●● |
| Nitrogênio | ●●○○○ | ●●○○○ | ●●○○○ |
| Erosão | ●●○○○ | ●●●●○ | ●●●●○ |
| Forragem | ●○○○○ | ●●●●○ | ●●●●○ |
| Renda | ●●●○○ | ●●●○○ | ●●●●○ |

Com os pesos do Sr. Edson (solo e renda altas, erosão média), a **estratégia C** fica em primeiro. Ela evita o milho que rende pouco no talhão arenoso e cobre melhor o solo onde ele é mais frágil.

### Cartão da estratégia C

> **Resumo:** uma opção é manter soja e milho com braquiária nos talhões argilosos e, no talhão 4, trocar o milho safrinha por braquiária depois da soja, como cobertura ou pasto.
>
> **Por que foi sugerida:** o talhão 4 parece mais arenoso, guarda menos água e teve milho mais fraco em 4 dos últimos 5 anos.
>
> **Evidências:** textura e água disponível (SoilGrids, confiança média, intervalo largo); milho mais fraco no talhão 4 (HLS e Sentinel-1, confiança alta); seca a partir de junho (IMERG, GLDAS e SMAP L4, confiança alta); aptidão (GAEZ v5).
>
> **Benefícios:** menos gasto com milho de baixo retorno, mais raiz e carbono no solo arenoso e pasto para vender.
>
> **Lacunas:** não há análise de solo do talhão 4. Com ela, a textura deixa de ser estimativa.
>
> **Riscos para revisão local:** fazer análise de textura e fertilidade antes de mudar o manejo; ajustar calagem com o agrônomo; planejar a dessecação da braquiária antes da soja.

## Conclusão

O SoilGrids é a fonte de números de solo da ferramenta. Ele não substitui o GAEZ (aptidão) nem a Embrapa (classe), mas completa os dois com textura, carbono e água disponível em 250 m. Seu ponto forte é dizer quanto sabe: a incerteza vai direto para o cartão. Para a Q-07, um caminho possível é usar os três juntos, cada um no seu papel, mas a escolha fica com a equipe.

## Limitações

- **É previsão de modelo:** não é medição; pode errar muito em regiões com poucos perfis, como a Amazônia.
- **250 m:** não vê variações dentro de talhões pequenos.
- **Retrato estático:** não mostra o efeito do manejo recente sobre carbono ou compactação.
- **Independência parcial com a Embrapa:** usam parte dos mesmos perfis.
- **API em beta:** pode ficar lenta ou mudar.
- **Tratamento:** mostrar a faixa de incerteza, cruzar com Embrapa, GAEZ e HLS, e pedir a análise de solo do produtor sempre que a confiança for média ou baixa.
