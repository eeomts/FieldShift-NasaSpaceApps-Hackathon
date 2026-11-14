# Sentinel-2 no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o Sentinel-2, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o Sentinel-2 aos outros datasets.

## O que é o Sentinel-2

O Sentinel-2 é uma missão do programa Copernicus, da União Europeia, operada pela ESA. Seus satélites levam o sensor **MSI**, que fotografa a Terra em **13 bandas**, do visível ao infravermelho de ondas curtas, numa faixa de 290 km de largura.

- **Resolução:** 10 m nas bandas do visível e do infravermelho próximo; 20 m nas bandas de "borda do vermelho" (*red edge*) e de ondas curtas; 60 m nas bandas atmosféricas.
- **Satélites:** Sentinel-2A (desde 2015), 2B (desde 2017) e 2C (lançado em 2024, assumiu o lugar do 2A em janeiro de 2025). O 2A seguiu em operação extra, como terceiro satélite.
- **Revisita:** 5 dias com dois satélites; menos com três.

Os dados são **gratuitos e abertos**. O nível mais útil é o **L2A**, que já vem como reflectância de superfície, com correção atmosférica.

## Por que usar

**1. Enxerga o talhão pequeno.** O HLS reamostra o Sentinel-2 para 30 m. Num talhão de 3 ha estreito, isso mistura a borda com a estrada ou a mata. Em 10 m, cabem nove pixels onde o HLS tem um. Isso importa no Sul, no Sudeste e na agricultura familiar, onde os talhões são pequenos.

**2. Bandas de borda do vermelho.** Elas reagem à clorofila e ajudam a separar uma lavoura vigorosa de uma lavoura verde, mas pálida, por exemplo por falta de nitrogênio. O Landsat não tem essas bandas; no HLS, elas só aparecem na coleção vinda do Sentinel-2 e em 30 m. Direto do Sentinel-2, saem em 20 m.

**3. Variação dentro do talhão.** Com 10 m dá para ver a mancha que sempre rende menos, a faixa de encosta que demora a fechar e a cabeceira encharcada.

## Como entra no projeto

### Escala: só nos pontos escolhidos

Como o HLS, o Sentinel-2 em 10 m **não entra no Brasil inteiro**. Fica restrito às regiões de demonstração e ao talhão que o produtor informa (D-008). O panorama nacional continua com o MODIS.

### Harmonização

- **Produto:** Sentinel-2 L2A, em tiles de 100 km × 100 km do sistema MGRS (o mesmo do HLS).
- **Acesso:** Copernicus Data Space Ecosystem (conta gratuita), com busca por STAC. Cópias em Cloud Optimized GeoTIFF também estão na AWS (Earth Search) e no Microsoft Planetary Computer, o que permite ler só o recorte da fazenda.
- **Processamento:** recortar o talhão, aplicar a máscara de cena (`SCL`) para tirar nuvem, sombra e água, calcular os índices, suavizar a série e resumir por talhão, por zona e por mês. Na grade comum, o resultado é agregado; o mapa de 10 m fica só na visão do talhão.

| Banda / camada | O que é | Uso |
| --- | --- | --- |
| B2, B3, B4 (10 m) | Azul, verde e vermelho | Imagem em cor natural, NDVI |
| B8 (10 m) | Infravermelho próximo | NDVI em 10 m |
| B5, B6, B7, B8A (20 m) | Borda do vermelho e infravermelho próximo estreito | Índice NDRE, ligado à clorofila |
| B11, B12 (20 m) | Infravermelho de ondas curtas | Umidade da vegetação (NDMI) e queimada (NBR) |
| `SCL` (20 m) | Classificação da cena | Descartar nuvem, sombra e água |

> Confirmar nas páginas oficiais a situação atual do Sentinel-2A (a operação extra foi anunciada por 12 meses a partir de março de 2025), a mudança de escala dos valores a partir da *processing baseline* 04.00 (o deslocamento que precisa ser descontado antes de calcular índices) quais bandas de borda do vermelho o HLSS30 mantém e os limites de download do Copernicus Data Space.

