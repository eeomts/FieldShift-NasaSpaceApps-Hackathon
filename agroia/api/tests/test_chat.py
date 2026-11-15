"""Chat: rotas das conversas e o agente com um modelo falso roteirizado (sem rede, sem chave, sem NASA POWER)."""
import json
from datetime import date, timedelta

import pytest
from fastapi import Depends
from google.genai import types
from sqlalchemy import text

from app.core.db import get_engine
from app.main import app
from app.repositories.conhecimento_repository import ConhecimentoRepository
from app.services.agente import agente_service
from app.services.agente.agente_service import de_json, para_json, provedor_de_busca
from app.services.agente.busca_conhecimento_service import BuscaConhecimentoService
from app.services.agente.modelo import get_modelo
from app.services.agente.prompt import RESPOSTA_FORA_DO_ESCOPO
from app.services.conversa_service import titulo_da_pergunta
from app.services.integracao.nasa_power import DiaPower, ErroNasaPower, SeriePower, get_cliente

SEM_TOKEN = {}
IRECE = {
    "q1_quem": "produtor", "q4_animais": "nao", "q6_irrigacao": "nao",
    "q5_local": {"lat": -11.314537, "lon": -41.814958, "nome": "Irecê, BA"},
    "q8_texto": "milho e feijão de novembro a março",
    "q8_culturas": [
        {"cultura_id": "milho", "texto_original": "milho", "inicio_mes": 11, "fim_mes": 3},
        {"cultura_id": "feijao", "texto_original": "feijão", "inicio_mes": 11, "fim_mes": 3},
    ],
}


# --- dublês ---


def chamada(nome: str, **args) -> types.GenerateContentResponse:
    parte = types.Part(function_call=types.FunctionCall(name=nome, args=args), thought_signature=b"assinatura-\xff\x00")
    return types.GenerateContentResponse(candidates=[types.Candidate(content=types.Content(role="model", parts=[parte]))])


def fala(texto: str) -> types.GenerateContentResponse:
    return types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=[types.Part(text=texto)]))],
        usage_metadata=types.GenerateContentResponseUsageMetadata(prompt_token_count=100, candidates_token_count=7),
    )


class ModeloFalso:
    """Devolve as respostas do roteiro, uma por chamada (a última se repete se `repetir`); guarda o que recebeu."""

    def __init__(self, roteiro: list, repetir: bool = False):
        self.roteiro = list(roteiro)
        self.repetir = repetir
        self.chamadas: list[dict] = []

    def gerar(self, contents, instrucao, ferramentas):
        self.chamadas.append({"contents": [para_json(c) for c in contents], "instrucao": instrucao, "ferramentas": ferramentas})
        item = self.roteiro[0] if self.repetir else self.roteiro.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class ClienteFalso:
    """Série sintética de 1991 até o fim pedido."""

    def __init__(self, erro: bool = False):
        self.erro = erro
        self.chamadas = 0

    def serie_diaria(self, lat, lon, inicio, fim) -> SeriePower:
        self.chamadas += 1
        if self.erro:
            raise ErroNasaPower("fora do ar")
        dias, d = [], inicio
        while d <= fim:
            dias.append(DiaPower(data=d, t2m=22.0, tmax=30.0, tmin=15.0, chuva=12.0 if d.toordinal() % 2 else 0.0, ur=70.0, radiacao=20.0, vento=2.0))
            d += timedelta(days=1)
        return SeriePower(lat=lat, lon=lon, elevacao_m=800.0, dias=dias)


class EmbedderFalso:
    def documentos(self, textos):
        return [self.consulta(t) for t in textos]

    def consulta(self, texto):
        return [1.0] + [0.0] * 767


@pytest.fixture(autouse=True)
def limpa_overrides(monkeypatch):
    monkeypatch.setattr(agente_service, "_hoje", lambda: date(2026, 11, 14))
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def modelo():
    def instala(roteiro, repetir=False) -> ModeloFalso:
        m = ModeloFalso(roteiro, repetir)
        app.dependency_overrides[get_modelo] = lambda: m
        return m

    return instala


