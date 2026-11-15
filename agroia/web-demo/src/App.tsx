import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import { SessaoProvider, useSessao } from "./api/sessao";
import { IdiomaProvider, useIdioma } from "./i18n";
import { Chat } from "./pages/Chat";
import { Dashboard } from "./pages/Dashboard";
import { Entrar } from "./pages/Entrar";
import { Onboarding } from "./onboarding/Onboarding";

function Carregando() {
  const { t } = useIdioma();
  return <div className="flex min-h-dvh items-center justify-center text-suave">{t("Carregando…", "Loading…")}</div>;
}

/** Só entra logado. Sem onboarding concluído, vai para /onboarding (site-contexto, seção 3). */
function Protegida({ children, exigeOnboarding }: { children: ReactNode; exigeOnboarding?: boolean }) {
  const { usuario, carregando } = useSessao();
  if (carregando) return <Carregando />;
  if (!usuario) return <Navigate to="/login" replace />;
  if (exigeOnboarding && !usuario.onboarding_concluido) return <Navigate to="/onboarding" replace />;
  return <>{children}</>;
}

function SoDeslogado({ children }: { children: ReactNode }) {
  const { usuario, carregando } = useSessao();
  if (carregando) return <Carregando />;
  if (usuario) return <Navigate to={usuario.onboarding_concluido ? "/dashboard" : "/onboarding"} replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <IdiomaProvider>
    <SessaoProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<SoDeslogado><Entrar /></SoDeslogado>} />
          <Route path="/cadastro" element={<Navigate to="/login" replace />} />
          <Route path="/onboarding" element={<Protegida><Onboarding /></Protegida>} />
          <Route path="/dashboard" element={<Protegida exigeOnboarding><Dashboard /></Protegida>} />
          <Route path="/agroia" element={<Protegida exigeOnboarding><Chat /></Protegida>} />
          <Route path="/chat" element={<Navigate to="/agroia" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </SessaoProvider>
    </IdiomaProvider>
  );
}
