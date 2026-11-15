"""Busca na base de conhecimento: descarta trecho fraco e registra a busca em busca_log."""
from fastapi import Depends

from app.models import BuscaLog
from app.repositories.conhecimento_repository import ConhecimentoRepository, TrechoEncontrado
from app.services.rag.embeddings import Embedder, get_embedder

LIMITE_DE_TRECHOS = 5

# Cosseno mínimo para aceitar um trecho que só o vetor achou. Calibrado com o gemini-embedding-001
# (relevantes >= 0,65; fora do assunto <= 0,61). Rever quando os textos de data/rag/ entrarem.
SIMILARIDADE_MINIMA = 0.64


class BuscaConhecimentoService:
    def __init__(
        self,
        repositorio: ConhecimentoRepository = Depends(),
        embedder: Embedder = Depends(get_embedder),
    ):
        self.repositorio = repositorio
        self.embedder = embedder

    def buscar(
        self,
        consulta: str,
        expressao_original: str | None = None,
        tipo: str | None = None,
        conversa_id: int | None = None,
    ) -> list[TrechoEncontrado]:
        """`consulta` é o texto reescrito pelo agente; `expressao_original` são as palavras do produtor."""
        vetor = self.embedder.consulta(consulta)
        candidatos = self.repositorio.buscar_hibrido(consulta, vetor, limite=LIMITE_DE_TRECHOS, tipo=tipo)
        aceitos = [t for t in candidatos if self._relevante(t)]

        self.repositorio.registrar_busca(
            BuscaLog(
                conversa_id=conversa_id,
                expressao_original=expressao_original,
                consulta=consulta,
                filtros={"tipo": tipo},
                trechos_ids=[t.trecho_id for t in aceitos],
                notas=[round(t.nota, 5) for t in aceitos],
                descartados=len(candidatos) - len(aceitos),
            )
        )
        return aceitos

    @staticmethod
    def _relevante(trecho: TrechoEncontrado) -> bool:
        # Palavra exata (a busca textual exige todos os termos) vale mesmo com cosseno baixo.
        return trecho.achado_por_palavra or trecho.similaridade >= SIMILARIDADE_MINIMA
