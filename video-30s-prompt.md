# AgroIA · Prompt estruturado para o vídeo de 30s

Vídeo de apresentação do **AgroIA** (Field Shift, NASA Space Apps 2026).
Pensado para gerar em ferramentas de vídeo com IA (Veo, Sora, Runway, Kling, Pika) **cena por cena**, já que a maioria gera clipes de 5 a 8s. As telas do app entram como gravação de tela ou mockup por cima.

---

## 1. Briefing

| Item | Definição |
|---|---|
| **Objetivo** | Em 30s, o jurado entende o problema, a solução e por que dados da NASA importam |
| **Público** | Jurados internacionais do Space Apps → narração em **inglês**, legendas em PT opcionais |
| **Mensagem central** | *"NASA has 40 years of data about every farm. AgroIA turns it into words a farmer can use, and answers every 'what if', any time."* |
| **Diferencial em destaque** | O **agente AgroIA**, disponível 24/7, que responde todos os "e se…" do produtor ("e se não chover em janeiro?", "e se eu plantar milheto em abril?") com base nos dados da fazenda dele, citando a fonte |
| **Personagem** | Dona Marta, 52 anos, 80 ha de soja no Cerrado (Luís Eduardo Magalhães, BA) |
| **Arco** | Espaço → problema na terra → app no celular → raio-x do campo → estratégias → **agente responde os "e se" de madrugada** → amanhecer e marca |
| **Formato** | 16:9, 1920×1080, 24 fps. Versão 9:16 recortando o centro (manter ação no centro) |
| **Tom** | Esperançoso, humano, claro. Nada de "IA futurista fria" |

> **Regra do Space Apps:** não usar o logo da NASA (meatball/worm) nem sugerir endosso. Pode citar os nomes dos dados (MODIS, SMAP, GPM, SRTM, NASA POWER).

---

## 2. Bíblia de estética ("Premium Playful")

Cole este bloco **no início de todo prompt de cena** para manter consistência.

```text
STYLE: warm "premium playful" look. Stylized 3D with soft clay-like materials
and rounded shapes, gentle tilt-shift depth of field, golden-hour lighting.
Palette strictly: cream #FFF7EA backgrounds, leaf green #1F7A4D, hill green
#3FA36B, sun yellow #FFC23D, earth beige #EFE4CF, rain blue #2563A8, dark ink
#1D2B22. Accents of terracotta #9C3B23 only for danger (drought, erosion).
Clean, uncluttered compositions, soft shadows, subtle film grain.
Camera moves are slow and smooth (dolly, gentle orbit, push-in).
Mood: hopeful, grounded, human. Brazilian Cerrado landscape: red-ochre soil,
flat plateaus, scattered twisted trees, wide sky.
```

**Negative prompt (todas as cenas):**
```text
no text, no letters, no logos, no NASA logo, no watermarks, no neon cyberpunk,
no dark sci-fi HUD, no robots, no distorted hands or faces, no photorealistic
gore, no oversaturated colors, no fast cuts, no glitch effects
```
*(Texto na tela sempre é colocado depois, na edição; IA de vídeo escreve mal.)*

### Tipografia e gráficos (edição)
- **Títulos:** Bricolage Grotesque Bold, cor tinta `#1D2B22` ou creme sobre verde
- **Textos e rótulos:** DM Sans Medium
- **Cartões:** cantos bem arredondados (24px), fundo creme, borda `#E9DEC8`, sombra "degrau" verde-escura `0 5px 0 #155C39`
- **Animação de UI:** entram com leve bounce (escala 0.9 → 1.03 → 1), 250 ms
- **Selo de fonte** em cada dado: pílula pequena amarela `#FFEFC7`, texto `#7A4E00` ("MODIS · 2001–2025")

---

## 3. Roteiro cena a cena

| # | Tempo | Visual | Texto na tela | Narração (EN) |
|---|---|---|---|---|
Duas vozes: o **narrador** (inglês) e a **Dona Marta** (português do interior, com legenda em inglês). Ela fala três vezes: a dor, as perguntas e o final.

| # | Tempo | Visual | Texto na tela | Quem fala |
|---|---|---|---|---|
| 1 | 0–3s | Satélite orbitando a Terra, câmera desce até o Brasil | — | 🎙️ Narrador: "Satellites have watched every farm for 40 years." |
| 2 | 3–8s | Dona Marta de costas/perfil olhando o campo seco, solo rachado, enxurrada na encosta | legenda + **7 months bare soil** | 👩‍🌾 Marta (voz em off): **"Meu pai plantava assim… mas a chuva não vem mais como antes."** |
| 3 | 8–11s | Mão segura o celular: marca a fazenda no mapa, escolhe prioridades | **AgroIA** | 🎙️ "AgroIA learns her farm…" |
| 4 | 11–15s | Cartões do "raio-x do campo" surgem sobre a vista aérea da fazenda | selos MODIS · SMAP · GPM | 🎙️ "…turns NASA data into plain words…" |
| 5 | 15–18s | Comparação A / B / C; a B (soja + milheto) se destaca | **3 strategies, side by side** | 🎙️ "…and compares crop rotations." |
| 6 | 18–27s | **O agente.** Noite, varanda, relógio 2:14. Marta grava **mensagem de voz** para a AgroIA, celular perto da boca; respostas chegam com selo de fonte | legendas + **Every "what if". 24/7.** | 👩‍🌾 **"E se não chover em janeiro?"** … 👩‍🌾 **"E se eu plantar milheto em abril?"** … 🎙️ "Every 'what if'. Answered any time." |
| 7 | 27–30s | Amanhecer: campo verde coberto, Marta sorri. Fecha no logo | **AgroIA · Field Shift** / *Supports. Never decides.* | 👩‍🌾 (voz em off) **"Agora eu decido sabendo."** |

