# 02 — Script da PAM (produção por município)

**Dono:** Pessoa 1 (Yury) · **Status:** pendente · **Depende de:** 01

## Por quê
O critério "renda extra" do motor precisa saber se a cultura se planta e rende no município do produtor. A fonte é a Produção Agrícola Municipal do IBGE (tabela 5457 do SIDRA).

## Entrada
- `data/catalogo/culturas.csv`: o `codigo_pam` de cada cultura (classificação 782 do SIDRA). Culturas sem código (cobertura, forrageira) ficam de fora.

## Saída: `data/brasil/pam/producao_municipal.csv`

| Coluna | Tipo | Exemplo |
|---|---|---|
| `municipio_id` | código IBGE de 7 dígitos | `3170206` |
| `cultura_id` | id da base | `soja` |
| `ano` | inteiro | `2023` |
| `area_plantada_ha` | número | `125000` |
| `area_colhida_ha` | número | `124800` |
| `producao_t` | número | `450000` |
| `rendimento_kg_ha` | número | `3605` |
| `valor_mil_reais` | número | `980000` |

Uma linha por município × cultura × ano, **últimos 10 anos disponíveis**.

## Passo a passo
1. Script `data/scripts/baixar_pam.py` (regras em `ToDo/README.md`).
2. API do SIDRA: `https://apisidra.ibge.gov.br/values/t/5457/n6/all/v/8331,216,214,112,215/p/<anos>/c782/<codigo_pam>`
   - variáveis: 8331 área plantada, 216 área colhida, 214 produção, 112 rendimento, 215 valor.
   - faça **uma chamada por cultura e por ano** (a API limita o tamanho da resposta **[verificar o limite]**).
   - a primeira linha da resposta é o cabeçalho descritivo: pule.
3. Símbolos do SIDRA: `-` = **zero** (valor zero de verdade) → `0`; `..`, `...` e `X` = sem dado → **vazio**.
4. Registre no `data/FONTES.md` (tabela, anos, data do download).
5. Detalhes da API: `docs/NasaSpaceApps-FieldShift/v1/tools/IBGE_PAM.md`.

## Pronto quando
- [ ] Roda com `python data/scripts/baixar_pam.py` e gera o CSV acima.
- [ ] Todo `cultura_id` existe na base; todo `municipio_id` tem 7 dígitos.
- [ ] Nenhum `..`, `...` ou `X` no CSV; nenhum "sem dado" virou 0.
- [ ] Conferência manual: 2 valores batem com a página do SIDRA.
