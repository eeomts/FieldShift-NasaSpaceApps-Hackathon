# data/rag — textos da base de conhecimento do agente

Cada arquivo `.md` desta pasta vira trechos que o agente busca para explicar as coisas ao produtor.

| Arquivo | Conteúdo |
|---|---|
| `metodologia-indicadores.md` | Como cada indicador é calculado e o que significa (geada, déficit hídrico, meses descobertos, erosão…) |
| `o-que-mede-cada-satelite.md` | NASA POWER, SoilGrids, SRTM, MODIS/VIIRS, SMAP, IMERG: o que cada um vê e o limite de escala |
| `fichas-culturas.md` | Uma seção por cultura da base: as 17 do Brasil (`data/catalogo/culturas.csv`) e as 18 dos EUA (`data/catalogo/eua/culturas.csv`) |
| `glossario-produtor.md` | O glossário científico reescrito em linguagem de produtor |

**Ficha e CSV andam juntos:** os números de `fichas-culturas.md` vêm dos dois `culturas.csv` (ver `data/catalogo/`). Mudar o CSV (ou a evidência de onde ele é gerado) obriga a rever a ficha e reingerir o RAG (`python -m app.cli.rag ingerir`, na pasta `agroai/api`). Hoje os números da ficha batem com os CSVs, mas nenhum teste confere isso. O mesmo vale para os outros textos: mudou o que o motor faz, revise o `.md` e reingira.

**Regras de escrita** (detalhes e exemplo no guia `docs/NasaSpaceApps-FieldShift/v1/application/dados/GUIA-PREPARACAO-DADOS.md`, seção 8):

1. Um assunto por seção (`##` ou `###`), de 100 a 400 palavras.
2. Cada seção se explica sozinha: repita o nome do assunto, nunca "como vimos acima".
3. Uma linha **"Como o produtor costuma dizer:"** com os jeitos populares de falar do assunto.
4. Fonte no fim de cada seção.
5. Nada de URL de API, parâmetro ou código.

---

Volta para o [`data/README.md`](../README.md).
