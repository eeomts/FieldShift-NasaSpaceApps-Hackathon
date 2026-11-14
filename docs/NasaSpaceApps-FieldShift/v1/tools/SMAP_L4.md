# SMAP L4 no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o SMAP L4, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o SMAP L4 aos outros datasets.

## O que é o SMAP L4

O SMAP comum mede a umidade só nos primeiros ~5 cm do solo. O **SMAP L4** (produto SPL4SMGP) combina essas medições com um modelo de superfície da NASA (Catchment, do sistema GEOS) e estima a umidade também na **zona das raízes, até cerca de 1 m**, de forma contínua, sem os buracos entre as passagens do satélite.

Em termos simples: é o SMAP observado, "esticado" para baixo e no tempo por um modelo que é corrigido pelas próprias medições do satélite.

## Por que usar

**1. Umidade onde a raiz trabalha.** O que define se a lavoura passa fome não é a superfície, é a água na zona das raízes. O L4 entrega isso diretamente.

**2. Mais fino e mais recente que o GLDAS.** Resolução de 9 km (o GLDAS tem ~28 km), dados a cada 3 horas e atraso de poucos dias. Serve para mostrar **como está o solo nesta safra**.

**3. Ancorado em medição.** Diferente de um modelo puro, o L4 assimila as observações do SMAP. Quando ele e o GLDAS concordam, a confiança do indicador sobe bastante.

**4. Contrastes do país.** Do Semiárido, onde poucos dias sem chuva já esgotam o solo, ao Sul, onde o solo raramente seca por muito tempo, o L4 mostra essas diferenças numa mesma escala.

A divisão de papéis fica assim: o **GLDAS** dá a climatologia longa (desde 2000) e o **SMAP L4** dá o detalhe recente (desde 2015) e a situação atual.

## Como entra no projeto

### Harmonização

- **Produto:** SPL4SMGP, grade EASE-Grid 2.0 de 9 km, passos de 3 horas, desde março de 2015.
- **Acesso:** NSIDC DAAC, pelo Earthdata Search, `earthaccess` ou AppEEARS (séries por ponto ou polígono).
- **Processamento:** recortar o Brasil, agregar os passos de 3 horas para médias diárias e mensais e reamostrar para a grade comum. Para o país inteiro, vale baixar só as variáveis necessárias (com Harmony ou OPeNDAP), porque a série de 3 horas é pesada.

| Variável | O que é | Uso |
| --- | --- | --- |
| `sm_surface` | Umidade de 0–5 cm | Comparação com o SMAP L3 e o GLDAS 0–10 cm |
| `sm_rootzone` | Umidade de 0–100 cm | Indicador principal de estresse hídrico |
| `sm_profile` | Umidade do perfil inteiro | Reserva total de água |
| `sm_rootzone_wetness` | Umidade da zona das raízes em escala relativa (0 a 1) | Comparar locais com solos diferentes |

> Confirmar nas páginas oficiais os nomes das variáveis, a versão atual do produto e a latência.

### Indicadores calculados

- **Anomalia da zona das raízes:** umidade atual comparada com a média de 2015 em diante para o mesmo período.
- **Dias de estresse:** número de dias por mês com a zona das raízes abaixo de um limiar (por exemplo, o percentil 20).
- **Resposta ao veranico:** quantos dias sem chuva bastam para a zona das raízes cair abaixo do limiar.

### Nível de confiança

O SMAP L4 é comparado com o GLDAS e o ERA5 usando **anomalias**, não valores absolutos, porque cada modelo usa profundidades e parâmetros de solo diferentes. Se os três indicam déficit no mesmo período, a confiança é alta. Na Amazônia, a vegetação densa atrapalha a medição do SMAP, então a confiança ali tende a ser menor.

## Onde o produtor vê isso

**Etapa 2, "situação desta safra".** Um indicador mostra se a água nas raízes está acima, dentro ou abaixo do normal agora.

**Calendário de vulnerabilidade.** Os dias de estresse por mês reforçam o que o GLDAS mostra na série longa.

**Cartão da estratégia.** Exemplo: "Na sua região, 8 dias sem chuva em fevereiro já bastam para a água nas raízes ficar crítica."

## Caso hipotético: SMAP L4 junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Antônio planta em sequeiro perto de Irecê, no sertão da Bahia, região de Caatinga e Semiárido. Também cria cabras e algumas vacas.

