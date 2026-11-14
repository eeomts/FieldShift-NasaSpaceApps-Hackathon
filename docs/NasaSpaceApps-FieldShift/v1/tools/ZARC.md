# ZARC no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o ZARC, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o ZARC aos outros datasets.

## O que é o ZARC

O ZARC (Zoneamento Agrícola de Risco Climático) é o estudo oficial do **Ministério da Agricultura (MAPA)**, feito com a **Embrapa**, que indica **quando plantar** cada cultura em cada município com menor risco de perda por clima.

Para cada combinação de município, cultura, tipo de solo e ciclo da cultivar, o ZARC lista os **períodos de semeadura**, divididos em decêndios (blocos de cerca de 10 dias), com o nível de risco: 20%, 30% ou 40%. O risco é a chance estimada de perda por seca, excesso de chuva, geada ou calor.

O ZARC é publicado em **portarias** por cultura e estado. Ele é exigido para acessar o Proagro e a subvenção ao seguro rural, por isso o produtor e o banco já o conhecem. Há zoneamentos para grãos, frutas, pastagens e até para o consórcio de milho com braquiária.

## Por que usar

**1. É a referência oficial de calendário.** A ferramenta não precisa inventar janela de plantio: o ZARC já a calcula para o país inteiro.

**2. Valida as estratégias.** A Q-11 cita o ZARC como forma de validar o projeto. Uma estratégia que sugere semear fora da janela de menor risco precisa ser revista ou explicada.

**3. Confiança do produtor.** Um cartão que diz "dentro da janela do ZARC" usa uma linguagem que o produtor e o agente de crédito já entendem.

**4. O que o ZARC não faz, a ferramenta faz.** O ZARC olha uma cultura por vez e não pensa em rotação, solo ou prioridades do produtor (ver a análise das ferramentas existentes). O Field Shift junta as janelas de duas ou três culturas e mostra se a sequência cabe no ano.

## Como entra no projeto

### Harmonização

- **Acesso:** Painel de Indicação de Riscos do ZARC (consulta por cultura, safra, município, solo e cultivar, com extração em PDF ou XLS); portarias no site do MAPA; "Tábua de risco" em CSV por safra no portal de dados abertos do MAPA (`dados.agricultura.gov.br`), com dicionário de dados.
- **Processamento:** baixar a tábua de risco das culturas de interesse, transformar decêndios em datas, guardar para cada município a janela de 20% (e as de 30% e 40%) por tipo de solo e ciclo, e ligar à grade comum pelo código do município.

| Campo | O que é | Uso |
| --- | --- | --- |
| Município (código IBGE) | Local da indicação | Ligar à grade e à PAM |
| Cultura | Cultura zoneada | Filtrar as culturas da estratégia |
| Tipo de solo | Classe pela água disponível no solo | Escolher a janela certa |
| Grupo de cultivar | Ciclo (precoce, médio, tardio) | Escolher a janela certa |
| Decêndio de semeadura | Bloco de ~10 dias do ano | Calendário |
| Nível de risco | 20%, 30% ou 40% | Cor da janela no calendário |

> Confirmar nas páginas oficiais os nomes exatos das colunas da tábua de risco, a classificação de solos usada em cada cultura (classes de água disponível), a diferença entre "Zarc Oficial" e "Zarc Para Validação" no painel, a safra vigente de cada portaria e o estado do ZARC por níveis de manejo do solo.

### Indicadores calculados

- **Janela de menor risco:** primeiro e último decêndio com risco de 20%, por cultura, solo e ciclo.
- **Encaixe da rotação:** se a segunda cultura cabe na janela depois da colheita típica da primeira.
- **Margem de folga:** quantos dias sobram entre a colheita e o fim da janela.
- **Plantio real fora da janela:** quantos dos últimos anos o HLS viu a semeadura depois do último decêndio de 20%.

### Nível de confiança

O ZARC é **referência oficial**, mas é uma simulação. Ele usa um balanço hídrico alimentado por séries de chuva de estações, muitas delas da ANA e do INMET. Por isso, comparar o ZARC com essas estações **não é confirmação independente**. Comparar com a água no solo do GLDAS e do SMAP L4 e com o calendário real do HLS é mais limpo. O ZARC também é feito por município: um talhão em baixada ou com solo diferente do declarado pode ter outro risco.

## Onde o produtor vê isso

**Etapa 2, calendário.** As janelas do ZARC aparecem como faixas verdes (20%), amarelas (30%) e laranjas (40%) por cultura, sobre a linha do tempo da rotação.

**Cartão da estratégia.** Cada cultura traz a frase "dentro da janela de menor risco do ZARC" ou "fora da janela", com a data.

**Glossário.** Explica decêndio, nível de risco, tipo de solo e o vínculo com o seguro e o Proagro.

## Caso hipotético: ZARC junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

O Sr. Edvaldo planta milho perto de Simão Dias, no agreste de Sergipe, no Nordeste oriental. Ali a chuva vem no outono e no inverno, de abril a agosto, ao contrário do Centro-Sul.

