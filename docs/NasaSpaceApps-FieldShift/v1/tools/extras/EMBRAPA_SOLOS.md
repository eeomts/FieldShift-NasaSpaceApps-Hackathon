# Embrapa Solos no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar os mapas de solos da Embrapa Solos e do PronaSolos, como eles entram na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta esses mapas aos outros datasets.

## O que é a Embrapa Solos e o mapa de solos do Brasil

A **Embrapa Solos** é o centro da Embrapa responsável pelo levantamento e pela classificação dos solos do país. Ela mantém o **Sistema Brasileiro de Classificação de Solos (SiBCS)**, que divide os solos em 13 ordens: Argissolos, Cambissolos, Chernossolos, Espodossolos, Gleissolos, Latossolos, Luvissolos, Neossolos, Nitossolos, Organossolos, Planossolos, Plintossolos e Vertissolos.

Três fontes interessam ao projeto:

- **Mapa de Solos do Brasil (Embrapa Solos, 2011), escala 1:5.000.000.** Atualizou a legenda do mapa de 2001 para o SiBCS. Serve para o panorama nacional.
- **Pedologia do IBGE, escala 1:250.000.** Mapa vetorial do Brasil inteiro, com unidades de mapeamento e pontos de amostragem (perfis de solo), seguindo o SiBCS. É bem mais detalhado que o de 1:5.000.000.
- **PronaSolos.** Programa nacional de levantamento de solos, coordenado pelo Ministério da Agricultura. Sua plataforma na web, lançada em 2020, reúne mapas e dados de solos da Embrapa, do IBGE e do Serviço Geológico do Brasil (CPRM), além de mapas interpretados, como aptidão agrícola e suscetibilidade à erosão.

## Por que usar

**1. É a classificação que o técnico brasileiro usa.** O agrônomo e o extensionista falam em "Latossolo Vermelho" ou "Argissolo Amarelo", não em classes de um sistema estrangeiro. Mostrar o solo nesses termos aproxima a ferramenta de quem vai revisá-la.

**2. Traz o que a grade global não traz.** O SoilGrids e o GAEZ dão números (textura, carbono, aptidão) em grade. O mapa brasileiro traz características que mudam o manejo: horizonte coeso, caráter arênico, plintita, drenagem ruim, pedregosidade.

**3. Perfis medidos em campo.** Os pontos de amostragem do IBGE e da Embrapa são perfis descritos e analisados em laboratório. São a melhor "verdade de campo" disponível para conferir as estimativas em grade.

**4. Fecha a lacuna do SSURGO.** Os dados de solo detalhados dos EUA ficam fora (D-003). Esta é a alternativa nacional prevista.

## Como entra no projeto

A fonte de solo do projeto **ainda não está decidida** (Q-07 e inconsistência I-1). Este documento não fecha essa decisão. Mostra o que os mapas brasileiros acrescentam e propõe um uso combinado, para a equipe avaliar: **classes e restrições** do mapa brasileiro, **números** do SoilGrids ou do GAEZ.

### Harmonização

- **Acesso:** shapefiles da pedologia 1:250.000 no portal de geociências do IBGE (BDiA, também por WMS); plataforma do PronaSolos e GeoInfo, a infraestrutura de dados espaciais da Embrapa; mapa de 1:5.000.000 nas publicações da Embrapa Solos.
- **Processamento:** recortar a fazenda; ler a **unidade de mapeamento**, que costuma ser uma associação de dois ou três solos (por exemplo, 60% de um, 40% de outro); guardar o componente dominante e os secundários; traduzir as características em restrições (coeso, arênico, mal drenado, raso). No panorama nacional, a classe dominante é rasterizada na grade comum.

| Campo | O que é | Uso |
| --- | --- | --- |
| Classe do componente dominante | Ordem e subordem do SiBCS (ex.: Argissolo Amarelo) | Nome do solo mostrado ao produtor |
| Componentes secundários | Outras classes da associação e suas proporções | Mostrar a incerteza dentro do polígono |
| Caracteres e textura | Coeso, arênico, textura média ou argilosa etc. | Regras de restrição de raiz e de água |
| Relevo e drenagem | Relevo da unidade e classe de drenagem | Cruzar com SRTM e com áreas úmidas |
| Pontos de amostragem | Perfis com análises de laboratório | Conferir SoilGrids e GAEZ perto da fazenda |

