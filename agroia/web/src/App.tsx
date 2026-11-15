import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import { SessaoProvider, useSessao } from "./api/sessao";
import { Chat } from "./pages/Chat";
import { Dashboard } from "./pages/Dashboard";
import { Entrar } from "./pages/Entrar";
import { Onboarding } from "./onboarding/Onboarding";

function Carregando() {
  return <div className="flex min-h-dvh items-center justify-center text-suave">Carregando…</div>;
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
    <SessaoProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<SoDeslogado><Entrar modo="login" /></SoDeslogado>} />
          <Route path="/cadastro" element={<SoDeslogado><Entrar modo="cadastro" /></SoDeslogado>} />
          <Route path="/onboarding" element={<Protegida><Onboarding /></Protegida>} />
          <Route path="/dashboard" element={<Protegida exigeOnboarding><Dashboard /></Protegida>} />
          <Route path="/chat" element={<Protegida exigeOnboarding><Chat /></Protegida>} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </SessaoProvider>
  );
}
