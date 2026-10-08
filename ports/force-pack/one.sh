#!/bin/bash
# one.sh <id>...: rebuild each plugin's skin + previews from its panel spec and theme, then list real warnings
cd "$(dirname "$0")"
for id in "$@"; do
  dir=$(awk -v i="$id" '$1==i{print $2}' ports.txt)
  python3 panels.py "$id" >/dev/null && python3 hwskin.py "$id" >/dev/null
  ./skin_only.sh "../$dir/vst.json" "preview/$id" > "logs_$id.txt" 2>&1 || echo "FAIL $id"
  python3 realwarn.py "$id"
done
