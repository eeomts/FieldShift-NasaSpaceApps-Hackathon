# Field Shift: o desafio da NASA explicado

Explicado do zero, para quem está começando. Desafio "Adapting Farms with NASA Data" do NASA Space Apps Challenge 2026.

> 💡 **Como ler este guia:** a Parte 1 explica as palavras difíceis que aparecem no desafio. A Parte 2 mostra o problema em uma página. Da Parte 3 em diante você vê como a ferramenta poderia funcionar, passo a passo, com a história de um agricultor. Se travar numa palavra, pule para o **Glossário** no final.

---

## Parte 0 — O desafio em 30 segundos

O clima está mudando: chove na hora errada, faz mais calor, falta água e o solo está ficando mais fraco. O agricultor precisa decidir **o que plantar em cada estação**, e errar custa caro.

**O que a NASA pede:** um programa (site, app, mapa ou modelo) que junte **dados de satélite da NASA** + **informações do solo e das plantas** + **o que o agricultor quer** (economizar água, ganhar mais dinheiro, melhorar o solo) e mostre **opções de rodízio de plantações**, comparando pelo menos três delas, explicando os prós, contras e incertezas de cada uma.

**O que a NASA NÃO pede:** uma máquina que manda no agricultor. A ferramenta **ajuda a pensar**, mas quem decide é ele.

> 🟢 **Na vida real:** é como o app de mapas do celular. Ele mostra três caminhos possíveis, diz quanto tempo cada um leva e avisa onde tem trânsito. Mas é você quem escolhe por onde ir, porque sabe coisas que o app não sabe (a rua que alaga, a padaria no caminho).

---

## Parte 1 — As palavras que você precisa conhecer

### 1.1 Rotação de culturas (crop rotation)

"Cultura", na agricultura, quer dizer **o tipo de planta cultivada** (milho, soja, alfafa, trigo). **Rotação de culturas** é trocar o que se planta no mesmo campo ao longo das estações e dos anos, em vez de plantar sempre a mesma coisa.

Por que trocar? Cada planta tira do solo nutrientes diferentes, atrai pragas diferentes e deixa coisas diferentes para trás. Plantar sempre o mesmo cansa o solo e deixa as pragas "acampadas" ali.

> 🟢 **Na vida real:** é como o cardápio de um restaurante. Se você comer só feijoada todo dia, falta vitamina e você enjoa. Variando o prato, o corpo fica mais saudável. O solo é parecido.

### 1.2 Saúde do solo

Solo saudável é solo que **segura água, tem nutrientes, tem vida (minhocas, fungos, bactérias) e não se desfaz** com chuva forte. Os inimigos dele são:

- **Erosão:** a chuva ou o vento levando embora a camada de cima do solo, que é a mais fértil.
- **Esgotamento de nutrientes:** as plantas "comem" o que o solo tem e ninguém repõe.
- **Pouca matéria orgânica:** matéria orgânica é resto de planta e bicho apodrecido. É o "adubo natural" que deixa o solo fofo e esponjoso.

> 🟢 **Na vida real:** o solo é como uma esponja de cozinha. Nova, ela absorve muita água. Velha e ressecada, a água escorre por cima. Matéria orgânica é o que mantém a esponja "nova".

### 1.3 Tipos especiais de planta citados no desafio

| Tipo | O que faz pelo solo |
|---|---|
| **Fixadora de nitrogênio** (feijão, soja, alfafa, ervilha) | Nitrogênio é o "alimento principal" das plantas. Essas plantas, com ajuda de bactérias nas raízes, puxam nitrogênio do ar e deixam no solo. É adubo de graça. |
| **Planta de cobertura** (cover crop) | Plantada só para o solo não ficar pelado entre uma safra e outra. Protege contra erosão e alimenta o solo. Muitas vezes nem é colhida. |
| **Raiz profunda** (nabo forrageiro, alfafa) | Fura o solo compactado, abrindo caminhos para a água entrar. |
| **Tolerante à seca** (sorgo, milheto) | Aguenta pouca água. Bom onde a água está acabando. |
| **Forrageira** (forage) | Planta que vira comida para o gado. Pode gerar renda extra. |

> 🟢 **Na vida real:** a planta de cobertura é como o lençol que você joga sobre o sofá quando vai viajar: ninguém está "usando" o sofá, mas ele fica protegido da poeira e do sol.

