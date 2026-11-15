# 01 — Pontos da demo

**Dono:** Pessoa 2 · **Status:** em revisão (falta o time aprovar as regiões) · **Prioridade:** primeira (destrava o AppEEARS)

## Por quê
A apresentação mostra 2 ou 3 produtores concretos em regiões contrastantes, onde os mesmos dados levam a recomendações diferentes. Todos os dados lentos (NDVI, umidade) são pré-calculados para esses pontos.

## Saída: `data/demo/pontos_demo.csv` (o cabeçalho já existe)

| Coluna | Exemplo |
|---|---|
| `id` | `cerrado_1` |
| `regiao` | `Cerrado` |
| `municipio`, `uf` | `Rio Verde`, `GO` |
| `latitude`, `longitude` | `-17.80`, `-50.92` (decimal com ponto; sul e oeste negativos) |
| `rotacao_atual` | `soja (out–fev) \| milho safrinha (fev–jun) \| pousio (jul–set)` |
| `historia` | o "seu Antônio" desse ponto em 2 ou 3 frases |
| `soilgrids_ok` | `true` depois do teste abaixo |

## Passo a passo
1. Escolha com o time 2 ou 3 regiões contrastantes (sugestões em `context/DECISOES.md`, Q-01): Cerrado, Semiárido, Sul.
2. Para cada uma, um ponto **em lavoura, não em cidade**: confira no Google Maps (satélite).
3. Teste no SoilGrids (cole no navegador, trocando lat/lon). Se `mean` vier preenchido, `soilgrids_ok = true`:
   `https://rest.isric.org/soilgrids/v2.0/properties/query?lon=-50.92&lat=-17.80&property=clay&depth=0-5cm&value=mean`
4. Escreva a história e a rotação atual usando culturas da base (`agroai/base/culturas.json`).

## Pronto quando
- [ ] 2 ou 3 pontos, todos com `soilgrids_ok = true`.
- [ ] As culturas da `rotacao_atual` existem na base.
- [ ] O time aprovou as regiões.

## Desbloqueia
03 (AppEEARS) e o pré-cálculo do backend.
