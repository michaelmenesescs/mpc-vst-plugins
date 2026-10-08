# Force pack: Schwung / Move ports with hardware panels

Twenty-three Schwung and Move-Everything modules built as MPC OS plugins for a Force, plus ML-185 (`ports/ml185`),
each with a skin that copies the front panel of the machine it models: the same sections in the same order, the
controls where the hardware has them, and Q-Links that follow the panel (on a Force, knobs 1-8 are the panel's top
row as printed, knobs 9-16 the next row). The module sources are their authors' repos (`build-tools/build_all.py`);
this folder keeps what is needed to rebuild them here.

## How a skin is made

1. `panel_specs.py` describes each panel as the hardware reads: pages, bands (top to bottom), sections (left to
   right, like the printed sections), rows of controls. Example: the 303's top band is WAVEFORM, TUNING, CUT OFF FREQ,
   RESONANCE, ENV MOD, DECAY, ACCENT, VOLUME; the 808 page is one column per instrument with LEVEL on top.
2. `panels.py <id>` turns that into a layout (`base/<id>.conf`): positions, knob sizes that fit MPC's touch boxes,
   and `qlinks` lines (each hardware row starts a bank of 8; more than 16 controls make Q-Link sub-pages A, B, C).
3. `hwskin.py <id>` styles it: theme colours, knob looks, the panel artwork (`panel_<n>.svg`: finish, header
   lettering, section plates) and `skin.css`, written into the port's `vst/` folder with `"art": "html"`.
4. `skin_only.sh <vst.json> [preview-dir]` builds just the skin and preview PNGs; `one.sh <id>...` runs 2-3 and then
   `realwarn.py`, which lists the skin checker's warnings that matter (it drops the overlaps an open popup list
   causes, since the list covers what is under it while open).
5. `stage_all.py` compiles every plugin and writes the installer zips to `~/force-staging/hw-skins/`.
   `gallery_data.py` collects the previews and Q-Link banks into `gallery/` (a page that shows every design).

`ports/<id>/` holds a copy of each port's generated files (vst.json, module.json, layout, css, panel drawings).
`build-tools/` has the batch tools that made the ports (`gen_ports.py` writes vst.json/module.json; note it
regenerates vst.json without the `layout`/`art` keys these skins need, so rerun `hwskin.py` after it).

## Status (2026-10-08)
Offline: every skin builds with no real checker warnings and renders previews; installer zips staged. Not yet on a
device: the panels, knob positions and Q-Link order still need a check on the Force.
