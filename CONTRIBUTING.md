# Contributing · المساهمة

شكراً على اهتمامك! Thanks for helping.

## Darija · الدارجة

The most useful contributions are about the language:

- **Spelling and word choices** → `skills/dz-reel/references/dialect-dz.md`.
- **Hook rules** (which words get flagged, Darija question/story words) → the `DIALECT_NAME == "dz"` block in `skills/dz-reel/scripts/22_hook.py`.
- **Regional variants** (Oran, Constantine, Algiers, the south…) — open an issue with examples first; we keep one default spelling and list variants.
- Tamazight/Kabyle captions are not supported yet — ideas welcome.

## Bugs

Open an issue with: what you asked Claude, the command that failed (`whisper.log`, terminal output), your Mac model and RAM, and — for
caption problems — a frame (`node scripts/04_render_frames.js <work> preview <seconds>` makes one). Don't post private footage.

## Pull requests

- Keep the original authors' credits and license files (see `THIRD_PARTY_NOTICES.md`).
- No assets you can't redistribute: sounds must be CC0 (or downloaded at run time), fonts OFL, images public domain or CC0.
- Test a render on a short clip before opening the PR, and say what you tested.
- Upstream bugs in majed-video are better fixed upstream too: [majedphotos/video-ad-editor](https://github.com/majedphotos/video-ad-editor).
