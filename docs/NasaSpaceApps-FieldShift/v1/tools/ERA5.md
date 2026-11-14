# ERA5 no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o ERA5, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o ERA5 aos outros datasets.

## O que é o ERA5

O ERA5 é a **reanálise climática** do ECMWF (Centro Europeu de Previsões Meteorológicas de Médio Prazo), produzida pelo serviço Copernicus de mudanças climáticas. Não é da NASA, mas é aberto e tem cobertura global.

Uma reanálise junta milhões de observações (estações, balões, satélites) num modelo do tempo e reconstrói, hora a hora, como estava a atmosfera e a superfície em cada ponto do planeta. O resultado é uma série contínua, sem buracos.

Há duas versões úteis para o projeto:

- **ERA5:** grade de 0,25° (cerca de 28 km), horária, desde 1940.
- **ERA5-Land:** só sobre os continentes, grade de 0,1° (cerca de 9 km), horária, desde 1950. Detalha melhor temperatura e umidade do solo.

Os dados mais recentes saem com poucos dias de atraso, numa versão preliminar (ERA5T).

## Por que usar

**1. Segunda opinião sobre o NASA POWER.** A meteorologia do POWER vem do MERRA-2, a reanálise da NASA. O ERA5 é outra reanálise, de outra instituição, com outro modelo. Quando os dois concordam, a confiança sobe.

**2. Série muito longa.** Desde 1940 (ERA5) ou 1950 (ERA5-Land). Dá para calcular o "normal" de cada mês com décadas de dados e ver se um risco, como geada ou veranico, mudou de frequência.

**3. Umidade e temperatura do solo em camadas.** O ERA5-Land estima a água no solo em quatro camadas (0–7, 7–28, 28–100 e 100–289 cm) e a temperatura do solo. É um terceiro ponto de vista, ao lado de GLDAS e SMAP L4.

**4. Dados horários.** Permitem contar horas de frio, horas de calor forte e mínimas noturnas, o que médias diárias escondem.

## Como entra no projeto

### Harmonização

- **Acesso:** Copernicus Climate Data Store (CDS), com cadastro gratuito e a biblioteca `cdsapi` em Python. Também há cópias no Google Earth Engine e em nuvem.
- **Processamento:** pedir só o retângulo do Brasil e as variáveis necessárias, agregar de horário para diário e mensal, e reamostrar para a grade comum. O ERA5-Land em 0,1° cobre o Brasil com cerca de 70 mil células: pesado em horário, leve depois de agregado. Por isso os indicadores nacionais são **pré-calculados** (D-008).

| Variável | O que é | Uso |
| --- | --- | --- |
| `t2m` | Temperatura do ar a 2 m | Máximas, mínimas, graus-dia, geada |
| `d2m` | Ponto de orvalho a 2 m | Umidade do ar, risco de doença |
| `tp` | Precipitação total | Comparação com IMERG e POWER |
| `swvl1` a `swvl4` | Água no solo em 4 camadas | Comparação com GLDAS e SMAP L4 |
| `stl1` | Temperatura do solo (0–7 cm) | Época de semeadura |
| `ssrd` | Radiação solar na superfície | Potencial de produção |
| `pev` | Evaporação potencial | Demanda de água da cultura |

> Confirmar nas páginas oficiais a latência atual do ERA5T, os nomes longos usados nos pedidos do CDS, a licença de uso e como cada variável acumulada (`tp`, `ssrd`, `pev`) é somada no ERA5-Land, que acumula desde 00 UTC.

### Indicadores calculados

- **Frequência de geada:** dias por mês com mínima abaixo de um limiar (ex.: 3 °C no abrigo).
- **Veranicos:** sequências de dias secos dentro da estação de chuva.
- **Encharcamento:** meses em que a camada de 0–7 cm fica perto da saturação.
- **Tendência:** a mesma métrica em 1981–2000 e 2001–2020, para mostrar o que mudou.

### Nível de confiança

O ERA5 entra em três comparações: temperatura com o POWER, chuva com IMERG, e umidade do solo com GLDAS e SMAP L4. A independência é **parcial**: as reanálises e os produtos de chuva usam muitas das mesmas observações, inclusive estações do INMET enviadas pela rede internacional. A estação mais próxima do INMET continua sendo a referência local. Atenção também ao **GAEZ v5**: o clima dele vem do AgERA5, que é derivado do ERA5. GAEZ e ERA5 nunca contam como duas confirmações.

## Onde o produtor vê isso

**Etapa 2, calendário de vulnerabilidade.** Faixas de "risco de geada", "veranico" e "solo encharcado" por mês, com a frase "comparado com os últimos 40 anos".

**Cartão da estratégia, em "Evidências".** O ERA5 aparece como uma das fontes que concordam (ou não) com o POWER e o IMERG.

**Glossário.** Explica que reanálise é uma reconstrução do tempo passado feita por modelo, e não uma medição direta.

## Caso hipotético: ERA5 junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Valdir cultiva arroz e cria gado perto de Dom Pedrito, na Campanha gaúcha, bioma Pampa. As lavouras ficam em várzea plana.

