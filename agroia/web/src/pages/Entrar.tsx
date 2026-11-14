import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";
import { ErroApi } from "../api/client";
import { useSessao } from "../api/sessao";
import { Logo } from "../components/Logo";
import { Paisagem } from "../components/Paisagem";
import { Seta } from "../components/icones";
import { Aviso, BotaoPrimario, Campo, cx } from "../components/ui";

export function Entrar({ modo }: { modo: "login" | "cadastro" }) {
  const { entrar, cadastrar } = useSessao();
  const navigate = useNavigate();
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const cadastro = modo === "cadastro";

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setErro(null);
    if (cadastro && senha.length < 8) {
      setErro("A senha precisa ter pelo menos 8 caracteres.");
      return;
    }
    setEnviando(true);
    try {
      const u = cadastro ? await cadastrar(nome, email, senha) : await entrar(email, senha);
      navigate(u.onboarding_concluido ? "/dashboard" : "/onboarding", { replace: true });
    } catch (err) {
      setErro(err instanceof ErroApi ? err.message : "Algo deu errado. Tente de novo.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="min-h-dvh lg:grid lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)]">
      {/* Celular: faixa no topo. Computador: painel fixo à esquerda. */}
      <div className="lg:sticky lg:top-0 lg:h-dvh lg:p-5">
        <Paisagem
          className={cx(
            "mx-auto max-w-[480px] [--escala-planta:1] lg:h-full lg:max-w-none lg:rounded-[44px] lg:[--escala-planta:2.2]",
            cadastro ? "h-[220px]" : "h-[300px]",
          )}
        />
      </div>

      <div className="mx-auto flex w-full max-w-[480px] flex-col gap-6 px-7 pt-7 pb-8 lg:min-h-dvh lg:max-w-[460px] lg:justify-center lg:px-10 lg:py-12">
        <div className="flex flex-col gap-2">
          <Logo />
          <h1 className="mt-1.5 mb-0 font-titulo text-[34px] leading-[1.05] font-extrabold tracking-[-0.03em] lg:text-[44px]">
            {cadastro ? "Vamos conhecer o seu campo." : <>Sua fazenda,<br />vista do espaço.</>}
          </h1>
          <p className="m-0 text-[15px] leading-[1.45] text-suave lg:text-[17px]">
            {cadastro
              ? "Usamos seus dados só para analisar o seu campo. Você pode apagar tudo quando quiser."
              : "Dados de satélite da NASA traduzidos para o seu campo, todo dia."}
          </p>
        </div>

        <form onSubmit={enviar} className="flex flex-1 flex-col gap-3 lg:flex-none" noValidate>
          {cadastro && <Campo rotulo="Seu nome" autoComplete="name" required value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Como quer ser chamado" />}
          <Campo rotulo="E-mail" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="voce@email.com" />
          <Campo
            rotulo="Senha"
            type="password"
            autoComplete={cadastro ? "new-password" : "current-password"}
            required
            minLength={cadastro ? 8 : undefined}
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            placeholder={cadastro ? "Pelo menos 8 caracteres" : "••••••••"}
          />
          {erro && <Aviso>{erro}</Aviso>}
          <div className="mt-auto flex flex-col gap-3 pt-4 lg:mt-2">
            <BotaoPrimario type="submit" disabled={enviando || !email || !senha || (cadastro && !nome)}>
              {enviando ? "Aguarde…" : cadastro ? "Criar conta" : "Entrar"}
              {!enviando && <Seta />}
            </BotaoPrimario>
            <p className="m-0 text-center text-sm text-suave">
              {cadastro ? (
                <>Já tem conta? <Link to="/login" className="font-bold text-folha">Entrar</Link></>
              ) : (
                <>Primeira vez? <Link to="/cadastro" className="font-bold text-folha">Criar conta</Link></>
              )}
            </p>
          </div>
        </form>
      </div>
    </main>
  );
}
