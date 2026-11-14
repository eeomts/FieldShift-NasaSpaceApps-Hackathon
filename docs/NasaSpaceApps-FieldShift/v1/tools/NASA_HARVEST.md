# NASA Harvest no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o NASA Harvest, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o Harvest aos outros datasets.

## O que é o NASA Harvest

O NASA Harvest é o **programa de agricultura e segurança alimentar** da NASA. Foi criado em 2017 como um consórcio liderado pela Universidade de Maryland, com universidades, governos, organizações internacionais e empresas parceiras no mundo todo.

Ele **não é um dataset**. É uma rede que transforma dados de satélite em informação para quem decide sobre agricultura. Entre o que produz e mantém:

- **GEOGLAM Crop Monitor:** boletins mensais sobre as condições das principais safras do mundo, feitos com parceiros de cada país.
- **Harvest GLAM:** sistema de monitoramento agrícola com séries de NDVI e máscaras de cultura. Houve uma versão adaptada para a Conab, com máscaras de cultura específicas do Brasil.
- **CropHarvest:** base aberta de pontos rotulados com o tipo de cultura, para treinar e testar mapas.
- **Código aberto** no GitHub e iniciativas regionais, entre elas uma para a América Latina.

No Brasil, parceiros do programa também publicaram estudos sobre a expansão da soja na América do Sul, com mapas anuais feitos a partir do Landsat.

## Por que usar

**1. Metodologia testada.** O Harvest já resolveu problemas que a equipe vai enfrentar: separar culturas pela curva do NDVI, detectar duas safras no mesmo ano, lidar com nuvens. Seguir esses métodos economiza tempo e evita erros comuns.

**2. Contexto da safra.** O Crop Monitor diz, mês a mês, se a safra de uma região está normal, abaixo ou acima do esperado. Isso ajuda a explicar um ano ruim que aparece nos dados do talhão.

**3. Credibilidade no pitch.** Citar o Harvest mostra que a abordagem do projeto segue o que a própria NASA faz em agricultura. A equipe **cita e se inspira**; não é parceira do programa e não deve se apresentar assim.

**4. Dados de referência abertos.** Mapas de cultura e pontos rotulados servem para conferir se a ferramenta identifica bem a rotação.

## Como entra no projeto

### Harmonização

Aqui não há variáveis para baixar e reamostrar. O Harvest entra de três formas:

- **Método:** a equipe lê os artigos e o código aberto do programa e adapta a detecção de safras (picos de NDVI) ao MODIS e ao HLS do projeto.
- **Referência:** mapas de soja e de culturas publicados por parceiros, quando abertos, viram camada de comparação.
- **Contexto:** os boletins do Crop Monitor dos anos da série entram como nota no histórico do talhão.

| Recurso | O que é | Uso |
| --- | --- | --- |
| GEOGLAM Crop Monitor | Boletim mensal de condição das safras | Explicar anos ruins no histórico |
| Harvest GLAM | Monitoramento com NDVI e máscaras de cultura | Comparar a curva do talhão com a da região |
| CropHarvest | Pontos rotulados por cultura | Testar o método de classificação |
| Mapas de soja de parceiros | Área de soja por ano, a partir do Landsat | Conferir o histórico de soja do talhão |

> Confirmar nas páginas oficiais a lista atual de ferramentas, se a versão do GLAM para a Conab continua no ar, quantos pontos do Brasil existem no CropHarvest, as licenças de uso de cada mapa e quem coordena hoje a iniciativa para a América Latina.

### Indicadores calculados

O Harvest não gera indicadores diretos. Ele melhora estes:

- **Número de safras por ano:** um ou dois picos de NDVI, com o método validado em outras regiões.
- **Histórico de culturas:** soja confirmada pelo mapa de referência.
- **Ano anômalo:** safras que o Crop Monitor marcou como ruins na região.

### Nível de confiança

Os recursos do Harvest não são fontes totalmente independentes:

- Os mapas de soja usam **Landsat**, o mesmo satélite de parte do HLS. Concordância entre eles é esperada e vale menos como confirmação.
- O Crop Monitor no Brasil usa informação de **parceiros nacionais, como a Conab**. Ele não confirma a Conab; repete parte dela.

O MapBiomas e o IBGE PAM continuam sendo as referências principais de histórico de culturas no Brasil.

## Onde o produtor vê isso

**Etapa 3, conferência da rotação.** O produtor vê se a ferramenta detectou uma ou duas safras por ano. O método por trás vem da literatura do Harvest.

**Histórico do talhão.** Uma nota curta: "Este ano foi ruim para o milho segunda safra na sua região, segundo o monitoramento global de safras."

**Página "Sobre os dados".** O Harvest aparece como referência de metodologia, não como fonte de números.

## Caso hipotético: NASA Harvest junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

A equipe escolhe como demonstração a fazenda do Sr. Marcos, perto de Rio Verde, no sudoeste de Goiás, região de Cerrado. Antes, precisa saber se a ferramenta detecta bem a safrinha.