### 1.4 Campo pelado (bare field)

É o período em que o campo fica **sem nenhuma planta**, normalmente entre a colheita e o próximo plantio. Nessa hora o solo fica exposto ao sol, ao vento e à chuva, e é quando mais sofre erosão. O desafio sugere que a ferramenta **mostre quando isso acontece**, porque é uma oportunidade de encaixar uma planta de cobertura.

### 1.5 Sensoriamento remoto (observação da Terra)

É **medir coisas na Terra sem tocar nelas**, usando satélites lá no espaço. O satélite "fotografa" a Terra com câmeras especiais que enxergam calor, umidade e até a "saúde" das plantas.

> 🟢 **Na vida real:** é como o médico que usa um termômetro de testa: ele mede sua temperatura sem colocar nada na sua boca. Rápido e de longe, mas um pouco menos preciso.

### 1.6 Satélite × medição no chão

| | Satélite | Medição no chão (estação, sensor no campo) |
|---|---|---|
| Cobertura | O mundo inteiro | Só aquele ponto |
| Precisão | Média (cada "pixel" pode ter quilômetros) | Alta, mas só ali |
| Histórico | Décadas de dados | Depende de alguém ter instalado |

O desafio pede para explicar essa diferença e mostrar que **juntar os dois** dá um resultado melhor.

> 🟢 **Na vida real:** o satélite é a foto aérea do bairro; a medição no chão é você andando na rua. A foto mostra tudo, mas sem detalhe. Andando, você vê o buraco na calçada, mas só da sua rua.

### 1.7 Resolução (espacial e temporal)

- **Resolução espacial:** o tamanho de cada "quadradinho" (pixel) da imagem. Um satélite pode ter pixel de 30 metros (vê um campo) e outro de 9 quilômetros (vê uma cidade inteira como um ponto só).
- **Resolução temporal:** de quanto em quanto tempo o satélite passa de novo. Uns todo dia, outros a cada 16 dias.

**Harmonizar** é colocar todos os dados na mesma "régua": mesmo tamanho de quadradinho e mesma frequência, para conseguir comparar.

> 🟢 **Na vida real:** imagine juntar receitas onde uma usa "xícaras", outra "gramas" e outra "colheres". Antes de cozinhar, você converte tudo para a mesma medida. Harmonizar dados é isso.

### 1.8 Os termos científicos que o desafio pede para explicar

- **Evapotranspiração (ET):** a água que sai do campo para o ar. Uma parte **evapora** do solo (como roupa secando no varal) e outra parte a planta **"transpira"** pelas folhas (como a gente suando). ET alta = o campo está "gastando" muita água.
- **Umidade do solo:** quanta água tem dentro da terra.
- **Anomalia de umidade do solo:** a diferença entre a umidade de **hoje** e o **normal** para essa época do ano. Se costuma estar úmido em março e este ano está seco, é uma anomalia negativa.
  > 🟢 **Na vida real:** sua febre não é "37,8 °C"; é "1 grau acima do seu normal". Anomalia é sempre comparação com o normal.
- **NDVI (índice de vegetação):** um número de -1 a 1 calculado da imagem de satélite que diz **o quão verde e viva** está a vegetação. Perto de 0,8 = planta vigorosa. Perto de 0,1 = solo pelado ou planta morrendo. Funciona porque folha saudável reflete muita luz infravermelha (que nosso olho não vê, mas o satélite vê).
- **Risco de geada:** chance de a temperatura cair abaixo de 0 °C e congelar a planta.
- **Estresse térmico:** calor tão forte que a planta para de crescer ou perde a flor.
- **Balanço hídrico:** a "conta bancária" da água: **chuva que entra − água que sai (evapotranspiração + escoamento)**. Saldo negativo = falta água.
  > 🟢 **Na vida real:** é o extrato do banco. Salário entra, contas saem. Se sai mais do que entra por muito tempo, o saldo fica no vermelho.

### 1.9 "SI" (inteligência artificial e modelos estatísticos)

No texto do desafio aparece **"SI techniques"**. Pelo contexto, é o que normalmente chamamos de **IA (inteligência artificial)** e técnicas estatísticas: programas que **aprendem padrões olhando muitos dados históricos**.

> ⚠️ **Cuidado:** a sigla "SI" não é a usual ("AI" seria o normal em inglês). Vale confirmar com os mentores do evento no Space Apps Connect o que exatamente eles querem dizer.

