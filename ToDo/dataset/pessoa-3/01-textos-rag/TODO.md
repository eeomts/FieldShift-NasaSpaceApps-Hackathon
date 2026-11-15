# 01 — Textos da base de conhecimento do agente (RAG)

**Dono:** Pessoa 3 · **Status:** pendente · **Prioridade:** primeira (o chat depende dela)

## Por quê
O agente busca nestes textos para explicar as coisas ao produtor. A qualidade da resposta depende diretamente da qualidade e do formato deles.

## Saídas em `data/rag/`

| Arquivo | Conteúdo | Base para começar |
|---|---|---|
| `glossario-produtor.md` | O glossário reescrito em linguagem de produtor | `docs/NasaSpaceApps-FieldShift/v1/.md/glossario-cientifico-ampliado-field-shift-brasil.md` |
| `o-que-mede-cada-satelite.md` | NASA POWER, SoilGrids, SRTM, MODIS/VIIRS, SMAP, IMERG: o que cada um vê e o limite de escala | Notas de `docs/.../tools/` (só "o que é" e "limitações") |
| `metodologia-indicadores.md` | Como cada indicador é calculado e o que significa (geada, déficit hídrico, meses descobertos, erosão…) | `docs/.../application/architecture/MOTOR-DE-ANALISE.md` |
| `fichas-culturas.md` | Uma seção por cultura da base: para que serve, o que faz pelo solo, cuidados | `data/catalogo/culturas.csv` e as evidências (depois da tarefa 01 do Yury) |

Ordem sugerida: glossário → satélites → metodologia → fichas.

## Regras de escrita (fazem a busca funcionar)
1. **Um assunto por seção** (`##` ou `###`), de **100 a 400 palavras**.
2. **Cada seção se explica sozinha**: repita o nome do assunto, nunca "como vimos acima".
3. Uma linha **"Como o produtor costuma dizer:"** com os jeitos populares de falar do assunto.
4. **Fonte no fim** de cada seção.
5. Nada de URL de API, parâmetro ou código.

Exemplo de seção pronta: `docs/.../application/dados/GUIA-PREPARACAO-DADOS.md`, seção 8.

## Pronto quando
- [ ] Os 4 arquivos em `data/rag/`, seguindo as 5 regras.
- [ ] Alguém leu 3 seções em voz alta e um produtor (ou alguém de fora da área) entenderia.
- [ ] Nenhum número sem fonte.
