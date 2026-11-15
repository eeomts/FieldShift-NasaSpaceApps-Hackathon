# Relatório: revisão do questionário de onboarding

> 14/11/2026 · Pessoa 3 (conteúdo para o produtor)
>
> O time propôs uma versão nova do questionário: 23 perguntas em 6 partes, com algumas perguntas agrupadas na mesma tela. Este relatório compara essa versão com o que o app já faz (`agroai/api/app/schemas/onboarding.py`, `agroai/api/app/services/onboarding/perfil.py`, `agroai/web/src/onboarding/Passos.tsx`) e com os roteiros de teste do chat (`TESTES_CHAT_SR_JOSE.md` e `TESTES_CHAT_SR_SMITH.md`).
>
> **Resultado:** a versão foi aplicada no `data/onboarding/perguntas.yaml`. **4 pontos não funcionavam** e foram corrigidos antes de entrar; as demais mudanças entraram como propostas.

## Resumo

| # | Pergunta | O que não funcionava | Como ficou no `perguntas.yaml` |
|---|---|---|---|
| 1 | 20 (perdas) | Regras de exibição de **geada** e **salinidade** escondiam ou mostravam a pergunta no lugar errado | Geada some só onde o histórico nunca teve frio de geada; salinidade só em clima seco ou com irrigação em clima mediterrâneo |
| 2 | 14 (sinais do solo) | Múltipla escolha **perde o "não"** de cada sinal e quebra a regra do perfil B | **Grade** na mesma tela: uma linha por sinal, com Sim / Não / Não sei |
| 3 | 20 (perdas) | **Um ano só** para todos os eventos marcados | **Um seletor de ano ao lado de cada evento** marcado |
| 4 | 15 (cor) | "Cinza" perdeu "**ou com manchas cinza**" | Rótulo voltou a ser "Cinza ou com manchas cinza" |

---

## 1. Regras de exibição da pergunta 20 (geada e salinidade)

**Versão proposta**
- "Ocultar geada em climas tropicais e áridos quentes."
- "Exibir salinidade somente em zona climática B ou quando houver irrigação."

**Por que não funciona**
- **Geada:** clima árido quente (zonas Köppen BWh e BSh) **também tem geada**. O Vale Central da Califórnia, área de amêndoa e citros, perde safra por geada, e o deserto do Arizona tem noites abaixo de zero. Com a regra proposta, o produtor dessas regiões nem vê a opção. *(TESTES_CHAT_SR_SMITH.md, teste 6.)*
- **Salinidade:** a **irrigação sozinha não indica sal no solo**. Um pivô em clima úmido (Nebraska) ou um arrozal no Delta do Arkansas não têm problema de sal, mas veriam a opção. *(TESTES_CHAT_SR_SMITH.md, testes 4 e 8.)*

**Como ficou**
- **Geada:** aparece se o histórico do NASA POWER do ponto tiver **pelo menos uma noite abaixo de 2 °C**, o mesmo limite do indicador de risco de geada. Se o POWER ainda não tiver chegado, some só em clima tropical (zona A).
- **Salinidade:** aparece em clima seco (zona B) **ou** com irrigação em clima mediterrâneo (Csa/Csb, verão sem chuva).
- A mesma lógica vale para a ordem da pergunta 17: o **gesso** aparece antes do calcário só em clima seco (zona B ou Csa/Csb).

Conferido em 11 locais (EUA e Brasil): a geada aparece em Fresno, Lubbock e Passo Fundo e some em Belém e Petrolina; o sal não aparece mais no pivô do Nebraska nem no arroz do Arkansas.

## 2. Pergunta 14: sinais do solo em múltipla escolha

**Versão proposta:** "Quais destas situações você já percebeu no seu solo?", com 5 situações, "Nenhuma dessas situações" e "Não sei", podendo marcar várias.

**Por que não funciona**
1. **"Não marcado" fica ambíguo.** Se o produtor não marca "água empoçada", pode ser "não acontece" ou "não sei". Para o app são coisas diferentes: "não" vira evidência de **drenagem boa** no retrato do solo, e "não sei" não vira evidência nenhuma.
2. **Quebra a regra do perfil B.** O `perfil.py` dá o perfil B quando o produtor responde **pelo menos 5 das 8 observações do solo sem "não sei"** (pergunta 13, os 5 sinais, a pergunta 16 e a 15). Com um "Não sei" só para tudo, a contagem não funciona.
3. **"Encontro minhocas" é um sinal bom no meio de 4 problemas.** Quem marca "Nenhuma dessas situações" estaria dizendo também que não encontra minhoca, que é um sinal ruim e provavelmente não o que ele quis dizer.

**Como ficou:** os 5 sinais continuam **na mesma tela**, mas numa **grade**: uma linha por sinal, com **Sim / Não / Não sei** em cada uma. A grade tem um botão "Não sei responder nenhuma", que marca "Não sei" em todas de uma vez. O sinal bom (minhocas) fica na última linha, com destaque diferente. Cada linha continua gravando o seu campo no app (`q14_encharca` a `q18_minhocas`), então **a regra do perfil B e o retrato do solo não mudam**.

## 3. Pergunta 20: um ano só para todas as perdas

**Versão proposta:** "Se selecionar algum evento, perguntar uma única vez: 'Lembra mais ou menos em que ano aconteceu?'"

