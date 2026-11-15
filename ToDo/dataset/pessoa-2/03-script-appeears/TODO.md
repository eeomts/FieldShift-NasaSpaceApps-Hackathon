# 03 — Script do AppEEARS (NDVI e umidade dos pontos da demo)

**Dono:** Pessoa 2 · **Status:** em andamento (pedidos na fila do AppEEARS) · **Depende de:** 01

## Por quê
O cartão "meses em que o campo fica descoberto" usa o NDVI, e o cartão "quantos dias o solo aguenta sem chuva" usa o SMAP. O AppEEARS é assíncrono (minutos a horas), então os pontos da demo são pedidos antes.

## Entrada
- `data/demo/pontos_demo.csv`
- Conta Earthdata Login; credenciais **nunca no código**: variável de ambiente (`EARTHDATA_TOKEN`, ou `EARTHDATA_USER` / `EARTHDATA_PASS`) ou o `~/.netrc` (`machine urs.earthdata.nasa.gov login ... password ...`).

## Saída
`data/demo/appeears/<id_da_tarefa>/`, uma pasta por pedido, com o bundle **como veio**, sem editar (ver `data/demo/appeears/README.md`). O `data/demo/appeears/tarefas.json` diz qual pasta é de qual pedido.

| Pedido | Produto | Camadas | Período | Para quê |
|---|---|---|---|---|
| `ndvi` | `MOD13Q1.061` | NDVI, `VI_Quality`, `pixel_reliability` (250 m) | 2001–hoje | Histórico de cobertura |
| `ndvi` | `VNP13A1.002` | NDVI, `VI_Quality`, `pixel_reliability` (500 m) | 2012–hoje (início do produto) | Continuidade do MODIS |
| `smap` | `SPL4SMGP.008` (versão mais nova, descoberta pela API) | `sm_rootzone` e `sm_surface` (9 km, a cada 3 h) | 31/03/2015–hoje (início do produto) | Dias que o solo aguenta |

## Passo a passo
1. Siga o guia que o time já escreveu: `docs/NasaSpaceApps-FieldShift/v1/tools/APPEEARS_AUTOMACAO.md`.
2. Script `data/scripts/baixar_appeears.py`: login → **dois pedidos**, cada um com todos os pontos e a própria data de início: `ndvi` (MOD13Q1 + VNP13A1) e `smap` (SPL4SMGP), separados para o NDVI não esperar o SMAP → espera ficar pronto → baixa os arquivos. Rodar de novo reaproveita os pedidos (`--novo` força pedidos novos).
3. Nomes exatos das camadas: `GET https://appeears.earthdatacloud.nasa.gov/api/product/<produto>` (não chute).
4. Registre no `data/FONTES.md`: id da tarefa, produtos, período e data.

## Pronto quando
- [ ] Roda com `python data/scripts/baixar_appeears.py` e baixa os CSVs de todos os pontos.
- [ ] Nenhuma credencial no código ou no Git.
- [ ] Cada CSV tem a série completa do período (sem tarefa pela metade).
