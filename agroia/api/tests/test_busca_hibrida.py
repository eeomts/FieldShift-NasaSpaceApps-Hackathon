"""Ingestão e busca híbrida contra o Postgres de teste, com um embedder falso (não gasta API)."""
import math
import re
import zlib
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_engine
from app.models import BuscaLog, Documento, Trecho
from app.models.conhecimento import EMBEDDING_DIM
from app.repositories.conhecimento_repository import ConhecimentoRepository
from app.services.agente.busca_conhecimento_service import SIMILARIDADE_MINIMA, BuscaConhecimentoService
from app.services.rag.fontes import Fonte
from app.services.rag.ingestao import IngestaoService


class EmbedderFalso:
    """Cada palavra acende uma posição do vetor: textos com palavras em comum ficam próximos."""

    def __init__(self):
        self.chamadas_documentos = 0

    @staticmethod
    def _vetor(texto: str) -> list[float]:
        v = [0.0] * EMBEDDING_DIM
        v[0] = 0.01  # evita vetor zerado
        for palavra in re.findall(r"\w+", texto.lower()):
            v[zlib.crc32(palavra.encode()) % (EMBEDDING_DIM - 1) + 1] += 1.0
        norma = math.sqrt(sum(x * x for x in v))
        return [x / norma for x in v]

    def documentos(self, textos: list[str]) -> list[list[float]]:
        self.chamadas_documentos += 1
        return [self._vetor(t) for t in textos]

    def consulta(self, texto: str) -> list[float]:
        return self._vetor(texto)


GLOSSARIO = """# Glossário

## Veranico

Veranico é um período seco no meio da estação chuvosa, que prejudica o milho na floração.

## Solo descoberto

Solo descoberto é a terra sem nenhuma cobertura vegetal depois da colheita, exposta à erosão.
"""

CULTURAS = """# Culturas

## Braquiária

A braquiária cobre o solo na seca, protege contra a erosão e serve de pasto para o gado.
"""

SATELITES = """# Satélites

## NDVI

O NDVI mede quão verde e vigorosa está a vegetação a partir de imagens de satélite.
"""

FONTES = [
    Fonte("glossario.md", "Glossário de teste", "glossario", fonte="Teste"),
    Fonte("culturas.md", "Culturas de teste", "cultura", fonte="Teste"),
    Fonte("satelites.md", "Satélites de teste", "satelite", fonte="Teste"),
]


@pytest.fixture
def db():
    with Session(get_engine(), expire_on_commit=False) as s:
        yield s


@pytest.fixture
def embedder() -> EmbedderFalso:
    return EmbedderFalso()


@pytest.fixture
def raiz(tmp_path: Path) -> Path:
    (tmp_path / "glossario.md").write_text(GLOSSARIO, encoding="utf-8")
    (tmp_path / "culturas.md").write_text(CULTURAS, encoding="utf-8")
    (tmp_path / "satelites.md").write_text(SATELITES, encoding="utf-8")
    return tmp_path


@pytest.fixture
def base(db, embedder, raiz) -> Path:
    """Base já ingerida com os 3 documentos de teste."""
    IngestaoService(ConhecimentoRepository(db), embedder).ingerir(FONTES, raiz)
    return raiz


def _servico(db, embedder) -> BuscaConhecimentoService:
    return BuscaConhecimentoService(ConhecimentoRepository(db), embedder)


def test_ingestao_grava_documentos_e_trechos(db, embedder, raiz):
    resultados = IngestaoService(ConhecimentoRepository(db), embedder).ingerir(FONTES, raiz)
    assert [r.situacao for r in resultados] == ["novo", "novo", "novo"]
    assert db.scalar(select(func.count()).select_from(Documento)) == 3
    assert db.scalar(select(func.count()).select_from(Trecho)) == 4
    doc = db.scalar(select(Documento).where(Documento.caminho_origem == "glossario.md"))
    assert (doc.tipo, doc.fonte, len(doc.hash_conteudo)) == ("glossario", "Teste", 64)


def test_busca_por_palavra_exata_acha_o_trecho(db, embedder, base):
    achados = ConhecimentoRepository(db).buscar_hibrido("veranico", embedder.consulta("veranico"))
    assert achados[0].secao == "Glossário > Veranico"
    assert achados[0].achado_por_palavra is True
    assert achados[0].documento_titulo == "Glossário de teste"
    assert achados[0].fonte == "Teste"
    assert 0 < achados[0].similaridade <= 1
    assert achados[0].nota > 0