@pytest.fixture
def clima():
    c = ClienteFalso()
    app.dependency_overrides[get_cliente] = lambda: c
    return c


@pytest.fixture
def busca_falsa():
    """Busca de verdade no banco de teste (vazio), com embedder falso."""

    def provedor(repositorio: ConhecimentoRepository = Depends()):
        return lambda: BuscaConhecimentoService(repositorio, EmbedderFalso())

    app.dependency_overrides[provedor_de_busca] = provedor


@pytest.fixture
def fazenda(client, auth):
    r = client.put("/fazenda", headers=auth, json={"respostas": IRECE, "concluir": True})
    assert r.status_code == 200
    return r.json()


@pytest.fixture
def conversa(client, auth) -> int:
    return client.post("/chat/conversas", headers=auth).json()["id"]


def perguntar(client, auth, conversa_id, texto="oi"):
    return client.post(f"/chat/conversas/{conversa_id}/mensagens", headers=auth, json={"mensagem": texto})


def mensagens_no_banco(conversa_id: int) -> list[dict]:
    with get_engine().connect() as c:
        linhas = c.execute(text("SELECT papel, visivel, texto, conteudo, tokens_entrada, tokens_saida FROM mensagem WHERE conversa_id=:i ORDER BY id"), {"i": conversa_id})
        return [dict(l._mapping) for l in linhas]


def respostas_de_ferramenta(chamadas_do_modelo: list[dict]) -> list[dict]:
    """Os function_response que o modelo recebeu na última chamada."""
    partes = [p for c in chamadas_do_modelo[-1]["contents"] for p in c["parts"] if "function_response" in p]
    return [p["function_response"] for p in partes]


# --- rotas ---


def test_exigem_token(client):
    for metodo, url in [("get", "/chat/conversas"), ("post", "/chat/conversas"), ("get", "/chat/conversas/1"), ("delete", "/chat/conversas/1")]:
        assert getattr(client, metodo)(url).status_code == 401
    assert client.post("/chat/conversas/1/mensagens", json={"mensagem": "oi"}).status_code == 401


def test_criar_listar_abrir_apagar(client, auth):
    assert client.get("/chat/conversas", headers=auth).json() == []

    a = client.post("/chat/conversas", headers=auth)
    assert a.status_code == 201
    assert set(a.json()) == {"id", "titulo", "criada_em", "atualizada_em"}
    assert a.json()["titulo"] is None
    assert a.json()["criada_em"].endswith(("Z", "+00:00"))
    b = client.post("/chat/conversas", headers=auth).json()

    lista = client.get("/chat/conversas", headers=auth).json()
    assert [c["id"] for c in lista] == [b["id"], a.json()["id"]]  # mais recente primeiro

    aberta = client.get(f"/chat/conversas/{b['id']}", headers=auth).json()
    assert aberta["mensagens"] == [] and aberta["id"] == b["id"]

    assert client.delete(f"/chat/conversas/{b['id']}", headers=auth).status_code == 204
    r = client.get(f"/chat/conversas/{b['id']}", headers=auth)
    assert r.status_code == 404 and r.json() == {"detail": "Conversa não encontrada."}
    assert client.delete(f"/chat/conversas/{b['id']}", headers=auth).status_code == 404


def test_conversa_de_outro_usuario_e_404_igual_a_inexistente(client, auth, modelo, conversa):
    outro = client.post("/auth/register", json={"nome": "Beto", "email": "beto@exemplo.com", "senha": "segredo123"}).json()["token"]
    h = {"Authorization": f"Bearer {outro}"}
    m = modelo([fala("não deveria chamar")])
    esperado = {"detail": "Conversa não encontrada."}
    for r in (
        client.get(f"/chat/conversas/{conversa}", headers=h),
        perguntar(client, h, conversa),
        client.delete(f"/chat/conversas/{conversa}", headers=h),
        client.get("/chat/conversas/999999", headers=h),
    ):
        assert r.status_code == 404 and r.json() == esperado
    assert m.chamadas == []
    assert client.get("/chat/conversas", headers=h).json() == []
    assert client.get(f"/chat/conversas/{conversa}", headers=auth).status_code == 200  # a do dono segue intacta


