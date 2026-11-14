# Integração de dados externos

> A parte do sistema que **trabalha sozinha, sem o produtor ver**: pega a coordenada do campo e busca dados de clima, solo, relevo e vegetação em serviços externos. O produtor só vê o resultado ("seu campo teve 3 geadas em julho de 2021"), nunca a busca.

## Como funciona

1. O produtor marca o campo no mapa (pergunta 5).
2. O sistema dispara as buscas com essa coordenada.
3. O produtor continua o questionário enquanto os dados chegam.
4. Os dados ficam guardados no banco e o motor cruza tudo com as respostas.

## Duas velocidades

| Velocidade | Fontes | Tempo | Como chamar |
|---|---|---|---|
| **Rápida** | NASA POWER, SoilGrids, SRTM | Segundos | Na hora |
| **Lenta** | NDVI (MODIS), SMAP, ET via AppEEARS; chuva IMERG | Minutos (pedido assíncrono) | Em segundo plano, por uma fila |

Na prática, o dashboard aparece em segundos com clima, solo e relevo, e os cartões de vegetação e umidade surgem depois, com o aviso "novo dado chegou".

## Componentes

- **Um conector por fonte**, todos com a mesma interface: `buscar(ponto, período) → dados + metadados (fonte, resolução, data)`.
- **Cache por célula da grade:** campos vizinhos reaproveitam a mesma consulta (o NASA POWER tem grade de 0,5°).
- **Fila no próprio Postgres:** uma tabela de jobs e um worker. Para o hackathon é mais simples do que Redis ou RabbitMQ.
- **Tolerante a falha:** se uma fonte cair, o resto segue e o cartão afetado mostra "dado indisponível".

## Serviços testados (14/11/2026)

Testes feitos em pontos de 5 continentes (Quênia, Índia, Brasil, EUA, França).

| Serviço | Para quê | Login | Resultado |
|---|---|---|---|
| **NASA POWER** | Clima mensal 2001–2024: temperatura, chuva, radiação, vento, umidade, umidade do solo | Não | ✅ 5 de 5 pontos, ~1,5 s, série completa |
| **SoilGrids** (ISRIC) | Argila, areia, carbono, pH | Não | ⚠️ OK em área agrícola; **vazio em área urbana** (máscara deles). Uma chamada levou 17 s |
| **OpenTopoData SRTM 30 m** | Altitude e declividade | Não | ✅ 5 de 5, ~1 s |
| **NASA GIBS** | Camadas visuais para mapa | Não | ✅ Só imagem, não valores |
| **Nominatim** (OSM) | Busca por endereço | Não | ✅ |
| **AppEEARS** | NDVI (MOD13Q1), ET (MOD16A2), SMAP L3/L4, ECOSTRESS, HLS, NASADEM | Earthdata (token de 48 h) | ✅ Produtos no catálogo. ⚠️ Assíncrono; tempo de resposta não documentado |
| **GPM IMERG** (GES DISC) | Chuva 10 km, extremos | Earthdata | ✅ Catálogo desde 1998. ⚠️ A versão Final vai até 30/09/2025 (tem atraso); sem endpoint simples por ponto encontrado |
| **FAO GAEZ v5** | Aptidão das culturas | — | ⚠️ Sem API encontrada; só portal e download de mapas |

## Pendências

- Confirmar o limite de uso do SoilGrids. Se for baixo, o cache por célula é obrigatório.
- Medir o tempo real de uma consulta por ponto no AppEEARS (precisa de conta Earthdata).
- Definir o acesso ao GAEZ v5, ao GRACE e ao ESA WorldCover (download único e consulta local).
- Revisar item por item a lista oficial de recursos do desafio.

## Observação de produto

Em fazenda pequena, o pixel de 250 m do MODIS mistura o campo com os vizinhos. Os **meses sem cobertura vêm do calendário que o produtor informa**; o NDVI entra como confirmação regional.
