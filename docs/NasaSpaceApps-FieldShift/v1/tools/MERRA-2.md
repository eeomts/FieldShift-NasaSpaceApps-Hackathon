# MERRA-2 no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o MERRA-2, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o MERRA-2 aos outros datasets.

## O que é o MERRA-2

O MERRA-2 (Modern-Era Retrospective analysis for Research and Applications, versão 2) é a **reanálise climática da NASA**, feita pelo GMAO. Uma reanálise junta observações de satélites, estações e balões a um modelo do tempo e reconstrói, hora a hora, como estava a atmosfera e a superfície em todo o planeta.

Cobre de **1980 até hoje**, com valores horários numa grade de cerca de 0,5° × 0,625° (por volta de 50 a 60 km).

## Por que usar

**1. Série longa para eventos raros.** Geadas fortes e ondas de calor não acontecem todo ano. Com mais de 40 anos de dados horários, dá para estimar com que frequência elas voltam. No Brasil, o risco de geada vai de quase nulo no Norte e no Nordeste a frequente no Sul (Paraná, Santa Catarina e Rio Grande do Sul) e nas áreas altas do Sudeste. Para trigo, milho safrinha e café no Paraná e em Minas, ele pesa na escolha da estratégia.

**2. Segunda opinião ao ERA5.** O documento do projeto usa a concordância entre fontes para definir a confiança. O MERRA-2 é uma reanálise independente do ERA5, feita por outra instituição com outro modelo.

**3. Base do NASA POWER.** Boa parte dos dados meteorológicos do POWER vem do MERRA-2. Isso tem uma consequência importante: **POWER e MERRA-2 concordarem não conta como duas fontes independentes**. A comparação que vale para a confiança é MERRA-2 (ou POWER) contra ERA5 e contra as estações do INMET.

## Como entra no projeto

### Harmonização

- **Coleções úteis:** `M2T1NXSLV` (temperatura e umidade perto da superfície), `M2T1NXFLX` (chuva corrigida por observações), `M2T1NXLND` (umidade e temperatura do solo).
- **Acesso:** GES DISC, pelo Earthdata Search, `earthaccess` ou Giovanni (para análises rápidas sem baixar nada).
- **Processamento:** recortar o Brasil, calcular mínimas e máximas diárias a partir dos valores horários e reamostrar para a grade comum.

| Variável | O que é | Uso |
| --- | --- | --- |
| `T2M` | Temperatura do ar a 2 m | Mínimas para geada, máximas para calor |
| `QV2M` / `RH` derivada | Umidade do ar | Noites secas e limpas, que favorecem geada |
| `PRECTOTCORR` | Chuva corrigida por observações | Comparação com GPM e CHIRPS |
| `GWETROOT` | Umidade relativa na zona das raízes | Comparação com GLDAS e SMAP L4 |

> Confirmar nas páginas oficiais os nomes das coleções e variáveis, a latência (o produto sai com algumas semanas de atraso) e a relação atual entre POWER e MERRA-2.

### Indicadores calculados

- **Frequência de geada:** número de anos, desde 1980, com mínima abaixo de 2 °C, 0 °C e −2 °C, por mês.
- **Ondas de calor:** dias seguidos com máxima acima de um limiar, por mês.
- **Tendência:** mudança dessas frequências entre as décadas de 1980–2000 e 2001–2025.

### Nível de confiança

Comparar MERRA-2 com ERA5 e com as estações do INMET mais próximas. Se as reanálises discordam ou as estações mostram mínimas bem mais baixas, a confiança cai. Em relevo acidentado, a resolução de 50 km esconde baixadas, e o SRTM é usado para avisar isso.

## Onde o produtor vê isso

**Etapa 2, vulnerabilidade por mês.** Indicadores de geada e calor mostram em que meses a cultura corre mais risco e com que frequência.

**Cartão da estratégia.** Exemplo: "Geadas que queimam o café aconteceram em 5 dos últimos 45 anos na sua região."

**Avisos de validação.** Quando a propriedade fica em baixada, o cartão avisa que o risco real pode ser maior que o mostrado.

## Caso hipotético: MERRA-2 junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Paulo tem café arábica a cerca de 900 m de altitude, perto de Três Pontas, no Sul de Minas (MG). Como o café é perene, a "rotação" aqui é o manejo da **entrelinha**.

