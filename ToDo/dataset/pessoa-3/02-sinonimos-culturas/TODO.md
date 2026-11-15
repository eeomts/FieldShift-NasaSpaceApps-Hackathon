# 02 — Sinônimos e nomes regionais das culturas

**Dono:** Pessoa 3 · **Status:** feito

## Por quê
Quando o produtor escreve "planto macaxeira e um capim pras vacas", a IA (ou a lista reserva, se a IA cair) casa cada palavra com uma cultura da base. Nome regional que não está na lista vira "não encontrado".

## Onde
Campo `nomes` de cada cultura em `agroia/base/culturas.json` (o arquivo é do app: mude **por PR** e avise o Pedro).

```json
{"id": "mandioca", "nomes": {"pt": ["mandioca", "macaxeira", "aipim", "maniva"], "en": ["cassava"]}}
```

## O que fazer
1. Para as 17 culturas do motor (lista em `data/catalogo/culturas.csv`), revise os nomes em PT e acrescente os regionais que faltam (Nordeste, Norte, Sul…).
2. Confira que cada uma tem pelo menos 1 nome em EN. O app tem só português e inglês: sem nomes em espanhol.
3. Inclua erros comuns de escrita quando forem frequentes ("mio", "fejão").
4. **Não use o mesmo nome em duas culturas** (ex.: "capim" já está em `pastagem`).

## Pronto quando
- [x] As 17 culturas revisadas (e as 7 que só estão no catálogo dos EUA).
- [x] Nenhum nome repetido entre culturas.
- [ ] Os testes da API continuam passando (`agroia/api/tests/test_interpretar.py`): peça ajuda ao backend para rodar.

## Fechamento (15/11/2026)
- Entregue a proposta em `data/catalogo/cultura_sinonimos.md`: 48 nomes novos em PT e EN (41 para as 17 culturas do motor e 7 para culturas que só estão no catálogo dos EUA), conferidos por script com a normalização do app, sem colisão.
- Decisão da Pessoa 3: só português e inglês. A proposta pede tirar a lista `"es"` das 42 culturas do `culturas.json`.
- Aplicar a proposta no `agroia/base/culturas.json` e rodar os testes da API é código: fica para o PR do app (passo a passo no próprio `cultura_sinonimos.md`). Por isso o item dos testes continua aberto.
