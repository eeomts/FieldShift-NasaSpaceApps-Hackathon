> Descartado em 15/11/2026 (ver D-009 em DECISOES.md): arquivo histórico.

# earthaccess no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar a biblioteca `earthaccess`, como ela entra na ferramenta e o que muda para o produtor, com um caso hipotético que mostra a equipe automatizando os dados de uma região do Sudeste.

## O que é

O `earthaccess` é uma biblioteca Python de código aberto, mantida pela comunidade com apoio da NASA e do NSIDC. Ela faz, dentro do código, o que o Earthdata Search faz no navegador: **entra com o Earthdata Login, busca no catálogo da NASA e baixa ou abre os arquivos**.

Em poucas linhas, troca um processo manual de dezenas de cliques por um script que pode ser repetido para qualquer região ou ano.

## Por que usar

**1. Repetir para o Brasil inteiro.** O escopo é nacional (D-008). Baixar à mão o GLDAS, o IMERG e o SMAP L4 para cada região não é viável em 48 horas. Com o `earthaccess`, a mesma função roda para o país inteiro ou para cada região de demonstração.

**2. Login resolvido.** A biblioteca cuida da autenticação no Earthdata Login, inclusive dos redirecionamentos que costumam travar downloads feitos com `requests` ou `wget`.

**3. Abre sem baixar.** Para dados na nuvem da NASA, a função `open` entrega os arquivos como objetos que o `xarray` lê direto. A equipe pode ler só o recorte necessário.

**4. Mesmo vocabulário do catálogo.** Os parâmetros (`short_name`, `version`, `bounding_box`, `temporal`) são os mesmos campos que aparecem no Earthdata Search. O inventário montado lá vira código sem tradução.

## Como entra no projeto

### Acesso

- **Instalação:** `pip install earthaccess`, num ambiente Python recente.
- **Credenciais:** as mesmas do Earthdata Login, lidas de um arquivo `.netrc`, de variáveis de ambiente ou digitadas na hora. Nunca colocar usuário e senha no código nem no repositório.

| Função / parâmetro | O que é | Uso no projeto |
| --- | --- | --- |
| `earthaccess.login()` | Autentica no Earthdata Login | Primeira linha de todo script |
| `search_datasets(keyword=..., cloud_hosted=True)` | Busca coleções | Confirmar o `short_name` e a versão |
| `search_data(short_name=..., version=...)` | Busca arquivos de uma coleção | Listar os arquivos do produto certo |
| `bounding_box=(oeste, sul, leste, norte)` | Recorte espacial da busca | Brasil (cerca de -74, -34, -34, 6) ou uma região |
| `temporal=("2001-01", "2025-12")` | Período da busca | Série longa para climatologia |
| `count=...` | Limite de resultados | Testar com poucos arquivos antes do lote |
| `download(resultados, pasta)` | Baixa os arquivos | Produtos leves, como o GLDAS mensal |
| `open(resultados)` | Abre na nuvem, sem baixar | Ler só o recorte com `xarray` |

Exemplo mínimo:

```python
import earthaccess
import xarray as xr

earthaccess.login()  # lê .netrc ou variáveis de ambiente

resultados = earthaccess.search_data(
    short_name="GLDAS_NOAH025_M",
    bounding_box=(-50.0, -25.0, -47.0, -22.5),  # sudoeste paulista
    temporal=("2001-01", "2025-12"),
)
arquivos = earthaccess.download(resultados, "dados/gldas")
ds = xr.open_mfdataset(arquivos)
```

> Confirmar nas páginas oficiais a versão atual da biblioteca e a versão mínima do Python, os nomes exatos das opções de login (`strategy`), os nomes das variáveis de ambiente e o comportamento de `open` para dados fora da nuvem. O `bounding_box` busca arquivos que **tocam** a caixa; o recorte fino continua sendo feito no `xarray`.

### O que produz para o projeto

- **Scripts de coleta** para cada dataset do inventário: GLDAS, GPM IMERG, SMAP L4, MODIS.
- **Arquivos brutos organizados** por produto e período, que alimentam o pré-cálculo dos indicadores na grade comum.
- **Registro da origem:** cada arquivo baixado guarda o nome do granule e a versão, que vão para a citação de fonte no cartão.

### Como ajuda a medir a confiança

O `earthaccess` não avalia a qualidade do dado. Mas, ao rodar por script, a equipe pode **contar quantos arquivos vieram** por mês e comparar com o esperado. Mês com arquivo faltando entra como lacuna e reduz a confiança do indicador. Como o processo é repetível, qualquer pessoa da equipe consegue refazer o cálculo e chegar ao mesmo número.

### Onde fica na arquitetura

A stack ainda não está decidida (Q-09). O `earthaccess` funciona em qualquer uma: num script de pré-cálculo que roda antes da demo, num notebook ou num backend. A recomendação é usá-lo **no pré-cálculo**, não a cada clique do produtor, porque buscas e downloads podem demorar.