Exemplo do que um modelo pode fazer aqui: olhar 20 anos de dados e perceber "todo ano, no fim de julho, o NDVI cai e o solo seca. É quando a plantação sofre".

> 🟢 **Na vida real:** é como a avó que, de tanto ver o céu, diz "esse vento aí traz chuva amanhã". Ela aprendeu o padrão observando. O modelo faz igual, só que com números e milhares de anos-campo.

### 1.10 Incerteza

Todo dado e toda previsão têm uma margem de erro. O desafio quer que a ferramenta **diga o quanto confia** em cada sugestão e **onde faltam dados**.

> 🟢 **Na vida real:** a previsão do tempo diz "70% de chance de chuva", não "vai chover". Ser honesto sobre a dúvida faz a pessoa confiar mais, não menos.

### 1.11 Ferramenta de apoio à decisão (decision-support tool)

Um programa que **organiza informações para ajudar alguém a decidir**, sem decidir por ele. É exatamente o que o desafio pede.

---

## Parte 2 — O quadro geral: os satélites e o que cada um mede

O desafio cita vários "produtos" da NASA. Cada um é como um **instrumento diferente** numa caixa de ferramentas.

| Nome | O que mede | Para que serve no nosso problema |
|---|---|---|
| **NASA POWER** | Temperatura, chuva, sol, vento, por dia, desde 1981 | ⭐ O mais fácil de usar. Dá o "clima histórico" de qualquer ponto. Ótimo para começar. |
| **SMAP** | Umidade do solo | Saber se o solo está seco ou úmido, e quando. |
| **GPM** | Chuva (precipitação) no mundo todo, a cada 30 min | Ver chuvas extremas e mudanças no padrão de chuva. |
| **ECOSTRESS** | Temperatura da superfície e evapotranspiração | Ver quando a planta está "sofrendo" de calor e sede. |
| **MODIS** | Imagens diárias de baixa resolução (inclui NDVI) | Acompanhar o verde das plantas dia a dia, em áreas grandes. |
| **Landsat** | Imagens detalhadas (pixel de 30 m), desde os anos 70 | Ver o campo individual: onde está verde, onde está pelado. |
| **GRACE / GRACE-FO** | Variação da água guardada debaixo da terra (lençol freático) | Ver se a água subterrânea está acabando ao longo dos anos. |
| **SRTM** | Relevo (altitude, inclinação do terreno) | Achar ladeiras com risco de erosão e baixadas onde a geada se acumula. |
| **GEDI** | Biomassa (quantidade de planta) usando laser | Opcional, mais avançado. |

> 💡 **Dica:** para um hackathon de 48 horas, **NASA POWER** é o melhor ponto de partida. Ele tem um site que devolve dados com uma simples chamada de URL, sem precisar baixar imagens gigantes. Deixe Landsat, SMAP e os outros como "camadas extras" se der tempo.

E fora da NASA, a ferramenta ainda precisa de:

| Informação | De onde pode vir |
|---|---|
| Tipo de solo | Bancos de dados públicos de solo (ex.: SoilGrids, ou o mapa de solos da Embrapa no Brasil) |
| Características das plantas | Quanta água gastam, se fixam nitrogênio, ciclo em dias (tabelas agronômicas) |
| Prioridades do agricultor | **Ele mesmo digita** na ferramenta |

---

## Parte 3 — Como a ferramenta poderia funcionar (a história do seu Antônio)

### O problema que resolve

Seu Antônio planta **milho no verão** e deixa o campo **pelado no inverno**, há 20 anos. Ultimamente o milho tem sofrido com secas no meio do verão, a água do poço está mais baixa e a terra parece "mais dura". Ele quer saber: *"o que posso mudar?"*

### Passo a passo

1. **Seu Antônio marca o campo dele no mapa.** Ele clica no ponto da fazenda ou desenha o contorno do campo.
2. **Ele conta a rotação atual:** "milho no verão, nada no inverno".
3. **Ele escolhe as prioridades** em controles simples, tipo arrastar uma barrinha:
   - Economizar água: muito importante
   - Ganhar renda extra: médio
   - Melhorar o solo: importante
   - Equipamento disponível: só trator e plantadeira de grãos
