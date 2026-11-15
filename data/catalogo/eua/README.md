# Catálogo de culturas dos EUA

Parâmetros agronômicos das culturas para pontos nos EUA, no **mesmo formato** do catálogo do Brasil (`data/catalogo/culturas.csv`), para que o motor use as duas tabelas do mesmo jeito. Escopo aberto em 15/11/2026 (decisão D-010 em `docs/NasaSpaceApps-FieldShift/v1/context/DECISOES.md`).

Quem constrói: o agente **`agroia-dataset-eua`** (`.claude/agents/agroia-dataset-eua.md`), chamado pelo coordenador em lotes. Tudo o que aprendemos no catálogo do Brasil está aqui e no agente.

## Estrutura

```
data/catalogo/eua/
├── README.md                 # este guia
├── culturas.csv              # GERADO por scripts/montar_csv.py (não editar à mão)
├── evidencias/<id>.json      # fonte da verdade: valores, origem, evidências, régua, pendências
└── cenarios/
    ├── <id>_etc.json         # cenários de água (scripts/etc_nasa_power.py)
    └── <id>_gd.json          # cenários de graus-dia (scripts/gd_nasa_power.py)
```

Cada agente escreve **só os arquivos da sua cultura**. O CSV é montado depois, por script, sem conflito entre agentes.

Colunas: as do Brasil + `codigo_nass` (começo do `short_desc` da série no USDA NASS QuickStats, isto é, `commodity_desc` mais a classe ou a utilização, ex.: "CORN, GRAIN"; para filtrar, use `short_desc` começando por esse texto, não `commodity_desc`; no lugar do `codigo_pam`) e `calendario_usda` (nome da cultura no USDA Agricultural Handbook 628, no lugar do `nome_zarc`). No CSV dos EUA, `codigo_pam` e `nome_zarc` ficam vazios. As colunas de janela, região e texto para o produtor (`semeadura_*`, `manejo_*`, `tipo_manejo`, `condicao_semeadura`, `estados_validos`, `lacuna_informacao`, `risco_revisao_local`) são as mesmas do Brasil e estão descritas em `../evidencias/README.md`; nos EUA, `estados_validos` usa siglas USPS.

Nas **coberturas**, `codigo_nass` e `calendario_usda` ficam **vazios**: os códigos do NASS e o Handbook 628 descrevem o grão (ex.: aveia de primavera semeada em março), não a cobertura. A explicação fica em `regua.observacoes.codigos`. Códigos NASS **conferidos na API do QuickStats (15/11/2026)** para as 12 culturas com código: cada `codigo_nass` é o começo exato de séries SURVEY reais, com dados por condado (a divisão em `commodity_desc`, classe e uso está em `regua.observacoes.codigos` de cada cultura). O feijão usa "BEANS, DRY EDIBLE, INCL CHICKPEAS" (decisão do usuário): "BEANS, DRY EDIBLE" sozinho só existe no Censo, e a série sem grão-de-bico é curta; por isso a área e a produção do NASS para o feijão **incluem grão-de-bico**. Nas séries por condado do time (`data/eua/nass/`), `trigo` soma inverno e primavera e `girassol` soma oleícola e confeiteiro. Isso diverge do `codigo_nass` desta tabela (trigo de inverno; girassol `OIL TYPE`), e faltam alfafa, amendoim, canola e cevada: corrigir exige baixar de novo, pendente de decisão do usuário (ver `data/README.md` e `data/FONTES.md`).

A janela de semeadura dos grãos (`semeadura_inicio/fim`) é o "most active" (15 a 85% semeado) do USDA Handbook 628 (2010) no estado de referência principal: o que os produtores fazem, não uma recomendação. Vem de `data/eua/nass/datas_plantio.csv`, exceto amendoim (Geórgia) e cevada (Dakota do Norte), lidos direto no texto do Handbook porque não estão nesse arquivo. A canola fica sem janela de propósito (o Handbook só tem a canola de inverno de Oklahoma) e a alfafa é perene. Numa linha com duas regiões, a outra região pode cair fora dessa janela (ex.: algodão, com a janela da Geórgia em `regua.arranjos.georgia`). As janelas dos grãos ficam no CSV como referência: o motor **não** as aplica. Só a janela das coberturas (as culturas sem `comercial`) entra, na regra 12, tanto nas candidatas novas quanto nas trocas (`agroia/api/app/services/motor/candidatas.py`).

## Culturas e sistemas

Os sistemas seguem os testes de chat do produtor americano (`docs/NasaSpaceApps-FieldShift/v1/application/prompts/examples/tests/TESTES_CHAT_SR_SMITH.md`). Uma linha representa **um sistema**: o mais comum na região de referência.

