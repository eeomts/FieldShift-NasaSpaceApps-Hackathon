# Front do AgroAI: build do React servido pelo Caddy. Contexto do build: agroai/web/.
FROM node:22-alpine AS build

WORKDIR /web

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .

# mesmo domínio do site: o Caddy repassa /api para a API
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM caddy:2-alpine

COPY --from=build /web/dist /srv
