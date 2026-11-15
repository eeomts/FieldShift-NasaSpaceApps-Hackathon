// Aba AgroAI (visual v3): conversa com o assistente, lista de conversas da equipe (/chat/conversas),
// resposta no idioma escolhido e pergunta vinda do Dashboard por /agroia?q=<pergunta>.
import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router";
import { abrirConversa, apagarConversa, criarConversa, enviarMensagem, listarConversas } from "../api/chat";
import { ErroApi } from "../api/client";
import { useSessao } from "../api/sessao";
import type { ConversaResumo, Mensagem } from "../api/tipos";
import { Casca, SeletorIdioma } from "../components/Casca";
import { Balao, BalaoLocal, Pensando } from "../components/chat/Mensagens";
import { Brilho, Conversas, Enviar, Lixeira, Mais, Voltar } from "../components/icones";
import { Aviso, BotaoContorno, cx, Texto } from "../components/ui";
import { useIdioma, type Idioma } from "../i18n";

const LIMITE = 2000;
const PERTO_DO_LIMITE = 1800;

const SUGESTOES: Record<Idioma, string[]> = {
  pt: ["O que plantar depois da colheita?", "Meu solo está seco?", "Vai dar geada aqui em julho?", "Quanto chove em janeiro na minha terra?"],
  en: ["What should I plant after harvest?", "Is my soil dry?", "Will it frost here in July?", "How much does it rain here in January?"],
};

function dataRelativa(iso: string, idioma: Idioma) {
  const t = (pt: string, en: string) => (idioma === "en" ? en : pt);
  const d = new Date(/(Z|[+-]\d\d:?\d\d)$/.test(iso) ? iso : `${iso}Z`);
  const min = Math.floor((Date.now() - d.getTime()) / 60000);
  if (min < 1) return t("agora", "now");
  if (min < 60) return t(`há ${min} min`, `${min} min ago`);
  const h = Math.floor(min / 60);
  if (h < 24) return t(`há ${h} h`, `${h} h ago`);
  const dias = Math.floor(h / 24);
  if (dias === 1) return t("ontem", "yesterday");
  if (dias < 7) return t(`há ${dias} dias`, `${dias} days ago`);
  return d.toLocaleDateString(idioma === "en" ? "en-US" : "pt-BR", { day: "2-digit", month: "2-digit" });
}

