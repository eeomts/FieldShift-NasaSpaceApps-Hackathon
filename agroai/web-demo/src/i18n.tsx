// Idioma do app (PT/EN): contexto, hook e traducao das mensagens de erro da API.
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { api, ErroApi, token } from "./api/client";

export type Idioma = "pt" | "en";

const CHAVE = "agroai.idioma";

export const paraIdioma = (v: unknown): Idioma => (v === "en" ? "en" : "pt");

function inicial(): Idioma {
  try {
    const salvo = localStorage.getItem(CHAVE);
    if (salvo === "pt" || salvo === "en") return salvo;
  } catch {
    /* sem localStorage: segue pelo navegador */
  }
  return typeof navigator !== "undefined" && navigator.language?.toLowerCase().startsWith("pt") ? "pt" : "en";
}

/** Erro da API em linguagem simples, por status (0 = sem rede). */
export function mensagemErro(e: unknown, idioma: Idioma): string {
  const t = (pt: string, en: string) => (idioma === "en" ? en : pt);
  const status = e instanceof ErroApi ? e.status : -1;
  if (status === 0) return t("Sem conexão com o servidor. Verifique sua internet.", "Can't reach the server. Check your internet.");
  if (status === 401) return t("Sua sessão acabou. Digite seu nome de novo para começar.", "Your session ended. Enter your name again to start.");
  if (status === 409) return t("Este e-mail já tem conta. Tente entrar.", "This email already has an account. Try logging in.");
  if (status === 422) return t("Confira os campos e tente de novo.", "Please check the fields and try again.");
  if (status === 503) return t("A AgroAI está indisponível agora. Tente de novo mais tarde.", "AgroAI is unavailable right now. Please try again later.");
  if (status >= 500) return t("O servidor teve um problema. Tente de novo em instantes.", "The server had a problem. Please try again in a moment.");
  return t("Algo deu errado. Tente de novo.", "Something went wrong. Please try again.");
}

interface Ctx {
  idioma: Idioma;
  /** Troca o idioma; com login ativo, grava na conta (PATCH /me). */
  setIdioma: (i: Idioma) => void;
  /** Usado pela sessão: aplica o idioma da conta sem gravar de volta. */
  aplicarDaConta: (i: Idioma) => void;
  t: (pt: string, en: string) => string;
  erro: (e: unknown) => string;
}

const IdiomaCtx = createContext<Ctx | null>(null);

export function IdiomaProvider({ children }: { children: ReactNode }) {
  const [idioma, setIdiomaState] = useState<Idioma>(inicial);

  const guardar = useCallback((i: Idioma) => {
    setIdiomaState(i);
    try {
      localStorage.setItem(CHAVE, i);
    } catch {
      /* ignora */
    }
  }, []);

  const setIdioma = useCallback(
    (i: Idioma) => {
      guardar(i);
      if (token.get()) void api("/me", { method: "PATCH", body: { idioma: i } }).catch(() => {});
    },
    [guardar],
  );

  const valor = useMemo<Ctx>(
    () => ({
      idioma,
      setIdioma,
      aplicarDaConta: guardar,
      t: (pt, en) => (idioma === "en" ? en : pt),
      erro: (e) => mensagemErro(e, idioma),
    }),
    [idioma, setIdioma, guardar],
  );
  return <IdiomaCtx.Provider value={valor}>{children}</IdiomaCtx.Provider>;
}

export function useIdioma(): Ctx {
  const c = useContext(IdiomaCtx);
  if (!c) throw new Error("useIdioma fora do IdiomaProvider");
  return c;
}

export const MESES_CURTOS: Record<Idioma, string[]> = {
  pt: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
  en: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
};
export const MESES_LONGOS: Record<Idioma, string[]> = {
  pt: ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
  en: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
};
export const INICIAIS_MESES = "JFMAMJJASOND".split("");
