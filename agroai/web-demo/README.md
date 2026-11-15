# AgroAI · versão de apresentação (NASA Space Apps)

Cópia do `web/` com **uma única diferença**: a entrada pede **só o nome**. Não tem e-mail, senha nem tela de login.

Por baixo, o app cria a conta sozinho na API (`POST /auth/register`) com um e-mail `demo-<aleatório>@demo.agroai.app` e uma senha aleatória, e guarda o token neste navegador. A API não mudou. O resto (questionário, dashboard, estratégias, chat) é igual ao `web/`.

```bash
cd agroai/web-demo
npm install
npm run dev        # http://localhost:5174 (o web/ normal continua na 5173)
```

A API precisa estar rodando (veja `agroai/README.md`). Em produção, inclua o endereço desta versão no `CORS_ORIGINS` da API.

Observações:
- Cada pessoa que entra vira uma conta nova no banco. "Sair" volta para a tela do nome e a conta antiga fica lá.
- Mudanças feitas no `web/` não chegam aqui sozinhas: se algo importante mudar lá antes da apresentação, copie para cá.