def test_filtro_por_tipo(db, embedder, base):
    consulta = "cobertura do solo e erosão"
    achados = ConhecimentoRepository(db).buscar_hibrido(consulta, embedder.consulta(consulta), tipo="cultura")
    assert achados and all(a.documento_tipo == "cultura" for a in achados)
    sem_filtro = ConhecimentoRepository(db).buscar_hibrido(consulta, embedder.consulta(consulta))
    assert {"glossario", "cultura"} <= {a.documento_tipo for a in sem_filtro}


def test_servico_descarta_trecho_fraco(db, embedder, base):
    # Nenhuma palavra em comum com a base: o vetor ainda devolve candidatos, mas todos abaixo do mínimo.
    candidatos = ConhecimentoRepository(db).buscar_hibrido("zzz qqq", embedder.consulta("zzz qqq"))
    assert candidatos and all(c.similaridade < SIMILARIDADE_MINIMA for c in candidatos)

    assert _servico(db, embedder).buscar("zzz qqq") == []
    log = db.scalars(select(BuscaLog).order_by(BuscaLog.id.desc())).first()
    assert log.trechos_ids == [] and log.descartados == len(candidatos)


def test_servico_registra_busca_log(db, embedder, base):
    aceitos = _servico(db, embedder).buscar(
        "solo descoberto depois da colheita", expressao_original="terra pelada dimais dipois q coio", tipo="glossario"
    )
    assert aceitos[0].secao == "Glossário > Solo descoberto"
    log = db.scalars(select(BuscaLog)).one()
    assert log.expressao_original == "terra pelada dimais dipois q coio"
    assert log.consulta == "solo descoberto depois da colheita"
    assert log.filtros == {"tipo": "glossario"}
    assert log.trechos_ids == [t.trecho_id for t in aceitos]
    assert len(log.notas) == len(aceitos) and log.criada_em is not None


def test_reingestao_sem_mudanca_nao_regrava(db, embedder, base):
    ids = set(db.scalars(select(Trecho.id)))
    chamadas = embedder.chamadas_documentos
    resultados = IngestaoService(ConhecimentoRepository(db), embedder).ingerir(FONTES, base)
    assert {r.situacao for r in resultados} == {"sem mudança"}
    assert embedder.chamadas_documentos == chamadas
    assert set(db.scalars(select(Trecho.id))) == ids


def test_reingestao_com_mudanca_regrava_so_o_documento_alterado(db, embedder, base):
    ids_antes = set(db.scalars(select(Trecho.id)))
    novo = CULTURAS.replace("Braquiária", "Capim").replace("braquiária", "capim")
    (base / "culturas.md").write_text(novo, encoding="utf-8")

    resultados = IngestaoService(ConhecimentoRepository(db), embedder).ingerir(FONTES, base)
    situacoes = {r.caminho: r.situacao for r in resultados}
    assert situacoes == {"glossario.md": "sem mudança", "culturas.md": "atualizado", "satelites.md": "sem mudança"}

    db.expire_all()
    ids_depois = set(db.scalars(select(Trecho.id)))
    assert len(ids_depois) == 4 and len(ids_antes & ids_depois) == 3  # só o trecho de culturas foi regravado
    assert db.scalars(select(Trecho.secao).where(Trecho.conteudo.contains("capim"))).all() == ["Culturas > Capim"]


def test_arquivo_inexistente_e_pulado(db, embedder, raiz):
    fontes = FONTES + [Fonte("data/rag/ainda-nao-existe.md", "Futuro", "metodologia")]
    resultados = IngestaoService(ConhecimentoRepository(db), embedder).ingerir(fontes, raiz)
    assert resultados[-1].situacao == "arquivo não encontrado"
    assert db.scalar(select(func.count()).select_from(Documento)) == 3


def test_documento_fora_da_lista_e_removido_com_os_trechos(db, embedder, base):
    resultados = IngestaoService(ConhecimentoRepository(db), embedder).ingerir(FONTES[:2], base)
    assert resultados[-1].situacao == "removido" and resultados[-1].caminho == "satelites.md"
    assert db.scalar(select(func.count()).select_from(Documento)) == 2
    assert db.scalar(select(func.count()).select_from(Trecho)) == 3
