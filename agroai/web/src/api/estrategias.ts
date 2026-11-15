// Comparação de rotações da fazenda (rota GET /fazenda/estrategias).
import { api } from "./client";
import type { Analise } from "./tipos";

export const obterEstrategias = () => api<Analise>("/fazenda/estrategias");
