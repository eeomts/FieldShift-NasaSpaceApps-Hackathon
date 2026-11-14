import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api, token } from "./client";
import type { Usuario } from "./tipos";

interface Sessao {
  usuario: Usuario | null;
  carregando: boolean;
  entrar: (email: string, senha: string) => Promise<Usuario>;
  cadastrar: (nome: string, email: string, senha: string) => Promise<Usuario>;
  sair: () => void;
  recarregar: () => Promise<void>;
}

const Ctx = createContext<Sessao | null>(null);

export function SessaoProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  const recarregar = useCallback(async () => {
    if (!token.get()) {
      setUsuario(null);
      return;
    }
    try {
      setUsuario(await api<Usuario>("/me"));
    } catch {
      token.clear();
      setUsuario(null);
    }
  }, []);

  useEffect(() => {
    recarregar().finally(() => setCarregando(false));
  }, [recarregar]);

  const comToken = async (caminho: string, body: unknown) => {
    const r = await api<{ token: string; usuario: Usuario }>(caminho, { method: "POST", body });
    token.set(r.token);
    setUsuario(r.usuario);
    return r.usuario;
  };

  const valor: Sessao = {
    usuario,
    carregando,
    entrar: (email, senha) => comToken("/auth/login", { email, senha }),
    cadastrar: (nome, email, senha) => comToken("/auth/register", { nome, email, senha, idioma: "pt" }),
    sair: () => {
      token.clear();
      setUsuario(null);
    },
    recarregar,
  };
  return <Ctx.Provider value={valor}>{children}</Ctx.Provider>;
}

export function useSessao(): Sessao {
  const s = useContext(Ctx);
  if (!s) throw new Error("useSessao fora do SessaoProvider");
  return s;
}
