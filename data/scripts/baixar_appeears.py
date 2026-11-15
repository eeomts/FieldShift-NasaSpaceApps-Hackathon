"""Baixa do AppEEARS o NDVI (MODIS + VIIRS) e a umidade do solo (SMAP L4) dos pontos da demo.

Uso, da raiz do repositório:

    python data/scripts/baixar_appeears.py           # envia (ou reaproveita) os pedidos, espera e baixa
    python data/scripts/baixar_appeears.py --novo    # força pedidos novos (ex.: para trazer dados mais recentes)

Dependências fora da biblioteca padrão: requests

Credenciais (nunca no código), na ordem em que são procuradas:
    1. EARTHDATA_TOKEN                      token do Earthdata Login
    2. EARTHDATA_USER e EARTHDATA_PASS      usuário e senha
    3. ~/.netrc com "machine urs.earthdata.nasa.gov login ... password ..."

O que o script faz:
    - lê os pontos de data/demo/pontos_demo.csv;
    - descobre a versão mais nova de cada produto e o nome exato das camadas pela API (nada fixo à mão);
    - envia dois pedidos de ponto: "ndvi" (MOD13Q1 + VNP13A1) e "smap" (SPL4SMGP), separados para o
      NDVI não esperar o SMAP, que é bem maior;
    - guarda os pedidos em data/demo/appeears/tarefas.json. Rodar de novo com os mesmos pontos e
      produtos reaproveita o pedido já feito em vez de criar outro;
    - espera cada pedido terminar e baixa os arquivos, sem editar, em data/demo/appeears/<id_da_tarefa>/
      (sobrescreve, não duplica).

Detalhes em docs/NasaSpaceApps-FieldShift/v1/tools/APPEEARS_AUTOMACAO.md e ToDo/dataset/pessoa-2/03-script-appeears.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import netrc
import os
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

INICIO = dt.date(2001, 1, 1)
ESPERA_ENTRE_CONSULTAS_S = 120
ESPERA_MAXIMA_H = 12

# Pedido -> {produto (sem versão): palavras que identificam as camadas}
PEDIDOS = {
    "ndvi": {
        "MOD13Q1": ["_NDVI", "_VI_Quality", "_pixel_reliability"],
        "VNP13A1": ["_NDVI", "_VI_Quality", "_pixel_reliability"],
    },
    "smap": {
        "SPL4SMGP": ["_sm_surface", "_sm_rootzone"],
    },
}


# ---------- sessão e credenciais ----------

class AppEEARS:
    def __init__(self):
        self.s = requests.Session()
        # Repete erros temporários. POST fica de fora para não duplicar pedido.
        retry = Retry(total=5, backoff_factor=5, status_forcelist=[429, 500, 502, 503, 504])
        self.s.mount("https://", HTTPAdapter(max_retries=retry))
        self.login()

    def login(self):
        token = os.environ.get("EARTHDATA_TOKEN")
        if not token:
            r = self.s.post(f"{API}/login", auth=credenciais(), timeout=60)
            r.raise_for_status()
            token = r.json()["token"]
        self.s.headers["Authorization"] = f"Bearer {token}"

    def req(self, metodo, caminho, **kw):
        kw.setdefault("timeout", 300)
        r = self.s.request(metodo, f"{API}/{caminho}", **kw)
        if r.status_code == 401 and not os.environ.get("EARTHDATA_TOKEN"):
            self.login()  # token venceu: entra de novo e repete
            r = self.s.request(metodo, f"{API}/{caminho}", **kw)
        if not r.ok:
            raise RuntimeError(f"{metodo} {caminho}: HTTP {r.status_code} {r.text[:300]}")
        return r

    def logout(self):
        if os.environ.get("EARTHDATA_TOKEN"):
            return  # token de fora: não é nosso para encerrar
        try:
            self.s.post(f"{API}/logout", timeout=30)
        except requests.RequestException:
            pass


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
    pontos = [{"id": l["id"], "category": l["regiao"],
               "latitude": float(l["latitude"]), "longitude": float(l["longitude"])}
              for l in linhas if l.get("id") and l.get("latitude") and l.get("longitude")]
    if not pontos:
        sys.exit(f"Nenhum ponto em {PONTOS}.")
    return pontos


def versao_mais_nova(catalogo, produto):
    candidatos = [p for p in catalogo
                  if p["Product"] == produto and p.get("Available", True) and not p.get("Deleted", False)]
    if not candidatos:
        raise RuntimeError(f"{produto} não está disponível no AppEEARS")
    return max(candidatos, key=lambda p: p["Version"])["ProductAndVersion"]


def camadas(api, produto_versao, palavras):
    nomes = api.req("GET", f"product/{produto_versao}").json()
    achadas = [n for n in nomes if any(n.endswith(p) for p in palavras)]
    faltando = [p for p in palavras if not any(n.endswith(p) for n in achadas)]
    if faltando:
        raise RuntimeError(f"{produto_versao}: camadas não encontradas para {faltando}. Disponíveis: {list(nomes)}")
    return achadas


def assinatura(pontos, camadas_pedido):
    """Identifica um pedido pelos pontos e camadas, sem a data final (que muda todo dia)."""
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


# ---------- fases ----------

def enviar(api, estado, pontos, forcar_novo):
    catalogo = api.req("GET", "product").json()
    hoje = dt.date.today()
    for nome, produtos in PEDIDOS.items():
        camadas_pedido = []
        for produto, palavras in produtos.items():
            pv = versao_mais_nova(catalogo, produto)
            camadas_pedido += [{"product": pv, "layer": c} for c in camadas(api, pv, palavras)]
        sig = assinatura(pontos, camadas_pedido)
        anterior = estado.get(nome)
        if anterior and anterior["assinatura"] == sig and not forcar_novo and anterior["status"] != "error":
            print(f"[{nome}] reaproveitando o pedido {anterior['task_id']} ({anterior['status']})")
            continue
        corpo = {
            "task_type": "point",
            "task_name": f"fieldshift_demo_{nome}_{hoje.isoformat()}",
            "params": {
                "dates": [{"startDate": INICIO.strftime("%m-%d-%Y"),  # formato americano MM-DD-AAAA
                           "endDate": hoje.strftime("%m-%d-%Y")}],
                "layers": camadas_pedido,
                "coordinates": pontos,
            },
        }
        task_id = api.req("POST", "task", json=corpo).json()["task_id"]
        estado[nome] = {
            "task_id": task_id, "assinatura": sig, "status": "pending",
            "inicio": INICIO.isoformat(), "fim": hoje.isoformat(),
            "produtos": sorted({c["product"] for c in camadas_pedido}),
            "camadas": [c["layer"] for c in camadas_pedido],
            "pontos": [p["id"] for p in pontos],
            "enviado_em": dt.datetime.now().isoformat(timespec="seconds"),
        }
        salvar_estado(estado)
        print(f"[{nome}] pedido enviado: {task_id} ({INICIO} a {hoje})")


def baixar(api, nome, info):
    task_id = info["task_id"]
    pasta = SAIDA / task_id
    pasta.mkdir(parents=True, exist_ok=True)
    arquivos = api.req("GET", f"bundle/{task_id}").json()["files"]
    for a in arquivos:
        destino = pasta / os.path.basename(a["file_name"])
        r = api.req("GET", f"bundle/{task_id}/{a['file_id']}", stream=True, allow_redirects=True)
        with open(destino, "wb") as f:
            for pedaco in r.iter_content(1 << 16):
                f.write(pedaco)
    print(f"[{nome}] {len(arquivos)} arquivos em {pasta.relative_to(RAIZ)}")


def esperar_e_baixar(api, estado):
    limite = time.time() + ESPERA_MAXIMA_H * 3600
    faltam = {n for n, i in estado.items() if n in PEDIDOS and not i.get("baixado")}
    while faltam:
        for nome in sorted(faltam):
            info = estado[nome]
            status = api.req("GET", f"task/{info['task_id']}").json()["status"]
            if status != info["status"]:
                print(f"[{nome}] {time.strftime('%H:%M')} {status}")
            info["status"] = status
            if status == "done":
                baixar(api, nome, info)
                info["baixado"] = dt.datetime.now().isoformat(timespec="seconds")
                faltam.discard(nome)
            elif status == "error":
                print(f"[{nome}] o AppEEARS devolveu erro; rode de novo para reenviar.", file=sys.stderr)
                faltam.discard(nome)
            salvar_estado(estado)
        if faltam:
            if time.time() > limite:
                print(f"Ainda processando depois de {ESPERA_MAXIMA_H} h: {sorted(faltam)}. "
                      "Rode de novo mais tarde; o pedido é reaproveitado.", file=sys.stderr)
                return False
            time.sleep(ESPERA_ENTRE_CONSULTAS_S)
    return all(estado[n].get("baixado") for n in PEDIDOS if n in estado)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--novo", action="store_true", help="envia pedidos novos mesmo que já existam")
    args = parser.parse_args()
    sys.stdout.reconfigure(line_buffering=True)  # mostra o andamento na hora, mesmo rodando no cron

    pontos = ler_pontos()
    estado = ler_estado()
    if args.novo:
        for info in estado.values():
            info.pop("baixado", None)
    api = AppEEARS()
    try:
        enviar(api, estado, pontos, args.novo)
        ok = esperar_e_baixar(api, estado)
    finally:
        api.logout()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
