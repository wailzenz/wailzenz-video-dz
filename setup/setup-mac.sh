#!/bin/bash
# wailzenz-video-dz — one-time setup for macOS (Apple Silicon recommended).
#
#   bash setup/setup-mac.sh            install everything that is missing (asks before big downloads)
#   bash setup/setup-mac.sh --yes      same, no questions
#   bash setup/setup-mac.sh --check    only report what is installed
#   bash setup/setup-mac.sh --no-models / --with-hadra
#
# Installs into $WVD_HOME (default ~/.wailzenz-video-dz): bin/ (ffmpeg links, deep-filter), py/ (Python 3.12),
# models/ (whisper.cpp), node_modules/ (puppeteer-core). Homebrew packages: ffmpeg-full, whisper-cpp, uv, node.
# Safe to run again: it skips what is already there.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(dirname "$HERE")"
WVD_HOME="${WVD_HOME:-$HOME/.wailzenz-video-dz}"
YES=0; CHECK=0; MODELS=1; HADRA=0
for a in "$@"; do case "$a" in
  --yes|-y) YES=1 ;; --check) CHECK=1 ;; --no-models) MODELS=0 ;; --with-hadra) HADRA=1 ;;
  *) echo "unknown option: $a"; exit 2 ;; esac; done
ok(){ printf '  ✅ %s\n' "$1"; }; miss(){ printf '  ⬜ %s\n' "$1"; MISSING=$((MISSING+1)); }; MISSING=0
ask(){ [ $YES = 1 ] && return 0; read -r -p "$1 [y/N] " r; [[ "$r" =~ ^[yYoO] ]]; }
have(){ command -v "$1" >/dev/null 2>&1; }

[ "$(uname -s)" = Darwin ] || { echo "❌ This script is for macOS. Windows/Linux: see docs/INSTALL.md"; exit 1; }
[ "$(uname -m)" = arm64 ] || echo "⚠️  Intel Mac: works, but transcription and rendering are much slower."

FFFULL="$(brew --prefix 2>/dev/null)/opt/ffmpeg-full/bin"
PY="$WVD_HOME/py/bin/python"
M_AR="ggml-large-v3-q5_0.bin"; M_EN="ggml-large-v3-turbo-q5_0.bin"
HF="https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
PYPKGS=(pip openai-whisper torch "transformers>=4.49" peft accelerate soundfile numpy scipy pillow sentencepiece protobuf)

status(){
  echo "wailzenz-video-dz setup — $WVD_HOME"
  have brew && ok "Homebrew" || miss "Homebrew (https://brew.sh)"
  [ -x "$FFFULL/ffmpeg" ] && [ -x "$WVD_HOME/bin/ffmpeg" ] && ok "ffmpeg-full (linked in $WVD_HOME/bin)" || miss "ffmpeg-full (brew) + link in $WVD_HOME/bin"
  have whisper-cli && ok "whisper.cpp" || miss "whisper-cpp (brew)"
  have uv && ok "uv" || miss "uv (brew)"
  have node && ok "node $(node -v)" || miss "node (brew)"
  [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ] && ok "Google Chrome" || miss "Google Chrome (https://www.google.com/chrome) — the caption engine renders with it"
  [ -x "$PY" ] && "$PY" -c "import whisper, torch, transformers, peft, soundfile, scipy" 2>/dev/null && ok "Python env" || miss "Python 3.12 env + packages"
  [ -d "$WVD_HOME/node_modules/puppeteer-core" ] && ok "puppeteer-core" || miss "puppeteer-core"
  [ -x "$WVD_HOME/bin/deep-filter" ] && ok "DeepFilterNet (voice cleanup)" || miss "DeepFilterNet"
  [ -f "$WVD_HOME/models/$M_AR" ] && ok "Whisper large-v3 (Arabic, 1.1 GB)" || miss "Whisper large-v3 (Arabic, 1.1 GB)"
  [ -f "$WVD_HOME/models/$M_EN" ] && ok "Whisper large-v3-turbo (English/French, 0.6 GB)" || miss "Whisper large-v3-turbo (0.6 GB)"
}
status
[ $CHECK = 1 ] && { [ $MISSING = 0 ] && echo "✅ ready" || echo "missing: $MISSING"; exit 0; }
[ $MISSING = 0 ] && [ $HADRA = 0 ] && { echo "✅ everything is installed"; exit 0; }

