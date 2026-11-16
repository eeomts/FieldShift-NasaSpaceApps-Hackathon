# ZARC: janelas de plantio

Janelas oficiais de semeadura do Zoneamento Agrícola de Risco Climático (MAPA/Embrapa), por município, tipo de solo, ciclo e risco (20, 30 e 40 %). Entram como dado preparado, nunca consultado ao vivo (D-009). **O motor ainda não lê este arquivo**: as regras para isso estão em "Regras para o motor usar o ZARC" (tarefa aberta no ToDo).

| Arquivo | O que é |
|---|---|
| `mapa_culturas_zarc.csv` | `cultura_id` da base → nome exato no ZARC (`\|` separa a 1ª e a 2ª safra). Copiado à mão para a coluna `nome_zarc` de `catalogo/culturas.csv` (um teste confere que os dois batem). |
| `janelas.csv` | Janelas das culturas da base, só **GO, RS e BA** (UFs dos pontos da demo). Em 15/11/2026: 363.514 janelas, 24,4 MB. **Fica fora do Git**: gere com `scripts/preparar_zarc.py`. |

A chave das janelas é `cultura_id` (mais `epoca` e `municipio_id`), não o nome do ZARC: `arroz` (sequeiro) e `arroz_irrigado` têm o mesmo nome "Arroz" e são separados pelo manejo.

## Origem

- Portal de dados abertos do MAPA, dataset "Tábua de Risco - Zoneamento Agrícola de Risco Climático" (ver `data/FONTES.md`), baixado em 15/11/2026: tábuas das **safras 2026/2027 e 2025/2026**, tábua **"Perene, Olerícola e Sem Safra"** e o dicionário de dados 2026.
- Da tábua sem safra vêm só: mandioca (`PERENE`, portarias de 12/02/2020), milheto (`SEM SAFRA`, 23/10/2020) e o arroz irrigado de clima tropical (`SEM SAFRA`, 09/12/2020), onde nenhuma tábua de safra tem o município.
- Os brutos ficam em `data/brutos/zarc/` (fora do Git).

## Filtros e escolha da safra

- Só as culturas com nome no mapa. **Sem ZARC**: crotalária, nabo forrageiro e guandu (não existem no ZARC), pastagem (a "Forrageira Pecuária" não diz a espécie e varia por classe de produtividade) e **aveia** (o ZARC é da aveia de grão; a da base é a aveia-preta de cobertura).
- Manejo `Sequeiro` para todas; `arroz_irrigado` usa as linhas `Irrigado` do mesmo nome "Arroz".
- Só os decêndios com risco 20, 30 ou 40 (0 = não indicado).
- **Safra por município** (decisão do usuário, 15/11/2026): para cada cultura, nome e município vale a safra mais recente que tem aquele município (2026/2027; se faltar, 2025/2026). A tábua sem safra só entra onde nenhuma tábua de safra tem o município. A coluna `safra` diz de onde veio cada linha.

### ⚠️ Municípios que vêm da safra 2025/2026

Na tábua, um município ausente quase sempre quer dizer que **o ZARC não indica o plantio ali** (linhas "tudo zero" são raras: 2.836 de 1,13 milhão na 2026/2027). Os municípios abaixo estão na 2025/2026 e **não estão na portaria vigente (2026/2027)**. Para eles, o arquivo mostra a janela da safra passada, que a portaria nova não traz. Quem usar estas linhas deve avisar isso ao produtor.

- **Milho 1ª safra, BA (44 de 295)**: Araci, Bom Jesus da Lapa, Boquira, Caculé, Caetité, Candiba, Cândido Sales, Carinhanha, Casa Nova, Condeúba, Cordeiros, Guajeru, Guanambi, Ibiassucê, Igaporã, Ipirá, Iuiu, Jacaraci, Licínio de Almeida, Macaúbas, Malhada, Matina, Mortugaba, Palmas de Monte Alto, Paratinga, Pé de Serra, Pindaí, Piripá, Presidente Jânio Quadros, Quijingue, Remanso, Retirolândia, Riacho de Santana, Rio do Antônio, Santa Brígida, Santaluz, São Domingos, Sebastião Laranjeiras, Serra do Ramalho, Sítio do Mato, Tanque Novo, Tremedal, Urandi, Valente. São do semiárido; a portaria nova da BA (Port. 217 de 10/07/2026) não os traz. Ex.: em Guanambi o melhor risco é 30 %, num decêndio só.
- **Girassol, BA (33 de 345)**: Bom Jesus da Lapa, Cansanção, Canudos, Capim Grosso, Carinhanha, Casa Nova, Gavião, Gentio do Ouro, Guanambi, Ipupiara, Itaguaçu da Bahia, Itiúba, Iuiu, Malhada, Matina, Morpará, Nordestina, Nova Fátima, Palmas de Monte Alto, Paulo Afonso, Ponto Novo, Queimadas, Remanso, Riacho de Santana, Santaluz, São Domingos, São José do Jacuípe, Sebastião Laranjeiras, Serra do Ramalho, Sento Sé, Sítio do Mato, Valente, Xique-Xique.
- **Girassol, GO (25 de 246)**: Alto Horizonte, Amaralina, Aragarças, Araguapaz, Aruanã, Bonópolis, Britânia, Campos Verdes, Iaciara, Itapirapuã, Jussara, Matrinchã, Montes Claros de Goiás, Mozarlândia, Mundo Novo, Mutunópolis, Nova Crixás, Novo Brasil, Novo Planalto, Porangatu, Santa Fé de Goiás, Santa Tereza de Goiás, Santa Terezinha de Goiás, São Miguel do Araguaia, Uirapuru.
- **Girassol, RS (6 de 497)**: Cambará do Sul, Chuí, Jaquirana, Santa Vitória do Palmar, São Francisco de Paula, Vacaria.
- **Trigo de GO (196 municípios) e da BA (130)**: todos da 2025/2026, porque a 2026/2027 ainda não tem trigo nessas UFs (não é município retirado).

