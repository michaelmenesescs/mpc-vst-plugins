#!/usr/bin/env python3
"""Build every staged module repo into an MPC-VST installer zip, stage the zips, and write a manifest.

For each repo: gen vst.json (via gen_ports.py) -> tools/build_port.sh -> tools/release.py -> copy zip.
Failures are logged (log file per module) and recorded in the manifest, never fatal.
"""
import json
import os
import re
import shutil
import subprocess
import sys

WORK = os.path.expanduser("~/force-work")
MPC_VST = os.path.join(WORK, "mpc-vst-plugins")
MODDIR = os.path.join(WORK, "modules")
STAGING = os.path.expanduser("~/force-staging")
LOGS = os.path.join(STAGING, "logs")
BASH5 = "/opt/homebrew/bin/bash"

MODULES = [
    ("schwung-hush1", "charlesvestal/schwung-hush1"),
    ("schwung-303", "charlesvestal/schwung-303"),
    ("schwung-hank", "charlesvestal/schwung-hank"),
    ("schwung-braids", "charlesvestal/schwung-braids"),
    ("schwung-chiptune", "charlesvestal/schwung-chiptune"),
    ("move-anything-plaits", "j3threejay/move-anything-plaits"),
    ("move-everything-mrhyde", "handcraftedcc/move-everything-mrhyde"),
    ("denis-move", "filliformes/denis-move"),
    ("schwung-6W6", "athousanddetails/schwung-6W6"),
    ("schwung-8W8", "athousanddetails/schwung-8W8"),
    ("schwung-9W9", "athousanddetails/schwung-9W9"),
    ("schwung-cw-78", "athousanddetails/schwung-cw-78"),
    ("schwung-libpo32", "mestela/schwung-libpo32"),
    ("schwung-sophie", "mestela/schwung-sophie"),
    ("weird-dreams-move", "filliformes/weird-dreams-move"),
    ("schwung-space-delay", "charlesvestal/schwung-space-delay"),
    ("schwung-psxverb", "charlesvestal/schwung-psxverb"),
    ("schwung-midiverb", "charlesvestal/schwung-midiverb"),
    ("schwung-junologue-chorus", "charlesvestal/schwung-junologue-chorus"),
    ("schwung-tapescam", "charlesvestal/schwung-tapescam"),
    ("schwung-filter", "charlesvestal/schwung-filter"),
    ("schwung-ducker", "charlesvestal/schwung-ducker"),
    ("schwung-4keq", "athousanddetails/schwung-4keq"),
    ("schwung-busdriver", "legsmechanical/schwung-busdriver"),
]

LICENSE_MAP = [
    (r"MIT License", "MIT"),
    (r"GNU GENERAL PUBLIC LICENSE\s*\n\s*Version 3", "GPL-3.0-or-later"),
    (r"GNU GENERAL PUBLIC LICENSE\s*\n\s*Version 2", "GPL-2.0-or-later"),
    (r"Apache License\s*\n?\s*Version 2\.0", "Apache-2.0"),
    (r"BSD 3-Clause", "BSD-3-Clause"),
    (r"BSD 2-Clause", "BSD-2-Clause"),
    (r"ISC License", "ISC"),
]


def detect_license(repo):
    for fn in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
        p = os.path.join(repo, fn)
        if os.path.isfile(p):
            txt = open(p, encoding="utf-8", errors="replace").read()
            for pat, spdx in LICENSE_MAP:
                if re.search(pat, txt):
                    return spdx
    return None


def run(cmd, cwd, logf):
    logf.write("$ " + " ".join(cmd) + "\n")
    logf.flush()
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    logf.write(p.stdout + "\n")
    logf.flush()
    return p.returncode, p.stdout


def main():
    os.makedirs(LOGS, exist_ok=True)
    only = sys.argv[1:]
    mods = [m for m in MODULES if not only or m[0] in only]

    # 1. author vst.json for every module in one pass (keeps uids unique across modules)
    subprocess.run([sys.executable, os.path.join(WORK, "gen_ports.py")] +
                   [os.path.join(MODDIR, m[0]) for m in mods], check=True)

    manifest = []
    for name, slug in mods:
        repo = os.path.join(MODDIR, name)
        vdir = os.path.join(repo, "vst")
        logp = os.path.join(LOGS, name + ".log")
        row = {"name": name, "repo": slug, "commit": None, "build": "failed", "zip": None,
               "version": None, "reason": None}
        try:
            row["commit"] = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()
        except Exception:
            pass
        with open(logp, "w") as logf:
            mod = json.load(open(os.path.join(repo, "src", "module.json")))
            row["version"] = str(mod.get("version", "1.0.0"))
            # 2. build (armhf)
            rc, out = run([BASH5, os.path.join(MPC_VST, "tools", "build_port.sh"),
                           os.path.join(vdir, "vst.json")], repo, logf)
            if rc != 0:
                row["reason"] = "build_port.sh failed (rc=%d)" % rc
                manifest.append(row)
                print("FAIL build  %-24s %s" % (name, row["reason"]))
                continue
            cfg = json.load(open(os.path.join(vdir, "vst.json")))
            so = os.path.join(vdir, "build", cfg["so"])
            if not os.path.isfile(so):
                row["reason"] = "no .so produced (%s)" % cfg["so"]
                manifest.append(row)
                print("FAIL build  %-24s %s" % (name, row["reason"]))
                continue
            # 3. release
            skin = os.path.join(vdir, "build", "skin", "%s - VST - %s" % (cfg["vendor"], cfg["name"]))
            entry = os.path.join(vdir, "build", "pluginlist-entry.xml")
            lic = detect_license(repo) or "NOASSERTION"
            cmd = [sys.executable, os.path.join(MPC_VST, "tools", "release.py"),
                   "--so", so, "--skin", skin, "--entry", entry,
                   "--version", row["version"],
                   "--about", str(mod.get("description", cfg["name"]))[:200],
                   "--repo", slug, "--license", lic,
                   "-o", os.path.join(vdir, "dist")]
            rc, out = run(cmd, repo, logf)
            zips = []
            ddir = os.path.join(vdir, "dist")
            if os.path.isdir(ddir):
                zips = [f for f in os.listdir(ddir) if f.endswith("-mpc-armv7.zip")]
            if rc != 0 or not zips:
                row["reason"] = "release.py failed (rc=%d)" % rc
                manifest.append(row)
                print("FAIL release %-23s %s" % (name, row["reason"]))
                continue
            src_zip = os.path.join(ddir, zips[0])
            dst_zip = os.path.join(STAGING, zips[0])
            shutil.copy2(src_zip, dst_zip)
            row["build"] = "ok"
            row["zip"] = os.path.basename(dst_zip)
            manifest.append(row)
            print("OK   %-30s -> %s" % (name, os.path.basename(dst_zip)))

    json.dump(manifest, open(os.path.join(STAGING, "manifest.json"), "w"), indent=1)
    ok = sum(1 for r in manifest if r["build"] == "ok")
    print("\n== %d/%d built OK ==" % (ok, len(manifest)))


if __name__ == "__main__":
    main()