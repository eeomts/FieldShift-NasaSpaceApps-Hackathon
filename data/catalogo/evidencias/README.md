# Evidências da base de culturas

Um arquivo por cultura de `../culturas.csv`, com a origem de cada número.

| Campo | O que tem |
|---|---|
| `valores` | Os valores que entraram em `culturas.csv` |
| `mudancas` | O que mudou e por quê, em ordem |
| `evidencias` | Fonte, link e trecho literal de cada coluna |
| `pendencias` | O que ficou sem fonte primária, decisões em aberto e alternativas |
| `pendencias_resolvidas` | Pendências antigas já resolvidas (histórico) |
| `origem` | Origem de cada coluna do filtro do motor (ver "Confiança") |
| `confianca_calculo` | A conta que gerou `confianca_parametros` |
| `regua` | Números e decisões que geram as colunas qualitativas (ver "Régua") |

Os valores foram conferidos em fontes primárias (Embrapa, FAO-56, FAO ECOCROP, ZARC/MAPA, IBGE e artigos científicos). As linhas que começam com `DECISÃO` registram escolhas do time ou do usuário. `PROXY` (outra espécie ou categoria genérica), `CÁLCULO` (estimativa do time, por exemplo Kc × ET0 com NASA POWER) e `ESTIMATIVA` aparecem marcados na coluna `fontes`.

Ao mudar um valor em `culturas.csv`, atualize também o arquivo da cultura.

## Convenções dos números
- `ciclo_dias_min/max`: da semeadura (ou da emergência, quando a fonte só der isso; a diferença é de 5 a 10 dias) à maturação fisiológica, a mesma fase dos graus-dia. A colheita pode vir depois, com o grão secando no campo.
- Planta de cobertura (sem `comercial` em `tipos`): ciclo, água e Kc valem até o **manejo no florescimento**, não até o grão.
- Cobertura cortada verde: `kc_final` = `kc_medio` (FAO-56, cap. 6).
- Kc medido em outro clima é convertido para a condição padrão do FAO-56 (eq. 62) e **limitado a 1,25** (FAO-56 eq. 72: no clima padrão, Kc max = max(1,2; Kcb + 0,05)). O valor medido fica nas evidências.
- Perenes forrageiras (`pastagem`; `alfafa` nos EUA): não têm ciclo de colheita. `ciclo_dias_*` e `graus_dia_ciclo_*` ficam vazios, com origem `vazio_nao_se_aplica`; as colunas de água e o Kc trazem a exigência **anual** (o Kc é a média dos cortes ou pastejos). O intervalo entre cortes e a soma térmica por corte ficam só nas pendências, como referência de manejo.
- `agua_ciclo_mm_min/max` é o **consumo com produtividade plena** (sem déficit), não o mínimo para colher algo. O motor deve preferir a água calculada no local (Kc × ET0 do NASA POWER); a coluna é reserva. Ver a regra 1 do motor: a água **não elimina** cultura de sequeiro.
- `tipos` contém `forrageira` quando `uso_forrageiro` = `principal`, ou quando é `com_restricao` numa cultura sem `comercial` (cobertura que pode ser pastejada). Grão com palhada ou rama que o animal come de vez em quando não leva `forrageira`.
- `tmax_critica_c`: temperatura que causa dano numa **fase sensível** (florescimento, enchimento de grão), dita na evidência. Cultura manejada ou morta antes de florescer fica vazia, com a justificativa em `origem`/`pendencias`; o limite de crescimento do ECOCROP (TMAX) não é limiar de dano e só entra quando a cultura é manejada no florescimento (coberturas do Brasil), marcado assim na evidência.

