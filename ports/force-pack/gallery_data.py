#!/usr/bin/env python3
"""Collect the preview images and Q-Link banks of every plugin into gallery/ (data.js + img/*.jpg)."""
import json
import os
import re
import subprocess

import hwskin

MODELLED = {"303": "Roland TB-303 (with Devil Fish mods)", "8w8": "Roland TR-808", "6w6": "Roland TR-606",
            "9w9": "Roland TR-909", "cw78": "Roland CR-78", "braids": "Mutable Instruments Braids",
            "plaits": "Mutable Instruments Plaits", "mrhyde": "Arturia MicroFreak", "denis": "Serge modular",
            "hush1": "Roland SH-101", "hank": "2-operator FM, drawn as a Yamaha DX", "chiptune": "Nintendo Game Boy sound chip",
            "libpo32": "Teenage Engineering PO-32 Tonic",
            "breakslicer": "BreakSlicer: our own break slicer, drawn as a desktop unit (no hardware)", "weird": "WeirdDrums: a boutique 8-voice analog drum machine (no hardware)",
            "midiverb": "Alesis Midiverb", "psxverb": "Sony PlayStation SPU reverb", "tapedelay": "Roland RE-201 Space Echo",
            "juno": "Roland Juno-60 chorus", "busdriver": "Ableton Drum Buss", "4keq": "SSL 4000 E/G channel EQ",
            "ducker": "Sidechain ducker as a 2U gain-reduction rack unit", "filter": "Oberheim SEM-style state-variable filter",
            "tapescam": "Hi-fi cassette deck",
            "ml185": "RYK M185 stage sequencer"}
GROUP = {"303": "Synths", "braids": "Synths", "plaits": "Synths", "mrhyde": "Synths", "denis": "Synths", "hush1": "Synths",
         "hank": "Synths", "chiptune": "Synths", "8w8": "Drum machines", "6w6": "Drum machines", "9w9": "Drum machines",
         "cw78": "Drum machines", "libpo32": "Drum machines", "weird": "Drum machines", "ml185": "Sequencer"}

out = []
for pid in hwskin.PORTS:
    vdir = os.path.join(hwskin.WORK, hwskin.PORTS[pid])
    lay = open(os.path.join(vdir, "layout.conf")).read()
    labels = dict((k, l or k.upper().replace("_", " ")) for l, k in re.findall(r'label="([^"]*)" key=(\S+)', lay))
    tabs, sub = [], 0
    for block in re.split(r"^\[tab ", lay, flags=re.M)[1:]:
        name = block.split("]", 1)[0]
        qs = re.findall(r'^qlinks "([^"]*)" = (.*)$', block, re.M)
        banks = []
        for qn, keys in qs:
            ks = [k.strip() for k in keys.split(",")]
            banks.append({"name": qn, "b1": [labels.get(k, "") if k != "-" else "" for k in ks[:8]],
                          "b2": [labels.get(k, "") if k != "-" else "" for k in ks[8:16]]})
        src = os.path.join(hwskin.HERE, "preview", pid, "p%d.png" % sub)
        img = "img/%s_%d.jpg" % (pid, len(tabs))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-q:v", "4", os.path.join(hwskin.HERE, "gallery", img)],
                       check=True)
        tabs.append({"name": name, "img": img, "banks": banks})
        sub += max(1, len(qs))
    vj = json.load(open(os.path.join(vdir, "vst.json")))
    out.append({"id": pid, "name": vj["name"], "model": MODELLED[pid], "group": GROUP.get(pid, "Effects"), "pages": tabs})
open(os.path.join(hwskin.HERE, "gallery", "data.js"), "w").write("window.PLUGINS = " + json.dumps(out, indent=0) + ";\n")
print(len(out), "plugins,", sum(len(p["pages"]) for p in out), "pages")