### Indicadores calculados

- **Calendário de cobertura em 10 m:** meses com NDVI abaixo de 0,3, por talhão e por zona.
- **Zonas persistentes:** pixels que ficam abaixo da média do talhão em vários anos seguidos.
- **NDRE relativo:** NDRE de cada zona comparado com a média do próprio talhão, no mesmo dia.

### Nível de confiança

O Sentinel-2 **não é uma fonte independente do HLS**. O HLSS30 é o próprio Sentinel-2, reamostrado. Se os dois mostram o mesmo solo descoberto, isso não conta como duas confirmações. A confirmação vem de outra fonte: Landsat (HLSL30), Sentinel-1 (radar), MapBiomas ou o que o produtor informa.

O NDRE baixo indica clorofila baixa, mas não diz a causa. Pode ser falta de nitrogênio, encharcamento, praga ou geada. Por isso ele aparece sempre como **hipótese para conferir no campo**, com confiança no máximo média.

## Onde o produtor vê isso

**Etapa 2, mapa do talhão.** Quando o talhão é pequeno, a ferramenta troca o pixel de 30 m pelo de 10 m e mostra as zonas que ficam descobertas por mais tempo.

**Etapa 3, conferência da rotação.** O produtor confere, talhão por talhão, o que o satélite viu.

**Cartão da estratégia.** Exemplo: "A faixa de cima do talhão 3 ficou descoberta 60 dias por ano, em média, entre a silagem e a aveia."

## Caso hipotético: Sentinel-2 junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

A Sra. Lúcia tem uma propriedade de 24 ha perto de Chapecó, no oeste de Santa Catarina. Produz leite com 30 vacas. A área é dividida em cinco talhões de 2 a 6 ha, alguns em encosta.

- **Rotação atual:** milho para silagem (setembro a janeiro), pousio (fevereiro a abril), aveia-preta e azevém para pastejo (maio a setembro).
- **Irrigação:** não tem.
- **Prioridades:** forragem e solo altas; renda média.
- **Mercado:** leite para a cooperativa; o milho vira silagem dentro da propriedade.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **Sentinel-2** | Em todos os talhões, NDVI abaixo de 0,3 de fevereiro a abril. No talhão 3, a faixa de cima fica descoberta 60 dias a mais que o resto. Na aveia de inverno, o NDRE dessa faixa é 20% menor que a média do talhão em 4 de 5 anos. |
| HLS | Mostra o pousio de fevereiro a abril, mas mistura dois talhões estreitos com a estrada e a mata ciliar. |
| SRTM | Faixa de cima do talhão 3 com declividade de 12% a 15%. |
| GPM IMERG | Chuvas fortes (acima de 50 mm em um dia) em vários anos entre outubro e fevereiro. |
| NASA POWER | Geadas em junho e julho na maioria dos anos. |
| MapBiomas | Classifica a área como mosaico de usos; não separa os talhões. |

### Onde os dados se completam

**O vazio de forragem tem lugar e data.** Entre a silagem e a aveia, o solo fica descoberto e as vacas ficam sem pasto verde. O Sentinel-2 mostra que isso acontece todo ano, de fevereiro a abril, e que é mais longo na encosta do talhão 3.

**A faixa pálida não é prova de falta de nitrogênio.** O NDRE baixo coincide com a parte mais inclinada (SRTM), onde a chuva forte (IMERG) leva solo e adubo. É uma hipótese forte, mas só a análise de solo e a conversa com o técnico confirmam. Confiança **alta** para o solo descoberto e **média** para a causa da faixa pálida.

**O HLS sozinho não resolveria aqui.** Em 30 m, dois dos cinco talhões não aparecem separados. O Sentinel-2 em 10 m resolve, mas não conta como confirmação independente do HLS.

### Regras ativadas

