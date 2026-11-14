# Banco de dados — PostgreSQL + PostGIS

## Por que Postgres

- **Relacional:** base de culturas, sinônimos e equipamentos são dados bem estruturados.
- **JSONB:** guarda respostas do questionário, o que a IA extraiu e as respostas brutas das APIs externas, sem uma tabela para cada formato.
- **PostGIS:** consultas geográficas (ver abaixo).

**O Postgres guarda, não calcula.** As regras e a pontuação ficam no código da aplicação, onde dá para testar e explicar.

## O que é o PostGIS

Uma **extensão do PostgreSQL** (não é outro banco) que ensina o banco a trabalhar com mapas e localização. Sem ela, um ponto é só dois números soltos; com ela, o banco entende geografia.

| Situação | Sem PostGIS | Com PostGIS |
|---|---|---|
| Guardar o campo | Colunas `lat` e `lon` | Coluna `geom` (ponto, ou polígono se o produtor desenhar o contorno) |
| Cache por célula (reaproveitar dado de um vizinho) | Conta da grade à mão no código | "Já tenho dado desta célula?" numa consulta |
| Tamanho do campo (com contorno) | Fórmula manual | `ST_Area(geom)` |
| Campos ou cenários da região (técnico, cooperativa) | Difícil | Consulta por distância ou área |
| Consultar mapas baixados (ex.: GAEZ) | Ler o arquivo no código | Carregar o mapa no banco e perguntar o valor no ponto |

Exemplo: existe dado do NASA POWER guardado a menos de 25 km deste campo?

```sql
SELECT payload
FROM cache_externo
WHERE servico = 'nasa_power'
  AND ST_DWithin(celula::geography, ST_MakePoint(-48.28, -18.92)::geography, 25000);
```

Com um ponto por campo daria para viver sem ele, mas ativar a extensão não custa nada e deixa o caminho pronto para contorno de campo, mapas e consultas por região.

## Modelo de dados (linhas gerais)

```
produtor ─< campo (geom POINT, irrigacao, terreno)
              ├─< resposta (pergunta_id, valor, texto_original, respondido_em)
              ├─< calendario_atual (cultura_id, inicio_mes, fim_mes, grupo_consorcio)
              ├─< evidencia_solo (atributo, valor, fonte, peso)      ← retrato do solo
              ├─< indicador (nome, valor, periodo, fonte_dataset)    ← dados externos
              └─< analise ─< estrategia ─< estrategia_criterio (criterio, nota, evidencias JSONB)
                     └── cenario (tipo, ajustes JSONB)               ← "e se?"

cultura (ciclo, Kc, geada, calor, água, fixa_N, família...)
  ├─< cultura_sinonimo (nome, idioma)        ← casamento do texto livre
  └─< cultura_equipamento >─ equipamento

cache_externo (servico, celula geom, params_hash, payload JSONB, obtido_em)
job_coleta (servico, campo_id, status, tentativas, erro)   ← fila da integração lenta
```
