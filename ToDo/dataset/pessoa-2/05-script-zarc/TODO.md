# 05 — Script do ZARC (janelas de plantio)

**Dono:** Pessoa 2 (Augusto; era do Yury até 15/11/2026) · **Status:** em andamento (falta a conferência no Painel do ZARC) · **Depende de:** P1-01

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

**2. `data/brasil/zarc/janelas.csv.gz`** (Brasil inteiro, só as culturas da base): uma linha por cultura × época × município × solo × ciclo × nível de manejo × safra, com os 36 decêndios numa coluna. O formato de "uma linha por janela" daria ~100 MB; assim são 548.752 linhas, 47 MB de texto e 2,5 MB em gzip (decisão do Augusto, 15/11/2026). Leia com `gzip.open(..., "rt")`, ou direto com pandas/DuckDB.

| Coluna | Exemplo |
|---|---|
| `cultura_id` | `soja` |
| `epoca` | `1` (safra principal) ou `2` (2ª safra: safrinha, feijão da seca) |
| `municipio_id` | `5218805` |
| `uf` | `GO` |
| `tipo_solo` | `Arenoso`, `Textura Média`, `Argiloso` ou `AD1` a `AD6` (água disponível), como no ZARC |
| `ciclo` | `Grupo I` a `Grupo IV` |
| `nivel_manejo` | vazio; `1` a `4` só nas linhas da soja por Nível de Manejo (NM1–NM4) |
| `safra` | `2025/2026` ou `sem safra` (arroz irrigado da tábua de perenes) |
| `riscos` | 36 caracteres, um por decêndio: `2` = 20 %, `3` = 30 %, `4` = 40 %, `0` = não indicado |

A data de cada decêndio sai de `decendio_para_datas()` no próprio script.

**3. `data/brasil/zarc/portarias.csv`**: a portaria do MAPA de cada cultura × época × UF × safra, a fonte de cada linha (fica fora do `janelas.csv.gz` para não repetir em 550 mil linhas).

## Passo a passo
1. Baixe a tábua e o dicionário; registre no `data/FONTES.md`.
2. Preencha o `mapa_culturas_zarc.csv` olhando os nomes no arquivo.
3. Script `data/scripts/preparar_zarc.py`: filtra as culturas do mapa, mantém as janelas de 20/30/40 % e converte decêndio em data.
   - **Manejo:** o motor é de sequeiro, então filtre `Cod_Outros_Manejos = 1` (Sequeiro) em **todas** as culturas; a tábua tem linhas irrigadas de trigo, feijão, arroz e aveia, entre outras. A única exceção é o `arroz_irrigado`, que usa `Cod_Outros_Manejos = 2` (Irrigado).
   - Uma janela com `fim` menor que `início` atravessa o ano (ex.: decêndio 34 a 3).
4. Decêndio: o ano tem 36 (3 por mês: dias 1–10, 11–20 e 21–fim). O dicionário só diz "decêndios de 1 a 36"; a conferência no Painel (abaixo) fecha a dúvida.

## Pronto quando
- [x] `mapa_culturas_zarc.csv` preenchido para toda cultura que existe no ZARC (as que não existem, com observação).
- [x] `janelas.csv.gz` gerado pelo script (2,5 MB comprimido; ver o formato acima).
- [ ] Conferência manual: 2 janelas batem com o Painel de Indicação de Riscos do ZARC. Sugestão: soja em Rio Verde (GO), solo AD4, Grupo II, que no arquivo dá 40 % em 21–30/09 e 20 % de 01/10 a 10/01; e trigo em Passo Fundo (RS), AD4, Grupo II, que dá 20 % de 01/06 a 31/07.

## Achado para o time
Irecê (BA), o ponto `semiarido_1` da demo, **não tem janela de sequeiro** de milho, feijão nem feijão-caupi na tábua 2025/2026. Das culturas de grão da base, só o sorgo granífero aparece lá (o feijão de Irecê é só irrigado). A rotação atual do ponto (milho + feijão consorciados) fica sem a referência do ZARC.
