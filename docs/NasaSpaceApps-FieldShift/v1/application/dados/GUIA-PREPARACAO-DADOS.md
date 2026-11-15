# Guia de preparação de dados

> 14/11/2026. O que cada pessoa do time precisa baixar, montar ou escrever **antes** de o app funcionar, e em que formato. Baseado na lista final de ferramentas (`tools/comparative/COMPARATIVO_FINAL.md`).
>
> Os arquivos ficam na pasta **`data/`** na raiz do repositório, e **a divisão das tarefas entre 3 pessoas está em `data/README.md`**. Cada arquivo corresponde a uma tabela do banco. O script que carrega os arquivos no banco é escrito **depois** que o backend for validado; até lá, o trabalho é preparar os arquivos no formato certo.

## Resumo: quem faz o quê

| # | Tarefa | Tipo de trabalho | Quem | Esforço | Bloqueia |
|---|---|---|---|---|---|
| 1 | **Parâmetros das culturas** (`data/catalogo/culturas.csv`) | Pesquisa agronômica | Alguém de agronomia | **Alto** | Motor inteiro, ZARC, PAM |
| 2 | Sinônimos das culturas (campo `nomes` do `agroia/base/culturas.json`) | Revisão de lista | Qualquer pessoa | Baixo | Texto livre do onboarding |
| 3 | O que cada cultura exige de equipamento (`cultura_equipamentos.csv`) | Planilha | Qualquer pessoa | Baixo | Filtro da pergunta 26b |
| 4 | Pontos da demo (`pontos_demo.csv`) | Decisão do time + teste | Time | Baixo | AppEEARS, pré-cálculo |
| 5 | Pedido no AppEEARS (NDVI e SMAP dos pontos) | Download | Quem tiver conta Earthdata | Médio (espera) | Cartão "meses descobertos" |
| 6 | ZARC (tábua de risco) | Download | Qualquer pessoa | Médio | Janelas da base de culturas |
| 7 | Códigos da PAM de cada cultura | Consulta | Qualquer pessoa | Baixo | Critério de renda |
| 8 | Textos do RAG | Escrita | Quem escreve bem para o produtor | Médio | Agente |
| 10 | Fotos de solo (pergunta 19) | Busca de imagens | Qualquer pessoa | Baixo | Onboarding |

A antiga tarefa 9 (`perguntas.yaml`) saiu: o questionário já está implementado nas telas do app (`agroia/web/src/onboarding/`).

**Fonte única do catálogo:** ids, nomes, sinônimos, família, grupo e tipos das culturas ficam em `agroia/base/culturas.json`; as categorias de equipamento, em `agroia/base/equipamentos.json`. Os arquivos de `data/catalogo/` usam esses mesmos ids e só acrescentam o que falta (parâmetros agronômicos e exigência de equipamento).

**Ordem:** a tarefa 1 é o caminho crítico e começa já. As tarefas 4 e 5 também começam cedo, porque o AppEEARS demora para responder. O resto anda em paralelo.

A malha municipal do IBGE, a PAM em si e os dados do NASA POWER, SoilGrids e SRTM são baixados **por script**, não à mão.

---

## Regras que valem para todos os arquivos

| Regra | Por quê |
|---|---|
| **UTF-8**, sem BOM | Acentos ("feijão") chegam certos no banco |
| **Separador vírgula, decimal com ponto** (`4.5`, não `4,5`) | ⚠️ O Excel em português salva CSV com `;` e decimal com vírgula. **Edite no Google Sheets** e use Arquivo → Fazer download → CSV, que sai no formato certo |
| **Vazio = não sei.** Nunca preencher 0 para "não sei" | Zero é um valor real; vazio vira "sem dado" e aparece como lacuna |
| **Ids iguais aos do `agroia/base/culturas.json`** (`feijao_caupi`, `aveia`, `pastagem`) | São as chaves que o app usa; um id diferente quebra a ligação |
| **Sim/não como `true` / `false`** | Formato que o carregador entende sem conversão |
| **Listas dentro de uma célula separadas por `|`** (`FAO-56|Embrapa`) | A vírgula já é o separador do CSV |
| **Toda linha com fonte** | O app mostra de onde vem cada número; sem fonte, não entra |
| **Unidade no nome da coluna** (`ciclo_dias_min`, `agua_ciclo_mm_max`) | Ninguém precisa adivinhar se é mm ou cm |

**Onde guardar o que for baixado:** downloads grandes (como a tábua completa do ZARC) ficam em `data/brutos/`, que o Git ignora; para compartilhar, use a pasta compartilhada do time. No repositório entram só os arquivos preparados e pequenos, nas pastas de `data/` (ver `data/README.md`).

---