## Exigência de graus-dia (`graus_dia_ciclo_min/max`)
- Fase: da **semeadura** até a maturação fisiológica (grãos) ou até o **manejo** (coberturas: no florescimento, na dessecação antes da cultura seguinte ou na morte pelo frio, conforme `tipo_manejo`). Perenes forrageiras (pastagem, alfafa): não se aplica.
- Método: GD = soma de max(0, Tmed − Tb), com Tmed = (Tmax + Tmin)/2, **sem teto**, e Tb = `temp_base_c` da linha. Fontes com outra Tb ou com teto foram convertidas (a conta está em `origem`).
- O mínimo é a **mediana** (2001-2020) do cenário de **menor soma** da região de referência: o local mais frio onde há ensaio ou recomendação, com a data de semeadura usada ali e o `ciclo_dias_min`. Na maioria das culturas é a semeadura mais tardia; em culturas que somam mais quando semeadas mais tarde (ex.: feijão na Dakota do Norte), é a data dos ensaios. Valor de ensaio de um ano só, ou mediana de ensaios, não substitui essa mediana climática; fica como conferência na evidência. Em ano frio a soma local pode ficar abaixo: por isso o motor compara a mediana local, não o ano a ano (regra 2).
- Uso no motor: ver a regra 2 (grãos: abaixo de 90% do mínimo elimina; coberturas: não elimina). Em culturas de dia curto (guandu, crotalária, milheto, nabo) e na soja, a soma varia com a época de semeadura e o grupo de maturação.
- Mandioca: a faixa vai do plantio a uma colheita de 8-12 meses (não é maturação); o filtro serve só como teste de frio (eliminar abaixo do mínimo).
- **Atenção ao NASA POWER**: nos ensaios conferidos, a Tmed do POWER ficou 1-2 °C abaixo da estação local. Com Tb alta (crotalária 16, mandioca 15, milheto 13) isso tira 12-25% da soma. Decisão (14/11): nas culturas de Tb alta (crotalária, milheto, mandioca), a exigência é recalculada com o POWER nas datas e locais dos ensaios, para ficar na mesma régua do motor.

## Regras para o motor (decididas em 14/11; regras 1, 2, 8 e 11 a 16 revistas em 15/11)
O motor ainda não lê este catálogo. Ao implementar, siga estas regras, que vêm das decisões tomadas sobre os dados. Valem para os dois catálogos (Brasil e EUA).