A cena 6 é a mais longa de propósito: é o diferencial. Marta perguntar **por voz** reforça a ideia: quem não gosta de digitar também consegue usar.

### Como fazer a Dona Marta falar

O difícil em vídeo com IA é a **boca sincronizar com a fala** (lip-sync). O roteiro foi montado para **quase não precisar disso**:

| Cena | Truque | Precisa de lip-sync? |
|---|---|---|
| 2 | Ela está de costas ou de perfil olhando o campo; a fala é voz em off (pensamento) | ❌ Não |
| 6 | O celular fica na frente da boca, como quem grava áudio no WhatsApp | ❌ Não (só um leve movimento) |
| 7 | Ela sorri em silêncio; a frase entra como voz em off | ❌ Não |

**De onde vem a voz (recomendado → alternativas):**
1. **⭐ Voz real gravada.** Uma pessoa de uns 50 anos, de preferência com sotaque do interior (mãe, tia, vizinha de alguém da equipe). Grava no celular, num quarto com roupa/cobertor (abafa o eco), 3 a 4 tomadas de cada frase. Grátis e é o que mais emociona.
2. **Vídeo com áudio nativo.** Ferramentas como o Veo 3 geram a cena já com a personagem falando e a boca sincronizada (no prompt: `She says in Brazilian Portuguese: "..."`). Funciona, mas o sotaque em português nem sempre convence e os créditos grátis são poucos.
3. **Lip-sync por cima.** Gravar a voz real e aplicar numa ferramenta de lip-sync (Kling, Hedra). Só vale se quiserem um plano com ela falando de frente; costuma gastar créditos.

**Direção para quem for gravar:** fala calma, sem "atuar". Na cena 2, cansada e um pouco preocupada. Na cena 6, baixinho, como quem fala de madrugada para não acordar ninguém. Na cena 7, tranquila e com um meio sorriso na voz.

---

## 4. Prompts por cena (colar após o STYLE)

**Cena 1 — Hook orbital (3s)**
```text
A small stylized satellite with golden solar panels glides slowly over a soft,
clay-textured Earth at dawn. The camera follows it, then gently tilts down
toward South America as the sunrise line crosses central Brazil. Warm rim
light, calm and majestic.
```

**Cena 2 — A dor (4s)**
```text
A 52-year-old Brazilian woman farmer with a wide straw hat and a simple work
shirt stands at the edge of a large bare field of cracked red-ochre soil
under a harsh, hazy sun, seen from behind over her shoulder (her face is not
visible). A shallow gully of eroded soil runs down a gentle slope beside her.
She slowly lowers her head toward the dry ground, worried but dignified.
Slow push-in from a medium-wide shot. Faint terracotta tones in the soil.
```

**Cena 3 — O app (3s)**
```text
Close-up of a farmer's weathered hand holding a modern smartphone over a
blurred Cerrado field. The phone screen is a plain bright green-screen
rectangle (for screen replacement). Soft golden light, shallow depth of
field, the thumb taps the screen gently.
```
➜ Na edição: substituir a tela pela gravação do onboarding (mapa Leaflet + chips de prioridade).

**Cena 4 — Raio-x do campo (5s)**
```text
Slow top-down drone shot over a rectangular farm on a flat Cerrado plateau,
stylized like a tilt-shift miniature. Soft translucent layers sweep across
the field like a scan: a blue wave for rain, a green gradient for vegetation,
gentle contour lines for slope on the east side. Clean, calm, no text.
```
➜ Na edição: cartões entram com bounce, um por vez (3 cabem em 5s):
- 🌱 "Bare soil from April to October" · MODIS
- 🌡️ "January is drier in 6 of the last 10 years" · SMAP · NASA POWER
- 🌧️ "Heavy November rain hits unprotected soil" · GPM

**Cena 5 — Estratégias (4s)**
```text
Slow sideways dolly over the same Cerrado field at warm midday. Half of the
field is bare red soil, the other half is covered by a dense green carpet of
millet cover crop, with a soft clean border between them. Calm, hopeful.
```
➜ Na edição: 3 cartões lado a lado por cima (A Atual 🔴, **B Soja + milheto 🟢 destacado com borda amarela**, C Soja + milho + capim 🟢).

**Cena 6 — O agente que responde os "e se" (8s) ⭐ diferencial**

