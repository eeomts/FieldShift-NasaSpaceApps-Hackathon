# ANA HidroWeb no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o HidroWeb, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o HidroWeb aos outros datasets.

## O que é o HidroWeb

O HidroWeb é o sistema da **ANA** (Agência Nacional de Águas e Saneamento Básico) que distribui os dados da **Rede Hidrometeorológica Nacional**. São milhares de estações espalhadas pelo país, operadas pela ANA e por parceiros:

- **Estações pluviométricas:** chuva diária, algumas com séries de muitas décadas.
- **Estações fluviométricas:** nível do rio (cota) e vazão, que mostram quanta água passa num ponto do rio.
- **Estações telemétricas:** enviam dados em quase tempo real, por satélite ou celular.

O HidroWeb faz parte do **SNIRH** (Sistema Nacional de Informações sobre Recursos Hídricos), que também reúne dados de outorgas, disponibilidade hídrica e o Monitor de Secas.

## Por que usar

**1. É o substituto brasileiro do NWIS.** Nos EUA, o desafio usa o NWIS do USGS para rios e poços. Aqui, o HidroWeb cumpre esse papel (D-003).

**2. Água para irrigar depende do rio.** O satélite mostra a chuva e a umidade do solo, mas não diz se o rio terá água em fevereiro. Para quem irriga, a vazão é o dado que importa.

**3. Séries longas de chuva.** Muitas estações pluviométricas da ANA têm décadas de dados. Elas ajudam a validar o GPM IMERG e o CHIRPS onde o INMET não tem estação.

**4. Ponte com a outorga.** O uso de água para irrigação precisa de outorga. Os órgãos gestores usam vazões de referência, como a Q90 ou a Q95, calculadas de séries como as do HidroWeb.

## Como entra no projeto

### Harmonização

- **Acesso:** portal HidroWeb, com busca de estações no mapa e download das séries em CSV ou TXT; serviço web REST da ANA (`hidrowebservice`), com documentação Swagger e acesso por cadastro. Há clientes de terceiros em Python e R, e um plugin para QGIS.
- **Processamento:** escolher as estações fluviométricas da bacia que abastece a propriedade e as pluviométricas num raio de 50 km; usar de preferência dados **consistidos** (já revisados pela ANA); calcular a curva de permanência da vazão e as médias mensais.

| Campo | O que é | Uso |
| --- | --- | --- |
| Código da estação | Identificador na rede | Ligar à bacia e à grade |
| Data | Dia da leitura | Série diária |
| Chuva (mm) | Chuva diária | Validar IMERG e CHIRPS |
| Cota (cm) | Nível do rio | Cheias e secas |
| Vazão (m³/s) | Água que passa no rio | Disponibilidade para irrigar |
| Nível de consistência | Dado bruto ou consistido | Filtrar dados não revisados |

> Confirmar nas páginas oficiais os nomes exatos dos campos, o processo de cadastro e autenticação do serviço web, os limites de consulta e a vazão de referência usada pelo órgão gestor de cada estado (Q90, Q95 ou Q7,10).

### Indicadores calculados

- **Vazões de referência:** Q90 e Q95 da estação mais próxima a jusante da captação.
- **Meses críticos:** meses em que a vazão costuma ficar abaixo da referência.
- **Frequência de escassez:** anos, de cada 10, com vazão abaixo da Q90 no pico da irrigação.
- **Chuva medida:** total mensal e veranicos, para comparar com IMERG e CHIRPS.

### Nível de confiança

A vazão é medida num ponto do rio. Se a estação fica longe da captação, o valor precisa ser ajustado pela área da bacia, e a confiança cai. Séries com muitos anos faltando ou só com dados brutos pesam menos. As estações pluviométricas da ANA podem entrar na calibração do IMERG Final e do CHIRPS, então a concordância com eles **não conta como confirmação independente**. A vazão, por outro lado, é uma medida diferente da chuva e se cruza bem com o GRACE (água armazenada na região) e com o GLDAS (escoamento).

## Onde o produtor vê isso

**Etapa 2, água disponível.** Para quem irriga, uma faixa mensal mostra "água no rio da sua bacia" comparada com a referência de outorga.

**Cartão da estratégia, em "Água".** Estratégias que pedem muita água no mês crítico perdem nota.

**Riscos para revisão local.** Quando o rio fica abaixo da referência com frequência, o cartão lembra de conferir a outorga e o volume do açude.

**Glossário.** Explica vazão, Q90 e outorga.

## Caso hipotético: HidroWeb junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Lauro tem uma propriedade perto de Alegrete, no oeste do Rio Grande do Sul, no Pampa. Planta arroz irrigado em várzea e cria gado de corte no campo nativo.

