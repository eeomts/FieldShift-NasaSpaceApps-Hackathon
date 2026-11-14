# Coleta automática via AppEEARS

Complemento a `APPEEARS.md`, `EARTHDATA_SEARCH.md` e `comparative/COMPARATIVO_FINAL.md`. Explica como baixar os dados da NASA de forma automática e sempre atualizada, sem pedido manual e sem manutenção de token.

> **Situação (14/11/2026):** proposta. O script descrito aqui **ainda não está no repositório** e **nunca foi executado**. Alguns nomes de campo foram escritos de memória e estão listados em [Pontos a confirmar](#pontos-a-confirmar).

## Resumo

- **O Earthdata Search não envia pedidos ao AppEEARS.** Ele é a interface de navegador do catálogo da NASA (o CMR). Ninguém baixa arquivo por ele neste projeto.
- **Quem faz os pedidos é a API do AppEEARS**, chamada por um script agendado (`appeears_sync.py`).
- **O CMR entra como sensor:** antes de cada pedido, o script pergunta ao CMR se saiu dado novo. Se não saiu, não pede nada.
- **O token não é guardado.** O script guarda o usuário e a senha do Earthdata Login e gera um token novo a cada execução.

| Etapa | Manual | Automatizado |
|---|---|---|
| 1. Descobrir produto, versão e cobertura | Earthdata Search | `GET /product` do AppEEARS + CMR API |
| 2. Enviar o pedido de ponto | Site do AppEEARS | `POST /task` |
| 3. Esperar e baixar | Site do AppEEARS | `GET /task/{id}` e `GET /bundle/{id}` |

## Produtos e prioridade

Da lista final (`COMPARATIVO_FINAL.md` §5), só quatro produtos vêm do catálogo da NASA. O resto (NASA POWER, SoilGrids, SRTM via OpenTopoData, IBGE PAM, ZARC) tem API própria e não passa por aqui.

| # | Produto | `short_name.versão` | Como baixar | Prioridade |
|---|---|---|---|---|
| 1 | NDVI MODIS (Terra) | `MOD13Q1.061` | AppEEARS (ponto) | 🟢 Essencial |
| 2 | NDVI VIIRS | `VNP13A1.002` | AppEEARS (ponto) | 🟢 Essencial (continuidade do MODIS) |
| 3 | Umidade do solo SMAP L4 | `SPL4SMGP` (confirmar a versão atual) | AppEEARS, no mesmo ciclo do NDVI | 🟡 1º da fila |
| 4 | Chuva GPM IMERG diário | `GPM_3IMERGDL` (Late) e `GPM_3IMERGDF` (Final) | `earthaccess` (não está no AppEEARS) | 🟡 2º da fila |

- **Opcional:** `MYD13Q1.061` (MODIS Aqua) junto com o item 1, para ter uma composição a cada ~8 dias em vez de 16. `VJ113A1` (VIIRS do NOAA-20) ainda precisa ser confirmado no catálogo.
- **Pitch, sem download agora:** HLS (`HLSL30`/`HLSS30`) e FIRMS (API própria).
- **Fora:** GLDAS, MOD16A2, ECOSTRESS, GRACE, Landsat e Sentinel separados.

### Qual IMERG usar

| Versão | Atraso | Uso |
|---|---|---|
| Final (`GPM_3IMERGDF`) | ~3 a 4 meses | Série histórica (mais precisa) |
| Late (`GPM_3IMERGDL`) | ~14 horas | Situação atual |

A série usa o Final; os meses mais recentes são completados com o Late, que vai sendo trocado pelo Final quando ele sair. O script do IMERG ainda não foi escrito (ver [Pendências](#pendências)).

### O que fazer no Earthdata Search (uma vez)

1. Confirmar o `short_name` e a versão de cada produto acima, principalmente `SPL4SMGP` e `VJ113A1`.
2. Ver se a cobertura chega às regiões da demo.
3. Aceitar as autorizações do LP DAAC (MODIS/VIIRS), do NSIDC (SMAP) e do GES DISC (IMERG) no perfil do Earthdata Login. Sem isso, o primeiro download automático falha com erro de permissão.

## Como o script funciona sozinho

O **cron** (ou o GitHub Actions) acorda o script uma vez por dia. Cada execução faz o ciclo abaixo e termina; nada fica esperando.

```
cron (06:00)
  └─ appeears_sync.py
       1. login        → usuário/senha (.netrc ou Secrets) → POST /login → token novo
       2. collect()    → para cada task_id pendente: GET /task/{id}
                            "done"       → baixa o bundle e avança a data "last"
                            "processing" → deixa para amanhã
                            "error"      → apaga e reenvia amanhã (2 erros seguidos = alerta)
       3. submit()     → para cada produto:
                            GET /product → descobre a versão mais nova
                            CMR          → "saiu granule depois da minha última data?"
                                           não → pula
                                           sim → POST /task (última data − 32 dias até hoje)
                                                 guarda o task_id como pendente
       4. salva o estado e faz logout
```

### As cinco regras que evitam manutenção

1. **Versão descoberta, não digitada.** O script pega a maior versão disponível de cada `short_name` em `GET /product`. Quando sair uma versão nova (por exemplo, `MOD13Q1.062`), ele passa a usá-la sozinho e baixa a série inteira de novo, porque o estado é guardado por versão.
2. **Camada achada por palavra-chave.** O script procura a camada que contém `NDVI` ou `sm_rootzone` em `GET /product/{id}`, em vez de fixar `_250m_16_days_NDVI`.
3. **Pedido incremental.** Cada pedido vai de `última data − 32 dias` até hoje. A sobreposição cobre composições que saem com atraso; as linhas repetidas são descartadas no pós-processamento.
4. **Pergunta ao CMR antes de pedir.** A busca de granules no CMR é pública, não pede login e usa a mesma base do Earthdata Search. Na maioria dos dias a resposta é "nada novo" e o script não envia nada.
5. **Duas fases.** Uma execução envia os pedidos e guarda os `task_id`; a seguinte baixa os que ficaram prontos. Se uma execução falhar, a próxima retoma de onde parou.

### O arquivo de estado

`data/appeears_state.json` é a memória entre uma execução e a próxima:

```json
{
  "last":    {"MOD13Q1.061": "2026-10-16", "VNP13A1.002": "2026-10-23"},
  "pending": {"SPL4SMGP": {"task_id": "abc-123", "pv": "SPL4SMGP.008", "newest": "2026-11-11"}},
  "errors":  {}
}
```

- `last`: data do granule mais novo já coberto, por produto **e versão**.
- `pending`: pedidos enviados que ainda não foram baixados.
- `errors`: quantos erros seguidos cada produto teve.

Na prática:

- **Dia 1:** não há estado, então o script pede tudo desde 2016.
- **Dia 2:** baixa o que ficou pronto e marca `last`.
- **Dia 3 em diante:** quase sempre "nada novo". Quando sai uma composição nova (a cada 8 a 16 dias), pede só o último mês.

> `last` recebe a data do **granule mais novo visto no CMR** no momento do pedido, e não a data de hoje. Se recebesse a data de hoje, uma composição que começou antes do pedido, mas foi publicada depois, nunca seria baixada.

## Token e credenciais

**Não existe token para renovar.** O token do AppEEARS vale cerca de 48 h, e cada execução dura minutos e começa com `POST /login`. O login *é* a renovação. Se a API responder 401 no meio da execução, o script faz login de novo e repete a chamada.

O que se guarda é o usuário e a senha do Earthdata Login:

| Onde roda | Onde guardar |
|---|---|
| Computador ou servidor | `~/.netrc`, com `chmod 600` |
| GitHub Actions | *Settings → Secrets*: `EDL_USER` e `EDL_PASS` |

Conteúdo do `~/.netrc` (a mesma linha serve para o `earthaccess`, usado no IMERG):

```
machine urs.earthdata.nasa.gov login SEU_USUARIO password SUA_SENHA
```

> **Não usar o token de usuário** gerado no perfil do `urs.earthdata.nasa.gov`. Ele vence a cada 60 dias e seria justamente a manutenção manual que queremos evitar.

A única manutenção de credencial é **atualizar o `.netrc` ou os Secrets quando a senha do Earthdata mudar**.

## Código

### `config/pontos.json` (exemplo)

Um ponto por talhão, mais pontos de controle se for útil. As coordenadas abaixo são ilustrativas.

```json
[
  {"id": "talhao_1", "category": "talhao",   "latitude": -2.99, "longitude": -47.35},
  {"id": "controle", "category": "controle", "latitude": -2.97, "longitude": -47.33}
]
```

### `scripts/appeears_sync.py`

Roda a partir da raiz do projeto. Depende só de `requests`.

```python
"""Coleta incremental do AppEEARS para o Field Shift Brasil.

Roda uma vez por dia (cron ou GitHub Actions). Não precisa de edição quando
saem versões novas dos produtos nem de renovação manual de token.
"""
import datetime as dt
import json
import netrc
import os
import sys

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API = "https://appeears.earthdatacloud.nasa.gov/api"
CMR = "https://cmr.earthdata.nasa.gov/search"
STATE = "data/appeears_state.json"
POINTS_FILE = "config/pontos.json"
RAW_DIR = "data/raw"
START = dt.date(2016, 1, 1)
OVERLAP = dt.timedelta(days=32)
MAX_ERRORS = 2

# short_name -> palavras-chave das camadas (sem versão: ela é descoberta)
WANTED = {
    "MOD13Q1": ["NDVI", "VI_Quality"],
    "MYD13Q1": ["NDVI", "VI_Quality"],
    "VNP13A1": ["NDVI", "VI_Quality"],
    "SPL4SMGP": ["sm_rootzone", "sm_surface"],
}


# ---------- credenciais e sessão ----------

def credentials():
    if "EDL_USER" in os.environ:                       # GitHub Actions
        return os.environ["EDL_USER"], os.environ["EDL_PASS"]
    user, _, pwd = netrc.netrc().authenticators("urs.earthdata.nasa.gov")
    return user, pwd                                   # computador ou servidor


class AppEEARS:
    def __init__(self):
        self.s = requests.Session()
        # repete erros temporários; POST fica de fora para não duplicar pedido
        retry = Retry(total=5, backoff_factor=5, status_forcelist=[429, 500, 502, 503, 504])
        self.s.mount("https://", HTTPAdapter(max_retries=retry))
        self.login()

    def login(self):
        r = self.s.post(f"{API}/login", auth=credentials(), timeout=60)
        r.raise_for_status()
        self.s.headers["Authorization"] = f"Bearer {r.json()['token']}"

    def req(self, method, path, **kw):
        kw.setdefault("timeout", 300)
        r = self.s.request(method, f"{API}/{path}", **kw)
        if r.status_code == 401:                       # token venceu: login e repete
            self.login()
            r = self.s.request(method, f"{API}/{path}", **kw)
        r.raise_for_status()
        return r

    def logout(self):
        try:
            self.s.post(f"{API}/logout", timeout=30)
        except requests.RequestException:
            pass


# ---------- estado ----------

def load_state():
    if os.path.exists(STATE):
        with open(STATE) as f:
            state = json.load(f)
    else:
        state = {}
    for key in ("last", "pending", "errors"):
        state.setdefault(key, {})
    return state


def save_state(state):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE)                             # troca atômica


# ---------- catálogo ----------

def latest_version(products, short):
    cands = [p for p in products if p["Product"] == short and p.get("Available", True)]
    if not cands:
        raise RuntimeError(f"{short} não está disponível no AppEEARS")
    return max(cands, key=lambda p: p["Version"])["ProductAndVersion"]


def find_layers(api, pv, keywords):
    layers = api.req("GET", f"product/{pv}").json()
    found = [n for n in layers if any(k.lower() in n.lower() for k in keywords)]
    if not found:
        raise RuntimeError(f"nenhuma camada de {pv} contém {keywords}")
    return found


def bbox_of(points, pad=0.01):
    lats = [p["latitude"] for p in points]
    lons = [p["longitude"] for p in points]
    return f"{min(lons) - pad},{min(lats) - pad},{max(lons) + pad},{max(lats) + pad}"


def newest_granule(short, version, bbox):
    """Data (AAAA-MM-DD) do granule mais novo no CMR para a área, ou None."""
    r = requests.get(f"{CMR}/granules.json", timeout=60, params={
        "short_name": short, "version": version, "bounding_box": bbox,
        "sort_key": "-start_date", "page_size": 1})
    r.raise_for_status()
    entries = r.json()["feed"]["entry"]
    return entries[0]["time_start"][:10] if entries else None


# ---------- fases ----------

def collect(state, api):
    for short, job in list(state["pending"].items()):
        tid = job["task_id"]
        status = api.req("GET", f"task/{tid}").json()["status"]
        if status == "error":
            state["errors"][short] = state["errors"].get(short, 0) + 1
            del state["pending"][short]                # reenvia na próxima execução
            print(f"{job['pv']}: pedido {tid} com erro")
            continue
        if status != "done":
            print(f"{job['pv']}: {status}")
            continue
        outdir = os.path.join(RAW_DIR, job["pv"], tid)
        os.makedirs(outdir, exist_ok=True)
        for f in api.req("GET", f"bundle/{tid}").json()["files"]:
            resp = api.req("GET", f"bundle/{tid}/{f['file_id']}", stream=True, allow_redirects=True)
            with open(os.path.join(outdir, os.path.basename(f["file_name"])), "wb") as out:
                for chunk in resp.iter_content(1 << 16):
                    out.write(chunk)
        state["last"][job["pv"]] = job["newest"]
        state["errors"].pop(short, None)
        del state["pending"][short]
        print(f"{job['pv']}: baixado em {outdir}")


def submit(state, api, points):
    products = api.req("GET", "product").json()
    today = dt.date.today()
    for short, keywords in WANTED.items():
        if short in state["pending"]:
            continue                                   # já tem pedido na fila
        pv = latest_version(products, short)
        last = state["last"].get(pv)
        newest = newest_granule(short, pv.split(".")[1], bbox_of(points))
        if last and newest and newest <= last:
            print(f"{pv}: nada novo")
            continue
        start = max(START, dt.date.fromisoformat(last) - OVERLAP) if last else START
        task = {
            "task_type": "point",
            "task_name": f"fieldshift_{pv}_{today}",
            "params": {
                "dates": [{"startDate": start.strftime("%m-%d-%Y"),   # formato americano
                           "endDate": today.strftime("%m-%d-%Y")}],
                "layers": [{"product": pv, "layer": l} for l in find_layers(api, pv, keywords)],
                "coordinates": points,
            },
        }
        tid = api.req("POST", "task", json=task).json()["task_id"]
        state["pending"][short] = {"task_id": tid, "pv": pv, "newest": newest or str(today)}
        print(f"{pv}: enviado {tid} ({start} a {today})")


def main():
    with open(POINTS_FILE) as f:
        points = json.load(f)
    state = load_state()
    api = AppEEARS()
    try:
        collect(state, api)
        submit(state, api, points)
    finally:
        save_state(state)
        api.logout()
    failing = [s for s, n in state["errors"].items() if n >= MAX_ERRORS]
    if failing:
        print(f"ALERTA: erros seguidos em {failing}", file=sys.stderr)
        sys.exit(1)                                    # cron/Actions avisam


if __name__ == "__main__":
    main()
```

### O que cada parte faz

| Parte | Função |
|---|---|
| `credentials()` | Lê o usuário e a senha das variáveis de ambiente (Actions) ou do `~/.netrc` |
| `AppEEARS` | Sessão com novas tentativas, `timeout`, login automático e novo login no 401 |
| `load_state` / `save_state` | Lê e grava o estado; a gravação é atômica, então uma queda no meio não corrompe o arquivo |
| `latest_version` | Escolhe a versão mais nova de cada produto no catálogo do AppEEARS |
| `find_layers` | Acha os nomes exatos das camadas por palavra-chave |
| `newest_granule` | Pergunta ao CMR qual é o granule mais novo na área dos pontos |
| `collect` | Verifica os pedidos pendentes e baixa os prontos para `data/raw/<produto.versão>/<task_id>/` |
| `submit` | Envia um pedido por produto só quando o CMR mostra dado novo |
| `main` | Junta tudo e termina com erro se algum produto falhou duas vezes seguidas |

## Agendamento

As composições do MODIS e do VIIRS saem a cada 8 a 16 dias, e o SMAP L4 tem cerca de 3 dias de atraso. **Uma execução por dia basta.**

### Opção 1: cron num computador ou servidor (recomendada)

```cron
MAILTO=voce@exemplo.com
0 6 * * *  cd /caminho/projeto && flock -n /tmp/appeears.lock python scripts/appeears_sync.py >> logs/sync.log 2>&1
```

- O `flock -n` impede duas execuções ao mesmo tempo, que enviariam pedidos duplicados.
- Com `MAILTO`, o cron manda e-mail quando o script termina com erro.

### Opção 2: GitHub Actions

Não precisa de servidor, mas a máquina do Actions é apagada ao final. Por isso o estado é salvo com commit, e os dados baixados precisam ir para o banco ou para um armazenamento externo dentro da própria execução. Senão, se perdem.

```yaml
# .github/workflows/appeears-sync.yml
name: appeears-sync
on:
  schedule:
    - cron: "0 9 * * *"        # 06:00 em Brasília (UTC-3)
  workflow_dispatch:
concurrency: appeears-sync     # equivalente ao flock
jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install requests
      - run: python scripts/appeears_sync.py
        env:
          EDL_USER: ${{ secrets.EDL_USER }}
          EDL_PASS: ${{ secrets.EDL_PASS }}
      # aqui entra o passo que envia data/raw para o banco ou armazenamento
      - name: Salvar estado
        if: always()
        run: |
          git config user.name "appeears-bot"
          git config user.email "actions@users.noreply.github.com"
          git add data/appeears_state.json
          git commit -m "chore: estado do AppEEARS" || true
          git push
```

## Checklist (uma vez só)

- [ ] Criar a conta no `urs.earthdata.nasa.gov`.
- [ ] Entrar uma vez pelo navegador no AppEEARS e no Earthdata Search, e aceitar as autorizações do LP DAAC, do NSIDC e do GES DISC.
- [ ] Criar o `~/.netrc` (com `chmod 600`) ou os Secrets `EDL_USER` e `EDL_PASS`.
- [ ] Criar o `config/pontos.json` com os talhões da demo.
- [ ] Instalar a dependência: `pip install requests`.
- [ ] Rodar uma vez na mão e conferir os [pontos a confirmar](#pontos-a-confirmar).
- [ ] Agendar no cron ou no GitHub Actions.

Depois disso, a manutenção fica em três casos: **troca de senha**, **um produto sair do catálogo** e **mudança na API do AppEEARS**. Os dois últimos são raros e aparecem como falha no log.

## Pontos a confirmar

Escritos de memória; conferir na primeira execução manual:

| O quê | Como conferir |
|---|---|
| O campo `Available` existe em cada item de `GET /product` | Imprimir um item da resposta |
| As palavras-chave `sm_rootzone` e `sm_surface` encontram as camadas do SMAP L4 | Imprimir as chaves de `GET /product/SPL4SMGP.<versão>` |
| O CMR aceita a versão no formato do AppEEARS (`061`, `002`, `008`) | Rodar `newest_granule` para cada produto e ver se não volta `None` |
| A versão atual do `SPL4SMGP` e a existência do `VJ113A1` | Earthdata Search ou `GET /product` |
| O limite de pontos por pedido | Documentação do AppEEARS |

> Se `newest_granule` voltar `None` (versão em formato diferente no CMR, por exemplo), o script não quebra, mas passa a enviar um pedido por dia para aquele produto. É o primeiro sintoma a olhar no log.

## Pendências

| # | Pendência | Observação |
|---|---|---|
| P-1 | Pôr o script, o `config/pontos.json` e o workflow no repositório | Este documento só descreve |
| P-2 | **Pós-processamento** | O script só baixa. Falta juntar os CSVs, tirar duplicatas por `(ponto, data, camada)` mantendo a mais recente, filtrar pela camada de qualidade e gravar no PostgreSQL (ver `application/architecture/BANCO-DE-DADOS.md`) |
| P-3 | Script do IMERG com `earthaccess` | Final para o histórico, Late para os meses recentes; usa o mesmo `.netrc` |
| P-4 | Dividir os pontos em lotes | Só se a lista passar do limite de pontos por pedido |

## Limitações

- **Não é tempo real.** Os pedidos do AppEEARS entram numa fila e podem levar horas; o dado novo aparece no dia seguinte, não na hora em que o produtor abre a ferramenta.
- **Só pontos.** O script faz pedidos `point`. Pedidos de área (HLS, mapas de solo descoberto) ficam para depois, como no pitch.
- **Primeira execução pesada.** A carga desde 2016 pode demorar; as seguintes pedem só o último mês.
- **Versão nova baixa tudo de novo.** É intencional, para não misturar versões na mesma série, mas gera uma carga grande no dia em que a versão muda.
- **Fim do MODIS.** Quando o Terra e o Aqua saírem de operação, o CMR para de mostrar granules novos do MODIS, e o VIIRS segue sozinho, sem mudança no script.
