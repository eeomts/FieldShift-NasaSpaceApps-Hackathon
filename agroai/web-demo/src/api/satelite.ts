// Satélite da fazenda: umidade (SMAP), NDVI (MODIS) e chuva dos últimos 30 dias (IMERG ou NASA POWER).
import { api } from "./client";
import type { Satelite } from "./tipos";

export const obterSatelite = () => api<Satelite>("/fazenda/satelite");
