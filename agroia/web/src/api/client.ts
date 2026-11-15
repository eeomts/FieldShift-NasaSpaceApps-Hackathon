const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const CHAVE_TOKEN = "agroia.token";

/** `message` é o detalhe cru da API (pode estar em português); a tela mostra `mensagemErro(e, idioma)`. */
export class ErroApi extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export const token = {
  get: () => localStorage.getItem(CHAVE_TOKEN),
  set: (t: string) => localStorage.setItem(CHAVE_TOKEN, t),
  clear: () => localStorage.removeItem(CHAVE_TOKEN),
};

function detalhe(corpo: unknown): string {
  const d = (corpo as { detail?: unknown })?.detail;
  return typeof d === "string" ? d : "";
}

export async function api<T>(caminho: string, opcoes: { method?: string; body?: unknown } = {}): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const t = token.get();
  if (t) headers.Authorization = `Bearer ${t}`;
  let resp: Response;
  try {
    resp = await fetch(`${BASE}${caminho}`, {
      method: opcoes.method ?? "GET",
      headers,
      body: opcoes.body === undefined ? undefined : JSON.stringify(opcoes.body),
    });
  } catch {
    throw new ErroApi(0, "network");
  }
  if (resp.status === 204) return undefined as T;
  const corpo = await resp.json().catch(() => null);
  if (!resp.ok) throw new ErroApi(resp.status, detalhe(corpo));
  return corpo as T;
}
