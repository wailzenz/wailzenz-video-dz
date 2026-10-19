# Third-party notices

wailzenz-video-dz is © 2026 wailzenz (MIT, see [LICENSE](LICENSE)) and contains work by others, redistributed under their licenses.

## Bundled in this repository

| Component | Where | Author | License |
|---|---|---|---|
| **majed-video 6.0.1** (video-ad-editor + motion/podcast/montage/thumbnail skills) — the editing engine, motion moves, scripts and method | `skills/dz-reel`, `skills/dz-podcast`, `skills/dz-montage`, `skills/dz-motion`, `skills/dz-thumbnail` | Majed Alzaabi — [majedphotos/video-ad-editor](https://github.com/majedphotos/video-ad-editor) | MIT (`skills/dz-reel/LICENSE-majed-video`) |
| **ffmpeg-skill 2.10.4** | `skills/dz-ffmpeg` | kajisho5 — [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | MIT (`skills/dz-ffmpeg/LICENSE`) |
| **sound-effects** skill (code) | `skills/dz-sound-effects` | Bart — [Barty-Bart/motion-graphics](https://github.com/Barty-Bart/motion-graphics); approach credited to Vox (@Voxyz_ai) | MIT (`skills/dz-sound-effects/LICENSE-code`) |
| Bundled sound effects | `skills/dz-sound-effects/sfx` | Kenney and Freesound authors (listed per file) | CC0 1.0 (`skills/dz-sound-effects/LICENSES.md`); one Mixkit sound is downloaded at run time, never stored here |
| three.js | `skills/dz-reel/motion/vendor.zip` | three.js authors | MIT (`vendor/three/LICENSE` inside the zip) |
| Fonts: Cairo, Tajawal, IBM Plex Sans Arabic, Noto Kufi Arabic, Readex Pro, Lalezar, Aref Ruqaa, Amiri Quran, Inter | `skills/dz-reel/motion/fonts` | their authors | SIL Open Font License 1.1 (`skills/dz-reel/motion/fonts/LICENSES.txt`) |
| Collage photos (Harvard bug log 1947, Apollo 13 MCC, IBM cards) | `skills/dz-reel/scripts/collage-assets` | Harvard/US Navy, NASA, US National Archives | Public domain (`collage-assets/LICENSES.md`) |
| Motion moves inspired by react-bits, gl-transitions, magicui, animate.css, Remotion, iart-ai and others (re-written, no copied code) | `skills/dz-reel/motion` | see `skills/dz-reel/motion/moves/CREDITS.md` | credited there |

## Downloaded by the setup script (not stored in this repository)

| Component | License |
|---|---|
| whisper.cpp and its GGML models (ggerganov/whisper.cpp, OpenAI Whisper weights) | MIT |
| openai-whisper, openai/whisper-medium | MIT |
| algerian-nlp/Hadra-ASR-whisper-medium (Algerian Darja adapter) | MIT |
| DeepFilterNet 0.5.6 | MIT / Apache-2.0 |
| PyTorch, transformers, peft, librosa and other Python packages | their own (BSD / Apache-2.0 / ISC …) |
| ffmpeg-full (Homebrew) | GPL-3.0-or-later — installed on your machine, not redistributed |
| puppeteer-core | Apache-2.0 |

## License texts

### majed-video

```
MIT License

Copyright (c) 2026 Majed Alzaabi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### ffmpeg-skill

```
MIT License

Copyright (c) 2026 kajisho5

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### sound-effects (Barty-Bart/motion-graphics)

```
MIT License

Copyright (c) 2026 Bart

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The Geist and Geist Mono fonts in skills/motion-broll/engine/fonts are
licensed separately under the SIL Open Font License 1.1 (see OFL-Geist.txt).
Icon paths are adapted from Lucide (ISC License).
```
