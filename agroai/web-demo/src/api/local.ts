// Busca de lugar e informacoes do ponto (rotas /local/*, exigem login).
import { api } from "./client";
import type { InfoLocal, LugarBusca } from "./tipos";

export const buscarLugar = (q: string, idioma: "pt" | "en") =>
  api<LugarBusca[]>(`/local/buscar?q=${encodeURIComponent(q)}&idioma=${idioma}`);

export const infoLocal = (lat: number, lon: number, idioma: "pt" | "en") =>
  api<InfoLocal>(`/local/info?lat=${lat}&lon=${lon}&idioma=${idioma}`);