> Confirmar nas páginas oficiais os nomes dos campos do shapefile do IBGE, a versão atual da pedologia 1:250.000, quais camadas do PronaSolos podem ser baixadas (e não só vistas) e se já há mapas digitais de propriedades do solo em grade para a região de interesse.

### Indicadores calculados

- **Classe de solo do talhão:** componente dominante e secundários, com proporção.
- **Restrições de manejo:** presença de horizonte coeso, textura arenosa, drenagem ruim ou solo raso.
- **Concordância com a grade:** textura do mapa brasileiro comparada com a do SoilGrids.

### Nível de confiança

A escala manda. Em 1:250.000, um polígono pode ter dezenas de quilômetros quadrados e mais de um tipo de solo. O mapa diz **qual solo é mais provável na região**, não qual está no talhão. Por isso a classe aparece com confiança **média** e sempre com os componentes secundários.

O mapa de suscetibilidade à erosão do PronaSolos usa declividade derivada do SRTM. Se ele e o SRTM apontam a mesma encosta, isso **não** conta como duas confirmações. A confirmação real é uma **análise de solo** do próprio talhão, que a ferramenta pede ao produtor quando ele tiver.

## Onde o produtor vê isso

**Etapa 2, ficha do solo.** O nome do solo, em português, com uma frase sobre o que ele significa para o manejo. Exemplo: "Argissolo Amarelo coeso: camada endurecida abaixo da superfície, que dificulta a raiz na seca."

**Cartão da estratégia.** As restrições do solo aparecem em "Por que foi sugerida" e em "Lacunas".

**Campo para análise de solo.** Se o produtor tiver uma análise, ela substitui o mapa nos indicadores do talhão.

## Caso hipotético: Embrapa Solos junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Severino é fornecedor de cana-de-açúcar perto de São Miguel dos Campos, em Alagoas, nos tabuleiros costeiros, a cerca de 30 km do litoral. Tem 80 ha.

- **Rotação atual:** cana-de-açúcar por cinco ou seis cortes; na reforma do canavial, o solo fica em pousio de três a quatro meses antes do novo plantio.
- **Irrigação:** não tem.
- **Prioridades:** solo e renda altas; nitrogênio médio.
- **Mercado:** cana para a usina vizinha; há compradores de amendoim e feijão na região.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **Pedologia IBGE 1:250.000** | Unidade com Argissolo Amarelo coeso como dominante e Latossolo Amarelo coeso como secundário no topo do tabuleiro; Argissolos nas encostas das grotas. |
| **Mapa de Solos do Brasil 1:5.000.000** | Mostra só Argissolos Amarelos na região, sem as encostas. |
| **PronaSolos** | Suscetibilidade à erosão alta nas encostas das grotas. Perfil de solo a 6 km da fazenda com camada coesa entre 30 e 70 cm. |
| SoilGrids | Argila aumentando com a profundidade; carbono orgânico baixo na superfície. |
| SRTM | Topo do tabuleiro plano; encostas das grotas com 15% a 25% de declividade. |
| GPM IMERG | Chuvas de abril a agosto; verão seco, com poucas chuvas fortes. |
| HLS | Solo descoberto por três a quatro meses na reforma, em dois talhões, nos últimos seis anos. |

### Onde os dados se completam

**O nome do solo explica o problema.** O SoilGrids mostra a argila aumentando em profundidade, mas não diz que existe uma camada coesa. O mapa do IBGE e o perfil do PronaSolos dizem: abaixo de 30 cm, o solo endurece na seca e a raiz da cana não passa.

**A escala importa.** O mapa de 1:5.000.000 nem mostra as encostas. O de 1:250.000 mostra, mas o limite exato só se vê no campo. Confiança **média** para a classe no talhão e **alta** para a presença de solos coesos na região.

