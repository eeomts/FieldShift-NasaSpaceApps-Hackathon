# ToDo do time

Tarefas com dono, uma pasta por tarefa. Cada pasta tem um `TODO.md` com o porquê, a entrada, a saída (formato exato), o passo a passo e quando a tarefa está pronta.

```
ToDo/
└── dataset/                       # preparação de dados (pesquisadores)
    ├── pessoa-1-yury/
    ├── pessoa-2/
    └── pessoa-3/
```

## Como usar

1. Pegue a tarefa de menor número da sua pasta que não esteja bloqueada.
2. Troque o **Status** no topo do `TODO.md` (`pendente` → `em andamento` → `em revisão` → `feito`).
3. Trabalhe numa branch sua (`data/<tarefa>`) e abra um PR pequeno quando terminar. Anotações, rascunhos e testes podem ficar na própria pasta da tarefa.
4. Tudo que for baixado entra no `data/FONTES.md` (fonte, URL, data, licença).
5. Cada arquivo de `data/` tem um dono só: precisa mudar arquivo de outra pessoa, avise ela.

## Quem faz o quê

| Pessoa | Tarefas | Prioridade |
|---|---|---|
| **1 — Yury** (agronomia) | ~~01 corrigir o `culturas.csv` duplicado~~ (feito, só conferir) · 02 script da PAM · 03 script do ZARC | 02 e 03 já podem começar |
| **2 — _____** (dados) | 01 pontos da demo · 02 script da malha municipal · 03 script do AppEEARS · 04 exigência de equipamento | 01 primeiro: destrava o AppEEARS |
| **3 — _____** (conteúdo) | 01 textos do RAG · 02 sinônimos das culturas · 03 fotos de solo | 01 primeiro: o agente depende dele |

## Dependências

```
P1-01 culturas.csv corrigido (feito) ──► P1-02 PAM, P1-03 ZARC, P2-04 equipamentos, P3-01 fichas das culturas
P2-01 pontos da demo ─────────► P2-03 AppEEARS
P2-02 malha municipal ────────► (backend liga cada fazenda ao município da PAM e do ZARC)
```

## Regras para os scripts (P1-02, P1-03, P2-02, P2-03)

- Ficam em `data/scripts/`, em **Python 3.12+**, um arquivo por fonte (`baixar_pam.py`, `baixar_zarc.py`...).
- Rodam com um comando só, da raiz do repositório: `python data/scripts/baixar_pam.py`.
- Dependências fora da biblioteca padrão: só `httpx` (ou `requests`) e `pandas`, listadas no topo do arquivo.
- **Nenhuma senha ou token no código**: leia de variável de ambiente (ex.: `EARTHDATA_TOKEN`).
- Rodar duas vezes dá o mesmo resultado (sobrescreve a saída, não duplica linhas).
- Ausente vira **vazio**, nunca 0. Saída em CSV UTF-8, separador vírgula, decimal com ponto.
- Arquivo bruto grande vai para `data/brutos/` (fora do Git); no repositório entra só a saída pronta e pequena (até ~20 MB).

## O que fica com o backend (não é tarefa de vocês)

- Pré-calcular clima (NASA POWER), solo (SoilGrids) e relevo (SRTM) dos pontos da demo, com os conectores da API.
- Carregar no banco os arquivos que vocês entregarem em `data/`.
- Ingerir os textos de `data/rag/` na base de conhecimento do agente.

O formato de saída de cada tarefa é o contrato entre vocês e o backend: entregando nesse formato, a carga é automática.
