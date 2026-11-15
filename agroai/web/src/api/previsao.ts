// Previsão dos próximos 7 dias no ponto da fazenda (Open-Meteo, D-014).
import { api } from "./client";
import type { Previsao } from "./tipos";

export const obterPrevisao = () => api<Previsao>("/fazenda/previsao");
