# Harmony e OPeNDAP no Field Shift Brasil

Complemento à *Documentação do Projeto* e ao *Banco de Dados NASA*. Explica por que usar o Harmony e o OPeNDAP, como eles entram na ferramenta e o que mudam para o produtor, com um caso hipotético que mostra a equipe montando o panorama nacional e conferindo uma região do oeste baiano.

## O que é

Os dois resolvem o mesmo problema: **pedir ao servidor só a parte do arquivo que interessa**, em vez de baixar o arquivo inteiro.

- **Harmony** é o serviço de transformação de dados da NASA no Earthdata Cloud. A equipe envia um pedido com coleção, área, período e variáveis, e o Harmony recorta, às vezes reprojeta ou converte o formato, e devolve os arquivos prontos. É ele que trabalha por trás da opção "personalizar" do Earthdata Search.
- **OPeNDAP** é um protocolo antigo e muito usado para acessar dados científicos pela internet. Um endereço OPeNDAP aponta para um arquivo no servidor, e a equipe pede só certas variáveis e faixas de índices. Bibliotecas como o `xarray` leem esse endereço como se fosse um arquivo local.

Os dois usam o Earthdata Login.

## Por que usar

**1. O Brasil inteiro sem baixar o planeta.** Produtos como o SMAP L4 e o MERRA-2 são globais. O Brasil é uma parte pequena de cada arquivo. Recortar no servidor reduz muito o volume e o tempo de download.

**2. Só as variáveis necessárias.** Um arquivo do GLDAS ou do MERRA-2 traz dezenas de variáveis. O projeto usa poucas: umidade na zona das raízes, evapotranspiração, escoamento, temperatura. O resto fica no servidor.

**3. Menos código de recorte.** Com o Harmony, o arquivo já chega na área e, quando o serviço permite, no formato desejado. Isso simplifica o pré-cálculo na grade comum (D-008).

**4. Leitura direta no código.** Com o OPeNDAP, um `xarray.open_dataset` no endereço certo basta para ler uma série, sem gerenciar arquivos baixados.

## Como entra no projeto

### Acesso

- **Harmony:** API em `harmony.earthdata.nasa.gov`, por URL ou pela biblioteca Python `harmony-py`. Autenticação por `.netrc` ou por token do Earthdata Login.
- **OPeNDAP:** servidores Hyrax dos centros de dados e do Earthdata Cloud. O endereço OPeNDAP de cada arquivo aparece nos links do Earthdata Search e nos resultados do `earthaccess`.

| Parâmetro / recurso | O que é | Uso no projeto |
| --- | --- | --- |
| Harmony `subset=lat(-34:6)` e `subset=lon(-74:-34)` | Recorte espacial | Retângulo do Brasil ou de uma região |
| Harmony `subset=time(...)` | Recorte no tempo | Só os anos da climatologia |
| Harmony `variable=...` | Escolha de variáveis | Só as variáveis usadas nos indicadores |
| Harmony `format=...` | Formato de saída | NetCDF ou GeoTIFF, quando o serviço converte |
| Harmony `/jobs` | Acompanhar pedidos | Ver o andamento de pedidos grandes |
| `harmony-py` (`Client`, `Request`, `BBox`) | Cliente Python | Montar e enviar pedidos no script de pré-cálculo |
| OPeNDAP com restrição | Variáveis e faixas de índices na URL | Ler uma variável numa janela, direto no `xarray` |

> Confirmar nas páginas oficiais quais coleções do inventário aceitam cada tipo de recorte e conversão no Harmony (nem todas aceitam tudo), a sintaxe atual dos parâmetros, o limite de arquivos antes de um pedido pausar para conferência, e os endereços OPeNDAP de cada centro de dados. Em 2026 o GES DISC moveu o OPeNDAP de várias coleções para o Earthdata Cloud, então endereços antigos podem não funcionar. Os nomes das variáveis dentro dos arquivos podem ter sufixos (por exemplo, `_inst` no GLDAS).

### O que produz para o projeto

- **Arquivos recortados para o Brasil**, com poucas variáveis, prontos para reamostrar na grade comum.
- **Panorama nacional pré-calculado:** climatologia, anomalias e frequência de déficit por célula e mês, a partir de GLDAS, SMAP L4 e MERRA-2.
- **Leituras rápidas de conferência** via OPeNDAP, para checar uma célula ou um mês sem baixar nada.

### Como ajuda a medir a confiança

O Harmony e o OPeNDAP não mudam o dado, só o recortam. A confiança depende do produto. Mas há um cuidado: um recorte mal feito (eixo de latitude invertido, longitude de 0 a 360 em vez de -180 a 180) pode deslocar o Brasil inteiro. Por isso, todo recorte é conferido com um ponto conhecido, comparando o valor com o Giovanni ou com o AppEEARS.

## Onde o produtor vê isso

O produtor **não vê** o Harmony nem o OPeNDAP. São peças do pré-cálculo.