def test_mensagem_vazia_ou_longa_demais_da_422(client, auth, conversa, modelo):
    m = modelo([fala("x")])
    for texto in ["", "   ", "x" * 2001]:
        assert perguntar(client, auth, conversa, texto).status_code == 422
    assert client.post(f"/chat/conversas/{conversa}/mensagens", headers=auth, json={}).status_code == 422
    assert m.chamadas == []
    assert perguntar(client, auth, conversa, "x" * 2000).status_code == 200


def test_titulo_corta_em_palavra():
    assert titulo_da_pergunta("  vai dar geada   aqui? ") == "vai dar geada aqui?"
    longa = "quanto chove em janeiro na minha terra e se vale a pena plantar sorgo depois do milho safrinha"
    t = titulo_da_pergunta(longa)
    assert len(t) <= 60 and longa.startswith(t) and longa[len(t)] == " "
    assert titulo_da_pergunta("a" * 100) == "a" * 60  # sem espaço: corta seco


def test_fonte_longa_e_cortada_em_palavra():
    from app.services.agente.ferramentas import _corta

    assert _corta("curto", 150) == "curto"
    assert _corta("Embrapa Milho e Sorgo, Sistemas de Produção (temp. ótima; frio", 40) == "Embrapa Milho e Sorgo, Sistemas de…"


def test_apagar_conta_leva_as_conversas(client, auth, conversa):
    assert client.delete("/me", headers=auth).status_code == 204
    with get_engine().connect() as c:
        assert c.execute(text("SELECT count(*) FROM conversa")).scalar() == 0


# --- agente ---


def test_resposta_direta_sem_ferramenta(client, auth, conversa, modelo):
    m = modelo([fala("Veranico é um período seco no meio da chuva.")])
    r = perguntar(client, auth, conversa, "o que é veranico?")
    assert r.status_code == 200
    corpo = r.json()
    assert set(corpo) == {"id", "papel", "texto", "fontes", "ferramentas_usadas", "criada_em"}
    assert corpo["papel"] == "assistente" and corpo["fontes"] == [] and corpo["ferramentas_usadas"] == []
    assert corpo["texto"].startswith("Veranico")

    aberta = client.get(f"/chat/conversas/{conversa}", headers=auth).json()
    assert aberta["titulo"] == "o que é veranico?"
    assert [(x["papel"], x["texto"][:8]) for x in aberta["mensagens"]] == [("produtor", "o que é "), ("assistente", "Veranico")]
    assert aberta["atualizada_em"] >= aberta["criada_em"]

    linhas = mensagens_no_banco(conversa)
    assert [(l["papel"], l["visivel"]) for l in linhas] == [("user", True), ("model", True)]
    assert (linhas[1]["tokens_entrada"], linhas[1]["tokens_saida"]) == (100, 7)
    assert [t.name for t in m.chamadas[0]["ferramentas"][0].function_declarations] == ["ver_ficha", "info_cultura", "buscar_conhecimento", "consultar_clima"]


