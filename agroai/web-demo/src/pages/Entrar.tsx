import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { useSessao } from "../api/sessao";
import { SeletorIdioma } from "../components/Casca";
import { Logo } from "../components/Logo";
import { useIdioma } from "../i18n";
import { Paisagem } from "../components/Paisagem";
import { Seta } from "../components/icones";
import { Aviso, BotaoPrimario, Campo, cx } from "../components/ui";

// Versão de apresentação (NASA Space Apps): só o nome, sem e-mail e senha.
export function Entrar() {
  const { entrarComNome } = useSessao();
  const { t, erro: textoErro } = useIdioma();
  const navigate = useNavigate();
  const [nome, setNome] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    if (!nome.trim()) return;
    setErro(null);
    setEnviando(true);
    try {
      const u = await entrarComNome(nome);
      navigate(u.onboarding_concluido ? "/dashboard" : "/onboarding", { replace: true });
    } catch (err) {
      setErro(textoErro(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="min-h-dvh lg:grid lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)]">
      {/* Celular: faixa no topo. Computador: painel fixo à esquerda. */}
      <div className="lg:sticky lg:top-0 lg:h-dvh lg:p-5">
        <Paisagem className={cx("mx-auto h-[300px] max-w-[480px] [--escala-planta:1] lg:h-full lg:max-w-none lg:rounded-[44px] lg:[--escala-planta:2.2]")} />
      </div>

      <div className="mx-auto flex w-full max-w-[480px] flex-col gap-6 px-7 pt-7 pb-8 lg:min-h-dvh lg:max-w-[460px] lg:justify-center lg:px-10 lg:py-12">
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between gap-3">
            <Logo />
            <SeletorIdioma />
          </div>
          <h1 className="mt-1.5 mb-0 font-titulo text-[34px] leading-[1.05] font-extrabold tracking-[-0.03em] lg:text-[44px]">
            {t("Sua fazenda,", "Your farm,")}<br />{t("vista do espaço.", "seen from space.")}
          </h1>
          <p className="m-0 text-[15px] leading-[1.45] text-suave lg:text-[17px]">
            {t("Dados de satélite da NASA traduzidos para o seu campo.", "NASA satellite data translated for your field.")}
          </p>
        </div>

        <form onSubmit={enviar} className="flex flex-1 flex-col gap-3 lg:flex-none" noValidate>
          <Campo rotulo={t("Seu nome", "Your name")} autoComplete="name" required autoFocus value={nome} onChange={(e) => setNome(e.target.value)} placeholder={t("Como quer ser chamado", "What should we call you?")} />
          {erro && <Aviso>{erro}</Aviso>}
          <div className="mt-auto flex flex-col gap-3 pt-4 lg:mt-2">
            <BotaoPrimario type="submit" disabled={enviando || !nome.trim()}>
              {enviando ? t("Aguarde…", "Please wait…") : t("Começar", "Get started")}
              {!enviando && <Seta />}
            </BotaoPrimario>
          </div>
        </form>
      </div>
    </main>
  );
}
