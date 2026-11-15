# Motor de análise

> O coração do sistema. Não é um algoritmo, são **três cálculos**, cada um com uma técnica. Todos são regras e contas transparentes; a IA não participa dos números.

| # | O que calcula | Técnica | Usa peso? |
|---|---|---|---|
| 1 | **Perfil** do produtor (A, B, C) e papel | Regras simples | Não |
| 2 | **Retrato do solo** (drenagem, textura, matéria orgânica, compactação, erosão) | Fusão de evidências | Sim, **peso por fonte** |
| 3 | **Match das rotações** | Filtro + pontuação por critério (análise multicritério) | Sim, **peso pelas prioridades do produtor** |

As perguntas não têm peso fixo. Cada resposta vira uma evidência sobre um atributo do solo (cálculo 2), e os pesos da comparação vêm das prioridades que o próprio produtor escolheu (cálculo 3).

---

## Cálculo 1: perfil

O perfil é o **nível de dado sobre o solo** (A, B ou C). Quem respondeu fica num campo separado, o **papel** (`produtor` ou `tecnico`, pela pergunta 1), que só muda o nível de detalhe da tela.

- **C** se a pergunta 12 = "sim", tem o resultado em mãos **e** informou pelo menos 2 valores do laudo.
- **B** se respondeu a textura (13) **ou** pelo menos 5 das 8 perguntas de **observação** do solo sem "não sei" (13 a 18, 20 e a 19, que vale uma quando tem cor e jeito). As perguntas de manejo (12, 21 e 22) não contam.
- **A** nos demais casos.

Modificadores: irrigação (pergunta 6) e criação de animais (pergunta 4).

---

## Cálculo 2: retrato do solo (fusão de evidências)

Cada atributo do solo recebe evidências de várias fontes, e cada fonte tem um peso de confiança.

| Fonte | Peso (proposta inicial) |
|---|---|
| Laudo de laboratório | 0,9 |
| Teste de campo guiado | 0,7 |
| Observação do produtor (perguntas 14–19) | 0,5 |
| SoilGrids (modelo global, 250 m) | 0,4 |
| "Não sei" | 0 (não gera evidência, só registra a lacuna) |

**Exemplo: drenagem**

| Evidência | Diz | Peso |
|---|---|---|
| P14 "A água empoça mais de um dia?" → Sim | ruim | 0,5 |
| P19 figuras → cinza × gruda | ruim | 0,5 |
| SoilGrids: 45 % de argila | moderada | 0,4 |

Votos: ruim = 1,0 contra moderada = 0,4. Resultado: **drenagem ruim, confiança média**. Como o SoilGrids discorda, o app mostra: *"O mapa global sugere drenagem moderada, mas você observou água empoçada. No seu campo vale o que você vê."*

---

## Cálculo 3: match das rotações

```
[Gerar candidatas] → [Filtro: elimina o inviável] → [Pontuar por critério] → [Peso das prioridades] → atual + 2 melhores
```

**a) Gerar candidatas** (regras sobre a base de culturas):
- Preencher a janela em que o campo fica vazio com planta de cobertura ou cultura comercial que caiba no clima daqueles meses.
- Trocar a cultura principal por uma mais tolerante à seca.
- Incluir uma leguminosa (fixa nitrogênio e quebra o ciclo de pragas).
- A rotação atual entra sempre, como base de comparação.

**b) Filtro (elimina o inviável):**
- A cultura não completa o ciclo na janela (graus-dia).
- Risco de geada alto em fase sensível.
- Precisa de mais água do que a chuva e a irrigação dão.
- Cultura excluída (26a), falta de equipamento (26b), drenagem incompatível (cálculo 2).

**c) Pontuar cada critério de 0 a 1:**

| Critério | Cálculo (simplificado) |
|---|---|
| Economizar água | 1 − (demanda de água das culturas ÷ chuva disponível) |
| Melhorar a terra | Meses com cobertura + biomassa + fixação de nitrogênio |
| Evitar erosão | Cobertura **nos meses de chuva forte** × declividade |
| Menos praga | Alternância de famílias botânicas |
| Renda extra | Culturas comerciais a mais |
| Comida pros animais | Valor forrageiro |

**d) Peso das prioridades** (pergunta 25, até 3 escolhas): 1ª = 0,5, 2ª = 0,3, 3ª = 0,2. Os critérios não escolhidos recebem um peso pequeno para não sumirem. *(Proposta inicial.)*

**Exemplo.** Prioridades: água (0,5), terra (0,3), erosão (0,2).

| | Água | Terra | Erosão | **Nota** |
|---|---|---|---|---|
| A) Atual: milho → parado | 0,6 | 0,2 | 0,2 | 0,30 + 0,06 + 0,04 = **0,40** |
| B) Milho → cobertura | 0,5 | 0,8 | 0,9 | 0,25 + 0,24 + 0,18 = **0,67** |
| C) Sorgo → feijão | 0,8 | 0,6 | 0,6 | 0,40 + 0,18 + 0,12 = **0,70** |

Toda nota se decompõe até o dado de origem. É daí que saem os blocos "por que foi sugerida" e "evidência" que o desafio exige.

---

## Cenários

Um cenário é **o motor rodando com outra entrada**, não um serviço separado.

| Tipo | O que muda | Exemplo |
|---|---|---|
| Clima | Ajuste nas séries climáticas | Chuva −20 %, temperatura +2 °C |
| Rotação | Calendário alternativo | "E se eu plantar sorgo em vez de milho?" |
| Recursos | Restrições | "E se eu tiver irrigação em parte do campo?" |

Cada cenário é salvo e aparece no dashboard e no chat. Deixar claro que é um **teste de sensibilidade, não uma previsão**.

---

## Por que não aprendizado de máquina

Não existe base de dados com o resultado de rotações reais para treinar um modelo, e ele seria uma caixa-preta. A IA fica onde é útil: entender o texto livre e reescrever as explicações em linguagem simples, sem mexer nos números.
