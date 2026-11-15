# data — dados preparados pelo time

Aqui ficam os dados que o time prepara à mão ou baixa uma vez, antes de o app funcionar. O passo a passo de cada tarefa está no guia `docs/NasaSpaceApps-FieldShift/v1/application/dados/GUIA-PREPARACAO-DADOS.md`.

## Fonte única do catálogo

O catálogo de culturas e equipamentos **mora no app**, em `agroia/base/`:

| O quê | Onde | Quem mexe |
|---|---|---|
| Ids, nomes e **sinônimos em PT/EN/ES**, família, grupo, perene, tipos (fixadora de N, cobertura, raiz profunda, tolerante à seca) | `agroia/base/culturas.json` | Pessoa 3 (sinônimos), por PR |
| Categorias de equipamento e seus sinônimos | `agroia/base/equipamentos.json` | Pessoa 2, só se faltar categoria |
| **Parâmetros agronômicos** (ciclo, temperatura, água, Kc, raiz, cobertura, código da PAM) | `data/catalogo/culturas.csv` | Pessoa 1 |

O `culturas.csv` usa **os mesmos ids** do `culturas.json` e não repete o que já está lá. Para criar uma cultura nova, ela entra primeiro no `culturas.json`.

## Divisão em 3 pessoas

Cada arquivo tem **um dono só**. Ninguém edita o arquivo de outra pessoa; se precisar de uma mudança, avise o dono. Isso evita conflito no Git.

### Pessoa 1 — Base de culturas (perfil: agronomia) · Yury

O caminho crítico do projeto: o motor inteiro depende dela.

| Tarefa | Arquivo | Esforço |
|---|---|---|
| 1. Parâmetros agronômicos das 17 culturas do motor | `catalogo/culturas.csv` | Alto |
| 7. Código da PAM de cada cultura (coluna `codigo_pam`) | `catalogo/culturas.csv` | Baixo |

As 17 culturas (os mesmos `id` do `agroia/base/culturas.json`) **já têm os parâmetros preenchidos**; o `codigo_pam` está em 10 delas (as outras não têm produto próprio na PAM, e a aveia da base é a aveia-preta de cobertura, que a PAM não conta; `arroz` e `arroz_irrigado` dividem o mesmo código). A produção por município sai em `brasil/pam/producao_municipal.csv` (`scripts/baixar_pam.py`). A coluna `nome_zarc` é copiada do `brasil/zarc/mapa_culturas_zarc.csv` (tarefa 6) e um teste da API confere que os dois batem.

### Pessoa 2 — Dados da NASA e do Brasil (perfil: dados) · Augusto

| Tarefa | Arquivo | Esforço |
|---|---|---|
| 4. Pontos da demo (decidir com o time e testar no SoilGrids) | `demo/pontos_demo.csv` | Baixo |
| 5. Pedido no AppEEARS (NDVI + SMAP dos pontos) | `demo/appeears/<id_da_tarefa>/` | Médio (espera) |
| 6. ZARC: baixar a tábua de risco e mapear os nomes das culturas | bruto em `brutos/zarc/`; mapa em `brasil/zarc/mapa_culturas_zarc.csv`; janelas em `brasil/zarc/janelas.csv` (GO, RS e BA; `scripts/preparar_zarc.py`) | Médio |
| 3. O que cada cultura exige de equipamento (ids do `agroia/base/equipamentos.json`) | `catalogo/cultura_equipamentos.csv` | Baixo |
| Registro de tudo que baixar | `FONTES.md` | — |

**Começar pela tarefa 4**: o AppEEARS só pode ser pedido depois que os pontos existirem, e ele demora.

### Pessoa 3 — Conteúdo para o produtor (perfil: escrita e produto) · _____________

| Tarefa | Arquivo | Esforço |
|---|---|---|
| 8. Textos do RAG | `rag/*.md` (lista em `rag/README.md`) | Médio |
| 2. Revisar e ampliar os sinônimos e nomes regionais das culturas | campo `nomes` do `agroia/base/culturas.json` | Baixo |
| 10. 12 fotos de solo com créditos ✅ feito | `onboarding/fotos-solo/` + `CREDITOS.md` | Baixo |

O questionário (antiga tarefa 9) já está implementado nas telas do app (`agroia/web/src/onboarding/`), então não precisa mais do `perguntas.yaml`.

**Questionário ✅ feito (15/11):** a revisão para escopo global (23 perguntas em 6 partes, regras por local, textos em PT e EN americano) está em `onboarding/perguntas.yaml`, com o porquê de cada mudança em `onboarding/relatorio-revisao-questionario.md`. Ela serve de especificação para as telas: o que o código ainda precisa fazer está no fim do relatório.

## Estrutura

