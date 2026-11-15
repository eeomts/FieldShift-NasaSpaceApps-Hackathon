"""Baixa do AppEEARS o NDVI (MODIS + VIIRS) e a umidade do solo (SMAP L4) dos pontos da demo.

DESCARTADO em 15/11/2026 (ver D-009 em DECISOES.md): o projeto não usa mais o AppEEARS, nem o NDVI e a umidade do solo (SMAP) nesta versão. Script mantido só como histórico.

Uso, da raiz do repositório:

    python data/scripts/baixar_appeears.py           # envia (ou reaproveita) os pedidos, espera e baixa
    python data/scripts/baixar_appeears.py --novo    # força pedidos novos (ex.: para trazer dados mais recentes)
    python data/scripts/baixar_appeears.py --pontos data/demo/pontos_demo_eua.csv --saida data/demo/appeears_eua
                                                     # outro conjunto de pontos (ex.: EUA), com pasta e tarefas.json próprios

Dependências fora da biblioteca padrão: requests

Credenciais (nunca no código), na ordem em que são procuradas:
    1. EARTHDATA_TOKEN                      token do Earthdata Login
    2. EARTHDATA_USER e EARTHDATA_PASS      usuário e senha
    3. ~/.netrc com "machine urs.earthdata.nasa.gov login ... password ..."

O que o script faz:
    - lê os pontos de data/demo/pontos_demo.csv;
    - descobre a versão mais nova de cada produto e o nome exato das camadas pela API (nada fixo à mão);
    - envia dois pedidos de ponto, cada um com a própria data de início:
        "ndvi" (MOD13Q1 + VNP13A1, desde 2001) e "smap" (SPL4SMGP, desde 2015, quando o produto começa).
      Ficam separados para o NDVI não esperar o SMAP, que é bem maior;
    - guarda os pedidos em data/demo/appeears/tarefas.json. Rodar de novo com os mesmos pontos, camadas e
      início reaproveita o pedido já feito em vez de criar outro. Se os parâmetros mudarem, o pedido antigo
      é cancelado no AppEEARS e um novo é enviado;
    - espera cada pedido terminar e baixa o bundle inteiro, sem editar, em data/demo/appeears/<id_da_tarefa>/
      (sobrescreve, não duplica). Um pedido só conta como baixado se a pasta existir com todos os arquivos.

Só rode uma instância por vez para a mesma --saida: duas instâncias disputam o tarefas.json.
Com --saida diferentes (Brasil e EUA) elas não se misturam.

Detalhes em docs/NasaSpaceApps-FieldShift/v1/tools/APPEEARS_AUTOMACAO.md e ToDo/dataset/pessoa-2/03-script-appeears.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import netrc
import os
import re
import sys
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API = "https://appeears.earthdatacloud.nasa.gov/api"
RAIZ = Path(__file__).resolve().parents[2]
PONTOS = RAIZ / "data" / "demo" / "pontos_demo.csv"
SAIDA = RAIZ / "data" / "demo" / "appeears"
ESTADO = SAIDA / "tarefas.json"

ESPERA_ENTRE_CONSULTAS_S = 120
ESPERA_MAXIMA_H = 12
EM_ANDAMENTO = {"pending", "queued", "processing"}

# Pedido -> data de início e {produto (sem versão): sufixos que identificam as camadas}
PEDIDOS = {
    "ndvi": {
        "inicio": dt.date(2001, 1, 1),
        "produtos": {
            "MOD13Q1": ["_NDVI", "_VI_Quality", "_pixel_reliability"],
            "VNP13A1": ["_NDVI", "_VI_Quality", "_pixel_reliability"],
        },
    },
    "smap": {
        "inicio": dt.date(2015, 3, 31),  # o SPL4SMGP começa em 31/03/2015
        "produtos": {
            "SPL4SMGP": ["_sm_surface", "_sm_rootzone"],
        },
    },
}


class ErroAPI(RuntimeError):
    def __init__(self, status, mensagem):
        super().__init__(mensagem)
        self.status = status


# ---------- sessão e credenciais ----------

class AppEEARS:
    def __init__(self):
        self.sessao = requests.Session()
        # Repete erros temporários. POST e DELETE ficam de fora para não duplicar nem repetir ação.
        retry = Retry(total=5, backoff_factor=5, status_forcelist=[429, 500, 502, 503, 504])
        self.sessao.mount("https://", HTTPAdapter(max_retries=retry))
        self.login()

    def login(self):
        token = os.environ.get("EARTHDATA_TOKEN")
        if not token:
            resposta = self.sessao.post(f"{API}/login", auth=credenciais(), timeout=60)
            resposta.raise_for_status()
            token = resposta.json()["token"]
        self.sessao.headers["Authorization"] = f"Bearer {token}"
        # Sem logout de propósito: o AppEEARS devolve o MESMO token a todas as sessões da conta,
        # e um logout invalida esse token para todo mundo (inclusive outros scripts do time).

    def req(self, metodo, caminho, **kw):
        kw.setdefault("timeout", 300)
        resposta = self.sessao.request(metodo, f"{API}/{caminho}", **kw)
        if resposta.status_code in (401, 403) and not os.environ.get("EARTHDATA_TOKEN"):
            # Token vencido ou invalidado (o AppEEARS devolve 403 nesse caso): entra de novo e repete.
            # Se ainda der 403/404, o problema é o recurso, não o token.
            self.login()
            resposta = self.sessao.request(metodo, f"{API}/{caminho}", **kw)
        if not resposta.ok:
            raise ErroAPI(resposta.status_code,
                          f"{metodo} {caminho}: HTTP {resposta.status_code} {resposta.text[:300]}")
        return resposta


def credenciais():
    usuario, senha = os.environ.get("EARTHDATA_USER"), os.environ.get("EARTHDATA_PASS")
    if usuario and senha:
        return usuario, senha
    try:
        dados = netrc.netrc().authenticators("urs.earthdata.nasa.gov")
    except (FileNotFoundError, netrc.NetrcParseError):
        dados = None
    if not dados:
        sys.exit("Sem credenciais: defina EARTHDATA_TOKEN, ou EARTHDATA_USER e EARTHDATA_PASS, "
                 "ou crie o ~/.netrc (ver o topo deste arquivo).")
    return dados[0], dados[2]


# ---------- pontos, catálogo e estado ----------

def ler_pontos():
    with open(PONTOS, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    pontos = [{"id": l["id"], "category": l["regiao"],  # "category" é o nome do campo na API
               "latitude": float(l["latitude"]), "longitude": float(l["longitude"])}
              for l in linhas if l.get("id") and l.get("latitude") and l.get("longitude")]
    if not pontos:
        sys.exit(f"Nenhum ponto em {PONTOS}.")
    return pontos


def chave_versao(produto):
    """Compara versões como números ("10" > "9"), não como texto."""
    return tuple(int(x) for x in re.findall(r"\d+", produto["Version"]))


def produto_mais_novo(catalogo, produto):
    candidatos = [p for p in catalogo
                  if p["Product"] == produto and p.get("Available", True) and not p.get("Deleted", False)]
    if not candidatos:
        raise RuntimeError(f"{produto} não está disponível no AppEEARS")
    return max(candidatos, key=chave_versao)


def camadas(api, produto_versao, sufixos):
    nomes = api.req("GET", f"product/{produto_versao}").json()
    achadas = [n for n in nomes if any(n.endswith(s) for s in sufixos)]
    faltando = [s for s in sufixos if not any(n.endswith(s) for n in achadas)]
    if faltando:
        raise RuntimeError(f"{produto_versao}: camadas não encontradas para {faltando}. Disponíveis: {list(nomes)}")
    return achadas


def assinatura(pontos, camadas_pedido):
    """Identifica um pedido pelos pontos e camadas. O início é comparado à parte (ver enviar())
    e a data final fica de fora porque muda todo dia."""
    texto = json.dumps({"pontos": pontos, "camadas": camadas_pedido}, sort_keys=True)
    return hashlib.sha256(texto.encode()).hexdigest()[:16]


def ler_estado():
    if ESTADO.exists():
        return json.loads(ESTADO.read_text(encoding="utf-8"))
    return {}


def salvar_estado(estado):
    SAIDA.mkdir(parents=True, exist_ok=True)
    tmp = ESTADO.with_suffix(".tmp")
    tmp.write_text(json.dumps(estado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(ESTADO)  # troca atômica: o arquivo nunca fica pela metade


def ja_baixado(info):
    """Só conta como baixado se a pasta existir com todos os arquivos do bundle."""
    if not info.get("baixado"):
        return False
    pasta = SAIDA / info["task_id"]
    arquivos = [a for a in pasta.iterdir() if not a.name.endswith(".part")] if pasta.is_dir() else []
    return len(arquivos) >= info.get("arquivos", 1)


# ---------- fases ----------

def cancelar(api, nome, task_id):
    try:
        api.req("DELETE", f"task/{task_id}")
        print(f"[{nome}] pedido antigo {task_id} cancelado no AppEEARS")
    except ErroAPI as e:
        if e.status == 404:
            print(f"[{nome}] pedido antigo {task_id} já não existe no AppEEARS")
        else:
            print(f"[{nome}] não consegui cancelar o pedido antigo {task_id} ({e}); ele pode ficar na fila",
                  file=sys.stderr)


def enviar(api, estado, pontos, forcar_novo):
    catalogo = api.req("GET", "product").json()
    hoje = dt.date.today()
    for nome, pedido in PEDIDOS.items():
        inicio = pedido["inicio"]
        camadas_pedido = []
        for produto, sufixos in pedido["produtos"].items():
            info_produto = produto_mais_novo(catalogo, produto)
            produto_versao = info_produto["ProductAndVersion"]
            comeco = info_produto.get("TemporalExtentStart")
            if comeco and inicio.isoformat() < comeco:
                print(f"[{nome}] aviso: {produto_versao} só tem dados desde {comeco}; "
                      f"o pedido começa em {inicio}")
            camadas_pedido += [{"product": produto_versao, "layer": c}
                               for c in camadas(api, produto_versao, sufixos)]
        assinatura_pedido = assinatura(pontos, camadas_pedido)

        anterior = estado.get(nome)
        if anterior:
            mesmo_pedido = (anterior["assinatura"] == assinatura_pedido
                            and anterior.get("inicio") == inicio.isoformat())
            em_andamento = anterior.get("status") in EM_ANDAMENTO
            if mesmo_pedido and not forcar_novo and anterior.get("status") not in ("error", "inacessivel"):
                print(f"[{nome}] reaproveitando o pedido {anterior['task_id']} ({anterior['status']})")
                continue
            if mesmo_pedido and forcar_novo and em_andamento:
                print(f"[{nome}] o pedido {anterior['task_id']} ainda está {anterior['status']}: "
                      "espere ele terminar antes de usar --novo", file=sys.stderr)
                continue
            if not mesmo_pedido and em_andamento:
                cancelar(api, nome, anterior["task_id"])  # parâmetros mudaram: o antigo virou lixo

        corpo = {
            "task_type": "point",
            "task_name": f"fieldshift_{PONTOS.stem.removeprefix('pontos_')}_{nome}_{hoje.isoformat()}",
            "params": {
                "dates": [{"startDate": inicio.strftime("%m-%d-%Y"),  # formato americano MM-DD-AAAA
                           "endDate": hoje.strftime("%m-%d-%Y")}],
                "layers": camadas_pedido,
                "coordinates": pontos,
            },
        }
        task_id = api.req("POST", "task", json=corpo).json()["task_id"]
        estado[nome] = {
            "task_id": task_id, "assinatura": assinatura_pedido, "status": "pending",
            "inicio": inicio.isoformat(), "fim": hoje.isoformat(),
            "produtos": sorted({c["product"] for c in camadas_pedido}),
            "camadas": [c["layer"] for c in camadas_pedido],
            "pontos": [p["id"] for p in pontos],
            "enviado_em": dt.datetime.now().isoformat(timespec="seconds"),
        }
        salvar_estado(estado)
        print(f"[{nome}] pedido enviado: {task_id} ({inicio} a {hoje})")


def baixar(api, nome, info):
    task_id = info["task_id"]
    pasta = SAIDA / task_id
    pasta.mkdir(parents=True, exist_ok=True)
    arquivos = api.req("GET", f"bundle/{task_id}").json()["files"]
    for arquivo in arquivos:
        destino = pasta / os.path.basename(arquivo["file_name"])
        parcial = destino.with_name(destino.name + ".part")
        resposta = api.req("GET", f"bundle/{task_id}/{arquivo['file_id']}", stream=True, allow_redirects=True)
        with open(parcial, "wb") as f:
            for pedaco in resposta.iter_content(1 << 16):
                f.write(pedaco)
        parcial.replace(destino)  # só aparece com o nome final quando está completo
    info["arquivos"] = len(arquivos)
    print(f"[{nome}] {len(arquivos)} arquivos em {pasta.relative_to(RAIZ)}")


def esperar_e_baixar(api, estado):
    limite = time.time() + ESPERA_MAXIMA_H * 3600
    faltam = {n for n, i in estado.items()
              if n in PEDIDOS and not ja_baixado(i) and i.get("status") != "inacessivel"}
    for nome in faltam:
        estado[nome].pop("baixado", None)  # marcado como baixado, mas a pasta sumiu ou está incompleta
    while faltam:
        for nome in sorted(faltam):
            info = estado[nome]
            try:
                status = api.req("GET", f"task/{info['task_id']}").json()["status"]
            except ErroAPI as e:
                if e.status not in (403, 404):
                    raise
                print(f"[{nome}] o pedido {info['task_id']} não existe nesta conta "
                      "(feito por outra conta ou apagado); rode com --novo", file=sys.stderr)
                status = "inacessivel"
            if status != info["status"]:
                print(f"[{nome}] {time.strftime('%H:%M')} {status}")
            info["status"] = status
            if status == "done":
                baixar(api, nome, info)
                info["baixado"] = dt.datetime.now().isoformat(timespec="seconds")
                faltam.discard(nome)
            elif status in ("error", "inacessivel"):
                if status == "error":
                    print(f"[{nome}] o AppEEARS devolveu erro; rode de novo para reenviar.", file=sys.stderr)
                faltam.discard(nome)
            salvar_estado(estado)
        if faltam:
            if time.time() > limite:
                print(f"Ainda processando depois de {ESPERA_MAXIMA_H} h: {sorted(faltam)}. "
                      "Rode de novo mais tarde; o pedido é reaproveitado.", file=sys.stderr)
                return False
            time.sleep(ESPERA_ENTRE_CONSULTAS_S)
    return all(ja_baixado(estado[n]) for n in PEDIDOS if n in estado)


def main():
    global PONTOS, SAIDA, ESTADO
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--novo", action="store_true", help="envia pedidos novos mesmo que já existam")
    parser.add_argument("--pontos", type=Path, default=PONTOS, help="CSV de pontos (padrão: os do Brasil)")
    parser.add_argument("--saida", type=Path, default=SAIDA, help="pasta dos bundles e do tarefas.json")
    args = parser.parse_args()
    PONTOS, SAIDA = args.pontos.resolve(), args.saida.resolve()
    ESTADO = SAIDA / "tarefas.json"
    sys.stdout.reconfigure(line_buffering=True)  # mostra o andamento na hora, mesmo rodando no cron

    pontos = ler_pontos()
    estado = ler_estado()
    api = AppEEARS()
    enviar(api, estado, pontos, args.novo)  # um pedido novo substitui o registro antigo, sem "baixado"
    ok = esperar_e_baixar(api, estado)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