have brew || { echo "❌ Install Homebrew first: https://brew.sh — then run this again."; exit 1; }
echo; echo "This downloads about 4 GB (Homebrew packages, PyTorch, 2 Whisper models)."
ask "Continue?" || { echo "stopped"; exit 1; }
mkdir -p "$WVD_HOME/bin" "$WVD_HOME/models"

for f in ffmpeg-full whisper-cpp uv node; do
  brew list --formula "$f" >/dev/null 2>&1 || { echo "⏬ brew install $f"; brew install "$f" || exit 1; }
done
FFFULL="$(brew --prefix)/opt/ffmpeg-full/bin"
ln -sf "$FFFULL/ffmpeg" "$WVD_HOME/bin/ffmpeg"; ln -sf "$FFFULL/ffprobe" "$WVD_HOME/bin/ffprobe"   # ffmpeg-full is keg-only

if ! { [ -x "$PY" ] && "$PY" -c "import whisper, torch, transformers, peft, soundfile, scipy" 2>/dev/null; }; then
  echo "⏬ Python 3.12 env + packages (PyTorch is the big one)"
  [ -x "$PY" ] || uv venv --python 3.12 "$WVD_HOME/py" || exit 1
  uv pip install --python "$PY" "${PYPKGS[@]}" || exit 1
fi

if [ ! -d "$WVD_HOME/node_modules/puppeteer-core" ]; then
  echo "⏬ puppeteer-core"
  [ -f "$WVD_HOME/package.json" ] || echo '{"private":true}' > "$WVD_HOME/package.json"
  (cd "$WVD_HOME" && npm i --silent --no-fund --no-audit puppeteer-core) || exit 1
fi

if [ ! -x "$WVD_HOME/bin/deep-filter" ]; then
  echo "⏬ DeepFilterNet 0.5.6 (official release, ~28 MB)"
  T=aarch64-apple-darwin; [ "$(uname -m)" = arm64 ] || T=x86_64-apple-darwin
  curl -sSfL -o "$WVD_HOME/bin/deep-filter" "https://github.com/Rikorose/DeepFilterNet/releases/download/v0.5.6/deep-filter-0.5.6-$T" \
    && chmod +x "$WVD_HOME/bin/deep-filter" || echo "⚠️  DeepFilterNet download failed — voice cleanup falls back to ffmpeg filters"
fi

if [ $MODELS = 1 ]; then
  for m in "$M_AR" "$M_EN"; do
    [ -f "$WVD_HOME/models/$m" ] && continue
    echo "⏬ $m (from huggingface.co/ggerganov/whisper.cpp)"
    curl -sSfL --retry 3 -o "$WVD_HOME/models/$m.part" "$HF/$m" && mv "$WVD_HOME/models/$m.part" "$WVD_HOME/models/$m" || echo "⚠️  $m failed — run again later"
  done
fi

if [ $HADRA = 1 ]; then
  echo "⏬ Algerian model (algerian-nlp/Hadra-ASR-whisper-medium + openai/whisper-medium, ~1.8 GB)"
  "$PY" -c "from huggingface_hub import snapshot_download as d; d('openai/whisper-medium', allow_patterns=['*.json','*.safetensors','*.txt']); d('algerian-nlp/Hadra-ASR-whisper-medium')" \
    || echo "⚠️  download failed — it will retry on first use of --engine hadra"
fi

echo; MISSING=0; status
source "$HERE/env.sh"; (cd "$ROOT/skills/dz-reel" && bash scripts/00_setup.sh | tail -3)
