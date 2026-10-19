# wailzenz-video-dz — source this at the start of every shell command:
#   source "<plugin>/setup/env.sh"
# Puts the plugin's tools first: ffmpeg-full, its Python 3.12 env (python3, pip, whisper, torch…), Node modules,
# and the Whisper models folder. Everything lives in $WVD_HOME (default ~/.wailzenz-video-dz), made by setup-mac.sh.
if [ -n "$BASH_VERSION" ]; then _wvd_src="${BASH_SOURCE[0]}"
elif [ -n "$ZSH_VERSION" ]; then eval '_wvd_src="${(%):-%x}"'
else _wvd_src="$0"; fi
export WVD_ROOT="$(cd "$(dirname "$_wvd_src")/.." && pwd)"
unset _wvd_src
export WVD_HOME="${WVD_HOME:-$HOME/.wailzenz-video-dz}"
export PATH="$WVD_HOME/bin:$WVD_HOME/py/bin:$WVD_HOME/py/Scripts:$PATH"
export VIRTUAL_ENV="$WVD_HOME/py"
export NODE_PATH="$WVD_HOME/node_modules${NODE_PATH:+:$NODE_PATH}"
export WHISPER_CPP_MODELS="${WHISPER_CPP_MODELS:-$WVD_HOME/models}"
export DZ_DIALECT="${DZ_DIALECT:-dz}"                     # dz = Algerian Darija hook rules · kw = original Kuwaiti rules
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_SKIP_SKILLS=1   # only matters if HyperFrames is also installed
