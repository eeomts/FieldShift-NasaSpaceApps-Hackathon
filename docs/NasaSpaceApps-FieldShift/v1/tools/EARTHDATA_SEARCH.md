# Earthdata Search no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o Earthdata Search e o Earthdata Login, como eles entram na ferramenta e o que mudam para o produtor, com um caso hipotético que mostra a equipe montando os dados de uma região do Semiárido.

## O que é

O **Earthdata Search** é o buscador oficial dos dados de Ciências da Terra da NASA. Pelo navegador, ele procura no catálogo central da NASA (o CMR, Common Metadata Repository) e mostra, para cada coleção, o período coberto, a resolução, o centro de dados que a distribui e os arquivos (chamados de *granules*) que caem na área e nas datas escolhidas.

O **Earthdata Login** (EDL) é a conta gratuita da NASA que libera o download. É o mesmo usuário e senha para quase tudo neste projeto: Earthdata Search, AppEEARS e `earthaccess`.

Em resumo: o Earthdata Search é o **mapa do catálogo**, e o Earthdata Login é a **chave** das portas.

## Por que usar

**1. Um lugar só para achar quase todos os datasets.** SMAP L4, GPM IMERG, GLDAS, HLS e MODIS estão no mesmo catálogo. A equipe não precisa visitar o site de cada centro de dados (GES DISC, LP DAAC, NSIDC) para descobrir o que existe.

**2. Confere a cobertura antes de escrever código.** Em poucos cliques dá para ver se um produto cobre o Brasil, desde quando existe e se há falhas. Isso evita descobrir no meio do hackathon que um dataset começa em 2015 ou que não tem dados para um mês.

**3. Mostra o nome exato do produto.** O `short_name` e a versão que aparecem no Earthdata Search são os mesmos usados no `earthaccess` e no AppEEARS. Copiar daqui evita erro de digitação e versão antiga.

**4. Recorte já no pedido.** Para várias coleções, dá para personalizar o download (subconjunto por área, variável e formato). Para o Brasil inteiro isso faz muita diferença no volume.

## Como entra no projeto

### Acesso

- **Endereço:** `search.earthdata.nasa.gov`, no navegador.
- **Conta:** criar o Earthdata Login em `urs.earthdata.nasa.gov`. É gratuita e não pede vínculo com instituição.
- **Autorizações:** alguns centros de dados pedem que o usuário aceite o uso do aplicativo deles na primeira vez (por exemplo, o arquivo do GES DISC). Se um download falhar com erro de permissão, esse costuma ser o motivo.
- **Token:** o perfil do Earthdata Login permite gerar um token para scripts, como alternativa ao usuário e senha.

| Filtro / opção | O que é | Uso no projeto |
| --- | --- | --- |
| Busca por palavra-chave | Nome ou sigla do produto | Achar `GPM_3IMERGDF`, `GLDAS_NOAH025_M`, `SPL4SMGP`, `HLSL30`, `MOD13Q1` |
| Filtro espacial | Retângulo, polígono, ponto ou arquivo enviado | Desenhar o Brasil, um bioma ou uma região de demonstração |
| Filtro temporal | Intervalo de datas, com opção de recorrência anual | Pegar só a estação seca ou só a safra, vários anos |
| Filtros de coleção | Disponível na nuvem, personalizável, nível de processamento | Preferir produtos que aceitam recorte |
| Personalizar (Customize) | Subconjunto por área, variável, formato | Reduzir o volume antes de baixar |
| Download | Lista de links, script ou aplicativo de download | Baixar em lote ou passar a lista para o código |

> Confirmar nas páginas oficiais os nomes e versões atuais de cada produto, quais coleções aceitam personalização, as opções de download disponíveis e a validade do token do Earthdata Login. O GES DISC está migrando serviços para o Earthdata Cloud ao longo de 2026, então alguns caminhos de download podem mudar.

### O que produz para o projeto

- **Inventário de dados:** uma tabela com o `short_name`, a versão, o período, a resolução e o centro de dados de cada dataset usado. Esse inventário alimenta os scripts com `earthaccess` e a seção de fontes da apresentação.
- **Teste de cobertura por região:** quantos arquivos existem para cada região de demonstração e período, antes de automatizar.
- **Downloads pontuais:** para produtos leves, como o GLDAS mensal, um download manual já resolve.

### Como ajuda a medir a confiança

O Earthdata Search não calcula nada. Mas ele mostra **lacunas no tempo** (meses sem arquivo) e a **versão** de cada produto. A ferramenta registra essas informações junto com cada indicador. Um indicador calculado com meses faltando, ou com uma versão antiga, recebe confiança menor.

## Onde o produtor vê isso

O produtor **não vê** o Earthdata Search nem precisa de conta no Earthdata Login. É uma ferramenta de bastidor da equipe.

O efeito chega de forma indireta:

- **Fontes citadas no cartão.** Cada evidência traz o nome do dataset e o período usado, tirados do inventário montado aqui.
- **Avisos de lacuna.** Quando faltam meses num dado, o cartão mostra "série incompleta" e a confiança cai.
- **Glossário.** Explica, em uma linha, que os dados vêm do catálogo público da NASA e podem ser conferidos por qualquer pessoa.

## Caso hipotético: Earthdata Search no fluxo da equipe

> Caso inventado, com números ilustrativos, para mostrar como a ferramenta ajuda a montar os dados de uma região.

### A região

A equipe escolhe o entorno de **Serra Talhada (PE)**, no sertão do Pajeú, como região de demonstração do Semiárido. A produtora fictícia é a Dona Lúcia, agricultora familiar.

- **Rotação atual:** milho e feijão em consórcio, no sequeiro, plantados com as primeiras chuvas (janeiro a março); pousio no resto do ano.
- **Irrigação:** não tem.
- **Prioridades:** água e renda altas; solo média.
- **Mercado:** feira local e alimento para a família e para as cabras.

### O que a equipe faz no Earthdata Search

1. **Desenha um retângulo** de cerca de 1° × 1° em volta do município e busca cada dataset do inventário.
2. **Confere períodos.** O GPM IMERG diário (`GPM_3IMERGDF`) e o GLDAS mensal cobrem 2001–2025 sem falhas. O SMAP L4 (`SPL4SMGP`) só começa em 2015. O HLS tem muitas imagens limpas, porque a região é pouco nublada fora da estação chuvosa.
3. **Usa o filtro temporal recorrente** para pegar só janeiro a junho de cada ano no IMERG, onde moram os veranicos.
4. **Personaliza o GLDAS** para baixar só a umidade na zona das raízes e a evapotranspiração, recortadas na região.
5. **Copia os nomes exatos** para o script com `earthaccess`, que vai repetir o processo nas outras regiões.

### O que cada dataset mostra (montado a partir da busca)

| Dataset | O que encontra (hipotético) |
| --- | --- |
| GPM IMERG | Chuva concentrada de janeiro a abril, com veranicos de 10 dias ou mais em 7 de cada 10 anos. |
| GLDAS | A zona das raízes cai abaixo do percentil 20 em abril em metade dos anos. |
| SMAP L4 | Confirma o solo seco em abril e maio de 2015 em diante. |
| NASA POWER | Evapotranspiração de referência alta o ano todo; não há risco de geada. |
| HLS | O roçado fica descoberto de junho a dezembro, cerca de 7 meses. |
| ZARC | Indica janela de menor risco para o feijão-caupi e para o sorgo no município. |

### Comparação das estratégias

| Critério | A: atual (milho + feijão) | B: sorgo + feijão-caupi | C: milho de ciclo curto + caupi, plantio após recarga do solo |
| --- | --- | --- | --- |
| Água | ●●○○○ | ●●●●○ | ●●●○○ |
| Solo | ●●○○○ | ●●●○○ | ●●○○○ |
| Renda | ●●●○○ | ●●●○○ | ●●●○○ |
| Forragem | ●●○○○ | ●●●●○ | ●●○○○ |

Com os pesos da Dona Lúcia (água e renda altas), a **estratégia B** fica em primeiro: empata em renda e tem a melhor nota em água. A C fica em segundo. A ferramenta mostra as opções e as evidências; a escolha continua sendo da produtora, com o apoio da extensão rural.

### Onde o Earthdata Search fez diferença

**Evitou uma conclusão frágil.** A equipe pretendia usar só o SMAP L4. A busca mostrou que ele começa em 2015, então a frequência de veranico em 10 anos ficaria com só 10 safras. O GLDAS, desde 2000, entrou como base, e o SMAP L4 como conferência: confiança **alta** quando os dois concordam.

**Achou o recorte certo.** Baixar o IMERG diário do Brasil inteiro para uma região de 1° seria desperdício. O filtro espacial e o recorrente reduziram o pedido a uma fração do volume.

## Conclusão

O Earthdata Search é o primeiro passo de qualquer dado da NASA no projeto. Ele não gera indicador, mas garante que a equipe usa o produto certo, na versão certa, com o período certo. O inventário feito aqui alimenta os scripts e as citações de fonte, e as lacunas que ele revela entram no nível de confiança.

## Limitações

- **Interface manual:** bom para explorar e conferir, ruim para repetir em 27 estados. A automação vem com `earthaccess`.
- **Nem toda coleção aceita recorte:** algumas só oferecem o arquivo inteiro.
- **Volume:** para o Brasil inteiro, alguns produtos somam milhares de arquivos; o pedido precisa ser recortado.
- **Mudanças de endereço:** a migração de serviços para o Earthdata Cloud pode mudar links e caminhos.
- **Autorizações por centro de dados:** o primeiro download de cada centro pode falhar até a autorização ser aceita no perfil.
- **Tratamento:** usar o Earthdata Search para descobrir e conferir, registrar `short_name`, versão e período no inventário, e automatizar o download com `earthaccess`.
