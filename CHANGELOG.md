# Changelog

## 1.1.0 — 2026-10-20

### Added — overlay bands (not always a 50/50 split)
- **`R_OVT` / `R_OVB` layouts**: the face keeps the whole frame and the panel sits in a band about 20% of the height — on top
  (y ≈ 260–480, under Instagram's top bar) or at the bottom (y ≈ 1230–1410, above Instagram's caption zone). `panelIn` places it by
  itself. With `R_OVB` the caption moves up above the band; with `R_OVT` it never rises into the band (also when `theme.json` sets `capY`).
- **`glass(x, y, w, h, r, a)`**: a semi-transparent card in the theme colour, so a panel doesn't need a black background.
  **`dsh()`**: a dark soft shadow for icons drawn straight on the video.
- **House-style rule 12** in `dz-reel`: mix the bands with the split screens; bands for light moments (step counter, icons,
  progress), split screens for heavy explainers; `R_OVB` only with room under the chin — on a close-up use `R_OVT`.
- Examples `sStep` (top band: glass card, step pill, icons, segmented progress bar) and `sFlow` (bottom band, transparent) in
  `examples/scenes.example.js`. Docs: layout table, `docs/img/overlay-band.png`.

### Fixed
- Documented that numbers or Latin text inside a panel need `T(…, 'ltr')` — the canvas is right-to-left, so «01 / 03» came out as «03 / 01».

## 1.0.0 — 2026-10-20

First public release. Based on **majed-video 6.0.1** by Majed Alzaabi (MIT) — the engine, the 100 motion moves and the editing
method are his. This release adds the Algerian layer and a house style on top.

### Added — the Algerian layer
- **Darija transcription** (`dz-reel/scripts/02a_transcribe_dz.py`): whisper.cpp large-v3 on the Mac GPU with a Darija prompt and
  DTW word timing (plus snapping each sentence start to the real voice onset — plain whisper.cpp times ran ~0.5 s early), the
  Algerian Hadra-ASR model (needs ~16 GB RAM), or openai-whisper large-v3 on any OS; `--engine compare` / `--save-default`.
- **Arabic glosses for French/English terms** (`"gloss"` in `fixes.json`): «normal "عادية"» — first occurrence only by default,
  punctuation after the gloss, never alone on a caption page; Latin terms highlighted; a warning lists terms without a gloss.
- **Algerian hook rules** (`22_hook.py`, `DZ_DIALECT=dz`): flags Gulf/Levantine/Egyptian words with their Darija equivalents, knows
  Darija question/contrast/story words and numbers (زوج، تلاتة…). `DZ_DIALECT=kw` restores the original rules.
- **Darija guide** for everything Claude writes: `dz-reel/references/dialect-dz.md`. Darija question words in podcast mode.
- `setup/setup-mac.sh` (one-command install into `~/.wailzenz-video-dz`) and `setup/env.sh`. Docs in Arabic, English and French.

### Added — the house style
- **`R_UP` layout**: face on top, caption under it, animation panel at the bottom (`panelIn` moves there by itself) — alternate it
  with `R_DOWN` / `R_LOWER` / `R_FULL`.
- **Rules in the skill**: full scene design every time; panels never duplicate the caption (visuals, not words); careful cutting;
  alternating panel positions; scenes tied to word times. Example: `examples/scenes.example.js`.
- **Careful cutting** (`01_cut_plan.py`): silence measured against the clip's own noise floor (not a fixed −32 dB that clipped soft
  Darija word endings), only pauses ≥ 0.55 s, breaths don't split a pause, more room after a word than before, edges pushed out of
  the voice, and a self-check that flags any cut touching speech.

### Fixed
- French/English phrases were reversed in captions, hook cards, podcast captions and the studio preview («le montage» → «montage le»).
- The motion kit had no canvas in reels (it looked for `window.X`) and ignored the theme colours; its timeline was hard-coded purple
  (on the engine's own banned list) and highlighted icons red — all now use `theme.json`.
- The automatic brightness fix (`25_scopes.py`) lifted a black backdrop to milky grey; dark videos now get a black-preserving curve.

### Changed
- Skills renamed: video-ad-editor → `dz-reel`, podcast-video → `dz-podcast`, montage-video → `dz-montage`, motion-video → `dz-motion`,
  thumbnail-video → `dz-thumbnail`. User data in `~/.wailzenz-video-dz`. Updates only through the plugin manager.
- Removed the upstream author's partner discount code and the pointer to his separate DaVinci add-on.