def test_clima_ferramenta_depois_resposta(client, auth, conversa, fazenda, clima, modelo):
    m = modelo([chamada("consultar_clima"), fala("Em janeiro chove bem (NASA POWER, média 1991–2020).")])
    r = perguntar(client, auth, conversa, "quanto chove em janeiro na minha terra?")
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["ferramentas_usadas"] == ["consultar_clima"]
    assert len(corpo["fontes"]) == 1
    fonte = corpo["fontes"][0]
    assert (fonte["tipo"], fonte["titulo"]) == ("clima", "NASA POWER")
    assert "1991–2020" in fonte["detalhe"] and "50 km" in fonte["detalhe"]

    # o modelo recebeu o clima com período e escala, sem coordenada
    (resposta,) = respostas_de_ferramenta(m.chamadas)
    dados = resposta["response"]
    assert resposta["name"] == "consultar_clima" and dados["periodo"] == "1991–2020" and len(dados["meses"]) == 12
    assert "50 km" in dados["escala"] and "-11.5" not in json.dumps(dados)
    assert dados["meses"][0]["mes"] == 1 and dados["meses"][0]["chuva_mm"] > 0

    # no banco: pergunta e resposta final visíveis; a chamada e o resultado da ferramenta, não
    linhas = mensagens_no_banco(conversa)
    assert [(l["papel"], l["visivel"]) for l in linhas] == [("user", True), ("model", False), ("user", False), ("model", True)]
    assert "function_call" in linhas[1]["conteudo"]["parts"][0]
    assert "function_response" in linhas[2]["conteudo"]["parts"][0]
    # a conversa aberta mostra só as visíveis
    aberta = client.get(f"/chat/conversas/{conversa}", headers=auth).json()
    assert [x["papel"] for x in aberta["mensagens"]] == ["produtor", "assistente"]
    assert aberta["mensagens"][1]["fontes"][0]["titulo"] == "NASA POWER"


def test_clima_de_um_ano_e_erro_do_power(client, auth, conversa, fazenda, clima, modelo):
    m = modelo([chamada("consultar_clima", ano=2020), fala("ok")])
    r = perguntar(client, auth, conversa, "e em 2020?")
    dados = respostas_de_ferramenta(m.chamadas)[0]["response"]
    assert dados["tipo"] == "ano" and dados["periodo"] == "2020" and len(dados["meses"]) == 12
    assert r.json()["fontes"][0]["detalhe"].startswith("2020")

    m = modelo([chamada("consultar_clima", ano=2040), fala("sem dado")])
    r = perguntar(client, auth, conversa, "e em 2040?")  # fora do que o POWER tem: ferramenta avisa
    assert "Só há clima de 1991 a 2025" in respostas_de_ferramenta(m.chamadas)[-1]["response"]["erro"]
    assert r.json()["fontes"] == [] and r.json()["ferramentas_usadas"] == ["consultar_clima"]


def test_power_fora_do_ar_a_ferramenta_avisa(client, auth, conversa, fazenda, modelo):
    app.dependency_overrides[get_cliente] = lambda: ClienteFalso(erro=True)
    m = modelo([chamada("consultar_clima"), fala("Não consegui o clima agora.")])
    r = perguntar(client, auth, conversa, "como é o clima?")
    assert r.status_code == 200 and r.json()["fontes"] == []
    assert "Não consegui o clima" in respostas_de_ferramenta(m.chamadas)[0]["response"]["erro"]


def test_fazenda_sem_localizacao(client, auth, conversa, clima, modelo):
    client.put("/fazenda", headers=auth, json={"respostas": {"q1_quem": "produtor"}})  # sem q5_local
    m = modelo([chamada("consultar_clima"), fala("Falta o local da sua terra.")])
    r = perguntar(client, auth, conversa, "quanto chove aqui?")
    assert r.status_code == 200
    assert respostas_de_ferramenta(m.chamadas)[0]["response"]["erro"] == "sem_localizacao"
    assert r.json()["fontes"] == [] and r.json()["ferramentas_usadas"] == ["consultar_clima"]
    assert clima.chamadas == 0


def test_sem_fazenda_nenhuma(client, auth, conversa, clima, modelo):
    m = modelo([chamada("ver_ficha"), chamada("consultar_clima"), fala("Preencha a ficha.")])
    r = perguntar(client, auth, conversa, "oi")
    assert r.status_code == 200 and r.json()["fontes"] == []
    assert clima.chamadas == 0