| Prioridade | id | Cultura / sistema nos EUA | Região de referência |
|---|---|---|---|
| 1 | `milho` | Corn for grain, sequeiro (variante irrigada em pendência) | Iowa, Illinois (Nebraska irrigado) |
| 1 | `soja` | Soybean, sequeiro | Iowa; Delta do Arkansas |
| 1 | `trigo` | **Hard red winter wheat** (trigo de inverno; o de primavera fica em pendência) | Kansas |
| 1 | `sorgo` | Grain sorghum, incluindo o double-crop depois do trigo | Kansas; oeste do Texas |
| 1 | `algodao` | Upland cotton, sequeiro | Oeste do Texas (Lubbock); sul da Geórgia (janela da Geórgia em `regua.arranjos.georgia`; ciclo e graus-dia mínimo do Texas, graus-dia máximo e água mínima da Geórgia: separar quando o motor ler arranjos) |
| 1 | `arroz_irrigado` | Rice, inundado (só candidato com várzea ou irrigação, regra 8) | Delta do Arkansas |
| 1 | `girassol` | Oilseed sunflower | Dakota do Norte |
| 1 | `amendoim` | Peanut (runner), em rotação com algodão | Sul da Geórgia |
| 1 | `centeio` | Cereal rye, cobertura de inverno depois do milho/soja | Iowa |
| 2 | `aveia` | Oats (*Avena sativa*), cobertura | Corn Belt |
| 2 | `ervilhaca` | Hairy vetch (*Vicia villosa*), cobertura de inverno antes do milho | Corn Belt (o Sudeste fica em `regua.arranjos.sudeste`) |
| 2 | `trevo` | Crimson clover (*Trifolium incarnatum*), cobertura | Geórgia (Alabama e Tennessee em `regua.arranjos.alabama` e `regua.arranjos.tennessee`) |
| 2 | `nabo_forrageiro` | Forage/tillage radish, cobertura | Corn Belt |
| 2 | `alfafa` | Alfalfa hay, perene forrageira: sem ciclo nem graus-dia (padrão da pastagem); água anual | Nebraska (a Califórnia fica em pendência) |
| 3 | `pastagem` | Tall fescue (*Lolium arundinaceum*), pasto perene forrageira: sem ciclo nem graus-dia; água anual; aviso do fungo em `regua.avisos` | Missouri e Kentucky (mesma faixa do Fescue Belt) |
| 3 | `feijao` | Dry edible bean (pinto e navy), sequeiro | Dakota do Norte (Michigan em `regua.arranjos.michigan`) |
| 3 | `canola` | Canola de primavera | Dakota do Norte |
| 3 | `cevada` | Barley de primavera, sequeiro | Dakota do Norte (Montana em `regua.arranjos.montana`) |

Atenção: o mesmo `id` pode ser **outra espécie ou outro sistema** do que no Brasil. Isso vale para `aveia` (*A. strigosa* no Brasil, *A. sativa* nos EUA), `pastagem` (braquiária no Brasil, festuca nos EUA) e `trigo` (trigo de primavera no Brasil, de inverno nos EUA). Diga isso em `sistema` e em `nome_cientifico`.

`arroz_irrigado` entrou em `agroia/base/culturas.json` no commit f910193 (antes era bloqueio do `montar_csv.py`). Quando o produtor escreve só "arroz" ou "rice", o app pede que ele diga se é irrigado ou de terras altas; não decide pelo país.

**Uma linha, uma região.** Quando a mesma espécie tem sistemas diferentes em regiões distantes (ex.: ervilhaca no Corn Belt e no Sudeste), a linha fica com a região de referência e a outra vai para `regua.arranjos.<regiao>` com `estados`, ou para as pendências. `estados_validos` diz onde a linha vale (ex.: trevo-encarnado só na Geórgia).

**Os arranjos regionais ficam guardados e o motor AINDA NÃO os lê** (trevo AL/TN, feijão MI, ervilhaca Sudeste, cevada MT, algodão GA): um ponto nesses estados vê "sem dado para sua região" (quando a linha tem `estados_validos`) ou os números da linha. Ler os arranjos é a parte da regra 13 que ainda falta no motor; a outra parte, `estados_validos`, já vale (tabela "regra x situação no motor" em `../evidencias/README.md`).

## O que reaproveitar do Brasil

