#!/usr/bin/env python3
"""Author an MPC-VST port (vst/vst.json + vst/module.json) for a Schwung/Move-Everything module repo.

Usage: gen_ports.py <module_repo_dir> [more dirs...]

Parameter source, in order of preference:
  1. capabilities.chain_params (or top-level) in src/module.json
  2. a chain_params JSON string literal embedded in the module's C/C++ source
  3. capabilities.ui_hierarchy params (when given as objects)
Sections always come from ui_hierarchy when present.
Sources/cflags are extracted from scripts/build.sh (CMakeLists fallback).
"""
import glob
import json
import os
import re
import sys

EFFECT_TYPES = {"audio_effect", "audio_fx", "effect", "fx"}


def _unescape_c(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            out.append({"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "'": "'", "0": "\0"}.get(n, n))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def extract_chain_params_c(repo):
    """Find `strcmp(key, "chain_params")` then the JSON string literal it returns and parse it."""
    cands = []
    for pat in ("src/**/*.c", "src/**/*.cpp", "src/**/*.cc", "src/**/*.h"):
        cands += glob.glob(os.path.join(repo, pat), recursive=True)
    for f in cands:
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        # Pattern B: a generated header's `..._chain_params_json[] = "..."` array literal
        for am in re.finditer(r'chain_params[a-z0-9_]*_json\s*\[\]\s*=\s*', txt):
            stop = txt.find(";", am.end())
            if stop < 0:
                continue
            lits = re.findall(r'"(?:[^"\\]|\\.)*"', txt[am.end():stop])
            if lits:
                try:
                    data = json.loads("".join(_unescape_c(l[1:-1]) for l in lits))
                    if isinstance(data, dict):
                        data = data.get("chain_params")
                    if isinstance(data, list) and data:
                        return data
                except Exception:
                    pass
        m = re.search(r'"chain_params"\s*\)\s*==\s*0', txt)
        if not m:
            continue
        start = txt.find('"', m.end())
        if start < 0:
            continue
        stop = txt.find(";", start)
        if stop < 0:
            continue
        lits = re.findall(r'"(?:[^"\\]|\\.)*"', txt[start:stop])
        if not lits:
            continue
        joined = "".join(_unescape_c(l[1:-1]) for l in lits)
        joined = re.sub(r'%[-+0-9.]*s', '', joined)          # printf-built JSON (e.g. midiverb)
        joined = re.sub(r'%[-+0-9.]*[diufgxXeo]', '0', joined)
        try:
            data = json.loads(joined)
        except Exception:
            continue
        if isinstance(data, dict):
            data = data.get("chain_params")
        if isinstance(data, list) and data:
            return data
    return None


def synth_from_ui(ui):
    levels = (ui or {}).get("levels") or {}
    order = ["root"] + [k for k in levels if k != "root"]
    params, seen = [], set()
    for lv in order:
        if lv not in levels:
            continue
        for p in levels[lv].get("params", []):
            if not isinstance(p, dict) or "key" not in p or p["key"] in seen:
                continue
            seen.add(p["key"])
            e = {"key": p["key"], "name": str(p.get("short_name") or p.get("label") or p["key"])[:24],
                 "type": p.get("type", "float")}
            if p.get("options"):
                e["options"] = list(p["options"])
            else:
                e["min"] = p.get("min", 0)
                e["max"] = p.get("max", 127 if "max_param" in p else 1)
                if e["type"] == "int" or "max_param" in p:
                    e["display"] = "int"
            if "default" in p:
                e["default"] = p["default"]
            params.append(e)
    return params


def load_params(repo):
    mod = json.load(open(os.path.join(repo, "src", "module.json")))
    caps = mod.get("capabilities", mod)
    ui = caps.get("ui_hierarchy")
    cp = caps.get("chain_params") or mod.get("chain_params")
    src = "module.json"
    if not cp:
        cp = extract_chain_params_c(repo)
        src = "C source" if cp else None
    if not cp and ui:
        cp = synth_from_ui(ui)
        src = "ui_hierarchy"
    return mod, caps, cp or [], ui, src


def has_symbol(repo, sym):
    for pat in ("src/**/*.c", "src/**/*.cpp", "src/**/*.cc", "src/**/*.h"):
        for f in glob.glob(os.path.join(repo, pat), recursive=True):
            try:
                if re.search(re.escape(sym) + r'\s*\(', open(f, encoding="utf-8", errors="replace").read()):
                    return True
            except Exception:
                pass
    return False


def extract_sources(repo):
    bs = os.path.join(repo, "scripts", "build.sh")
    sources = []
    if os.path.isfile(bs):
        txt = open(bs, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'((?:/build/)?src/[^\s"\'\\;$(){}\[\]|&]+\.(?:cxx|cpp|cc|c))', txt):
            rel = m.group(1)
            if rel.startswith("/build/"):
                rel = rel[len("/build/"):]
            if "*" in rel or "?" in rel:
                for g in sorted(glob.glob(os.path.join(repo, rel))):
                    sources.append(os.path.relpath(g, repo))
            elif os.path.isfile(os.path.join(repo, rel)):
                sources.append(rel)
    if not sources:
        for g in sorted(glob.glob(os.path.join(repo, "src", "**", "*.c*"), recursive=True)):
            if re.search(r'/(tests?|tools)/', g):
                continue
            sources.append(os.path.relpath(g, repo))
    seen, out = set(), []
    for s in sources:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


SYS_HEADERS = {"string.h", "memory.h", "stdio.h", "stdlib.h", "math.h", "time.h", "errno.h",
               "assert.h", "ctype.h", "stdint.h", "stddef.h", "stdbool.h", "limits.h", "float.h",
               "stdarg.h", "strings.h", "unistd.h", "fcntl.h", "inttypes.h", "signal.h", "wchar.h"}


def _dir_has_sys(repo, rel):
    d = repo if rel in ("", ".") else os.path.join(repo, rel)
    return any(os.path.isfile(os.path.join(d, x)) for x in SYS_HEADERS)


def _header_index(repo):
    idx = []
    for root, dirs, files in os.walk(os.path.join(repo, "src")):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            if f.endswith((".h", ".hpp", ".hh", ".hxx")):
                idx.append(os.path.relpath(os.path.join(root, f), repo))
    return idx


def cflags_for(repo, sources):
    """Precise include roots: for each `#include "x/y.h"` find where that path lives and add the root
    it resolves from. Source dirs that directly contain a SYSTEM header (a vendored `string.h`) are
    left off the search path so they cannot shadow the real one."""
    roots = ["src"]
    roots += [os.path.dirname(s) for s in sources if not _dir_has_sys(repo, os.path.dirname(s))]
    idx = _header_index(repo)
    by_suffix = {}
    for h in idx:
        by_suffix.setdefault(h, []).append(h)
        by_suffix.setdefault(h.split("/")[-1], []).append(h)
    for s in sources:
        p = os.path.join(repo, s)
        if not os.path.isfile(p):
            continue
        for inc in re.findall(r'#\s*include\s+"([^"]+)"', open(p, encoding="utf-8", errors="replace").read()):
            if "/" not in inc and inc in SYS_HEADERS:
                continue  # a bare system header name: resolvable to the system copy, never via -I
            for h in by_suffix.get(inc, []) + by_suffix.get(inc.split("/")[-1], []):
                if h.endswith(inc):
                    root = h[: len(h) - len(inc)].rstrip("/")
                    roots.append(root if root else ".")
                    break
    seen, out = set(), []
    for r in roots:
        if r and r not in seen and not _dir_has_sys(repo, r):
            seen.add(r)
            out.append("-I" + r)
    return out


def build_sh_flags(repo):
    """-D / -I / -include flags the module's own build.sh uses (e.g. -DTEST, -Isrc/third_party/eurorack)."""
    bs = os.path.join(repo, "scripts", "build.sh")
    if not os.path.isfile(bs):
        return []
    txt = open(bs, encoding="utf-8", errors="replace").read()
    flags = []
    for m in re.finditer(r'(?<!\S)(-D[A-Za-z_][A-Za-z0-9_]*(?:=[^\s"\'\\]+)?)', txt):
        flags.append(m.group(1))
    for m in re.finditer(r'(?<!\S)(-I[^\s"\'\\;)]+)', txt):
        flags.append(m.group(1))
    for m in re.finditer(r'(?<!\S)(-include)\s+([^\s"\'\\;)]+)', txt):
        flags += [m.group(1), m.group(2)]
    seen, out = set(), []
    for f in flags:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def cxx_std(repo):
    """The -std=gnu++NN the module's own build.sh asks for, else gnu++14."""
    bs = os.path.join(repo, "scripts", "build.sh")
    if os.path.isfile(bs):
        m = re.search(r'-std=(?:gnu\+\+|c\+\+)(\d+[a-z]?)', open(bs, encoding="utf-8", errors="replace").read())
        if m:
            return "-std=gnu++" + m.group(1)
    return "-std=gnu++14"


def so_name(mod, repo):
    mid = mod.get("id") or os.path.basename(repo)
    return re.sub(r'[^a-z0-9_-]', '-', str(mid).lower()) + ".so"


def uid_for(name, used):
    al = re.sub(r'[^A-Za-z0-9]', '', name)
    base = (al + "XXXX")[:4]
    cand, n = base, 0
    while cand in used:
        n += 1
        cand = (base[:3] + str(n))[:4]
    used.add(cand)
    return cand


def version_int(v):
    p = [int(x) for x in re.findall(r'\d+', str(v))[:3]] + [0, 0, 0]
    return p[0] * 10000 + p[1] * 100 + p[2]


def main():
    used_uids = set()
    for repo in sys.argv[1:]:
        repo = os.path.abspath(repo)
        mod, caps, params, ui, psrc = load_params(repo)
        name = str(mod.get("name") or os.path.basename(repo))
        vendor = str(caps.get("author") or mod.get("author") or "Move Everything")
        vendor = re.sub(r'\s*[Cc]ommunity\s*', '', vendor)
        vendor = re.sub(r'[\\/:*?"<>|]+', ' ', vendor)          # no path chars: '/' would nest the skin folder
        vendor = re.sub(r'\s+', ' ', vendor).strip() or "Move Everything"
        ctype = str(caps.get("component_type", ""))
        effect = ctype in EFFECT_TYPES or (bool(caps.get("audio_in")) and not caps.get("audio_out"))
        # Effects export move_audio_fx_init_v2 (in-place process_block); instruments export
        # move_plugin_init_v2 (render). Each needs its own adapter.
        is_fx = has_symbol(repo, "move_audio_fx_init_v2") and not has_symbol(repo, "move_plugin_init_v2")
        if is_fx:
            effect = True
        uid = uid_for(name, used_uids)
        so = so_name(mod, repo)
        vdir = os.path.join(repo, "vst")
        os.makedirs(vdir, exist_ok=True)
        json.dump({"id": mod.get("id"), "name": name,
                   "capabilities": {"chain_params": params, "ui_hierarchy": ui}},
                  open(os.path.join(vdir, "module.json"), "w"), indent=1)
        cfg = {"name": name, "vendor": vendor, "uid": uid,
               "version": version_int(mod.get("version", "1.0.0")), "so": so, "module": "module.json"}
        if is_fx:
            cfg["adapter"] = "schwungfx"
        if effect:
            cfg["effect"] = True
        sources = extract_sources(repo)
        cflags = cflags_for(repo, sources)
        for f in build_sh_flags(repo):
            if f not in cflags:
                cflags.append(f)
        cflags = [c for c in cflags if not (c.startswith("-I") and _dir_has_sys(repo, c[2:]))]
        if any(s.endswith((".cc", ".cpp", ".cxx")) for s in sources):
            cflags.append(cxx_std(repo))
        libs = ["-lm"]
        base = [os.path.basename(s) for s in sources]
        if len(base) != len(set(base)):   # e.g. two Blip_Buffer.cpp (nes + gb emu): upstream localizes them
            libs.append("-Wl,--allow-multiple-definition")
        cfg["build"] = {"root": "..", "sources": sources, "cflags": cflags, "libs": libs}
        json.dump(cfg, open(os.path.join(vdir, "vst.json"), "w"), indent=1)
        print("%-26s params=%-4d (%-11s) sources=%-4d effect=%s" % (
            os.path.basename(repo), len(params), psrc, len(sources), effect))


if __name__ == "__main__":
    main()