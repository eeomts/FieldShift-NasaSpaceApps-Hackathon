# ZARC: janelas de plantio

Janelas oficiais de semeadura do Zoneamento Agrícola de Risco Climático (MAPA/Embrapa), por município, tipo de solo, ciclo e risco (20, 30 e 40 %). Entram como dado preparado, nunca consultado ao vivo (D-009).

| Arquivo | O que é |
|---|---|
| `mapa_culturas_zarc.csv` | `cultura_id` da base → nome exato no ZARC (`\|` separa a 1ª e a 2ª safra). Copiado para a coluna `nome_zarc` de `catalogo/culturas.csv`. |
| `janelas.csv` | Janelas das culturas da base, só **GO, RS e BA** (UFs dos pontos da demo): 277.499 linhas, 19 MB. |

## Origem

- Portal de dados abertos do MAPA, dataset "Tábua de Risco - Zoneamento Agrícola de Risco Climático" (ver `data/FONTES.md`), baixado em 15/11/2026: tábua da **safra 2025/2026** e tábua **"Perene, Olerícola e Sem Safra"**, mais o dicionário de dados 2026.
- Da tábua sem safra vêm só: mandioca (`PERENE`, portarias de 12/02/2020), milheto (`SEM SAFRA`, 23/10/2020) e o arroz irrigado de clima tropical (`SEM SAFRA`, 09/12/2020) das UFs que não estão na tábua 2025/2026.
- Os brutos ficam em `data/brutos/zarc/` (fora do Git).

## Filtros

- Só as culturas com nome no mapa. Sem ZARC: crotalária, nabo forrageiro e guandu (não existem no ZARC) e pastagem (a "Forrageira Pecuária" do ZARC não diz a espécie e varia por classe de produtividade).
- Manejo `Sequeiro` para todas; `arroz_irrigado` usa as linhas `Irrigado` do mesmo nome "Arroz".
- Só os decêndios com risco 20, 30 ou 40 (0 = não indicado).
- Com mais de uma tábua, vale a de safra mais recente para cada cultura e UF; a sem safra só entra onde nenhuma tábua de safra tem a combinação.

## Como rodar

```
python3 -I data/scripts/preparar_zarc.py data/brasil/zarc/mapa_culturas_zarc.csv data/brasil/zarc/janelas.csv \
    data/brutos/zarc/dados-abertos-tabua-de-risco-safra-2025-2026.csv \
    data/brutos/zarc/dados-abertos-tabua-de-risco-safra-perene-olericola-sem-safra.csv \
    --ufs GO,RS,BA
```

Sem `--ufs` sai o Brasil inteiro: 1,58 milhão de linhas e ~110 MB, grande demais para o Git (MG sozinho tem 19 MB). Para outra UF, troque a lista; acima de ~20 MB, gere fora do repositório.

## Colunas

| Coluna | Conteúdo |
|---|---|
| `cultura_id` | id da base (`catalogo/culturas.csv`) |
| `epoca` | 1 = 1º nome do mapa (verão, safra das águas); 2 = 2º nome (2ª safra, safrinha, safra da seca) |
| `municipio_id`, `uf` | código IBGE de 7 dígitos (`geocodigo` da tábua) e sigla |
| `tipo_solo` | `Arenoso`, `Textura Média`, `Argiloso` (tipos 1 a 3) ou `AD1` a `AD6` (classes de água disponível), conforme a cultura |
| `ciclo` | grupo de cultivar: `Grupo I` a `Grupo IV`, ou `Perene` (mandioca) |
| `nivel_manejo` | `NM1` a `NM4` onde o ZARC separa por nível de manejo do solo (na safra 2025/2026, só a soja do PR, fora deste recorte); vazio nos demais |
| `safra` | `2025/2026`, ou `SEM SAFRA` / `PERENE` para as portarias sem vigência por safra |
| `risco_pct` | 20, 30 ou 40 |
| `inicio_decendio`, `fim_decendio` | trecho contínuo de decêndios com o mesmo risco (1 a 36) |
| `inicio_data`, `fim_data` | o mesmo trecho em `MM-DD` |

Decêndios: 36 por ano, dias 1–10, 11–20 e 21–fim do mês (fevereiro até 28). A numeração está confirmada na tabela de períodos das portarias (ex.: Portaria SPA/MAPA nº 393/2025, item 3.3: período 1 = 1º a 10 de janeiro, período 6 = 21 a 28 de fevereiro). O dicionário de dados só diz "decêndios de 1 a 36".

Uma janela que atravessa o ano (dezembro → janeiro) é uma linha só, com `inicio_decendio` > `fim_decendio` (ex.: 28 → 1 = de 10-01 a 01-10 do ano seguinte). Cada linha é um risco exato; a janela "até 30 %" é a união das linhas de 20 e 30.

## Conferência manual (15/11/2026)

O Painel de Indicação de Riscos (https://mapa-indicadores.agricultura.gov.br/publico/extensions/Zarc/Zarc.html) é um painel Qlik que só funciona no navegador; não foi possível consultá-lo por script. As janelas foram conferidas contra a linha da tábua bruta, lida à parte (awk), decêndio a decêndio:

| Caso | Tábua bruta (decêndios com risco) | `janelas.csv` |
|---|---|---|
| Soja, Rio Verde/GO (5218805), AD4, Grupo II, Port. 368/2025 | 1: 20; 27: 40; 28–36: 20 | 40 % de 09-21 a 09-30 (27–27); 20 % de 10-01 a 01-10 (28→1) |
| Milho 2ª safra, Rio Verde/GO (5218805), Argiloso, Grupo I, Port. 386/2025 | 1–5: 20; 6: 30 | 20 % de 01-01 a 02-20 (1–5); 30 % de 02-21 a 02-28 (6–6) |
| Soja, Sorriso/MT (5107925), AD4, Grupo III, Port. 372/2025 (saída do Brasil inteiro) | 1: 20; 27: 40; 28–36: 20 | 40 % de 09-21 a 09-30; 20 % de 10-01 a 01-10 |
| Milho 2ª safra, Cascavel/PR (4104808), Argiloso, Grupo II, Port. 393/2025 (saída do Brasil inteiro) | 1–3: 20; 4: 30; 36: 20 | 30 % de 02-01 a 02-10 (4–4); 20 % de 12-21 a 01-31 (36→3) |

Falta conferir no Painel, no navegador, pelo menos 2 dessas janelas.

## Limitações

- Recorte só de GO, RS e BA. Outras UFs: rodar o script.
- Safra 2025/2026. A tábua 2026/2027 já está no portal (portarias até 11/11/2026) e é a vigente para a soja e o milho de verão semeados agora, mas está incompleta (trigo em 3 UFs, girassol sem o Norte). Para usá-la, passe as duas tábuas de safra: o script pega a mais recente por cultura e UF e grava a safra na coluna `safra`.
- Mandioca, milheto e o arroz irrigado tropical vêm de portarias de 2020 (sem safra); o nome "Mandioca (aipim, macaxeira)" é o único ZARC de mandioca.
- O ZARC é de sequeiro (salvo o arroz irrigado), municipal e simulado: ver `docs/NasaSpaceApps-FieldShift/v1/tools/ZARC.md`.
