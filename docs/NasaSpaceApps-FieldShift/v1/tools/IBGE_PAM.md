# IBGE PAM no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o IBGE PAM, como ele entra na ferramenta e onde o produtor vê o resultado, com um caso hipotético que junta o IBGE PAM aos outros datasets.

## O que é o IBGE PAM

A PAM (Produção Agrícola Municipal) é a pesquisa anual do IBGE sobre as lavouras de **cada município** do Brasil. Para cada cultura, temporária ou permanente, ela informa:

- área plantada e área colhida;
- quantidade produzida;
- rendimento médio (produtividade);
- valor da produção.

A série principal começa em **1974** e hoje vai até **2025**. Os dados ficam no **SIDRA**, o banco de tabelas do IBGE, e podem ser baixados por API.

A PAM não é medição de satélite nem de balança. É uma estimativa feita pelos agentes do IBGE com informantes locais, como secretarias de agricultura, extensão rural e cooperativas.

## Por que usar

**1. É o substituto brasileiro do NASS.** Nos EUA, o desafio usa o NASS QuickStats para estatísticas agrícolas. Aqui, a PAM cumpre esse papel (D-003).

**2. Diz o que de fato se planta no município.** Uma estratégia com trigo faz pouco sentido num lugar onde ninguém planta trigo e não há quem compre. A PAM mostra quais culturas têm área e mercado local.

**3. Mostra a variação da produtividade.** Com décadas de dados, dá para ver quanto o rendimento cai nos anos ruins. Essa variação é uma medida de risco que o produtor entende.

**4. Ajuda a calibrar a renda.** Produtividade e valor da produção por município dão uma base realista para a nota de "renda".

**5. Confere os mapas.** A área de soja do MapBiomas num município pode ser comparada com a área da PAM.

## Como entra no projeto

### Harmonização

- **Acesso:** API do SIDRA (`apisidra.ibge.gov.br`), que devolve JSON. Exemplo de consulta: `/values/t/5457/n6/all/v/112/p/2025/c782/40124` (rendimento médio da soja em todos os municípios em 2025). Também há a API de agregados (`servicodados.ibge.gov.br/api/v3/agregados`), com os metadados de cada tabela. No R, o pacote `sidrar`; em Python, `sidrapy`.
- **Processamento:** baixar as culturas de interesse para os 5.570 municípios, juntar ao mapa de municípios do IBGE pelo código de 7 dígitos e ligar cada célula da grade comum ao seu município. Como o volume é pequeno, dá para guardar a série inteira.

| Tabela / variável | O que é | Uso |
| --- | --- | --- |
| Tabela 5457 | Lavouras temporárias e permanentes, 1974–2025 | Série principal por cultura |
| Tabela 839 | Milho 1ª e 2ª safra separados, 2003–2025 | Peso da safrinha no município |
| `v/8331` | Área plantada ou destinada à colheita (ha) | Culturas comuns no local |
| `v/216` | Área colhida (ha) | Perda de área (plantada menos colhida) |
| `v/214` | Quantidade produzida (t) | Produção total |
| `v/112` | Rendimento médio (kg/ha) | Produtividade e variação |
| `v/215` | Valor da produção (mil R$) | Base para a renda |
| `c782` | Produto (ex.: 40124 soja, 40122 milho, 40112 feijão, 40125 sorgo, 40127 trigo) | Filtrar a cultura |

> Os códigos acima foram conferidos nos metadados do SIDRA em novembro de 2026. Confirmar nas páginas oficiais as mudanças de método ao longo da série, as moedas antigas do valor da produção (antes de 1994) e se há tabela que separe as safras do feijão.

### Indicadores calculados

- **Culturas do município:** as que somam mais área nos últimos 5 anos.
- **Produtividade típica:** mediana do rendimento nos últimos 10 anos.
- **Anos ruins:** frequência de anos com rendimento 20% abaixo da mediana.
- **Perda de área:** diferença entre área plantada e área colhida.
- **Tendência:** a área da cultura cresce, cai ou fica estável.
- **Valor por hectare:** valor da produção × 1.000 ÷ área colhida, em R$/ha, corrigido pela inflação (IPCA). É a base do critério de renda.
- **Rendimento em anos secos:** média do rendimento nos anos secos ÷ média nos demais − 1. Os anos secos vêm da chuva (GPM IMERG, INMET) e do NASA POWER no local; é aqui que a PAM e os dados de clima se cruzam.
- **Escala regional:** usar a **microrregião** (`/n9/`) como padrão, por ser mais estável que o município, e mostrar o município como detalhe.