1. **Água:** calcular a demanda no local (Kc × ET0 do NASA POWER, a mesma conta de `scripts/etc_nasa_power.py`) e comparar com a chuva local na janela da cultura. A água **nunca elimina cultura de sequeiro**: chuva abaixo da demanda local (ou, sem a conta local, abaixo de `agua_ciclo_mm_min`) marca "água no limite" e mostra o déficit estimado em mm. Só elimina pela água o `arroz_irrigado` sem várzea ou irrigação (regra 8). Perenes forrageiras (`pastagem`, `alfafa`): a coluna é anual; comparar com a chuva do ano, com a mesma regra. Motivo: a coluna é consumo com produtividade plena, e a chuva da estação fica abaixo dela em regiões onde a cultura de sequeiro é típica (girassol na Dakota do Norte, soja em Iowa, algodão em Lubbock, alfafa no Nebraska).
2. **Graus-dia:** uma única função compartilhada entre o dataset e o motor, GD = soma de max(0, Tmed − Tb), **sem teto**. Compare a **mediana 2001-2020** dos graus-dia locais na janela da cultura. Grãos: mediana abaixo de 90% do `graus_dia_ciclo_min` elimina; entre 90% e 100% marca "no limite térmico, validar localmente"; se o P10 local ficar abaixo de 90% do mínimo, só avisa "em ano frio pode não completar". Coberturas: graus-dia **não elimina**; abaixo do mínimo, avisa "pouco crescimento antes do frio ou do manejo" (quem decide se cabe é a janela, regra 12). Perenes forrageiras: não se aplica.
3. **Viés de temperatura do POWER:** não corrigir a temperatura no filtro de graus-dia. O viés do POWER muda de sinal conforme o local (1-2 °C mais frio em Santa Maria e Seropédica, ~2 °C mais quente em Rio Largo-AL), e as exigências das culturas de Tb alta (crotalária, milheto, mandioca) já foram calculadas com o próprio POWER nas datas dos ensaios. Nas demais, o efeito é pequeno e a margem de 10% do filtro suave cobre.
4. **Consórcio milho + braquiária (ILP):** usar o Kc do componente dominante em cada período (milho até a colheita, braquiária depois) e a massa de `regua.arranjos.consorcio_milho_safrinha` da pastagem.
5. **Valor forrageiro vazio ("não sei"):** ignorar o critério "Comida pros animais" para aquela cultura, redistribuir o peso entre os outros critérios e mostrar "sem dado". Não usar padrão regional.
6. **Palhada local:** para soja, milho, trigo, arroz e sorgo, escalar a massa de palhada pela produtividade da PAM do município (média de 3 a 5 anos), com a regressão da Tabela 11.2 do IPCC; para o feijão, a razão R_AG da Tabela 11.1a (IPCC 2019). Marcar a origem como cálculo. Nas demais culturas, usar o típico do bloco `regua`.
7. **Teste de sensibilidade:** para culturas de confiança `baixa`, rodar a comparação com o Kc no mínimo e no máximo plausíveis. Se a ordem das estratégias não mudar, o cartão pode dizer que a recomendação é robusta.
8. **Arroz irrigado:** só é candidato se o produtor tiver várzea ou irrigação, e não passa pelo filtro de chuva. O id `arroz_irrigado` está em `agroia/base/culturas.json` desde o commit f910193. Quando o produtor escreve só "arroz" ou "rice", o app não escolhe: pede para o produtor dizer se é irrigado ou de terras altas (não decide pelo país).
9. **Mandioca:** o filtro de graus-dia serve só como teste de frio (eliminar abaixo do mínimo); não eliminar pelo máximo.
10. **Confiança baixa na tela:** mostrar a faixa em vez de um número e explicar em linguagem simples, com os textos de `lacuna_informacao` e `risco_revisao_local`. Exemplo: "Ainda não existem medições no Brasil de quanta água esta cobertura usa. Usamos valores de outros países, por isso a estimativa pode errar. Confirme com seu agrônomo."
11. **Calor (`tmax_critica_c`):** vale só na fase sensível dita na evidência e gera **aviso** de risco de calor naquela fase; nunca elimina. Vazio = sem aviso.
12. **Janela das coberturas:** só sugerir a cobertura depois da cultura X se a colheita de X, no calendário do produtor, cair até `semeadura_fim` e X for compatível com `condicao_semeadura` (`apos_colheita_graos` serve depois de qualquer grão; `apos_cereal_inverno` e `apos_silagem` só depois deles). `a_lanco_lavoura_em_pe` aparece só como informação no detalhe, nunca como sugestão. Com isso, aveia e nabo dos EUA (semeadura em agosto e setembro) não aparecem depois do milho ou da soja colhidos em outubro. Coberturas sem janela preenchida (Brasil, por enquanto): mostrar "janela não confirmada".
13. **Região válida:** com `estados_validos` preenchido e o ponto fora da lista, mostrar "sem dado para sua região" para aquela cultura, sem sugerir nem eliminar. Se houver arranjo regional no bloco `regua` com o estado do ponto, usar os números do arranjo.
14. **Perenes forrageiras (`pastagem`, `alfafa`):** sem filtro de ciclo nem de graus-dia; o vazio dessas colunas é "não se aplica", não "não sei". Água anual pela regra 1.
15. **Faixa junto com a classe:** quando `regua.detalhe.depende_da_epoca` for `true`, a tela mostra a classe com a faixa (ex.: "palhada baixa, de 0,5 a 5 t/ha conforme a data de manejo").
16. **Aviso junto da classe:** se `regua.avisos.<coluna>` existir, a tela mostra o texto sempre junto da classe daquela coluna (no cartão, não só no detalhe), em qualquer confiança. Como o aviso está no arquivo de evidência e não no CSV, o carregador do catálogo precisa levar o bloco `regua.avisos` junto com a linha.
17. **Frio (decidida em 15/11, a implementar):** com `tmin_critica_c` preenchida, o teste usa o limiar da cultura (no lugar dos 2 °C fixos do indicador de geada) **só nos dias da fase sensível**, não em meses inteiros. A fase vai da semeadura + `fase_frio_inicio_frac` × ciclo até a semeadura + `fase_frio_fim_frac` × ciclo, com ciclo = média de `ciclo_dias_min` e `ciclo_dias_max` da linha (`ciclo_todo` = o ciclo inteiro; perene = o ano todo). Um ano conta quando, dentro da fase, houver `tmin_dias_seguidos` dias seguidos (vazio = 1) com mínima do ar **abaixo de `tmin_critica_c`**. Se mais de 30% dos anos contarem: com `tmin_efeito` = `elimina` (ou vazio), a cultura sai; com `aviso` (dano parcial, como a esterilidade do arroz por frio), ela fica, com o aviso "frio na floração em X% dos anos", como o calor na regra 11. O texto da tela diz "geada" só quando o limiar é de geada (até 0 °C); acima disso, "frio". Sem `tmin_critica_c`: comportamento atual (2 °C no terço do meio, se `sensivel_geada`). Por decisão de 15/11 ficam assim, por falta de limiar com fonte: feijão-caupi, mandioca, milheto e braquiária (Brasil) e amendoim (EUA). Isso pede o clima por dia (ou ao menos por decêndio), e não só o `clima_mensal` de hoje, que guarda os dias abaixo de 2 °C.

