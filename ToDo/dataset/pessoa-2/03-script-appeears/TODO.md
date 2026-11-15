# 03 — Script do AppEEARS (NDVI e umidade dos pontos da demo)

**Dono:** Pessoa 2 · **Status:** pendente · **Depende de:** 01

## Por quê
O cartão "meses em que o campo fica descoberto" usa o NDVI, e o cartão "quantos dias o solo aguenta sem chuva" usa o SMAP. O AppEEARS é assíncrono (minutos a horas), então os pontos da demo são pedidos antes.

## Entrada
- `data/demo/pontos_demo.csv`
- Conta Earthdata Login; credenciais **só em variável de ambiente** (`EARTHDATA_USER` / `EARTHDATA_PASS` ou `EARTHDATA_TOKEN`).

## Saída
`data/demo/appeears/<id_da_tarefa>/` com os CSVs **como vieram**, sem editar (ver `data/demo/appeears/README.md`).

| Produto | Camadas | Para quê |
|---|---|---|
| `MOD13Q1.061` | NDVI + qualidade (250 m, 2001–hoje) | Histórico de cobertura |
| `VNP13A1.002` | NDVI + qualidade (500 m) | Continuidade do MODIS |
| `SPL4SMGP` (versão atual) | umidade da zona das raízes | Dias que o solo aguenta |

## Passo a passo
1. Siga o guia que o time já escreveu: `docs/NasaSpaceApps-FieldShift/v1/tools/APPEEARS_AUTOMACAO.md`.
2. Script `data/scripts/baixar_appeears.py`: login → um pedido por ponto com os 3 produtos → espera ficar pronto → baixa os CSVs.
3. Nomes exatos das camadas: `GET https://appeears.earthdatacloud.nasa.gov/api/product/<produto>` (não chute).
4. Registre no `data/FONTES.md`: id da tarefa, produtos, período e data.

## Pronto quando
- [ ] Roda com `python data/scripts/baixar_appeears.py` e baixa os CSVs de todos os pontos.
- [ ] Nenhuma credencial no código ou no Git.
- [ ] Cada CSV tem a série completa do período (sem tarefa pela metade).
