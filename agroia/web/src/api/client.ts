const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const CHAVE_TOKEN = "agroia.token";

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

function mensagemDeErro(status: number, corpo: unknown): string {
  const detail = (corpo as { detail?: unknown })?.detail;
  if (typeof detail === "string") return detail;
  if (status === 422) return "Confira os campos e tente de novo.";
  if (status >= 500) return "O servidor teve um problema. Tente de novo em instantes.";
  return "Algo deu errado. Tente de novo.";
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
    throw new ErroApi(0, "Sem conexão com o servidor. Verifique sua internet.");
  }
  if (resp.status === 204) return undefined as T;
  const corpo = await resp.json().catch(() => null);
  if (!resp.ok) throw new ErroApi(resp.status, mensagemDeErro(resp.status, corpo));
  return corpo as T;
}