- **Manejo atual:** entrelinha capinada, com solo descoberto o ano todo.
- **Irrigação:** não tem.
- **Prioridades:** solo e água altas; renda alta.
- **Mercado:** café.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **MERRA-2** | Mínima abaixo de 0 °C em junho ou julho em 5 dos 45 anos desde 1980. A frequência caiu nas últimas décadas, mas houve um evento forte recente. Dias acima de 32 °C em outubro dobraram desde os anos 2000. |
| ERA5 | Concorda com os anos de geada forte, mas mostra mínimas cerca de 1 °C mais altas. |
| INMET (estação mais próxima) | Mínimas 2 °C abaixo das duas reanálises nos dias de geada. |
| SRTM | Parte do cafezal está numa baixada, 40 m abaixo do entorno. |
| GLDAS / SMAP L4 | Zona das raízes abaixo do normal em agosto e setembro, antes da florada. |
| GPM IMERG | Chuvas fortes em dezembro e janeiro. |
| HLS | Entrelinha com NDVI baixo o ano todo: solo nu. |

### Onde os dados se completam

**A geada é rara, mas existe.** Só uma série longa como a do MERRA-2 mostra isso com segurança. O ERA5 confirma os mesmos anos, então o padrão é confiável.

**Mas o valor regional subestima o risco local.** As estações do INMET mostram mínimas mais baixas que as reanálises, e o SRTM mostra que parte do cafezal está numa baixada, onde o ar frio se acumula. O risco no talhão do Sr. Paulo é maior que o da célula de 50 km. Confiança **média**, com aviso de validação local.

**O calor também pesa.** Mais dias quentes em outubro, junto com o solo seco antes da florada (GLDAS e SMAP L4), aumentam o estresse do café nessa fase.

### Regras ativadas

- **Chuva forte e solo nu na entrelinha** aumentam o peso das coberturas.
- **Déficit hídrico antes da florada** pede uma cobertura que não concorra com o café por água na seca.
- **Risco de geada em baixada** pede cuidado: vegetação alta na entrelinha impede o solo de devolver calor à noite e pode piorar a geada.

### Comparação das estratégias

| Critério | A: atual (entrelinha capinada) | B: braquiária roçada na entrelinha | C: amendoim forrageiro na entrelinha |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●●○○ |
| Solo | ●○○○○ | ●●●●● | ●●●●○ |
| Nitrogênio | ●○○○○ | ●○○○○ | ●●●●○ |
| Erosão | ●○○○○ | ●●●●● | ●●●●○ |
| Forragem | ●○○○○ | ●●○○○ | ●●○○○ |
| Renda | ●●●○○ | ●●●○○ | ●●●●○ |

Com os pesos do Sr. Paulo, a **estratégia B** fica em primeiro, com a C muito próxima.

### Cartão da estratégia B

> **Resumo:** cobrir a entrelinha com braquiária, roçada baixa no inverno e na seca.
>
> **Por que foi sugerida:** a entrelinha fica nua o ano todo e recebe chuvas fortes; a cobertura protege o solo e guarda água.
>
> **Evidências:** solo nu na entrelinha (HLS, confiança alta); chuvas fortes (GPM, confiança alta); solo seco antes da florada (GLDAS e SMAP L4, confiança alta); geadas em 5 de 45 anos (MERRA-2 e ERA5, confiança média no talhão).
>
> **Benefícios:** menos erosão, mais matéria orgânica e mais infiltração de água.
>
> **Lacunas:** a temperatura mínima real da baixada não é conhecida.
>
> **Riscos para revisão local:** na baixada, manter a braquiária roçada bem baixa de maio a agosto, porque cobertura alta aumenta o risco de geada. Roçar ou dessecar na seca para não competir com o café por água. Um termômetro de mínima na baixada ajudaria a confirmar o risco.

## Conclusão

O MERRA-2 traz a memória longa do clima: mostra eventos raros, como geadas, e como o calor está mudando. Ele também ensina uma lição de método: concordância só vale como evidência quando as fontes são independentes. Por isso, a confiança se apoia na comparação com o ERA5 e com as estações do INMET, não com o POWER.

## Limitações

- **Resolução de ~50 km:** não enxerga baixadas, topos de morro nem efeitos locais de relevo.
- **Não é independente do POWER:** comparar com ERA5 e INMET para medir a confiança.
- **Mínimas suavizadas:** reanálises tendem a subestimar o frio extremo em noites limpas.
- **Latência de semanas:** serve para histórico, não para o tempo de hoje.
- **Tratamento:** comparar com ERA5 e INMET, usar o SRTM para marcar baixadas e mostrar o risco local como faixa, não como número exato.
