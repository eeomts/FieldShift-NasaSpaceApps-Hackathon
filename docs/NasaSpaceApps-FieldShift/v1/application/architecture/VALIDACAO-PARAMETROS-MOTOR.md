# Validação dos parâmetros do motor

Conferência, em 15/11/2026, dos números marcados "proposta, validar com o Yury" em `agroai/api/app/services/motor/parametros.py`. Para cada um: a conta que o motor faz, o que dizem as fontes e o veredito.

- **ok**: o número tem fonte, ou é coerente com uma fonte (dito quando a fonte só confirma a ordem de grandeza).
- **troca para X**: uma fonte indica outro valor ou outra forma.
- **sem fonte**: é escolha de produto. Precisa aparecer como escolha na tela ou no documento.

Todas as fontes foram abertas nesta conferência. As URLs e os trechos estão em cada seção e na lista do fim. Nenhum código, catálogo ou outro documento foi alterado.

> **Atualização de 15/11/2026 (mesmo dia, depois da conferência).** A regra 17 (frio por cultura; seção 2.2 e item 5 da seção 3) foi **implementada** no motor, e o texto da nota de renda passou a dizer que é contagem (item 8 da seção 3, só a parte da renda). O restante do documento é o histórico da conferência e não foi reescrito: onde o texto diz "não está pronto" ou "hoje", leia as marcas "implementado" abaixo.

---

## 1. Resumo

| # | Constante | Valor atual | Veredito | Valor proposto | Fonte principal |
|---|---|---|---|---|---|
| 1 | `AGUA_ALERTA_ABAIXO` | 0,80 | **ok** (ordem de grandeza) | manter 0,80 e explicar o aviso pelo Ky | FAO-56 eq. 90 e Tab. 24 (Ky do FAO-33); ZARC soja (ISNA ≥ 0,55) |
| 2 | `GEADA_FASE_SENSIVEL = "terco_medio"` | terço do meio do ciclo | **ok como reserva**; a regra 17 (implementada em 15/11/2026) substitui quando houver `tmin_critica_c` | manter só para cultura sem `tmin_critica_c` | FAO Frost protection, Tab. 4.5; FAO-56 cap. 6 e Tab. 11 |
| 3 | `TERRA_PESO_COBERTURA / BIOMASSA / FIXADORA` | 0,4 / 0,3 / 0,3 | **sem fonte** (pesos); estrutura coerente com a FAO | manter e mostrar como escolha da equipe | FAO, Agricultura de Conservação (3 princípios); NRCS SCI só como analogia |
| 4a | `CLASSE_BIOMASSA` | 0,33 / 0,66 / 1,0 | **ok** | manter (a curva dá ≈ 0,3 / 0,7 / 0,9) | Lopes, Cogo & Levien 1987 (RBCS 11:71-75); Alvarenga et al. 2001 (régua do README) |
| 4b | `CLASSE_FORRAGEIRO` | 0 / 0,3 / 0,6 / 1,0 | **sem fonte** | 0 / 0,33 / 0,67 / 1,0 (degraus iguais) ou declarar o atual | régua do README (classe ordinal) |
| 5 | `FATOR_DECLIVE` | 0,25 / 0,5 / 0,75 / 1,0 / 1,0 | **troca** (a forma está achatada) | fator = mín(1; LS da RUSLE). Com rampa de 46 m: **0,22 / 0,84 / 1 / 1 / 1**. Com o SRTM, usar a declividade medida | USDA AH 537 (definição do LS); tabelas de LS da RUSLE (NRCS); classes da Embrapa |
| 6a | `K_LIMITE_BAIXA / MEDIA` | 0,020 / 0,035 | **troca** | **0,015 / 0,030** | Mannigel et al. 2002 (classes de K para solos brasileiros) |
| 6b | `FATOR_K` | 0,75 / 1,0 / 1,25 | **troca** | proporcional ao K: **K ÷ 0,0225** (ou, por classe, 0,44 / 1 / 1,67) | USLE, A = R·K·LS·C·P (AH 537); centro da classe "médio" de Mannigel et al. 2002 |
| 7 | `PRAGAS_DESCONTO_MESMA_FAMILIA` | 0,2 por par | **troca** (forma); o 0,2 não tem fonte | tirar o desconto; nota = 1 − pares seguidos da mesma família ÷ pares | Embrapa Soja (alternar espécies); a conta atual pune quem acrescenta cultura |
| 8 | `RENDA_POR_COMERCIAIS` | 0 / 0,5 / 0,8 / 1,0 | **sem fonte** | manter e explicar na tela que é contagem, não lucro (texto feito em 15/11/2026: "Contamos as culturas de venda; preço e produção da sua região ainda não entram nesta nota.") | calibrar depois com o valor da produção do IBGE PAM (D-009) |
| 9 | `MAX_CANDIDATAS` | 30 | **sem fonte** (engenharia) | aplicar o corte **depois** do filtro, ou tirar o corte | contagem feita com o catálogo atual (seção 2.9) |

Notas de 0 a 1 citadas abaixo foram calculadas com o código atual do motor (`criterios.py`), rodado localmente.

---

## 2. Item por item

### 2.1 Aviso de água em 80 % (`AGUA_ALERTA_ABAIXO = 0,80`)

**A conta do motor** (`filtro.py`, `_agua`). Para cada cultura nova: razão = chuva média do período (1991–2020) ÷ ETc do período, com ETc = Kc × ET0 do NASA POWER, Kc por terços do ciclo. Abaixo de 0,80 sai o aviso "água no limite" com o déficit em mm. Abaixo de 0,50, com irrigação em parte da área, o texto diz que "só fecha na parte irrigada". A água nunca elimina (regra 1). O aviso só pesa na ordem das estratégias como desempate (`pontuacao._chave` conta os alertas por último).

