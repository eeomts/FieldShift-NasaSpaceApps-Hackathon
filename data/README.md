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
| 1. Parâmetros agronômicos das 16 culturas do motor | `catalogo/culturas.csv` | Alto |
| 7. Código da PAM de cada cultura (coluna `codigo_pam`) | `catalogo/culturas.csv` | Baixo |

As 16 culturas (os mesmos `id` do `agroia/base/culturas.json`) **já têm os parâmetros preenchidos**; o `codigo_pam` está em 9 delas (as outras não aparecem na PAM ou falta conferir). A coluna `nome_zarc` não é preenchida à mão: ela vem do `brasil/zarc/mapa_culturas_zarc.csv` (tarefa 6, Pessoa 2) na carga.

### Pessoa 2 — Dados da NASA e do Brasil (perfil: dados) · Augusto

| Tarefa | Arquivo | Esforço |
|---|---|---|
| 4. Pontos da demo (decidir com o time e testar no SoilGrids) | `demo/pontos_demo.csv` | Baixo |
| 5. Pedido no AppEEARS (NDVI + SMAP dos pontos) | `demo/appeears/<id_da_tarefa>/` | Médio (espera) |
| 6. ZARC: baixar a tábua de risco e mapear os nomes das culturas | bruto em `brutos/zarc/`; mapa em `brasil/zarc/mapa_culturas_zarc.csv`; recorte das 16 culturas em `brasil/zarc/` | Médio |
| 3. O que cada cultura exige de equipamento (ids do `agroia/base/equipamentos.json`) | `catalogo/cultura_equipamentos.csv` | Baixo |
| Registro de tudo que baixar | `FONTES.md` | — |

**Começar pela tarefa 4**: o AppEEARS só pode ser pedido depois que os pontos existirem, e ele demora.

### Pessoa 3 — Conteúdo para o produtor (perfil: escrita e produto) · _____________

| Tarefa | Arquivo | Esforço |
|---|---|---|
| 8. Textos do RAG | `rag/*.md` (lista em `rag/README.md`) | Médio |
| 2. Revisar e ampliar os sinônimos e nomes regionais das culturas | campo `nomes` do `agroia/base/culturas.json` | Baixo |
| 10. 12 fotos de solo com créditos | `onboarding/fotos-solo/` + `CREDITOS.md` | Baixo |

O questionário (antiga tarefa 9) já está implementado nas telas do app (`agroia/web/src/onboarding/`), então não precisa mais do `perguntas.yaml`.

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
│   └── appeears/<id_da_tarefa>/    # Pessoa 2 (CSVs como vieram)
├── brasil/
│   └── zarc/
│       ├── mapa_culturas_zarc.csv  # Pessoa 2 (cultura_id → nome no ZARC)
│       └── <recortes>.csv          # Pessoa 2 (só as 16 culturas)
├── rag/                            # Pessoa 3 (textos .md)
├── onboarding/
│   └── fotos-solo/                 # Pessoa 3 (+ CREDITOS.md)
└── brutos/                         # downloads grandes: FORA do Git
```

## Dependências entre as pessoas

```
Pessoa 1: ids das 16 culturas (já prontos) ───► todos usam os mesmos ids
Pessoa 2: pontos_demo.csv ──► pedido no AppEEARS ──► CSVs em demo/appeears/
Pessoa 2: mapa_culturas_zarc.csv ──► preenche nome_zarc na carga
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