**A suscetibilidade à erosão não é uma prova a mais.** O mapa do PronaSolos e o SRTM concordam nas encostas, mas o mapa usa declividade do próprio SRTM. Conta como uma fonte só.

### Regras ativadas

- **Horizonte coeso** aumenta o peso de plantas com raiz forte e profunda na reforma, como a crotalária.
- **Solo descoberto na reforma** aumenta o peso das culturas de cobertura.
- **Carbono orgânico baixo e prioridade alta em solo** aumentam o peso de adubação verde.

### Comparação das estratégias

| Critério | A: atual (cana → pousio na reforma → cana) | B: cana → crotalária na reforma → cana | C: cana → amendoim na reforma → cana |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●○○○ | ●●○○○ |
| Solo | ●○○○○ | ●●●●○ | ●●●○○ |
| Nitrogênio | ●○○○○ | ●●●●○ | ●●●○○ |
| Erosão | ●○○○○ | ●●●●○ | ●●●○○ |
| Forragem | ●○○○○ | ●○○○○ | ●○○○○ |
| Renda | ●●●○○ | ●●●○○ | ●●●●○ |

A C traz renda na reforma com a venda do amendoim. A B não vende nada na reforma, mas melhora mais o solo e deixa mais nitrogênio. Com solo e renda altos e nitrogênio médio, a **estratégia B** fica em primeiro, por pouco. A C fica logo atrás e a ferramenta mostra as duas, explicando a diferença.

### Cartão da estratégia B

> **Resumo:** uma opção é semear crotalária logo depois da última colheita, para cobrir o solo durante a reforma e incorporá-la antes do novo plantio da cana.
>
> **Por que foi sugerida:** seu solo provavelmente tem uma camada coesa abaixo de 30 cm, que dificulta a raiz; e na reforma o solo fica descoberto por três a quatro meses.
>
> **Evidências:** solos coesos na região (pedologia IBGE e perfil do PronaSolos, confiança média para o talhão); argila aumentando em profundidade (SoilGrids, confiança média); solo descoberto na reforma (HLS, confiança alta); encostas inclinadas nas grotas (SRTM, confiança alta).
>
> **Benefícios:** raiz que ajuda a abrir caminho na camada coesa, nitrogênio para a cana nova e solo coberto.
>
> **Lacunas:** não temos uma análise de solo nem uma descrição do perfil no seu talhão; o mapa indica o solo mais provável da região.
>
> **Riscos para revisão local:** confirmar a camada coesa com uma trincheira ou um penetrômetro, com o técnico da usina ou da extensão rural; ajustar a época da crotalária ao calendário de plantio da usina; manter as encostas das grotas com cobertura permanente.

## Conclusão

Os mapas da Embrapa Solos, do IBGE e do PronaSolos dão nome e contexto ao solo. Onde a grade global só mostra números, o mapa brasileiro diz "coeso", e isso muda a estratégia. A escala limita: o mapa diz o solo mais provável da região, não o do talhão. Por isso a melhor combinação parece ser a classe e as restrições do mapa brasileiro com os números do SoilGrids ou do GAEZ, sempre substituídos por uma análise de solo quando o produtor tiver uma. A escolha final continua em aberto na Q-07.

## Limitações

- **Escala:** 1:5.000.000 só serve para o panorama; 1:250.000 ainda é regional; mapas mais detalhados cobrem só parte do país.
- **Associações:** um polígono tem mais de um solo; o dominante pode não ser o do talhão.
- **Idade dos levantamentos:** parte dos dados vem de levantamentos antigos, como o RadamBrasil, reclassificados para o SiBCS.
- **Classes, não números:** o mapa diz o tipo de solo, mas não dá fertilidade nem carbono atuais.
- **Produtos derivados não são independentes:** a suscetibilidade à erosão usa declividade do SRTM.
- **Tratamento:** mostrar componentes e proporções, combinar com SoilGrids ou GAEZ, conferir com os perfis próximos e pedir a análise de solo do produtor.
