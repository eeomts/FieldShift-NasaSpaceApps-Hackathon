# data — dados preparados pelo time

Volta para o [README principal](../README.md). As tarefas de cada pessoa, com o passo a passo, estão em [`ToDo/`](../ToDo/README.md).

Aqui ficam os dados que o time prepara à mão ou baixa uma vez, antes de o app funcionar. O passo a passo de cada tarefa está no guia `docs/NasaSpaceApps-FieldShift/v1/application/dados/GUIA-PREPARACAO-DADOS.md`.

## Fonte única do catálogo

O catálogo de culturas e equipamentos **mora no app**, em `agroai/base/`:

| O quê | Onde | Quem mexe |
|---|---|---|
| Ids, nomes e **sinônimos em PT/EN**, família, grupo, perene e tipos (fixadora de N, cobertura, raiz profunda, tolerante à seca) como padrão global, mais o bloco `por_pais` com `perene` e `tipos` de cada país | `agroai/base/culturas.json` | Pessoa 3 (sinônimos), por PR |
| Categorias de equipamento e seus sinônimos | `agroai/base/equipamentos.json` | Pessoa 2, só se faltar categoria |
| **Parâmetros agronômicos do Brasil**: 17 culturas (ciclo, temperatura, água, Kc, raiz, cobertura, código da PAM) | `data/catalogo/culturas.csv` | Pessoa 1 |
| **Parâmetros agronômicos dos EUA**: 18 culturas, no mesmo formato, com `codigo_nass` e `calendario_usda` no lugar de `codigo_pam` e `nome_zarc` (decisão D-010 do catálogo, 15/11/2026) | `data/catalogo/eua/culturas.csv` (guia em `catalogo/eua/README.md`) | Pessoa 1 |

Os dois `culturas.csv` usam **os mesmos ids** do `culturas.json` e não repetem o que já está lá (nomes, sinônimos, família, grupo). A exceção são `perene` e `tipos`: o CSV repete os dois **por país**, porque o valor pode mudar de um país para outro. Esse valor vem do bloco `por_pais` do `culturas.json` (`por_pais.BR` e `por_pais.US`, só para os ids que existem no CSV daquele país), e o `montar_csv.py` confere: se faltar o bloco do país ou o valor for diferente, ele aponta PROBLEMA. Para mudar `perene` ou `tipos`, mude o `por_pais` e a evidência juntos. Para criar uma cultura nova, ela entra primeiro no `culturas.json`.

**Os dois `culturas.csv` são gerados** das evidências (`catalogo/evidencias/<id>.json` no Brasil e `catalogo/eua/evidencias/<id>.json` nos EUA) por `catalogo/scripts/montar_csv.py`. Para mudar um valor, edite a evidência e rode o script com `--apply`; o teste `agroai/api/tests/test_dados_consistencia.py` confere, byte a byte, que o CSV versionado é igual ao gerado. O que cada regra do motor faz com esses parâmetros está em `catalogo/evidencias/README.md`.

## O que o motor lê hoje

- **Lê:** o `culturas.csv` de cada país e o `catalogo/cultura_equipamentos.csv`; as malhas `brasil/municipios/municipios.geojson` e `eua/condados/condados.geojson` (para achar o município ou o condado da fazenda); os textos de `rag/*.md` (pelo chat).
- **Não lê (dado preparado para depois):** a PAM (`brasil/pam/`), o NASS (`eua/nass/`) e as janelas do ZARC (`brasil/zarc/janelas.csv`).
- **Renda:** hoje a nota de renda é a **contagem de culturas de venda** (tipo `comercial`) da rotação. Preço e produção da região não entram. A PAM e o NASS só vão entrar quando o motor passar a lê-los (nota datada na D-009, em `DECISOES.md`).

## Divisão em 3 pessoas

Cada arquivo tem **um dono só**. Ninguém edita o arquivo de outra pessoa; se precisar de uma mudança, avise o dono. Isso evita conflito no Git.

### Pessoa 1 — Base de culturas (perfil: agronomia) · Yury

O caminho crítico do projeto: o motor inteiro depende dela.

| Tarefa | Arquivo | Esforço |
|---|---|---|
| 1. Parâmetros agronômicos das 17 culturas do motor (Brasil) e das 18 dos EUA | `catalogo/culturas.csv` e `catalogo/eua/culturas.csv` | Alto |
| 7. Código da PAM de cada cultura (coluna `codigo_pam`) | `catalogo/culturas.csv` | Baixo |

