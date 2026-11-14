# FIRMS no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o FIRMS, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o FIRMS aos outros datasets.

## O que é o FIRMS

O FIRMS (Fire Information for Resource Management System) é o sistema da NASA que distribui os **focos de fogo ativo** detectados pelos satélites. Cada foco é um ponto com data, hora, posição e intensidade, registrado quando o sensor percebe um pixel muito mais quente que o entorno.

Usa dois sensores:

- **MODIS** (satélites Terra e Aqua): pixels de 1 km, desde 2000.
- **VIIRS** (satélites Suomi NPP, NOAA-20 e NOAA-21): pixels de 375 m, desde 2012, mais sensível a fogos pequenos.

Os dados saem em quase tempo real (poucas horas) e ficam num arquivo histórico.

## Por que usar

**1. O fogo faz parte do risco em boa parte do país.** Na seca, queimadas são comuns no Cerrado, no Pantanal e na borda da Amazônia. O fogo queima palhada, expõe o solo, reduz matéria orgânica e pode atingir a lavoura vinda do vizinho.

**2. Contrapeso às culturas de cobertura.** As estratégias da ferramenta muitas vezes sugerem palhada na seca. Palhada seca também é **combustível**. O FIRMS mostra onde isso exige cuidado extra.

**3. Indicador de degradação.** Áreas que queimam quase todo ano tendem a ter solo mais pobre e mais erosão.

**4. Fogos diferentes em biomas diferentes.** No Cerrado, o fogo costuma vir de manejo de pasto e de queimadas que escapam. Na borda da Amazônia, está muito ligado ao desmatamento recente. A ferramenta não julga a origem do fogo, mas o contexto muda a leitura: perto de áreas recém-desmatadas, focos repetidos indicam paisagem em transformação, não só risco sazonal.

## Como entra no projeto

### Harmonização

- **Acesso:** site do FIRMS, com download do arquivo histórico do Brasil em CSV ou shapefile, ou API com uma chave gratuita (`MAP_KEY`).
- **Processamento:** manter os focos de confiança nominal ou alta, contar focos por célula da grade comum e por mês, e calcular a recorrência por ano. O Brasil tem centenas de milhares de focos por ano, então vale trabalhar com o arquivo anual, não com a API ponto a ponto.

| Campo | O que é | Uso |
| --- | --- | --- |
| `latitude`, `longitude` | Centro do pixel do foco | Localizar o foco |
| `acq_date`, `acq_time` | Data e hora da detecção | Calendário de fogo |
| `frp` | Potência radiativa do fogo | Intensidade do fogo |
| `confidence` | Confiança da detecção | Filtrar falsos alarmes |
| `daynight` | Dia ou noite | Separar padrões |

> Confirmar nas páginas oficiais os nomes dos campos em cada sensor, o formato da API e os limites de uso. Para área efetivamente queimada, usar também o MODIS MCD64A1 ou o MapBiomas Fogo. O **Programa Queimadas do INPE** reúne focos de vários satélites para o Brasil e serve de comparação.

### Indicadores calculados

- **Calendário de fogo:** focos por mês na região.
- **Recorrência:** em quantos anos, desde 2012, houve foco num raio de 2 km do talhão.
- **Proximidade:** distância média dos focos à propriedade.

### Nível de confiança

Um foco é o **centro de um pixel** de 375 m ou 1 km, não o lugar exato do fogo. Um foco "dentro" do talhão pode ter sido no vizinho. Por isso o FIRMS é cruzado com cicatrizes de queimada no HLS (queda do índice NBR), com o MapBiomas Fogo e com os focos do INPE. Se as fontes concordam, a confiança é alta.

## Onde o produtor vê isso

**Etapa 2, vulnerabilidade por mês.** Um indicador de "risco de fogo no entorno" aparece nos meses secos.

**Riscos para revisão local.** Quando a estratégia sugere palhada na seca e a região queima com frequência, o cartão inclui cuidados como aceiros.

**Glossário.** Explica que o satélite vê o calor do fogo, não a área queimada, e que um foco pode estar a algumas centenas de metros do ponto mostrado.

## Caso hipotético: FIRMS junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Geraldo planta grãos perto de Balsas, no sul do Maranhão, região do MATOPIBA, onde a agricultura avançou sobre o Cerrado nas últimas décadas. A fazenda faz divisa com pastagens e uma reserva de cerrado.

