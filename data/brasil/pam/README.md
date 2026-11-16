# PAM: produção agrícola por município

Produção Agrícola Municipal do IBGE (tabela 5457 do SIDRA), por município, cultura e ano. É dado preparado para o critério "renda extra" do motor: diz se a cultura se planta e quanto rende no município do produtor. **O motor ainda não lê este arquivo** (conferido em 15/11/2026): hoje a nota de renda é a contagem de culturas de venda da rotação, sem preço nem produção da região. A PAM só entra na nota quando o motor passar a lê-la. Equivale ao `eua/nass/producao_condado.csv` dos EUA.

| Arquivo | O que é |
|---|---|
| `producao_municipal.csv` | Gerado por `scripts/baixar_pam.py` em 15/11/2026: 556.400 linhas (5.564 municípios × 10 culturas × 10 anos), 19,5 MB. **Fica fora do Git**: gere com o script. |

## Origem

- IBGE, SIDRA, [tabela 5457](https://sidra.ibge.gov.br/tabela/5457) ("Área plantada ou destinada à colheita, área colhida, quantidade produzida, rendimento médio e valor da produção das lavouras temporárias e permanentes"), nível município (`n6`).
- API: `https://apisidra.ibge.gov.br/values/t/5457/n6/all/v/8331,216,214,112,215/p/<ano>/c782/<codigo_pam>/f/c`, uma chamada por produto e por ano. Os anos publicados vêm de `https://servicodados.ibge.gov.br/api/v3/agregados/5457/periodos`.
- Baixado em 15/11/2026: anos 2016 a 2025 (os 10 últimos publicados; 2025 é o mais recente, série atualizada pelo IBGE em 23/10/2026).
- Limite da API, medido em 15/11/2026: **100.000 valores por consulta** (acima disso, HTTP 400 "excedeu o limite: 100000"). Um produto × um ano × 5 variáveis × 5.564 municípios = 27.820 valores.

## Culturas

O código de cada cultura vem da coluna `codigo_pam` de `data/catalogo/culturas.csv` (classificação 782 da tabela). Hoje, 10 culturas:

| `cultura_id` | Produto na PAM (código) |
|---|---|
| `soja` | Soja (em grão) (40124) |
| `milho` | Milho (em grão) (40122): 1ª e 2ª safra somadas |
| `feijao` | Feijão (em grão) (40112): todos os tipos e safras, **inclusive o caupi** (gênero *Vigna*) |
| `trigo` | Trigo (em grão) (40127) |
| `arroz` e `arroz_irrigado` | Arroz (em casca) (40102): a PAM **não separa** o irrigado do sequeiro; as duas culturas recebem as mesmas linhas |
| `algodao` | Algodão herbáceo (em caroço) (40099): produção em caroço, não em pluma (o NASS dos EUA dá pluma) |
| `mandioca` | Mandioca (40119) |
| `sorgo` | Sorgo (em grão) (40125) |
| `girassol` | Girassol (em grão) (40114) |

Lista de produtos da classificação 782: [metadados da tabela 5457](https://servicodados.ibge.gov.br/api/v3/agregados/5457/metadados) (86 categorias). O feijão inclui o caupi pelas [notas técnicas da PAM 2024](https://biblioteca.ibge.gov.br/visualizacao/periodicos/66/pam_2024_v51_br_notas_tecnicas.pdf): "consideram-se, agrupadamente, todos os tipos (preto e de cores), incluindo também os diferentes gêneros (Phaseolus e Vigna)".

Ficam de fora (sem produto próprio na PAM): milheto (não existe na classificação 782), feijão-caupi (está dentro de "Feijão (em grão)" e não se separa), crotalária, nabo forrageiro, guandu e pastagem. A aveia tem produto ("Aveia (em grão)", 40103), mas o `codigo_pam` dela está vazio no catálogo: a aveia da base é a aveia-preta de cobertura, e a PAM só conta a de grão (as notas técnicas excluem "cobertura morta para o plantio direto (aveia-preta...)").

## Colunas

Uma linha por município × cultura × ano. Todos os municípios que o SIDRA devolve entram, inclusive os que não plantaram a cultura (linha com zeros).

| Coluna | Conteúdo |
|---|---|
| `municipio_id` | código IBGE de 7 dígitos (o mesmo de `brasil/municipios/municipios.csv`) |
| `cultura_id` | id da base (`agroai/base/culturas.json`) |
| `ano` | ano civil da colheita |
| `area_plantada_ha` | área plantada ou destinada à colheita (variável 8331), ha |
| `area_colhida_ha` | área colhida (216), ha |
| `producao_t` | quantidade produzida (214), t |
| `rendimento_kg_ha` | rendimento médio (112), kg/ha, como o IBGE publica |
| `valor_mil_reais` | valor da produção (215), mil R$ correntes do ano (sem correção pela inflação) |

## Símbolos do SIDRA

| No SIDRA | Significado (notas técnicas da PAM) | No CSV |
|---|---|---|
| `-` | dado numérico igual a zero, não resultante de arredondamento | `0` |
| `..` | não se aplica dado numérico | vazio |
| `...` | dado numérico não disponível | vazio |
| `X` | omitido para não identificar o informante | vazio |

Vazio é sempre "sem dado", nunca 0. Um município sem a cultura no ano vem com `-` em tudo, então a linha tem 0 em tudo, inclusive no rendimento: **para média de produtividade, use só as linhas com `area_colhida_ha` > 0**. Outros casos do download de 15/11/2026: 1.112 linhas com área plantada e o resto 0 (perda total: plantou e não colheu, rendimento 0) e 5.800 linhas inteiramente vazias, de 82 municípios quase todos urbanos (Recife, Natal, Vitória, Belo Horizonte, Barueri...) em que o IBGE publica `...` para todos os produtos no ano. Não veio nenhum `..` nem `X` nestas culturas e anos, mas o script os trata.

## Como rodar

```
python3 data/scripts/baixar_pam.py                             # 10 últimos anos, todas as culturas com codigo_pam
python3 data/scripts/baixar_pam.py --anos 5                    # 5 últimos anos
python3 data/scripts/baixar_pam.py --culturas soja,milho --saida /outra/pasta/pam.csv
```

Só `requests` fora da biblioteca padrão. São 90 chamadas (9 produtos × 10 anos) com 1 s de pausa e até 3 novas tentativas com espera (10, 30 e 90 s); levou cerca de 20 minutos em 15/11/2026. O script para sem gravar se vier um símbolo desconhecido ou um município com código fora de 7 dígitos, grava num `.tmp` e só então substitui o arquivo (rodar de novo sobrescreve, não duplica) e avisa se a saída passar de 20 MB.

## Tamanho

Em 15/11/2026: **556.400 linhas, 19,5 MB** (19.516.497 bytes), cerca de 1,95 MB por ano com 10 culturas, ou 0,2 MB por cultura e ano. Cabe no limite de ~20 MB do Git, mas com folga de só 0,5 MB: **uma cultura a mais (ex.: aveia de grão) passa de 20 MB**. Nesse caso, ou se reduz para 9 anos (`--anos 9`, ainda acima dos 5 que a média de produtividade precisa), ou se grava fora do Git (`--saida data/brutos/pam/producao_municipal.csv`). Os 5.564 municípios são os que o SIDRA devolve para a tabela. Dos 5.571 de `brasil/municipios/municipios.csv`, faltam 7, que a tabela 5457 não traz: Santa Cruz do Arari (PA), Arraial do Cabo, Nilópolis e São João de Meriti (RJ), Diadema, Ilha Comprida e São Caetano do Sul (SP). Quando o motor passar a ler a PAM, esses 7 ficam sem dado (ausente = sem dado, não 0).

## Conferência manual

Duas células conferidas em 15/11/2026 contra a API de agregados do IBGE (`servicodados.ibge.gov.br/api/v3`), uma consulta diferente da que o script usa (`apisidra`):

| Município, cultura, ano | Coluna | CSV | API de agregados |
|---|---|---|---|
| Sorriso (MT) 5107925, soja, 2024 | `producao_t` / `rendimento_kg_ha` | 2084520 / 3480 | 2084520 / 3480 ([consulta](https://servicodados.ibge.gov.br/api/v3/agregados/5457/periodos/2024/variaveis/214%7C112?localidades=N6%5B5107925%5D&classificacao=782%5B40124%5D)) |
| Unaí (MG) 3170404, feijão, 2023 | `valor_mil_reais` / `area_plantada_ha` | 222300 / 21500 | 222300 / 21500 ([consulta](https://servicodados.ibge.gov.br/api/v3/agregados/5457/periodos/2023/variaveis/215%7C8331?localidades=N6%5B3170404%5D&classificacao=782%5B40112%5D)) |

Também conferido: uma segunda rodada só do girassol 2024–2025 deu linhas idênticas às do arquivo (rodar de novo não muda nada).

---

Volta para o [`data/README.md`](../../README.md).