O efeito indireto:

- **Panorama nacional disponível.** Qualquer ponto do Brasil tem indicadores regionais de água e clima, porque o recorte tornou o processamento nacional viável.
- **Respostas rápidas.** Como os indicadores estão pré-calculados, a ferramenta responde na hora, sem esperar downloads.
- **Mesmas fontes, mesmo rigor.** A origem e a versão de cada produto continuam registradas e citadas no cartão.

## Caso hipotético: Harmony e OPeNDAP no fluxo da equipe

> Caso inventado, com números ilustrativos, para mostrar como as ferramentas ajudam a montar o panorama nacional e uma região.

### A tarefa

A equipe precisa do **panorama nacional de água no solo**: para cada célula da grade comum, a frequência com que a zona das raízes fica abaixo do normal em cada mês. Depois, quer conferir uma região de demonstração no **oeste baiano, perto de Luís Eduardo Magalhães (BA)**, no MATOPIBA.

O produtor fictício da região é o Sr. Neto.

- **Rotação atual:** soja (novembro a março), milheto ou pousio na seca.
- **Irrigação:** não tem no talhão analisado.
- **Prioridades:** água e solo altas; renda média.
- **Mercado:** soja, milho, algodão e milheto.

### O que a equipe faz

1. **Harmony para o SMAP L4.** Um pedido com o retângulo do Brasil, a variável de umidade na zona das raízes e o período 2015–2025. Como são muitos arquivos, o pedido pausa para conferência; a equipe olha a prévia e manda continuar.
2. **Harmony ou OPeNDAP para o GLDAS mensal.** Só `RootMoist`, `Evap` e `Qs`, de 2001 a 2025, recortados no Brasil.
3. **Reamostragem** dos dois produtos para a grade comum e cálculo da climatologia e da frequência de déficit.
4. **Conferência por OPeNDAP.** Para a célula de Luís Eduardo Magalhães, a equipe lê direto do servidor a série do GLDAS de 2020 e compara com o valor que o script calculou. Os números batem.
5. **Conferência com o Giovanni.** A média da área no Giovanni bate com a da grade, o que mostra que o recorte não deslocou o mapa.

### O que aparece (hipotético)

| Fonte | O que mostra para a região do Sr. Neto |
| --- | --- |
| GLDAS (via Harmony / OPeNDAP) | Zona das raízes abaixo do percentil 20 em junho em 6 de cada 10 anos. |
| SMAP L4 (via Harmony) | Concorda com o GLDAS nos anos em comum (2015–2025). |
| MERRA-2 (via Harmony) | Ar seco e quente de agosto a outubro. |
| GPM IMERG | Seca de maio a outubro. |
| HLS (via AppEEARS) | Solo descoberto de julho a outubro na parte em pousio. |
| FIRMS | Focos frequentes no entorno entre agosto e outubro. |

### Onde o Harmony e o OPeNDAP fizeram diferença

**O panorama nacional coube no prazo.** Sem o recorte no servidor, o SMAP L4 global de 10 anos seria pesado demais para o hackathon. Com o Harmony, só o Brasil e uma variável vieram para a equipe.

**Um erro de recorte foi pego cedo.** No primeiro teste, um script próprio de recorte usava longitude de 0 a 360 e jogou o Brasil para o meio do oceano. A conferência por OPeNDAP com um ponto conhecido mostrou o erro antes que ele chegasse ao mapa.

**A região confirma o padrão do Cerrado.** Déficit na seca, solo descoberto e fogo no entorno: as mesmas regras do caso do FIRMS são ativadas aqui. O comparador do Sr. Neto mostra estratégias com cobertura do solo e cuidado com a palha seca, e deixa a escolha com ele e com o agrônomo.

## Conclusão

O Harmony e o OPeNDAP são o que deixa o pré-cálculo nacional leve. Eles recortam no servidor, trazem só as variáveis usadas e permitem conferir um ponto sem baixar nada. O produtor não os vê, mas é por causa deles que qualquer lugar do Brasil tem um panorama de água e clima pronto, com a mesma origem e o mesmo rigor das regiões de demonstração.

## Limitações

- **Nem toda coleção aceita todo serviço:** algumas só permitem recorte espacial, outras nenhum; conferir coleção por coleção.
- **Pedidos grandes demoram e podem pausar:** precisam ser acompanhados e liberados.
- **Endereços mudam:** a migração para o Earthdata Cloud trocou caminhos OPeNDAP de várias coleções.
- **Erros silenciosos de recorte:** eixos invertidos ou longitude de 0 a 360 deslocam o mapa sem dar erro.
- **OPeNDAP lento em séries longas:** ler muitos arquivos pela rede pode ser mais lento que baixar uma vez.
- **Tratamento:** preferir o Harmony para recortes grandes e o OPeNDAP para leituras pontuais, conferir cada recorte com um ponto conhecido e com o Giovanni, e registrar coleção, versão e parâmetros de cada pedido.
