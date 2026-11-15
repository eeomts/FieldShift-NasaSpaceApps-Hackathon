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
- Perenes sem ciclo de colheita (`pastagem`): as colunas de água trazem a exigência **anual**.
- O motor deve preferir a água calculada no local (Kc × ET0 do NASA POWER). As colunas `agua_ciclo_mm_*` servem de reserva: abaixo do mínimo elimina, entre mínimo e máximo é "água no limite".

## Exigência de graus-dia (`graus_dia_ciclo_min/max`)
- Fase: da **semeadura** até a maturação fisiológica (grãos) ou até o **manejo no florescimento** (coberturas). Pastagem: não se aplica.
- Método: GD = soma de max(0, Tmed − Tb), com Tmed = (Tmax + Tmin)/2, **sem teto**, e Tb = `temp_base_c` da linha. Fontes com outra Tb ou com teto foram convertidas (a conta está em `origem`).
- Uso no motor: abaixo do mínimo, a cultura não completa o ciclo e é eliminada; entre mínimo e máximo, "no limite". Em culturas de dia curto (guandu, crotalária, milheto, nabo) e na soja, a soma varia com a época de semeadura e o grupo de maturação.
- Mandioca: a faixa vai do plantio a uma colheita de 8-12 meses (não é maturação); o filtro serve só como teste de frio (eliminar abaixo do mínimo).
- **Atenção ao NASA POWER**: nos ensaios conferidos, a Tmed do POWER ficou 1-2 °C abaixo da estação local. Com Tb alta (crotalária 16, mandioca 15, milheto 13) isso tira 12-25% da soma. Decisão (14/11): nas culturas de Tb alta (crotalária, milheto, mandioca), a exigência é recalculada com o POWER nas datas e locais dos ensaios, para ficar na mesma régua do motor.

## Regras para o motor (decididas em 14/11)
O motor ainda não lê este catálogo. Ao implementar, siga estas regras, que vêm das decisões tomadas sobre os dados:

1. **Água:** calcular a demanda no local (Kc × ET0 do NASA POWER, a mesma conta de `scripts/etc_nasa_power.py`). As colunas `agua_ciclo_mm_*` são reserva: abaixo do mínimo elimina, entre mínimo e máximo marca "água no limite". Para perenes (`pastagem`) a coluna é anual: comparar com a chuva do ano.
2. **Graus-dia:** uma única função compartilhada entre o dataset e o motor, GD = soma de max(0, Tmed − Tb), **sem teto**. Filtro suave: abaixo de 90% do `graus_dia_ciclo_min` elimina; entre 90% e 100% marca "no limite térmico, validar localmente".
3. **Viés de temperatura do POWER:** não corrigir a temperatura no filtro de graus-dia. O viés do POWER muda de sinal conforme o local (1-2 °C mais frio em Santa Maria e Seropédica, ~2 °C mais quente em Rio Largo-AL), e as exigências das culturas de Tb alta (crotalária, milheto, mandioca) já foram calculadas com o próprio POWER nas datas dos ensaios. Nas demais, o efeito é pequeno e a margem de 10% do filtro suave cobre.
4. **Consórcio milho + braquiária (ILP):** usar o Kc do componente dominante em cada período (milho até a colheita, braquiária depois) e a massa de `regua.arranjos.consorcio_milho_safrinha` da pastagem.
5. **Valor forrageiro vazio ("não sei"):** ignorar o critério "Comida pros animais" para aquela cultura, redistribuir o peso entre os outros critérios e mostrar "sem dado". Não usar padrão regional.
6. **Palhada local:** para soja, milho, trigo, arroz e sorgo, escalar a massa de palhada pela produtividade da PAM do município (média de 3 a 5 anos), com a regressão da Tabela 11.2 do IPCC; para o feijão, a razão R_AG da Tabela 11.1a (IPCC 2019). Marcar a origem como cálculo. Nas demais culturas, usar o típico do bloco `regua`.
7. **Teste de sensibilidade:** para culturas de confiança `baixa`, rodar a comparação com o Kc no mínimo e no máximo plausíveis. Se a ordem das estratégias não mudar, o cartão pode dizer que a recomendação é robusta.
8. **Arroz irrigado:** só é candidato se o produtor tiver várzea ou irrigação, e não passa pelo filtro de chuva. Antes, o id `arroz_irrigado` precisa entrar em `agroia/base/culturas.json`.
9. **Mandioca:** o filtro de graus-dia serve só como teste de frio (eliminar abaixo do mínimo); não eliminar pelo máximo.
10. **Confiança baixa na tela:** mostrar a faixa em vez de um número e explicar em linguagem simples. Exemplo: "Ainda não existem medições no Brasil de quanta água esta cobertura usa. Usamos valores de outros países, por isso a estimativa pode errar. Confirme com seu agrônomo."

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
- `detalhe.depende_da_epoca`: `true` quando o mínimo e o máximo da faixa caem em classes diferentes. Na tela, mostre a classe e, no detalhe, a faixa com o aviso "depende da época".
