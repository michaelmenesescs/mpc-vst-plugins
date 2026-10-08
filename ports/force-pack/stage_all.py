#!/usr/bin/env python3
"""Build every plugin with its hardware skin and write the installer zips to ~/force-staging/hw-skins/ (plus a log
per plugin and a summary). Nothing touches a device. Uses build_all.py's repo list and license detection."""
import json
import os
import subprocess
import sys

import hwskin

WORK = hwskin.WORK
MV = os.path.join(WORK, "mpc-vst-plugins")
OUT = os.path.expanduser("~/force-staging/hw-skins")
sys.path.insert(0, WORK)
import build_all  # noqa: E402

SLUG = dict(build_all.MODULES)
os.makedirs(os.path.join(OUT, "logs"), exist_ok=True)


def run(cmd, cwd, log):
    return subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT).returncode


summary = []
for pid in sys.argv[1:] or list(hwskin.PORTS):
    vdir = os.path.join(WORK, hwskin.PORTS[pid])
    repo = os.path.dirname(vdir)
    cfg = json.load(open(os.path.join(vdir, "vst.json")))
    with open(os.path.join(OUT, "logs", pid + ".log"), "w") as log:
        if run(["/opt/homebrew/bin/bash", os.path.join(MV, "tools", "build_port.sh"), os.path.join(vdir, "vst.json")], repo, log):
            summary.append((pid, "FAIL build"))
            print(pid, "FAIL build", flush=True)
            continue
        skin = os.path.join(vdir, "build", "skin", "%s - VST - %s" % (cfg["vendor"], cfg["name"]))
        if pid == "ml185":
            run([sys.executable, os.path.join(vdir, "force_qlinks.py"), skin], repo, log)
            version, about, extra = "1.1.0", "8-stage step sequencer that plays another track over its own MIDI port", []
        else:
            mod = json.load(open(os.path.join(repo, "src", "module.json")))
            version = str(mod.get("version", "1.0.0"))
            about = str(mod.get("description", cfg["name"]))[:200]
            slug = SLUG.get(os.path.basename(repo))
            extra = ["--repo", slug, "--license", build_all.detect_license(repo) or "NOASSERTION"] if slug else []
        rc = run([sys.executable, os.path.join(MV, "tools", "release.py"), "--so", os.path.join(vdir, "build", cfg["so"]),
                  "--skin", skin, "--entry", os.path.join(vdir, "build", "pluginlist-entry.xml"), "--version", version,
                  "--about", about] + extra + ["-o", OUT], repo, log)
        summary.append((pid, "ok %s" % version if rc == 0 else "FAIL release"))
        print(pid, summary[-1][1], flush=True)
open(os.path.join(OUT, "SUMMARY.txt"), "w").write("".join("%-10s %s\n" % s for s in summary))