- **Rotação atual:** soja (novembro a março), milheto ou pousio até novembro.
- **Irrigação:** não tem.
- **Prioridades:** solo e água altas; renda média.
- **Mercado:** soja, milho e sorgo.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| HLS | Solo descoberto de julho a outubro na maioria dos anos; o milheto só se estabelece quando a chuva vai até abril. |
| GLDAS / SMAP L4 | Zona das raízes abaixo do normal a partir de maio. |
| NASA POWER | Umidade relativa abaixo de 20% em vários dias de agosto e setembro, com máximas acima de 36 °C. |
| GPM IMERG | Nenhuma chuva relevante de junho a outubro. |
| **FIRMS** | Focos num raio de 2 km da fazenda em 10 dos últimos 13 anos, quase todos entre agosto e outubro. Dois focos dentro da divisa, em 2020 e 2024. |
| INPE Queimadas | Confirma o mesmo padrão de focos no município. |
| MapBiomas Fogo | Cicatriz de queimada na pastagem vizinha nos dois anos. |
| HLS (NBR) | Queda do índice de queimada numa faixa de 200 m do talhão em 2024. |
| MODIS Land Cover / MapBiomas | Entorno com pastagem e savana, as classes que mais queimam na região. |

### Onde os dados se completam

**A estratégia natural tem um risco escondido.** Os dados de solo e cobertura levam a uma sugestão clássica: cobrir o solo com braquiária depois da segunda cultura. Mas o FIRMS mostra que o entorno queima quase todo ano, justamente quando a palhada estaria mais seca. O POWER mostra o ar muito seco e quente nesses meses.

**O foco "dentro" da fazenda era no vizinho.** O FIRMS colocou dois focos na divisa, mas o MapBiomas Fogo e o HLS mostram que a cicatriz ficou na pastagem vizinha, a 200 m do talhão. O risco é real, mas vem de fora: confiança **alta** para o risco no entorno e **média** para a posição exata.

### Regras ativadas

- **Solo descoberto longo e calor forte** aumentam o peso das culturas de cobertura.
- **Recorrência de fogo no entorno** adiciona um risco às estratégias com palhada seca e reduz um pouco sua nota em "solo", porque a palhada pode ser perdida.
- **Ar muito seco em agosto e setembro** reforça a necessidade de manejo da palhada nesses meses.

### Comparação das estratégias

| Critério | A: atual (soja → milheto ou pousio) | B: soja → milho + braquiária | C: soja → sorgo + braquiária, com aceiro e pastejo leve |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●●●○ |
| Solo | ●○○○○ | ●●●○○ | ●●●●○ |
| Nitrogênio | ●●○○○ | ●●○○○ | ●●○○○ |
| Erosão | ●○○○○ | ●●●●○ | ●●●●○ |
| Forragem | ●○○○○ | ●●●●○ | ●●●●● |
| Renda | ●●●○○ | ●●●●○ | ●●●○○ |

Sem o FIRMS, a B teria nota cheia em solo. Com o risco de fogo, a **estratégia C** fica em primeiro para os pesos do Sr. Geraldo.

### Cartão da estratégia C

> **Resumo:** depois da soja, plantar sorgo com braquiária para cobrir o solo, mas controlar o volume de palha seca com pastejo leve e manter aceiros na divisa.
>
> **Por que foi sugerida:** seu talhão fica cerca de 4 meses descoberto na seca, mas o entorno queima quase todo ano nessa mesma época.
>
> **Evidências:** solo descoberto (HLS, confiança alta); solo seco a partir de maio (GLDAS e SMAP L4, confiança alta); fogo no entorno em 10 de 13 anos (FIRMS, INPE, MapBiomas Fogo e HLS, confiança alta); ar muito seco e quente em agosto e setembro (POWER, confiança alta).
>
> **Benefícios:** o solo fica protegido, o sorgo tolera melhor a seca e o pastejo leve gera forragem enquanto reduz o combustível.
>
> **Lacunas:** não sabemos se há gado disponível para o pastejo nem se já existem aceiros.
>
> **Riscos para revisão local:** fazer aceiros na divisa com a pastagem antes de julho, combinar com os vizinhos e com a brigada local, e ajustar a lotação para não degradar a cobertura. Conferir com o agrônomo a época de dessecação antes da soja.

## Conclusão

O FIRMS não aponta uma cultura, mas impede a ferramenta de ser ingênua. Uma estratégia que parece ótima no papel, cobrir o solo com palhada na seca, pode virar risco numa região que queima todo ano. Juntando FIRMS, clima seco e cicatrizes de queimada, o cartão mostra o benefício e o cuidado necessário lado a lado. Em regiões onde quase não há fogo, como boa parte do Sul, o mesmo indicador fica apagado e a recomendação não muda.

## Limitações

- **Foco não é área queimada:** mostra o calor detectado no momento da passagem; para a área, usar MCD64A1 ou MapBiomas Fogo.
- **Posição aproximada:** o ponto é o centro de um pixel de 375 m ou 1 km.
- **Fogos pequenos ou rápidos escapam:** principalmente no MODIS, e entre as passagens dos satélites.
- **Nuvens e fumaça densa:** podem esconder focos.
- **Origem do fogo:** o satélite não diz se é manejo, acidente ou desmatamento; isso exige contexto local.
- **Tratamento:** filtrar por confiança, contar por recorrência e raio, e cruzar com MapBiomas Fogo, INPE e HLS.
