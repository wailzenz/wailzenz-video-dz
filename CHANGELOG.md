# Changelog

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