def test_historico_da_segunda_pergunta_leva_os_turnos_de_ferramenta(client, auth, conversa, fazenda, clima, modelo):
    modelo([chamada("consultar_clima"), fala("resposta 1")])
    perguntar(client, auth, conversa, "primeira")
    m = modelo([fala("resposta 2")])
    assert perguntar(client, auth, conversa, "segunda").status_code == 200

    enviado = m.chamadas[0]["contents"]
    assert [c["role"] for c in enviado] == ["user", "model", "user", "model", "user"]
    assert enviado[0]["parts"][0]["text"] == "primeira"
    assert enviado[1]["parts"][0]["function_call"]["name"] == "consultar_clima"
    assert enviado[2]["parts"][0]["function_response"]["name"] == "consultar_clima"
    assert enviado[3]["parts"][0]["text"] == "resposta 1"
    assert enviado[4]["parts"][0]["text"] == "segunda"
    # a assinatura do modelo volta exatamente como veio (bytes)
    assert de_json(enviado[1]).parts[0].thought_signature == b"assinatura-\xff\x00"
    assert [x["papel"] for x in client.get(f"/chat/conversas/{conversa}", headers=auth).json()["mensagens"]] == ["produtor", "assistente"] * 2


def test_historico_limita_as_visiveis(client, auth, conversa, modelo):
    modelo([fala(f"r{i}") for i in range(15)])
    for i in range(12):
        perguntar(client, auth, conversa, f"p{i}")
    m = modelo([fala("fim")])
    perguntar(client, auth, conversa, "ultima")
    enviado = m.chamadas[0]["contents"]
    assert len(enviado) == 21  # 20 visíveis (10 pares) + a pergunta nova
    assert enviado[0]["role"] == "user" and enviado[0]["parts"][0]["text"] == "p2"


def test_estourar_as_rodadas_da_503_e_nao_grava(client, auth, conversa, fazenda, clima, modelo):
    m = modelo([chamada("ver_ficha")], repetir=True)
    r = perguntar(client, auth, conversa, "nunca para")
    assert r.status_code == 503
    assert r.json() == {"detail": "O assistente está fora do ar agora. Tente de novo em alguns minutos."}
    assert len(m.chamadas) == agente_service.MAX_RODADAS_FERRAMENTA + 1
    assert mensagens_no_banco(conversa) == []
    assert client.get(f"/chat/conversas/{conversa}", headers=auth).json()["titulo"] is None


def test_sem_chave_da_503(client, auth, conversa):
    get_modelo.cache_clear()  # modelo de verdade, sem GEMINI_API_KEY no ambiente de teste
    r = perguntar(client, auth, conversa, "oi")
    assert r.status_code == 503 and "fora do ar" in r.json()["detail"]
    assert mensagens_no_banco(conversa) == []


def test_erro_do_gemini_da_503_e_depois_funciona(client, auth, conversa, modelo):
    modelo([RuntimeError("429 cota"), fala("agora foi")])
    assert perguntar(client, auth, conversa, "oi").status_code == 503
    assert mensagens_no_banco(conversa) == []
    r = perguntar(client, auth, conversa, "oi de novo")
    assert r.status_code == 200 and r.json()["texto"] == "agora foi"
    assert len(mensagens_no_banco(conversa)) == 2  # sem pergunta órfã da tentativa que falhou


def test_resposta_vazia_do_modelo_da_503(client, auth, conversa, modelo):
    modelo([types.GenerateContentResponse(candidates=[])])
    assert perguntar(client, auth, conversa, "oi").status_code == 503
    assert mensagens_no_banco(conversa) == []


def test_ver_ficha_nao_vaza_nome_email_nem_local_exato(client, auth, conversa, fazenda, modelo):
    m = modelo([chamada("ver_ficha"), fala("ok")])
    r = perguntar(client, auth, conversa, "o que você sabe da minha fazenda?")
    assert r.json()["fontes"] == [{"tipo": "fazenda", "titulo": "Respostas da sua fazenda", "detalhe": None}]
    resposta = respostas_de_ferramenta(m.chamadas)[0]["response"]
    bruto = json.dumps(resposta, ensure_ascii=False)
    for proibido in ("Marta", "marta@", "Irecê", "-11.31", "-41.81"):
        assert proibido not in bruto
    assert resposta["local_aproximado"] == {"lat": -11.3, "lon": -41.8}
    assert [c["cultura"] for c in resposta["calendario"]] == ["milho", "feijao"]
    assert resposta["respostas"]["q6_irrigacao"] == "nao" and resposta["papel"] == "produtor"
    # a instrução também não leva nome nem e-mail
    assert "Marta" not in m.chamadas[0]["instrucao"] and "marta@" not in m.chamadas[0]["instrucao"]


