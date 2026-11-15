#!/usr/bin/env bash
# Mixa as vozes (voz/) com a trilha (music.wav) e gera soundtrack.wav/.mp3.
# A música abaixa sozinha (sidechain) quando alguém fala.
set -euo pipefail
cd "$(dirname "$0")"
[ -f music.wav ] || python3 music.py music.wav
ffmpeg -y -loglevel error -i voz/l1.wav -i voz/l2.wav -i voz/l3.wav -i voz/l4.wav \
 -i voz/narrador/n1.wav -i voz/narrador/n2.wav -i voz/narrador/n3.wav -i voz/narrador/n4.wav -i voz/narrador/n5.wav -i music.wav -filter_complex "\
[0]loudnorm=I=-16:TP=-2,adelay=3500|3500[a];[1]loudnorm=I=-18:TP=-2,adelay=18700|18700[b];[2]loudnorm=I=-18:TP=-2,adelay=21700|21700[c];[3]loudnorm=I=-16:TP=-2,adelay=27400|27400[d];\
[a][b][c][d]amix=inputs=4:normalize=0,highpass=f=80,aecho=0.9:0.9:35:0.06,aformat=sample_rates=44100:channel_layouts=stereo[marta];\
[4]loudnorm=I=-16:TP=-2,adelay=300|300[e];[5]loudnorm=I=-16:TP=-2,adelay=8300|8300[f];[6]loudnorm=I=-16:TP=-2,adelay=11200|11200[g];[7]loudnorm=I=-16:TP=-2,adelay=15200|15200[h];[8]loudnorm=I=-16:TP=-2,adelay=25050|25050[i];\
[e][f][g][h][i]amix=inputs=5:normalize=0,highpass=f=70,equalizer=f=150:t=q:w=1:g=2,aformat=sample_rates=44100:channel_layouts=stereo[narr];\
[marta][narr]amix=inputs=2:normalize=0,apad=whole_dur=30,asplit[v1][v2];\
[9]volume=0.8[mu];[mu][v1]sidechaincompress=threshold=0.015:ratio=10:attack=20:release=450[m];\
[m][v2]amix=inputs=2:normalize=0,alimiter=limit=0.95,atrim=0:30[out]" -map "[out]" -ar 44100 soundtrack.wav
ffmpeg -y -loglevel error -i soundtrack.wav -b:a 192k soundtrack.mp3
echo "ok: soundtrack.wav e soundtrack.mp3"
