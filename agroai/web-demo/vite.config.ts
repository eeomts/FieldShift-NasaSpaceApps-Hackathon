import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

// Versão de apresentação (NASA Space Apps): roda na 5174 para não brigar com o web/ (5173).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5174, strictPort: true },
  preview: { port: 4174, strictPort: true },
});