- **Rotação atual:** arroz irrigado por inundação (outubro a março) por dois anos, depois dois anos de pousio com pastejo.
- **Irrigação:** sim, com água bombeada do rio e de um açude.
- **Prioridades:** água e renda altas; forragem média.
- **Mercado:** arroz, soja e gado de corte.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **HidroWeb (vazão)** | Na estação a jusante da captação, a vazão ficou abaixo da Q90 em janeiro ou fevereiro em 4 dos últimos 10 anos. |
| **HidroWeb (chuva)** | Estação da ANA a 18 km mostra janeiros secos nos mesmos anos. |
| GPM IMERG | Mesmo padrão de chuva (não independente da estação). |
| GRACE | Água armazenada na região abaixo do normal nos anos de La Niña. Entra só como contexto (D-005). |
| SMAP / GLDAS | Solo da várzea encharcado no inverno e seco no verão dos anos críticos. |
| MapBiomas | Arroz e campo nativo alternando no talhão desde 1990. |
| SRTM | Várzea plana, com drenagem lenta. |
| IBGE PAM | Área de soja crescendo no município nos últimos 10 anos. |

### Onde os dados se completam

**O arroz depende do mês em que o rio está mais baixo.** O arroz pede mais água em janeiro e fevereiro. O HidroWeb mostra que, em 4 de 10 anos, o rio ficou abaixo da referência justamente nesses meses. A chuva da ANA, o IMERG e o GRACE explicam o porquê: verões secos na região. Vazão e chuva são medidas diferentes, então a confiança no risco é **alta**.

**A soja usa menos água.** A soja em terras baixas não precisa de inundação. Com drenagem, ela entra na rotação e reduz a demanda de água no verão.

**O pasto do pousio vale mais com inverno cultivado.** O campo nativo do pousio produz pouco no inverno. O azevém depois da soja dá forragem no frio.

### Regras ativadas

- **Vazão abaixo da referência no pico da irrigação** reduz a nota de água das estratégias com mais arroz.
- **Várzea com drenagem lenta** adiciona o risco de encharcamento às culturas de sequeiro.
- **Gado na propriedade** aumenta o peso das forrageiras de inverno.

### Comparação das estratégias

| Critério | A: atual (arroz → pousio com pastejo) | B: arroz → soja em terras baixas → arroz | C: arroz → soja → azevém para pastejo no inverno |
| --- | --- | --- | --- |
| Água | ●○○○○ | ●●●○○ | ●●●○○ |
| Solo | ●●○○○ | ●●●○○ | ●●●●○ |
| Nitrogênio | ●●○○○ | ●●●○○ | ●●●○○ |
| Erosão | ●●●○○ | ●●●○○ | ●●●●○ |
| Forragem | ●●●○○ | ●●○○○ | ●●●●● |
| Renda | ●●●○○ | ●●●●○ | ●●●●○ |

Com os pesos do Sr. Lauro (água e renda altas, forragem média), a **estratégia C** fica em primeiro. Ela empata com a B em água e renda e ganha com folga em forragem.

### Cartão da estratégia C

> **Resumo:** uma opção é intercalar o arroz com soja em terras baixas e, depois da soja, semear azevém para o gado pastejar no inverno.
>
> **Por que foi sugerida:** em 4 dos últimos 10 anos, o rio que abastece sua lavoura ficou abaixo da vazão de referência em janeiro ou fevereiro, quando o arroz mais precisa de água.
>
> **Evidências:** vazão baixa no pico da irrigação (HidroWeb, confiança alta); verões secos (estação da ANA e IMERG, que não são independentes; GRACE como contexto); histórico de arroz e campo (MapBiomas, confiança alta); várzea plana (SRTM, confiança alta).
>
> **Benefícios:** menos água bombeada nos anos de soja, quebra do ciclo de plantas daninhas do arroz e forragem no inverno.
>
> **Lacunas:** não sabemos o volume do açude, a vazão outorgada nem se a área já tem drenagem.
>
> **Riscos para revisão local:** a soja em várzea exige drenagem (sulcos ou camalhões); conferir com o agrônomo. Verificar a outorga com o órgão gestor de água e ajustar a lotação do azevém.

## Conclusão

O HidroWeb leva a ferramenta do céu para o rio. A chuva e o solo mostram o que cai na lavoura; a vazão mostra se haverá água para bombear. Para quem irriga, como no arroz do Pampa ou nos pivôs do Cerrado, esse é muitas vezes o limite que decide a rotação. Para quem não irriga, o HidroWeb entra só com as estações de chuva.

## Limitações

- **Estação longe da captação:** a vazão precisa ser ajustada pela área da bacia.
- **Rede desigual:** há rios sem estação ou com séries curtas.
- **Dados brutos:** os mais recentes ainda não foram consistidos.
- **Não mede o açude nem o poço:** a água guardada na propriedade fica de fora.
- **Outorga é regra local:** a vazão de referência e o órgão gestor mudam por estado e por rio.
- **Tratamento:** usar dados consistidos, mostrar a distância até a estação, cruzar vazão com GRACE e GLDAS e lembrar sempre de conferir a outorga.
