import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { paraIdioma, useIdioma } from "../i18n";
import { api, token } from "./client";
import type { Usuario } from "./tipos";

interface Sessao {
  usuario: Usuario | null;
  carregando: boolean;
  /** Versão de apresentação: a pessoa só diz o nome; a conta é criada por baixo. */
  entrarComNome: (nome: string) => Promise<Usuario>;
  sair: () => void;
  recarregar: () => Promise<void>;
}

/** Texto aleatório para o e-mail e a senha da conta de apresentação (a pessoa nunca vê). */
function aleatorio(bytes: number): string {
  const b = new Uint8Array(bytes);
  crypto.getRandomValues(b);
  return Array.from(b, (x) => x.toString(16).padStart(2, "0")).join("");
}

const Ctx = createContext<Sessao | null>(null);

export function SessaoProvider({ children }: { children: ReactNode }) {
  const { idioma, aplicarDaConta } = useIdioma();
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

  // Ao logar (ou abrir o app já logado), vale o idioma da conta.
  const idDaConta = usuario?.id;
  const idiomaDaConta = usuario?.idioma;
  useEffect(() => {
    if (idDaConta) aplicarDaConta(paraIdioma(idiomaDaConta));
  }, [idDaConta, idiomaDaConta, aplicarDaConta]);

  const comToken = async (caminho: string, body: unknown) => {
    const r = await api<{ token: string; usuario: Usuario }>(caminho, { method: "POST", body });
    token.set(r.token);
    setUsuario(r.usuario);
    return r.usuario;
  };

  const valor: Sessao = {
    usuario,
    carregando,
    // A API continua pedindo e-mail e senha: geramos os dois, e o token fica salvo neste navegador.
    entrarComNome: (nome) =>
      comToken("/auth/register", { nome: nome.trim(), email: `demo-${aleatorio(8)}@demo.agroai.app`, senha: aleatorio(16), idioma }),
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