### Como o motor usa cada coluna por tipo de cultura

| Coluna | Grão de sequeiro | Arroz irrigado | Cobertura | Perene forrageira |
|---|---|---|---|---|
| `agua_ciclo_mm_*` / conta local | aviso "água no limite" (regra 1) | elimina sem várzea ou irrigação (regra 8) | aviso | aviso, anual |
| `graus_dia_ciclo_*` | mediana local < 90% do mín. elimina (regra 2) | igual ao grão | só aviso (regra 2) | não se aplica |
| `tmax_critica_c` | aviso na fase sensível (regra 11) | aviso | vazio, salvo manejo no florescimento | aviso, se houver |
| `sensivel_geada` | elimina se a geada cair na fase sensível da evidência | igual | dano só na fase dita na evidência | idem |
| `tmin_critica_c`, fase, `tmin_dias_seguidos`, `tmin_efeito` | limiar, dias da fase e dias seguidos do teste de frio (regra 17) | igual (esterilidade = aviso) | igual, se a fase cair antes do manejo | fase `ciclo_todo` |
| janela e `condicao_semeadura` | — | — | decide se cabe depois da cultura anterior (regra 12) | — |
| `estados_validos` | regra 13 | regra 13 | regra 13 | regra 13 |

## Confiança (`confianca_parametros`)
Para cada coluna do filtro do motor (`temp_base_c`, `ciclo_dias_min/max`, `graus_dia_ciclo_min/max`, `agua_ciclo_mm_min/max`, `kc_inicial/medio/final`, `profundidade_raiz_m`), `origem` registra um tipo:

| Tipo | Conta como lacuna? |
|---|---|
| `medido` (medição publicada, em condição comparável) | não |
| `publicado` (tabela ou recomendação oficial para a própria espécie; inclui o Kc ini do grupo no FAO-56 e contas simples sobre números oficiais) | não |
| `convencao_com_fonte` (regra do time apoiada em texto publicado) | não |
| `vazio_nao_se_aplica` | não |
| `estudo_unico`, `calculo`, `proxy`, `convencao_sem_fonte`, `vazio_nao_sei` | **sim** |

0 lacunas = `alta`; 1 a 2 = `media`; 3 ou mais = `baixa`.

Critérios para escolher o tipo (decididos em 15/11, revisão dos lotes 1 e 2 dos EUA):
- `estudo_unico`: uma fonte só, com **1 local, ou 1 ano, ou 1 cultivar**, ou ensaio em câmara. Ensaio de campo com **2 ou mais locais e 2 ou mais anos** na região = `medido`. Estudo lido só pelo resumo, sem a tabela do número, = `estudo_unico`.
- Ciclo cujo fim é uma **data de recomendação publicada** (semeadura e manejo da extensão) = `publicado`; fim pela morte no frio, sem data publicada = `convencao_com_fonte`.
- Kc do FAO-56 da própria espécie, ou do grupo que a Tab. 12 dá para ela = `publicado`; Kc de outra espécie = `proxy`.

## Colunas de janela, região e texto para o produtor
Valem para os dois catálogos (Brasil e EUA). Vazias = "não sei" (ou "sem restrição", em `estados_validos`).

