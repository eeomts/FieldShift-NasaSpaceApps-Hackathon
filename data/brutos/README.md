# data/brutos — downloads grandes (fora do Git)

Tudo nesta pasta é **ignorado pelo Git** (menos este README). Aqui ficam os arquivos baixados que são grandes demais para o repositório:

```text
data/brutos/
├── zarc/        # tábua de risco completa do ZARC, como veio do portal do MAPA
└── outros/      # qualquer outro download grande
```

Regras:
- Registre cada download em `data/FONTES.md` (URL, data, versão), para outra pessoa conseguir baixar de novo.
- O que for **usado** pelo app sai daqui já filtrado e pequeno, para a pasta certa (ex.: as janelas do ZARC das culturas da base vão para `data/brasil/zarc/janelas.csv`, pelo `scripts/preparar_zarc.py`).
- Para compartilhar um bruto com o time, use a pasta compartilhada do time, não o Git.

---

Volta para o [`data/README.md`](../README.md).
