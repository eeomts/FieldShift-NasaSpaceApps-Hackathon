# 02 — Sinônimos e nomes regionais das culturas

**Dono:** Pessoa 3 · **Status:** pendente

## Por quê
Quando o produtor escreve "planto macaxeira e um capim pras vacas", a IA (ou a lista reserva, se a IA cair) casa cada palavra com uma cultura da base. Nome regional que não está na lista vira "não encontrado".

## Onde
Campo `nomes` de cada cultura em `agroia/base/culturas.json` (o arquivo é do app: mude **por PR** e avise o Pedro).

```json
{"id": "mandioca", "nomes": {"pt": ["mandioca", "macaxeira", "aipim", "maniva"], "en": ["cassava"], "es": ["yuca"]}}
```

## O que fazer
1. Para as 16 culturas do motor (lista em `data/catalogo/culturas.csv`), revise os nomes em PT e acrescente os regionais que faltam (Nordeste, Norte, Sul…).
2. Confira que cada uma tem pelo menos 1 nome em EN e 1 em ES.
3. Inclua erros comuns de escrita quando forem frequentes ("mio", "fejão").
4. **Não use o mesmo nome em duas culturas** (ex.: "capim" já está em `pastagem`).

## Pronto quando
- [ ] As 16 culturas revisadas.
- [ ] Nenhum nome repetido entre culturas.
- [ ] Os testes da API continuam passando (`agroia/api/tests/test_interpretar.py`): peça ajuda ao backend para rodar.