- **Rotação atual:** soja (outubro a fevereiro) e milho safrinha (fevereiro a junho).
- **Irrigação:** não tem.
- **Prioridades:** renda e água altas; solo média.
- **Mercado:** soja, milho e sorgo para a agroindústria local.

### O que cada dataset diz sobre o local

| Fonte | O que encontra (hipotético) |
| --- | --- |
| MODIS NDVI, método inspirado no Harvest | Dois picos por ano em 9 dos últimos 10 anos. Num ano, o segundo pico quase não aparece. |
| HLS | Confirma os dois picos no talhão, com datas mais precisas. |
| Mapa de soja de parceiros do Harvest | Soja no talhão em todos os anos (concordância esperada, pois também usa Landsat). |
| MapBiomas | Soja todos os anos; não separa a safrinha. |
| IBGE PAM | Área de milho segunda safra alta e estável no município. |
| GEOGLAM Crop Monitor | No ano do pico fraco, condições ruins para o milho segunda safra no Centro-Oeste por chuvas que acabaram cedo. |
| GPM IMERG / GLDAS | Naquele ano, chuva até o início de março e zona das raízes seca em abril. |
| ZARC | Janela de baixo risco para o milho safrinha até o fim de fevereiro. |

### Onde os dados se completam

**O método funciona.** A detecção de dois picos, inspirada no Harvest, bate com o HLS e com o IBGE PAM. A equipe ganha confiança para usar o mesmo método em outras regiões do Cerrado.

**O ano ruim tem explicação.** O pico fraco não foi erro da ferramenta nem falta de safrinha. O Crop Monitor mostra que a região inteira sofreu, e o IMERG e o GLDAS mostram o motivo: a chuva acabou cedo. Confiança **alta** para a explicação; o Crop Monitor entra como contexto, não como medição do talhão.

**Concordância que não conta em dobro.** Mapa de soja dos parceiros e HLS concordam, mas os dois usam Landsat. A ferramenta conta isso como uma linha de evidência, não duas.

### Regras ativadas

- **Safrinha com déficit de água em alguns anos** aumenta o peso de estratégias que protegem o milho da seca de abril.
- **Solo descoberto depois da safrinha** aumenta o peso das culturas de cobertura.
- **Prioridade alta em água** dá peso a culturas e calendários que reduzem o risco hídrico.

### Comparação das estratégias

| Critério | A: atual (soja → milho) | B: soja → milho + braquiária | C: soja precoce → milho até o fim de fevereiro, sorgo depois |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●●●○ |
| Solo | ●●○○○ | ●●●●○ | ●●●○○ |
| Nitrogênio | ●●○○○ | ●●○○○ | ●●○○○ |
| Erosão | ●●○○○ | ●●●●○ | ●●●○○ |
| Forragem | ●○○○○ | ●●●●○ | ●●○○○ |
| Renda | ●●●●○ | ●●●●○ | ●●●●○ |

Com os pesos do Sr. Marcos (renda e água altas, solo média), a **estratégia B** fica em primeiro, com a C muito perto. A C protege mais a água; a B ganha em solo, erosão e forragem.

### Cartão da estratégia B

> **Resumo:** uma opção é manter a soja e o milho safrinha e semear braquiária junto com o milho para cobrir o solo depois da colheita.
>
> **Por que foi sugerida:** a safrinha é feita quase todo ano, mas em alguns anos a chuva acaba cedo; e o solo fica descoberto de julho a setembro.
>
> **Evidências:** duas safras por ano (MODIS e HLS, com método da literatura do Harvest, confiança alta); ano ruim explicado (Crop Monitor como contexto, IMERG e GLDAS, confiança alta); janela de plantio (ZARC).
>
> **Benefícios:** palhada para o plantio direto, mais água infiltrada e forragem na seca.
>
> **Lacunas:** não sabemos a produtividade real de cada ano; com ela, a comparação de renda fica mais segura.
>
> **Riscos para revisão local:** definir com o agrônomo a época e a dose de semeadura da braquiária para não competir com o milho, e planejar a dessecação antes da soja.

## Conclusão

O NASA Harvest é o "professor" do projeto, não uma fonte de dados. Ele mostra como a NASA já usa satélites em agricultura, oferece métodos e referências abertas e dá contexto aos anos atípicos. Usado com cuidado, sem contar em dobro fontes que dividem o mesmo satélite, ele aumenta a confiança da equipe no próprio método e a credibilidade do pitch.

## Limitações

- **Não é dataset:** não substitui nenhum dos datasets obrigatórios.
- **Foco em grandes safras e em escala regional:** pouco sobre talhão e agricultura familiar.
- **Disponibilidade variável:** ferramentas e mapas mudam de endereço ou saem do ar.
- **Independência parcial:** mapas usam Landsat; boletins usam dados de parceiros nacionais.
- **Não somos parceiros:** o projeto só cita e se inspira no programa.
- **Tratamento:** usar como metodologia e contexto, citar as fontes corretamente, confirmar licenças e manter MapBiomas e IBGE PAM como referências principais no Brasil.