As 17 culturas do Brasil (os mesmos `id` do `agroai/base/culturas.json`) **já têm os parâmetros preenchidos**; o `codigo_pam` está em 10 delas (as outras não têm produto próprio na PAM, e a aveia da base é a aveia-preta de cobertura, que a PAM não conta; `arroz` e `arroz_irrigado` dividem o mesmo código). As 18 culturas dos EUA (`catalogo/eua/culturas.csv`, também com ids do `culturas.json`) usam `codigo_nass` e `calendario_usda`; nas coberturas esses dois campos ficam vazios. A produção por município sai em `brasil/pam/producao_municipal.csv` (`scripts/baixar_pam.py`). A coluna `nome_zarc` é copiada do `brasil/zarc/mapa_culturas_zarc.csv` (tarefa 6) e um teste da API confere que os dois batem.

### Pessoa 2 — Dados da NASA e do Brasil (perfil: dados) · Augusto

| Tarefa | Arquivo | Esforço |
|---|---|---|
| 4. Pontos da demo (decidir com o time e testar no SoilGrids) | `demo/pontos_demo.csv` | Baixo |
| 5. ~~Pedido no AppEEARS (NDVI + SMAP dos pontos)~~ **descartada em 15/11/2026**: o projeto não vai mais usar o AppEEARS. `demo/appeears/` e `scripts/baixar_appeears.py` ficam só como histórico | `demo/appeears/` (histórico) | — |
| 6. ZARC: baixar a tábua de risco e mapear os nomes das culturas | bruto em `brutos/zarc/`; mapa em `brasil/zarc/mapa_culturas_zarc.csv`; janelas em `brasil/zarc/janelas.csv` (GO, RS e BA; `scripts/preparar_zarc.py`) | Médio |
| 3. O que cada cultura exige de equipamento (ids do `agroai/base/equipamentos.json`) | `catalogo/cultura_equipamentos.csv` | Baixo |
| Registro de tudo que baixar | `FONTES.md` | — |

**Começar pela tarefa 4** (pontos da demo). A antiga espera do AppEEARS acabou: ele foi descartado.

### Pessoa 3 — Conteúdo para o produtor (perfil: escrita e produto) · _____________

| Tarefa | Arquivo | Esforço |
|---|---|---|
| 8. Textos do RAG | `rag/*.md` (lista em `rag/README.md`) | Médio |
| 2. Revisar e ampliar os sinônimos e nomes regionais das culturas | campo `nomes` do `agroai/base/culturas.json` | Baixo |
| 10. 12 fotos de solo com créditos ✅ feito | `onboarding/fotos-solo/` + `CREDITOS.md` | Baixo |

**Questionário ✅ feito (15/11):** a revisão para escopo global (23 perguntas em 6 partes, regras por local, textos em PT e EN americano) está em `onboarding/perguntas.yaml`, com o porquê de cada mudança em `onboarding/relatorio-revisao-questionario.md`. O `perguntas.yaml` é a especificação; as telas que o implementam estão em `agroai/web/src/onboarding/` (e na cópia de apresentação, `agroai/web-demo/src/onboarding/`).

## Estrutura

```text
data/
├── README.md                       # este arquivo
├── FONTES.md                       # registro de todo download (todos escrevem aqui)
├── catalogo/
│   ├── culturas.csv                # Pessoa 1 (17 culturas do Brasil; GERADO das evidências por scripts/montar_csv.py)
│   ├── evidencias/                 # Pessoa 1 (fonte dos valores do Brasil: um JSON por cultura + README das regras do motor)
│   ├── eua/                        # Pessoa 1 (18 culturas dos EUA, D-010 do catálogo: culturas.csv gerado, evidencias/, cenarios/, README.md)
│   ├── scripts/                    # montar_csv.py, regua.py, confianca.py, etc_nasa_power.py, gd_nasa_power.py
│   ├── cultura_sinonimos.md        # Pessoa 3 (proposta de nomes; a fonte é o agroai/base/culturas.json)
│   └── cultura_equipamentos.csv    # Pessoa 2
├── demo/
│   ├── pontos_demo.csv             # Pessoa 2
│   ├── appeears/                   # histórico: AppEEARS descartado em 15/11/2026 (tarefas.json + README com o aviso)
│   └── pontos_demo_eua.csv         # Pessoa 2 (pontos dos EUA)
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
│   ├── perguntas.yaml              # especificação do questionário (23 perguntas)
│   ├── relatorio-revisao-questionario.md
│   ├── perguntas-antes-e-depois.md
│   └── fotos-solo/                 # Pessoa 3 (+ CREDITOS.md)
├── scripts/                        # downloads e preparação (PAM, ZARC, malhas, AppEEARS, NASS)
└── brutos/                         # downloads grandes: FORA do Git
```

