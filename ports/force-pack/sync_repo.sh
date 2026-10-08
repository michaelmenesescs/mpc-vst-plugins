#!/bin/bash
# sync_repo.sh: copy the toolkit and each port's generated skin files into the repo (ports/force-pack, ports/ml185)
set -e
cd "$(dirname "$0")"
R="${MV:-$HOME/force-work/mpc-vst-plugins}"
FP="$R/ports/force-pack"
cp hwskin.py hwpanel.py panels.py panel_specs.py m_*.py one.sh realwarn.py skin_only.sh sheet.py sync_repo.sh \
   gallery_data.py stage_all.py "$FP/"
mkdir -p "$FP/base"
rm -f "$FP"/base/*.conf "$FP"/base/*.art.json
cp base/*.conf "$FP/base/"
cp base/*.art.json "$FP/base/" 2>/dev/null || true
while read -r id dir; do
  src="../$dir"
  if [ "$id" = ml185 ]; then dst="$R/ports/ml185/vst"; else dst="$FP/ports/$id"; fi
  mkdir -p "$dst"
  rm -f "$dst"/panel_*.svg "$dst"/hw_*.svg
  for f in layout.conf module.json vst.json skin.css; do [ -f "$src/$f" ] && cp "$src/$f" "$dst/"; done
  cp "$src"/panel_*.svg "$dst/" 2>/dev/null || true
  cp "$src"/hw_*.svg "$dst/" 2>/dev/null || true
  cp "$src"/knob_*.svg "$dst/" 2>/dev/null || true
done < ports.txt
echo synced
