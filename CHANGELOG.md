# Changelog

## 1.2.0 — 2026-10-20

### Added — captions never cover the face, always under the chin
- `23_headcrop.py` also writes the face track (`studio.json` → `face`: head top and chin every 0.1 s; the chin includes ~10% of the
  face height for a beard). Run it on every video.
- **`underChin()`**: wherever a caption sits over the full-screen picture (`R_FULL`, `R_OVT`, `R_OVB`; card, plain-text and big-word
  styles), its top goes under the chin. A `theme.json` → `capY` above the head is overridden.
- **`chinLift()`**: on a close-up, a full-screen scene's video slides up so the caption fits under the chin above Instagram's caption
  zone — only as far as the hair allows, never in a scene with a cut-out / behind-the-head effect, and only when it saves at least one
  caption. Card captions drop to one line a page when two lines don't fit. `theme.json` → `"chinLift": false` turns it off.
- **`08_safe_check.js`** reports each lift and fails (exit 3) on any caption that still lands on the face, with the sentence's times —
  give it `R_UP` / `R_DOWN` or `nocap`.
- House-style rule 13 in `dz-reel`; docs and READMEs.
- `safe.json` → `"ignore": [{s, e, why}]` in `08_safe_check.js`: a full-frame background graphic (a sticker's halftone) no longer
  reads as 100% ink; each ignored window is printed with its reason, and its text is checked by eye.
- `stickerFreeze` takes `ty` (the word sticker's height), so it can stay above the 1500 band.

### Fixed — first fully English video
- English/French videos are recognised (no Arabic letters in `fixes.json`): no Arabic-gloss warnings, and Latin words are no
  longer all highlighted.
- Latin caption words keep their punctuation on the right («have.», was «.have») — the page is right-to-left.
- The highlight pill sweeps in reading order (Latin left → right) and the letters it hasn't reached stay readable (was «oney.»).
- A sentence's first word can be timed late too (a clip that opens mid-word): the voice-onset snap now also moves it back
  (0.26 → 0.05 s on the test). Darija timings are unchanged.
- The sentence grouping no longer splits a sentence's last word into a caption of its own when the 12-word limit is reached.
- `stickerFreeze`'s word sticker was white on white with a dark theme — it now uses the darker theme colour.

### Removed
- The upstream author's paid-course promotion that `dz-reel` added to the end of every delivery.

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
