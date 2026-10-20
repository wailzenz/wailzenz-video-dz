# How wailzenz-video-dz works

## The skills

| Skill | Use it for |
|---|---|
| `dz-reel` | A talking-head video → a finished 9:16 reel (the main one) |
| `dz-podcast` | Multi-camera sessions or long episodes → several reels, or a 16:9 episode |
| `dz-montage` | A folder of clips with no talking → a montage cut on the beat |
| `dz-motion` | A script or idea, no person on camera → a motion-graphics explainer |
| `dz-thumbnail` | Covers and thumbnails |

You don't call them by name: say what you want and Claude picks the right one.

## House style (built in)

1. **Full scene design every time** — split screens, explainer panels, moves, transitions, a depth moment, SFX, end card.
2. **Never duplicate the caption** — panels are visuals (icons, mockups, boards); they never show the words being captioned. Words big on screen → `nocap:true` for that sentence.
3. **Careful cutting** — only real pauses (≥ 0.55 s, measured against the clip's own noise floor), every cut in silence, hesitations removed whole or not at all, restarts keep the second take; `01_cut_plan.py` self-checks and `19_seam_check.py` re-listens after the render.
4. **Alternating layouts** — `R_DOWN` (animation top, face bottom) ↔ `R_UP` (face top, animation bottom) ↔ the overlay bands `R_OVT` / `R_OVB` ↔ `R_LOWER` (big panel, small face) ↔ `R_FULL`.
5. **Not always a 50/50 split** — a panel can be a band (about 20% of the height) over the full-screen video, at the top or the bottom, with no black background: drawn straight on the video, or on a semi-transparent `glass()` card. Bands are for light moments (a step counter, icons, a progress bar); split screens are for heavy explainers.

| Layout | Face | Panel | Caption |
|---|---|---|---|
| `R_FULL` | whole frame | — (or text over the video) | bottom |
| `R_DOWN` | lower card | top (`panelIn`) | between them |
| `R_UP` | top 960 px | bottom (`panelIn` moves there by itself) | under the face |
| `R_OVT` | whole frame | band on top, y ≈ 260–480, over the video | bottom (as usual) |
| `R_OVB` | whole frame | band at the bottom, y ≈ 1230–1410, over the video | above the band (needs room under the chin — on a close-up use `R_OVT`) |
| `R_LOWER` | small card at the bottom | big area on top | above the face card |

![A top overlay band: a semi-transparent card with a step pill, icons and a progress bar, over the full-screen video](img/overlay-band.png)

Overlay helpers in `compose.html`: `glass(x, y, w, h, r, a)` draws a semi-transparent card in the theme colour (`a` ≈ 0.5–0.6); `dsh()` sets a dark soft shadow for icons drawn straight on the video; numbers or Latin text inside a panel go through `T(text, x, y, font, colour, 'center', 'ltr')` so «01 / 03» doesn't come out reversed. Patterns: `sStep` and `sFlow` in the example below.

See [`examples/scenes.example.js`](../examples/scenes.example.js) for a full reel's scenes, tied to word times.

## A reel, step by step (`dz-reel`)

1. **Setup check** — `scripts/00_setup.sh` confirms ffmpeg, Python, Chrome and puppeteer-core.
2. **Your look** — on the first video, onboarding saves your colours, fonts, logo and name to `~/.wailzenz-video-dz/profile.json`.
3. **Cut plan** — real pauses out, every cut in silence, with a self-check (`01_cut_plan.py`).
4. **Transcription** — `02a_transcribe_dz.py` writes word-timed `a.json`.
5. **Correction + captions** — Claude fixes the Darija transcript into `fixes.json`, then `02_captions.py` builds `caps.json`.
6. **You approve the script** — the full transcript is shown; you say what to drop.
7. **Cuts, zooms, scenes, motion** — `03_cut_zoom.py`, then scenes designed in `compose.html`.
8. **Sound effects, final render, mastering, subtitles (SRT), cover.**
9. **Checks before delivery** — sync, loudness (≈ −14 LUFS), safe zones away from the app buttons, a contact sheet of frames.

## Transcription engines

```bash
python3 scripts/02a_transcribe_dz.py <work> [--engine auto|cpp|hadra|whisper|compare] [--lang ar|en|fr]
```

| Engine | What | Notes |
|---|---|---|
| `cpp` | whisper.cpp large-v3, Metal GPU | Default on a Mac. ~20 s for a 1-minute reel, ~2 GB RAM. Word times come from DTW alignment, and each sentence's first word is snapped to where the voice really starts (plain whisper.cpp times ran ~0.5 s early). Gets a short Darija prompt so it doesn't "correct" you into فصحى. |
| `hadra` | [algerian-nlp/Hadra-ASR-whisper-medium](https://huggingface.co/algerian-nlp/Hadra-ASR-whisper-medium) (MIT) | Trained on Algerian Darja. ~1.8 GB download. **Needs a 16 GB machine in practice** — on an 8 GB Mac it swapped to a halt on a 48 s clip, on the GPU and on the CPU (`WVD_TORCH_DEVICE=cpu`). Its published scores are self-reported — test it on your voice. |
| `whisper` | openai-whisper large-v3 | Any OS; NVIDIA GPU if present, else CPU (slow). |
| `compare` | runs `cpp` (or `whisper`) and `hadra` | Writes `a_cpp.json` / `a_hadra.json` side by side. Keep the one that needed fewer fixes: `--save-default hadra`. |

## `fixes.json` — the corrected transcript

```json
{
  "fix":   [["هادي","حاجة","normal","بزاف"], ["نخدمو","بـ","Claude","Code"]],
  "gloss": {"normal": "عادية", "Claude Code": "كلود كود"},
  "hot":   ["بزاف"],
  "fx":    {"خلاص": "drop"}
}
```

- `fix` — one list per Whisper sentence, **same word count** as Whisper's (timings stay exact). A string instead of a list = Whisper hallucinated; the words are spread over the sentence.
- `gloss` — the Arabic meaning shown in quotes after a French/English term. Keys are the term exactly as in `fix` (one word or a phrase). `02_captions.py` warns about any Latin term without one.
- `hot_latin` (default `true`) — Latin-script terms are highlighted automatically. `gloss_quotes` (default `""`) — e.g. `"()"` for parentheses.
- `gloss_repeat` (default `false`) — a term is glossed the first time it appears in the video only; `true` glosses every time. Punctuation after a term moves after its gloss («software "برمجيات"،»), and a gloss never starts a caption page on its own.
- `hot` — Arabic words highlighted when spoken. `fx` — word effects: drop, shake, crack, type, pulse, stretch (kashida), slam.

See [`examples/fixes.example.json`](../examples/fixes.example.json).

## Caption position

Filmed close to the camera, your chin sits where the caption box goes (bottom edge y = 1460). Put the box in the space above your head with `theme.json` → `"capY": 450` (its bottom edge in px; 450 keeps a 3-line page under the top safe zone), and `"capYFrom": 4.9` to start after an opening hook or "layers" sentence.

## The Algerian layer

- **Dialect rules** for everything Claude writes: `skills/dz-reel/references/dialect-dz.md` (spelling, common words, hooks, CTAs).
- **Hook checker** (`22_hook.py`): 3–8 words, Western digits, a hook device (number, question, contrast, curiosity, story), and Algerian words — it flags شلون/وايد/الحين and suggests كيفاش/بزاف/درك. `DZ_DIALECT=kw` restores the original Kuwaiti rules.
- **Latin word order**: the caption, hook, podcast and studio painters place words right-to-left, which used to reverse French/English phrases («le montage» → «montage le»). Each Latin run is now flipped back so it reads left-to-right.

## Privacy — what goes online

Your video and audio stay on your machine. The network is used only for:

- setup downloads (Homebrew, PyTorch, Whisper models, DeepFilterNet, puppeteer-core) and the first use of the Hadra model (Hugging Face);
- a 5-second update check against this repo's GitHub releases;
- **optional** features you ask for: Wikimedia Commons images for collages, free Microsoft Edge voices for motion videos (sends the script text), AI-generated scenes via fal.ai (paid, your own key).

## Data folder

`~/.wailzenz-video-dz/` (override with `WVD_HOME`): `py/`, `models/`, `bin/`, `node_modules/`, `profile.json` (your look), `config.json` (your default engine), `voice-samples/`.
