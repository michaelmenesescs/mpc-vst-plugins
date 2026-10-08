# Force pack: Schwung / Move ports with hardware-style skins

Twenty-three Schwung and Move-Everything modules built as MPC OS plugins for a Force, plus the hardware-style skin
generator. The module sources are their authors' own repos (listed in `build-tools/build_all.py`); this folder keeps
what is needed to rebuild them here.

- `build-tools/`: `gen_ports.py` writes each module's `vst/vst.json` + `vst/module.json`, `build_all.py` builds every
  module into an installer zip, `consolidate.py` writes the build manifest. They expect the module repos cloned under
  `~/force-work/modules/` and this repo at `~/force-work/mpc-vst-plugins`.
- `hwskin.py`: one theme per plugin, modelled on the hardware it emulates (303, 808, 606, 909, CR-78, SH-101,
  Braids/Plaits, MicroFreak, Serge, Space Echo, Midiverb, SSL channel EQ, Juno chorus, ...). It reads the port's
  base layout (`base/<id>.conf`) and writes `layout.conf`, `skin.css` and one `panel_<n>.svg` per page into the port's
  `vst/` folder, and sets `"art": "html"` in its vst.json. `ports/<id>/` holds a copy of each port's generated files.
- `skin_only.sh <vst.json> [preview-dir]`: rebuilds just the skin (no compile) and renders preview PNGs.

Status (2026-10-08): skins generated and previewed offline only; not yet installed on a device. Next: per-plugin
layouts that place the controls where the original hardware has them.
