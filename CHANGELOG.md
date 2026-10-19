# Changelog

## 1.0.0 — 2026-10-19

First release. Based on **majed-video 6.0.1** by Majed Alzaabi, plus ffmpeg-skill 2.10.4 and the sound-effects skill.

### Added — the Algerian layer
- **Darija transcription** (`dz-reel/scripts/02a_transcribe_dz.py`): whisper.cpp large-v3 on the Mac GPU with a Darija prompt, the Algerian
  Hadra-ASR model, or openai-whisper large-v3 on any OS; `--engine compare` and `--save-default` to pick the best engine per speaker.
- **Arabic glosses for French/English terms** in captions (`"gloss"` in `fixes.json`): «normal "عادية"»; Latin terms highlighted automatically;
  a warning lists terms without a gloss.
- **Algerian hook rules** (`22_hook.py`, `DZ_DIALECT=dz`): flags Gulf/Levantine/Egyptian words with their Darija equivalents, knows Darija
  question/contrast/story words and numbers (زوج، تلاتة…). `DZ_DIALECT=kw` restores the original rules.
- **Darija guide** for everything Claude writes: `dz-reel/references/dialect-dz.md`.
- Darija question words in podcast question detection (`15_podcast.py`).
- `setup/setup-mac.sh` (one-command install into `~/.wailzenz-video-dz`) and `setup/env.sh`.
- Docs in Arabic, English and French.

### Fixed
- French/English phrases were reversed in captions, hook cards, podcast captions and the studio preview («le montage» → «montage le»;
  English-only lines read backwards). Each Latin run is now laid out left-to-right inside the RTL line.
- `dz-ffmpeg`: ASS captions now use `Encoding=-1` for Arabic/Hebrew; upstream's `1` scrambled the word order of Arabic lines.

### Changed
- Skills renamed: video-ad-editor → `dz-reel`, podcast-video → `dz-podcast`, montage-video → `dz-montage`, motion-video → `dz-motion`,
  thumbnail-video → `dz-thumbnail`, ffmpeg-skill → `dz-ffmpeg`, sound-effects → `dz-sound-effects`.
- User data moved from `~/.video-ad-editor` to `~/.wailzenz-video-dz`. Updates go through the plugin manager only.
- Removed the upstream author's partner discount code and the pointer to his separate DaVinci add-on.