- **Rotação atual:** feijão e milho nas águas (novembro a março), pousio o resto do ano.
- **Irrigação:** não tem.
- **Prioridades:** água e forragem altas; renda média.
- **Mercado:** feijão, milho, sorgo e feijão-caupi; usa forragem no próprio rebanho.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| GPM IMERG / CHIRPS | Chuva concentrada de dezembro a março, com veranicos de 10 a 20 dias em 7 de cada 10 anos. |
| NASA POWER | Evapotranspiração de referência acima de 5,5 mm/dia em quase todo o ciclo. |
| GLDAS | Zona das raízes abaixo do normal em fevereiro e março em mais da metade dos anos desde 2000. |
| **SMAP L4** | Em média, 8 dias sem chuva derrubam a zona das raízes abaixo do percentil 20. Na safra 2025/26, fevereiro ficou 45% abaixo do normal. |
| ECOSTRESS | Queda da evapotranspiração do milho em fevereiro, sinal de estresse. |
| HLS | O NDVI do milho para de subir antes do pendoamento nos anos de veranico; o do feijão-caupi segue subindo. |
| FAO GAEZ | Aptidão boa para sorgo, milheto e feijão-caupi; baixa para milho. |
| ZARC | Risco alto para milho de sequeiro em quase todas as datas de plantio do município. |

### Onde os dados se completam

**O problema é o veranico, não só a chuva total.** O GPM mostra que o total do ano é baixo e concentrado, com veranicos frequentes. O SMAP L4 mostra quanto tempo o solo aguenta: cerca de 8 dias. Como os veranicos duram de 10 a 20 dias, a raiz do milho fica sem água na fase mais sensível.

**A série longa confirma.** O GLDAS mostra que isso acontece desde 2000, não só nos últimos anos. O ECOSTRESS e o HLS mostram o efeito na planta. Quatro fontes apontam o mesmo problema: confiança **alta**.

**Onde a confiança cai.** O L4 trabalha com 9 km e com o solo médio da célula. Se o talhão tem solo mais raso ou arenoso que a média, seca ainda mais rápido. A ferramenta marca essa lacuna e pede a análise de solo.

### Regras ativadas

- **Veranico mais longo que a resistência do solo** aumenta o peso das culturas tolerantes à seca.
- **Prioridade alta em forragem** aumenta o peso de culturas de duplo uso (grão e forragem).
- **Aptidão baixa no GAEZ e risco alto no ZARC** reduzem a nota do milho.

### Comparação das estratégias

| Critério | A: atual (feijão e milho → pousio) | B: feijão-caupi e sorgo de duplo uso → pousio | C: feijão-caupi → milheto |
| --- | --- | --- | --- |
| Água | ●○○○○ | ●●●●○ | ●●●●○ |
| Solo | ●○○○○ | ●●○○○ | ●●●●○ |
| Nitrogênio | ●●○○○ | ●●●○○ | ●●●●○ |
| Erosão | ●○○○○ | ●●○○○ | ●●●○○ |
| Forragem | ●●○○○ | ●●●●● | ●●●○○ |
| Renda | ●●●○○ | ●●●○○ | ●●●○○ |

Com os pesos do Sr. Antônio (água e forragem altas), a **estratégia B** fica em primeiro, com a C logo atrás.

### Cartão da estratégia B

> **Resumo:** trocar o milho por sorgo, que aguenta melhor os veranicos e serve de grão e de forragem, e o feijão comum pelo feijão-caupi.
>
> **Por que foi sugerida:** na sua região, cerca de 8 dias sem chuva já secam o solo na profundidade das raízes, e os veranicos costumam durar mais que isso.
>
> **Evidências:** veranicos frequentes (GPM e CHIRPS, confiança alta); solo seca rápido na zona das raízes (SMAP L4, GLDAS e ERA5 concordam, confiança alta); estresse visível na lavoura (ECOSTRESS e HLS, confiança média).
>
> **Benefícios:** sorgo e feijão-caupi toleram melhor a falta de água, o caupi fixa nitrogênio e o sorgo garante forragem para o rebanho mesmo em ano ruim.
>
> **Lacunas:** não sabemos a profundidade e a textura do seu solo; se for raso ou arenoso, a reserva de água é ainda menor.
>
> **Riscos para revisão local:** escolher as cultivares e a data de plantio com o técnico e conferir o ZARC do município. Ataque de pássaros no sorgo e mercado para o grão precisam ser avaliados. Palma forrageira, comum na região, pode complementar a forragem, mas fica fora desta comparação.

## Conclusão

O SMAP L4 traduz o veranico em algo que o produtor entende: quantos dias o solo aguenta. O GLDAS mostra que o problema é antigo, e o SMAP L4 mostra o detalhe e a situação de agora. No Semiárido, o mesmo indicador que no Sul quase nunca acende vira o centro da recomendação, que é exatamente o contraste que a ferramenta quer mostrar no país.

## Limitações

- **Série curta:** começa em 2015; para climatologia longa, usar o GLDAS.
- **Resolução de 9 km:** valor regional, não do talhão.
- **Zona das raízes é estimada por modelo:** só a superfície é observada pelo satélite.
- **Vegetação densa:** na Amazônia e em matas fechadas, a medição do SMAP perde qualidade.
- **Parâmetros de solo genéricos:** podem não representar o solo real do talhão.
- **Tratamento:** comparar anomalias com GLDAS e ERA5, mostrar o nível de confiança e pedir a análise de solo do produtor.