```
data/
├── README.md                       # este arquivo
├── FONTES.md                       # registro de todo download (todos escrevem aqui)
├── catalogo/
│   ├── culturas.csv                # Pessoa 1 (parâmetros; ids do agroia/base/culturas.json)
│   └── cultura_equipamentos.csv    # Pessoa 2
├── demo/
│   ├── pontos_demo.csv             # Pessoa 2
│   ├── appeears/<id_da_tarefa>/    # Pessoa 2 (CSVs como vieram)
│   ├── pontos_demo_eua.csv         # Pessoa 2 (pontos dos EUA)
│   └── appeears_eua/<id_da_tarefa>/  # Pessoa 2 (AppEEARS dos pontos dos EUA)
├── brasil/
│   ├── municipios/                 # Pessoa 2 (malha do IBGE)
│   ├── pam/
│   │   ├── producao_municipal.csv  # Pessoa 1: produção por município × cultura × ano (PAM, 2016-2025), gerado por scripts/baixar_pam.py
│   │   └── README.md               # origem, colunas, símbolos do SIDRA e conferência
│   └── zarc/
│       ├── mapa_culturas_zarc.csv  # Pessoa 2 (cultura_id → nome no ZARC)
│       ├── janelas.csv             # janelas do ZARC (GO, RS e BA), gerado por scripts/preparar_zarc.py
│       └── README.md               # origem, safra por município, colunas e regras para o motor
├── eua/                            # Pessoa 2 (o mesmo papel do brasil/, ver abaixo)
│   ├── condados/                   # condados.csv + condados.geojson (Censo, TIGERweb)
│   └── nass/
│       ├── mapa_culturas_nass.csv  # cultura_id → nome no NASS
│       ├── datas_plantio.csv       # datas usuais de plantio/colheita por estado (no lugar do ZARC)
│       └── producao_condado.csv    # produção por condado (no lugar da PAM; precisa de NASS_API_KEY)
├── rag/                            # Pessoa 3 (textos .md)
├── onboarding/
│   └── fotos-solo/                 # Pessoa 3 (+ CREDITOS.md)
└── brutos/                         # downloads grandes: FORA do Git
```

## EUA: o que substitui cada fonte brasileira

Os dados da NASA (AppEEARS, SMAP, POWER) e o SoilGrids cobrem os EUA do mesmo jeito. O que muda são as fontes nacionais:

| Brasil | EUA | Diferença que o motor precisa saber |
|---|---|---|
| Município (IBGE, 7 dígitos) | Condado (Censo, FIPS de 5 dígitos), `eua/condados/` | `condado_id` em vez de `municipio_id` |
| ZARC: janelas por município, solo, ciclo e risco (20/30/40 %) | NASS: datas **usuais** de plantio e colheita **por estado**, `eua/nass/datas_plantio.csv` | Mais grosso (estado), sem risco em %, sem solo e ciclo; edição de 2010 |
| PAM: produção por município | NASS Quick Stats: produção por condado, `eua/nass/producao_condado.csv` | Sem valor da produção; números escondidos pelo NASS ficam vazios |

Culturas da base sem dado nos EUA: mandioca, milheto, feijão-caupi e as de cobertura (ver as observações em `eua/nass/mapa_culturas_nass.csv`).

Para gerar: `python data/scripts/baixar_condados_eua.py`, `python data/scripts/preparar_datas_plantio_eua.py`, `NASS_API_KEY=... python data/scripts/baixar_nass_eua.py` e `python data/scripts/baixar_appeears.py --pontos data/demo/pontos_demo_eua.csv --saida data/demo/appeears_eua`.

## Dependências entre as pessoas

```
Pessoa 1: ids das 17 culturas (já prontos) ───► todos usam os mesmos ids
Pessoa 2: pontos_demo.csv ──► pedido no AppEEARS ──► CSVs em demo/appeears/
Pessoa 2: mapa_culturas_zarc.csv ──► nome_zarc em culturas.csv; janelas.csv
Pessoa 1: culturas.csv completo ──► Pessoa 3 escreve fichas-culturas.md
```

Se precisar de uma cultura nova, ela entra primeiro no `agroia/base/culturas.json` (por PR) e só depois nos arquivos de `data/`.

## Regras de formato (resumo)

- CSV em **UTF-8**, separador **vírgula**, decimal com **ponto**. Edite no **Google Sheets** e exporte como CSV; o Excel em português troca por `;` e vírgula decimal.
- **Vazio = não sei.** Nunca use 0 para "não sei".
- Sim/não como `true` / `false`. Listas numa célula separadas por `|`.
- Ids em `snake_case`, sem acento.
- Toda linha com fonte.

## Fluxo no Git

- Cada pessoa trabalha na própria branch: `data/catalogo`, `data/nasa-brasil`, `data/conteudo`.
- PRs pequenos e frequentes (ex.: a cada 4 ou 5 culturas preenchidas), para os outros já poderem usar.
- Nada de arquivo grande no Git: use `brutos/` (ignorado) e registre no `FONTES.md`.
