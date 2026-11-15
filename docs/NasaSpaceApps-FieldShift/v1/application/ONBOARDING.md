# Onboarding — questionário do primeiro acesso

> Versão fechada em 14/11/2026. Define o que o produtor responde no primeiro acesso, para que serve cada resposta e onde entra IA.

## Objetivo

O questionário faz duas coisas ao mesmo tempo:

1. **Descobre o perfil do produtor** (A, B ou C), quem está respondendo (produtor ou técnico) e quanto ele sabe do próprio solo.
2. **Coleta o mínimo para a análise funcionar**: local, o que planta e quando, sinais do solo, histórico de perdas e prioridades.

## Regras de desenho

- No máximo **5 minutos**, cerca de 20 a 30 toques. Funciona no celular.
- Toda pergunta fechada tem **Sim / Não / Não sei**. "Não sei" também é informação: marca onde a confiança é baixa.
- Usar figuras sempre que a pergunta for visual (terreno, terra).
- Dá para pular e voltar depois. O técnico pode preencher junto com o produtor.
- **A IA nunca decide sozinha.** Ela interpreta o texto livre e o produtor sempre confirma (ver "Uso de IA").

---

## Perfis de produtor

| Perfil | Quem é | Dado de solo | O que o app faz |
|---|---|---|---|
| **A: Experiência** | Pequeno, sem irrigação, sem técnico frequente | Só observação | Usa dados globais e as respostas do questionário. Sugere testes simples para subir a confiança |
| **B: Observador** | Pequeno ou médio; já fez algum teste ou sabe a textura | Observação e teste de campo | Combina o que ele informa com os dados globais |
| **C: Com laudo** | Médio, tem técnico, faz análise a cada 2–3 anos | Laudo de laboratório | Os valores do laudo substituem os modelados. Confiança mais alta |

**Papel** (quem respondeu), separado do perfil: `produtor` ou `tecnico` (pergunta 1). Um técnico da extensão também tem um perfil A, B ou C, conforme o que se sabe do solo daquele campo; o papel só muda o nível de detalhe técnico na tela. *(Antes existia um perfil "D: Técnico", que misturava as duas coisas e apagava a informação do laudo.)*

**Modificadores** (mudam prioridades e culturas possíveis, não o perfil): irrigação e criação de animais.

**Regra inicial de classificação:**
- **Papel:** `tecnico` se a pergunta 1 = "técnico"; senão `produtor`.
- **C** se a pergunta 12 = "sim", tem o resultado em mãos **e** informou pelo menos 2 valores do laudo. Só dizer que tem o laudo não basta: sem números, o app sugere digitá-los como próximo passo.
- **B** se respondeu a textura (13) **ou** pelo menos 5 das 8 perguntas de **observação** do solo sem "não sei" (13 a 18, 20 e a 19, que vale uma quando tem cor e jeito). As perguntas de manejo (12, 21 e 22) não contam: "nunca usei calcário" não diz nada sobre como o solo é.
- **A** nos demais casos.

---

## Bloco 1: Quem é você

| # | Pergunta | Respostas | Para quê |
|---|---|---|---|
| 1 | Quem está respondendo? | Sou o produtor / Sou técnico ou ajudo um produtor | Perfil D; nível de detalhe da tela |
| 2 | Tamanho aproximado da área | Faixas (sem número exato) | Escala; tipo de recomendação |
| 3 | Você recebe visita de técnico agrícola? | Sim / Às vezes / Não | Linguagem e próximo passo sugerido |
| 4 | Tem criação de animais? | Sim / Não | Modificador: valoriza forragem |

## Bloco 2: O campo

| # | Pergunta | Respostas | Para quê |
|---|---|---|---|
| 5 | Onde fica o campo? | Toque no mapa ou GPS | Chave para todos os dados globais |
| 6 | Tem irrigação? | Sim / Só em parte / Não | Modificador: balanço de água e culturas possíveis |
| 7 | Como é o terreno? | Figuras: plano / levemente inclinado / bem inclinado | Erosão. Cruza com a declividade do SRTM |