4. **A ferramenta busca os dados da NASA** daquele ponto: 20+ anos de chuva, temperatura, umidade do solo, NDVI, água subterrânea e relevo.
5. **Ela mostra o "raio-x" do campo**, em linguagem simples:
   - "Seu campo fica **pelado de maio a setembro** (o NDVI fica abaixo de 0,2)."
   - "Nos últimos 10 anos, **janeiro ficou 1,5 °C mais quente** e a umidade do solo em janeiro está **abaixo do normal** em 7 de 10 anos."
   - "A água debaixo da terra na sua região **caiu** desde 2010 (GRACE)."
   - "A parte sul do campo é **inclinada**: risco maior de erosão."
6. **Ela monta pelo menos 3 estratégias** (a atual + 2 alternativas) e compara lado a lado:

| | A) Atual: milho + campo pelado | B) Milho + planta de cobertura no inverno | C) Sorgo + feijão/ervilha |
|---|---|---|---|
| Uso de água | Alto | Alto (cobertura usa pouca) | **Menor** |
| Solo | Piora (pelado no inverno) | **Melhora** (protegido) | Melhora (feijão deixa nitrogênio) |
| Erosão | Alta | **Baixa** | Média |
| Pragas | Ciclo de pragas do milho continua | Igual | **Quebra o ciclo** (planta diferente) |
| Renda | Conhecida | Igual + pouco custo de semente | Incerta: tem mercado para sorgo aqui? |

7. **Para cada estratégia, ela explica** (é o que o desafio pede, com essas palavras):
   - **Por que foi sugerida:** "o campo fica pelado 5 meses e a encosta sul tem erosão".
   - **Qual a evidência:** "dados de NDVI do Landsat 2005–2025 e relevo do SRTM".
   - **Benefícios:** "menos erosão, mais matéria orgânica".
   - **Lacunas de informação:** "não temos dados de pragas locais".
   - **Riscos para revisão local:** "confirme com o técnico agrícola se a planta de cobertura não atrapalha o plantio do milho".
8. **Seu Antônio conversa com o agrônomo** levando esse relatório. A decisão final é deles.

### E se der erro? (ou: onde a ferramenta pode se enganar)

- **Pixel grande demais:** o satélite de umidade (SMAP) tem pixel de ~9 km. A fazenda do seu Antônio pode ser bem diferente do "quadradão" em volta. A ferramenta deve **avisar** isso.
- **Nuvens:** em dias nublados, satélites de imagem (Landsat, MODIS) não enxergam o chão. Fica buraco nos dados.
- **Coisas que satélite não vê:** preço de mercado, pragas, o que o vizinho planta, a experiência da família. Por isso o agricultor sempre tem a palavra final.

---

## Parte 4 — Ideias de "extras" citadas no desafio

São opcionais, mas contam pontos se der tempo:

- **Mapa interativo** com camadas que liga e desliga (chuva, calor, umidade).
- **Linha do tempo**: arrastar e ver o campo mudando de 2000 até hoje.
- **Mapa de vulnerabilidade do campo**: manchas de "risco de erosão", "ponto de sede", "área de geada".
- **Simulador ("e se?")**: barrinhas para "e se chover 20% menos?" ou "e se esquentar 2 °C?" e ver como as estratégias mudam.
- **Lembretes visíveis** do tipo "esta é uma sugestão; confirme com quem conhece a região".

---

## Parte 5 — Um formato possível para a equipe (o mínimo que funciona)

O repositório `nasa-space-app` hoje só tem o `README.md`. Uma organização simples para começar poderia ser:

```text
nasa-space-app/
├── README.md          # o que é o projeto e como rodar
├── dados/             # scripts que buscam dados da NASA (começar pelo NASA POWER)
├── modelo/            # regras e cálculos que montam e comparam as rotações
├── culturas.csv       # tabela das plantas: água que gasta, fixa nitrogênio?, ciclo...
└── app/               # a tela: mapa, formulário de prioridades, comparação
```

Para ter uma ideia de como é "pedir dados" à NASA POWER, este é um exemplo de endereço (você cola no navegador e recebe os números):

```text
https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M,PRECTOTCORR&community=AG&longitude=-47.9&latitude=-15.8&start=2005&end=2024&format=JSON
```

Linha por linha do que ele pede:

- `temporal/monthly/point` → "quero dados **mensais** de **um ponto**".
- `parameters=T2M,PRECTOTCORR` → temperatura a 2 metros do chão (`T2M`) e chuva (`PRECTOTCORR`).
- `community=AG` → formato pensado para **agricultura**.
- `longitude` / `latitude` → onde fica o ponto (aqui, perto de Brasília).
- `start` / `end` → de 2005 a 2024.
- `format=JSON` → o formato de texto que programas leem fácil.

> 💡 **Dica:** não tentem usar todos os satélites. Uma ferramenta **simples, que funciona e que explica bem** ganha de uma ferramenta enorme que não roda na hora da apresentação.

---

## Por onde começar

1. **Leia a aba "Resources"** da página do desafio: a NASA lista lá os links e tutoriais oficiais dos dados.
2. **Teste o NASA POWER** colando o endereço acima no navegador e mudando a latitude/longitude para uma fazenda real.
3. **Escolham juntos uma região e uma rotação de exemplo** (ex.: milho/soja no Paraná, ou alfafa em Nevada, como na foto do desafio). Ter um "seu Antônio" concreto ajuda a apresentação.
4. **Montem a tabela das 3 estratégias** à mão primeiro (como na Parte 3) e só depois automatizem.
5. **Desenhem a tela no papel** antes de programar, pensando num agricultor que não é da área de tecnologia.

Ficou alguma dúvida? Pergunte sem medo. Em hackathon, quem pergunta cedo economiza horas depois. 🚀

> ⚠️ **Cuidado:** a ferramenta dá **sugestões**, não ordens. Uma recomendação errada sobre plantio pode custar a safra de uma família. Deixe isso claro na tela e na apresentação: mostre a incerteza, diga de onde vem cada dado e lembre que a palavra final é do agricultor e do técnico local.

---

## Glossário

| Termo | O que significa |
|---|---|
| **Anomalia** | Diferença entre o valor de agora e o normal para aquela época do ano. |
| **Apoio à decisão (ferramenta de)** | Programa que organiza informações para ajudar alguém a decidir, sem decidir por ele. |
| **Balanço hídrico** | Conta da água: o que entra (chuva) menos o que sai (evaporação, escoamento). |
| **Biomassa** | Quantidade de planta (matéria viva) num lugar. |
| **Campo pelado (bare field)** | Período em que o campo fica sem nenhuma planta. |
| **Cultura** | Tipo de planta cultivada (milho, soja, trigo...). |
| **Erosão** | Perda da camada fértil do solo levada por chuva ou vento. |
| **Estresse térmico** | Calor forte demais que prejudica a planta. |
| **Evapotranspiração (ET)** | Água que sai do campo para o ar: evaporação do solo + "suor" das plantas. |
| **Fixadora de nitrogênio** | Planta (como feijão e soja) que tira nitrogênio do ar e deixa no solo. |
| **Forrageira** | Planta usada como alimento para o gado. |
| **Geada (risco de)** | Chance de a temperatura cair abaixo de 0 °C e congelar a planta. |
| **Harmonizar dados** | Converter dados diferentes para a mesma "régua" (mesmo tamanho de pixel e mesma frequência). |
| **IA / "SI"** | Programas que aprendem padrões a partir de muitos dados. |
| **Incerteza** | Margem de erro de um dado ou de uma previsão. |
| **JSON** | Formato de texto organizado que programas leem com facilidade. |
| **Lençol freático / água subterrânea** | Água guardada debaixo da terra, que abastece poços. |
| **Matéria orgânica** | Restos de plantas e bichos no solo; deixa a terra fofa e fértil. |
| **NDVI** | Número de -1 a 1 que mostra o quão verde e viva está a vegetação. |
| **Pixel** | Cada "quadradinho" de uma imagem de satélite. |
| **Planta de cobertura (cover crop)** | Planta usada para proteger o solo entre safras. |
| **Resolução espacial** | Tamanho do pixel (quanto de chão cada quadradinho representa). |
| **Resolução temporal** | De quanto em quanto tempo o satélite mede de novo. |
| **Rotação de culturas** | Trocar o que se planta no mesmo campo ao longo do tempo. |
| **Satélite / sensoriamento remoto** | Medir a Terra de longe, a partir do espaço. |
| **Umidade do solo** | Quantidade de água dentro da terra. |
| **ECOSTRESS, GEDI, GPM, GRACE, Landsat, MODIS, NASA POWER, SMAP, SRTM** | Satélites e bases de dados da NASA (veja a tabela da Parte 2). |