## Como rodar

```
python3 -I data/scripts/preparar_zarc.py              # GO, RS e BA, todas as tábuas de data/brutos/zarc/
python3 -I data/scripts/preparar_zarc.py --ufs MT,PR  # outras UFs
python3 -I data/scripts/preparar_zarc.py --todas --saida /outra/pasta/janelas.csv   # Brasil inteiro (fora do Git)
```

O script lê em streaming, usa só a biblioteca padrão, imprime no stderr as linhas por cultura, UF e safra e o tamanho, avisa acima de 20 MB e **sai com código 1 sem gravar** se a mesma combinação aparecer com riscos diferentes. Duas rodadas dão o mesmo arquivo (sha256 conferido em 15/11/2026). Brasil inteiro em 15/11/2026: 1.815.506 janelas, 122,4 MB (~70 s, ~1,7 GB de memória).

## Colunas

| Coluna | Conteúdo |
|---|---|
| `cultura_id` | id da base (`catalogo/culturas.csv`) |
| `epoca` | 1 = 1º nome do mapa (verão, safra das águas); 2 = 2º nome (2ª safra, safrinha, safra da seca) |
| `municipio_id`, `uf` | código IBGE de 7 dígitos (`geocodigo` da tábua) e sigla |
| `tipo_solo` | `Arenoso`, `Textura Média`, `Argiloso` (tipos 1 a 3) ou `AD1` a `AD6` (classes de água disponível). Depende da cultura **e da safra**: na 2026/2027, milho e girassol passaram a usar AD, então a mesma cultura pode ter os dois sistemas no arquivo |
| `ciclo` | grupo de cultivar: `Grupo I` a `Grupo IV`, ou `Perene` (mandioca) |
| `nivel_manejo` | `NM1` a `NM4` onde o ZARC separa por nível de manejo do solo (neste recorte, só a soja do RS na 2026/2027); vazio nos demais |
| `safra` | `2026/2027`, `2025/2026`, ou `SEM SAFRA` / `PERENE` para as portarias sem vigência por safra |
| `risco_pct` | 20, 30 ou 40 |
| `inicio_decendio`, `fim_decendio` | trecho contínuo de decêndios com o mesmo risco (1 a 36) |
| `inicio_data`, `fim_data` | o mesmo trecho em `MM-DD` |

Decêndios: 36 por ano, dias 1–10, 11–20 e 21–fim do mês (fevereiro até 28; o 29/02 de ano bissexto pertence ao decêndio 6). A numeração está confirmada na tabela de períodos das portarias (Portaria SPA/MAPA nº 393/2025, item 3.3); o dicionário de dados só diz "decêndios de 1 a 36".

Uma janela que atravessa o ano é uma linha só, com `inicio_decendio` > `fim_decendio` (ex.: 28 → 1 = de 10-01 a 01-10). Cada linha é um risco exato; a janela "até 30 %" é a união das linhas de 20 e 30.

**Desvios da especificação da tarefa**, justificados: colunas `epoca` (sem ela, milho, feijão e sorgo de 1ª e 2ª safra se misturam) e `nivel_manejo` (a soja do RS da 2026/2027 tem quatro níveis); janela que vira o ano numa linha só; recorte por UF (o Brasil passa de 120 MB); safra mista por município (acima); tamanho de 24,4 MB, acima dos ~20 MB pedidos (aceito pelo usuário; o GitHub só avisa a partir de 50 MB).

## Conferência manual (15/11/2026)

