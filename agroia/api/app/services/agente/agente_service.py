"""O agente: laço do Gemini com as ferramentas executadas aqui (chamada automática desligada) e gravação da rodada."""
import json
import logging
from collections.abc import Callable
from datetime import UTC, date, datetime

from fastapi import Depends
from google.genai import types

from app.core.erros import ErroDeNegocio
from app.models import Mensagem, Usuario
from app.repositories.conhecimento_repository import ConhecimentoRepository
from app.repositories.conversa_repository import ConversaRepository
from app.schemas.chat import Fonte, MensagemOut
from app.services.agente.busca_conhecimento_service import BuscaConhecimentoService
from app.services.agente.ferramentas import DECLARACOES, Ferramentas
from app.services.agente.modelo import ModeloIA, get_modelo
from app.services.agente.prompt import montar_instrucao
from app.services.clima.clima_service import ClimaService
from app.services.conversa_service import ConversaService, mensagem_para_saida, titulo_da_pergunta
from app.services.rag.embeddings import get_embedder

log = logging.getLogger(__name__)

MAX_RODADAS_FERRAMENTA = 5
HISTORICO_VISIVEIS = 20
FORA_DO_AR = "O assistente está fora do ar agora. Tente de novo em alguns minutos."


def provedor_de_busca(
    repositorio: ConhecimentoRepository = Depends(),
) -> Callable[[], BuscaConhecimentoService]:
    """A busca só cria o embedder (que exige a chave) quando o agente chama a ferramenta."""
    return lambda: BuscaConhecimentoService(repositorio, get_embedder())


def para_json(c: types.Content) -> dict:
    """O Content completo como veio (chamadas, respostas de ferramenta, assinaturas); bytes saem em base64."""
    return json.loads(c.model_dump_json(exclude_none=True))


def de_json(d: dict) -> types.Content:
    return types.Content.model_validate_json(json.dumps(d))


def _comeca_na_pergunta(mensagens: list[Mensagem]) -> list[Mensagem]:
    """O histórico enviado ao Gemini precisa começar numa pergunta do produtor."""
    for i, m in enumerate(mensagens):
        if m.visivel and m.papel == "user":
            return mensagens[i:]
    return []


def _texto(c: types.Content) -> str:
    return "".join(p.text for p in c.parts or [] if p.text and not p.thought).strip()


def _tokens(resp: types.GenerateContentResponse) -> tuple[int | None, int | None]:
    u = resp.usage_metadata
    if u is None:
        return None, None
    saida = (u.candidates_token_count or 0) + (u.thoughts_token_count or 0)
    return u.prompt_token_count, saida or None


def _hoje() -> date:
    return date.today()


class AgenteService:
    def __init__(
        self,
        conversas: ConversaService = Depends(),
        repositorio: ConversaRepository = Depends(),
        modelo: ModeloIA = Depends(get_modelo),
        clima: ClimaService = Depends(),
        busca: Callable[[], BuscaConhecimentoService] = Depends(provedor_de_busca),
    ):
        self.conversas = conversas
        self.repositorio = repositorio
        self.modelo = modelo
        self.clima = clima
        self.busca = busca

    def responder(self, usuario: Usuario, conversa_id: int, texto: str) -> MensagemOut:
        """Roda o agente e grava a rodada inteira de uma vez; se o assistente falhar, não grava nada (503)."""
        conversa = self.conversas.obter_do_usuario(usuario, conversa_id)
        agora = datetime.now(UTC)
        hoje = _hoje()
        instrucao = montar_instrucao(usuario, hoje)
        ferramentas = Ferramentas(usuario, self.clima, self.busca, conversa.id, hoje, ao_falhar=self.repositorio.db.rollback)

        historico = _comeca_na_pergunta(self.repositorio.para_historico(conversa.id, HISTORICO_VISIVEIS))
        contents = [de_json(m.conteudo) for m in historico]
        pergunta = types.Content(role="user", parts=[types.Part(text=texto)])
        contents.append(pergunta)
        novas = [Mensagem(papel="user", conteudo=para_json(pergunta), visivel=True, texto=texto, criada_em=agora)]

        fontes: list[Fonte] = []
        usadas: list[str] = []
        for rodada in range(MAX_RODADAS_FERRAMENTA + 1):
            resposta = self._chamar_modelo(contents, instrucao)
            conteudo = resposta.candidates[0].content if resposta.candidates else None
            if conteudo is None or not conteudo.parts:
                log.warning("Gemini sem conteúdo na resposta")
                raise ErroDeNegocio(503, FORA_DO_AR)
            conteudo.role = "model"
            entrada, saida = _tokens(resposta)
            chamadas = [p.function_call for p in conteudo.parts if p.function_call]

            if not chamadas:
                final = _texto(conteudo)
                if not final:
                    raise ErroDeNegocio(503, FORA_DO_AR)
                novas.append(
                    Mensagem(
                        papel="model", conteudo=para_json(conteudo), visivel=True, texto=final,
                        fontes=[f.model_dump() for f in fontes], ferramentas_usadas=usadas,
                        tokens_entrada=entrada, tokens_saida=saida, criada_em=datetime.now(UTC),
                    )
                )
                break

            if rodada == MAX_RODADAS_FERRAMENTA:
                log.warning("Limite de %s rodadas de ferramenta estourado", MAX_RODADAS_FERRAMENTA)
                raise ErroDeNegocio(503, FORA_DO_AR)

            respostas = []
            for ch in chamadas:
                resultado = ferramentas.executar(ch.name or "", dict(ch.args or {}))
                if ch.name not in usadas:
                    usadas.append(ch.name)
                for f in resultado.fontes:
                    if f not in fontes:
                        fontes.append(f)
                respostas.append(
                    types.Part(function_response=types.FunctionResponse(id=ch.id, name=ch.name, response=resultado.dados))
                )
            retorno = types.Content(role="user", parts=respostas)
            novas.append(
                Mensagem(papel="model", conteudo=para_json(conteudo), tokens_entrada=entrada, tokens_saida=saida, criada_em=datetime.now(UTC))
            )
            novas.append(Mensagem(papel="user", conteudo=para_json(retorno), criada_em=datetime.now(UTC)))
            contents += [conteudo, retorno]

        titulo = titulo_da_pergunta(texto) if conversa.titulo is None else None
        self.repositorio.gravar_rodada(conversa, novas, titulo, novas[-1].criada_em)
        return mensagem_para_saida(novas[-1])

    def _chamar_modelo(self, contents: list[types.Content], instrucao: str) -> types.GenerateContentResponse:
        try:
            return self.modelo.gerar(contents, instrucao, DECLARACOES)
        except Exception as e:  # sem chave, cota, timeout, API fora: o produtor vê o mesmo aviso
            log.warning("Falha ao chamar o Gemini: %s: %s", type(e).__name__, str(e)[:200])
            raise ErroDeNegocio(503, FORA_DO_AR) from None
