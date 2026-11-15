# Os dois sites do AgroAI (web e web-demo) compilados e servidos pelo mesmo Caddy. Contexto do build: agroai/.
FROM node:22-alpine AS web

WORKDIR /build

COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY web/ ./

# mesmo domínio do site: o Caddy repassa /api para a API
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM node:22-alpine AS demo

WORKDIR /build

COPY web-demo/package.json web-demo/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY web-demo/ ./

ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM caddy:2-alpine

COPY --from=web /build/dist /srv/web
COPY --from=demo /build/dist /srv/demo
