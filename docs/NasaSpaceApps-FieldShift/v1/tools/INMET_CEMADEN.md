# INMET e CEMADEN no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o INMET e o CEMADEN, como eles entram na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o INMET e o CEMADEN aos outros datasets.

## O que são o INMET e o CEMADEN

O **INMET** (Instituto Nacional de Meteorologia) mantém a principal rede oficial de **estações meteorológicas** do Brasil:

- **Estações convencionais:** leituras feitas por observador, algumas com séries desde 1961. Os dados diários ficam no **BDMEP** (Banco de Dados Meteorológicos).
- **Estações automáticas:** dados de hora em hora (chuva, temperatura, umidade, radiação, vento e pressão), a partir dos anos 2000.
- **Normais climatológicas 1991–2020:** médias oficiais por estação.

O **CEMADEN** (Centro Nacional de Monitoramento e Alertas de Desastres Naturais) mantém uma rede de **pluviômetros automáticos** em municípios com risco de desastres, além de estações no Semiárido para monitorar a seca. Também publica o **Alerta-Secas**, um mapa da severidade da seca por município.

## Por que usar

**1. São o substituto brasileiro do CoCoRaHS.** Nos EUA, o desafio usa uma rede de pluviômetros de voluntários. Aqui, INMET e CEMADEN cumprem esse papel (D-003).

**2. Chuva medida no chão.** O GPM IMERG e o NASA POWER estimam a chuva em células de 10 a 50 km. Um pluviômetro mede num ponto. Comparar os dois mostra se o satélite erra muito na região.

**3. Veranicos e chuvas fortes.** Estimativas de satélite costumam suavizar extremos. A estação mostra melhor as chuvas de 80 mm em uma hora e os 20 dias sem chuva no meio da safra.

**4. Validação do projeto.** A Q-11 cita as estações do INMET como forma de validar a ferramenta.

## Como entra no projeto

### Harmonização

- **Acesso INMET:** portal de dados históricos, com um arquivo ZIP por ano contendo um CSV por estação automática; BDMEP para as séries diárias das convencionais; API de dados meteorológicos (`apitempo.inmet.gov.br`), que pede cadastro e token.
- **Acesso CEMADEN:** mapa interativo da rede observacional, com download de dados dos pluviômetros por estado e período.
- **Processamento:** juntar os dados por estação, tirar valores inválidos (o INMET usa código para dado ausente), somar a chuva por dia e por mês e marcar os meses com muitas falhas. Depois, ligar cada estação à célula da grade comum e às células vizinhas num raio de 50 km.

| Variável | O que é | Uso |
| --- | --- | --- |
| Precipitação (mm) | Chuva por hora ou por dia | Validar IMERG e POWER |
| Temperatura do ar (°C) | Máxima, mínima, horária | Validar POWER, calor e geada |
| Umidade relativa (%) | Umidade do ar | Risco de fogo e doenças |
| Radiação global | Energia do sol | Validar POWER e evapotranspiração |
| Vento | Velocidade e direção | Evapotranspiração e deriva |
| Chuva CEMADEN (mm) | Acumulado em intervalos curtos | Densificar a rede onde o INMET é raro |

> Confirmar nas páginas oficiais os nomes das colunas e as linhas de cabeçalho dos CSVs do INMET, as regras e o token da API, o intervalo de registro dos pluviômetros do CEMADEN, o formato do download no mapa interativo e se as estações do Semiárido têm sensores de umidade do solo com dados abertos.

### Indicadores calculados

- **Viés do satélite:** diferença média entre a chuva do IMERG e a do pluviômetro, por mês.
- **Veranicos:** sequências de 10, 15 ou 20 dias sem chuva relevante dentro da estação chuvosa.
- **Chuvas extremas:** dias acima de 50 mm por ano.
- **Início e fim da chuva:** data típica, para comparar com o ZARC.
- **Geada:** dias com mínima abaixo de 2 °C no abrigo.

### Nível de confiança

O pluviômetro mede um ponto. Uma estação a 40 km pode não representar o talhão, sobretudo com chuva de trovoada. A série precisa ter poucos buracos. Atenção: o **IMERG Final** usa pluviômetros na calibração, e parte deles pode ser do INMET. Por isso, concordância entre IMERG e INMET **não conta como duas fontes independentes**. A rede do CEMADEN, mais densa e mais recente, ajuda a ter uma comparação mais limpa.

## Onde o produtor vê isso

**Etapa 2, calendário de vulnerabilidade.** Uma linha "chuva medida na estação mais próxima" aparece ao lado da estimativa de satélite, com a distância até a estação.

**Cartão da estratégia, em "Evidências".** Exemplo: "veranico de 15 dias ou mais em março em 6 dos últimos 10 anos (pluviômetro a 12 km)".

**Glossário.** Explica a diferença entre chuva medida e chuva estimada por satélite.

## Caso hipotético: INMET e CEMADEN junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

Dona Francisca é agricultora familiar perto de Serra Talhada, no sertão de Pernambuco, no Semiárido. Tem 8 hectares e um pequeno rebanho de cabras.