- **Rotação atual:** milho (semeado entre maio e junho, colhido em setembro), pousio de outubro a abril.
- **Irrigação:** não tem.
- **Prioridades:** renda alta; solo e água médios.
- **Mercado:** milho para granjas e fábricas de ração da região; venda de palha e silagem para vizinhos com gado.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **ZARC (milho)** | Para solo de água disponível média e ciclo precoce, janela de 20% do segundo decêndio de abril ao fim de maio. Primeira quinzena de junho com 30%. |
| **ZARC (milho + braquiária)** | Janela parecida para o consórcio no município. |
| HLS | Semeadura depois de 10 de junho em 3 dos últimos 5 anos. |
| GPM IMERG / CEMADEN | Chuva começa a firmar no fim de abril; acaba cedo em agosto em 4 de 10 anos. |
| GLDAS / SMAP L4 | Nos anos de semeadura tardia, a zona das raízes já estava seca no enchimento de grãos, em agosto. |
| IBGE PAM | Rendimento municipal do milho muito variável, com 3 anos ruins em 10. |
| SRTM | Talhão com 5–7% de declividade. |
| NASA POWER | Sol forte e solo descoberto de outubro a março. |

### Onde os dados se completam

**O atraso custa caro.** O ZARC diz que a janela de menor risco termina em maio. O HLS mostra plantios em junho em 3 de 5 anos. O GLDAS e o SMAP L4 mostram que, nesses anos, a água acabou no enchimento de grãos. A PAM confirma anos ruins no município. As fontes vêm de métodos diferentes, então a confiança é **alta**.

**O pousio expõe o solo ao sol e às primeiras chuvas.** Seis meses de solo nu, com declividade e chuva forte em abril, levam a erosão. O ZARC tem janela para o consórcio de milho com braquiária, então a cobertura não exige mudar o calendário.

### Regras ativadas

- **Semeadura real fora da janela de 20% do ZARC** aumenta o peso de estratégias que antecipam a semeadura.
- **Solo descoberto longo com declividade** aumenta o peso das culturas de cobertura.
- **Cultura de cobertura com janela própria no ZARC** permite sugerir o consórcio sem aumentar o risco.

### Comparação das estratégias

| Critério | A: atual (milho semeado até junho → pousio) | B: milho semeado até o fim de maio → pousio | C: milho + braquiária semeados até o fim de maio |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●●○○ |
| Solo | ●○○○○ | ●○○○○ | ●●●●○ |
| Nitrogênio | ●●○○○ | ●●○○○ | ●●○○○ |
| Erosão | ●○○○○ | ●○○○○ | ●●●●○ |
| Forragem | ●○○○○ | ●○○○○ | ●●●●○ |
| Renda | ●●●○○ | ●●●●○ | ●●●●○ |

Com os pesos do Sr. Edvaldo (renda alta, solo e água médios), a **estratégia C** fica em primeiro. Ela empata com a B em renda e água e ganha com folga em solo. A B já melhora a renda só por respeitar a janela.

### Cartão da estratégia C

> **Resumo:** uma opção é semear o milho até o fim de maio, dentro da janela de menor risco do ZARC, junto com braquiária para cobrir o solo depois da colheita.
>
> **Por que foi sugerida:** em 3 dos últimos 5 anos o seu milho foi semeado em junho, fora da janela de 20% do ZARC, e nesses anos a água acabou no enchimento de grãos. Depois da colheita, o solo fica 6 meses descoberto.
>
> **Evidências:** janela de semeadura (ZARC, referência oficial); data real de plantio (HLS, confiança alta); falta de água em agosto (GLDAS e SMAP L4, confiança média por ser escala regional); anos ruins no município (IBGE PAM, confiança média); declividade (SRTM, confiança alta).
>
> **Benefícios:** menos anos com perda, semeadura dentro da janela que conta para o seguro e solo coberto até as chuvas de abril, com palha e pasto para vender.
>
> **Lacunas:** não sabemos o tipo de solo da sua lavoura no critério do ZARC nem o ciclo da cultivar que você usa. Os dois mudam a janela.
>
> **Riscos para revisão local:** semear em abril depende de a chuva firmar; confirmar a umidade do solo antes. Ajustar com o agrônomo a dose de braquiária para não competir com o milho e conferir as regras do seguro.

## Conclusão

O ZARC é a **régua oficial** da ferramenta. Os dados da NASA mostram o que aconteceu no talhão e por quê; o ZARC diz se a data escolhida estava dentro do risco aceito. Juntos, eles transformam a ideia de semear mais cedo numa evidência que o produtor, o agrônomo e o banco reconhecem. Num caso do Centro-Sul, a mesma regra trabalharia com a janela da safrinha em fevereiro, e não com o milho de maio do Nordeste.

## Limitações

- **Uma cultura por vez:** o ZARC não avalia a sequência; a ferramenta precisa juntar as janelas.
- **Escala municipal:** baixadas, encostas e solos diferentes no mesmo município têm risco diferente.
- **Depende do solo e do ciclo declarados:** se o produtor não sabe, a ferramenta mostra a faixa de janelas.
- **É simulação:** usa séries de estações e um modelo de balanço hídrico; não é observação do ano.
- **Não é independente das estações:** as séries da ANA e do INMET entram no cálculo.
- **Muda por safra:** as portarias são revistas; a versão usada deve aparecer no cartão.
- **Tratamento:** guardar a safra da portaria, mostrar as janelas por solo e ciclo, comparar com HLS, GLDAS e SMAP L4 e pedir ao produtor o tipo de solo e a cultivar.
