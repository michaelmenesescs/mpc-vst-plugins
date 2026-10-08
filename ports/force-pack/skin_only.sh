#!/usr/bin/env bash
# Rebuild only the skin (params.h, skin/, pluginlist entry) of a port, no compile: for trying out themes.
#   skin_only.sh path/to/vst.json [preview-dir]
set -euo pipefail
MV="${MV:-$HOME/force-work/mpc-vst-plugins}"
CFG="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
eval "$(python3 "$MV/tools/gen_vst.py" "$CFG" --shell)"
mkdir -p "$ROOT/$PORT/build"
docker run --rm -u "$(id -u):$(id -g)" -e HOME=/tmp -v "$ROOT":/w -v "$MV":/mv:ro -w /w mpc-vst-html-art \
  python3 /mv/tools/gen_vst.py "$PORT/vst.json" >/dev/null
if [ -n "${2:-}" ]; then
  mkdir -p "$2"; rm -f "$2"/p*.png
  S=$(ls -d "$ROOT/$PORT/build/skin/"*/)
  python3 "$MV/tools/studio.py" preview "${S}Plugin Skins" -o "$2/p%d.png" >/dev/null
fi
