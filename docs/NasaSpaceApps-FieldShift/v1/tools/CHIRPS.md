# CHIRPS no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o CHIRPS, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o CHIRPS aos outros datasets.

## O que é o CHIRPS

O CHIRPS (Climate Hazards Center InfraRed Precipitation with Station data) é uma série de **chuva sobre os continentes** feita pelo Climate Hazards Center da Universidade da Califórnia em Santa Bárbara, com apoio do USGS. Não é da NASA, mas é aberto e muito usado em monitoramento de seca.

Junta três ingredientes:

- **Satélite infravermelho:** estima a chuva pela temperatura do topo das nuvens, vista por satélites geoestacionários.
- **Climatologia:** o "normal" de chuva de cada lugar, calibrado com dados de estações.
- **Estações:** pluviômetros de várias redes, usados para corrigir a estimativa.

Resolução de **0,05° (cerca de 5 km)**, desde **1981**. A versão 2.0 cobre de 50° S a 50° N. A **versão 3**, lançada em 2025, cobre de 60° S a 60° N e usa muito mais estações. As duas cobrem o Brasil inteiro.

## Por que usar

**1. Série longa em resolução fina.** O IMERG começa em 2000; o CHIRPS volta a 1981. Com mais de 40 anos, dá para dizer com mais segurança "em quantos anos de cada 10" a chuva falhou num mês.

**2. Feito para seca.** O produto foi criado para alertas de seca em regiões agrícolas. Trabalha bem com acumulados de 5 dias (pentadas), que é a escala certa para ver veranicos e o começo real da estação chuvosa.

**3. Reforça o IMERG.** Usa outro método de satélite (infravermelho, não micro-ondas). Quando os dois concordam, a confiança sobe. Mas a independência é parcial, como explicado em "Nível de confiança".

**4. Leve de processar.** Um único valor de chuva por célula e por período, em arquivos simples.

## Como entra no projeto

### Harmonização

- **Acesso:** servidor do Climate Hazards Center, em GeoTIFF e NetCDF, sem cadastro. Também está no Google Earth Engine.
- **Processamento:** recortar o Brasil (cerca de 280 mil células de 5 km), somar por pentada e por mês e reamostrar para a grade comum. Para o talhão, usar a célula de 5 km que o contém.
- **Versões:** a **preliminar** sai dois dias depois de cada pentada; a **final** sai uma vez por mês, cerca de três semanas depois do fim do mês. Para séries históricas, usar só a final.

| Variável / produto | O que é | Uso |
| --- | --- | --- |
| `precip` (pentadal) | Chuva acumulada em 5 dias, em mm | Veranicos e início da estação |
| `precip` (mensal) | Chuva acumulada no mês | Climatologia e anomalias |
| `precip` (diário) | Chuva do dia, derivada da pentada | Calendário fino, com cuidado em extremos |
| CHIRP (sem estações) | Só satélite e climatologia | Checar o efeito das estações |

> Confirmar nas páginas oficiais se a versão 3 já tem produto diário para todo o período, os nomes das coleções no Earth Engine e quais redes brasileiras de estações entram em cada versão.

### Indicadores calculados

- **Início da estação:** primeira pentada com chuva acumulada suficiente e sem pausa longa logo depois.
- **Veranicos:** sequências de pentadas secas dentro da estação, por mês.
- **Anos secos:** em quantos anos a chuva da estação ficou abaixo do percentil 20.
- **Comparação de décadas:** 1981–2000 contra 2001–2020.

### Nível de confiança

O CHIRPS é comparado com o IMERG, o ERA5 e os pluviômetros locais. Cuidado com a contagem de fontes:

- O CHIRPS usa estações das redes internacionais, onde entram estações do INMET. Comparar o CHIRPS com uma estação que ele mesmo usou **não é validação independente**.
- O IMERG Final também é ajustado com pluviômetros. CHIRPS e IMERG podem compartilhar parte da mesma base de estações.
- Pluviômetros do CEMADEN, da ANA ou de agências estaduais que **não** entram no CHIRPS são a melhor checagem.

Na faixa litorânea do Nordeste, parte da chuva vem de nuvens "quentes", que o infravermelho enxerga mal. Ali o CHIRPS tende a errar mais, e o IMERG pesa mais.

## Onde o produtor vê isso

**Etapa 2, calendário de chuva.** Uma faixa por pentada mostra quando a chuva costuma começar e onde costumam cair os veranicos.

**Janela de plantio.** "Na sua região, em 1 de cada 3 anos a chuva para por 15 dias logo depois de começar." Junto com o ZARC, ajuda a mostrar o risco de plantar cedo.

**Cartão da estratégia, em "Evidências".** O CHIRPS aparece ao lado do IMERG como fonte da regularidade da chuva.

## Caso hipotético: CHIRPS junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

A Sra. Lúcia tem 8 hectares perto de Serra Talhada, no Sertão do Pajeú (PE), região de Caatinga e Semiárido. É agricultora familiar e cria algumas cabras.