### Nível de confiança

O valor é do **município**, não do talhão. Um município grande pode misturar várzea e chapada. A queda de rendimento num ano é cruzada com a chuva (GPM IMERG, INMET) e com a água no solo (GLDAS, SMAP L4) para saber se veio do clima.

## Onde o produtor vê isso

**Etapa 1, culturas possíveis.** A lista de culturas sugeridas mostra quais já têm área no município.

**Cartão da estratégia, em "Renda".** Exemplo, com números ilustrativos: "No seu município, o milho rendeu em média 6,2 t/ha nos últimos 10 anos, com 2 anos ruins."

**Glossário.** Explica que o número é a média do município e que a lavoura dele pode estar acima ou abaixo.

## Caso hipotético: IBGE PAM junto com os outros dados

> Caso inventado, com números ilustrativos.

### O produtor

A Sra. Helena planta grãos perto de Itapeva, no sudoeste de São Paulo, região de transição entre Mata Atlântica e Cerrado, com inverno frio.

- **Rotação atual:** soja todo verão (outubro a março); no inverno, trigo em alguns anos e pousio nos outros.
- **Irrigação:** não tem.
- **Prioridades:** renda alta; solo e nitrogênio médios.
- **Mercado:** soja, milho, trigo e feijão. Há cerealista e moinho na região.

### O que cada dataset diz sobre o local

| Dataset | O que encontra (hipotético) |
| --- | --- |
| **IBGE PAM** | No município, soja, milho, trigo e feijão têm área relevante. A área de trigo cresceu 40% em 10 anos. O rendimento do milho de verão é estável; o da soja caiu mais de 20% em 3 dos últimos 10 anos. |
| **IBGE PAM (tabela 839)** | Quase todo o milho é de 1ª safra; a safrinha é pequena. |
| GPM IMERG / INMET | Os 3 anos ruins da soja tiveram veranico em janeiro. |
| GLDAS / SMAP L4 | Zona das raízes abaixo do normal em janeiro nesses anos. |
| NASA POWER | Geada em julho em 4 de 10 anos. |
| MapBiomas | Soja todo ano no talhão desde 2008. |
| HLS | No inverno, trigo em 4 dos últimos 8 anos; nos outros, solo com pouca palha. |
| IBGE PAM (valor da produção) | Valor da produção por hectare do trigo e do milho mostra mercado regional ativo. |

### Onde os dados se completam

**A soja todo verão concentra o risco.** A PAM mostra que a soja do município perde rendimento nos anos de veranico. O IMERG e o GLDAS confirmam que esses anos foram secos em janeiro. Alternar com milho de verão espalha o risco.

**O mercado existe.** A PAM mostra trigo crescendo e milho estável no município. Isso torna realista uma estratégia com essas culturas.

**A safrinha não é o caminho aqui.** A tabela 839 mostra pouca safrinha no município, e o POWER mostra geada no inverno. O inverno é de trigo ou de cobertura, não de milho.

### Regras ativadas

- **Monocultura de verão com quedas recorrentes** aumenta o peso da rotação de verão.
- **Cultura com área e tendência de alta no município** aumenta a nota de renda dessa cultura.
- **Geada frequente no inverno** reduz o peso de culturas sensíveis ao frio nessa época.

### Comparação das estratégias

| Critério | A: atual (soja → trigo ou pousio) | B: soja → aveia-preta + ervilhaca de cobertura | C: soja e milho alternados no verão → trigo |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●○○ | ●●○○○ |
| Solo | ●●○○○ | ●●●●○ | ●●●●○ |
| Nitrogênio | ●●○○○ | ●●●●○ | ●●●○○ |
| Erosão | ●●○○○ | ●●●●○ | ●●●●○ |
| Forragem | ●○○○○ | ●●●○○ | ●●○○○ |
| Renda | ●●●○○ | ●●○○○ | ●●●●○ |

Com os pesos da Sra. Helena (renda alta, solo e nitrogênio médios), a **estratégia C** fica em primeiro, com a B logo atrás. A B é melhor em nitrogênio, mas a C ganha em renda, que pesa mais. A ferramenta mostra as duas e explica a diferença.

### Cartão da estratégia C