## 1. Parâmetros das culturas — `data/catalogo/culturas.csv` (caminho crítico)

**Para quê:** o motor filtra o que não cabe no clima do local e dá nota a cada estratégia comparando os dados da NASA com estes parâmetros. Sem eles, nada funciona.

O app já conhece 40 culturas (`agroia/base/culturas.json`, com família, grupo, perene, tipos e sinônimos). Este CSV acrescenta **só os parâmetros agronômicos**, e só para as culturas que o motor vai usar nas estratégias.

**Culturas do motor (16)**, com os ids do app. Cobrem as rotações atuais típicas e as alternativas que o motor sugere:

| Grupo | Culturas (id) |
|---|---|
| Comerciais atuais | `soja`, `milho`, `feijao`, `trigo`, `arroz`, `algodao`, `mandioca` |
| Tolerantes à seca | `sorgo`, `milheto`, `feijao_caupi`, `girassol` |
| Cobertura e adubo verde | `crotalaria`, `nabo_forrageiro`, `aveia` (parâmetros da aveia-preta), `guandu` |
| Forrageira | `pastagem` (parâmetros da braquiária) |

**Colunas** (o arquivo tem uma linha de exemplo do milho, **a conferir**):

| Coluna | O que é | Unidade / valores | Fonte sugerida |
|---|---|---|---|
| `id` | Id da cultura no `agroia/base/culturas.json` | já preenchido | — |
| `nome_cientifico` | Espécie usada como referência dos parâmetros | já preenchido | Embrapa |
| `ciclo_dias_min`, `ciclo_dias_max` | Duração do plantio à colheita | dias | Embrapa, FAO-56 |
| `temp_base_c` | Temperatura abaixo da qual não cresce (graus-dia) | °C | Literatura |
| `temp_otima_min_c`, `temp_otima_max_c` | Faixa ideal | °C | FAO ECOCROP |
| `tmax_critica_c` | Calor que prejudica a floração | °C | Literatura |
| `sensivel_geada` | Sofre com geada? | `true`/`false` | — |
| `agua_ciclo_mm_min`, `agua_ciclo_mm_max` | Água necessária no ciclo | mm | FAO-56, FAO ECOCROP |
| `kc_inicial`, `kc_medio`, `kc_final` | Coeficiente de cultura por fase | número (ex.: `1.2`) | **FAO-56, tabela 12** |
| `profundidade_raiz_m` | Profundidade efetiva das raízes | m | FAO-56 |
| `cobertura_solo` | Quanto cobre o solo | `baixa`/`media`/`alta` | Embrapa |
| `aporte_biomassa` | Palha deixada | `baixo`/`medio`/`alto` | Embrapa |
| `valor_forrageiro` | Serve de comida para animais? | `nenhum`/`baixo`/`medio`/`alto` | — |
| `codigo_pam` | Código da cultura na PAM (ver tarefa 7) | texto | API de agregados do IBGE |
| `fontes` | De onde vieram os números | texto, várias separadas por `|` | — |
| `confianca_parametros` | Quão seguro é o conjunto | `baixa`/`media`/`alta` | Julgamento de quem preencheu |

**Cuidados:**
- **Faixas, não um número só**, onde houver variação entre cultivares (ciclo, água).
- Se um parâmetro não foi achado, **deixe vazio** e baixe a `confianca_parametros`.
- O Kc do FAO-56 é para condições padrão; anote se usou outra fonte.

---

## 2. Sinônimos — campo `nomes` do `agroia/base/culturas.json`

**Para quê:** a IA e a lista reserva casam o que o produtor escreve ("macaxeira", "capim pras vacas") com a base. Quanto mais nomes populares, melhor.

O arquivo já tem nomes em PT, EN e ES para as 40 culturas. A tarefa é **revisar e acrescentar nomes regionais**, por PR:

```json
{"id": "mandioca", "nomes": {"pt": ["mandioca", "macaxeira", "aipim", "maniva"], "en": ["cassava"], "es": ["yuca"]}}
```

**Meta:** os nomes regionais conhecidos em português de cada cultura do motor, e pelo menos um nome em inglês e um em espanhol.

---

## 3. Exigência de equipamento — `data/catalogo/cultura_equipamentos.csv`

**Para quê:** o filtro da pergunta 26b ("que máquinas você tem?") elimina culturas que o produtor não consegue plantar ou colher.

- As categorias já existem em `agroia/base/equipamentos.json` (`trator`, `plantadeira_graos`, `colhedora`, `pulverizador`, `preparo_solo`, `rocadeira`, `ensiladeira`, `irrigacao`, `tracao_animal`, `manual`). Só acrescente uma categoria nova lá, por PR, se faltar.
- No CSV, para cada cultura do motor, o que ela **exige** em cada etapa (`plantio` ou `colheita`). Se dá para fazer à mão, use `manual`.