- **Rotação atual:** arroz irrigado (outubro a março) e resteva com gado no inverno. O mesmo talhão repete arroz há muitos anos.
- **Irrigação:** inundação no arroz, com água de açude próprio.
- **Prioridades:** renda e forragem altas; solo média.
- **Mercado:** arroz, soja e venda de terneiros.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **ERA5-Land** | Camada de 0–7 cm perto da saturação de junho a agosto em 8 de cada 10 anos. Em média, 12 dias por inverno com mínima abaixo de 3 °C. |
| **ERA5** | Em 5 dos últimos 20 verões, mais de 20 dias seguidos sem chuva relevante entre dezembro e janeiro. |
| NASA POWER | Mesma frequência de geada na célula de 0,5°; verões secos nos mesmos anos. |
| GPM IMERG | Confirma os verões secos (série desde 2000). |
| INMET (estação mais próxima) | Mínimas do inverno 1 °C mais baixas que o ERA5-Land, em média. |
| SRTM | Declividade abaixo de 1%: drenagem lenta. |
| MapBiomas | Arroz no talhão em 9 dos últimos 10 anos. |
| ZARC | Janela de soja para o município aberta de outubro a dezembro. |

### Onde os dados se completam

**O inverno é frio e encharcado.** O ERA5-Land mostra solo saturado no inverno, e o SRTM explica: a várzea é plana e drena devagar. Uma pastagem de inverno precisa tolerar frio e excesso de água.

**A soja corre risco no verão seco.** ERA5, POWER e IMERG concordam sobre os verões secos. São duas reanálises diferentes e um produto de satélite: confiança **alta** para o padrão regional.

**A geada local é mais forte.** A estação do INMET registra mínimas mais baixas que o ERA5-Land. A ferramenta usa a estação para ajustar o limiar e marca a geada no talhão com confiança **média**.

### Regras ativadas

- **Arroz repetido por muitos anos** aumenta o peso das estratégias que incluem soja na rotação.
- **Solo saturado no inverno** limita as culturas de inverno às tolerantes a encharcamento.
- **Prioridade alta em forragem** aumenta o peso das pastagens de inverno.

### Comparação das estratégias

| Critério | A: atual (arroz → resteva com gado) | B: arroz e soja alternados → azevém | C: arroz e soja alternados → azevém com leguminosa tolerante a encharcamento |
| --- | --- | --- | --- |
| Água | ●○○○○ | ●●●○○ | ●●●○○ |
| Solo | ●●○○○ | ●●●○○ | ●●●●○ |
| Nitrogênio | ●○○○○ | ●●○○○ | ●●●●○ |
| Erosão | ●●●○○ | ●●●○○ | ●●●○○ |
| Forragem | ●●○○○ | ●●●●○ | ●●●●● |
| Renda | ●●●○○ | ●●●●○ | ●●●●○ |

Com os pesos do Sr. Valdir (renda e forragem altas, solo média), a **estratégia C** fica em primeiro. Ela empata com a B em renda e ganha em forragem, solo e nitrogênio.

### Cartão da estratégia C

> **Resumo:** uma opção é alternar arroz e soja no verão e, no inverno, formar pasto de azevém com uma leguminosa que aguente solo encharcado.
>
> **Por que foi sugerida:** o talhão repete arroz há anos, o solo fica saturado no inverno e a forragem é uma das suas prioridades.
>
> **Evidências:** solo encharcado no inverno (ERA5-Land e SRTM, confiança alta); verões secos em 1 de cada 4 anos (ERA5, POWER e IMERG, confiança alta); geada frequente (ERA5-Land e INMET, confiança média no talhão).
>
> **Benefícios:** a soja quebra o ciclo de plantas daninhas do arroz, a leguminosa fixa nitrogênio e o gado tem pasto de melhor qualidade no inverno.
>
> **Lacunas:** não sabemos se o talhão tem drenagem para a soja nem a capacidade do açude.
>
> **Riscos para revisão local:** soja em várzea exige drenagem; a leguminosa precisa ser escolhida com o agrônomo para o tipo de solo; o pastejo pesado em solo molhado compacta a várzea.

## Conclusão

O ERA5 é a segunda opinião sobre o clima. Ele não substitui o POWER, mas permite dizer se o POWER está certo, com uma fonte que não deriva dele. A série longa e as camadas de solo do ERA5-Land ajudam a explicar riscos que a chuva sozinha não mostra, como o encharcamento de inverno no Pampa. A estação do INMET fecha a conta no nível local.

## Limitações

- **É modelo, não medição:** suaviza eventos locais, como geadas em baixadas e chuvas de verão muito concentradas.
- **Resolução:** 28 km (ERA5) ou 9 km (ERA5-Land), ainda regional.
- **Chuva menos confiável que temperatura:** para chuva, o IMERG e as estações do INMET costumam ser melhores.
- **Independência parcial:** usa observações que também entram em outros produtos; o AgERA5 do GAEZ deriva dele.
- **Volume:** dados horários para o Brasil inteiro são pesados.
- **Tratamento:** pedir só as variáveis e a área necessárias, pré-calcular os indicadores, cruzar com POWER, IMERG e INMET e mostrar o nível de confiança.
