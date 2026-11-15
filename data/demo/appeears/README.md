# data/demo/appeears — saídas do AppEEARS dos pontos da demo

> **DESCARTADO em 15/11/2026.** O projeto não vai mais usar o AppEEARS (decisão do usuário). Esta pasta e o script `data/scripts/baixar_appeears.py` ficam só como histórico. O app não lê estes arquivos, e o conteúdo abaixo não deve ser registrado no `data/FONTES.md` nem refeito.

Gerado por `python data/scripts/baixar_appeears.py`. São **dois pedidos**, cada um com todos os pontos de `data/demo/pontos_demo.csv`, e cada pedido vira uma subpasta com o id que o AppEEARS devolve:

```
data/demo/appeears/
├── tarefas.json                  # qual pasta é de qual pedido, com produtos, camadas e período
├── <id_do_pedido_ndvi>/          # MOD13Q1.061 + VNP13A1.002, desde 2001
│   ├── *-MOD13Q1-061-results.csv
│   ├── *-VNP13A1-002-results.csv
│   └── ...                       # resto do bundle: JSON do pedido, README e tabelas de qualidade
└── <id_do_pedido_smap>/          # SPL4SMGP, desde 31/03/2015 (início do produto)
    ├── *-SPL4SMGP-*-results.csv
    └── ...
```

- O bundle vem **inteiro e como veio**, sem editar: os CSVs e os arquivos de apoio (pedido em JSON, README e as tabelas que traduzem os códigos de qualidade).
- O **`tarefas.json` é versionado de propósito**: ele é o registro de quais pedidos geraram estes arquivos. O script o reescreve a cada rodada (status, data do download, número de arquivos), então ele só é commitado **depois do download**, já com `"baixado"`.
- Os pedidos pertencem à conta do Earthdata que os criou. Com outra conta, o script avisa que o pedido não existe nela; rode com `--novo`.
- Registre cada pedido em `data/FONTES.md` (id, produtos, período real e data).