def test_instrucao_tem_data_idioma_e_resumo(client, auth, conversa, fazenda, modelo):
    m = modelo([fala("ok")])
    perguntar(client, auth, conversa, "oi")
    instrucao = m.chamadas[0]["instrucao"]
    assert "14/11/2026" in instrucao and "(pt)" in instrucao
    assert "milho (nov–mar)" in instrucao and "sequeiro" in instrucao and "hemisfério sul" in instrucao
    assert "-11" not in instrucao  # sem coordenada


def test_info_cultura(client, auth, conversa, modelo):
    m = modelo([chamada("info_cultura", cultura="sorgo"), chamada("info_cultura", cultura="Sorgo"), fala("ok")])
    r = perguntar(client, auth, conversa, "vale a pena plantar sorgo?")
    ferramentas = respostas_de_ferramenta(m.chamadas)
    sorgo = ferramentas[0]["response"]
    assert sorgo["encontrada"] and sorgo["id"] == "sorgo"
    assert sorgo["parametros"]["ciclo_dias_min"] == 90 and sorgo["parametros"]["sensivel_geada"] is True
    assert sorgo["parametros"]["confianca_parametros"] == "alta"
    # fonte repetida entra uma vez só; a ferramenta também
    assert len(r.json()["fontes"]) == 1 and r.json()["fontes"][0]["tipo"] == "cultura"
    assert r.json()["fontes"][0]["titulo"] == "Base de culturas: Sorgo"
    assert r.json()["ferramentas_usadas"] == ["info_cultura"]


def test_cultura_fora_da_base(client, auth, conversa, modelo):
    m = modelo([chamada("info_cultura", cultura="jambu"), fala("Não está na base.")])
    r = perguntar(client, auth, conversa, "e o jambu?")
    resposta = respostas_de_ferramenta(m.chamadas)[0]["response"]
    assert resposta["encontrada"] is False and "não está na base" in resposta["mensagem"]
    assert "parametros" not in resposta and r.json()["fontes"] == []


def test_buscar_conhecimento_registra_conversa_no_log(client, auth, conversa, busca_falsa, modelo):
    m = modelo([chamada("buscar_conhecimento", consulta="veranico definição", expressao_original="veranico"), fala("Não achei.")])
    r = perguntar(client, auth, conversa, "o que é veranico?")
    assert r.status_code == 200 and r.json()["fontes"] == [] and r.json()["ferramentas_usadas"] == ["buscar_conhecimento"]
    assert respostas_de_ferramenta(m.chamadas)[0]["response"]["trechos"] == []  # base de teste vazia
    with get_engine().connect() as c:
        linha = c.execute(text("SELECT conversa_id, consulta, expressao_original FROM busca_log")).one()
    assert (linha.conversa_id, linha.consulta, linha.expressao_original) == (conversa, "veranico definição", "veranico")

    client.delete(f"/chat/conversas/{conversa}", headers=auth)
    with get_engine().connect() as c:  # a busca fica registrada, sem a conversa
        assert c.execute(text("SELECT conversa_id FROM busca_log")).scalar() is None


def test_buscar_conhecimento_com_trecho_vira_fonte(client, auth, conversa, modelo):
    from app.repositories.conhecimento_repository import TrechoEncontrado

    class BuscaFixa:
        def buscar(self, consulta, expressao_original=None, tipo=None, conversa_id=None):
            return [TrechoEncontrado(1, "Glossário do produtor", "glossario", None, None, "Veranico", "Veranico é um período seco.", 0.03, 0.8, True)]

    app.dependency_overrides[provedor_de_busca] = lambda: (lambda: BuscaFixa())
    m = modelo([chamada("buscar_conhecimento", consulta="veranico"), fala("Veranico é um período seco.")])
    r = perguntar(client, auth, conversa, "veranico?")
    assert r.json()["fontes"] == [{"tipo": "conhecimento", "titulo": "Glossário do produtor", "detalhe": "Veranico"}]
    assert respostas_de_ferramenta(m.chamadas)[0]["response"]["trechos"][0]["texto"] == "Veranico é um período seco."