- **Rotação atual:** milho e feijão consorciados na chuva (fevereiro a maio) e pousio no resto do ano.
- **Irrigação:** não tem; usa cisterna só para casa e animais.
- **Prioridades:** água e renda altas; forragem média.
- **Mercado:** feira local e programas públicos de compra de alimentos.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **CHIRPS** | A chuva começa de fato, em média, na primeira quinzena de fevereiro. Em 15 dos últimos 44 anos houve 3 ou mais pentadas secas seguidas em março. A década de 2011–2020 teve mais anos secos que a de 1991–2000. |
| GPM IMERG | Concorda sobre as pausas de março (desde 2000), com mais chuvas fortes isoladas. |
| Pluviômetro do CEMADEN no município | Confirma as pausas de março nos anos em que tem dados (fora da base do CHIRPS, a confirmar). |
| GLDAS / SMAP L4 | Nos anos com pausa, a zona das raízes seca em cerca de 20 dias. |
| NASA POWER | Evapotranspiração de referência alta o ano inteiro; máximas acima de 34 °C em março. |
| MODIS NDVI | Roçado verde só de fevereiro a maio; solo descoberto o resto do ano. |
| SRTM | Declividade de 6 a 10% em parte do roçado. |
| ZARC | Risco alto para milho na maioria das datas; risco menor para feijão-caupi e sorgo. |

### Onde os dados se completam

**A pausa de março é o problema central.** O CHIRPS mostra, com 44 anos, que a pausa acontece em cerca de 1 de cada 3 anos. O IMERG concorda no período em comum, e o GLDAS e o SMAP L4 mostram que a raiz fica sem água nessa pausa. O milho, que floresce em março e abril, é a cultura mais exposta. Confiança **alta**, com a ressalva de que CHIRPS e IMERG não são totalmente independentes.

**A série longa muda a leitura.** O IMERG, desde 2000, já mostra a pausa. Mas só o CHIRPS, desde 1981, permite comparar décadas e ver que ela ficou um pouco mais comum em 2011–2020.

**Solo descoberto em declive.** O MODIS mostra o roçado descoberto por 8 meses, e o SRTM mostra declive. As primeiras chuvas fortes levam o solo.

### Regras ativadas

- **Pausa frequente na floração do milho** aumenta o peso de culturas tolerantes à seca e de ciclo curto.
- **Solo descoberto em declive** aumenta o peso de culturas que deixam resto no chão.
- **Prioridade média em forragem** dá peso a culturas que servem para as cabras.

### Comparação das estratégias

| Critério | A: atual (milho + feijão → pousio) | B: sorgo + feijão-caupi → restos para as cabras | C: feijão-caupi precoce; sorgo forrageiro se a chuva continuar |
| --- | --- | --- | --- |
| Água | ●○○○○ | ●●●●○ | ●●●○○ |
| Solo | ●○○○○ | ●●●○○ | ●●○○○ |
| Nitrogênio | ●●○○○ | ●●○○○ | ●●●○○ |
| Erosão | ●○○○○ | ●●●○○ | ●●○○○ |
| Forragem | ●●○○○ | ●●●●○ | ●●●○○ |
| Renda | ●●●○○ | ●●●○○ | ●●●●○ |

Com os pesos da Sra. Lúcia (água e renda altas, forragem média), a **estratégia B** fica em primeiro, com a C logo atrás. A C ganha em renda e nitrogênio, mas perde em água, forragem, solo e erosão.

### Cartão da estratégia B

> **Resumo:** uma opção é trocar o milho pelo sorgo, mantendo o feijão-caupi no consórcio, e deixar os restos no roçado para cobrir o solo e alimentar as cabras.
>
> **Por que foi sugerida:** em cerca de 1 de cada 3 anos a chuva para por 15 dias ou mais em março, justamente quando o milho floresce.
>
> **Evidências:** pausas de chuva em março (CHIRPS, 44 anos, e IMERG, confiança alta); raiz sem água nas pausas (GLDAS e SMAP L4, confiança média); risco por cultura (ZARC); solo descoberto em declive (MODIS e SRTM, confiança alta).
>
> **Benefícios:** o sorgo aguenta melhor a pausa e rebrota, o caupi tem ciclo curto e os restos viram forragem e cobertura.
>
> **Lacunas:** não sabemos o preço do sorgo na sua feira nem se há semente adaptada disponível.
>
> **Riscos para revisão local:** confirmar com a extensão rural as variedades de sorgo e caupi da região, o espaçamento do consórcio e quanto resto pode ir para as cabras sem deixar o solo descoberto.

## Conclusão

O CHIRPS dá à ferramenta memória longa sobre a chuva. No Semiárido, onde a pergunta é "quantas vezes a chuva falha?", 40 anos de dados valem mais que 15. Junto com o IMERG ele mostra a regularidade da chuva; junto com GLDAS e SMAP L4, o efeito disso na raiz. A cautela é contar as fontes com honestidade, porque as estações que corrigem o CHIRPS também aparecem em outros produtos.

## Limitações

- **Infravermelho é indireto:** erra mais com nuvens "quentes", como no litoral do Nordeste.
- **Diário é derivado:** o valor diário vem da pentada; extremos diários são menos confiáveis.
- **Poucas estações, mais erro:** onde há poucos pluviômetros, como em partes da Amazônia, a correção é fraca.
- **Independência parcial:** compartilha estações com IMERG e outros produtos.
- **Só continente:** não cobre oceano, o que não afeta o projeto.
- **Tratamento:** usar a versão final, trabalhar em pentadas, comparar com IMERG e com pluviômetros fora da base do CHIRPS, e mostrar o nível de confiança.
