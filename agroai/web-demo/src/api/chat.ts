// Chamadas do chat com o assistente (rotas /chat/conversas).
import { api } from "./client";
import type { Conversa, ConversaResumo, EnviarMensagem, Mensagem } from "./tipos";

export const listarConversas = () => api<ConversaResumo[]>("/chat/conversas");

export const criarConversa = () => api<ConversaResumo>("/chat/conversas", { method: "POST" });

export const abrirConversa = (id: number) => api<Conversa>(`/chat/conversas/${id}`);

export const enviarMensagem = (id: number, mensagem: string, idioma: "pt" | "en") => {
  const body: EnviarMensagem = { mensagem, idioma };
  return api<Mensagem>(`/chat/conversas/${id}/mensagens`, { method: "POST", body });
};

export const apagarConversa = (id: number) =>
  api<void>(`/chat/conversas/${id}`, { method: "DELETE" });
