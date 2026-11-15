"""PUT /fazenda e a busca do SoilGrids em segundo plano: status, retrato com a fusão e quando não chama de novo (cliente falso)."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.db import get_engine
from app.models import Fazenda
from solo_helpers import ERRO, ClienteFalso, resposta_urbana

RIO_VERDE = {"lat": -17.644301, "lon": -51.080503}
PASSO_FUNDO = {"lat": -28.310532, "lon": -52.412854}


def put(client, auth, local=RIO_VERDE, **respostas):
    corpo = {"respostas": ({"q5_local": local} if local else {}) | respostas}
    r = client.put("/fazenda", headers=auth, json=corpo)
    assert r.status_code == 200, r.text
    return r.json()


def lido(client, auth) -> dict:
    return client.get("/fazenda", headers=auth).json()


def mexer_no_banco(**colunas):
    with Session(get_engine()) as s:
        s.execute(update(Fazenda).values(**colunas))
        s.commit()


def test_put_nao_espera_o_soilgrids_responde_processando_e_depois_fica_pronto(client, auth, cliente_solo):
    f = put(client, auth, q13_textura="argilosa")
    assert f["status_processamento"] == "processando"  # a resposta saiu antes da busca
    assert f["retrato_solo"]["soilgrids"] is None
    assert [a["atributo"] for a in f["retrato_solo"]["sintese"]] == ["textura", "materia_organica", "acidez"]
    assert f["retrato_solo"]["sintese"][0]["evidencias"][0]["fonte"] == "produtor"  # por enquanto, só o que o produtor contou

    f = lido(client, auth)  # a tarefa já rodou
    assert f["status_processamento"] == "pronto"
    r = f["retrato_solo"]
    assert r["soilgrids"]["classe_textural"] == "argilosa" and r["soilgrids"]["sem_dado"] is False
    textura = r["sintese"][0]
    assert textura["valor"] == "argilosa" and textura["confianca"] == "alta"  # produtor (0,5) + mapa (0,4)
    assert [e["fonte"] for e in textura["evidencias"]] == ["produtor", "soilgrids"]
    assert cliente_solo.pontos == [(RIO_VERDE["lat"], RIO_VERDE["lon"])]


def test_o_contrato_do_retrato(client, auth):
    put(client, auth)
    r = lido(client, auth)["retrato_solo"]
    assert set(r) == {"fonte", "indicadores", "figuras", "sintese", "soilgrids"}
    assert set(r["soilgrids"]) == {
        "argila_pct", "areia_pct", "silte_pct", "carbono_g_kg", "materia_organica_g_kg", "ph", "ctc_cmol_kg",
        "densidade_g_cm3", "classe_textural", "k_usle", "incerteza", "camada", "fonte", "sem_dado",
    }  # fmt: skip
    assert set(r["sintese"][0]) == {"atributo", "valor", "confianca", "evidencias", "divergencia"}
    assert set(r["sintese"][0]["evidencias"][0]) == {"fonte", "valor", "peso", "texto"}


def test_a_busca_roda_com_o_banco_no_estado_processando(client, auth, cliente_solo, monkeypatch):
    vistos = []

    class Espiao(ClienteFalso):
        def propriedade(self, lat, lon, nome):
            with Session(get_engine()) as s:
                vistos.append(s.scalars(select(Fazenda.status_processamento)).one())
            return super().propriedade(lat, lon, nome)

    espiao = Espiao()
    monkeypatch.setattr("app.services.solo.processamento.get_cliente", lambda: espiao)
    put(client, auth)
    assert vistos and set(vistos) == {"processando"}


def test_falha_do_soilgrids_marca_erro_e_o_retrato_fica_so_com_o_produtor(client, auth, cliente_solo):
    cliente_solo.resposta = ERRO
    assert put(client, auth, q13_textura="media")["status_processamento"] == "processando"
    f = lido(client, auth)
    assert f["status_processamento"] == "erro"
    assert f["retrato_solo"]["soilgrids"] is None
    assert f["retrato_solo"]["sintese"][0]["valor"] == "media"
    assert [e["fonte"] for e in f["retrato_solo"]["sintese"][0]["evidencias"]] == ["produtor"]


def test_excecao_inesperada_na_busca_tambem_vira_erro_e_nao_prende_em_processando(client, auth, cliente_solo):
    cliente_solo.resposta = RuntimeError("bug")
    put(client, auth)
    assert lido(client, auth)["status_processamento"] == "erro"


def test_ponto_urbano_fica_pronto_com_sem_dado(client, auth, cliente_solo):
    cliente_solo.resposta = resposta_urbana()
    put(client, auth, local={"lat": -23.5505, "lon": -46.6333}, q13_textura="argilosa")
    f = lido(client, auth)
    assert f["status_processamento"] == "pronto"
    assert f["retrato_solo"]["soilgrids"]["sem_dado"] is True and f["retrato_solo"]["soilgrids"]["argila_pct"] is None
    assert f["retrato_solo"]["sintese"][0]["valor"] == "argilosa"  # só o produtor


def test_sem_local_fica_pendente_e_nao_chama_o_soilgrids(client, auth, cliente_solo):
    f = put(client, auth, local=None, q13_textura="media")
    assert f["status_processamento"] == "pendente"
    assert lido(client, auth)["status_processamento"] == "pendente"
    assert cliente_solo.chamadas == []


def test_mesmo_local_ja_processado_nao_chama_de_novo_mas_refaz_o_retrato(client, auth, cliente_solo):
    put(client, auth, q13_textura="argilosa")
    assert lido(client, auth)["status_processamento"] == "pronto"

    f = put(client, auth, q13_textura="arenosa")  # só mudou a resposta
    assert f["status_processamento"] == "pronto"  # nada a esperar
    assert f["retrato_solo"]["soilgrids"]["classe_textural"] == "argilosa"  # o mapa continua no retrato
    textura = f["retrato_solo"]["sintese"][0]
    assert textura["valor"] == "arenosa" and textura["divergencia"].startswith("O mapa global sugere terra argilosa, mas você observou terra arenosa.")
    assert len(cliente_solo.pontos) == 1


def test_local_novo_busca_de_novo_e_descarta_o_mapa_do_local_antigo(client, auth, cliente_solo):
    put(client, auth)
    f = put(client, auth, local=PASSO_FUNDO)
    assert f["status_processamento"] == "processando" and f["retrato_solo"]["soilgrids"] is None
    assert lido(client, auth)["status_processamento"] == "pronto"
    assert cliente_solo.pontos == [(RIO_VERDE["lat"], RIO_VERDE["lon"]), (PASSO_FUNDO["lat"], PASSO_FUNDO["lon"])]


def test_fazenda_com_local_e_sem_mapa_no_retrato_busca_na_proxima_gravacao(client, auth, cliente_solo):
    put(client, auth)
    mexer_no_banco(retrato_solo={"fonte": "produtor", "indicadores": [], "figuras": None}, status_processamento="pendente")  # como as de antes
    assert put(client, auth)["status_processamento"] == "processando"
    f = lido(client, auth)
    assert f["status_processamento"] == "pronto" and f["retrato_solo"]["soilgrids"] is not None
    assert len(cliente_solo.pontos) == 1  # o ponto já estava no cache do banco: a API não é chamada de novo


def test_busca_em_andamento_nao_agenda_outra(client, auth, cliente_solo):
    put(client, auth)
    mexer_no_banco(retrato_solo={}, status_processamento="processando")  # simula a busca ainda rodando
    cliente_solo.chamadas.clear()
    f = put(client, auth, q13_textura="media")
    assert f["status_processamento"] == "processando"
    assert cliente_solo.chamadas == []  # nenhuma tarefa nova


def test_busca_presa_ha_muito_tempo_tenta_de_novo(client, auth, cliente_solo):
    put(client, auth)
    antigo = datetime.now(timezone.utc) - timedelta(hours=1)
    mexer_no_banco(retrato_solo={}, status_processamento="processando", atualizado_em=antigo)
    assert put(client, auth)["status_processamento"] == "processando"
    assert lido(client, auth)["status_processamento"] == "pronto"


def test_erro_recente_nao_insiste_a_cada_gravacao(client, auth, cliente_solo):
    cliente_solo.resposta = ERRO
    put(client, auth)
    assert lido(client, auth)["status_processamento"] == "erro"
    n = len(cliente_solo.chamadas)
    assert put(client, auth, q13_textura="media")["status_processamento"] == "erro"
    assert len(cliente_solo.chamadas) == n


def test_se_o_local_mudou_durante_a_busca_a_tarefa_antiga_nao_mexe_na_fazenda(client, auth, monkeypatch):
    class MudaDeLocal(ClienteFalso):
        def propriedade(self, lat, lon, nome):
            mexer_no_banco(lat=PASSO_FUNDO["lat"], lon=PASSO_FUNDO["lon"], status_processamento="processando")
            return super().propriedade(lat, lon, nome)

    monkeypatch.setattr("app.services.solo.processamento.get_cliente", lambda: MudaDeLocal())
    put(client, auth)
    f = lido(client, auth)
    assert f["status_processamento"] == "processando"  # quem cuida do novo local é a tarefa dele
    assert f["retrato_solo"]["soilgrids"] is None


# --- resultado parcial, retomada e "processando" preso ---


def test_falha_em_uma_propriedade_ainda_fica_pronto_se_veio_a_textura(client, auth, cliente_solo):
    cliente_solo.falhas = {"soc"}
    put(client, auth, q13_textura="argilosa")
    f = lido(client, auth)
    assert f["status_processamento"] == "pronto"
    mapa = f["retrato_solo"]["soilgrids"]
    assert mapa["argila_pct"] == 40.0 and mapa["classe_textural"] == "argilosa" and mapa["ph"] == 5.5
    assert mapa["carbono_g_kg"] is None and mapa["materia_organica_g_kg"] is None and mapa["k_usle"] is None
    sintese = {a["atributo"]: a for a in f["retrato_solo"]["sintese"]}
    assert sintese["textura"]["valor"] == "argilosa" and sintese["acidez"]["valor"] == "media"
    assert sintese["materia_organica"]["valor"] is None  # sem carbono, sem matéria orgânica do mapa


def test_sem_a_textura_fica_erro_mas_o_que_veio_entra_no_retrato(client, auth, cliente_solo):
    cliente_solo.falhas = {"clay"}
    put(client, auth)
    f = lido(client, auth)
    assert f["status_processamento"] == "erro"
    mapa = f["retrato_solo"]["soilgrids"]
    assert mapa["argila_pct"] is None and mapa["classe_textural"] is None and mapa["ph"] == 5.5
    sintese = {a["atributo"]: a for a in f["retrato_solo"]["sintese"]}
    assert sintese["acidez"]["valor"] == "media" and sintese["acidez"]["confianca"] == "baixa"  # só o pH: acidez sai
    assert sintese["textura"]["valor"] is None  # textura não


def test_a_proxima_busca_so_pede_o_que_faltou_e_fica_pronto(client, auth, cliente_solo):
    cliente_solo.falhas = {"clay"}
    put(client, auth)
    assert lido(client, auth)["status_processamento"] == "erro"
    cliente_solo.falhas = set()
    cliente_solo.chamadas.clear()
    mexer_no_banco(atualizado_em=datetime.now(timezone.utc) - timedelta(hours=1))  # o erro já não é recente
    assert put(client, auth)["status_processamento"] == "processando"
    assert cliente_solo.pedidas() == ["clay"]
    f = lido(client, auth)
    assert f["status_processamento"] == "pronto" and f["retrato_solo"]["soilgrids"]["classe_textural"] == "argilosa"


def test_pronto_so_com_a_textura_nao_busca_o_resto_a_cada_gravacao(client, auth, cliente_solo):
    cliente_solo.falhas = {"soc"}
    put(client, auth)
    cliente_solo.chamadas.clear()
    assert put(client, auth, q13_textura="media")["status_processamento"] == "pronto"
    assert cliente_solo.chamadas == []


def test_processando_ha_mais_de_15_minutos_o_get_devolve_erro(client, auth):
    put(client, auth)
    mexer_no_banco(status_processamento="processando", atualizado_em=datetime.now(timezone.utc) - timedelta(minutes=16))
    assert lido(client, auth)["status_processamento"] == "erro"
    mexer_no_banco(atualizado_em=datetime.now(timezone.utc) - timedelta(minutes=14))
    assert lido(client, auth)["status_processamento"] == "processando"  # ainda dentro do prazo


def test_depois_de_preso_a_proxima_gravacao_reagenda(client, auth, cliente_solo):
    put(client, auth)
    mexer_no_banco(retrato_solo={}, status_processamento="processando", atualizado_em=datetime.now(timezone.utc) - timedelta(minutes=20))
    assert lido(client, auth)["status_processamento"] == "erro"
    assert put(client, auth)["status_processamento"] == "processando"
    assert lido(client, auth)["status_processamento"] == "pronto"


def test_prazo_do_processando_preso_e_constante_nomeada():
    from app.services.onboarding.fazenda_service import PROCESSANDO_PRESO

    assert PROCESSANDO_PRESO == timedelta(minutes=15)
