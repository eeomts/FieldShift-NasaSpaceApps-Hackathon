# A dor do agricultor e um caso de uso

## 1. Como os agricultores escolhem a rotação hoje

- **Experiência e tradição:** "meu pai plantava assim, eu planto assim". A rotação muda pouco em décadas.
- **Conversa com vizinhos, cooperativa e revenda:** o que funcionou para o vizinho vira referência, mesmo com solo e relevo diferentes.
- **Técnico agrícola ou agrônomo:** quando há acesso, mas eles atendem muitas propriedades e têm pouco tempo para cada uma.
- **Análise de solo pontual:** feita de tempos em tempos, mostra os nutrientes, mas não diz nada sobre clima ou água.
- **Previsão do tempo de curto prazo:** ajuda a decidir a semana, não a estratégia dos próximos anos.
- **Preço do momento:** muitas vezes a escolha é "o que está pagando melhor agora".

## 2. As dores

| Dor | Como aparece no dia a dia |
|---|---|
| **O clima mudou e a memória não acompanha** | O mês "que sempre chovia" agora falha. A experiência de 20 anos atrás já não vale tanto. |
| **Falta de dados sobre a própria terra** | Não sabe com números quanto o campo esquentou, quantas vezes faltou água ou quando o solo fica sem plantas. |
| **Risco alto de testar algo novo** | Trocar de cultura e errar pode custar uma safra inteira. Por isso, ninguém arrisca. |
| **Solo se degradando aos poucos** | Erosão, terra dura e menos matéria orgânica só aparecem quando já viraram problema. |
| **Água ficando escassa** | O poço baixa e a irrigação fica cara, mas não sabe que cultura gastaria menos. |
| **Dados existem, mas são inacessíveis** | A NASA tem 40 anos de dados de graça, mas em formatos técnicos que o agricultor não consegue usar. |
| **Informação espalhada** | Clima num lugar, solo em outro, mercado em outro. Ninguém junta tudo. |

## 3. Por que essa ferramenta seria boa

- **Transforma dados de satélite em frases simples** sobre a fazenda dele, como "seu campo fica sem plantas 5 meses por ano".
- **Mostra o histórico real do local**, não a memória ou o palpite do vizinho.
- **Compara opções antes de arriscar**: o agricultor vê prós, contras e incertezas no papel, não no prejuízo.
- **Respeita as prioridades dele**: economizar água, ganhar renda extra ou melhorar o solo.
- **Melhora a conversa com o técnico**: o agricultor chega com um relatório e o tempo da visita rende mais.
- **É honesta**: diz o que não sabe e deixa a decisão com quem conhece a terra.

---

## 4. Caso hipotético: Dona Marta, oeste da Bahia

### Quem ela é
- **Dona Marta, 52 anos**, 80 hectares em Luís Eduardo Magalhães (BA), no Cerrado.
- **Rotação atual:** soja de novembro a março. De abril a outubro, **o campo fica sem nada plantado**.
- **Solo:** arenoso, com pouca matéria orgânica.
- **Água:** não tem irrigação e depende só da chuva.
- **Equipamento:** trator, plantadeira e colheitadeira de grãos.
- **Mercado:** vende soja para a cooperativa. O vizinho cria gado e compraria forragem (capim e outras plantas para alimentar os animais).
- **Problemas recentes:** em 2 das últimas 4 safras faltou chuva em janeiro, bem quando a soja enche os grãos. Nas chuvas de novembro, a terra está "escorrendo" na parte mais inclinada do campo.

### O que ela informa na ferramenta
1. Marca a fazenda no mapa.
2. Preenche o calendário: soja de novembro a março e campo vazio no resto do ano.
3. Define as prioridades:
   - **Melhorar o solo:** alta
   - **Reduzir erosão:** alta
   - **Renda extra:** média
   - **Economizar água:** média
4. Informa as restrições: sem irrigação e só equipamento de grãos.

### O que a ferramenta mostra ("Raio-x do campo")

Os números abaixo são hipotéticos, só para ilustrar o formato.

- 🌱 **"Seu campo fica sem cobertura de abril a outubro na maioria dos anos."** O verde das plantas visto por satélite fica muito baixo nesses meses. *Fonte: MODIS, 2001–2025.*
- 🌡️ **"Janeiro ficou cerca de 1 °C mais quente desde 2005, e em 6 dos últimos 10 anos o solo esteve mais seco que o normal nesse mês."** *Fonte: NASA POWER e SMAP.*
- 🌧️ **"As chuvas fortes de novembro caem justamente quando a terra está sem proteção."** *Fonte: GPM.*
- ⛰️ **"A faixa leste do campo tem declive maior e mais risco de erosão."** *Fonte: SRTM.*
- 💧 **"Nos últimos 20 anos, o solo da sua região teve mais anos secos que antes."** *Fonte: GLDAS.*

### As 3 estratégias comparadas

| | A) Atual: soja e campo vazio | B) Soja e depois milheto como cobertura | C) Soja e depois milho com capim plantado junto |
|---|---|---|---|
| Água | Baixo uso | Baixo uso (milheto aguenta seca) | Médio, com risco se a chuva parar cedo |
| Solo | 🔴 Piora | 🟢 Melhora | 🟢 Melhora muito |
| Erosão | 🔴 Alta | 🟢 Baixa | 🟢 Baixa |
| Pragas | Ciclo da soja contínuo | Quebra parcial | Quebra parcial |
| Renda | Só a soja | Soja + pouco custo | Soja + milho + capim vendido ao vizinho |
| Confiança | Alta | Média | Média-baixa |

### Exemplo de explicação: estratégia B
- **Por que foi sugerida:** o campo fica 7 meses sem plantas e a chuva forte chega com a terra exposta. Melhorar o solo e reduzir erosão são as prioridades dela.
- **Evidência:** verde das plantas visto por satélite (MODIS), chuva (GPM e NASA POWER) e inclinação do terreno (SRTM).
- **Benefícios:** a terra fica coberta, as raízes do milheto ajudam a água a entrar no solo e sobra palha para plantar a soja seguinte sem arar a terra (plantio direto).
- **O que não sabemos:** se ela consegue comprar semente de milheto na região e como estão as pragas locais.
- **Converse com seu técnico sobre:** a data limite para plantar o milheto antes de a chuva acabar e como eliminar o milheto antes de plantar a soja.

### O resultado
Dona Marta leva o relatório para o técnico da cooperativa. Juntos, decidem **testar a estratégia B em 20 dos 80 hectares**, começando pela faixa inclinada. Assim ela arrisca pouco e compara o resultado na safra seguinte.

A estratégia C fica como "talvez no futuro", depois que ela confirmar com o vizinho que ele compra o capim.

> A ferramenta não decidiu nada por ela. Mostrou o que estava acontecendo no campo, deu opções com prós e contras e deixou claro o que precisava ser conferido. **A decisão foi da Dona Marta e do técnico.**