**Por que não funciona:** o app procura **cada evento no dado da NASA daquele ano**: geada na temperatura mínima, seca na falta de água, chuva forte na chuva extrema. Se o produtor marca geada e seca e dá um ano só, não dá para saber a qual evento o ano pertence, e o app confere o evento errado no ano errado.

**Como ficou:** continua uma pergunta só, de múltipla escolha, mas **cada evento marcado ganha o seu seletor de ano** ao lado, com a opção "Não lembro". O app recebe `q24_perdas.<evento>.ano` separado para cada um, como já espera hoje.

**Regra adotada para os eventos não marcados:** se o produtor marcou algum evento, os que ele não marcou contam como "não". "Nunca perdi uma safra por esses motivos" grava "não" em todos, e "Não sei" grava "não sei" em todos. Aqui a ambiguidade do item 2 é menor, porque a pergunta pede uma lista do que aconteceu; mesmo assim, vale o time confirmar.

## 4. Pergunta 15: cor "Cinza"

**Versão proposta:** "Cinza."

**Por que não funciona:** a opção existe para detectar **terra que fica encharcada**, e o sinal disso no solo é justamente a **mancha cinza** no meio de outra cor (mosqueado). Muitos solos que encharcam não são inteiros cinza, só manchados. Sem o "ou com manchas cinza", o produtor que vê manchas não se reconhece na opção.

**Como ficou:** "Cinza ou com manchas cinza" (inglês: "Gray, or gray-mottled").

---

## Mudanças da versão proposta que entraram como estavam

| Pergunta | Mudança |
|---|---|
| Todas | Numeração de 1 a 23 em 6 partes ("Quem é você?", "Sua propriedade", "O que você planta?", "Conhecendo seu solo", "Clima e perdas de safra", "Suas prioridades") |
| 2, 3, 6, 9, 13, 16, 18, 19, 21, 23 | Textos novos (ex.: "Nos períodos sem plantio, a terra fica descoberta?", "Sim, toda a propriedade") |
| 15 | Cor e aparência ao toque na mesma tela, em dois grupos |
| 17 | "Nunca fiz" no lugar de "Não" e **campo para escrever** ao marcar "Outra correção" (campo novo `q21_correcao_outra`) |
| 23 | Equipamentos viram etiquetas removíveis e podem ser adicionados por uma lista |
| Resumo final | Perfil, calendário anual, retrato do solo, até 3 próximos passos e o botão "Ver minha fazenda" |

O que já tinha sido ajustado antes e continua valendo: a ajuda sobre neve na pergunta 9 (clima com inverno de neve), hectare ou acre na pergunta 2 conforme o país e o inglês americano.

## Ajustes para acompanhar o app atual

Ao comparar com o código, apareceram mudanças recentes do app que o YAML ainda não tinha:

| Ponto | O que mudou no app | Como ficou no YAML |
|---|---|---|
| Pergunta 1 | "Técnico" **não é mais o perfil D**: virou o papel de quem responde (`calcula_papel`). Os perfis agora são A, B e C. | Pergunta 1 alimenta o `papel`, não o perfil |
| Perfil C | Exige **pelo menos 2 valores do laudo** (`MIN_VALORES_LAUDO_C = 2`), não basta dizer que tem o resultado | Entrou o `q12_laudo` (pH, argila, matéria orgânica, P, K, CTC, V%), que aparece quando o produtor diz que tem o resultado |
| Caminhos | O código foi reorganizado em camadas | O cabeçalho do YAML aponta para `schemas/onboarding.py` e `services/onboarding/perfil.py` |

**Atenção ao resumo final da versão proposta:** ele fala em "Perfil da propriedade (A–D)". Pelo app atual, o perfil vai de **A a C**, e o "técnico" aparece à parte, como papel.

## Observações (não bloqueiam)

- **Unidades do laudo:** os campos usam as unidades dos laudos brasileiros (mg/dm³, g/dm³, cmolc/dm³). Laudos dos EUA costumam vir em **ppm** e com matéria orgânica em **%**. A CTC em meq/100 g tem o mesmo número que cmolc/dm³. Vale uma ajuda por país quando o app atender fora do Brasil.
- **Perguntas 8 e 22 (culturas):** seguem em espera até a nova base de culturas.

## O que o código precisa fazer para seguir esta versão

Nada disso foi feito neste trabalho, que mexeu só em arquivos de `data/`:

1. **Pergunta 14:** tela em grade (5 linhas Sim / Não / Não sei + botão "Não sei responder nenhuma"). Os campos do schema não mudam.
2. **Pergunta 20:** tela de múltipla escolha com ano por evento, gravando nos campos `Perdas` que já existem. `Perdas` ganha `alagamento`, `granizo` e `salinidade`.
3. **Pergunta 17:** `q21_calcario` (sim/não) vira `q21_correcao` (lista), mais o campo de texto `q21_correcao_outra`. O `perfil.py` não usa a 17 nas regras de perfil, então o perfil não muda.
4. **Pergunta 5:** `Local` ganha `pais`, `zona_climatica` e `hemisferio`, que as regras das perguntas 2, 9, 17 e 20 usam.
5. **Regras por local** (perguntas 9, 17 e 20), como descritas acima.
