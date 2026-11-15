# Vídeo de 30s do AgroAI

Vídeo de apresentação do Field Shift (NASA Space Apps 2026), em cartoon 2D com as cores do app.
O roteiro e a estética estão em [`../video-30s-prompt.md`](../video-30s-prompt.md).

| Arquivo | O que é |
|---|---|
| `agroia-30s.mp4` | **O vídeo final** (1920×1080, 24 fps, 30s, com vozes e música) |
| `index.html` | A animação. Abrindo no navegador dá para dar play e arrastar a linha do tempo. O MP4 é gerado dela |
| `music.py` | Gera a trilha leve (violão + piano) só com numpy, sem direitos autorais |
| `voz/l1..l4.wav` | Falas da Dona Marta (voz sintética "Ava") |
| `voz/narrador/n1..n5.wav` | Falas do narrador (voz sintética "Andrew") |
| `voz/samples/` | Amostras de outras vozes para comparar |
| `mix.sh` | Junta vozes + música (a música abaixa quando alguém fala) e gera `soundtrack.wav/.mp3` |
| `render.js` | Captura a animação quadro a quadro no Chromium e gera o MP4 com o ffmpeg |

## Gerar de novo

Precisa de Python 3 com numpy, ffmpeg, Node 20+ e Chromium.

```bash
cd video
./mix.sh                                   # gera music.wav (se faltar) e soundtrack.wav
npm i --no-save puppeteer-core@23.11.1     # só na primeira vez
node render.js index.html agroia-30s.mp4 soundtrack.wav 24
```

Para trocar uma voz (por exemplo, uma gravação real), substitua o `.wav` em `voz/` mantendo o nome e rode os dois comandos de novo.
Os tempos de cada fala estão em `mix.sh` (`adelay`, em ms) e as legendas em `index.html` (`CUES`).
Se a nova fala for mais longa, ajuste os dois.

Os números que aparecem na tela são ilustrativos (o vídeo mostra o selo "Illustrative example").