- **Rotação atual:** milho com feijão consorciados (fevereiro a junho), pousio no resto do ano.
- **Irrigação:** não tem; a cisterna é só para a casa.
- **Prioridades:** água e forragem altas; renda média.
- **Mercado:** feijão vendido na feira; milho e palha para os animais.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **CEMADEN** | Pluviômetro a 12 km. Veranico de 15 dias ou mais entre fevereiro e abril em 6 dos últimos 10 anos. |
| **INMET** | Estação automática a 40 km. Mesmo padrão de veranicos; máximas acima de 34 °C em março e abril. |
| GPM IMERG | Chuva total parecida com a do pluviômetro, mas só 3 veranicos longos em 10 anos. |
| NASA POWER | Evapotranspiração de referência muito acima da chuva em todos os meses, menos em março. |
| GLDAS / SMAP L4 | Zona das raízes seca em poucos dias depois de cada chuva. |
| HLS | O milho seca antes de encher o grão em metade dos anos. |
| ZARC | Para o município, o milho tem janela curta e de risco mais alto que o feijão-caupi e o sorgo. |
| Alerta-Secas (CEMADEN) | Seca moderada a severa em 4 dos últimos 10 anos. |

### Onde os dados se completam

**O satélite esconde os veranicos.** O IMERG acerta o total de chuva, mas suaviza os dias secos e conta só 3 veranicos longos. O pluviômetro do CEMADEN conta 6. A estação do INMET, mais longe, concorda com o CEMADEN. As duas redes são independentes entre si, então a confiança é **alta**.

**O problema é a chuva mal distribuída.** O total do ano até daria para o milho. Mas o solo seca rápido (GLDAS e SMAP L4), e um veranico no florescimento basta para perder a espiga, como o HLS mostra.

### Regras ativadas

- **Veranicos frequentes no ciclo** aumentam o peso das culturas tolerantes à seca.
- **Rebanho e prioridade alta em forragem** aumentam o peso de culturas para os animais.
- **Diferença grande entre satélite e pluviômetro** faz a ferramenta usar o pluviômetro nos indicadores de veranico.

### Comparação das estratégias

| Critério | A: atual (milho + feijão) | B: sorgo granífero + feijão-caupi | C: feijão-caupi + sorgo forrageiro, com reserva de palma |
| --- | --- | --- | --- |
| Água | ●○○○○ | ●●●○○ | ●●●●○ |
| Solo | ●●○○○ | ●●●○○ | ●●●○○ |
| Nitrogênio | ●●●○○ | ●●●○○ | ●●●○○ |
| Erosão | ●●○○○ | ●●●○○ | ●●●○○ |
| Forragem | ●●○○○ | ●●●○○ | ●●●●● |
| Renda | ●●●○○ | ●●●○○ | ●●○○○ |

Com os pesos de Dona Francisca (água e forragem altas, renda média), a **estratégia C** fica em primeiro. Ela tem a melhor nota nos dois critérios que mais pesam. Perde um pouco em renda, porque sobra menos grão para vender.

### Cartão da estratégia C

> **Resumo:** uma opção é trocar o milho por sorgo forrageiro, manter o feijão-caupi e reservar uma parte da área para palma forrageira, que guarda alimento para os animais na seca.
>
> **Por que foi sugerida:** o pluviômetro perto da sua propriedade registrou veranicos longos no meio da safra em 6 dos últimos 10 anos, e o milho perdeu a espiga em metade deles.
>
> **Evidências:** veranicos (CEMADEN e INMET, confiança alta); solo que seca rápido (GLDAS e SMAP L4, confiança média por ser escala regional); milho falhando (HLS, confiança média); janela de risco (ZARC).
>
> **Benefícios:** o sorgo rebrota depois de um veranico, o caupi tolera calor e a palma garante forragem no fim da seca.
>
> **Lacunas:** não sabemos a distância real até o pluviômetro mais próximo da sua roça nem o tamanho do rebanho.
>
> **Riscos para revisão local:** a palma sofre com a cochonilha; buscar variedades resistentes com a extensão rural (IPA ou ATER). Confirmar sementes de sorgo e caupi adaptadas à região.

## Conclusão

INMET e CEMADEN são o **chão** dos dados de clima. O satélite cobre todo o país, mas suaviza os extremos que mais machucam a lavoura. A estação mostra o veranico como ele foi. No Semiárido, onde a distribuição da chuva importa mais que o total, essa diferença muda a estratégia.

## Limitações

- **Rede rala:** em boa parte do interior a estação mais próxima fica a dezenas de quilômetros.
- **Falhas nas séries:** estações automáticas têm meses com dados faltando.
- **Ponto, não área:** um pluviômetro não representa bem chuvas de trovoada.
- **Séries curtas:** a rede do CEMADEN é recente e não serve para normais climatológicas.
- **Não independentes do IMERG Final:** parte das estações entra na calibração do satélite.
- **Tratamento:** mostrar a distância até a estação, marcar meses com falha, usar várias estações vizinhas e tratar a concordância com o IMERG com cautela.