O Painel de Indicação de Riscos (https://mapa-indicadores.agricultura.gov.br/publico/extensions/Zarc/Zarc.html) é um painel Qlik que só funciona no navegador. As janelas foram conferidas contra a linha da tábua bruta, decêndio a decêndio:

| Caso | Tábua bruta (decêndios com risco) | `janelas.csv` |
|---|---|---|
| Soja, Rio Verde/GO (5218805), AD4, Grupo II, 2026/2027, Port. 198 de 03/07/2026 | 1: 20; 27: 40; 28–36: 20 | 40 % 27–27 (09-21 a 09-30); 20 % 28→1 (10-01 a 01-10) |
| Soja, Passo Fundo/RS (4314100), AD4, Grupo II, NM1, 2026/2027, Port. 209 de 03/07/2026 | 1–3: 30; 28–34: 20; 35–36: 30 | 20 % 28–34 (10-01 a 12-10); 30 % 35→3 (12-11 a 01-31). Com NM4: 20 % 28→3 (10-01 a 01-31) |
| Milho 1ª safra, Guanambi/BA (2911709), Argiloso, Grupo I, 2025/2026, Port. 174 de 27/05/2025 (município fora da 2026/2027) | 31: 30; 32: 40 | 30 % 31–31; 40 % 32–32 |
| Milheto, Passo Fundo/RS (4314100), Argiloso, Grupo I, SEM SAFRA, Port. 349 de 23/10/2020 (vira o ano) | 1–4: 20; 29–36: 20 | 20 % 29→4 (10-11 a 02-10) |

**Conferência no Painel (15/11/2026, no navegador)**: com os filtros safra 2026\2027, Sequeiro, clima "Não se aplica", Grupo II e AD4, o Painel mostrou para a soja de **Rio Verde/GO** dec1 = 20, dec27 = 40 e dec28 a dec36 = 20; e para a soja de **Passo Fundo/RS** com nível de manejo 1 (NM1) dec1 a dec3 = 30, dec28 a dec34 = 20 e dec35 a dec36 = 30. Os dois casos batem decêndio a decêndio com o `janelas.csv` (linhas 1 e 2 da tabela acima).

## Regras para o motor usar o ZARC (a implementar; tarefa no ToDo)

O motor ainda não lê `janelas.csv`. Antes de ligar, seguir estas regras (propostas na revisão de 15/11/2026, a aprovar com o time):

- **Z1 Chave**: `cultura_id` + `epoca` + `municipio_id` (IBGE do ponto). Época 1 = cultura de verão; 2 = 2ª safra.
- **Z2 Safra**: usar a linha que o arquivo tem e citar "ZARC/MAPA, safra X". Se a safra for anterior à vigente, dizer isso ao produtor (municípios da lista acima). Futuro: `portarias.csv` (cultura_id, epoca, uf, safra, portaria).
- **Z3 Solo**: a classe depende da cultura e da safra (tipo 1-3 de textura ou AD1-AD6). Ordem: resposta do produtor no cadastro, depois SoilGrids (argila, areia e silte), depois nenhuma. Os limites e a fórmula vêm da norma do MAPA, transcritos com a fonte; a IA não calcula. Sem solo: usar só os decêndios indicados em todas as classes do município (interseção, o mais seguro) e dizer "depende do seu solo".
- **Z4 Ciclo**: usar o grupo de cultivar informado pelo produtor; a tabela de ciclo para grupo vem da portaria de cada cultura. Sem a informação: interseção dos grupos presentes.
- **Z5 Nível de manejo** (soja do RS): NM1 por padrão (o mais restritivo); NM maior só se o produtor declarar as práticas que a portaria exige. Ex.: Passo Fundo, AD4, Grupo II: com NM1, risco de 20 % de 10-01 a 12-10; com NM4, de 10-01 a 01-31.
- **Z6 Risco**: calcular sobre o conjunto de decêndios 1-36, não sobre datas; linha com início > fim dá a volta no ano; "até 20 %" = linhas de 20; "até 30 %" = união de 20 e 30; 40 % = "risco alto"; o 29/02 entra no decêndio 6.
- **Z7 Ausência**, três mensagens diferentes: (a) cultura sem `nome_zarc`: "o ZARC não cobre esta cultura" (aveia, crotalária, nabo, guandu, pastagem); (b) UF fora do recorte: "sem dado do ZARC para o seu estado neste protótipo"; (c) UF no recorte e cultura com ZARC, mas sem linha: "o ZARC não indica o plantio no seu município, solo e ciclo". UFs do recorte: GO, RS, BA.
- **Z8**: o motor traduz e calcula; a IA só cita o resultado e a fonte.

## Limitações

- Recorte só de GO, RS e BA. Outras UFs: rodar o script.
- Safra mista por município (ver a lista acima). A 2026/2027 ainda não tem trigo em GO e na BA.
- Na demo de Irecê (BA, 2914604, rotação milho + feijão) não há linha de sequeiro de milho 1ª, feijão nem feijão-caupi em nenhuma das duas safras; só sorgo granífero (1ª e 2ª), sorgo forrageiro, amendoim e mamona. Pela regra Z7(c), a demo dirá "o ZARC não indica".
- Mandioca, milheto e o arroz irrigado tropical vêm de portarias de 2020 (sem safra); "Mandioca (aipim, macaxeira)" é o único ZARC de mandioca.
- O ZARC é de sequeiro (salvo o arroz irrigado), municipal e simulado.

---

Volta para o [`data/README.md`](../../README.md).
