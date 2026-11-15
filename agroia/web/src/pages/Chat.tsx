// Tela do chat: lista de conversas e conversa com o assistente.
import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { abrirConversa, apagarConversa, criarConversa, enviarMensagem, listarConversas } from "../api/chat";
import { ErroApi } from "../api/client";
import type { ConversaResumo, Mensagem } from "../api/tipos";
import { Balao, Pensando } from "../components/chat/Mensagens";
import { Mais, Seta, Voltar } from "../components/icones";
import { Logo } from "../components/Logo";
import { Aviso, BotaoContorno, BotaoPrimario, cx, Texto } from "../components/ui";

const LIMITE = 2000;
const PERTO_DO_LIMITE = 1800;
const SUGESTOES = ["Vai dar geada aqui em julho?", "O que é veranico?", "Quanto chove em janeiro na minha terra?"];

function textoDeErro(e: unknown) {
  return e instanceof ErroApi ? e.message : "Algo deu errado. Tente de novo.";
}

function dataRelativa(iso: string) {
  const d = new Date(/(Z|[+-]\d\d:?\d\d)$/.test(iso) ? iso : `${iso}Z`);
  const min = Math.floor((Date.now() - d.getTime()) / 60000);
  if (min < 1) return "agora";
  if (min < 60) return `há ${min} min`;
  const h = Math.floor(min / 60);
  if (h < 24) return `há ${h} h`;
  const dias = Math.floor(h / 24);
  if (dias === 1) return "ontem";
  if (dias < 7) return `há ${dias} dias`;
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });
}

