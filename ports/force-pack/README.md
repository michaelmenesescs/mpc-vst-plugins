# Force pack: Schwung / Move ports with hardware panels

Twenty-three Schwung and Move-Everything modules built as MPC OS plugins for a Force, plus ML-185 (`ports/ml185`).
Each has a skin drawn as the front panel of the machine it models: the controls at the hardware's own positions,
the same control types (knobs, faders, slide switches, LED buttons, rotary selectors), its colours, knob caps and
printed graphics, and Q-Links in the panel's reading order (on a Force, knobs 1-8 are the panel's first row).
The panels carry the plugins' own names, never a manufacturer's logo. The module sources are their authors' repos
(`build-tools/build_all.py`); this folder keeps what is needed to rebuild them here.

| Plugin | Drawn as | Reference |
|---|---|---|
| 303 | TB-303 top panel and keyboard section, Devil Fish pots | Commons "Roland TB-303 Panel.jpg" |
| 8W8 | TR-808 instrument columns, plates, step keys | Commons "Roland TR-808 (large).jpg" |
| 9W9 | TR-909 section bars, 2x2 knob grids, cream keys | Commons "Roland TR-909 (large).jpg" |
| 6W6 | TR-606 level row, middle strip, black step section | Commons "Roland TR-606.jpg" |
| HUSH ONE | SH-101 slider sections, switches, performance panel | Commons "Roland SH-101.jpg" |
| CW-78 | CR-78 faders, master box, coloured rhythm selector | polynominal.com photo, published control list |
| TapeDelay | RE-201 face: VU, MODE SELECTOR rotary, chrome knobs | Commons "RE201 Face.JPG" |
| Junologue Chorus | Juno-60 chorus section, wood cheeks | Commons "Roland Juno-60.jpg" |
| 4K EQ | SSL E/G channel EQ, turned on its side | the SL4000 channel module layout |
| Midiverb | Midiverb with its printed program chart (per unit) | Commons "Alesis MIDIVerb.jpg" |
| Braids, Plaits | the modules in a rack, sister panels for extras | Mutable Instruments manual drawings |
| MrHyde | MicroFreak panel and matrix grid | Commons "MicroFreak.jpg" |
| Denis | Serge paperface row in a wooden boat, patch matrix | Commons "Serge Modular.jpg" |
| ML-185 | M185 / Metropolis-style stage columns | RYK M185, Intellijel Metropolis panels |
| Libpo32 | PO-32 circuit board, LCD, key grid | PO-32 descriptions (Sound On Sound) |
| Chiptune | Game Boy (DMG), LCD greens | Commons "Game-Boy-Original.jpg" |
| PSX Verb | PlayStation top: disc lid (DECAY), buttons | the SCPH-100x console |
| Bus Driver | Ableton Drum Buss device | the device's own panel |
| Hank | Yamaha DX-style panel (2-op FM) | DX7 / DX100 |
| Ducker, FILTER, TAPESCAM | 2U gain-reduction unit, Oberheim SEM-style filter, hi-fi cassette deck | no single unit: the classic forms |
| Weird Dreams | an invented boutique 8-voice analog drum machine | none (no hardware exists) |

## How a skin is made

1. `m_roland.py`, `m_fx.py`, `m_euro.py`, `m_misc.py` draw each machine with `hwpanel.Page`: every control placed at
   its panel position (plugin-area pixels, 1280 x 628), the SVG artwork around it (finish, printed legends, scales,
   stripes, screws, plates), knob and switch images (`hw_*.svg`), and `qrow()` Q-Link rows. Knob names are printed
   on the panel (`ns=0`; MPC still shows the live value under the knob) and touch widths narrow to their
   neighbours, so touch boxes never overlap. A rotary selector is a picture per position plus a tap-to-pick field.
   Plugin controls the hardware doesn't have go on further pages in the same finish.
   `panel_specs.py` maps plugin ids to these functions.
2. `panels.py <id>` writes the layout (`base/<id>.conf`) and its artwork and images (`base/<id>.art.json`).
   (Its grid layout, `page` / `band` / `sec`, is still there for a page with no hardware drawing.)
3. `hwskin.py <id>` writes the port's `vst/` files: `layout.conf` with theme colours, `panel_<n>.svg`, `hw_*.svg`,
   `skin.css`, and `"art": "html"` in vst.json.
4. `one.sh <id>...` runs 2-3, a skin-only build with previews (`skin_only.sh`, `preview/<id>/pN.png`), then
   `realwarn.py` (checker warnings that matter; open popup lists are ignored). `sheet.py <id>` makes a contact
   sheet of the previews.
5. `stage_all.py` compiles every plugin and writes the installer zips to `~/force-staging/hw-skins/`;
   `gallery_data.py` collects the previews and Q-Link banks into `gallery/`; `sync_repo.sh` copies the toolkit and
   each port's generated files here (`ports/<id>/`, `ports/ml185/vst/`).

`build-tools/` has the batch tools that made the ports (`gen_ports.py` writes vst.json/module.json; it regenerates
vst.json without the `layout`/`art` keys these skins need, so rerun `hwskin.py` after it).

## Status (2026-10-08)
Offline: every skin builds with 0 real checker warnings; previews compared with the reference photos; installer
zips staged. Not yet on a device: knob positions, the rotary selectors (picture + popup field) and Q-Link order
still need a check on the Force. Printed-only parts (sequencer keys, jacks, the 303's keyboard, the RE-201's input
knobs, Braids' FINE / MODULATION) are artwork: they don't respond to touch.
