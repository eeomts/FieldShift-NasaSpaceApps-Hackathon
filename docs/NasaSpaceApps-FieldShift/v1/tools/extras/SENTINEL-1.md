# Sentinel-1 no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o Sentinel-1, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o Sentinel-1 aos outros datasets.

## O que é o Sentinel-1

O Sentinel-1 é a missão de **radar** do programa Copernicus, da União Europeia, operada pela ESA. Em vez de fotografar a luz do sol, o satélite emite um pulso de micro-ondas (banda C) e mede o que volta, o chamado **retroespalhamento**. Por isso funciona **de dia, de noite e através das nuvens**.

- **Modo usado sobre terra:** IW (*Interferometric Wide swath*), faixa de 250 km, com pixel de 10 m no produto GRD.
- **Polarizações:** VV e VH. A VH reage muito à estrutura da vegetação (folhas, caules); a VV reage mais ao solo e à umidade da superfície.
- **Satélites:** Sentinel-1A (desde 2014), 1B (2016 a 2021, perdido por falha), 1C (lançado em dezembro de 2024) e 1D (lançado em novembro de 2025).
- **Revisita:** 12 dias com um satélite na mesma órbita; 6 dias com dois.

Os dados são gratuitos. O arquivo completo também é distribuído pela **ASF**, o centro de dados de radar da NASA.

## Por que usar

**1. A safra brasileira acontece debaixo de nuvem.** A soja do Centro-Oeste e do Norte cresce na estação chuvosa. Nesses meses, o HLS pode ter uma ou nenhuma imagem limpa por mês. O radar não depende disso.

**2. Fecha o calendário do talhão.** A VH sobe quando a lavoura fecha e cai de uma vez na colheita. Com isso dá para estimar as datas de plantio e colheita mesmo sem imagem óptica. É o papel que o `HLS.md` já prevê para ele.

**3. É uma fonte independente do óptico.** Radar e óptico medem coisas diferentes. Quando os dois concordam no calendário, a confiança sobe de verdade.

**4. Ponte com produtos da NASA.** O projeto OPERA, do JPL, gera o **RTC-S1**: retroespalhamento do Sentinel-1 já corrigido para o relevo, em 30 m. Isso tira a parte mais difícil do processamento de radar.

## Como entra no projeto

### Harmonização

- **Escala:** só nos pontos e regiões de demonstração, como o HLS. O Brasil inteiro em 10 m a cada 12 dias é volume demais para o hackathon.
- **Acesso:** ASF (Vertex ou `asf_search`, com login do Earthdata) para o GRD e o OPERA RTC-S1; Copernicus Data Space para o GRD.
- **Processamento:** usar o RTC-S1 quando houver; se não, calibrar o GRD, corrigir o relevo, aplicar um filtro de ruído (*speckle*), converter para decibéis e tirar a média por talhão em cada passagem. Comparar sempre imagens da **mesma órbita** (mesma geometria).

| Variável | O que é | Uso |
| --- | --- | --- |
| VH (dB) | Retroespalhamento cruzado | Crescimento e colheita da lavoura |
| VV (dB) | Retroespalhamento copolarizado | Solo exposto e umidade da superfície |
| VH/VV | Razão entre as duas | Separar vegetação de solo, menos sensível à chuva do dia |
| RVI | Índice de vegetação por radar | Série comparável ao NDVI, sem nuvens |
| Máscara do RTC-S1 | Áreas de sombra e sobreposição do radar | Descartar pixels ruins em relevo forte |

> Confirmar nas páginas oficiais a cobertura do Brasil no plano de aquisição atual (com 1C e 1D), se o arquivo histórico do OPERA RTC-S1 cobre o Brasil desde 2016 ou só a partir do processamento recente, e a fórmula do RVI adotada pela equipe. A missão NISAR (NASA e ISRO, radar em banda L) pode ser um complemento futuro; verificar a disponibilidade dos dados.

### Indicadores calculados

- **Datas de plantio e colheita:** início da subida e queda brusca da VH, por talhão e por safra.
- **Duração da cobertura:** dias entre a subida e a queda.
- **Solo exposto na safra:** períodos com VH baixa em meses em que o óptico não tem imagem.

### Nível de confiança

O radar também se engana. Chuva no dia da passagem molha o solo e sobe a VV. Relevo forte cria sombras. Lavouras diferentes podem ter curvas parecidas. Por isso o calendário do radar é sempre cruzado com o HLS nos meses em que há imagem limpa e com o que o produtor informou. Se radar e óptico concordam, a confiança é **alta**. Se só o radar cobre o período, é **média**.

Do começo de 2022 até a entrada em operação do 1C, em 2025, havia só um satélite em órbita. Nesses anos, a série tem menos passagens, e isso aparece no indicador.

## Onde o produtor vê isso

**Etapa 3, conferência da rotação.** O calendário de cada safra mostra as datas estimadas de plantio e colheita, com um aviso quando a data veio só do radar.

**Cartão da estratégia.** Exemplo: "Em 3 dos últimos 6 anos, sua soja foi colhida depois de 10 de abril."

**Glossário.** Explica que o radar "sente" a estrutura da planta, não a cor, e por isso enxerga através das nuvens.

## Caso hipotético: Sentinel-1 junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Raimundo planta grãos perto de Paragominas, no Pará, na borda da Amazônia. A área era pastagem degradada e virou lavoura há cerca de dez anos.

