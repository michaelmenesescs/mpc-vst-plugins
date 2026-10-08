#!/usr/bin/env python3
"""Rewrite the skin's Program Mode Q-Links for the Force's single row of 8 knobs.

MPC reads Program Mode Q-Links (the Q-Link modes that don't follow the plugin's page) as Q-Link 1..16 in a straight line,
so on a Force knob N is Q-Link N. shadow_skin numbers them column-wise for a 4x4 MPC grid, which put Pitch 4, Pitch 8,
Pulses 4... under knobs 1, 2, 3 (seen on a Force, 2026-10-08). Here knobs 1-8 = Pitch 1-8, bank 2 = Pulses 1-8."""
import json, os, sys

skin = sys.argv[1]
params = json.load(open(os.path.join(os.path.dirname(__file__), "params.json")))
params = params["params"] if isinstance(params, dict) else params
index = {p["key"]: i for i, p in enumerate(params)}
keys = ["pitch%d" % i for i in range(1, 9)] + ["pulses%d" % i for i in range(1, 9)]
prog = {"Q-Link %d" % (n + 1): index[k] for n, k in enumerate(keys)}
for f in ("Q-Links.json", "Q-Links - 8by1.json"):
    path = os.path.join(skin, "Plugin Skins", f)
    q = json.load(open(path))
    q["Program Mode Q-Links"] = prog
    json.dump(q, open(path, "w"), indent=4)
    print("patched", path)