**Fontes**
- FAO-56, cap. 8, eq. 90 (https://www.fao.org/4/x0490e/x0490e0e.htm): a função do FAO-33 é (1 − Ya/Ym) = Ky (1 − ETc adj/ETc). Trecho: *"Ky is a factor that describes the reduction in relative yield according to the reduction in ETc caused by soil water shortage."* A Tabela 24 traz o Ky da estação inteira: *"Maize 1.25 … Soybean 0.85 … Beans 1.15 … Sorghum 0.9 … Sunflower 0.95 … Cotton 0.85 … Spring Wheat 1.15 … Winter wheat 1.05 … Groundnet 0.70 … Alfalfa 1.1"*.
- ZARC da soja, SP, Portaria SPA/MAPA nº 381/2025 (https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-risco-climatico/portarias/safra-vigente/sao-paulo/PORTN381SOJASP.ret2.pdf): *"Foi considerado um ISNA ≥ 0,50 na Fase I - Estabelecimento e ISNA ≥ 0,55 na Fase III - Floração e enchimento de grãos."* O ISNA é ETr/ETm num balanço hídrico com a água guardada no solo.
- FAO, Irrigation Water Management, Training Manual 3, cap. 3 (https://www.fao.org/4/s2022e/s2022e08.htm): nem toda a chuva fica para a planta. *"the effective rainfall (8) is the total rainfall (1) minus runoff (4) minus evaporation (5) and minus deep percolation (7)"*, com *"Pe = 0.8 P − 25 if P > 75 mm/month"*.

**Veredito: ok, pela ordem de grandeza.** Se a planta só tivesse a chuva do período, ETa/ETc = 0,8 daria, pela eq. 90, uma perda esperada de Ky × 20 %: cerca de 25 % no milho, 17 % na soja e no algodão, 18 % no sorgo, 19 % no girassol, 23 % no feijão e 14 % no amendoim. É um bom ponto para dizer "atenção". Não é um valor publicado como limiar: nenhuma fonte usa "chuva ÷ ETc = 0,8".

Duas forças contrárias que o texto da tela precisa admitir:
- A chuva bruta conta água que escorre ou passa da raiz. Pela fórmula da FAO, um mês com 150 mm aproveita cerca de 95 mm.
- A conta ignora a água guardada no solo na semeadura. O ZARC conta essa água e aceita ISNA de 0,55 na floração.

Uma coisa compensa a outra em parte. Por isso **não** proponho trocar para a chuva efetiva sem testar: na soja de sequeiro do Cerrado, ela daria aviso em quase todo lugar, contra a regra 1.

**O que fazer**
- Manter 0,80. No comentário do código, trocar "proposta" por "coerente com a eq. 90 do FAO-56 (Ky do FAO-33): 80 % da água ≈ 15–25 % de perda nos grãos; não é limiar publicado".
- Opcional: no aviso, citar o Ky da cultura ("com só a chuva do período, a perda pode chegar a cerca de X %"). O Ky não está no catálogo; seria coluna nova, com fonte na Tabela 24.
- O `AGUA_MUITO_ABAIXO = 0,50` não foi pedido. Pela mesma conta, ele equivale a cerca de 35–60 % de perda e é coerente com o limiar de risco severo do ZARC (ISNA 0,50 a 0,55), também só pela ordem de grandeza.

### 2.2 Geada no terço do meio do ciclo (`GEADA_FASE_SENSIVEL = "terco_medio"`)

**A conta do motor** (`filtro._geada`, `calendario.meses_do_terco_medio`). Só para culturas com `sensivel_geada`. O ciclo, em meses inteiros, é cortado em três partes iguais. Entram os meses que **tocam** o terço do meio: num ciclo de 4 meses, os meses 2 e 3 (de 25 % a 75 % do ciclo); num de 3 meses, só o do meio; num de 5 meses, do 2º ao 4º. Perene: o ano todo. Um ano conta quando algum desses meses teve 1 dia ou mais com mínima abaixo de 2 °C (`clima/limiares.py`). A cultura sai se isso aconteceu em mais de 30 % dos anos.

**A regra 17 substitui o terço do meio (implementada em 15/11/2026).** Com `tmin_critica_c` preenchida (catálogos preenchidos em 15/11; ver o README de evidências, "Dano por frio"), o teste usa o limiar da cultura só nos **dias** da fase sensível: da semeadura + `fase_frio_inicio_frac` × ciclo médio até a semeadura + `fase_frio_fim_frac` × ciclo médio (`ciclo_todo` = o ciclo inteiro). Um ano conta com `tmin_dias_seguidos` dias seguidos abaixo do limiar (vazio = 1). Com `tmin_efeito` = `aviso` (esterilidade do arroz), a cultura não sai: recebe um aviso, como o calor. O terço do meio com 2 °C fica só como **reserva** para cultura sem limiar com fonte (README das evidências, regra 17).

**Estado em 15/11/2026: implementado** (`filtro.py`: `janela_do_frio`, `fracao_de_anos_com_frio`, `_frio`; reserva em `_geada`). A semeadura é o dia 15 do mês de início (`SEMEADURA_DIA_DO_MES`, proposta, validar com o Yury; alternativa: dias 1, 11 e 21, como os decêndios do ZARC), os anos de semeadura são 1991-2020 e só entram os anos com todos os dias da janela. Sem a mínima diária do local, a cultura com `tmin_critica_c` recebe uma lacuna e não é eliminada. O texto diz "geada" quando o limiar é de até 0 °C e "frio" acima disso, com a fase em linguagem simples (florada, enchimento dos grãos, todo o ciclo). A conferência de Passo Fundo, Ness County, Santa Maria e outros locais na tela continua pendente.

**Fontes para a reserva**
- FAO, *Frost protection: fundamentals, practice and economics*, vol. 1, Tabela 4.5 (https://www.fao.org/4/y7223e/y7223e0a.htm), temperaturas críticas de dano em germinação / floração / frutificação (°C): *"Spring wheat -9, -10 -1, -2 -2, -4"*; *"Soybeans -3, -4 -2, -3 -2, -3"*; *"Corn [maize] -2, -3 -1, -2 -2, -3"*; *"Sunflower -5, -6 -2, -3 -2, -3"*; *"Beans -5, -6 -2, -3 -3, -4"*. Em todas as culturas da tabela, a floração é a fase mais sensível ou empata com a mais sensível. A mesma obra (https://www.fao.org/4/y7223e/y7223e07.htm) diz que esses limites valem para o ar no abrigo: *"correlated with air temperatures called 'critical temperatures' measured in standard instrument shelters"*.
- FAO-56, cap. 6 (https://www.fao.org/4/x0490e/x0490e0a.htm): *"Effective full cover for many crops occurs at the initiation of flowering."* e *"The mid-season stage runs from effective full cover to the start of maturity."* Ou seja, a floração começa no início da fase média.
- FAO-56, Tabela 11 (https://www.fao.org/4/x0490e/x0490e0b.htm), duração das fases (inicial, desenvolvimento, média, final). Onde começa a fase média, em fração do ciclo: milho (grão) *"30 40 50 30 150"* → 0,47; *"20 35 40 30 125"* → 0,44. Soja *"20 30/35 60 25 140"* (Central USA) → 0,36–0,39; *"15 15 40 15 85"* (trópicos) → 0,35. Trigo *"15 25 50 30 120"* → 0,33. Feijão seco *"20 30 40 20 110"* → 0,45.

**Veredito: ok como reserva.** A floração cai entre 30 % e 47 % do ciclo nesses exemplos, dentro ou na borda do terço do meio (33 % a 67 %). A regra "mês que toca" ainda alarga a janela. A floração é a fase mais sensível ao frio na tabela da FAO. A soja do Japão (fase média começando em 0,30) fica um pouco antes do terço: é a margem de erro da reserva.

Duas observações para a tela e para o código:
- Os 2 °C no abrigo ficam 3 a 5 °C acima do dano na floração da FAO (−1 a −3 °C). A reserva é conservadora e elimina mais do que a tabela pediria. O ZARC da soja usa *"temperaturas mínimas menores ou iguais a 3°C no abrigo meteorológico"* (portaria citada em 2.1), também conservador. Não é preciso trocar, mas o texto deve dizer "risco de geada", não "dano certo".
- O texto do alerta dizia sempre "fase de floração". Com a regra 17, a fase pode ser `enchimento_grao`, `ciclo_todo` etc.; o texto usa `fase_sensivel_frio` (**implementado em 15/11/2026**, em `filtro._frio` e `parametros.FASES_FRIO_TEXTO`). A reserva `_geada` mantém "fase de floração".

**O que a regra 17 exigia no código** (**implementado em 15/11/2026**; a lista abaixo é o histórico do que foi pedido):
1. (Feito: `catalogo.py` lê os seis campos como número ou texto.) `catalogo.py` não conhecia `tmin_critica_c`, `fase_sensivel_frio`, `fase_frio_inicio_frac`, `fase_frio_fim_frac`, `tmin_dias_seguidos` e `tmin_efeito`: hoje elas caem em `extras`, como texto. Precisam entrar em `CAMPOS_NUMERICOS` (ou `CAMPOS_TEXTO`) e no `CulturaMotor`.
2. (Feito: a Tmin diária fica em `clima_mensal.tmin_diaria`, lista JSONB de 28 a 31 valores por mês, migration 0008; `agregacao.py` preenche; `ClimaDoLocal.tmin_por_dia`. Célula sem a coluna é baixada de novo no primeiro uso. A migration ainda precisa rodar na VPS, só com confirmação do usuário.) **O dado de clima de então não bastava.** `clima_mensal` guarda só os dias abaixo de 2 °C por mês (`TMIN_GEADA_C`), e os dados diários não ficam no banco. A regra 17 precisa, para cada limiar do catálogo (hoje de −3,3 a 15 °C, inclusive 10 e 15 °C do arroz), contar os dias **dentro da janela da fase** e a **maior sequência de dias seguidos** abaixo do limiar. Opções: guardar a série diária de `T2M_MIN` por célula (ou por decêndio, como o ZARC) e contar na hora; ou um JSONB por ano com, para cada limiar do catálogo, as datas ou sequências abaixo dele. Contar só "dias abaixo de cada grau inteiro por mês" não serve: não cobre 10 e 15 °C, não conta dias seguidos e não recorta a janela. Isso pede migration e reagregação do clima nas células (na VPS, só com confirmação do usuário), quando o motor implementar a regra.
3. (Feito.) A janela da fase vai em **dias** (decisão de 15/11), não em meses inteiros: contar por mês elimina o arroz irrigado em Santa Maria em até 18 de 19 anos e o feijão em 11 de 19; pela janela, 4 a 9 e 1 de 19 (simulação com NASA POWER diário 2001-2019, `reviews/`, revisão de 15/11).

### 2.3 Fórmula da nota Terra (pesos 0,4 / 0,3 / 0,3)

**A conta do motor** (`criterios.nota_terra`): nota = 0,4 × (meses com planta ÷ 12) + 0,3 × (classe de palha da cultura com **mais** palha) + 0,3 × (1 se alguma cultura fixa nitrogênio). Exemplos com o código atual: milho só, nov–mar → 0,47. Soja + milho safrinha (9 meses) → 0,90. A mesma rotação com cobertura em jul–set → 1,0.

**Fontes**
- FAO, Agricultura de Conservação (https://www.fao.org/conservation-agriculture/en/), três princípios: *"Minimum mechanical soil disturbance"*, *"Permanent soil organic cover (at least 30 percent) with crop residues and/or cover crops"* e *"Species diversification through varied crop sequences and associations involving at least three different crops."* Os três termos do motor correspondem a cobertura permanente (meses e palha) e diversificação (leguminosa).
- Índice de Condicionamento do Solo (SCI) do NRCS, que mede se a matéria orgânica sobe ou desce, como analogia de pesos. Extensão da UGA, C962 (https://openscholar.uga.edu/record/26479/files/C962.pdf): *"the organic matter (OM) and field operation (FO) factors account for 80% (40% each) of the SCI value. The remaining 20% is accounted for by the erosion (ER) fraction"*. Só confirma que índices oficiais de solo também usam pesos redondos escolhidos por especialistas. Não mede a mesma coisa e não dá os pesos do motor.

**Veredito: sem fonte para os pesos.** A estrutura segue os princípios da FAO, mas 0,4 / 0,3 / 0,3 é escolha da equipe.

**Como deixar explícito**
- Na tela, no detalhe da nota: "A nota Terra soma três coisas, com pesos escolhidos pela equipe: meses com planta (40 %), palha que fica no campo (30 %) e planta que fixa nitrogênio (30 %)."
- No documento do motor: registrar como decisão, com a referência aos três princípios da FAO.

**Forma com fonte de calibrar (para depois):** rodar o motor nos pontos da demo com os pesos de 0,2 a 0,6 e ver se a ordem das estratégias muda (o teste de sensibilidade da regra 7). Se não mudar, dizer "a ordem não depende dos pesos".

**Duas observações (não pedidas):**
- A palha usa a **maior** classe da rotação, não a soma. Duas culturas de palha alta valem o mesmo que uma.
- A coluna `cobertura_solo` do catálogo (palha que sobra 60 dias depois) não é usada. Ela permitiria contar como "cobertos" os meses logo após a colheita de quem deixa muita palha. Hoje esses meses contam como vazios, na nota Terra e na de erosão.

### 2.4 Conversão das classes de palhada e de forragem

#### a) Palhada (`CLASSE_BIOMASSA`: baixo 0,33, médio 0,66, alto 1,0)

**Fontes.** A régua do README das evidências define as classes por matéria seca (MS) que fica no campo: baixo < 2,3 t/ha, médio de 2,3 a < 6, alto ≥ 6 t/ha.
- O limite de 6 t/ha vem de Alvarenga et al. 2001: *"Pode-se considerar que 6 t ha-1 de resíduos sobre a superfície seja uma quantidade adequada ao SPD"* (trecho citado no README).
- A curva que liga massa à cobertura do solo vem de Lopes, Cogo & Levien (1987), RBCS 11:71-75 (https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/132491/1/Revistabrasileiradecienciadosolov.11p.7175.pdf). Curvas por resíduo: *"MILHO CS = 100(1−e^−0,000313 MR)"*, trigo 0,000326, soja 0,000252; a curva média de 0,000297 é a do README. Trecho: *"dosagens próximas a 2.000 kg/ha foram suficientes para cobrir ao redor de 40% a superfície do solo"*.

**A conta.** Com a curva média, a cobertura típica de cada classe, usando a mediana da palha típica (`regua.ms_palhada_t_ha.tipico`) dos dois catálogos e tirando as exceções de algodão e mandioca:

| Classe | Palha típica (mediana) | Cobertura pela curva | Valor no motor |
|---|---|---|---|
| baixo | 0,9–1,3 t/ha (caupi, centeio, ervilhaca) | 0,23–0,32 | 0,33 |
| médio | 4,0–4,3 t/ha | 0,70–0,72 | 0,66 |
| alto | 7–11 t/ha | 0,87–0,96 | 1,0 |

**Veredito: ok.** Os três valores ficam a cerca de 0,1 ou menos da fração de solo coberta medida no Brasil, e "alto = 1" coincide com a quantidade "adequada ao SPD". Trocar o comentário "proposta" por: "≈ cobertura do solo pela curva de Lopes, Cogo & Levien (1987) na palha típica da classe; alto = 6 t/ha ou mais (Alvarenga et al. 2001)".

#### b) Forragem (`CLASSE_FORRAGEIRO`: nenhum 0, baixo 0,3, médio 0,6, alto 1,0)

**Fonte.** A régua do README define a classe pelo uso recomendado (`nao_serve` → nenhum, `residual` → baixo, `com_restricao` → médio, `principal` → alto), com rebaixamento por digestibilidade abaixo de 60 %. É uma escala de **ordem**, sem medida por trás dos números.

**Veredito: sem fonte.** Os degraus nem são iguais: de baixo para médio sobe 0,3, de médio para alto sobe 0,4.

**Proposta:** degraus iguais, 0 / 0,33 / 0,67 / 1,0, iguais aos da palha, ou manter o atual e escrever o motivo. Na tela: "nota pela classe de uso como comida para o gado (não é medida de produção de forragem)".

**Calibração possível:** a régua já guarda a digestibilidade (`regua.digestibilidade_pct`) em várias culturas. Uma nota contínua pela digestibilidade teria fonte, mas mistura a palhada (grão) com a forragem (cobertura). Fica para a v2.

### 2.5 Fatores de declividade (`FATOR_DECLIVE`)

**A conta do motor** (`criterios.nota_erosao`): nota de erosão = 1 − (1 − parcela coberta) × fator de declive × fator K, limitada a 0–1. A "parcela coberta" é a fração dos dias de chuva forte que caem em meses com planta. O fator de declive multiplica a parte **descoberta**. Hoje: plano 0,25, suave ondulado 0,5, ondulado 0,75, forte ondulado 1,0, montanhoso 1,0; sem dado 0,5. A classe vem do SRTM (com a declividade em %) ou da pergunta 7.

Lida assim, a fórmula é uma USLE relativa: 1 − (perda do campo ÷ perda de um campo de referência), com o fator C aproximado por "descoberto = 1, coberto = 0" e o R aproximado pela parcela de chuva forte. Para isso, o fator de declive deveria ser o **LS** da USLE/RUSLE dividido pelo LS de referência.

**Fontes**
- Classes de relevo da Embrapa, Boletim de P&D 213, Tabela 1 (https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/950793/1/BPD213RelevoZonaMata.pdf): *"Plano 0–3; Suave Ondulado 3–8; Ondulado 8 – 20; Forte Ondulado 20 – 45; Montanhoso 45 – 75; Escarpado > 75"*, com *"Fonte: Santos et al., 2005"*. São as mesmas de `srtm.py`.
- USDA Agriculture Handbook 537 (Wischmeier & Smith 1978) (https://www.ars.usda.gov/ARSUserFiles/60600505/RUSLE/AH_537%20Predicting%20Rainfall%20Soil%20Losses.pdf): *"A=RKLSCP"* e *"LS is the expected ratio of soil loss per unit area from a field slope to that from a 72.6-ft length of uniform 9-percent slope under otherwise identical conditions."* O LS é o próprio fator relativo, com referência publicada: a parcela-padrão de 22,1 m e 9 %, onde LS = 1.
- Tabelas de LS da RUSLE (AH 703) publicadas pelo NRCS no guia técnico de Oklahoma (https://efotg.sc.egov.usda.gov/references/Agency/OK/RUSLE_Chap3_LS_Factors.pdf). Usei a tabela de razão moderada entre sulco e entressulco, que o documento manda usar em lavoura: *"Table 2-2 should be used when predicting erosion on cropland"*, com a nota *"Such as for row-cropped agricultural and other moderately consolidated soil conditions with little-to-moderate cover"*. O mesmo texto diz: *"Soil loss increases more rapidly with slope steepness than it does with slope length."* O PDF original do AH 703 no site do ARS não abriu (o link devolveu uma página HTML). Por isso a tabela vem da reprodução do NRCS.

**A conta: LS da RUSLE no meio de cada classe**, tabela de razão moderada, interpolada. Rampa típica declarada: **46 m (150 pés)**. Mostro também 23 m (a parcela-padrão) e 91 m. O guia do NRCS diz que a enxurrada *"will usually concentrate in less than 400 ft"* (122 m).

| Classe (meio) | LS, rampa 23 m | LS, rampa 46 m | LS, rampa 91 m | LS ÷ LS do forte ondulado (46 m) | Fator atual |
|---|---|---|---|---|---|
| plano (1,5 %) | 0,20 | 0,22 | 0,26 | 0,03 | 0,25 |
| suave ondulado (5,5 %) | 0,64 | 0,84 | 1,13 | 0,11 | 0,50 |
| ondulado (14 %) | 1,86 | 2,76 | 4,09 | 0,36 | 0,75 |
| forte ondulado (32,5 %) | 4,78 | 7,59 | 12,04 | 1,00 | 1,00 |
| montanhoso (60 %) | 8,33 | 13,65 | 22,36 | 1,80 | 1,00 |

Na RUSLE, o LS sobe de 30 a 60 vezes do plano ao forte ondulado. No motor, sobe 4 vezes. **A forma atual está achatada.**

**Veredito: troca.** Duas formas com fonte. A diferença entre elas é só a referência (onde o fator vale 1), e essa escolha é de produto:

- **Proposta principal (B): fator = mín(1; LS)**, com a referência na parcela-padrão da USLE, que é publicada. Com rampa de 46 m, por classe: **0,22 / 0,84 / 1 / 1 / 1**. Quando houver `declividade_pct` do SRTM, calcular o LS da declividade medida (interpolando a tabela ou pela equação do AH 703), em vez de usar o meio da classe. Pela pergunta 7, usar o meio da classe. O teto em 1 é escolha a declarar: acima da parcela-padrão, o motor não separa ondulado de montanhoso.
- **Alternativa (A): fator = mín(1; LS ÷ LS do forte ondulado)**: 0,03 / 0,11 / 0,36 / 1 / 1. Mantém o forte ondulado como hoje, mas no plano e no suave ondulado a nota de erosão fica perto de 1 em qualquer rotação. O critério deixaria de separar estratégias justamente onde está a maior parte das lavouras de grão.

Recomendo **B**. Num solo descoberto a 5 % de declive, a perda já é metade ou mais da parcela-padrão, e isso merece aparecer.

**Efeito esperado** (parcela coberta 0,5; solo de textura média, K = 0,016; K proposto na seção 2.6):

| Classe | Nota hoje | Nota com B e o K proposto |
|---|---|---|
| plano | 0,91 | 0,92 |
| suave ondulado | 0,81 | 0,70 |
| ondulado | 0,72 | 0,64 |
| forte ondulado / montanhoso | 0,63 | 0,64 |

A erosão passa a pesar mais no suave ondulado e no ondulado. No plano e no muito inclinado, quase nada muda.

`FATOR_DECLIVE_SEM_DADO = 0,5` é **sem fonte**: fica entre o plano e o suave ondulado e deve continuar marcado como "valor médio" na lacuna, como já acontece.

Limite do dado, para a tela: o SRTM de 30 m numa grade 3×3 suaviza o relevo, e a declividade do ponto não é a do talhão inteiro (já dito na metodologia de declividade).

### 2.6 Erodibilidade K (`K_LIMITE_BAIXA`, `K_LIMITE_MEDIA`, `FATOR_K`)

**A conta do motor.** O K vem do SoilGrids pelo método de Williams (EPIC), em t·ha·h/(ha·MJ·mm), com fator de conversão 0,1317 (`solo/derivados.py`). O AH 537 dá 1,313 para MJ·cm, ou seja 0,1313 para MJ·mm. A diferença é de 0,3 %, e a unidade está certa. Classes de hoje: baixa < 0,020, média < 0,035, alta a partir daí. Fatores: 0,75 / 1,0 / 1,25. O fator K multiplica o fator de declive.

**A multiplicação é coerente com a USLE?** Sim. A USLE é um produto (*"A=RKLSCP"*, AH 537): dobrar o K dobra a perda. Multiplicar o fator de declive pelo fator K é a forma certa. O problema é a escala: na USLE, o fator relativo deveria ser K ÷ K de referência, e 0,75 / 1 / 1,25 encolhe uma diferença real de 4 a 6 vezes para 1,7 vez.

**Fontes**
- Mannigel et al. 2002, *Fator erodibilidade e tolerância de perda dos solos do Estado de São Paulo*, Acta Scientiarum 24(5):1335-1340 (https://periodicos.uem.br/ojs/index.php/ActaSciAgron/article/download/2374/1787). Classes, em t·ha·h/(ha·MJ·mm): *"muito alto para valores de K entre 0,0450 e 0,0600"*; *"alto para valores de K entre 0,0300 e 0,0450"*; *"médio para valores de K entre 0,0150 e 0,0300"*; *"baixo para valores de K entre 0,0090 e 0,0150"*; *"muito baixo para valores de K menores do que 0,0090"*.
- Do mesmo artigo, os valores de referência dos EUA: *"Foster et al. (1981) classificaram a magnitude dos fatores K iguais a 0,01; 0,03 e 0,06 t.ha.h/ha.MJ.mm, respectivamente, como baixa, moderada e alta."*
- Ainda no artigo, K medidos: Latossolo Vermelho Distrófico típico muito argiloso, *"0,0061"*; Latossolo Vermelho Distroférrico muito argiloso, *"0,0071"*; Argissolo Vermelho-Amarelo, *"0,0466"*.

**A conta: K de Williams em solos típicos** (com o código do app):

| Solo (argila/areia/silte %, C g/kg) | K de Williams | Classe hoje | Classe proposta |
|---|---|---|---|
| Latossolo muito argiloso (70/15/15, 20) | 0,0126 | baixa | baixa |
| Latossolo argiloso (50/35/15, 15) | 0,0138 | baixa | baixa |
| Textura média (25/65/10, 10) | 0,0163 | baixa | média |
| Arenoso/médio (15/75/10, 8) | 0,0169 | baixa | média |
| Franco-siltoso dos EUA (20/20/60, 15) | 0,0234 | média | média |
| Muito siltoso (15/15/70, 10) | 0,0337 | média | alta |

Com os limites de hoje, quase todo solo brasileiro típico cai em "baixa", e o Williams só passa de 0,035 com mais de 70 % de silte. Isso aumenta a nota de erosão de quase todas as fazendas. Os limites de Mannigel põem os Latossolos argilosos em "baixa", o que bate com os K medidos no artigo (0,006 a 0,007, ainda mais baixos que o Williams), e os solos de textura média em "média".

**Veredito: troca.**
- Limites: **0,015 e 0,030** (Mannigel et al. 2002: muito baixo + baixo = baixa; médio = média; alto + muito alto + extremamente alto = alta).
- Fator: **proporcional ao K**, como na USLE: fator K = K ÷ 0,0225 (centro da classe "médio", 0,015–0,030). Na tabela acima: 0,56 / 0,61 / 0,72 / 0,75 / 1,04 / 1,50. Se a equipe preferir manter classes (o K do SoilGrids é aproximado), usar o K do centro de cada classe: baixa ≈ 0,010 (valor "baixa" de Foster) → **0,44**; média → **1**; alta ≈ 0,0375 (centro de 0,030–0,045) → **1,67**.
- `FATOR_K_SEM_DADO = 1,0` (neutro) continua sem fonte, mas faz sentido: usa a classe média.

**Efeito esperado:** nos Latossolos argilosos, o fator cai de 0,75 para cerca de 0,6, e a nota de erosão sobe um pouco. Nos solos de textura média, o fator fica quase igual, cerca de 0,72–0,75 (contínuo), ou sobe para 1,0 (por classe). Nos siltosos, vai a 1,5. Junto com a troca do declive, ver a tabela da seção 2.5.

**Limite a mostrar:** o Williams é uma estimativa pela textura. Nos Latossolos muito argilosos ele dá cerca de 0,013, contra 0,006–0,007 medidos (Mannigel et al. 2002). O texto da tela deve dizer "estimada pelo mapa global de solo".

### 2.7 Desconto de pragas (`PRAGAS_DESCONTO_MESMA_FAMILIA = 0,2`)

**A conta do motor** (`criterios.nota_pragas`). As culturas são ordenadas pelo mês de início, e a rotação é tratada como ciclo (com 3 culturas ou mais, a última volta para a primeira). Nota = (famílias distintas − 1) ÷ (culturas − 1) − 0,2 × (pares seguidos da mesma família).

**Fontes do princípio**
- Embrapa Soja, Circular Técnica 45 (2007) (https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/470323/1/circtec45.pdf): *"a rotação de culturas consiste em alternar no tempo, o cultivo de espécies vegetais numa determinada área, preferencialmente com culturas que possuem sistemas radiculares diferentes (gramíneas e leguminosas, por exemplo)"*.
- Embrapa, Salton & Hernani (https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/857203/1/32556.pdf): *"Com a rotação é possível quebrar o ciclo de várias pragas e doenças"*.
- FAO, Agricultura de Conservação (seção 2.3): diversificação com *"at least three different crops"*.

Nenhuma fonte dá um número como 0,2. A família botânica é um indicador aproximado: pragas e doenças passam mais entre plantas próximas.

**A conta com o código atual:**

| Rotação | Nota hoje | Nota proposta |
|---|---|---|
| soja só | 0,0 | 0,0 |
| soja + milho | 1,0 | 1,0 |
| soja + milho + trigo | **0,3** | 0,67 |
| soja + milho + crotalária | **0,3** | 0,67 |
| soja + milho + nabo forrageiro | 1,0 | 1,0 |
| milho + milheto | 0,0 | 0,0 |
| soja + feijão | 0,0 | 0,0 |
| aveia + soja + trigo + milho | **0,0** | 0,5 |

O problema: acrescentar uma terceira cultura de família que já existe **derruba** a nota de 1,0 para 0,3. A rotação clássica da Embrapa (milho, aveia, soja, trigo) recebe 0,0, a mesma nota da soja sozinha. O termo (distintas − 1) ÷ (n − 1) já pune a repetição. O desconto de 0,2 pune de novo. E a candidata de leguminosa na janela (regra 3 das candidatas) piora a nota de pragas.

**Veredito: troca** (de forma). O 0,2 é **sem fonte**, e a forma contradiz o próprio princípio citado.

**Proposta:** tirar o desconto e o termo de famílias distintas. Nota = 1 − (pares seguidos da mesma família ÷ total de pares), com a volta da última para a primeira. Uma cultura só = 0. Essa forma não tem número escolhido: mede só "quantas vezes a cultura seguinte é da mesma família que a anterior", que é o mecanismo das fontes (quebrar o ciclo entre uma cultura e a seguinte).

**Efeito esperado:** a nota de pragas deixa de cair quando se acrescenta cultura. Rotações com 3 ou mais culturas sobem de 0,0–0,3 para 0,5–0,67. Onde não há repetição seguida, nada muda.

Se a equipe quiser premiar a diversidade da FAO (3 culturas ou mais), um bônus seria escolha de produto, a declarar.

### 2.8 Escala de renda (`RENDA_POR_COMERCIAIS`: 0 → 0; 1 → 0,5; 2 → 0,8; 3 ou mais → 1,0)

**A conta do motor** (`criterios.nota_renda`): conta as culturas com o tipo `comercial` na rotação. Não usa preço, produtividade nem custo.

**Veredito: sem fonte.** A escala de ganho decrescente (a 2ª cultura vale menos que a 1ª) é escolha da equipe. É razoável, porque mais culturas comerciais trazem mais renda e mais trabalho e risco, mas nenhuma fonte dá esses degraus.

**Como deixar explícito**
- Na tela: "Renda extra = quantas culturas da rotação você pode vender. Não é lucro nem preço." (**Feito em 15/11/2026**, na explicação da nota de renda: "Contamos as culturas de venda; preço e produção da sua região ainda não entram nesta nota.")
- No documento do motor: registrar a escala como decisão.

**Forma com fonte de calibrar:** o valor da produção por hectare do IBGE PAM no município (a fonte de renda escolhida na D-009) daria uma nota relativa, por exemplo o valor por hectare da rotação dividido pelo da melhor rotação candidata. Nos EUA, o arquivo do NASS carregado hoje não tem o valor da produção (D-010). Até lá, a contagem fica, com o aviso acima.

### 2.9 Máximo de 30 candidatas (`MAX_CANDIDATAS = 30`)

**A conta do motor** (`candidatas.gerar_candidatas`): as candidatas são geradas em ordem (janela vazia, troca por tolerante à seca, leguminosa) e cortadas nas 30 primeiras **antes do filtro**. Cada candidata é avaliada em memória, sem rede (`motor_service.analisar_entradas`), então o custo de avaliar mais candidatas é pequeno.

**A conta: quantas candidatas o catálogo atual gera** (rodando o gerador sem o corte):

| Rotação atual | Candidatas |
|---|---|
| BR soja (out–fev) + milho safrinha (mar–jun) | 14 |
| BR milho só (nov–mar) | 21 |
| BR soja + milho + trigo, sem mês vazio | 10 |
| BR milho + sorgo, vazio mai–set | 25 |
| BR milho + sorgo + girassol, vazio jul–out | 28 |
| EUA milho (mai–set) | 17 |
| EUA milho + cevada, vazio dez–abr | 20 |

O máximo teórico no Brasil é cerca de 16 (janela) + 7 (tolerante à seca) + 5 leguminosas × (culturas − 1). Com 4 culturas e mês vazio, passa de 30. Nesse caso, as que caem são sempre as **últimas geradas**, as trocas por leguminosa, e antes do filtro: uma inviável pode tomar o lugar de uma viável.

**Veredito: sem fonte** (escolha de engenharia). Hoje o corte não age nos casos testados.

**Proposta:** aplicar o limite **depois** do filtro (sobre as sobreviventes) ou tirá-lo. Se quiser um teto de segurança, que seja alto (por exemplo, 100), com um aviso no log quando cortar. A lista de eliminadas mostrada ao produtor também pode ter um teto próprio para a tela.

---

## 3. O que o time do motor precisa mudar no código

Nada abaixo foi alterado por esta conferência.

1. **`parametros.py`, comentários.** Trocar "proposta, validar com o Yury" pelo veredito e pela fonte de cada linha (tabela da seção 1). Nos itens sem fonte (pesos da Terra, forragem, renda, máximo de candidatas, fator de declive sem dado), escrever "escolha de produto (VALIDACAO-PARAMETROS-MOTOR.md)".
2. **Declive (`FATOR_DECLIVE`, `criterios.nota_erosao`).** Trocar pelos LS da RUSLE com rampa de 46 m e teto 1: plano 0,22, suave ondulado 0,84, ondulado 1, forte ondulado 1, montanhoso 1. Melhor ainda: quando `relevo.declividade_pct` existir, calcular o LS da declividade medida (tabela da seção 2.5 ou equação do AH 703). Declarar a rampa como constante (`RAMPA_TIPICA_M = 46`).
3. **K (`K_LIMITE_BAIXA`, `K_LIMITE_MEDIA`, `FATOR_K`).** Limites 0,015 e 0,030. Fator proporcional: `fator_k = k_usle / 0.0225`, ou, por classe, 0,44 / 1 / 1,67. Manter a classe só para o texto da tela.
4. **Pragas (`nota_pragas`).** Tirar `PRAGAS_DESCONTO_MESMA_FAMILIA` e o termo (distintas − 1) ÷ (n − 1). Nota = 1 − repetidos ÷ pares, com a volta da última para a primeira. Uma cultura = 0. Atualizar os testes de `test_motor_criterios.py`.
5. **Regra 17 (frio por cultura). Implementada em 15/11/2026 (itens a a d); o texto abaixo é o pedido original.** a) `catalogo.py`: ler `tmin_critica_c`, `fase_frio_inicio_frac`, `fase_frio_fim_frac` e `tmin_dias_seguidos` como números e `fase_sensivel_frio` e `tmin_efeito` como texto (hoje caem em `extras`). b) Clima: dado diário (ou por decêndio) de `T2M_MIN`, com contagem na janela da fase e de dias seguidos, para qualquer limiar do catálogo (ver 2.2, item 2; migration quando implementar). c) `_geada`: com `tmin_critica_c`, usar o limiar, a janela em dias e os dias seguidos; `tmin_efeito` = `aviso` gera aviso, não eliminação; sem limiar, manter o terço do meio com 2 °C. d) Texto do alerta: usar a fase da cultura no lugar de "fase de floração" fixo, em linguagem simples (ex.: "florada", "enchimento dos grãos"), e dizer "frio", não "geada", quando o limiar for acima de 0 °C (arroz).
6. **Candidatas (`MAX_CANDIDATAS`).** Mover o corte para depois do filtro em `motor_service.analisar_entradas`, ou tirá-lo. Ajustar `test_no_maximo_30_candidatas`.
7. **Forragem (`CLASSE_FORRAGEIRO`).** Decidir entre 0 / 0,33 / 0,67 / 1,0 e o atual com o motivo escrito.
8. **Texto da tela** (com o front; a parte da renda foi feita em 15/11/2026): explicar a nota Terra (pesos da equipe), a renda (contagem, não lucro), o aviso de água (80 % da água ≈ 15–25 % de perda, segundo a FAO) e a erodibilidade ("estimada pelo mapa global de solo").
9. **Opcional (v2):** contar como cobertos os meses de palha após a colheita, com `cobertura_solo`; coluna Ky no catálogo para o aviso de água; nota de renda pelo valor da produção do IBGE PAM.

---

## 4. Fontes consultadas

| Fonte | URL | Usada em |
|---|---|---|
| FAO-56, cap. 8 (eq. 90, Tabela 24, Ky do FAO-33) | https://www.fao.org/4/x0490e/x0490e0e.htm | 2.1 |
| FAO-56, definição das fases | https://www.fao.org/4/x0490e/x0490e0a.htm | 2.2 |
| FAO-56, Tabela 11 (duração das fases) | https://www.fao.org/4/x0490e/x0490e0b.htm | 2.2 |
| FAO, Irrigation Water Management, Training Manual 3 (chuva efetiva) | https://www.fao.org/4/s2022e/s2022e08.htm | 2.1 |
| MAPA, ZARC soja SP, Portaria SPA/MAPA nº 381/2025 | https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-risco-climatico/portarias/safra-vigente/sao-paulo/PORTN381SOJASP.ret2.pdf | 2.1, 2.2 |
| FAO, Frost protection, vol. 1, Tabela 4.5 | https://www.fao.org/4/y7223e/y7223e0a.htm | 2.2 |
| FAO, Frost protection, vol. 1, temperatura crítica no abrigo | https://www.fao.org/4/y7223e/y7223e07.htm | 2.2 |
| USDA Agriculture Handbook 537 (USLE) | https://www.ars.usda.gov/ARSUserFiles/60600505/RUSLE/AH_537%20Predicting%20Rainfall%20Soil%20Losses.pdf | 2.5, 2.6 |
| NRCS Oklahoma, RUSLE cap. 3, tabelas de LS | https://efotg.sc.egov.usda.gov/references/Agency/OK/RUSLE_Chap3_LS_Factors.pdf | 2.5 |
| Embrapa, Boletim de P&D 213 (classes de relevo, Santos et al. 2005) | https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/950793/1/BPD213RelevoZonaMata.pdf | 2.5 |
| Mannigel et al. 2002, Acta Scientiarum 24(5) | https://periodicos.uem.br/ojs/index.php/ActaSciAgron/article/download/2374/1787 | 2.6 |
| Lopes, Cogo & Levien 1987, RBCS 11:71-75 | https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/132491/1/Revistabrasileiradecienciadosolov.11p.7175.pdf | 2.4 |
| FAO, Agricultura de Conservação | https://www.fao.org/conservation-agriculture/en/ | 2.3, 2.7 |
| UGA Extension C962 (Soil Conditioning Index do NRCS) | https://openscholar.uga.edu/record/26479/files/C962.pdf | 2.3 |
| Embrapa Soja, Circular Técnica 45 (rotação de culturas) | https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/470323/1/circtec45.pdf | 2.7 |
| Embrapa, Salton & Hernani (rotação de culturas) | https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/857203/1/32556.pdf | 2.7 |

Não confirmados nesta conferência (e por isso não usados como fonte): o PDF original do AH 703 (o link do ARS devolveu HTML) e a equação de LS de Bertoni & Lombardi Neto (só aparece citada por terceiros).
