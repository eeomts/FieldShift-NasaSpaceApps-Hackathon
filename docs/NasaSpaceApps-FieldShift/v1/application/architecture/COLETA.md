# 1. Coleta — onboarding e análise do produtor

> A coleta é o **onboarding**: coletar as informações do produtor e analisá-lo. A saída é a **ficha do produtor**, a entrada de todo o resto do app. As perguntas estão em [`../ONBOARDING.md`](../ONBOARDING.md).

## 1a. Coletar

| Tipo de resposta | Perguntas | Tratamento |
|---|---|---|
| Escolha fechada (sim / não / não sei, faixas, figuras) | A maioria | Gravada direto |
| Texto livre | 8 (o que planta), 26a (o que não plantaria), 26b (equipamentos) | IA separa em itens → casa com a base → o produtor confirma um por um |
| Local | 5 | Ponto no mapa ou GPS |

### A busca de dados começa no meio do questionário

Assim que o produtor marca o local (pergunta 5, bloco 2), o sistema **dispara a integração de dados externos em segundo plano** (ver [INTEGRACAO-DE-DADOS.md](INTEGRACAO-DE-DADOS.md)). Enquanto ele responde os blocos 3 a 6, os dados vão chegando. Quando ele termina, a análise fica pronta quase na hora.

### Componente de texto livre (IA)

As perguntas 8, 26a e 26b usam o mesmo componente:

```
texto livre → IA extrai uma lista estruturada (JSON validado) → casa com a base → o produtor confirma
```

- A IA só devolve itens que **existem na base** ou marcados como "não encontrado".
- Cada item vem com confiança; os de confiança baixa são perguntados primeiro.
- O texto original é sempre guardado junto.
- Se a IA estiver fora do ar, o produtor escolhe numa lista com ícones.

## 1b. Analisar o produtor (a ficha)

| Parte da ficha | De onde vem | Como é calculada |
|---|---|---|
| **Perfil** (A, B, C) + papel + modificadores | Perguntas 1, 3, 4, 6, 12, 13 | Regras simples (ver [MOTOR-DE-ANALISE.md](MOTOR-DE-ANALISE.md#cálculo-1-perfil)) |
| **Calendário atual** | Pergunta 8 confirmada, 10 e 11 | Meses ocupados, consórcios e meses descobertos |
| **Retrato do solo** | Perguntas 13–22 + SoilGrids + SRTM | Fusão de evidências com peso por fonte |
| **Histórico de perdas × dados** | Perguntas 23–24 + NASA POWER | Procura o evento no ano informado; confirma ou registra a diferença |
| **Prioridades e restrições** | Perguntas 25, 26a, 26b | Viram os pesos e os filtros da comparação de estratégias |
| **Lacunas e próximos passos** | Todo "não sei" | Lista do que falta e do teste simples que ajudaria |

A ficha fica no banco e **pode ser atualizada depois**: quando o produtor faz um teste de campo, traz um laudo ou corrige algo pelo chat.
