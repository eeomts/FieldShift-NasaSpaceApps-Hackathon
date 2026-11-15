# 05 — Script do ZARC (janelas de plantio)

**Dono:** Pessoa 2 (Augusto; era do Yury até 15/11/2026) · **Status:** em andamento (mapa de nomes e `janelas.csv` feitos em 15/11/2026 pelo Yury; falta conferir 2 janelas no Painel e ligar ao motor) · **Depende de:** P1-01

## Por quê
As janelas de plantio oficiais (risco climático de 20 %, 30 % e 40 %) por município, tipo de solo e ciclo validam as estratégias do motor. O ZARC entra só como dado preparado, nunca consultado ao vivo.

## Entrada
- Tábua de risco do ZARC, safra vigente, no portal de dados abertos do MAPA (`dados.agricultura.gov.br`, procure "Tábua de risco ZARC"), **e o dicionário de dados**.
- Arquivo completo em `data/brutos/zarc/` (fora do Git).

## Saídas
**1. `data/brasil/zarc/mapa_culturas_zarc.csv`** (feito, PR #34): o nome exato que o ZARC usa para cada `cultura_id`. Quando o ZARC separa a cultura (1ª e 2ª safra), os nomes vêm separados por `|`, o principal primeiro.

| `cultura_id` | `nome_zarc` | `observacao` |
|---|---|---|
| `milho` | `<nome no ZARC>` | `1ª safra; a 2ª safra é outra cultura no ZARC?` |

**2. `data/brasil/zarc/janelas.csv`**: só as culturas da base.

| Coluna | Exemplo |
|---|---|
| `cultura_id` | `soja` |
| `municipio_id` | `3170206` |
| `uf` | `MG` |
| `tipo_solo` | `<classe do ZARC>` |
| `ciclo` | `<grupo de cultivar>` |
| `safra` | `2025/2026` |
| `risco_pct` | `20` |
| `inicio_decendio` / `fim_decendio` | `28` / `33` |
| `inicio_data` / `fim_data` | `10-01` / `11-30` (mês-dia) |

## Passo a passo
1. Baixe a tábua e o dicionário; registre no `data/FONTES.md`.
2. Preencha o `mapa_culturas_zarc.csv` olhando os nomes no arquivo.
3. Script `data/scripts/preparar_zarc.py`: filtra as culturas do mapa, mantém as janelas de 20/30/40 % e converte decêndio em data.
4. Decêndio: o ano tem 36 (3 por mês: dias 1–10, 11–20 e 21–fim). **Confirme no dicionário** se a numeração do ZARC segue isso.

## Pronto quando
- [x] `mapa_culturas_zarc.csv` preenchido para toda cultura que existe no ZARC (as que não existem, com observação).
- [x] `janelas.csv` gerado pelo script (`data/scripts/preparar_zarc.py`; GO, RS e BA, 24,4 MB, aceito acima de 20 MB; safra por município, ver `data/brasil/zarc/README.md`), com o tamanho dentro do limite (~20 MB); se passar, gere só as UFs da demo e avise.
- [ ] Conferência manual: 2 janelas batem com o Painel de Indicação de Riscos do ZARC.

## Próximo: ligar o ZARC ao motor
- [ ] Aprovar e implementar as regras Z1 a Z8 de `data/brasil/zarc/README.md` (chave, safra, solo SoilGrids -> classe do ZARC, grupo de ciclo, nível de manejo, união dos riscos, três mensagens de ausência, a IA só cita). O motor (`agroia/api/app/services/motor/`) ainda não lê o `janelas.csv`.