export function Chat() {
  const { usuario } = useSessao();
  const { idioma, t, erro } = useIdioma();
  const [params, setParams] = useSearchParams();

  const [conversas, setConversas] = useState<ConversaResumo[]>([]);
  const [listaCarregando, setListaCarregando] = useState(true);
  const [listaErro, setListaErro] = useState<unknown>(null); // erro guardado cru: traduz na tela
  const [verLista, setVerLista] = useState(false); // celular: lista por cima da conversa

  const [abertaId, setAbertaId] = useState<number | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [abrindo, setAbrindo] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erroEnvio, setErroEnvio] = useState<unknown>(null);
  const [aviso, setAviso] = useState<string | null>(null);
  const [texto, setTexto] = useState("");
  const [confirmando, setConfirmando] = useState(false);
  const [apagando, setApagando] = useState(false);

  const atual = useRef<number | null>(null); // conversa aberta agora (ignora respostas atrasadas)
  const fim = useRef<HTMLDivElement>(null);
  const campo = useRef<HTMLTextAreaElement>(null);
  const perguntaDaUrl = useRef(false);

  const recarregarLista = useCallback(async () => {
    try {
      setConversas(await listarConversas());
      setListaErro(null);
    } catch (e) {
      setListaErro(e);
    } finally {
      setListaCarregando(false);
    }
  }, []);

  useEffect(() => {
    void recarregarLista();
    // só na entrada da tela; trocar o idioma não recarrega a lista
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fim.current?.scrollIntoView({ block: "end" });
  }, [mensagens, enviando, abrindo]);

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

  function limpar() {
    setMensagens([]);
    setErroEnvio(null);
    setAviso(null);
    setTexto("");
    setConfirmando(false);
    setVerLista(false);
  }

  function novaConversa() {
    definirAberta(null);
    limpar();
  }

  async function abrir(id: number) {
    definirAberta(id);
    limpar();
    setAbrindo(true);
    try {
      const c = await abrirConversa(id);
      if (atual.current === id) setMensagens(c.mensagens);
    } catch (e) {
      if (atual.current !== id) return;
      if (e instanceof ErroApi && e.status === 404) {
        definirAberta(null);
        setAviso(t("Essa conversa não existe mais.", "That conversation no longer exists."));
        void recarregarLista();
      } else {
        setErroEnvio(e);
      }
    } finally {
      if (atual.current === id || atual.current === null) setAbrindo(false);
    }
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
      }
      await enviarMensagem(id, pergunta, idioma);
      const c = await abrirConversa(id);
      if (atual.current === id) setMensagens(c.mensagens);
      void recarregarLista();
    } catch (e) {
      if (atual.current === id) {
        setMensagens((ms) => ms.filter((m) => m.id !== otimista.id));
        setErroEnvio(e);
        setTexto(pergunta);
      }
    } finally {
      setEnviando(false);
    }
  }

  // "Perguntar à AgroAI" no Dashboard: /agroia?q=<pergunta> abre uma conversa nova e envia sozinho.
  useEffect(() => {
    const q = params.get("q");
    if (!q || perguntaDaUrl.current) return;
    perguntaDaUrl.current = true;
    setParams({}, { replace: true });
    void enviar(q);
    // roda uma vez por entrada com ?q=
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  async function apagar() {
    if (abertaId === null) return;
    setApagando(true);
    try {
      await apagarConversa(abertaId);
      setConversas((cs) => cs.filter((c) => c.id !== abertaId));
      definirAberta(null);
      limpar();
    } catch (e) {
      setConfirmando(false);
      setErroEnvio(e);
    } finally {
      setApagando(false);
    }
  }

  const primeiroNome = usuario?.nome?.split(" ")[0] ?? "";
  const saudacao = t(
    `Oi${primeiroNome ? `, ${primeiroNome}` : ""}! Eu conheço o seu campo pelas suas respostas e pelos dados da NASA. Pergunte sobre clima, solo ou o que plantar.`,
    `Hi${primeiroNome ? `, ${primeiroNome}` : ""}! I know your field from your answers and from NASA data. Ask about weather, soil or what to plant.`,
  );
  const semMensagens = !abrindo && mensagens.length === 0;

  const lista = (
    <div className="flex min-h-0 flex-1 flex-col gap-2">
      <button
        type="button"
        onClick={novaConversa}
        disabled={enviando}
        className="flex h-12 items-center justify-center gap-2 rounded-2xl border-0 bg-folha px-4 text-[15px] font-bold text-white shadow-[0_3px_0_#14532D] disabled:opacity-60"
      >
        <Mais size={18} /> {t("Nova conversa", "New chat")}
      </button>
      <div className="flex min-h-0 flex-1 flex-col gap-1.5 overflow-y-auto pt-1">
        {listaCarregando && <Texto>{t("Carregando suas conversas…", "Loading your chats…")}</Texto>}
        {listaErro != null && (
          <>
            <Aviso>{erro(listaErro)}</Aviso>
            <BotaoContorno type="button" onClick={() => void recarregarLista()}>{t("Tentar de novo", "Try again")}</BotaoContorno>
          </>
        )}
        {!listaCarregando && listaErro == null && conversas.length === 0 && (
          <p className="m-0 px-1 text-sm leading-snug text-suave">{t("Suas conversas aparecem aqui.", "Your chats show up here.")}</p>
        )}
        {conversas.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => void abrir(c.id)}
            aria-current={c.id === abertaId ? "true" : undefined}
            disabled={enviando}
            className={cx(
              "flex min-h-14 flex-col items-start gap-0.5 rounded-2xl border-2 bg-white px-3.5 py-2.5 text-left disabled:opacity-60",
              c.id === abertaId ? "border-folha" : "border-transparent hover:border-folha/40",
            )}
          >
            <span className="w-full truncate text-[15px] font-bold">{c.titulo ?? t("Conversa nova", "New chat")}</span>
            <span className="text-xs text-suave">{dataRelativa(c.atualizada_em, idioma)}</span>
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <Casca>
      <div className="mx-auto flex min-h-0 w-full max-w-[1120px] flex-1 gap-6 lg:px-10">
        {/* Lista de conversas: coluna no computador */}
        <aside aria-label={t("Conversas", "Chats")} className="hidden min-h-0 w-[260px] shrink-0 flex-col py-6 lg:flex">
          {lista}
        </aside>

        <section className="relative mx-auto flex min-h-0 w-full max-w-[760px] flex-1 flex-col">
          {/* Cabeçalho da AgroAI */}
          <header className="flex items-center gap-3 border-b-2 border-linha px-4 py-3.5 lg:px-0 lg:pt-7">
            <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-folha text-sol shadow-[0_3px_0_#14532D]">
              <Brilho size={24} />
            </span>
            <div className="min-w-0 flex-1">
              <h1 className="m-0 font-titulo text-[21px] leading-tight font-extrabold tracking-[-0.02em]">AgroAI</h1>
              <p className="m-0 line-clamp-2 text-[13px] leading-snug text-suave lg:line-clamp-none">
                {t("Conhece o seu campo · cita a fonte de cada dado", "Knows your field · cites the source of every number")}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setVerLista((v) => !v)}
              aria-expanded={verLista}
              aria-label={t("Conversas", "Chats")}
              className="flex h-11 w-11 items-center justify-center rounded-xl border-2 border-borda bg-white text-tinta lg:hidden"
            >
              <Conversas size={20} />
            </button>
            <SeletorIdioma className="lg:hidden" />
            {abertaId !== null && !confirmando && (
              <button
                type="button"
                onClick={() => setConfirmando(true)}
                disabled={enviando}
                aria-label={t("Apagar conversa", "Delete chat")}
                className="flex h-11 items-center gap-1.5 rounded-xl px-2.5 text-sm font-bold text-suave hover:bg-terra disabled:opacity-60"
              >
                <Lixeira size={18} /> <span className="hidden lg:inline">{t("Apagar", "Delete")}</span>
              </button>
            )}
          </header>

          {/* Lista no celular */}
          {verLista && (
            <div className="absolute inset-x-0 top-[78px] bottom-0 z-20 flex flex-col gap-2 bg-creme px-4 py-3 lg:hidden">
              <button type="button" onClick={() => setVerLista(false)} className="flex h-10 items-center gap-1.5 self-start rounded-xl px-2 text-[15px] font-bold text-suave">
                <Voltar size={18} /> {t("Voltar à conversa", "Back to chat")}
              </button>
              {lista}
            </div>
          )}

          {confirmando && (
            <div role="alertdialog" aria-label={t("Apagar conversa", "Delete chat")} className="mx-4 mt-3 flex flex-col gap-3 rounded-2xl bg-sol-claro px-4 py-3 lg:mx-0">
              <span className="text-base font-bold">{t("Apagar esta conversa? Não dá para desfazer.", "Delete this chat? This can't be undone.")}</span>
              <div className="grid grid-cols-2 gap-2">
                <BotaoContorno type="button" onClick={() => setConfirmando(false)} disabled={apagando}>{t("Cancelar", "Cancel")}</BotaoContorno>
                <button
                  type="button"
                  onClick={() => void apagar()}
                  disabled={apagando}
                  className="h-12 rounded-2xl border-0 bg-perigo px-4 text-[15px] font-bold text-white disabled:opacity-60"
                >
                  {apagando ? t("Apagando…", "Deleting…") : t("Apagar", "Delete")}
                </button>
              </div>
            </div>
          )}

          {/* Mensagens */}
          <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto px-4 py-4 lg:px-4" aria-live="polite">
            <span className="self-center rounded-full bg-sol-claro px-3 py-1 text-xs font-bold text-sol-texto">
              {t("A AgroAI apoia. Quem decide é você.", "AgroAI supports. You decide.")}
            </span>
            {aviso && <Aviso>{aviso}</Aviso>}
            {abrindo && <Texto>{t("Abrindo a conversa…", "Opening the chat…")}</Texto>}
            {!abrindo && (abertaId === null || mensagens.length === 0) && <BalaoLocal texto={saudacao} />}
            {mensagens.map((m) => (
              <Balao key={m.id} m={m} />
            ))}
            {enviando && <Pensando />}
            <div ref={fim} />
          </div>

          {/* Sugestões + campo */}
          <form
            className="flex flex-col gap-2.5 px-4 pt-1 pb-4 lg:px-4 lg:pb-6"
            onSubmit={(e) => {
              e.preventDefault();
              void enviar(texto);
            }}
          >
            {semMensagens && (
              <div className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1 lg:mx-0 lg:px-0">
                {SUGESTOES[idioma].map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => void enviar(s)}
                    disabled={enviando}
                    className="h-11 shrink-0 rounded-full border-2 border-borda bg-white px-4 text-[15px] whitespace-nowrap text-tinta hover:border-folha/50 disabled:opacity-60"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
            {erroEnvio != null && <Aviso>{erro(erroEnvio)}</Aviso>}
            <div className="flex items-end gap-2">
              <textarea
                ref={campo}
                value={texto}
                rows={1}
                maxLength={LIMITE}
                aria-label={t("Escreva sua pergunta", "Type your question")}
                placeholder={t("Pergunte sobre o seu campo…", "Ask about your field…")}
                onChange={(e) => setTexto(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                    e.preventDefault();
                    void enviar(texto);
                  }
                }}
                className="min-h-[52px] flex-1 resize-none rounded-[18px] border-2 border-borda bg-white px-4 py-3.5 text-base leading-snug text-tinta placeholder:text-suave/60 focus:border-folha focus:outline-none"
              />
              <button
                type="submit"
                disabled={enviando || !texto.trim()}
                aria-label={t("Enviar", "Send")}
                className="flex h-[52px] w-[52px] shrink-0 items-center justify-center rounded-[18px] border-0 bg-sol text-tinta shadow-degrau-sol disabled:opacity-60"
              >
                <Enviar size={22} />
              </button>
            </div>
            {texto.length >= PERTO_DO_LIMITE && (
              <span className="self-end text-[13px] font-bold text-suave">{texto.length}/{LIMITE}</span>
            )}
          </form>
        </section>
      </div>
    </Casca>
  );
}