| Coluna | Formato | O que é |
|---|---|---|
| `semeadura_inicio`, `semeadura_fim` | `MM-DD` | Janela de semeadura recomendada na região de referência, com fonte. **Obrigatória nas coberturas** (sem `comercial`). Nos grãos dos EUA, é o "most active" (15 a 85% semeado) do USDA Handbook 628: o que os produtores fazem, não uma recomendação |
| `manejo_inicio`, `manejo_fim` | `MM-DD` | Janela de manejo (dessecação, rolagem, corte) ou data típica da morte pelo frio |
| `tipo_manejo` | `dessecacao`, `morte_pelo_frio`, `rolagem`, `corte` ou vazio | Como a cobertura termina |
| `condicao_semeadura` | lista com `\|`: `apos_colheita_graos`, `apos_cereal_inverno`, `apos_silagem`, `a_lanco_lavoura_em_pe` | Depois de quê a cobertura pode ser semeada na janela |
| `estados_validos` | lista com `\|` de siglas (UF no Brasil, USPS nos EUA); vazio = sem restrição | Onde a linha vale. Fora dela, o motor mostra "sem dado para sua região" |
| `lacuna_informacao` | texto simples, até 300 caracteres | O que não sabemos, para a tela (requisito R7 do Field Shift). **Obrigatório com confiança `baixa`** |
| `risco_revisao_local` | texto simples, até 300 caracteres | O que o produtor deve confirmar com o agrônomo ou a extensão. **Obrigatório com confiança `baixa`** |

Os dois textos são para o produtor: sem sigla, sem nome de modelo, sem "proxy" ou "P10". Exemplo: "Não achamos medição de quanta água o trevo-encarnado usa na Geórgia; usamos a de um trevo parecido."

## Dano por frio (`tmin_critica_c` e fase sensível)
Valem para os dois catálogos. Vazias = "não sei". A fisiologia é a mesma da espécie nos dois países (mesmo limiar, mesma fase, mesma fonte principal); a fração do ciclo segue o ciclo de cada linha. **Exceção:** grupo de cultivar diferente, quando uma fonte diz que os grupos diferem no frio (ex.: arroz japônica dos EUA x cultivares do Brasil); cada evidência registra o grupo, com fonte, e o validador aceita a diferença só na lista de exceções (`EXCECOES_FRIO` em `scripts/montar_csv.py`).

| Coluna | Formato | O que é |
|---|---|---|
| `tmin_critica_c` | °C | Temperatura **mínima diária do ar a 2 m** (abrigo meteorológico, a mesma medida do `T2M_MIN` do NASA POWER) abaixo da qual há **dano à produção** na fase sensível |
| `fase_sensivel_frio` | `emergencia`, `vegetativo`, `floracao`, `enchimento_grao` ou `ciclo_todo` | Em que fase o frio causa esse dano. `floracao` inclui o espigamento ou o emborrachamento quando a fonte junta as fases |
| `fase_frio_inicio_frac`, `fase_frio_fim_frac` | 0 a 1 | Onde a fase cai no ciclo da linha (`ciclo_dias`, da semeadura à maturação ou ao manejo): dias da semeadura ao início e ao fim da fase, publicados, divididos pelo ciclo médio da linha. `ciclo_todo` = 0 e 1. Perenes: vazias |
| `tmin_dias_seguidos` | inteiro ≥ 2 | Quantos dias seguidos abaixo do limiar a fonte exige (ex.: 3 no arroz pelo zoneamento). Só com fonte que diga a duração; vazia = 1 dia |
| `tmin_efeito` | `elimina` ou `aviso` | O que o dano faz: `elimina` = mata a planta ou perde a lavoura; `aviso` = perda parcial (ex.: esterilidade de parte das flores). Vazia = `elimina` |

- **Temperatura do abrigo, não da folha.** Fonte que dá a temperatura na relva, na folha ou no tecido: registre o valor da fonte e só converta para o abrigo com uma relação publicada (a relva fica alguns graus abaixo do abrigo em noite de geada), marcada como `calculo`. Sem conversão com fonte, deixe vazia.
- **Dano à produção, não à folha.** Queima de folha que a planta recupera não conta. O limiar é o da fase em que o frio tira produção (esterilidade, aborto de flor, morte da planta).
- **Cobertura:** limiar de dano antes do manejo. Cobertura que tolera o frio do sistema, ou cujo fim é a morte pelo frio (`tipo_manejo` = `morte_pelo_frio`), fica vazia, com a justificativa em `origem`. Cobertura tropical que morre na geada antes do manejo (crotalária, guandu) leva o limiar, com `ciclo_todo`.
- Cada coluna preenchida aparece em `evidencias[].colunas` (fonte, URL e trecho literal) e tem `origem` (mesmos tipos da tabela de Confiança) em uma destas chaves: `tmin_critica_c` (limiar e `tmin_efeito`), `fase_frio_frac` (a fase e as duas frações) e `tmin_dias_seguidos`. Estas colunas **não entram** na conta de `confianca_parametros`.
- **Vazio justificado:** a justificativa fica em `origem.tmin_critica_c` (tipo `vazio_nao_sei` ou `vazio_nao_se_aplica`); uma entrada em `evidencias` é opcional, quando houver trecho que sustente o vazio.
- `sensivel_geada` continua como está; se a fonte do limiar contradisser a coluna, registre em `pendencias`.