> **Resumo:** uma opção é alternar soja e milho no verão e manter trigo no inverno.
>
> **Por que foi sugerida:** no seu município, a soja perdeu mais de 20% do rendimento em 3 dos últimos 10 anos, sempre com veranico em janeiro; o milho de verão foi mais estável, e o trigo tem área e mercado crescentes.
>
> **Evidências:** rendimento e área por cultura (IBGE PAM, confiança média por ser média do município); veranico nos anos ruins (GPM IMERG e INMET, confiança alta); solo seco em janeiro (GLDAS e SMAP L4, confiança alta); trigo no inverno em metade dos anos (HLS, confiança alta).
>
> **Benefícios:** risco espalhado entre duas culturas de verão, mais palha do milho para o plantio direto e solo coberto no inverno.
>
> **Lacunas:** não sabemos a produtividade da sua lavoura em relação à média do município, nem o custo do milho na sua propriedade.
>
> **Riscos para revisão local:** o trigo sofre com geada no florescimento; confirmar com o agrônomo a cultivar e a época dentro da janela do ZARC. Avaliar o frete e a venda do milho antes de mudar.

## Conclusão

A PAM traz a voz da **região**: o que se planta, quanto rende e quantas vezes dá errado. Os satélites explicam por que um ano foi ruim; a PAM mostra o tamanho do prejuízo e se há mercado para mudar. Em outro município, a mesma regra poderia apontar o feijão ou o sorgo, conforme o que a PAM mostrar.

## Limitações

- **Escala municipal:** um valor por município e por ano; não descreve o talhão.
- **Estimativa, não medição:** depende de informantes locais.
- **Atraso:** cada ano sai só no segundo semestre do ano seguinte (os dados de 2025 foram atualizados em outubro de 2026).
- **Safras misturadas:** fora do milho, a PAM nem sempre separa safra e safrinha.
- **Mudanças de município:** municípios criados depois de 1974 quebram a série.
- **Corte mínimo:** produto com menos de 1 ha e 1 t no município fica fora da pesquisa, então culturas pequenas aparecem como ausentes.
- **Só 64 produtos:** culturas de cobertura, como braquiária e crotalária, provavelmente não aparecem.
- **Valor nominal:** o valor da produção precisa ser corrigido pelo IPCA (tabela 1737 do SIDRA) para comparar anos.
- **Ano civil:** quando a colheita passa do ano civil, conta no ano em que se colheu a maior parte, então a safrinha pode cair no ano seguinte ao plantio.
- **Tratamento:** usar mediana e frequência de anos ruins, cruzar quedas com dados de clima e avisar que é média do município.

## Guia técnico: API do SIDRA

Referência para quem vai implementar a coleta. Os códigos de tabela, variáveis e produtos citados em *Harmonização* foram conferidos nos metadados do SIDRA; o resto desta seção vem da documentação dos clientes oficiais e comunitários (`sidrar`, `sidrapy`, `DadosAbertosBrasil`) e da ajuda oficial (`apisidra.ibge.gov.br/home/ajuda`). Itens com ⚠️ devem ser confirmados na primeira chamada real.

### APIs do IBGE usadas

| API | Endereço base | Para quê |
| --- | --- | --- |
| **SIDRA** | `https://apisidra.ibge.gov.br/values` | Baixar os dados da tabela 5457 |
| **Agregados v3** | `https://servicodados.ibge.gov.br/api/v3/agregados` | Metadados: variáveis, classificações, códigos dos produtos, períodos |
| **Localidades v1** | `https://servicodados.ibge.gov.br/api/v1/localidades` | Código IBGE do município, da microrregião e da UF |
| **Malhas v3** (opcional) | `https://servicodados.ibge.gov.br/api/v3/malhas` | Contorno do município para o mapa |

Todas são abertas, sem login, e devolvem JSON.

### Anatomia da URL

```
https://apisidra.ibge.gov.br/values/t/5457/n6/<município>/v/8331,216,214,112,215/p/last%2010/c782/40124,40122
                                    └─┬──┘└──────┬──────┘└──────────┬─────────┘└────┬────┘└──────┬──────┘
                                   tabela  nível + local        variáveis        período   produto (soja, milho)
```

