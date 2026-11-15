"""Gera a trilha leve de 30s (violão dedilhado + piano suave) só com numpy.

Uso: python3 music.py saida.wav
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 30.0
BPM = 90
BEAT = 60 / BPM
N = int(SR * DUR)
rng = np.random.default_rng(7)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pluck(freq, dur, bright=0.5):
    """Corda dedilhada (Karplus-Strong)."""
    n = int(SR * dur)
    period = int(SR / freq)
    buf = rng.uniform(-1, 1, period)
    # suaviza o ataque: menos "arranhado"
    for _ in range(2):
        buf = 0.5 * (buf + np.roll(buf, 1))
    out = np.zeros(n)
    decay = 0.996
    for i in range(n):
        j = i % period
        out[i] = buf[j]
        buf[j] = decay * (bright * buf[j] + (1 - bright) * buf[j - 1])
    fade = np.linspace(1, 0, n) ** 1.5
    return out * fade


def piano(freq, dur):
    t = np.arange(int(SR * dur)) / SR
    tone = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t)
            + 0.12 * np.sin(6 * np.pi * freq * t))
    env = np.minimum(t / 0.02, 1) * np.exp(-t * 1.6)
    return tone * env


# C  G/B  Am  F  (notas MIDI do arpejo)
CHORDS = [
    [48, 55, 60, 64, 67, 64],   # C
    [47, 55, 59, 62, 67, 62],   # G/B
    [45, 52, 57, 60, 64, 60],   # Am
    [41, 53, 57, 60, 65, 60],   # F
]
PIANO = [[72, 76, 79], [71, 74, 79], [69, 72, 76], [69, 72, 77]]

guitar = np.zeros(N + SR * 4)
keys = np.zeros(N + SR * 4)

eighth = BEAT / 2
bar = BEAT * 4
t = 0.0
bar_i = 0
while t < DUR - 1.2:
    chord = CHORDS[bar_i % 4]
    for k in range(8):
        st = t + k * eighth
        if st >= DUR - 1.2:
            break
        note = chord[k % 6] if k < 6 else chord[(k - 4) % 6]
        s = pluck(midi_hz(note), 2.2, bright=0.45)
        i = int(st * SR)
        guitar[i:i + len(s)] += s * (0.9 if k == 0 else 0.55)
    # piano: uma nota da melodia por tempo, simples
    for k, m in enumerate(PIANO[bar_i % 4] + [PIANO[bar_i % 4][1]]):
        st = t + k * BEAT
        s = piano(midi_hz(m), 2.5)
        i = int(st * SR)
        keys[i:i + len(s)] += s * 0.35
    t += bar
    bar_i += 1

# acorde final longo (C maior) no logo
end = int((DUR - 1.3) * SR)
for m in [48, 55, 60, 64, 67, 72]:
    s = pluck(midi_hz(m), 4.0, bright=0.5)
    guitar[end:end + len(s)] += s * 0.6
    s = piano(midi_hz(m + 12), 4.0)
    keys[end:end + len(s)] += s * 0.25

guitar = guitar[:N]
keys = keys[:N]
tt = np.arange(N) / SR


def curve(points):
    xs, ys = zip(*points)
    return np.interp(tt, xs, ys)


# curva da música (seção 5 do prompt)
g_gain = curve([(0, 0), (0.6, 0.45), (3, 0.45), (3.6, 0.18), (7.8, 0.18),
                (8.6, 0.6), (17.6, 0.85), (18.4, 0.08), (26.6, 0.08),
                (27.2, 1.0), (30, 1.0)])
k_gain = curve([(0, 0), (8, 0), (9.5, 0.5), (17.6, 0.7), (18.4, 0.75),
                (26.6, 0.75), (27.2, 1.0), (30, 1.0)])

mix = guitar * g_gain + keys * k_gain
# eco curto para dar ar
delay = int(0.23 * SR)
wet = np.zeros_like(mix)
wet[delay:] = mix[:-delay] * 0.25
mix = mix + wet
mix *= np.minimum(1, (DUR - tt) / 0.25)  # sem estalo no fim
mix = mix / np.max(np.abs(mix)) * 0.8

stereo = np.stack([mix, np.roll(mix, int(0.012 * SR))], axis=1)
pcm = (stereo * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("ok", sys.argv[1])