## Bloco 3: O que você planta

### 8. Descrição livre, separada pela IA e confirmada cultura por cultura

**Passo 8a — o produtor escreve do jeito dele:**
> "Conte rapidinho o que você planta e em que época."
> *Ex.: "planto milho e feijão juntos na época das águas, depois mandioca, e tem um pedaço de capim pras vacas"*

**Passo 8b — a IA separa as culturas.** Ela devolve uma lista estruturada:

```json
[
  { "texto_original": "milho", "cultura_id": "milho", "inicio_mes": 10, "fim_mes": 2, "consorcio_com": ["feijao"], "confianca": "alta" },
  { "texto_original": "feijão", "cultura_id": "feijao", "inicio_mes": 10, "fim_mes": 1, "consorcio_com": ["milho"], "confianca": "alta" },
  { "texto_original": "mandioca", "cultura_id": "mandioca", "inicio_mes": null, "fim_mes": null, "confianca": "media" },
  { "texto_original": "capim pras vacas", "cultura_id": "pastagem", "inicio_mes": 1, "fim_mes": 12, "perene": true, "confianca": "media" }
]
```

**Passo 8c — confirmação uma cultura por vez.** Cada cultura aparece num cartão próprio:
1. "Você planta **milho**?" → confirmar, trocar ou remover.
2. "De que mês a que mês?" → régua de 12 meses, já preenchida com o palpite da IA.
3. Só se a IA detectou consórcio: "O milho é plantado **junto** com o feijão?" → Sim / Não.
4. Opcional: "Ocupa o campo todo ou uma parte?" → Todo / Parte.

Depois de todos os cartões, aparece o **calendário completo** do ano para uma última conferência. Os meses vazios ficam destacados: "Nesses meses o campo fica sem nada?"

**Casos que a IA precisa tratar:**

| Caso | Exemplo | Como tratar |
|---|---|---|
| Várias culturas na mesma frase | "milho e feijão" | Um cartão por cultura |
| Consórcio (juntas no mesmo campo) | "milho com feijão junto" | Marcar `consorcio_com` e confirmar |
| Mesma cultura duas vezes no ano | "feijão das águas e feijão da seca" | Dois cartões com períodos diferentes |
| Cultura perene | café, capim, frutíferas | Marcar perene: ocupa o ano todo, sem rotação clássica |
| Nome local ou regional | macaxeira = aipim = mandioca; *cassava* | Base de culturas com sinônimos em português e inglês |
| Cultura fora da nossa base | uma planta que não temos cadastrada | Manter o nome e marcar "sem parâmetros". Ela entra no calendário, mas não na pontuação |
| Época não informada | "planto mandioca" | Período vazio no cartão; o produtor preenche |
| Ciclo com mais de um ano | "rotação de 2 anos" | Fica para depois do MVP; registrar como lacuna |

| # | Pergunta | Respostas | Para quê |
|---|---|---|---|
| 10 | Depois da colheita, o que acontece com o campo? | Fica parado / Vira pasto / Planto outra coisa / Planto algo pra cobrir o solo | Meses sem cobertura e risco de erosão |
| 11 | Deixa a palha ou o resto da cultura no campo? | Sim / Não / Não sei | Cobertura do solo e matéria orgânica |

## Bloco 4: O que você sabe do seu solo

Respostas: **Sim / Não / Não sei**, exceto onde indicado.

