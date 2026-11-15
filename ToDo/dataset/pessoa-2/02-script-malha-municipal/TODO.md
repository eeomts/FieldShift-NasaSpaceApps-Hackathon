# 02 — Script da malha municipal (IBGE)

**Dono:** Pessoa 2 · **Status:** em revisão

## Por quê
O backend descobre o município da fazenda pelo ponto no mapa. É isso que liga o produtor à PAM e ao ZARC, sem perguntar nada a ele.

## Saídas
**1. `data/brasil/municipios/municipios.csv`**

| Coluna | Exemplo |
|---|---|
| `municipio_id` | `5218805` (7 dígitos) |
| `nome` | `Rio Verde` |
| `uf` | `GO` |

**2. `data/brasil/municipios/municipios.geojson`**: os polígonos, com `municipio_id` em `properties`, na resolução mais leve que a API oferecer.

## Passo a passo
1. Script `data/scripts/baixar_malha_municipal.py` (regras em `ToDo/README.md`).
2. Nomes e UF: `https://servicodados.ibge.gov.br/api/v1/localidades/municipios`
3. Polígonos: API de malhas v3 do IBGE, país inteiro dividido por município, em GeoJSON, qualidade mínima **[verificar os parâmetros exatos na documentação]**:
   `https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?intrarregiao=municipio&formato=application/vnd.geo+json&qualidade=minima`
4. Confira que a propriedade de código no GeoJSON tem os mesmos 7 dígitos do CSV (renomeie para `municipio_id` se vier com outro nome).
5. Registre no `data/FONTES.md`.

## Pronto quando
- [ ] ~5.570 municípios no CSV e no GeoJSON, com os mesmos códigos.
- [ ] GeoJSON até ~20 MB (se passar, guarde em `data/brutos/` e avise o backend).
- [ ] Teste: o ponto de Rio Verde (-17.80, -50.92) cai dentro do polígono `5218805` (qualquer ferramenta: geojson.io, QGIS ou `shapely`).
