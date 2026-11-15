# Deploy do AgroAI

```
internet :80/:443
  -> web   Caddy: TLS, serve o build do React e repassa /api/* para a API
       -> api   FastAPI (uvicorn): aplica as migrations e responde
            -> db    Postgres 17 + pgvector + PostGIS (opcional: DB_HOST=db)
```

Três regras que explicam o resto:

1. **`.deploy/env/<ambiente>.env` é a única configuração** de cada ambiente (`local` ou `producao`). Fica fora do Git; o modelo é o `env/exemplo.env`.
2. **Quem sobe é o `./.deploy/agroai`.** Ele lê o `.env`, valida e chama o `docker compose`. O `docker compose` direto para com erro de propósito.
3. **As migrations rodam sozinhas.** A API aplica as pendentes antes de servir; se uma falhar, o container não sobe (melhor do que servir com o banco errado).

Site e API ficam no **mesmo domínio**: o front é compilado com `VITE_API_URL=/api` e o Caddy tira o `/api` antes de repassar. Não há CORS para configurar.

## Local (Docker Desktop aberto)

```sh
cp .deploy/env/exemplo.env .deploy/env/local.env
# preencha JWT_SECRET (e troque a DB_PASSWORD)
./.deploy/agroai local up -d --build
```

- Site: http://localhost:9090 · API: http://localhost:9090/api/saude · docs da API: http://localhost:9090/api/docs
- Banco: `127.0.0.1:5434` (usuário e senha do `local.env`), para DBeaver/psql.
- Não há bind mount: mudou código, rode `up -d --build` de novo. Para mexer no código com recarga na hora, use o `uv run uvicorn` e o `npm run dev` do `agroai/README.md`.

## Primeira subida na VPS

Precisa de Docker e do domínio já apontando para o IP da VPS (o Caddy pede o certificado sozinho, mas só se o DNS já resolver).

```sh
git clone <repo> ~/agroai && cd ~/agroai
cp .deploy/env/exemplo.env .deploy/env/producao.env
nano .deploy/env/producao.env
```

No `producao.env`:

```sh
SITE=https://agroai.SEU-DOMINIO.com
JWT_SECRET=<gerado, 48+ caracteres>
```

E o banco, de um dos dois jeitos:

| | Banco no compose | Postgres que já existe |
|---|---|---|
| `DB_HOST` | `db` | endereço do servidor |
| Extensões | já vêm (pgvector, PostGIS) | `vector` e `postgis` precisam estar instaladas nele (exige admin) |
| Backup | `./.deploy/backup producao` | o mesmo script (usa um container `postgres:17`) |

Postgres fora do Docker **na mesma máquina**: `DB_HOST=host.docker.internal` (não `localhost`: dentro do container, `localhost` é o próprio container).

Então:

```sh
./.deploy/agroai producao up -d --build
./.deploy/agroai producao logs -f
```

## VPS que já tem nginx (outros projetos)

Se um nginx do host já ocupa 80/443, o Caddy não sobe ("address already in use"). Não derrube o nginx: ponha o AgroAI atrás dele.

```
internet :443 -> nginx do host (TLS pelo certbot) -> 127.0.0.1:8082 -> Caddy (só HTTP) -> API
```

No `producao.env`: `PROXY=127.0.0.1:8082`. O script troca o Caddy para `:80` sem certificado, publicado só em `127.0.0.1`.

```sh
./.deploy/agroai producao up -d --build
curl -I -H 'Host: agroai.SEU-DOMINIO.com' http://127.0.0.1:8082/   # 200

sudo cp .deploy/nginx-agroai.conf /etc/nginx/sites-available/agroai
sudo nano /etc/nginx/sites-available/agroai        # server_name e porta
sudo ln -s /etc/nginx/sites-available/agroai /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d agroai.SEU-DOMINIO.com
```

A porta tem de estar livre: `sudo ss -ltnp | grep 8082` sem saída.

## Atualizar

```sh
cd ~/agroai && git pull && ./.deploy/agroai producao up -d --build
```

Migration nova entra sozinha no start. Os dados ficam no volume.

## Dia a dia

```sh
./.deploy/agroai local ps                         # o que está de pé
./.deploy/agroai local logs -f api                # log da API (erro de Python cai aqui)
./.deploy/agroai local logs -f web                # acesso e TLS
./.deploy/agroai local restart api
./.deploy/agroai local down                       # derruba; os dados ficam no volume
./.deploy/agroai local exec api alembic current   # migration aplicada
./.deploy/agroai local exec db psql -U agricultura_app -d agricultura
```

## Backup

```sh
./.deploy/backup producao                                            # dump conferido em .deploy/backups/
./.deploy/restaurar producao .deploy/backups/agroai-producao-<data>.sql.gz
```

- O `backup` confere se o dump terminou inteiro, guarda `BACKUP_DIAS` dias e, se `BACKUP_REMOTO` estiver preenchido e o `rclone` configurado, manda uma cópia para lá.
- O `restaurar` pede para digitar `RESTAURAR` e, antes de mexer, faz um backup do estado atual.
- Agende na VPS (`crontab -e`), todo dia às 3h:
  ```cron
  0 3 * * * cd /home/<usuario>/agroai && ./.deploy/backup producao >> .deploy/backups/backup.log 2>&1
  ```
- Teste a restauração de vez em quando no ambiente `local`: backup que nunca foi restaurado é só uma esperança.

## Armadilhas

1. **`./.deploy/agroai <ambiente> down -v` apaga o banco** (e o certificado). É o único comando que mexe nos volumes.
2. **Crie o `.env` do ambiente antes do primeiro `up`.** O script confere e avisa.
3. **Porta ocupada ou "acesso a um soquete proibido" no Windows:** o Hyper-V/WSL reserva faixas de porta a cada boot. Veja com `netsh interface ipv4 show excludedportrange protocol=tcp` e troque a porta do `SITE`. Nesta máquina a 9080 e a 443 já são do `controla`, e a 5432 é de um PostgreSQL instalado no Windows.
4. **`VITE_API_URL` é de build**, não de execução: mudou, rode `up -d --build`.
5. **O certificado vive no volume `caddy`.** Não apague à toa: o Let's Encrypt limita quantos certificados você pode pedir por semana.
6. **API reiniciando sem parar:** quase sempre é migration falhando ou banco inacessível. Veja `./.deploy/agroai <ambiente> logs api`.
7. **`pg_dump` com versão menor que a do servidor** falha no backup de banco externo: troque `postgres:17-alpine` no `.deploy/lib.sh` pela versão do servidor.