## Onde o produtor vê isso

O produtor **não vê** o `earthaccess`. É código de bastidor.

O efeito indireto:

- **Mais regiões cobertas.** Com o processo automatizado, a ferramenta pode mostrar indicadores para qualquer ponto do Brasil, não só para as regiões baixadas à mão.
- **Dados mais recentes.** Rodar o script de novo atualiza as séries sem retrabalho.
- **Fontes rastreáveis.** As citações do cartão vêm do registro que o script gera.

## Caso hipotético: earthaccess no fluxo da equipe

> Caso inventado, com números ilustrativos, para mostrar como a ferramenta ajuda a montar os dados de uma região.

### A região

A equipe quer uma quarta região de demonstração, no **sudoeste paulista, perto de Itapeva (SP)**, no Sudeste. O produtor fictício é o Sr. Rogério.

- **Rotação atual:** soja no verão (outubro a fevereiro), milho safrinha ou feijão (fevereiro a junho), trigo em parte da área no inverno.
- **Irrigação:** não tem.
- **Prioridades:** renda alta; solo e água médias.
- **Mercado:** soja, milho, feijão e trigo.

### O que a equipe faz com o earthaccess

1. **Reaproveita o script** já usado no Cerrado e no Semiárido; só troca o `bounding_box`.
2. **Busca com `count=5`** para testar e confere os nomes das variáveis antes do lote completo.
3. **Baixa o GLDAS mensal** (2001–2025) e o **IMERG diário**, e abre o **SMAP L4** pela nuvem com `open`, lendo só a região.
4. **Conta os arquivos por mês.** O IMERG veio completo; o SMAP L4 tem alguns dias faltando em 2019.
5. **Grava o registro** de granules e versões ao lado dos indicadores.

Tudo isso leva menos de uma hora, contra um dia de trabalho manual.

### O que os dados mostram (hipotético)

| Dataset | O que encontra |
| --- | --- |
| GPM IMERG | Chuva bem distribuída de outubro a março; inverno com chuva moderada, sem seca longa. |
| GLDAS | A zona das raízes raramente cai abaixo do percentil 20; quando cai, é em agosto. |
| SMAP L4 | Concorda com o GLDAS, com uma lacuna curta em 2019. |
| NASA POWER | Mínimas abaixo de 3 °C em alguns dias de junho e julho na maioria dos anos. |
| HLS (via AppEEARS) | Pouco solo descoberto: o talhão fica verde quase o ano todo, com um intervalo curto em setembro. |
| ZARC | Janelas de plantio largas para soja e milho; trigo com janela definida no outono. |

### Onde o earthaccess fez diferença

**Mesma regra, outra região, sem retrabalho.** O pré-cálculo que identifica "solo descoberto longo" e "déficit na safrinha" rodou aqui com o mesmo código. Nenhuma das duas regras foi ativada. Isso é um resultado: a ferramenta não força sugestões de cobertura onde o solo já fica coberto.

**A lacuna foi registrada, não escondida.** Os dias faltando no SMAP L4 em 2019 aparecem como lacuna no registro. Como o GLDAS cobre esse período, o indicador de água mantém confiança **alta**, com a observação de que só uma fonte cobriu aqueles dias.

**O que pesa aqui é outra coisa.** Com pouca falta de água e pouco solo descoberto, as diferenças entre estratégias ficam em renda, nitrogênio e risco de geada no inverno. O comparador do Sr. Rogério destaca isso, e a escolha entre trigo, aveia ou outras opções de inverno fica com ele e com o agrônomo.

## Conclusão

O `earthaccess` é o que torna o escopo nacional possível no prazo do hackathon. Ele transforma o inventário feito no Earthdata Search em scripts repetíveis, cuida do login e permite ler só o necessário dos dados na nuvem. O produtor não o vê, mas é por causa dele que a ferramenta consegue mostrar a mesma análise em regiões tão diferentes quanto o Cerrado, o Semiárido e o Sudeste.

## Limitações

- **Busca por caixa, não por forma:** o `bounding_box` traz arquivos que tocam a área; o recorte exato é feito depois.
- **Volume:** produtos diários ou de 30 m para o Brasil inteiro somam muitos arquivos; testar com `count` antes.
- **Leitura na nuvem:** é mais rápida dentro da região da nuvem da NASA; de fora, pode ser lenta e às vezes vale mais baixar.
- **Biblioteca em evolução:** nomes de funções e opções podem mudar entre versões; fixar a versão no ambiente do projeto.
- **Credenciais:** um `.netrc` ou variável de ambiente esquecido no repositório expõe a conta.
- **Tratamento:** usar o `earthaccess` no pré-cálculo, fixar a versão, testar com poucos arquivos e contar arquivos por mês.