export function Chat() {
  const [conversas, setConversas] = useState<ConversaResumo[]>([]);
  const [listaCarregando, setListaCarregando] = useState(true);
  const [listaErro, setListaErro] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);

  const [emConversa, setEmConversa] = useState(false); // celular: mostra a conversa em vez da lista
  const [abertaId, setAbertaId] = useState<number | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [abrindo, setAbrindo] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erroEnvio, setErroEnvio] = useState<string | null>(null);
  const [texto, setTexto] = useState("");
  const [confirmando, setConfirmando] = useState(false);
  const [apagando, setApagando] = useState(false);

  const atual = useRef<number | null>(null); // conversa aberta agora (para ignorar respostas atrasadas)
  const fim = useRef<HTMLDivElement>(null);
  const campo = useRef<HTMLTextAreaElement>(null);

  const recarregarLista = useCallback(async () => {
    try {
      setConversas(await listarConversas());
      setListaErro(null);
    } catch (e) {
      setListaErro(textoDeErro(e));
    } finally {
      setListaCarregando(false);
    }
  }, []);

  useEffect(() => {
    void recarregarLista();
  }, [recarregarLista]);

  useEffect(() => {
    fim.current?.scrollIntoView({ block: "end" });
  }, [mensagens, enviando, abrindo, emConversa]);

  useEffect(() => {
    const el = campo.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  }, [texto]);

  function definirAberta(id: number | null) {
    atual.current = id;
    setAbertaId(id);
  }

  function novaConversa() {
    definirAberta(null);
    setMensagens([]);
    setErroEnvio(null);
    setAviso(null);
    setTexto("");
    setConfirmando(false);
    setEmConversa(true);
  }

  async function abrir(id: number) {
    definirAberta(id);
    setMensagens([]);
    setErroEnvio(null);
    setAviso(null);
    setTexto("");
    setConfirmando(false);
    setEmConversa(true);
    setAbrindo(true);
    try {
      const c = await abrirConversa(id);
      if (atual.current === id) setMensagens(c.mensagens);
    } catch (e) {
      if (atual.current !== id) return;
      if (e instanceof ErroApi && e.status === 404) {
        definirAberta(null);
        setEmConversa(false);
        setAviso("Essa conversa não existe mais.");
        void recarregarLista();
      } else {
        setErroEnvio(textoDeErro(e));
      }
    } finally {
      if (atual.current === id || atual.current === null) setAbrindo(false);
    }
  }

  function voltarParaLista() {
    setEmConversa(false);
    setConfirmando(false);
  }

  async function enviar(conteudo: string) {
    const pergunta = conteudo.trim();
    if (!pergunta || enviando || pergunta.length > LIMITE) return;
    setEnviando(true);
    setErroEnvio(null);
    setAviso(null);
    setTexto("");
    const otimista: Mensagem = {
      id: -Date.now(),
      papel: "produtor",
      texto: pergunta,
      fontes: [],
      ferramentas_usadas: [],
      criada_em: new Date().toISOString(),
    };
    setMensagens((ms) => [...ms, otimista]);
    let id = abertaId;
    try {
      if (id === null) {
        id = (await criarConversa()).id;
        definirAberta(id);
        void recarregarLista();
      }
      await enviarMensagem(id, pergunta);
      const c = await abrirConversa(id);
      if (atual.current === id) setMensagens(c.mensagens);
      void recarregarLista();
    } catch (e) {
      if (atual.current === id) {
        setMensagens((ms) => ms.filter((m) => m.id !== otimista.id));
        setErroEnvio(textoDeErro(e));
        setTexto(pergunta);
      }
    } finally {
      setEnviando(false);
    }
  }

  async function apagar() {
    if (abertaId === null) return;
    setApagando(true);
    try {
      await apagarConversa(abertaId);
      setConversas((cs) => cs.filter((c) => c.id !== abertaId));
      definirAberta(null);
      setMensagens([]);
      setConfirmando(false);
      setEmConversa(false);
    } catch (e) {
      setConfirmando(false);
      setErroEnvio(textoDeErro(e));
    } finally {
      setApagando(false);
    }
  }

  const vazia = !abrindo && mensagens.length === 0;

  return (
    <div className="flex h-dvh flex-col">
      <header className="border-b-2 border-linha bg-white/90">
        <div className="mx-auto flex max-w-[1120px] items-center justify-between gap-3 px-4 py-3 lg:px-10">
          <Logo />
          <Link to="/dashboard" className="flex items-center gap-1.5 rounded-xl px-3 py-2 text-[15px] font-bold text-suave hover:bg-terra">
            <Voltar size={18} /> Início
          </Link>
        </div>
      </header>

      <div className="mx-auto flex min-h-0 w-full max-w-[1120px] flex-1 gap-6 px-4 py-4 lg:px-10 lg:py-6">
        {/* Lista de conversas */}
        <aside className={cx("min-h-0 w-full flex-col gap-3 lg:flex lg:w-[320px] lg:shrink-0", emConversa ? "hidden" : "flex")}>
          <h1 className="m-0 font-titulo text-[26px] leading-tight font-extrabold tracking-[-0.03em]">Conversas</h1>
          <BotaoPrimario type="button" onClick={novaConversa}>
            <Mais /> Nova conversa
          </BotaoPrimario>
          {aviso && <Aviso>{aviso}</Aviso>}
          <div className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto">
            {listaCarregando && <Texto>Carregando suas conversas…</Texto>}
            {listaErro && (
              <>
                <Aviso>{listaErro}</Aviso>
                <BotaoContorno type="button" onClick={() => void recarregarLista()}>Tentar de novo</BotaoContorno>
              </>
            )}
            {!listaCarregando && !listaErro && conversas.length === 0 && (
              <Texto>Você ainda não conversou com o assistente. Toque em "Nova conversa".</Texto>
            )}
            {conversas.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => void abrir(c.id)}
                aria-current={c.id === abertaId ? "true" : undefined}
                disabled={enviando}
                className={cx(
                  "flex min-h-14 flex-col items-start gap-0.5 rounded-[18px] border-2 bg-white px-4 py-3 text-left shadow-cartao disabled:opacity-60",
                  c.id === abertaId ? "border-folha" : "border-transparent hover:border-folha/50",
                )}
              >
                <span className="w-full truncate text-base font-bold">{c.titulo ?? "Conversa nova"}</span>
                <span className="text-[13px] text-suave">{dataRelativa(c.atualizada_em)}</span>
              </button>
            ))}
          </div>
        </aside>

        {/* Conversa */}
        <section className={cx("min-h-0 min-w-0 flex-1 flex-col overflow-hidden rounded-[22px] bg-white shadow-cartao lg:flex", emConversa ? "flex" : "hidden")}>
          <div className="flex items-center justify-between gap-2 border-b-2 border-linha px-3 py-2">
            <button
              type="button"
              onClick={voltarParaLista}
              disabled={enviando}
              className="flex h-11 items-center gap-1.5 rounded-xl px-3 text-[15px] font-bold text-suave hover:bg-terra disabled:opacity-60 lg:invisible"
            >
              <Voltar size={18} /> Conversas
            </button>
            {abertaId !== null && !confirmando && (
              <button
                type="button"
                onClick={() => setConfirmando(true)}
                disabled={enviando}
                className="h-11 rounded-xl px-3 text-[15px] font-bold text-suave hover:bg-terra disabled:opacity-60"
              >
                Apagar conversa
              </button>
            )}
          </div>

          {confirmando && (
            <div role="alertdialog" aria-label="Apagar conversa" className="flex flex-col gap-3 bg-sol-claro px-4 py-3">
              <span className="text-base font-bold">Apagar esta conversa? Não dá para desfazer.</span>
              <div className="grid grid-cols-2 gap-2">
                <BotaoContorno type="button" onClick={() => setConfirmando(false)} disabled={apagando}>Cancelar</BotaoContorno>
                <button
                  type="button"
                  onClick={() => void apagar()}
                  disabled={apagando}
                  className="h-12 rounded-2xl bg-[#B3261E] px-4 text-[15px] font-bold text-white disabled:opacity-60"
                >
                  {apagando ? "Apagando…" : "Apagar"}
                </button>
              </div>
            </div>
          )}

          <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto bg-white px-4 py-4" aria-live="polite">
            {abrindo && <Texto>Abrindo a conversa…</Texto>}
            {vazia && (
              <div className="flex flex-col gap-3">
                <p className="m-0 text-base leading-[1.5] text-suave">
                  Pergunte sobre o clima da sua terra, as culturas e a rotação. Eu respondo com dados da NASA e mostro de onde veio cada número.
                </p>
                <div className="flex flex-col gap-2">
                  {SUGESTOES.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => void enviar(s)}
                      disabled={enviando}
                      className="flex min-h-12 items-center justify-between gap-2 rounded-2xl border-2 border-borda bg-white px-4 py-2.5 text-left text-base font-bold hover:border-folha/50 disabled:opacity-60"
                    >
                      {s} <Seta size={18} className="shrink-0 text-folha" />
                    </button>
                  ))}
                </div>
              </div>
            )}
            {mensagens.map((m) => (
              <Balao key={m.id} m={m} />
            ))}
            {enviando && <Pensando />}
            <div ref={fim} />
          </div>

          <form
            className="flex flex-col gap-2 border-t-2 border-linha px-3 pt-3 pb-3"
            onSubmit={(e) => {
              e.preventDefault();
              void enviar(texto);
            }}
          >
            {erroEnvio && <Aviso>{erroEnvio}</Aviso>}
            <div className="flex items-end gap-2">
              <textarea
                ref={campo}
                value={texto}
                rows={1}
                maxLength={LIMITE}
                aria-label="Escreva sua pergunta"
                placeholder="Escreva sua pergunta"
                onChange={(e) => setTexto(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                    e.preventDefault();
                    void enviar(texto);
                  }
                }}
                className="min-h-12 flex-1 resize-none rounded-2xl border-2 border-borda bg-white px-4 py-3 text-base leading-snug text-tinta placeholder:text-suave/60 focus:border-folha focus:outline-none"
              />
              <BotaoPrimario type="submit" disabled={enviando || !texto.trim()} className="h-12 rounded-2xl px-5 text-base">
                {enviando ? "Enviando…" : "Enviar"}
              </BotaoPrimario>
            </div>
            <div className="flex items-center justify-between gap-2 text-[13px] text-suave">
              <span>A AgroIA apoia. Quem decide é você.</span>
              {texto.length >= PERTO_DO_LIMITE && <span className="font-bold">{texto.length}/{LIMITE}</span>}
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}
