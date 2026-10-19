# Installing wailzenz-video-dz

## 1. Install the plugin (any OS)

In Claude Code:

```
/plugin marketplace add wailzenz/wailzenz-video-dz
/plugin install wailzenz-video-dz@wailzenz-video-dz
```

Start a new Claude Code session afterwards so the skills load.

## 2. Install the tools — macOS (recommended)

Ask Claude *"set up the wailzenz-video-dz tools"*, or run:

```bash
bash ~/.claude/plugins/marketplaces/wailzenz-video-dz/setup/setup-mac.sh
```

Options: `--check` (only report), `--yes` (no questions), `--no-models`, `--with-hadra` (pre-download the Algerian model, ~1.8 GB).

What it installs (it skips anything already there):

| Where | What |
|---|---|
| Homebrew | `ffmpeg-full` (captions need its libass + HarfBuzz — the plain `ffmpeg` formula can't burn subtitles), `whisper-cpp`, `uv`, `node` |
| `~/.wailzenz-video-dz/py` | Python 3.12 with openai-whisper, PyTorch, transformers, peft, librosa, ffmpeg-normalize… (your system Python is not touched) |
| `~/.wailzenz-video-dz/models` | `ggml-large-v3-q5_0.bin` (Arabic, 1.1 GB), `ggml-large-v3-turbo-q5_0.bin` (English/French, 0.6 GB) from huggingface.co/ggerganov/whisper.cpp |
| `~/.wailzenz-video-dz/bin` | links to ffmpeg-full, DeepFilterNet 0.5.6 (voice cleanup, from its official GitHub release) |
| `~/.wailzenz-video-dz/node_modules` | `puppeteer-core` (drives your Google Chrome to render captions) |

You also need **Google Chrome** installed in `/Applications`.

**Hardware:** Apple Silicon with 8 GB RAM works (one heavy job at a time); 16 GB is comfortable. The Algerian Hadra engine peaks at about 6 GB of RAM — close other apps when you use it.

## 2b. Windows / Linux (experimental — reports welcome)

The skills run their scripts with `bash`, so on Windows use **Git Bash** (Git for Windows). Then install:

1. **Python 3.12**, and create the env: `py -3.12 -m venv "%USERPROFILE%\.wailzenz-video-dz\py"` (Linux: `python3.12 -m venv ~/.wailzenz-video-dz/py`), then
   `~/.wailzenz-video-dz/py/Scripts/pip install openai-whisper torch "transformers>=4.49" peft accelerate librosa soundfile numpy scipy matplotlib ffmpeg-normalize pillow`
   (with an NVIDIA GPU, install the CUDA build of PyTorch first — transcription is much faster).
2. **ffmpeg** with libass: on Windows the "full" build from gyan.dev; on Linux your distro's `ffmpeg`. Check `ffmpeg -filters | grep subtitles`.
3. **Node.js 20+** and **Google Chrome**, then `cd ~/.wailzenz-video-dz && npm i puppeteer-core`.
4. Transcribe with `--engine whisper` (whisper.cpp is optional here).

## Updating

```
claude plugin marketplace update wailzenz-video-dz && claude plugin update wailzenz-video-dz@wailzenz-video-dz
```

Then start a new session. Re-run `setup-mac.sh --check` after big updates.

## Uninstalling

```
/plugin uninstall wailzenz-video-dz@wailzenz-video-dz
```

and delete `~/.wailzenz-video-dz` (tools and models). The Homebrew packages stay; remove them with `brew uninstall` if you don't need them.

## Troubleshooting

| Problem | Fix |
|---|---|
| Arabic letters come out disconnected or reversed in a burned subtitle | You're using plain `ffmpeg`. Source `setup/env.sh` first (it puts ffmpeg-full first), and never use `drawtext` for Arabic. |
| French/English words in the wrong order | Make sure the project's `compose.html` was copied from this plugin's `compose.REFERENCE.html` (old projects keep their old copy). |
| `whisper-cli` not found / model missing | Run `setup-mac.sh`, or use `--engine whisper`. |
| The Mac freezes during transcription or rendering | Run one heavy job at a time; render with fewer workers; close Chrome tabs. |