- **Rotação atual:** soja (janeiro a abril ou maio) e milho safrinha em seguida, quando dá tempo. Nos outros anos, pousio.
- **Irrigação:** não tem.
- **Prioridades:** renda e solo altas; água média.
- **Mercado:** soja e milho para tradings da região; há pecuaristas vizinhos que compram pasto.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **Sentinel-1** | Série completa de janeiro a maio em todos os anos. Em 3 de 6 safras, a queda da VH (colheita da soja) veio depois de 10 de abril. Nesses anos, o milho plantado depois teve VH máxima 30% menor. |
| HLS | De 0 a 1 imagem limpa por mês de janeiro a abril. Confirma as colheitas de maio, mas não as de abril. |
| GPM IMERG | A chuva termina, em média, na primeira quinzena de junho. |
| GLDAS / SMAP L4 | A zona das raízes cai abaixo do normal a partir de junho. |
| FIRMS | Focos no entorno entre setembro e novembro na maioria dos anos. |
| MapBiomas | Pastagem até 2015; soja a partir de 2016. Não separa o milho safrinha. |

### Onde os dados se completam

**Sem o radar, o calendário seria adivinhado.** O HLS quase não tem imagem limpa nos meses que decidem a safrinha. O Sentinel-1 mostra a data real da colheita em cada ano.

**A data da colheita explica o milho fraco.** Quando a soja sai depois de 10 de abril, o milho cresce com a chuva acabando (IMERG) e o solo secando (GLDAS e SMAP L4). Calendário com confiança **média** nos anos de abril (só radar) e **alta** nos anos de maio (radar e HLS).

**O solo ainda é de pasto recuperado.** O MapBiomas mostra pastagem até 2015. Solo de pasto degradado ganha muito com raiz e palha.

### Regras ativadas

- **Colheita tardia em metade dos anos** aumenta o peso de uma regra condicional para a segunda cultura.
- **Fim de chuva em junho** reduz a nota de água do milho plantado tarde.
- **Histórico de pastagem degradada e prioridade alta em solo** aumentam o peso de braquiária consorciada.
- **Fogo no entorno na seca** adiciona um risco às estratégias com palhada.

### Comparação das estratégias

| Critério | A: atual (soja → milho ou pousio) | B: soja → milho safrinha todo ano | C: soja → milho + braquiária se a soja sair até 10/4; só braquiária depois disso |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●○○○ | ●●●○○ |
| Solo | ●○○○○ | ●●○○○ | ●●●●○ |
| Nitrogênio | ●●○○○ | ●●○○○ | ●●○○○ |
| Erosão | ●●○○○ | ●●●○○ | ●●●●○ |
| Forragem | ●○○○○ | ●●○○○ | ●●●●○ |
| Renda | ●●●○○ | ●●●●○ | ●●●○○ |

A B tem a melhor renda, mas arrisca o milho nos anos de colheita tardia. Com renda e solo altos, a **estratégia C** fica em primeiro: perde um ponto em renda e ganha dois em solo. A B fica em segundo.

### Cartão da estratégia C

> **Resumo:** uma opção é decidir a segunda cultura pela data de colheita da soja: milho com braquiária quando a soja sai até 10 de abril; só braquiária, para cobertura ou pasto, quando sai depois.
>
> **Por que foi sugerida:** em metade dos últimos seis anos sua soja saiu depois de 10 de abril, e o milho desses anos rendeu menos porque a chuva acaba em junho.
>
> **Evidências:** datas de colheita (Sentinel-1, confiança média a alta, conforme o ano); fim da chuva (GPM IMERG, confiança alta); solo secando a partir de junho (GLDAS e SMAP L4, confiança alta); histórico de pastagem (MapBiomas, confiança alta).
>
> **Benefícios:** menos milho plantado fora de hora, raiz e palha para recuperar o solo de pasto e a opção de vender pasto aos vizinhos na seca.
>
> **Lacunas:** não sabemos o custo da semente de braquiária nem se há acordo com os pecuaristas.
>
> **Riscos para revisão local:** conferir com o agrônomo a data-limite do milho na sua região e o ZARC do município; planejar a dessecação da braquiária antes da soja; manter aceiros, porque o entorno queima de setembro a novembro.

## Conclusão

O Sentinel-1 é o que permite à ferramenta funcionar na borda da Amazônia e no Centro-Oeste na época das chuvas. Ele não diz qual cultura está no talhão, mas diz quando ela nasceu e quando saiu. Junto com chuva e água no solo, essa data explica por que uma safrinha deu certo ou não. Nas regiões de céu limpo, ele vira só uma confirmação extra.

## Limitações

- **Ruído de radar (*speckle*):** pixel a pixel, o sinal é granulado; trabalhar com médias por talhão.
- **Chuva no dia da passagem:** molha o solo e altera o sinal, principalmente na VV.
- **Relevo forte:** gera sombra e sobreposição; usar a máscara do RTC-S1.
- **Não identifica a cultura sozinho:** a curva mostra o ciclo, mas a cultura vem do produtor e do MapBiomas.
- **Menos passagens de 2022 a 2025:** só o 1A operava até o 1C entrar em serviço.
- **Processamento mais difícil que o óptico:** preferir o OPERA RTC-S1 quando ele cobrir a área.
- **Tratamento:** média por talhão, mesma órbita, máscara de sombra, cruzamento com HLS e com a rotação informada.
