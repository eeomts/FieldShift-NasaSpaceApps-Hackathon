"""Grava as fontes no banco: divide em trechos, gera embeddings e salva. Só reprocessa o que mudou (hash)."""
import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

from fastapi import Depends

from app.core.caminhos import RAIZ_REPO
from app.models import Documento, Trecho
from app.repositories.conhecimento_repository import ConhecimentoRepository
from app.services.rag.chunker import dividir_markdown
from app.services.rag.embeddings import Embedder, get_embedder
from app.services.rag.fontes import FONTES, Fonte

log = logging.getLogger(__name__)


@dataclass
class ResultadoIngestao:
    caminho: str
    situacao: str  # novo | atualizado | sem mudança | arquivo não encontrado | removido
    trechos: int = 0


class IngestaoService:
    def __init__(
        self,
        repositorio: ConhecimentoRepository = Depends(),
        embedder: Embedder = Depends(get_embedder),
    ):
        self.repositorio = repositorio
        self.embedder = embedder

    def ingerir(
        self, fontes: list[Fonte] | None = None, raiz: Path = RAIZ_REPO, forcar: bool = False
    ) -> list[ResultadoIngestao]:
        fontes = FONTES if fontes is None else fontes
        resultados = [self._ingerir_fonte(f, raiz, forcar) for f in fontes]
        # Documento que saiu da lista de fontes sai do banco (arquivo ausente mas ainda listado fica).
        for caminho in self.repositorio.remover_documentos_fora_de([f.caminho for f in fontes]):
            resultados.append(ResultadoIngestao(caminho, "removido"))
        return resultados

    def _ingerir_fonte(self, fonte: Fonte, raiz: Path, forcar: bool) -> ResultadoIngestao:
        arquivo = raiz / fonte.caminho
        if not arquivo.is_file():
            log.warning("fonte não encontrada, pulando: %s", fonte.caminho)
            return ResultadoIngestao(fonte.caminho, "arquivo não encontrado")

        texto = arquivo.read_text(encoding="utf-8")
        hash_atual = hashlib.sha256(texto.encode("utf-8")).hexdigest()
        documento = self.repositorio.documento_por_caminho(fonte.caminho)
        if documento and documento.hash_conteudo == hash_atual and not forcar:
            return ResultadoIngestao(fonte.caminho, "sem mudança", len(documento.trechos))

        # Embeddings antes de mexer no banco: se a API falhar, o documento antigo continua intacto.
        brutos = dividir_markdown(texto)
        # O título da seção entra no texto embutido: ajuda a achar o assunto certo.
        vetores = self.embedder.documentos([f"{b.secao}\n\n{b.conteudo}".strip() for b in brutos])

        situacao = "atualizado" if documento else "novo"
        if documento is None:
            documento = Documento(caminho_origem=fonte.caminho)
        documento.titulo = fonte.titulo
        documento.tipo = fonte.tipo
        documento.fonte = fonte.fonte
        documento.url = fonte.url
        documento.licenca = fonte.licenca
        documento.idioma = fonte.idioma
        documento.hash_conteudo = hash_atual
        documento.trechos.clear()  # apaga os trechos antigos (delete-orphan)
        documento.trechos.extend(
            Trecho(
                ordem=b.ordem,
                secao=b.secao[:300] or None,
                conteudo=b.conteudo,
                embedding=v,
                tokens=b.tokens_estimados,
                metadados={},
            )
            for b, v in zip(brutos, vetores, strict=True)
        )
        self.repositorio.salvar_documento(documento)
        return ResultadoIngestao(fonte.caminho, situacao, len(brutos))
