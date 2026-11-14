# data/rag — textos da base de conhecimento do agente

Cada arquivo `.md` desta pasta vira trechos que o agente busca para explicar as coisas ao produtor.

| Arquivo | Conteúdo |
|---|---|
| `metodologia-indicadores.md` | Como cada indicador é calculado e o que significa (geada, déficit hídrico, meses descobertos, erosão…) |
| `o-que-mede-cada-satelite.md` | NASA POWER, SoilGrids, SRTM, MODIS/VIIRS, SMAP, IMERG: o que cada um vê e o limite de escala |
| `fichas-culturas.md` | Uma seção por cultura da base (as 16 de `data/catalogo/culturas.csv`) |
| `glossario-produtor.md` | O glossário científico reescrito em linguagem de produtor |

**Regras de escrita** (detalhes e exemplo no guia `docs/NasaSpaceApps-FieldShift/v1/application/dados/GUIA-PREPARACAO-DADOS.md`, seção 8):

1. Um assunto por seção (`##` ou `###`), de 100 a 400 palavras.
2. Cada seção se explica sozinha: repita o nome do assunto, nunca "como vimos acima".
3. Uma linha **"Como o produtor costuma dizer:"** com os jeitos populares de falar do assunto.
4. Fonte no fim de cada seção.
5. Nada de URL de API, parâmetro ou código.