def test_conhecimento_leva_no_maximo_3_trechos(client, auth, conversa, modelo):
    from app.repositories.conhecimento_repository import TrechoEncontrado

    class BuscaCinco:
        def buscar(self, consulta, expressao_original=None, tipo=None, conversa_id=None):
            return [TrechoEncontrado(i, f"Doc {i}", "glossario", None, None, f"Sec {i}", f"texto {i}", 0.03, 0.8, True) for i in range(5)]

    app.dependency_overrides[provedor_de_busca] = lambda: (lambda: BuscaCinco())
    m = modelo([chamada("buscar_conhecimento", consulta="x"), fala("ok")])
    r = perguntar(client, auth, conversa, "x?")
    assert [t["documento"] for t in respostas_de_ferramenta(m.chamadas)[0]["response"]["trechos"]] == ["Doc 0", "Doc 1", "Doc 2"]
    assert [f["titulo"] for f in r.json()["fontes"]] == ["Doc 0", "Doc 1", "Doc 2"]


def test_instrucao_proibe_dizer_que_vale_a_pena(client, auth, conversa, modelo):
    m = modelo([fala("ok")])
    perguntar(client, auth, conversa, "oi")
    instrucao = m.chamadas[0]["instrucao"]
    assert "NUNCA diga que uma cultura ou prática" in instrucao and "vale a pena" in instrucao and "a favor e contra" in instrucao


def test_ferramenta_desconhecida_ou_com_erro_nao_derruba(client, auth, conversa, modelo):
    def quebra():
        raise RuntimeError("sem chave do embedder")

    app.dependency_overrides[provedor_de_busca] = lambda: quebra
    m = modelo([chamada("inventada"), chamada("buscar_conhecimento", consulta="x"), fala("ok")])
    assert perguntar(client, auth, conversa, "oi").status_code == 200
    assert "erro" in respostas_de_ferramenta(m.chamadas)[0]["response"]


def test_conteudo_do_gemini_vai_e_volta_do_json():
    c = types.Content(role="model", parts=[types.Part(function_call=types.FunctionCall(name="x", args={"a": 1}), thought_signature=b"\x00\xff\x10")])
    assert de_json(json.loads(json.dumps(para_json(c)))) == c


def test_instrucao_pede_texto_simples_sem_markdown(client, auth, conversa, modelo):
    m = modelo([fala("ok")])
    perguntar(client, auth, conversa, "oi")
    instrucao = m.chamadas[0]["instrucao"]
    assert "SEM markdown" in instrucao and "linha em branco" in instrucao and '"- "' in instrucao


def test_instrucao_tem_regra_de_escopo_antes_dos_numeros(client, auth, conversa, modelo):
    m = modelo([fala("ok")])
    perguntar(client, auth, conversa, "oi")
    instrucao = m.chamadas[0]["instrucao"]
    assert RESPOSTA_FORA_DO_ESCOPO in instrucao and "1. ESCOPO" in instrucao
    assert "programação e código" in instrucao and "NÃO chame ferramenta" in instrucao
    assert instrucao.index("1. ESCOPO") < instrucao.index("NUNCA inventa número")


def test_fora_do_escopo_responde_a_frase_fixa_sem_ferramenta(client, auth, conversa, modelo):
    m = modelo([fala(RESPOSTA_FORA_DO_ESCOPO)])
    r = perguntar(client, auth, conversa, "como fazer um hello world em python")
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["texto"] == RESPOSTA_FORA_DO_ESCOPO
    assert corpo["fontes"] == [] and corpo["ferramentas_usadas"] == []
    assert len(m.chamadas) == 1
