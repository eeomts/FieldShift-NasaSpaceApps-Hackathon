# 2. Dashboard e 3. Chat + cenários

## 2. Dashboard

O que o produtor vê depois do onboarding.

| Seção | Conteúdo |
|---|---|
| **Seu perfil e seu solo** | Resumo da ficha, com a confiança e o que concorda ou discorda entre o produtor e os dados |
| **Raio-x do campo** | Cartões curtos (meses descobertos, geada, calor, chuva, erosão), cada um com **"de onde vem?"** e **"o que significa?"** |
| **Você disse × os dados mostram** | As perdas que ele relatou (perguntas 23–24) comparadas com o que a NASA registrou |
| **Comparar estratégias** | Atual + 2 lado a lado, semáforo por critério, selo de confiança |
| **Meus cenários** | Cenários salvos (do chat ou dos controles deslizantes) |
| **Próximos passos** | O que faria a confiança subir. Ex.: "Faça o teste do tato (2 min)" |

Aviso fixo na tela: *"Sugestões para conversar com seu técnico. A decisão é sua."*

---

## 3. Chat + cenários

O produtor conversa em linguagem natural. O modelo de linguagem usa **ferramentas** que consultam a ficha e o motor de análise. **Ele nunca calcula sozinho.**

### Ferramentas

| Ferramenta | Exemplo de pergunta |
|---|---|
| `ver_ficha` | "O que vocês sabem do meu campo?" |
| `consultar_indicador` | "Choveu menos esse ano que o normal?" |
| `comparar_estrategias` | "Qual gasta menos água, a B ou a C?" |
| `criar_cenario` | "E se faltar chuva em março?" / "E se eu plantar sorgo?" |
| `atualizar_ficha` | "Fiz o teste do pote, deu bastante argila" → atualiza o retrato do solo |
| `info_cultura` | "Feijão aguenta geada?" |
| `explicar_termo` | "O que é evapotranspiração?" |

### Regras

- Todo número vem de uma ferramenta, com fonte e período.
- Não prescreve: nada de "plante X" ou "aplique Y kg". Mostra opções e riscos.
- Responde no idioma do produtor.
- Se faltar dado, diz que falta, em vez de chutar.
- Um cenário criado no chat aparece no dashboard, e vice-versa.

### IA

API do Claude com uso de ferramentas (tool use), modelo `claude-opus-5-5`. O mesmo componente atende o texto livre do onboarding (perguntas 8, 26a e 26b), com saída em JSON validado. Usar um modelo mais barato em alguma parte é uma decisão de custo a medir depois.