Plano A (7–8s, um clipe):
```text
Night on the simple wooden porch of a small Brazilian farmhouse in the
Cerrado. Deep blue sky full of stars, a warm porch lamp, crickets. The same
52-year-old woman farmer sits on a bench, holding her smartphone; the screen
is a plain bright green-screen rectangle (for screen replacement) and its
soft glow lights her face. She holds the phone close to her mouth, speaking
quietly into it like recording a voice message, then lowers it, reads, relaxes
and gives a small relieved smile. Slow push-in from medium shot to close-up. Moonlight blue
#2563A8 tones mixed with warm yellow #FFC23D lamp light.
```
Plano B (se a ferramenta só gera 5s): dividir em *(a)* close do rosto preocupado iluminado pela tela, 3s, e *(b)* close da mão digitando, 5s.

➜ Na edição, a tela vira o **chat da AgroIA** (fundo creme, balões arredondados):
- Canto da tela: relógio **2:14 AM** e um selo verde pulsando **"AgroIA · online 24/7"**
- 🎤 Marta: balão de **mensagem de voz** (ondinha de áudio) com a transcrição embaixo: *"E se não chover em janeiro?"*; legenda do vídeo em inglês: *"What if it doesn't rain in January?"*
- 🌱 AgroIA (aparece digitando "…" por 0,5s): *"Your soybeans would be filling their grains then. In 6 of the last 10 years, January soil was drier than normal here. Sowing a bit earlier lowers that risk."* · selo **SMAP · NASA POWER**
- 🎤 Marta (mensagem de voz): *"E se eu plantar milheto em abril?"*; legenda: *"What if I plant millet in April?"*
- 🌱 AgroIA: *"Good fit: millet handles dry spells and covers your soil until October."* · selo **MODIS · GPM**
- Texto grande por cima no fim: **Every "what if". 24/7.**

As respostas precisam ser curtas (no máximo duas linhas na tela) e marcadas como ilustrativas se não vierem do app de verdade. Se o chat já estiver funcionando no dia, gravar a tela real é ainda melhor.

**Cena 7 — Amanhecer e final (3s)**
```text
Match cut from night to sunrise: the same woman farmer stands in a lush green
field of tall cover crop, smiling softly, hand resting on the plants. Gentle
breeze, warm backlight, lens flare. Camera pulls back slowly, leaving clean
cream-colored sky space at the top for a title.
```
A passagem da noite (cena 6) para o amanhecer (cena 7) é o "respiro" do vídeo: a dúvida da madrugada vira tranquilidade.
➜ Na edição: fundo vai para creme `#FFF7EA`, logo AgroIA + "Field Shift · NASA Space Apps 2026" + *Supports. Never decides.*

---

## 5. Som

### Música leve

- **Estilo:** acústica e leve, com violão dedilhado, um pouco de piano e, no máximo, um shaker suave. Sem bateria, sem batida eletrônica. 85–95 BPM. Clima "manhã no campo", de esperança calma.
- **Busca nos bancos grátis:** Pixabay Music ou YouTube Audio Library, com termos como `acoustic hopeful`, `gentle folk guitar`, `warm countryside`. Ver a licença (Pixabay não exige crédito).
- **Se quiserem gerar:** Suno ou Udio com o prompt
  ```text
  gentle acoustic folk instrumental, fingerpicked nylon guitar and soft piano,
  warm and hopeful, Brazilian countryside morning feeling, 90 BPM, no drums,
  no vocals, 30 seconds, soft ending
  ```
  (no plano grátis o uso é não comercial, o que serve para hackathon)

**Curva da música nos 30s:**
| Cena | Música |
|---|---|
| 1 | Entra baixinho, só violão |
| 2 | Fica quase muda: a fala da Marta e o vento seco são o centro |
| 3–5 | Cresce aos poucos, ganha o piano |
| 6 | Volta a baixar, só piano suave (é madrugada) |
| 7 | Abre cheia no amanhecer e termina numa nota longa com o logo |

**Mixagem:** quando alguém fala, a música abaixa uns 12–15 dB (o CapCut faz isso sozinho com "redução de música"/ducking). A voz sempre manda.

### Efeitos e vozes

- **SFX:** zumbido grave do espaço (cena 1), vento seco e cigarras (cena 2), "plim" suave a cada cartão (cena 4), grilos, bip de gravar áudio e som de mensagem chegando (cena 6), pássaros e vento nas folhas (cena 7)
- **Narrador:** inglês, calmo e caloroso. Pode ser alguém da equipe com bom inglês
- **Dona Marta:** ver "Como fazer a Dona Marta falar" na seção 3

---

## 6. Checklist de edição

- [ ] Tudo em 30s cravados (Space Apps corta o que passar)
- [ ] Texto na tela legível no celular: no mínimo 48px em 1080p
- [ ] Números marcados como exemplo ("illustrative") se não forem dados reais da fazenda
- [ ] Nenhum logo da NASA
- [ ] Legenda queimada (muita gente assiste sem som)
- [ ] Exportar MP4 H.264 e uma versão 9:16