---

## 4. Pontos da demo — `pontos_demo.csv`

**Para quê:** os casos concretos da apresentação (Q-01 a Q-03 do `DECISOES.md`). Todos os dados lentos são pré-calculados para eles.

| Coluna | O que é |
|---|---|
| `id` | `cerrado_1`, `semiarido_1`… |
| `regiao` | Cerrado, Semiárido, Sul… |
| `municipio`, `uf` | Para conferir com a PAM e o ZARC |
| `latitude`, `longitude` | Decimal, com ponto (sul e oeste negativos): `-18.95`, `-47.12` |
| `rotacao_atual` | Ex.: `soja (out–fev) | milho safrinha (fev–jun) | pousio (jul–set)` |
| `historia` | O "seu Antônio" desse ponto, em 2 ou 3 frases |
| `soilgrids_ok` | `true` depois de testar (ver abaixo) |

**Cuidados:**
- **O ponto precisa estar em área agrícola, não em cidade.** O SoilGrids devolve vazio em área urbana. Conferir no Google Maps (modo satélite) se é lavoura.
- **Testar no SoilGrids** colando no navegador (trocar lat/lon):
  `https://rest.isric.org/soilgrids/v2.0/properties/query?lon=-47.12&lat=-18.95&property=clay&depth=0-5cm&value=mean`
  Se o valor `mean` vier preenchido, marcar `soilgrids_ok = true`.
- Escolher regiões **contrastantes** (ex.: Cerrado, Semiárido e Sul), para mostrar que a recomendação muda com o lugar.

---

## 5. AppEEARS: NDVI e SMAP dos pontos da demo

**Para quê:** o cartão "meses descobertos" (NDVI) e "quantos dias o solo aguenta" (SMAP).

**Passo a passo (pelo site, sem código):**
1. Criar a conta em `urs.earthdata.nasa.gov` e entrar em `appeears.earthdatacloud.nasa.gov`.
2. **Extract → Point Sample.** Enviar os pontos de `pontos_demo.csv` (o site aceita CSV com `ID`, `Category`, `Latitude`, `Longitude`).
3. Período: **2001-01-01 até hoje**.
4. Produtos e camadas:
   - `MOD13Q1.061` → camadas de NDVI e de qualidade (250 m, histórico)
   - `VNP13A1.002` → camadas de NDVI e de qualidade (500 m, continuidade do MODIS)
   - `SPL4SMGP` (versão mais recente) → umidade da zona das raízes, se o SMAP entrar
5. Enviar e anotar o **id da tarefa**. Quando ficar pronta (pode levar de minutos a horas), baixar os CSVs.
6. Guardar os CSVs, sem editar, em `data/demo/appeears/<id_da_tarefa>/` e anotar no `data/FONTES.md` o id, a data e os produtos.

---

## 6. ZARC: tábua de risco

**Para quê:** a janela de plantio oficial de cada cultura por município entra na base de culturas.

1. No portal de dados abertos do MAPA (`dados.agricultura.gov.br`), procurar **"Tábua de risco ZARC"**.
2. Baixar a safra vigente **só das culturas da base** (tarefa 1).
3. Baixar também o **dicionário de dados**: ele diz o nome de cada coluna e o que são os tipos de solo e grupos de cultivar.
4. Guardar o arquivo completo em `data/brutos/zarc/` (fica fora do Git).
5. Preencher `data/brasil/zarc/mapa_culturas_zarc.csv` com o nome exato que o ZARC usa para cada `cultura_id` (a coluna `nome_zarc` de `culturas.csv` é preenchida a partir daqui na carga).
6. Salvar em `data/brasil/zarc/` um recorte com **só as 16 culturas** (pequeno o bastante para o Git).
7. Anotar no `data/FONTES.md` a URL, a safra e a data do download.

Converter decêndios em datas e cruzar com os municípios fica para o script de carga.

---

## 7. Códigos da PAM

**Para quê:** ligar cada cultura da base aos dados de produção por município (critério de renda).

1. Abrir no navegador: `https://servicodados.ibge.gov.br/api/v3/agregados/5457/metadados`
2. Procurar a classificação **782** (produto das lavouras) e anotar o código de cada cultura da base.
3. Preencher a coluna `codigo_pam` em `culturas.csv`.
4. Culturas de cobertura (crotalária, nabo, braquiária) **provavelmente não existem** na PAM: deixar vazio.

O download dos valores por município é feito por script.

---

## 8. Textos do RAG (conhecimento do agente)