## Régua das colunas qualitativas
Calculada por `../scripts/regua.py` a partir do bloco `regua` de cada arquivo (`python3 -I data/catalogo/scripts/regua.py` mostra a prévia; `--apply` grava, e rodar de novo não duplica nada).

**`aporte_biomassa`**: matéria seca (MS) de palhada que fica no campo, em t/ha (grãos: resíduo pós-colheita; coberturas: MS no manejo; pastagem: braquiária solteira na dessecação). Usa o valor típico.

| baixo | medio | alto |
|---|---|---|
| < 2,3 | 2,3 a < 6 | ≥ 6 |

- **6 t/ha**: "Pode-se considerar que 6 t ha-1 de resíduos sobre a superfície seja uma quantidade adequada ao SPD" (Alvarenga et al. 2001, Informe Agropecuário 22(208)).
- **2,3 t/ha**: massa que dá 50% de cobertura do solo pela curva medida no Brasil, % cobertura = 100(1 − e^(−0,000297·M)), M em kg/ha (Lopes, Cogo & Levien 1987, RBCS 11:71-75); 50% é o mínimo pedido para o plantio direto (Cruz et al. 2001).

**`cobertura_solo`**: a mesma escala, aplicada à palhada que **sobra 60 dias depois**, M · e^(−k·60), com k (decomposição, por dia) medido para a cultura. 60 dias é o tempo até a cultura seguinte cobrir 50% do solo (USDA Agriculture Handbook 537; De Maria, ESALQ 1995). Os limites têm fonte, mas a combinação em regra é decisão do time.

**`valor_forrageiro`**: pelo uso recomendado (`uso_forrageiro`):

| nao_serve | residual | com_restricao | principal |
|---|---|---|---|
| nenhum | baixo | medio | alto |

- `principal` cai para `medio` se a digestibilidade for < 60%, só quando a métrica for DIVMS, DIVMO, DMS, DMO ou DMD (NDT não entra).
- `com_restricao` sem digestibilidade = vazio ("não sei").
- Linhas de grão avaliam a forragem no **cenário de grão** (palhada e grão como ração eventual). A silagem de planta inteira é outro cenário, porque tira a palhada do campo.

**Campos extras do bloco `regua`**
- `excecoes`: valor que vence a régua quando a fonte diz outra coisa (algodão: restos destruídos por lei; mandioca: "não devolve quase nada ao solo"; crotalária: tóxica e recusada pelo animal).
- `arranjos` (pastagem): MS de cada arranjo. A linha usa a braquiária solteira; o consórcio com milho safrinha fica guardado para o motor usar quando a rotação for de integração lavoura-pecuária.
- `arranjos` regionais (ex.: `regua.arranjos.sudeste` da ervilhaca, `regua.arranjos.michigan` do feijão nos EUA): a linha vale para a região de referência; o arranjo guarda os números de outra região (ciclo, graus-dia, água e palhada, quando houver, com `origem` de cada número pelos mesmos tipos da tabela de Confiança) e `estados` como texto com `|` (ex.: `"MI"`, `"GA|AL"`), no mesmo formato de `estados_validos`, para o motor usar quando o ponto estiver nela, quando ele passar a ler arranjos (ainda não lê).
- `avisos`: texto curto (até 200 caracteres, linguagem do produtor) por coluna qualitativa, ex.: `{"valor_forrageiro": "Atenção: ..."}`. É para um risco que a classe sozinha esconde (ex.: o fungo da festuca, que intoxica o gado, numa forragem "alta"). O `regua.py` não mexe nesta chave. Ver a regra 16.
- `detalhe.depende_da_epoca`: `true` quando o mínimo e o máximo da faixa caem em classes diferentes. Na tela, mostre a classe **junto com a faixa** e o aviso "depende da época" (não só no detalhe).