## EUA: o que substitui cada fonte brasileira

Os dados da NASA (POWER) e o SoilGrids cobrem os EUA do mesmo jeito. O que muda são as fontes nacionais:

| Brasil | EUA | Diferença que o motor precisa saber |
|---|---|---|
| Município (IBGE, 7 dígitos) | Condado (Censo, FIPS de 5 dígitos), `eua/condados/` | `condado_id` em vez de `municipio_id` |
| ZARC: janelas por município, solo, ciclo e risco (20/30/40 %) | NASS: datas **usuais** de plantio e colheita **por estado**, `eua/nass/datas_plantio.csv` | Mais grosso (estado), sem risco em %, sem solo e ciclo; edição de 2010 |
| PAM: produção por município | NASS Quick Stats: produção por condado, `eua/nass/producao_condado.csv` | Sem valor da produção; números escondidos pelo NASS ficam vazios |
| Catálogo de culturas (`catalogo/culturas.csv`, 17 culturas) | Catálogo dos EUA (`catalogo/eua/culturas.csv`, 18 culturas, D-010 do catálogo) | `codigo_nass` e `calendario_usda` no lugar de `codigo_pam` e `nome_zarc`; o motor lê o catálogo do país da fazenda |

**O que há do NASS por cultura** (conferido em 15/11/2026): `eua/nass/producao_condado.csv` e `eua/nass/datas_plantio.csv` têm as mesmas 9 culturas: milho, soja, trigo, arroz_irrigado, algodão, sorgo, girassol, aveia e feijão. Das 18 culturas do catálogo dos EUA, as outras 9 não têm dado nesses dois arquivos:
- **alfafa, amendoim, canola e cevada** têm `codigo_nass` no catálogo, mas nunca foram baixadas (ver o aviso abaixo);
- **centeio, ervilhaca, nabo forrageiro, pastagem e trevo** (coberturas e pasto) não têm série do NASS por condado.

Mandioca, milheto, feijão-caupi, crotalária, guandu e arroz de terras altas só existem no catálogo do Brasil e não têm dado do NASS (ver as observações em `eua/nass/mapa_culturas_nass.csv`, que ainda lista as culturas do catálogo do Brasil).

> **Aviso (revisão de 15/11/2026): o `SERIES` do `scripts/baixar_nass_eua.py` não segue o `codigo_nass` do catálogo dos EUA.** O `trigo` do catálogo é o de inverno (`WHEAT, WINTER`), mas o script soma inverno e primavera (sem o durum). O `girassol` do catálogo é `SUNFLOWER, OIL TYPE`, mas o script soma oleícola e confeiteiro (non-oil). Faltam as quatro culturas acima (alfafa, amendoim, canola e cevada), e o script baixa a aveia, que não tem `codigo_nass` no catálogo (cobertura). Corrigir muda os números do `producao_condado.csv` e exige baixar de novo, com a `NASS_API_KEY`. **Pendente, decisão do usuário.** O motor não lê esse arquivo hoje.

Para gerar: `python data/scripts/baixar_condados_eua.py`, `python data/scripts/preparar_datas_plantio_eua.py` e `NASS_API_KEY=... python data/scripts/baixar_nass_eua.py`.

## AppEEARS: descartado em 15/11/2026

O projeto **não vai mais usar o AppEEARS** (decisão do usuário, 15/11/2026; nota datada na D-009 do `DECISOES.md`). `demo/appeears/` (só o `tarefas.json` e o README) e `scripts/baixar_appeears.py` ficam apenas como histórico, sem apagar. Não existe `demo/appeears_eua/`, e não há dado do AppEEARS a registrar no `FONTES.md`.

## Dependências entre as pessoas

```text
Pessoa 1: ids das 17 culturas do Brasil e das 18 dos EUA (já prontos) ───► todos usam os mesmos ids
Pessoa 2: pontos_demo.csv ──► (o pedido no AppEEARS foi descartado em 15/11/2026)
Pessoa 2: mapa_culturas_zarc.csv ──► nome_zarc em culturas.csv; janelas.csv
Pessoa 1: culturas.csv completo (Brasil e EUA) ──► Pessoa 3 escreve fichas-culturas.md
```

Se precisar de uma cultura nova, ela entra primeiro no `agroai/base/culturas.json` (por PR) e só depois nos arquivos de `data/`.

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