| Bloco | Significado | Exemplos |
| --- | --- | --- |
| `/t/{tabela}` | Tabela do SIDRA | `/t/5457` (todas as lavouras), `/t/839` (milho 1ª e 2ª safra), `/t/1737` (IPCA) |
| `/n{nível}/{locais}` | Nível territorial | `n1` Brasil, `n3` UF, `n6` município, `n9` microrregião, `n8` mesorregião; um código, vários separados por vírgula ou `all` |
| `/v/{variáveis}` | Variáveis | `/v/214,112`, `/v/allxp` (todas, sem as percentuais) |
| `/p/{períodos}` | Anos | `last`, `last%2010`, `2015-2024`, `2021,2024`, `all` |
| `/c782/{produtos}` | Produto | `/c782/40124` ou `/c782/all` |
| `/h/n` (opcional) | Resposta sem a linha de cabeçalho | — |

⚠️ Pedir `/n6/all` com muitas variáveis e anos pode estourar o limite de valores por consulta. Divida por UF ou por produto.

### Estrutura da resposta

A API devolve uma lista JSON. **O primeiro item é o cabeçalho**, que diz o que cada chave significa; os demais são as linhas. As dimensões (`D1`, `D2`…) seguem a ordem dos blocos na URL ⚠️.

```json
[
  {"NC": "Nível Territorial (Código)", "MN": "Unidade de Medida", "V": "Valor",
   "D1C": "Município (Código)", "D1N": "Município", "D2C": "Variável (Código)",
   "D3C": "Ano (Código)", "D4C": "Produto das lavouras temporárias e permanentes (Código)"},
  {"NC": "6", "MN": "Toneladas", "V": "14800", "D1C": "<código>", "D2C": "214", "D3C": "2024", "D4C": "40125"}
]
```

- `V` vem como **texto**: converta para número.
- Símbolos ⚠️: `-` costuma indicar zero absoluto; `..`, `...` e `X` indicam dado não disponível, não aplicável ou omitido por sigilo. **Nunca trate `..` ou `X` como zero.**

### Descobrir códigos

```python
import requests

# Produtos (classificação 782) e seus códigos na tabela 5457
meta = requests.get("https://servicodados.ibge.gov.br/api/v3/agregados/5457/metadados").json()
for c in meta["classificacoes"]:
    print(c["id"], c["nome"])
    for cat in c["categorias"][:10]:
        print("   ", cat["id"], cat["nome"])

# Código IBGE de um município (a resposta também traz a microrregião, campo "microrregiao" ⚠️)
muns = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados/GO/municipios").json()
codigo = next(m["id"] for m in muns if m["nome"] == "Rio Verde")
```

### Implementação em Python

```python
import pandas as pd, requests

VARIAVEIS = {8331: "area_plantada_ha", 216: "area_colhida_ha", 214: "quantidade_t",
             112: "rendimento_kg_ha", 215: "valor_mil_reais"}

def montar_url(nivel, localidade, codigos_produtos, periodo="last 10"):
    v = ",".join(str(k) for k in VARIAVEIS)
    c = ",".join(str(p) for p in codigos_produtos)
    return (f"https://apisidra.ibge.gov.br/values/t/5457/n{nivel}/{localidade}"
            f"/v/{v}/p/{periodo.replace(' ', '%20')}/c782/{c}")

def para_tabela(dados):
    cabecalho, linhas = dados[0], dados[1:]
    df = pd.DataFrame(linhas).rename(columns=cabecalho)
    df["Valor"] = pd.to_numeric(df["Valor"].replace({"-": "0"}), errors="coerce")  # ".." e "X" viram vazio
    return df.pivot_table(index=["Produto das lavouras temporárias e permanentes", "Ano"],
                          columns="Variável", values="Valor").reset_index()

url = montar_url(nivel=9, localidade="<microrregião>", codigos_produtos=[40124, 40122, 40125])
tabela = para_tabela(requests.get(url, timeout=60).json())
```

Alternativas prontas: `sidrapy.get_table(table_code="5457", territorial_level="6", ibge_territorial_code="<cód.>", period="last 10")` em Python, ou `get_sidra(api="/t/5457/n6/<cód.>/v/214/p/last%2010/c782/all")` com o pacote `sidrar` em R.

### Boas práticas

1. Baixe e guarde antes da demo, com cache por microrregião e produto.
2. Use a microrregião como padrão e mostre o município como detalhe.
3. Confirme os códigos nos metadados da tabela 5457 antes da primeira coleta.
4. Nunca trate `..` ou `X` como zero.
5. Corrija o valor pela inflação antes de comparar anos.
6. Cite sempre "IBGE/PAM" e a escala ao lado do número.
7. Peça só as variáveis e os produtos necessários, para não estourar o limite da API.