| # | Pergunta | Para quê |
|---|---|---|
| 12 | Já fez análise de solo em laboratório? *(se sim: tem o resultado? de quando? se tem: os valores do laudo, todos opcionais: pH em água, argila %, matéria orgânica g/dm³, fósforo e potássio mg/dm³, CTC cmolc/dm³, saturação por bases %)* | Nível de dado; abre o caminho do laudo (perfil C). Os valores entram no retrato do solo com fonte "laudo" e confiança alta |
| 13 | A terra é mais arenosa, argilosa ou meio-termo? *(escolha + Não sei)* | Textura. Cruza com SoilGrids |
| 14 | Depois de chuva forte, a água fica empoçada mais de um dia? | Drenagem e infiltração |
| 15 | Quando seca, a terra forma uma casca na superfície? | Encrostamento |
| 16 | Já viu a chuva levando terra (valetas, água barrenta saindo do campo)? | Erosão |
| 17 | A terra fica muito dura pra cavar ou arar? | Compactação |
| 18 | Encontra minhocas quando cava? | Vida no solo |
| 19 | **Com qual figura a sua terra mais se parece?** *(duas rodadas, ver abaixo)* | Matéria orgânica, drenagem e textura (aproximadas) |
| 20 | Tem partes do campo onde a lavoura sempre vai pior? | Variação dentro do campo |
| 21 | Já usou calcário? | Acidez conhecida e manejada |
| 22 | Usa adubo ou esterco? | Manejo de fertilidade |

### 19. Duas rodadas de figuras, cruzadas

**Rodada 1, a cor** ("Com qual figura sua terra mais se parece?"):

| Figura | Cor | O que costuma indicar |
|---|---|---|
| 1 | Preta ou marrom bem escura | Mais matéria orgânica |
| 2 | Marrom | Matéria orgânica média |
| 3 | Vermelha | Ferro oxidado; geralmente bem drenada |
| 4 | Amarelada | Ferro hidratado; drenagem um pouco menor |
| 5 | Cinza ou com manchas cinza | Fica encharcada com frequência |
| 6 | Clara ou esbranquiçada | Pouca matéria orgânica; pode ser arenosa ou lavada |

**Rodada 2, o jeito na mão** ("E quando você pega um punhado, ela parece mais com qual?"):

| Figura | Aspecto | O que costuma indicar |
|---|---|---|
| 1 | Solta, escorre entre os dedos | Arenosa; retém pouca água |
| 2 | Fofa, em grumos pequenos | Boa estrutura, boa vida no solo |
| 3 | Gruda e molda quando molhada | Argilosa |
| 4 | Torrões duros que não se desfazem | Compactada ou adensada |
| 5 | Racha quando seca | Argila expansiva |
| 6 | Com muitas pedras ou cascalho | Pedregosa; raiz e máquina têm limite |

**O cruzamento** dá uma estimativa melhor do que cada rodada sozinha. Exemplos:

| Cor × jeito | Leitura provável | Confiança |
|---|---|---|
| Escura × fofa | Matéria orgânica boa, estrutura boa | Média |
| Vermelha × gruda | Argilosa e bem drenada | Média |
| Cinza × gruda | Argilosa com drenagem ruim; cuidado com culturas sensíveis a encharcamento | Média |
| Clara × solta | Arenosa, pouca matéria orgânica, seca rápido | Média |
| Escura × solta | Combinação incomum; pedir confirmação ou sugerir teste do tato | Baixa |

> **Cuidado:** cor e aspecto são indícios, não análise. O app trata o resultado como "informado pelo produtor", com confiança média ou baixa. Quando ele discorda do SoilGrids, o app mostra os dois e sugere um teste simples. As figuras precisam ser fotos reais de solos de vários continentes, não ilustrações. As faixas de leitura acima são preliminares **[verificar com referência de pedologia]**.

## Bloco 5: O que você tem sentido no clima

Respostas: **Sim / Não / Não sei**.

| # | Pergunta | Para quê |
|---|---|---|
| 23 | Sente que a chuva mudou nos últimos anos? | Percepção. O app compara com a tendência de chuva |
| 24a | Já perdeu safra por **geada**? | Cruza com Tmin (POWER) |
| 24b | Já perdeu safra por **chuva forte**? | Cruza com chuva extrema (POWER/IMERG) |
| 24c | Já perdeu safra por **calor intenso**? | Cruza com Tmax e dias de calor (POWER) |
| 24d | Já perdeu safra por **falta de chuva**? | Cruza com déficit hídrico e seca (POWER, SMAP L4) |

