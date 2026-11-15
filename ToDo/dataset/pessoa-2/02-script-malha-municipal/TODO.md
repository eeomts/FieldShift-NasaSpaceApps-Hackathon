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
- [x] ~5.570 municípios no CSV e no GeoJSON, com os mesmos códigos: 5.571 no CSV e 5.570 no GeoJSON. A exceção é Boa Esperança do Norte (MT, 5101837), criado recentemente e ainda sem polígono na API (o script avisa; registrado no `data/FONTES.md`).
- [x] GeoJSON até ~20 MB: 3,3 MB.
- [x] Teste: o ponto de Rio Verde (-17.80, -50.92) cai dentro do polígono `5218805` (qualquer ferramenta: geojson.io, QGIS ou `shapely`). Conferido por ray casting em 14/11/2026; os 3 pontos da demo também caem nos municípios certos (5218805 Rio Verde, 4314100 Passo Fundo, 2914604 Irecê).

## Para o backend (tarefa futura: descobrir o município pelo ponto)
- Se o ponto não cair em nenhum polígono (Boa Esperança do Norte, ou um buraco da malha simplificada), a resposta é **"município desconhecido"**: nunca o vizinho mais próximo, nunca 0.
- A malha é de qualidade mínima (divisas simplificadas): perto de uma divisa, a tela mostra o município como **"município aproximado, confirme"** e deixa o produtor corrigir.