| Coluna | Reaproveita? | Como |
|---|---|---|
| `nome_cientifico`, `familia_botanica`, `tipos`, `fixa_nitrogenio`, `raiz_profunda` | Sim, se for a **mesma espécie** | Copiar e conferir. Os `tipos` podem mudar com o papel da cultura nos EUA (por exemplo, a aveia é só cobertura) |
| `temp_base_c`, `temp_otima_*`, `tmax_critica_c` | Sim (é fisiologia da espécie) | Manter a mesma Tb do Brasil para o motor tratar as duas tabelas igual. Conferir com fonte dos EUA (extensão rural) e registrar a divergência em `pendencias` |
| `sensivel_geada` | Conferir | As culturas de inverno dos EUA (trigo de inverno, centeio, ervilhaca) toleram o frio no vegetativo; a coluna fala do dano na fase sensível |
| `kc_inicial`, `kc_medio`, `kc_final` | Sim | FAO-56 Tab. 12, padronizado, com teto de 1,25 (eq. 72). As tabelas do FAO-56 vêm em boa parte de medições nos EUA |
| `profundidade_raiz_m` | Sim | FAO-56 Tab. 22, limite superior (sequeiro) |
| `ciclo_dias_min/max` | **Não** | Da semeadura à maturação fisiológica (grãos) ou ao manejo (coberturas), por maturidade relativa, pela extensão estadual. A colheita típica (USDA NASS *Field Crops Usual Planting and Harvesting Dates*, 2010, Agricultural Handbook 628) fica registrada à parte |
| `graus_dia_ciclo_min/max` | **Não** | Fontes dos EUA (GDD por maturidade relativa, NDAWN), convertidas para °C, com a Tb da linha e **sem teto**: modo `alvo_com_teto` do `gd_nasa_power.py` |
| `agua_ciclo_mm_min/max` | **Não** | Consumo com produtividade plena (não o mínimo "para colher algo"), pela extensão (Nebraska, K-State, Texas A&M, NDSU) ou por cálculo com `etc_nasa_power.py` em cenários dos EUA |
| Bloco `regua` (palhada, C/N, k, forragem) | Só o método | Dados dos EUA: RUSLE2 (razão palha/grão e decomposição por cultura), SARE *Managing Cover Crops Profitably*, Midwest Cover Crops Council, NASEM/NRC e Dairy One (forragem). A régua é a **mesma** do Brasil (cortes de 2,3 e 6 t/ha, 60 dias), para as notas serem comparáveis |
| `codigo_pam`, `nome_zarc` | Não se aplicam | Usar `codigo_nass` e `calendario_usda` |

## Mapa de fontes (EUA x Brasil)

| Brasil | EUA |
|---|---|
| IBGE PAM (produção e produtividade por município) | USDA NASS QuickStats (por condado); começo do `short_desc` em `codigo_nass` |
| ZARC/MAPA (janela de plantio e ciclo) | USDA Agricultural Handbook 628; USDA RMA (datas finais de plantio do seguro) |
| Embrapa (sistemas de produção, circulares) | Extensão das universidades land-grant (Iowa State, K-State, UNL, NDSU, Texas A&M AgriLife, UGA, Univ. of Arkansas) e USDA-ARS |
| CQBAL (valor nutritivo) | NASEM/NRC (tabelas de alimentos), Dairy One Feed Composition Library, Feedipedia |
| Coletas brasileiras de palhada e decomposição | RUSLE2 (USDA-ARS/NRCS), SARE, Midwest Cover Crops Council, NRCS Plant Guides |
| FAO-56, ECOCROP, IPCC | Os mesmos (a calibração temperada do IPCC e dos modelos combina melhor com os EUA) |
| WOFOST/AquaCrop (só conferência no Brasil) | Os mesmos, com mais peso: várias calibrações do AquaCrop são dos EUA (o milho é de Davis, CA) |

## Conversões
- °F para °C: (°F − 32) / 1,8. Graus-dia em °F para °C: dividir por 1,8, **mas só se a Tb da fonte for a mesma da linha** (50 °F = 10 °C; DD60 do algodão = Tb 15,6 °C).
- **Teto:** o GDD 86/50 do milho e da soja limita a Tmax em 86 °F (30 °C) e eleva a Tmin a 50 °F. O catálogo é **sem teto**: converta com o modo `alvo_com_teto` do `gd_nasa_power.py` (ex.: 2700 GDD °F até a maturação em Nashua-IA, semeadura em 1/5, ≈ 1450 °C·dia sem teto) e marque como `calculo`.
- Polegadas para mm: × 25,4. lb/acre para kg/ha: × 1,121. t curta/acre para t/ha: × 2,242.
- bu/acre para t/ha: milho e sorgo × 0,0628; soja e trigo × 0,0673; cevada × 0,0538; aveia × 0,0359.

## Fluxo do coordenador
1. Conferir se os ids do lote existem em `agroia/base/culturas.json`.
2. Chamar o agente `agroia-dataset-eua` em **lotes de até 4 em paralelo**, cada um com 1 ou 2 culturas, dizendo o id, a prioridade e o sistema desta tabela.
3. Depois de cada lote, na raiz do repositório. O `regua.py` lê as culturas do CSV já gravado, por isso o CSV é montado **antes** (para entrar a cultura nova) e **depois** (para levar as classes e a confiança):
   ```
   python3 -I data/catalogo/scripts/montar_csv.py --catalogo data/catalogo/eua --apply  # valida e grava (cultura nova entra no CSV)
   python3 -I data/catalogo/scripts/regua.py --catalogo data/catalogo/eua --apply
   python3 -I data/catalogo/scripts/confianca.py --catalogo data/catalogo/eua --apply
   python3 -I data/catalogo/scripts/montar_csv.py --catalogo data/catalogo/eua --apply  # grava o CSV
   ```
4. Revisar com `/revisar` (foco nas culturas de confiança `media` e `baixa`).
5. Commit no padrão do projeto (skill `commit-agroia`).

As regras de confiança, da régua e do motor são as mesmas do Brasil: `data/catalogo/evidencias/README.md`.