**Opcional em cada "sim":** "Lembra mais ou menos o ano?" → seletor de ano ou "não lembro".

> **Por que isso importa:** com o ano em mãos, o app procura o evento nos dados da NASA e mostra ao produtor. Ex.: "Em 2021 o NASA POWER registrou 3 noites abaixo de 0 °C em julho no seu local." Se o dado confirma a memória dele, a confiança na ferramenta sobe. Se não confirma, isso também é informação: o pixel de ~50 km pode não ter captado o microclima do campo dele. Essa diferença deve aparecer como lacuna, nunca como "você está errado".

## Bloco 6: O que é importante pra você

| # | Pergunta | Respostas | Para quê |
|---|---|---|---|
| 25 | Escolha até 3 | Economizar água / Melhorar a terra / Evitar erosão / Renda extra / Comida pros animais / Menos praga | Pesos da comparação de estratégias |
| 26a | Tem alguma cultura que você **não** plantaria? Por quê? | Texto livre → IA compara com a **base de culturas** | Culturas excluídas e o motivo (mercado, costume, já deu errado) |
| 26b | Que máquinas e equipamentos você tem ou consegue usar? | Texto livre → IA compara com a **lista de equipamentos** | Restringe as culturas viáveis (plantio, colheita) |

**Como funcionam a 26a e a 26b:**
1. O produtor escreve livre. *Ex.: "não planto soja, não tenho onde vender"* / *"tenho trator pequeno e plantadeira, colheita é na mão"*
2. A IA casa cada item com a base (culturas com sinônimos; equipamentos em categorias como `trator`, `plantadeira_graos`, `colhedora`, `tracao_animal`, `manual`).
3. O app mostra o que entendeu em etiquetas: *"Não plantaria: soja (motivo: mercado)"* / *"Equipamentos: trator, plantadeira; colheita manual"*. O produtor confirma ou corrige.
4. O que não casar com a base fica guardado como texto e aparece como lacuna.

---

## Uso de IA no onboarding

As três perguntas de texto livre (**8, 26a e 26b**) usam **o mesmo componente**:

```
texto livre → IA extrai uma lista estruturada → casa com a base (culturas / equipamentos) → o produtor confirma item por item
```

**Regras do componente:**
- A IA só pode devolver itens que **existem na base** ou marcados como "não encontrado". Ela não inventa culturas nem parâmetros.
- Cada item vem com confiança. Os de confiança baixa são perguntados primeiro.
- O texto original é sempre guardado junto, para rastreabilidade.
- Se a IA estiver fora do ar, o produtor escolhe da lista com ícones. O app continua funcionando.

**Dependência:** a base de culturas precisa de **sinônimos e nomes locais em português e inglês** (PT e EN, os idiomas do app). Ela é a peça central do casamento.

---

## O que sai do questionário

1. **Perfil** (A, B ou C) + papel (produtor ou técnico) + modificadores (irrigação, animais).
2. **Calendário atual** confirmado: culturas, meses, consórcios e meses sem cobertura.
3. **Retrato do solo provisório**: cada resposta vira um indicador marcado como "informado pelo produtor", que o app cruza com SoilGrids, SRTM e NASA POWER. Quando concordam, a confiança sobe; quando discordam, o app mostra a diferença.
4. **Histórico de perdas**, com ano quando houver, para cruzar com os dados da NASA.
5. **Prioridades, culturas excluídas e equipamentos**: os pesos e as restrições da comparação de estratégias.
6. **Próximo passo sugerido** a partir dos "não sei". Ex.: não sabe a textura → teste do tato (2 minutos).

## Pendências

- Fotos reais de solo para as 12 figuras da pergunta 19, com origem e licença.
- Validar a tabela de cruzamento cor × jeito com uma referência de pedologia.
- Definir as faixas de tamanho de área da pergunta 2 de forma que sirvam em vários países.
- Montar a base de culturas com sinônimos e a lista de equipamentos.
- Escolher o modelo de IA e o formato de saída (JSON com esquema validado).