- **Solo descoberto após a cultura principal** aumenta o peso das culturas de cobertura de ciclo curto.
- **Prioridade alta em forragem** aumenta o peso de culturas que podem ser pastejadas.
- **Encosta com chuva forte e solo descoberto** aumenta o peso do critério erosão no talhão 3.
- **Clorofila baixa recorrente** aumenta o peso de leguminosas no inverno, com aviso de conferência local.

### Comparação das estratégias

| Critério | A: atual (silagem → pousio → aveia + azevém) | B: silagem → feijão → aveia + azevém | C: silagem → milheto para pastejo → aveia + azevém + ervilhaca |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●○○○ | ●●●○○ |
| Solo | ●●○○○ | ●●○○○ | ●●●●○ |
| Nitrogênio | ●●○○○ | ●●●○○ | ●●●●○ |
| Erosão | ●●○○○ | ●●●○○ | ●●●●○ |
| Forragem | ●●●○○ | ●●●○○ | ●●●●● |
| Renda | ●●●○○ | ●●●●○ | ●●●○○ |

A B tem a melhor renda direta, com a venda do feijão. Mas a Sra. Lúcia deu peso alto a forragem e solo, e nesses dois critérios a **estratégia C** fica bem à frente. Com os pesos dela, a C fica em primeiro, a B em segundo e a atual em último.

### Cartão da estratégia C

> **Resumo:** uma opção é semear milheto logo depois da silagem, para pastejo de fevereiro a abril, e incluir ervilhaca (uma leguminosa) na mistura de aveia e azevém do inverno.
>
> **Por que foi sugerida:** seus talhões ficam descobertos de fevereiro a abril todo ano, justamente quando falta pasto verde; e a faixa de cima do talhão 3, a mais inclinada, fica descoberta ainda mais tempo e mostra a aveia mais pálida.
>
> **Evidências:** solo descoberto de fevereiro a abril (Sentinel-2, confiança alta); faixa inclinada de 12% a 15% (SRTM, confiança alta); chuva forte no verão (GPM IMERG, confiança alta); aveia pálida na faixa de cima (Sentinel-2, confiança média, causa não confirmada).
>
> **Benefícios:** pasto verde no outono, solo coberto na época de chuva forte e nitrogênio da ervilhaca para o milho seguinte.
>
> **Lacunas:** não sabemos o resultado da análise de solo do talhão 3 nem se o milheto se estabelece bem no seu solo depois da silagem.
>
> **Riscos para revisão local:** conferir com o técnico da cooperativa ou da extensão rural a causa da faixa pálida antes de mudar a adubação; ajustar a data de semeadura do milheto para que ele seja pastejado antes das primeiras geadas.

## Conclusão

O Sentinel-2 leva a ferramenta para dentro do talhão pequeno. Em 10 m, ele mostra o vazio de forragem com data e lugar, e as bandas de borda do vermelho apontam zonas pálidas que merecem visita. O cuidado está em não contar o Sentinel-2 e o HLS como duas provas, porque são a mesma observação. Nas propriedades grandes, o HLS já basta; nas pequenas, o Sentinel-2 faz diferença.

## Limitações

- **Nuvens:** é um sensor óptico; na estação chuvosa do Centro-Oeste e do Norte há poucas imagens limpas.
- **Mesma fonte do HLS:** o HLSS30 vem do Sentinel-2; os dois não se confirmam entre si.
- **Escala:** inviável no Brasil inteiro em 10 m; usar só nos pontos escolhidos.
- **Bandas em resoluções diferentes:** o NDRE e o NDMI saem em 20 m, não em 10 m.
- **NDRE não diz a causa:** clorofila baixa pode ser nitrogênio, água, praga ou geada.
- **Série mais curta:** começa em 2015, contra 2013 do Landsat 8 e 2000 do MODIS.
- **Tratamento:** máscara de cena, desconto do deslocamento de escala, contagem de imagens limpas, agregação por talhão e confirmação com Landsat, Sentinel-1, MapBiomas e o produtor.