**Para quê:** o agente busca nestes textos para explicar as coisas ao produtor. A qualidade da resposta depende diretamente da qualidade destes textos.

**Documentos a escrever** (em `data/rag/`):

| Documento | Conteúdo | Base existente |
|---|---|---|
| `metodologia-indicadores.md` | Como cada indicador é calculado e o que ele significa (geada, déficit hídrico, meses descobertos, erosão…) | `architecture/MOTOR-DE-ANALISE.md` |
| `o-que-mede-cada-satelite.md` | NASA POWER, SoilGrids, SRTM, MODIS/VIIRS, SMAP, IMERG: o que cada um vê, em linguagem simples, e o limite de escala | Notas de `tools/` (só a parte "o que é" e "limitações") |
| `fichas-culturas.md` | Uma seção por cultura: para que serve, vantagens para o solo, cuidados | Base de culturas |
| Revisão do glossário | Trocar linguagem técnica por linguagem de produtor | `.md/glossario-cientifico-ampliado-field-shift-brasil.md` |

**Regras de escrita (fazem a busca funcionar):**

| Regra | Por quê |
|---|---|
| **Um assunto por seção** (`##` ou `###`) | Cada seção vira um trecho da busca |
| **Seções de 100 a 400 palavras** | Menor que isso falta contexto; maior, a busca perde precisão |
| **Cada seção se explica sozinha**: repetir o nome do assunto, nunca "como vimos acima" | O agente recebe a seção solta, sem o resto do documento |
| **Uma linha "Como o produtor costuma dizer:"** com os jeitos populares de falar do assunto | Aproxima a busca do vocabulário informal ("terra pelada", "veranico") |
| **Fonte no fim de cada seção** | O agente cita de onde veio |
| **Nada de URL de API, parâmetro ou código** | Isso é documentação de desenvolvedor e confunde o agente |

**Exemplo de seção bem escrita:**

```markdown
## Solo descoberto

Solo descoberto é quando a terra do campo fica sem nenhuma planta por cima, geralmente
depois da colheita. Sem cobertura, a chuva forte bate direto no chão, arranca a camada
de cima (a mais rica) e leva embora. O sol também esquenta e resseca a terra, e a
matéria orgânica se perde mais rápido. Quanto mais inclinado o terreno e mais forte a
chuva, maior o estrago.

Como o produtor costuma dizer: terra pelada, chão limpo, campo parado, terra sem nada.

Fonte: Embrapa, guia de plantas de cobertura.
```

---

## 9. ~~`perguntas.yaml`~~ (saiu)

O questionário já está implementado nas telas do app (`agroia/web/src/onboarding/`), e o formato das respostas está em `agroia/api/app/schemas/onboarding.py`. Não é mais preciso converter as perguntas para um arquivo.

---

## 10. Fotos de solo (pergunta 19)

- **12 fotos reais**: 6 de cor (escura, marrom, vermelha, amarela, cinza, clara) e 6 de aspecto na mão (solta, fofa, gruda, torrões, racha, pedras).
- De preferência **solos de lugares diferentes do Brasil**.
- **Só imagens com licença que permita uso** (domínio público, Creative Commons, fotos próprias).
- Nome do arquivo igual ao valor que o app usa: `cor_amarela.jpg`, `jeito_torroes.jpg`… (lista completa no `CREDITOS.md`)
- Salvar em `data/onboarding/fotos-solo/` e, para cada foto, preencher uma linha no `CREDITOS.md` da mesma pasta: arquivo, autor, link e licença.

---

## `FONTES.md`: registro de tudo que foi baixado

Toda tarefa de download acrescenta uma linha em `data/FONTES.md`:

| Arquivo | Fonte | URL | Data do download | Versão / safra | Licença | Quem baixou |
|---|---|---|---|---|---|---|

Isso alimenta a seção "dados usados" da submissão do Space Apps e a coluna "de onde vem?" do app.

---

## Checklist final antes da carga

- [ ] `culturas.csv` com as 16 culturas do motor, sem `0` no lugar de "não sei", cada linha com `fontes`
- [ ] Sinônimos regionais revisados no `agroia/base/culturas.json`
- [ ] `cultura_equipamentos.csv` cobrindo plantio e colheita de todas as culturas do motor, com ids do `equipamentos.json`
- [ ] `pontos_demo.csv` com todos os pontos marcados `soilgrids_ok = true`
- [ ] Tarefa do AppEEARS concluída e CSVs guardados
- [ ] `mapa_culturas_zarc.csv` e `codigo_pam` preenchidos onde existirem
- [ ] Textos do RAG revisados com as regras de escrita
- [ ] 12 fotos de solo com créditos, com os nomes do `CREDITOS.md`
- [ ] `FONTES.md` atualizado
