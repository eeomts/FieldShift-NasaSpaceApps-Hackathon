---
name: debug-agroai
description: Checklist de depuracao do AgroAI com as armadilhas que ja aconteceram no projeto (porta 5432 ocupada por Postgres local, migration nao aplicada, .env vazio, CORS, IP fora do firewall da VPS, Gemini fora do ar, SoilGrids vazio em area urbana, -999 do NASA POWER, tipos do front fora de sincronia com a API). Use quando a API nao sobe, uma tela quebra, nao salva, da 500 ou "a alteracao nao funcionou".
---

# debug-agroai

Rode o mais barato primeiro: `curl localhost:8000/saude`, os testes (`pytest`) e a checagem de tipos do front (`npx tsc -p tsconfig.json --noEmit`).

## Checklist, do mais comum ao menos

1. **`column ... does not exist` / erro 500 ao ler a fazenda.** Migration não aplicada no banco que a API está usando (ex.: a `0002` criou `fazenda.papel`). Ver `SELECT version_num FROM alembic_version` e comparar com `migrations/versions/`. Na VPS, quem roda é quem tem acesso, com confirmação do usuário.
2. **`jwt_secret` ou `db_password` "should have at least…".** O `.env` está vazio ou foi sobrescrito. Preencher de novo a partir do `.env.example`.
3. **Erro de conexão com o banco da VPS.** O IP da máquina precisa estar liberado no firewall e no `pg_hba.conf` da VPS.
4. **Autenticação falhou com mensagem em português** ("autenticação do tipo senha falhou"). A conexão caiu num PostgreSQL instalado no Windows (serviço `postgresql-x64-*`), não no container. Use outra porta para o container (ex.: 5433 ou 55433) e confira com `Get-NetTCPConnection -LocalPort <porta>`.
5. **Site diz "Sem conexão com o servidor".** API parada ou em outra porta; conferir `VITE_API_URL` em `agroai/web/.env`. Em desenvolvimento o CORS aceita qualquer porta do localhost; em produção o domínio precisa estar em `CORS_ORIGINS`.
6. **`ModuleNotFoundError: No module named 'app'`.** Comandos da API precisam rodar de dentro de `agroai/api`.
7. **Texto livre não separa as culturas / sempre cai na lista.** Sem `GEMINI_API_KEY` ou o Gemini falhou (cota, timeout): o app usa a lista reserva de propósito. Ver o log (`Falha ao interpretar com Gemini`).
8. **Tela mostra código cru ("ruim", "presente") ou campo vazio.** O front está usando um campo que mudou na API (ex.: `valor` × `texto` no retrato do solo). Comparar o schema Pydantic com `agroai/web/src/api/tipos.ts`.
9. **Fazenda antiga com formato antigo.** Dados derivados (perfil, retrato do solo) são recalculados quando o produtor salva o questionário de novo.
10. **Dado externo vazio.** SoilGrids devolve vazio em área urbana (máscara deles): use ponto rural. NASA POWER usa `-999` para ausente: tem que virar `None`, nunca 0. AppEEARS é assíncrono: "sem dado" pode ser só tarefa ainda processando.
11. **`python3` trava no Windows.** É o atalho da Microsoft Store. Use o Python do `.venv` (`agroai/api/.venv/Scripts/python.exe`) ou o `uv run`.

## Como reportar
Causa com `caminho:linha` e a evidência (linha do log, saída do teste, resposta da API); correção proposta; se envolve a VPS, só descrever e deixar o usuário decidir.
