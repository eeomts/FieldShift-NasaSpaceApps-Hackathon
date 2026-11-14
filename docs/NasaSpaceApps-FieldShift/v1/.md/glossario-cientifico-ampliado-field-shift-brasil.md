# Field Shift Brasil — Glossário científico ampliado

**Água, vegetação, clima, solo e observação da Terra**

Explicações aprofundadas, cálculos comentados e aplicações para uma ferramenta de apoio à decisão agrícola.

*Preparado para Guilherme Moura de Melo · Projeto NASA SPACE APP · 14 de novembro de 2026*

> ⚠️ Todos os números dos exemplos são hipotéticos. As aplicações descrevem possibilidades para o projeto, não diagnósticos de propriedades nem funcionalidades já implementadas.

---

## Sumário

1. [Como ler este guia e entender o projeto](#1-como-ler-este-guia-e-entender-o-projeto)
2. [Evapotranspiração: como a água retorna à atmosfera](#2-evapotranspiração-como-a-água-retorna-à-atmosfera)
3. [ET real, ET de referência, ET da cultura e demanda hídrica](#3-et-real-et-de-referência-et-da-cultura-e-demanda-hídrica)
4. [Umidade do solo: quantidade, profundidade e disponibilidade](#4-umidade-do-solo-quantidade-profundidade-e-disponibilidade)
5. [Anomalias de umidade: comparação com o habitual](#5-anomalias-de-umidade-comparação-com-o-habitual)
6. [Índices de vegetação e o funcionamento do NDVI](#6-índices-de-vegetação-e-o-funcionamento-do-ndvi)
7. [EVI, qualidade das imagens e calendário de cobertura](#7-evi-qualidade-das-imagens-e-calendário-de-cobertura)
8. [Risco de geada: ocorrência, exposição e dano](#8-risco-de-geada-ocorrência-exposição-e-dano)
9. [Balanço hídrico: a conta da água](#9-balanço-hídrico-a-conta-da-água)
10. [Indicadores de água: déficit, estresse e armazenamento](#10-indicadores-de-água-déficit-estresse-e-armazenamento)
11. [Precipitação, chuva efetiva e eventos extremos](#11-precipitação-chuva-efetiva-e-eventos-extremos)
12. [Temperatura, calor e microclima](#12-temperatura-calor-e-microclima)
13. [Solo, infiltração, drenagem e erosão](#13-solo-infiltração-drenagem-e-erosão)
14. [Rotação de culturas e estratégias de cobertura](#14-rotação-de-culturas-e-estratégias-de-cobertura)
15. [De onde vêm os dados e o que cada fonte pode responder](#15-de-onde-vêm-os-dados-e-o-que-cada-fonte-pode-responder)
16. [Escala espacial, tempo e harmonização](#16-escala-espacial-tempo-e-harmonização)
17. [Incerteza, qualidade e validação local](#17-incerteza-qualidade-e-validação-local)
18. [Quatro cenários didáticos para o Brasil](#18-quatro-cenários-didáticos-para-o-brasil)
19. [Exercícios numéricos comentados](#19-exercícios-numéricos-comentados)
20. [Como escrever os cartões da ferramenta](#20-como-escrever-os-cartões-da-ferramenta)
21. [Erros frequentes e como corrigi-los](#21-erros-frequentes-e-como-corrigi-los)
22. [Dicionário complementar e perguntas de revisão](#22-dicionário-complementar-e-perguntas-de-revisão)
23. [Fontes e rastreabilidade](#23-fontes-e-rastreabilidade)

---

## 1. Como ler este guia e entender o projeto

### 1.1 O problema que o glossário ajuda a resolver

O Field Shift Brasil foi pensado como uma ferramenta de apoio à decisão. O produtor informa seu contexto, a ferramenta organiza evidências ambientais e apresenta a estratégia atual junto de alternativas. Para que essa comparação seja útil, não basta mostrar mapas coloridos: é preciso explicar o que cada número representa, como foi obtido e qual pergunta ele consegue responder.

Considere uma tela que apresenta NDVI de 0,35, umidade do solo de 0,18 m³/m³ e evapotranspiração de 2 mm/dia. Sem contexto, o usuário pode interpretar todos os valores como baixos e concluir que a lavoura está perdida. Essa conclusão não se sustenta apenas com esses números. Pode ser uma área recém-colhida, uma cultura no início do desenvolvimento, um solo com características específicas ou uma observação afetada por limitações de qualidade. O glossário serve para transformar números em perguntas bem formuladas.

### 1.2 Quatro níveis de informação

Uma **observação** é o registro de um sinal ou de uma grandeza. Um **produto estimado** é o resultado de um processamento ou modelo. Um **indicador** resume uma condição, como a diferença em relação à média histórica. Uma **recomendação** acrescenta julgamento: compara opções com critérios e restrições. Esses quatro níveis se relacionam, mas não são intercambiáveis.

No projeto, a cadeia pode ser descrita assim: o sensor registra um sinal; um processamento produz uma estimativa; a equipe calcula um indicador; uma regra combina esse indicador com a cultura e as prioridades do produtor; por fim, a interface apresenta uma alternativa acompanhada de justificativa. Quanto mais transparente essa cadeia, mais fácil identificar onde existe uma lacuna.

### 1.3 O que vem do contexto e o que foi acrescentado

O recorte no Brasil inteiro (decisão D-008, que substituiu o foco inicial em Minas Gerais), a comparação de pelo menos três estratégias, o uso de regras transparentes, as prioridades do produtor e a distinção entre rotação de culturas anuais e cobertura nas entrelinhas do café vêm da documentação fornecida. As fórmulas, explicações de unidades e distinções técnicas aprofundam o glossário anterior com fontes oficiais listadas ao final.

Os cenários regionais deste guia são exercícios de raciocínio. Eles não demonstram que toda a região tem o mesmo clima, solo ou problema. Uma propriedade deve ser analisada no seu próprio contexto. Também não se considera que todos os conjuntos de dados citados já tenham sido integrados ao protótipo.

### 1.4 A pergunta principal

Antes de interpretar qualquer indicador, pergunte: **qual variável, em qual unidade, para qual lugar, em qual período, em qual profundidade e com qual qualidade?** Essa sequência evita grande parte das interpretações incorretas discutidas neste documento.

---

## 2. Evapotranspiração: como a água retorna à atmosfera

### 2.1 Definição e componentes

Evapotranspiração, abreviada como ET, é a transferência de água para a atmosfera pela combinação de evaporação e transpiração. A evaporação ocorre em superfícies como solo úmido, água livre e folhas molhadas. A transpiração envolve a passagem de água pela planta e a liberação de vapor, principalmente pelos estômatos, pequenas aberturas nas folhas. [1, 2]

O processo participa do funcionamento normal da vegetação. A água absorvida pelas raízes circula pela planta, e sua perda como vapor se relaciona às trocas gasosas e ao resfriamento. Por isso, chamar toda evapotranspiração de desperdício seria inadequado. Parte dela está associada à atividade da cultura; outra parte pode ocorrer diretamente no solo, sem representar transpiração da planta cultivada. [1, 2]

### 2.2 O que significa um valor em milímetros

Uma lâmina de 1 mm corresponde a 1 litro distribuído sobre 1 m². Em 1 hectare, que possui 10.000 m², essa mesma lâmina equivale a 10.000 litros ou 10 m³. A unidade permite comparar chuva, irrigação e evapotranspiração sobre uma mesma área. O intervalo de tempo deve acompanhar o número: 4 mm/dia não é a mesma informação que 4 mm/mês. [1]

**Exemplo hipotético:** uma área de 2 hectares apresenta ET média de 4 mm/dia durante cinco dias. O acumulado é 4 × 5 = 20 mm. Cada milímetro sobre 2 hectares corresponde a 20 m³. Assim, 20 mm correspondem a 400 m³ de água transferida à atmosfera no período. A conta converte uma lâmina em volume; ela não determina automaticamente o volume que precisa ser irrigado.

Para planejar reposição, ainda faltam informações sobre chuva aproveitável, água já armazenada, perdas do sistema de aplicação e objetivo do manejo. Se o produtor já possui reserva suficiente no solo, repor imediatamente todo o volume da ET pode ser desnecessário. Se parte da água aplicada não chega à região das raízes, a lâmina bruta e a lâmina efetivamente aproveitada serão diferentes.

### 2.3 Aplicação e interpretação no Field Shift

Uma utilização possível é comparar o comportamento da ET ao longo do ciclo de cada estratégia. A equipe pode perguntar se a fase de maior demanda coincide com um período de menor oferta de água. Também pode investigar mudanças entre anos, desde que mantenha comparáveis o produto, a área e o período.

A frase "esta cultura economiza água porque apresentou ET baixa" exige cautela. A ET observada pode ser baixa porque havia pouca vegetação, porque o ciclo estava terminando ou porque faltava água. Para sustentar uma vantagem de manejo, é preciso esclarecer o que está sendo comparado e se o resultado produtivo ou a cobertura desejada foram mantidos.

> **Texto curto sugerido:** "Água que passa do solo e da vegetação para o ar durante o período analisado."

---

## 3. ET real, ET de referência, ET da cultura e demanda hídrica

### 3.1 Por que existem nomes diferentes

ET real, ETo e ETc respondem a perguntas diferentes. A **ET real**, também chamada ETa em muitos produtos, representa o fluxo que efetivamente ocorre nas condições existentes. **ETo** representa a evapotranspiração de uma superfície de referência padronizada e bem abastecida de água. **ETc** representa a evapotranspiração de uma cultura em condições padrão. A relação **ETc = Kc × ETo** usa um coeficiente de cultura para ligar a referência climática à cultura. [1, 3]

ET potencial é um termo cujo significado depende da formulação empregada. Não deve ser automaticamente substituído por ETo. Ao integrar produtos distintos, a equipe precisa ler a definição adotada por cada um. Uma razão entre ET real e potencial também precisa usar componentes compatíveis. [1, 2]

### 3.2 Coeficiente de cultura: Kc

Kc é um coeficiente adimensional que expressa a relação entre ETc e ETo em uma determinada condição. Ele varia com o desenvolvimento da cultura e com aspectos de manejo e ambiente. Portanto, um único valor fixo para todos os meses pode esconder mudanças importantes do ciclo. [3, 4]

**Exemplo hipotético:** para ETo de 4,0 mm/dia e Kc de 0,75, a ETc é 3,0 mm/dia. Se, em outra fase, o Kc adotado for 1,10, a ETc será 4,4 mm/dia sob a mesma ETo. O cálculo mostra como a fase da cultura altera a estimativa, mesmo sem mudança no clima de referência. Os coeficientes deste exemplo não são indicados para uma espécie específica.

Agora imagine que um produto estime ET real de 2,0 mm/dia, enquanto a ETc calculada seja 4,0 mm/dia. A diferença merece investigação, mas não prova isoladamente que a falta de água é sua única causa. As áreas, datas, métodos e condições da cultura precisam ser compatíveis antes da comparação. O sistema não deve simplesmente transformar essa diferença em uma ordem de irrigação.

### 3.3 Demanda atmosférica e demanda da cultura

"Demanda atmosférica" descreve o efeito das condições meteorológicas sobre a transferência de água. "Demanda hídrica da cultura" acrescenta as características e o estágio da planta. Radiação, temperatura, umidade do ar e vento influenciam os processos de evaporação e transpiração. [3, 4]

No projeto, é útil manter campos separados: ETo para a referência climática, ETc estimada para a cultura e ET real para o fluxo estimado nas condições observadas. Se o produto disponível fornece apenas uma dessas variáveis, a interface deve mostrar exatamente essa informação.

Uma explicação clara ao produtor seria: "O ambiente favorecia maior uso de água, mas a vegetação apresentou um fluxo menor. Precisamos verificar se isso corresponde ao estágio da lavoura ou a uma limitação." Essa formulação informa a evidência sem antecipar uma causa ainda não comprovada.

---

## 4. Umidade do solo: quantidade, profundidade e disponibilidade

### 4.1 O que a medida representa

Umidade do solo é a quantidade de água contida no solo. Em conteúdo volumétrico, costuma ser expressa em m³/m³. Um valor de 0,20 m³/m³ corresponde a um volume de água equivalente a 20% do volume de solo considerado. Isso não significa que a planta tenha "20% da água de que precisa", porque quantidade presente e disponibilidade para absorção são conceitos diferentes. [5, 6]

A profundidade é parte indispensável da descrição. A superfície pode secar após alguns dias sem chuva enquanto camadas mais profundas ainda conservam água. O SMAP observa a umidade superficial; o SMAP L4, usado no projeto, estima também a zona das raízes combinando essas observações com modelos. É necessário identificar o produto e a camada, e não atribuir a todos os dados SMAP a mesma profundidade. [5, 6]

### 4.2 Um exemplo de conversão em armazenamento

Considere, apenas para exercício, uma camada uniforme de 0,40 m de espessura e umidade volumétrica de 0,25 m³/m³. A lâmina total de água nessa camada é 0,25 × 0,40 × 1.000 = 100 mm. Se a umidade cair para 0,20 m³/m³, o armazenamento passa a 80 mm. A diferença é de 20 mm.

Essa conta supõe que o valor representa toda a camada de forma uniforme. Aplicá-la a uma medida superficial e atribuir o resultado a um metro de profundidade seria um erro. Também seria incorreto afirmar que os 100 mm iniciais estão integralmente disponíveis à cultura. Parte da água pode estar retida de maneira que as raízes não consigam extraí-la nas condições consideradas.

### 4.3 Como isso muda a análise

Imagine dois talhões com a mesma umidade de 0,20 m³/m³. Um deles pode ter solo, estrutura e profundidade explorável diferentes do outro. A mesma quantidade relativa de água não implica a mesma reserva útil, nem o mesmo risco para plantas com sistemas radiculares distintos. Por isso, uma classificação universal de "solo seco" baseada apenas em um corte numérico pode ser inadequada.

No Field Shift, o produtor pode informar resultados de análise e características do solo. Quando essa informação não estiver disponível, a ferramenta deve manter a limitação explícita. É mais correto comunicar "umidade superficial baixa em relação ao histórico desta área" do que afirmar "a raiz está sem água" quando a camada radicular não foi avaliada.

> **Texto curto sugerido:** "Quantidade de água presente na camada de solo analisada. A profundidade e o tipo de solo influenciam sua interpretação."

---

## 5. Anomalias de umidade: comparação com o habitual

### 5.1 O significado de anomalia

Anomalia é uma diferença em relação a uma referência. Para umidade do solo, a comparação deve considerar o mesmo local e uma época equivalente. Uma anomalia negativa indica umidade abaixo da referência; uma positiva indica umidade acima dela. Uma anomalia próxima de zero indica proximidade do comportamento de referência, não ausência de problemas agrícolas. [7]

Na forma simples: **anomalia = valor observado − valor médio de referência**. Outras apresentações usam porcentagens, percentis ou padronização pelo desvio-padrão. Esses formatos não devem compartilhar uma legenda sem identificação. Um valor de −0,05 m³/m³ e um valor padronizado de −1,0 descrevem grandezas diferentes. [7, 8]

### 5.2 Exemplo com unidade física

Suponha que a média de umidade de determinado mês, para uma área e camada específicas, seja 0,25 m³/m³. No mês analisado, o valor foi 0,20 m³/m³. A anomalia simples é −0,05 m³/m³. Em conteúdo volumétrico, isso representa cinco pontos percentuais: de 25% para 20%.

Se a equipe escolher uma diferença relativa, a conta será (0,20 − 0,25) ÷ 0,25 × 100 = −20%. Esse resultado quer dizer que o valor é 20% menor que a referência. Ele não significa uma queda de vinte pontos percentuais. A interface deve distinguir "diferença relativa de 20%" de "diferença de cinco pontos percentuais".

### 5.3 Exemplo com padronização

Se a média hipotética for 0,25 e o desvio-padrão for 0,05, o valor de 0,20 produz z = (0,20 − 0,25) ÷ 0,05 = −1. O resultado está um desvio-padrão abaixo da média. Isso não autoriza tratar automaticamente o valor como uma probabilidade exata: a distribuição dos dados e o método precisam ser considerados.

O cálculo também exige uma referência consistente. Se um mapa usa dez anos e outro usa trinta, parte da diferença entre resultados pode vir da escolha da base. Quando o desvio-padrão é muito pequeno ou zero, a padronização requer tratamento específico. A aplicação não deve exibir números extremos ou indefinidos como se fossem observações válidas.

### 5.4 Interpretação agrícola

Uma anomalia positiva durante um período normalmente muito seco pode indicar apenas uma condição menos seca. Uma anomalia negativa durante um período normalmente muito úmido pode ocorrer sem que a cultura esteja imediatamente sob deficiência de água. O indicador responde "está diferente do habitual?", e não, sozinho, "há água suficiente para esta cultura?".

No projeto, apresente o período de referência junto do indicador. Exemplo de texto: "Mais seco que o habitual para este mês, considerando a série disponível. A condição na zona das raízes ainda precisa ser confirmada."

---

## 6. Índices de vegetação e o funcionamento do NDVI

### 6.1 O que os índices observam

Índices de vegetação combinam informações de diferentes faixas da luz refletida pela superfície. Eles ajudam a acompanhar a presença e a variação da vegetação. O NDVI, Índice de Vegetação por Diferença Normalizada, compara o infravermelho próximo com a faixa do vermelho. A vegetação verde apresenta um comportamento espectral que torna essa combinação útil para monitoramento. [9]

A fórmula é **NDVI = (NIR − RED) ÷ (NIR + RED)**. NIR representa a reflectância no infravermelho próximo; RED representa a reflectância no vermelho. O resultado é adimensional. Nas condições usuais de aplicação, varia de −1 a 1, embora dados inadequados ou processamentos incorretos possam produzir valores que precisem ser rejeitados. [9, 10]

### 6.2 Exemplo explicado passo a passo

Considere NIR = 0,50 e RED = 0,10. O numerador é 0,40 e o denominador é 0,60. Portanto, NDVI = 0,40 ÷ 0,60 = aproximadamente 0,67. Em outra observação, NIR = 0,30 e RED = 0,20 resultam em 0,10 ÷ 0,50 = 0,20.

O primeiro valor expressa um contraste espectral maior que o segundo. Isso pode ser compatível com vegetação verde mais expressiva, mas o cálculo não informa sozinho a espécie, a produtividade ou a causa de uma mudança. O número precisa ser interpretado junto da data, do manejo e da qualidade da imagem.

Uma série hipotética de 0,25, 0,45, 0,68, 0,72 e 0,30 pode sugerir estabelecimento, crescimento e posterior redução da vegetação. Se a última data coincide com a colheita, a queda pode ser esperada. Se a queda ocorre durante uma fase em que o campo deveria continuar verde, ela merece investigação. O mesmo valor final pode ter explicações distintas.

### 6.3 Por que não criar faixas universais de saúde

É tentador classificar qualquer NDVI abaixo de 0,30 como "ruim" e acima de 0,60 como "bom". Para o Field Shift, isso pode gerar conclusões enganosas. Uma plantação recém-emergida e uma plantação adulta não devem ser julgadas da mesma forma. Áreas com linhas espaçadas e áreas com dossel fechado também produzem sinais diferentes.

Uma regra de produto mais defensável é comparar a área consigo mesma em períodos equivalentes e considerar a cultura informada. Mesmo assim, mudanças de manejo, de sensor ou de qualidade precisam ser verificadas. O índice funciona como evidência de uma condição da cobertura verde; a explicação agronômica requer contexto adicional.

> **Texto curto sugerido:** "Indicador de presença e vigor da vegetação verde. Deve ser interpretado conforme a cultura e a época do ano."

---

## 7. EVI, qualidade das imagens e calendário de cobertura

### 7.1 EVI e NDVI não são números intercambiáveis

EVI significa Índice de Vegetação Melhorado. Sua formulação busca reduzir interferências do fundo do solo e da atmosfera e melhorar a sensibilidade em vegetação densa, em que o NDVI pode perder capacidade de distinguir variações. O EVI tradicional utiliza também a banda azul. Há variantes, e a fórmula precisa acompanhar o produto utilizado. [11, 12]

No protótipo, não é adequado misturar NDVI e EVI em uma mesma série como se fossem a mesma variável. Também não convém apresentar a diferença entre eles como uma mudança real da lavoura. Uma troca de indicador exige uma transição documentada, com legenda clara e avaliação da comparabilidade.

### 7.2 Nuvens, sombras e pixels mistos

Uma observação só deve entrar na análise se cumprir os critérios de qualidade do produto. Nuvens e sombras podem alterar o sinal. Um pixel pode combinar lavoura, estrada, árvore e solo exposto. Assim, um valor associado ao polígono da propriedade pode não representar exclusivamente a cultura de interesse.

Considere um talhão pequeno cortado por uma estrada. Se poucos pixels o representam, incluir ou excluir apenas um pixel de borda pode mudar sua média. Antes de interpretar a mudança como resposta da cultura, a equipe deveria conferir se a área válida e os pixels utilizados permaneceram comparáveis. Essa é uma verificação metodológica proposta para o projeto.

### 7.3 Vegetação verde não equivale a toda cobertura do solo

Palhada e resíduos vegetais podem proteger o solo sem apresentar o mesmo sinal de vegetação verde. A FAO distingue cobertura com resíduos e cobertura com plantas vivas. [13] Portanto, NDVI baixo não demonstra, por si só, que a terra esteja completamente desprotegida.

Para o calendário do Field Shift, é mais seguro usar a categoria "baixa cobertura verde detectada" quando o NDVI é a única evidência. A classificação "solo descoberto" pode exigir análise adicional das imagens e confirmação do produtor. Essa diferença de linguagem evita que o sistema recomende cobertura para uma área que já possui palhada suficiente.

### 7.4 Exemplo de calendário interpretável

Imagine janeiro e fevereiro com NDVI alto, março com queda, abril com NDVI baixo e maio com recuperação. O aplicativo poderia perguntar ao produtor se houve colheita em março e estabelecimento de outra cultura em maio. Se a resposta for positiva, a série ajuda a organizar o histórico; se for negativa, a equipe investiga outras hipóteses.

O calendário é uma reconstrução apoiada por evidências. Ele não substitui automaticamente o registro de plantio e colheita. Para culturas perenes, o sinal pode misturar a cultura principal com o manejo das entrelinhas, exigindo ainda mais atenção à escala.

---

## 8. Risco de geada: ocorrência, exposição e dano

### 8.1 O fenômeno e a vulnerabilidade

Geada está associada à formação de gelo e, no uso agrícola, a eventos de frio que podem causar congelamento e lesões. A presença de gelo visível não é uma medida completa dos danos. A sensibilidade depende da espécie, variedade, estágio de desenvolvimento e condições anteriores à exposição. Danos por frio acima do congelamento constituem um fenômeno distinto. [14, 15]

Há situações predominantemente **radiativas**, relacionadas à perda de calor em noites claras e pouco ventosas, e situações **advectivas**, associadas à entrada de ar frio. O relevo e a movimentação local do ar também influenciam a distribuição do frio. [14]

### 8.2 Temperatura do ar não é temperatura da planta

Uma temperatura medida em abrigo meteorológico descreve condições diferentes da temperatura de uma folha ou da superfície do solo. Em certas noites, uma superfície vegetal pode estar mais fria que o ar registrado na altura do sensor. Por isso, um único limite baseado em temperatura de uma grade regional não representa automaticamente o congelamento do tecido vegetal. [14, 15]

No projeto, uma formulação prudente é "condições históricas favoráveis a episódios de frio potencialmente prejudiciais". Para transformá-la em um indicador de risco por cultura, são necessários critérios explícitos e validação compatível com o uso pretendido.

### 8.3 Exemplo de frequência histórica

Suponha que a equipe escolha um limiar apenas para triagem e encontre 12 dias abaixo desse limiar em 600 dias válidos de uma determinada estação do ano. A frequência observada é 12 ÷ 600 = 2%. Isso não significa "2% de chance de a cultura morrer", nem "2% de probabilidade de geada amanhã". O cálculo descreve a ocorrência histórica do critério meteorológico escolhido.

Agora imagine que esses 12 dias se concentrem em apenas três anos. A informação sobre agrupamento muda a interpretação. Outro local com 12 dias distribuídos por muitos anos pode ter a mesma frequência, mas outra estrutura temporal. Um painel útil pode mostrar tanto o total de dias quanto os anos em que ocorreram eventos.

### 8.4 Cuidados com a agregação mensal

Uma média mensal pode esconder uma única madrugada extrema. Para produzir um resumo mensal, a equipe deve primeiro preservar informações diárias ou horárias adequadas, como mínimo observado, duração abaixo do critério e contagem de episódios. A média pode entrar como contexto, mas não deve ser o único dado usado para avaliar extremos.

> **Texto curto sugerido:** "Possibilidade de condições de frio capazes de prejudicar a cultura. O risco depende da planta, da fase de desenvolvimento e do local."

---

## 9. Balanço hídrico: a conta da água

### 9.1 Definição e limite da análise

Balanço hídrico é a contabilização de entradas, saídas e variação do armazenamento de água. É preciso definir qual sistema está sendo analisado: uma camada de solo, a zona das raízes, uma propriedade ou uma bacia. Também é necessário definir o período. Sem esses limites, não fica claro quais movimentos de água entram na conta. [16]

Para um exercício na zona das raízes, podemos escrever:

**ΔS = P + I + C − ET − R − D**

- **ΔS** é a variação do armazenamento;
- **P**, precipitação;
- **I**, irrigação;
- **C**, contribuição por ascensão capilar;
- **ET**, evapotranspiração real;
- **R**, escoamento superficial;
- **D**, drenagem para abaixo da zona considerada.

Fluxos laterais e outros componentes devem ser incluídos quando relevantes. [16, 17]

### 9.2 Exemplo completo e hipotético

Considere armazenamento inicial de 60 mm. Durante o período, choveu 30 mm, foram aplicados 10 mm de irrigação e a contribuição capilar foi considerada nula. A ET foi 25 mm, o escoamento 8 mm e a drenagem 7 mm. A variação é 30 + 10 − 25 − 8 − 7 = 0 mm. O armazenamento final permanece em 60 mm.

Se alguém calculasse apenas chuva menos ET, encontraria 30 − 25 = 5 mm. Esse resultado não corresponde à variação final porque ignora os demais componentes. O exemplo demonstra por que "choveu mais que evapotranspirou" não basta para descrever o que aconteceu com a reserva do solo.

Em um segundo período, mantendo o armazenamento inicial em 60 mm, suponha P = 10, I = 0, C = 0, ET = 30, R = 0 e D = 0. A variação seria −20 mm, e o armazenamento final, 40 mm. A redução indica uso da reserva. Ela ainda não informa, sozinha, se a cultura ultrapassou um limite crítico de disponibilidade.

### 9.3 Consistência física

Um cálculo que produz armazenamento negativo deve ser revisado. Em um modelo físico, a retirada efetiva de água é limitada pela disponibilidade e por outros processos. Não é correto manter indefinidamente uma ET de demanda quando o solo já não consegue fornecê-la. Da mesma forma, exceder a capacidade de armazenamento exige representar drenagem, escoamento ou outras saídas.

Na implementação, essas verificações ajudam a detectar erros de unidade, sinal e integração temporal. Um número matematicamente calculável não é automaticamente fisicamente plausível.

### 9.4 Aplicação no projeto

O balanço pode apoiar a comparação de calendários: uma estratégia concentra maior demanda justamente quando a reserva tende a cair? Outra mantém cobertura, mas consome água em um intervalo importante para a próxima cultura? As respostas dependem do conjunto de componentes, e não apenas do nome da espécie.

> **Texto curto sugerido:** "Conta da água que entra, sai e fica armazenada na área durante o período analisado."

---

## 10. Indicadores de água: déficit, estresse e armazenamento

### 10.1 Déficit hídrico

Déficit hídrico expressa uma insuficiência de água em relação a uma necessidade definida. A definição operacional deve acompanhar o indicador: pode estar ligada à demanda da cultura, ao balanço do solo ou a uma comparação climática. Não se deve usar a palavra com métodos diferentes sem explicar a diferença. [17, 18]

No Field Shift, uma sugestão é apresentar "necessidade hídrica estimada não atendida", quando a equipe realmente dispõe dos componentes necessários para essa estimativa. Caso haja somente chuva e ETo, o resultado deve ser identificado como uma aproximação climática, não como diagnóstico completo da condição radicular.

### 10.2 Estresse hídrico

Estresse hídrico é a resposta da planta à limitação de água. A restrição pode alterar a transpiração e o desenvolvimento. Indicadores térmicos e de evapotranspiração ajudam a investigar a condição. [2]

Exemplo interpretativo: a chuva ficou abaixo da referência, mas o solo ainda tinha reserva suficiente e a cultura permaneceu em desenvolvimento normal. Há um sinal climático desfavorável, mas não necessariamente estresse já instalado. Em outro caso, a chuva mensal pode parecer adequada e, ainda assim, um intervalo longo sem chuva coincidir com uma fase sensível da cultura.

### 10.3 Déficit, anomalia e estresse não são sinônimos

A **anomalia** compara com o habitual. O **déficit** compara oferta e necessidade. O **estresse** descreve uma resposta da planta. Essa separação é especialmente útil na interface: evita apresentar três cartões como se fossem medições independentes da mesma coisa.

Uma narrativa possível é: "A umidade ficou abaixo da referência histórica; o balanço estimado sugere redução da reserva; a resposta da vegetação ainda não confirma estresse." Outra é: "A umidade regional está próxima da referência, mas existem sinais localizados que precisam de verificação." Ambas preservam a diferença entre evidência e interpretação.

### 10.4 Água armazenada em escala regional

O armazenamento de água em grandes áreas inclui a água do solo, a subterrânea e a superficial. Modelos de superfície terrestre, como o GLDAS, estimam parte desses componentes; a separação de outros, como a água subterrânea, exige informações adicionais. Esses produtos não medem diretamente o nível de um poço específico.

No projeto, esse uso é de contexto regional e de longo prazo. Uma tendência de redução regional pode justificar atenção à dependência de irrigação, mas não determina a vazão disponível em uma propriedade. Essa distinção precisa aparecer no mapa e na explicação do indicador.

---

## 11. Precipitação, chuva efetiva e eventos extremos

### 11.1 Acumulado e intensidade

Precipitação acumulada é a quantidade que caiu durante um intervalo. Intensidade é uma taxa, como mm/h. Para converter uma taxa em acumulado, é preciso considerar sua duração. Uma taxa constante de 12 mm/h durante meia hora representa 6 mm, e não 12 mm. Produtos como IMERG fornecem estimativas de precipitação a partir da combinação de informações de satélites e de outros componentes do processamento. [19, 20]

No protótipo, a variável deve ser verificada antes de somar valores. Somar taxas sem multiplicar pelos intervalos correspondentes produz um acumulado incorreto. Outro erro é considerar um dado ausente como zero: "não foi possível observar" e "não choveu" são situações diferentes.

### 11.2 A distribuição da chuva importa

Considere dois meses com 100 mm de chuva. No primeiro, todo o volume se concentrou em um único dia; no segundo, houve eventos menores distribuídos ao longo do período. O total mensal é igual, mas a disponibilidade de água entre eventos pode ser diferente. Não é possível concluir qual situação foi melhor para a cultura sem considerar solo, demanda, intensidade e estágio de desenvolvimento.

Essa comparação é um exemplo didático, não uma regra de que chuva distribuída sempre resolve o problema. A aplicação deve preservar informações como número de dias com chuva e duração dos intervalos secos, quando a resolução temporal permitir.

### 11.3 Precipitação efetiva

É a parcela da precipitação aproveitável para atender à cultura, conforme o método e o sistema considerados. Nem toda a água que cai permanece disponível na zona das raízes: parte pode escoar, evaporar ou drenar para abaixo dela. [18]

Uma sugestão para a interface é mostrar "chuva total" e "chuva aproveitável estimada" como campos separados. Se a segunda não foi calculada, não se deve renomear a primeira como água disponível. A diferença é especialmente importante em comparações de solos e manejos.

### 11.4 Eventos extremos e vulnerabilidade

Um critério de chuva extrema precisa informar a duração e a referência. Um acumulado diário alto e uma intensidade de poucos minutos são informações distintas. Para o Field Shift, é possível resumir a ocorrência histórica de eventos fortes, mas atribuir dano ou erosão exige considerar cobertura, relevo e características do solo.

> **Texto curto sugerido:** "Quantidade de chuva no período. A distribuição no tempo influencia quanto dessa água pode ser aproveitado pela cultura."

---

## 12. Temperatura, calor e microclima

### 12.1 Temperatura do ar e temperatura da superfície

Temperatura do ar descreve o estado térmico do ar na condição e altura de medição. Temperatura da superfície, frequentemente abreviada como LST, refere-se à superfície observada pelo sensor. Ela pode refletir folhas, solo, palhada ou uma mistura desses elementos.

**Exemplo hipotético:** um mapa apresenta 39 °C na superfície, enquanto uma referência meteorológica indica 30 °C no ar. Isso não comprova que uma das fontes esteja errada. Elas podem representar alvos, horários e escalas diferentes. A primeira pergunta deve ser "o que cada produto mede ou estima?" antes de comparar os valores.

### 12.2 Estresse térmico

É a condição em que temperaturas desfavoráveis prejudicam processos da planta. No caso de calor, o efeito depende da cultura, da fase e da duração da exposição. Para o projeto, é importante não transformar qualquer temperatura elevada em diagnóstico de dano. A definição do limiar deve ter justificativa agronômica e indicar a variável usada.

Uma média de 28 °C pode resultar de dias moderados ou da combinação de períodos muito quentes e muito frios. Assim como no risco de geada, médias são úteis para contexto, mas podem ocultar extremos. Um resumo interpretável pode separar temperatura média, máxima e número de dias acima de um critério documentado.

### 12.3 Microclima

Microclima é o conjunto de condições ambientais em uma escala local. No contexto da ferramenta, significa reconhecer que duas partes de uma propriedade podem apresentar condições diferentes das descritas por uma célula regional. Sombra, posição no relevo, cobertura e circulação do ar são exemplos de aspectos que podem motivar uma investigação local.

A aplicação não precisa prometer um mapa de microclima se os dados não o sustentam. Pode indicar "contexto regional" e acrescentar uma pergunta ao produtor sobre áreas mais frias, mais expostas ou com histórico de problemas. O conhecimento de campo passa a complementar o dado, em vez de ser ignorado por uma classificação automática.

> **Texto curto sugerido:** "Condições de temperatura e ambiente que variam dentro da paisagem e podem afetar cada parte da lavoura de forma diferente."

---

## 13. Solo, infiltração, drenagem e erosão

### 13.1 Termos que explicam o caminho da água

**Infiltração** é a entrada de água no solo pela superfície. **Drenagem** descreve a movimentação e saída da água, podendo incluir a passagem para camadas abaixo da zona das raízes. **Escoamento superficial** é a água que se desloca sobre o terreno. Esses processos participam do balanço e ajudam a explicar por que duas áreas não aproveitam a chuva da mesma forma. [16, 18]

Um exemplo de erro seria interpretar infiltração como sinônimo de armazenamento útil. A água pode entrar no solo e continuar descendo, ultrapassando a camada explorada pela cultura. Outro erro seria classificar toda drenagem como ruim: sua interpretação depende do objetivo e das condições do sistema.

### 13.2 Capacidade de campo e água disponível

**Capacidade de campo** corresponde, de forma operacional, à água retida depois que a drenagem gravitacional diminui de maneira importante. O **ponto de murcha permanente** é uma referência para a condição em que a planta não consegue recuperar a turgescência nas condições padronizadas consideradas. A diferença entre essas referências, juntamente com a profundidade explorada, ajuda a estimar a água disponível. [17]

**Exemplo hipotético:** se a capacidade de campo for 0,30 m³/m³, o ponto de murcha 0,15 m³/m³ e a profundidade considerada 0,60 m, a reserva total disponível estimada será (0,30 − 0,15) × 0,60 × 1.000 = 90 mm. Isso não significa que seja adequado consumir toda a reserva antes de ocorrer estresse. O manejo exige critérios adicionais.

### 13.3 Cobertura, matéria orgânica e estrutura

A cobertura com resíduos ou plantas integra práticas de conservação. Ela pode proteger a superfície e alterar as condições de infiltração e evaporação. A escolha da cobertura deve considerar a cultura seguinte e a disponibilidade de recursos, em vez de supor um benefício idêntico em qualquer situação. [13, 21]

Para o Field Shift, "melhoria do solo" precisa ser desdobrada em critérios observáveis ou hipóteses explícitas. Uma nota genérica de solo pode esconder objetivos diferentes: cobertura durante chuvas fortes, produção de resíduos, diversificação de raízes ou contribuição de nutrientes. Não é possível afirmar que a matéria orgânica aumentou apenas porque o NDVI ficou maior em um mês.

### 13.4 Erosão e declividade

Erosão envolve desprendimento e transporte de material. A declividade é a inclinação do terreno; pode compor uma análise de vulnerabilidade, mas não determina sozinha a perda de solo. No projeto, a combinação "declividade elevada + cobertura insuficiente + chuvas intensas" pode orientar uma prioridade de avaliação, sem apresentar uma taxa de erosão não calculada.

A mensagem adequada seria: "Esta área reúne fatores que justificam atenção à proteção do solo." Uma mensagem inadequada seria: "Esta área perdeu dez toneladas de solo", quando não existe modelo ou medição para sustentar esse número.

---

## 14. Rotação de culturas e estratégias de cobertura

### 14.1 Rotação e comparação de estratégias

Rotação de culturas é uma sequência planejada de espécies ou grupos de culturas ao longo do tempo em uma área. No contexto da agricultura de conservação, a diversificação se combina com proteção do solo e manejo adequado. Seus resultados dependem da sequência escolhida e das condições locais. [21, 22]

Para o Field Shift, a unidade de comparação deve ser uma **estratégia completa**. Não basta comparar "milho" com "leguminosa" sem explicitar época, duração, cobertura e relação com a cultura seguinte. Uma estratégia pode ter excelente desempenho em um critério e ser inadequada por falta de mercado ou incompatibilidade com o calendário do produtor.

### 14.2 Culturas de cobertura e palhada

Culturas de cobertura são estabelecidas para funções como proteção do solo, produção de biomassa e manejo de nutrientes. Depois do manejo, parte de seus resíduos pode permanecer como palhada. Plantas vivas utilizam água; resíduos mortos não transpiram. Por isso, manter uma cobertura viva e manter palhada não são decisões equivalentes em um período de restrição hídrica. [13, 23]

No projeto, uma proposta de cobertura deve informar o objetivo e o que falta validar: data de implantação, momento de manejo, compatibilidade com a cultura principal e efeito esperado sobre a água. A palavra "cobertura" sozinha não explica essas escolhas.

### 14.3 Leguminosas e fixação de nitrogênio

Muitas leguminosas podem estabelecer associação com bactérias capazes de fixar nitrogênio atmosférico. O benefício depende de condições biológicas e de manejo. A presença de uma leguminosa não garante uma quantidade fixa de nitrogênio para a cultura seguinte. [24]

O aplicativo pode apresentar "potencial de contribuição de nitrogênio", desde que a regra esteja documentada. Não deve afirmar uma economia exata de fertilizante sem os dados e cálculos correspondentes. Parte do nutriente pode ser removida com a colheita, e a disponibilidade depende do destino e da decomposição dos resíduos.

### 14.4 Raízes profundas e tolerância à seca

Essas características são critérios de interesse na proposta do projeto. Entretanto, profundidade efetiva de raízes e desempenho sob falta de água dependem do ambiente. Uma restrição física no solo pode limitar a exploração, e tolerância à seca não significa independência de água.

Para café e outras culturas perenes, a documentação propõe tratar cobertura nas entrelinhas e manejo do solo separadamente da troca da cultura principal. A comparação deve respeitar essa diferença. Não faz sentido apresentar uma recomendação de substituição anual do café como se fosse uma rotação de grãos.

---

## 15. De onde vêm os dados e o que cada fonte pode responder

### 15.1 Funções diferentes dentro da análise

A documentação do Field Shift reúne missões, sensores, produtos, sistemas de modelagem e bases agroclimáticas. Eles não constituem uma lista de medições equivalentes. O papel de cada fonte deve ser definido antes da combinação. A tabela abaixo resume usos propostos no projeto; não confirma que todas as integrações estejam prontas.

| Fonte ou grupo | Pergunta que pode apoiar | Limitação a comunicar |
|---|---|---|
| NASA POWER | Como variam as condições meteorológicas de referência? | Dado em grade não é estação instalada na propriedade. |
| GPM / IMERG | Como a chuva se distribui no espaço e no tempo? | Estimativa de precipitação exige avaliação de qualidade e versão. |
| SMAP L4 | Como varia a umidade na superfície e na zona das raízes? | A zona das raízes é estimada com modelo, em escala regional. |
| HLS | Como muda a cobertura e a vegetação observável? | Nuvens, mistura de alvos e escala do talhão interferem. |
| MODIS / VIIRS | Como evoluem padrões de vegetação em séries e áreas maiores? | Um pixel pode incluir diferentes usos da terra. |
| SRTM | Como é o relevo e a inclinação do terreno? | Relevo sozinho não mede erosão nem geada. |
| GLDAS / ERA5 | Como reconstruir condições ambientais em séries contínuas? | Resultados incluem modelagem e assimilação de observações. |
| FAO GAEZ | Qual a aptidão sob condições e hipóteses definidas? | Aptidão e rendimento potencial não garantem resultado real. |

### 15.2 Reanálise

Reanálise combina observações e modelos para reconstruir condições ambientais de maneira consistente. ERA5 é um exemplo. O NASA POWER também utiliza fontes de modelagem e assimilação para seus parâmetros meteorológicos. Isso significa que "veio da NASA" não implica que cada número seja uma leitura direta de satélite sobre a fazenda. [25, 26]

### 15.3 Aptidão não é promessa de produtividade

GAEZ oferece informações de aptidão e potencial produtivo sob hipóteses de clima, solo e manejo. [27] No Field Shift, essas informações podem filtrar alternativas para investigação. Elas não devem ser convertidas automaticamente em previsão de lucro ou produtividade da propriedade. O contexto do projeto já reconhece a necessidade de informações sobre mercado, histórico e restrições locais.

Antes de implementar, registre o identificador do produto, versão, unidade, cobertura temporal e geográfica. Este guia não fixa uma resolução única para cada missão porque produtos diferentes podem ter características diferentes.

---

## 16. Escala espacial, tempo e harmonização

### 16.1 Resolução espacial

Resolução espacial descreve o nível de detalhe associado ao dado. O espaçamento de uma grade e a resolução efetiva da informação nem sempre são idênticos. Para o usuário, a pergunta prática é: que tamanho de área contribui para este número, e essa área corresponde ao talhão que ele pretende analisar?

Como proposta metodológica, o Field Shift deve guardar a resolução de origem e a escala de interpretação junto de cada indicador. Um valor regional pode aparecer em um painel da propriedade, desde que esteja identificado como contexto regional. A localização do clique no mapa não transforma automaticamente o dado em uma medição local.

### 16.2 Reamostragem não cria observações

Imagine uma célula hipotética de 9 km de lado com um único valor de umidade. Reapresentá-la em células de 30 m produz 300 × 300 = 90.000 células menores. Isso não gera 90.000 medições independentes. O valor original continua representando informação de escala muito mais ampla.

A reamostragem é útil para compatibilizar grades, mas a equipe deve evitar que a aparência detalhada do mapa sugira uma precisão inexistente. Uma proposta de interface é apresentar o contorno da grade de origem ou uma nota visível sobre a escala do indicador.

### 16.3 Agregação temporal

Uma média, uma soma, um máximo e um mínimo respondem a perguntas diferentes. Chuva acumulada geralmente exige integração ou soma adequada ao produto. Temperatura média descreve uma condição típica do período. Para geada, mínimos e duração de episódios são mais informativos do que apenas a média. Para vegetação, uma composição temporal precisa explicitar como os pixels válidos foram selecionados.

O projeto prevê passos mensais de comparação. Isso pode ser útil para o calendário, desde que os indicadores mensais preservem características relevantes dos dados originais. "Número de dias abaixo do critério no mês" é diferente de "temperatura média do mês".

### 16.4 Comparabilidade entre fontes

Antes de comparar duas séries, confira unidade, área, período, profundidade, horário e tratamento de dados ausentes. Depois, verifique se as duas representam a mesma grandeza. Temperatura superficial e temperatura do ar não se tornam equivalentes por estarem ambas em graus Celsius.

Uma harmonização correta torna os dados utilizáveis em conjunto sem apagar suas diferenças. O objetivo não é fabricar uniformidade, mas documentar o que foi transformado e quais limites permaneceram.

---

## 17. Incerteza, qualidade e validação local

### 17.1 O que significa incerteza

Incerteza descreve a limitação do conhecimento sobre um valor ou interpretação. Ela pode decorrer de erros de medição, hipóteses de modelo, resolução, ausência de observações ou incompatibilidade entre o dado e a pergunta. Um número exibido com muitas casas decimais não necessariamente possui alta precisão.

No Field Shift, "confiança alta, média ou baixa" deve ser uma classificação com critérios públicos. A documentação sugere avaliar resolução, extensão da série e concordância entre fontes. Essas dimensões podem compor uma classificação operacional, mas não equivalem automaticamente a um intervalo estatístico ou a uma probabilidade calibrada.

### 17.2 Exemplo de comunicação responsável

Considere uma propriedade pequena com imagens ópticas recentes e boa área válida, mas sem informações sobre solo. A interpretação de cobertura pode ter suporte melhor que a estimativa de água disponível. Em vez de uma confiança única para toda a recomendação, a ferramenta pode mostrar confiança por indicador e destacar o elo mais fraco da justificativa.

Outra situação: dois produtos de chuva concordam. Isso é útil, mas a concordância não prova independência, pois eles podem compartilhar observações ou componentes de processamento. A equipe deve evitar contar duas fontes semelhantes como duas confirmações totalmente independentes.

### 17.3 Ausência de dado não é condição normal

Um mês sem imagens válidas deve aparecer como "sem dados suficientes". Substituir o vazio por zero faria parecer que a vegetação desapareceu. Substituí-lo pela média sem aviso esconderia uma estimativa. Se houver preenchimento de lacuna, a interface deve diferenciar observação disponível de valor interpolado ou modelado.

Exemplo de cartão: "Cobertura verde: avaliação indisponível neste mês por baixa quantidade de observações válidas." Esse texto é mais útil que uma classificação verde de "normal" atribuída por falta de evidência.

### 17.4 Validação em campo

Validação é comparar resultados com informações adequadas à variável e à escala. Para o projeto, registros de plantio e colheita ajudam a interpretar vegetação; medições locais de chuva ajudam a avaliar precipitação; análise e observações do solo ajudam a interpretar disponibilidade de água. Uma foto de folhas verdes não valida automaticamente um balanço hídrico.

A recomendação final deve indicar o que precisa ser confirmado. "Verificar profundidade efetiva das raízes" é mais acionável que "consulte um especialista" sem explicar a dúvida. O papel da ferramenta é organizar a decisão e tornar suas limitações identificáveis.

---

## 18. Quatro cenários didáticos para o Brasil

### 18.1 Grãos e intervalo entre safras

Imagine uma área de grãos com queda de NDVI depois da colheita e recuperação apenas meses depois. A primeira hipótese de trabalho é um intervalo de baixa cobertura verde. Antes de classificá-lo como solo descoberto, pergunte se existe palhada. Em seguida, verifique quando ocorrem as chuvas mais intensas e como o relevo se relaciona com a área.

A comparação poderia incluir a estratégia atual, uma alternativa com cobertura em parte do intervalo e uma alternativa com outro calendário. A equipe avaliaria benefícios esperados de proteção do solo junto do uso adicional de água e das exigências de manejo. Nenhuma alternativa deve receber vantagem automática apenas por manter NDVI mais alto.

### 18.2 Área com restrição de água

Imagine uma propriedade em que o produtor relata dificuldade para manter uma segunda cultura. Uma anomalia negativa de umidade reforça a investigação, mas o histórico precisa ser separado da situação do ano atual. Se o período normalmente já apresenta pouca água, uma condição "normal" pode continuar sendo limitante.

As estratégias poderiam variar a duração do ciclo, o calendário ou a intensidade de uso de cobertura viva. O sistema deve perguntar sobre irrigação disponível e restrições operacionais. Uma alternativa tolerante à seca pode ser candidata, mas o rótulo de tolerância não elimina a necessidade de avaliar a oferta de água.

### 18.3 Café com manejo das entrelinhas

Imagine um cafezal com vegetação entre linhas e diferentes condições de exposição no terreno. A ferramenta deve comparar manejos da cobertura, preservando a distinção em relação à rotação de culturas anuais. O sinal de um pixel pode misturar cafeeiros, entrelinhas e sombras; por isso, mudanças do índice precisam ser interpretadas com o produtor.

A avaliação pode considerar proteção do solo e possível competição por água, além das condições históricas de frio. A decisão sobre manejo requer conhecimento local do sistema. A ferramenta não deve concluir que qualquer vegetação adicional é sempre benéfica ou sempre prejudicial.

### 18.4 Área inclinada e chuva concentrada

Imagine uma área com maior declividade, episódios de chuva intensa e baixa cobertura verde detectada. Esses sinais justificam investigar a proteção do solo. Mas, antes de atribuir uma classe de erosão, é preciso verificar resíduos, características do solo, práticas existentes e escala dos dados.

Uma recomendação explicável diria: "Esta alternativa foi incluída porque aumenta a cobertura no período em que os dados apontam maior exposição à chuva intensa." Também deveria indicar os custos ou restrições a validar. Sem cálculo de perda de solo, não se deve prometer uma redução percentual específica da erosão.

### 18.5 O que os cenários demonstram

Grãos no Cerrado, sequeiro no Semiárido, café no Sudeste serrano e áreas inclinadas com chuva concentrada são recortes candidatos para a demonstração (ver Q-01 em `DECISOES.md`). O Sul, com geada e culturas de inverno, e a borda da Amazônia, com muitas nuvens na safra, são outros contrastes possíveis. As histórias acima ilustram perguntas associadas a esses recortes; não são diagnósticos regionais. O valor da demonstração será mostrar como dados locais alteram a comparação, e não apenas repetir estereótipos sobre cada região.

---

## 19. Exercícios numéricos comentados

### 19.1 Lâmina e volume

**Problema hipotético:** uma área de 3 hectares apresenta ET acumulada de 18 mm. Qual é o volume correspondente? Cada milímetro em 1 hectare corresponde a 10 m³. Portanto, 18 × 3 × 10 = 540 m³. A conversão também pode ser feita por área: 30.000 m² × 0,018 m = 540 m³.

**Interpretação:** esse é o volume equivalente à lâmina estimada. Não é uma prescrição de irrigação. A pergunta "quanto irrigar?" exige uma conta adicional, com reserva do solo, chuva e desempenho do sistema.

### 19.2 Umidade relativa à referência

**Problema hipotético:** referência de 0,24 m³/m³ e observação de 0,18 m³/m³. A anomalia simples é −0,06 m³/m³. A diferença relativa é −0,06 ÷ 0,24 × 100 = −25%. Em porcentagem volumétrica, o valor foi de 24% para 18%, uma redução de seis pontos percentuais.

**Interpretação:** "25% abaixo da referência" é correto para a diferença relativa. "O solo perdeu 25 pontos percentuais de umidade" não é. Também não se pode deduzir a água disponível às raízes sem conhecer a camada e suas características.

### 19.3 NDVI

**Problema hipotético:** NIR = 0,48 e RED = 0,12. A conta é (0,48 − 0,12) ÷ (0,48 + 0,12) = 0,36 ÷ 0,60 = 0,60. Se outro dia apresentar NIR = 0,36 e RED = 0,18, o índice será 0,18 ÷ 0,54 = aproximadamente 0,33.

**Interpretação:** houve redução do contraste usado pelo índice. Para saber o motivo, verifique qualidade, manejo, fase de desenvolvimento e consistência dos pixels. Não atribua automaticamente a mudança à falta de água.

### 19.4 Demanda estimada e balanço

**Problema hipotético:** ETo = 5 mm/dia e Kc = 0,80. ETc = 4 mm/dia. Em sete dias, se ambos permanecerem constantes, a ETc acumulada será 28 mm. Suponha agora que o balanço use ET real de 24 mm, chuva de 12 mm e irrigação de 5 mm, sem outros fluxos. A reserva diminui 7 mm: 12 + 5 − 24 = −7.

**Interpretação:** ETc e ET real tiveram papéis diferentes. Trocar silenciosamente uma pela outra altera o significado do resultado. O aplicativo deve informar qual variável foi utilizada na conta.

### 19.5 Frequência de frio

**Problema hipotético:** 9 dias atenderam ao critério de frio entre 900 dias válidos. A frequência é 1%. Se o arquivo original tinha 1.000 dias e 100 estavam ausentes, usar 1.000 no denominador trataria ausência como observação válida.

**Interpretação:** além da frequência, informe a cobertura de dados e o critério aplicado. O resultado descreve a série observada; não é uma probabilidade de dano nem uma previsão para o dia seguinte.

---

## 20. Como escrever os cartões da ferramenta

### 20.1 Estrutura sugerida

Cada cartão pode conter nome simples, definição, valor, unidade, período, comparação histórica, fonte, escala, qualidade e implicação para a análise. Nem todos esses campos precisam estar visíveis ao mesmo tempo, mas devem ser acessíveis. Uma camada curta atende o produtor; uma camada de detalhes permite a revisão técnica.

Exemplo hipotético de cartão de umidade:

> "Umidade superficial abaixo do habitual. Valor: 0,18 m³/m³. Referência para o mês: 0,24 m³/m³. Diferença: −0,06 m³/m³. Escala: regional. Interpretação: investigar possível redução da reserva; a condição na zona das raízes não foi medida diretamente."

Esse cartão separa dado, comparação e consequência proposta. Não utiliza "seca severa" sem um método que sustente essa classificação.

### 20.2 Texto curto e explicação expandida

| Termo | Texto curto para o produtor |
|---|---|
| Evapotranspiração | Água que passa do solo e da vegetação para o ar. |
| ETo | Referência climática para estimar a demanda de água. |
| Umidade do solo | Água presente na camada de solo analisada. |
| Anomalia de umidade | Diferença em relação ao habitual para a época e o local. |
| NDVI | Indicador da presença e do vigor da vegetação verde. |
| Risco de geada | Possibilidade de frio prejudicial, conforme a cultura e o local. |
| Balanço hídrico | Conta da água que entra, sai e permanece armazenada. |
| Déficit hídrico | Insuficiência de água em relação à necessidade considerada. |
| Estresse hídrico | Resposta da planta à limitação de água. |
| Confiança do indicador | Qualidade do suporte disponível para interpretar o resultado. |

A explicação expandida deve acrescentar o que o indicador não resolve sozinho. Para NDVI, por exemplo: "Uma queda pode ocorrer após a colheita ou por outros fatores. Confira a fase da cultura e a qualidade da observação." Para chuva: "O total não informa sozinho quanto ficou disponível na região das raízes."

### 20.3 Justificativa de uma estratégia

Uma boa justificativa conecta condição, alternativa e limitação: "A alternativa foi incluída para ampliar a proteção do solo no intervalo de baixa cobertura verde. O histórico de chuva e o relevo justificam atenção a esse período. Ainda é necessário verificar palhada existente, água disponível e compatibilidade com o calendário."

Uma nota final pode organizar prioridades, mas não substitui essa explicação. Se o produtor aumentar o peso da água, o sistema deve mostrar por que a classificação mudou. Uma pontuação de 8 não significa 80% de chance de sucesso, a menos que exista um modelo probabilístico validado que lhe dê esse significado.

---

## 21. Erros frequentes e como corrigi-los

### 21.1 "NDVI alto garante produtividade alta"

**Correção:** o índice descreve características da vegetação verde observada. Produtividade exige outras informações. No projeto, a comunicação deve falar em cobertura e comportamento da vegetação, evitando prometer rendimento com base apenas no índice.

### 21.2 "NDVI baixo significa solo totalmente descoberto"

**Correção:** pode existir palhada, resíduos, cultivo recém-estabelecido ou problemas de qualidade. Use "baixa cobertura verde detectada" quando essa for a evidência disponível e confirme a condição do solo com informações complementares.

### 21.3 "ET baixa é sempre economia de água"

**Correção:** pode representar menor atividade vegetal ou limitação de água. Para falar em eficiência, defina o resultado obtido e o uso de água considerado. Comparar apenas a saída de água, sem o benefício produtivo ou ambiental, é insuficiente.

### 21.4 "Anomalia positiva significa excesso prejudicial"

**Correção:** significa acima da referência. O nível pode continuar adequado ou até baixo para a necessidade da cultura. Anomalia, disponibilidade e encharcamento respondem a perguntas diferentes.

### 21.5 "A média mensal não mostrou frio, então não houve geada"

**Correção:** um extremo curto pode desaparecer na média. Preserve mínimos e contagens de eventos a partir de dados na resolução temporal adequada. Declare o critério meteorológico e não o confunda automaticamente com dano.

### 21.6 "Chuva menos ET é todo o balanço hídrico"

**Correção:** é uma conta parcial. Irrigação, armazenamento, escoamento, drenagem e outros fluxos podem alterar o resultado. Se usar uma aproximação, identifique-a como tal.

### 21.7 "Aumentar a resolução da imagem aumenta a precisão do dado"

**Correção:** reamostrar muda a grade ou apresentação, mas não cria novas observações. A interpretação deve preservar a escala de origem. Um mapa visualmente detalhado pode continuar sustentado por informação regional.

### 21.8 "Duas fontes concordaram, então o dado está comprovado"

**Correção:** concordância é uma evidência, não garantia. As fontes podem compartilhar dados e hipóteses. Verifique independência, escala, período e possibilidade de validação local.

### 21.9 "A melhor nota identifica uma cultura ideal para qualquer produtor"

**Correção:** a nota depende de critérios, pesos e restrições. Uma opção pode ser ambientalmente interessante e operacionalmente inviável. A comparação deve permitir entender essas diferenças, preservando o julgamento do produtor e a revisão agronômica.

---

## 22. Dicionário complementar e perguntas de revisão

### 22.1 Termos de uso recorrente

- **Talhão:** unidade delimitada de manejo dentro da propriedade. Seu tamanho e contorno influenciam como os dados de imagem podem representá-lo.
- **Dossel:** conjunto de partes aéreas da vegetação, especialmente folhas e ramos, que compõe a superfície observada em muitos produtos de sensoriamento.
- **Fenologia:** sequência de fases de desenvolvimento, como emergência, crescimento, florescimento e maturação. No projeto, ajuda a comparar observações de momentos equivalentes do ciclo.
- **Biomassa:** quantidade de matéria biológica considerada em uma área ou organismo. Deve-se indicar se a medida envolve matéria seca ou fresca, parte aérea ou subterrânea, e qual método foi utilizado. NDVI não é uma medida direta de biomassa em qualquer situação.
- **Série temporal:** sequência de valores organizados no tempo. Sua interpretação depende de frequência, lacunas e consistência do método.
- **Climatologia de referência:** descrição estatística de condições climáticas em um período definido. No aplicativo, o período precisa acompanhar comparações e anomalias.
- **Pixel:** unidade de uma imagem ou grade. Pode representar mistura de alvos, e não necessariamente uma cultura homogênea.
- **Validação:** avaliação de um resultado usando informações adequadas à variável e à escala. Não se resume à semelhança visual entre mapas.
- **Cenário:** conjunto de hipóteses para explorar uma possibilidade. Um cenário de menor chuva não é necessariamente uma previsão de que essa chuva ocorrerá.
- **Resiliência:** capacidade de um sistema de lidar com perturbações e manter ou recuperar funções relevantes. No Field Shift, precisa ser traduzida em critérios concretos, e não usada como promessa genérica.

### 22.2 Perguntas para testar a compreensão

**Por que dois meses com a mesma chuva acumulada podem ter efeitos diferentes?**
Porque a distribuição dos eventos, a intensidade, a reserva do solo e a fase da cultura alteram a interpretação do total.

**Por que uma área com anomalia de umidade igual a zero pode sofrer restrição?**
Porque o habitual daquela época pode ser insuficiente para a necessidade da cultura. Normalidade histórica não equivale a adequação agronômica.

**Por que um NDVI que caiu depois da colheita não indica necessariamente problema?**
Porque a retirada da vegetação é uma explicação de manejo compatível com a data. A série deve ser lida junto do calendário.

**Por que dados mensais precisam preservar extremos?**
Porque médias podem ocultar eventos curtos relevantes, como madrugadas frias ou chuva concentrada.

**Qual é a principal função do glossário na ferramenta?**
Permitir que cada evidência seja compreendida dentro de seus limites, para que a comparação de estratégias seja explicável e revisável.

---

## 23. Fontes e rastreabilidade

### 23.1 Base do projeto

Documentos fornecidos pelo usuário: "Field Shift Minas - Documentação do Projeto.md" e "Texto colado(20261114-132558).txt", que contém o contexto do desafio e a descrição de recursos. Eles fundamentaram o recorte inicial em Minas Gerais (depois ampliado para o Brasil inteiro pela D-008), os objetivos, as fontes candidatas e a proposta de comparação de estratégias.

As explicações são sínteses em português, acompanhadas de exemplos próprios. Não são transcrições dos documentos científicos. Os números dos exercícios e os cenários são didáticos. As sugestões para a interface e a metodologia constituem propostas de aplicação, não especificações oficialmente aprovadas pela NASA.

### 23.2 Referências técnicas

1. FAO. Crop evapotranspiration, Paper 56. Capítulo 1: processos, unidades e conceitos de evapotranspiração. <https://www.fao.org/4/x0490e/x0490e04.htm>
2. NASA/JPL. ECOSTRESS: missão e relação entre evaporação, transpiração e água na vegetação. <https://www.jpl.nasa.gov/missions/ecosystem-spaceborne-thermal-radiometer-experiment-on-space-station-ecostress/>
3. FAO. Paper 56, capítulo 5: evapotranspiração da cultura e abordagem por coeficiente. <https://www.fao.org/4/x0490e/x0490e0a.htm>
4. FAO. Paper 56, capítulo 6: coeficiente de cultura e fases de desenvolvimento. <https://www.fao.org/4/x0490e/x0490e0b.htm>
5. NASA/JPL. SMAP: descrição da missão e umidade superficial. <https://smap.jpl.nasa.gov/mission/description/>
6. NASA Goddard. NASA-USDA Global Soil Moisture Data: integração de observações e modelo. <https://earth.gsfc.nasa.gov/hydro/data/nasa-usda-global-soil-moisture-data>
7. Copernicus Climate Change Service. About the data and analysis: definições e anomalias. <https://climate.copernicus.eu/ESOTC/2019/about-data-and-analysis>
8. NASA Goddard. FLDAS-Global: variáveis e referência climatológica de anomalias. <https://ldas.gsfc.nasa.gov/fldas/models/global>
9. NASA Earth Observatory. Measuring Vegetation: NDVI and EVI. <https://science.nasa.gov/earth/earth-observatory/measuring-vegetation-ndvi-evi/>
10. USGS. Landsat Normalized Difference Vegetation Index: fórmula e especificações do produto. <https://www.usgs.gov/landsat-missions/landsat-normalized-difference-vegetation-index>
11. NASA. HLS Vegetation Indices: índices e diferenças de sensibilidade. <https://science.nasa.gov/mission/landsat/hls-vegetation-indices/>
12. USGS. Landsat Enhanced Vegetation Index. <https://www.usgs.gov/landsat-missions/landsat-enhanced-vegetation-index>
13. FAO. Soil organic cover: resíduos e cobertura do solo. <https://www.fao.org/conservation-agriculture/in-practice/soil-organic-cover/en>
14. FAO. Frost protection: fundamentals, practice, and economics. Volume 1, capítulo 1. <https://www.fao.org/4/y7223e/y7223e07.htm>
15. FAO. Frost protection. Volume 1, capítulo 4: danos e temperaturas críticas. <https://www.fao.org/4/y7223e/y7223e0a.htm>
16. FAO. Multiple uses of water services in large irrigation systems: limites e componentes do balanço. <https://www.fao.org/4/i3414e/i3414e.pdf>
17. FAO. Paper 56, capítulo 8: disponibilidade de água, estresse e balanço na zona radicular. <https://www.fao.org/4/x0490e/x0490e0e.htm>
18. FAO. Irrigation Water Needs: precipitação efetiva e necessidade de irrigação. <https://www.fao.org/4/s2022e/s2022e08.htm>
19. NASA GPM. IMERG: descrição do produto de precipitação. <https://gpm.nasa.gov/data/imerg>
20. NASA GPM. Precipitation Data Directory: produtos e integração de estimativas. <https://gpm.nasa.gov/data/directory>
21. FAO. Conservation Agriculture: princípios gerais. <https://www.fao.org/conservation-agriculture>
22. FAO. Crop rotation in conservation agriculture. <https://www.fao.org/family-farming/detail/en/c/1619114/>
23. FAO. Cover crop species, with a special focus on legumes. <https://www.fao.org/family-farming/detail/en/c/1619115/>
24. USDA NRCS. National Agronomy Manual: culturas e fixação biológica de nitrogênio. <https://www.nrcs.usda.gov/sites/default/files/2022-10/National-Agronomy-Manual.pdf>
25. ECMWF. Complete ERA5 global atmospheric reanalysis. <https://www.ecmwf.int/en/forecasts/datasets/complete-era5-global-atmospheric-reanalysis>
26. NASA POWER. Meteorological data sources. <https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/>
27. FAO. Global Agro-Ecological Zones: recursos e potencial agrícola. <https://www.fao.org/land-water/resources/tools/databases/gaez/en>

*Consulta das fontes: 14 de novembro de 2026. Características operacionais e versões de produtos devem ser conferidas novamente no momento da implementação. As fontes foram usadas para conceitos e limites de interpretação, não para produzir um diagnóstico atual de qualquer região do Brasil.*
