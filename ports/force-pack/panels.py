#!/usr/bin/env python3
"""Hardware panel layouts: each plugin's controls placed where the machine it models has them.

A panel is written as the hardware reads: a page is a list of bands (stacked top to bottom), a band is a list of
sections (left to right, like the printed sections of a front panel), a section is a list of rows of controls.

    page("808", [band(sec("BASS DRUM", ["bd_level", "bd_tone", "bd_decay"], ...), ...)])

A control is "key[:flags][=LABEL]": flags big (a larger knob), s (vertical slider), e (vertical option buttons),
h (horizontal option buttons), p (popup list), t (toggle), b (trigger button), r (text readout). Without flags an
option parameter becomes buttons (up to 4 options) or a popup, anything else a knob. "-" leaves a cell empty.
A section is sec(title, row, row, ...) where each row is a list (or one control string for a one-control row).

Q-Links follow the panel: each hardware row (across the band's sections, left to right) starts a new bank of 8, so
on a Force knobs 1-8 are the top row as printed. A page with more than 16 Q-Link controls gets nested sub-pages of
16. qorder="flat" packs controls without the row padding (a 4x4 grid: two rows per bank).

    panels.py <id>      writes skins/base/<id>.conf (then hwskin.py <id> styles it)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import hwskin  # noqa: E402

X0, X1 = 10, 1270
YT, YB = 92 + hwskin.HEAD, 708
GAP = 6
TITLE = 34

# cell width units / row height weights per kind
UNIT = {"txt": 0.9, "knob": 1.0, "big": 1.35, "s": 0.62, "e": 1.1, "h": 1.0, "p": 1.25, "t": 0.8, "b": 1.3, "r": 1.6, "-": 1.0}


def page(name, bands, qorder="rows"):
    return {"name": name, "bands": bands, "qorder": qorder}


def band(*sections, weight=None):
    return {"sections": list(sections), "weight": weight}


def sec(title, *rows, w=None):
    return {"title": title, "rows": [r if isinstance(r, list) else [r] for r in rows], "w": w}


# ---- parameters ----------------------------------------------------------------------------------------------
def load_params(vdir):
    s = open(os.path.join(vdir, "build", "params.h")).read()
    out = {}
    for m in re.finditer(r'\{\s*"([^"]+)",\s*"([^"]*)",\s*"[^"]*",\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*(\d+),\s*([^,]+),\s*(\d+)', s):
        key, name, lo, hi, _, nopts, _, mom = m.groups()
        out[key] = {"name": name, "nopts": int(nopts), "momentary": mom == "1"}
    return out


class Ctl:
    def __init__(self, spec, params):
        self.spec = spec
        if spec == "-":
            self.key, self.kind, self.label = None, "-", ""
            return
        if spec.startswith("txt:"):   # static text: a row name in a grid
            self.key, self.kind, self.label = None, "txt", spec[4:].upper()
            return
        spec, _, label = spec.partition("=")
        key, _, flags = spec.partition(":")
        if key not in params:
            raise SystemExit("panel: no parameter %r" % key)
        p = params[key]
        self.key = key
        kind = flags or ""
        if not kind:
            if p["momentary"]:
                kind = "b"
            elif p["nopts"] > 1:
                kind = "e" if p["nopts"] <= 4 else "p"
            else:
                kind = "knob"
        self.kind = kind
        self.nopts = p["nopts"]
        self.label = (label or p["name"]).upper()[:14]

    @property
    def unit(self):
        return UNIT.get(self.kind, 1.0)

    def height(self):
        k = self.kind
        if k in ("knob", "-"):
            return 1.0
        if k == "big":
            return 1.3
        if k == "s":
            return 1.55
        if k == "e":
            return 0.35 + 0.2 * self.nopts
        if k in ("p", "r", "h"):
            return 0.7
        return 0.65


# ---- layout ----------------------------------------------------------------------------------------------------
def render(pages, params):
    out = []
    for pg in pages:
        bands = pg["bands"]
        for b in bands:
            for s in b["sections"]:
                s["ctl"] = [[Ctl(c, params) for c in row] for row in s["rows"]]
        # band heights: sum of each row's tallest control, plus the section title
        bh = []
        for b in bands:
            nrows = max(len(s["ctl"]) for s in b["sections"])
            rows_h = [max([c.height() for s in b["sections"] if i < len(s["ctl"]) for c in s["ctl"][i]] or [1.0])
                      for i in range(nrows)]
            bh.append((b["weight"] or sum(rows_h)) + 0.32)
        total = YB - YT - GAP * (len(bands) - 1)
        y = YT
        lines = ["[tab %s]" % pg["name"]]
        qrows = []
        for b, h in zip(bands, bh):
            hb = total * h / sum(bh)
            secs = b["sections"]
            units = [s["w"] or max(sum(c.unit for c in row) for row in s["ctl"]) for s in secs]
            free = X1 - X0 - GAP * (len(secs) - 1)
            x = X0
            band_rows = {}
            for s, u in zip(secs, units):
                w = free * u / sum(units)
                fx, fy, fw, fh = int(x), int(y), int(w), int(hb)
                lines.append('frame x=%d y=%d w=%d h=%d%s' % (fx, fy, fw, fh, ' title="%s"' % s["title"] if s["title"] else ""))
                inner_top = fy + (TITLE if s["title"] else 8)
                rows = s["ctl"]
                rh = [max(c.height() for c in row) for row in rows]
                ry = inner_top
                for i, row in enumerate(rows):
                    hh = (fy + fh - 6 - inner_top) * rh[i] / sum(rh)
                    ru = sum(c.unit for c in row)
                    cx0 = fx + 4
                    for c in row:
                        cw = (fw - 8) * c.unit / ru
                        lines += place(c, cx0, ry, cw, hh)
                        if c.key and c.kind not in ("b", "r"):
                            band_rows.setdefault(i, []).append(c.key)
                        cx0 += cw
                    ry += hh
                x += w + GAP
            for i in sorted(band_rows):
                qrows.append(band_rows[i])
            y += hb + GAP
        lines += qlink_lines(pg["name"], qrows, pg["qorder"])
        out.append("\n".join(lines))
    return "\n\n".join(out) + "\n"


def place(c, x, y, w, h):
    if c.kind == "-":
        return []
    if c.kind == "txt":
        return ['text cx=%d cy=%d label="%s" size=1.2' % (int(x + w / 2), int(y + h / 2 - 10), c.label)]
    cx, cy = int(x + w / 2), int(y + h / 2)
    lab = c.label.replace('"', "")
    bw = int(min(w - 4, 130))
    small = w < 96 or len(lab) * 9.2 > bw   # the name would run into its neighbour's: smaller text
    ns = " ns=12" if small else ""
    if c.kind in ("knob", "big"):
        # MPC's knob box: the strip (2r + 10) plus name and value text, 2r + 61 px tall from cy - r - 5
        r = min(w * (0.36 if c.kind == "big" else 0.30), (h - 66) / 2)
        r = int(max(12, min(r, 52 if c.kind == "big" else 40)))
        top = y + (h - (2 * r + 61)) / 2
        return ['knob cx=%d cy=%d r=%d label="%s" key=%s bw=%d%s' % (cx, int(top + r + 5), r, lab, c.key, bw, ns)]
    if c.kind == "s":
        sh = int(max(60, h - 64))
        return ['slider_v cx=%d cy=%d w=%d h=%d label="%s" key=%s bw=%d%s' % (cx, int(y + 8 + sh / 2), 30 if w > 50 else 24,
                                                                           sh, lab, c.key, bw, ns)]
    if c.kind == "e":
        sh = int(max(20, min(30 if w < 200 else 64, (h - 34) / c.nopts - 2)))   # a wide, tall cell: big hardware buttons
        sw = int(min(w - 10, 135))
        return ['enum_v cx=%d cy=%d label="%s" key=%s sw=%d sh=%d' % (cx, cy + 14, lab, c.key, sw, sh)]
    if c.kind == "h":
        sw = int(min((w - 10) / c.nopts - 2, 135))
        return ['enum_h cx=%d cy=%d label="%s" key=%s sw=%d' % (cx, cy + 10, lab, c.key, sw)]
    if c.kind == "p":
        pw = int(min(w - 12, 240))
        extra = ""
        if c.nopts > 12:   # a long list opens as columns: narrow cells so all of them fit across the screen
            cols = -(-c.nopts // 12)
            extra = " cols=%d cw=%d" % (cols, min(pw, (1240 - 12) // cols - 2))
        return ['popup cx=%d cy=%d w=%d h=44 label="%s" key=%s%s' % (cx, cy + 12, pw, lab, c.key, extra)]
    if c.kind == "t":
        return ['toggle cx=%d cy=%d label="%s" key=%s bw=%d%s' % (cx, cy, lab, c.key, bw, ns)]
    if c.kind == "b":
        return ['button cx=%d cy=%d label="%s" key=%s' % (cx, cy, lab, c.key)]
    if c.kind == "r":
        return ['readout cx=%d cy=%d w=%d h=44 label="%s" key=%s' % (cx, cy + 12, int(w - 12), lab, c.key)]
    raise SystemExit("panel: unknown kind %s" % c.kind)


def qlink_lines(name, rows, order):
    slots = []
    for r in rows:
        slots += r
        if order == "rows" and len(slots) % 8:
            slots += ["-"] * (8 - len(slots) % 8)
    while slots and slots[-1] == "-":
        slots.pop()
    chunks = [slots[i:i + 16] for i in range(0, len(slots), 16)]
    chunks = [c for c in chunks if any(k != "-" for k in c)]
    out = []
    for n, c in enumerate(chunks):
        while c[-1] == "-":
            c.pop()
        title = name if len(chunks) == 1 else "%s %s" % (name, "ABCDEFGH"[n])
        out.append('qlinks "%s" = %s' % (title, ",".join(c)))
    return out


def build(pid):
    from panel_specs import PANELS
    vdir = os.path.join(WORK, hwskin.PORTS[pid])
    params = load_params(vdir)
    pages = PANELS[pid](params) if callable(PANELS[pid]) else PANELS[pid]
    used = {c for pg in pages for b in pg["bands"] for s in b["sections"] for row in s["rows"] for c0 in (row if isinstance(row, list) else [row])
            for c in [c0.partition("=")[0].partition(":")[0]] if c != "-"}
    missing = [k for k in params if k not in used and not k.endswith("__open")]
    text = "# hwpanel: hardware layout written by skins/panels.py (edit panel_specs.py, not this file)\n\n" + render(pages, params)
    os.makedirs(hwskin.BASE, exist_ok=True)
    open(os.path.join(hwskin.BASE, pid + ".conf"), "w").write(text)
    print("%-10s %d pages%s" % (pid, len(pages), ("; not placed: " + " ".join(missing)) if missing else ""))


if __name__ == "__main__":
    from panel_specs import PANELS
    for pid in sys.argv[1:] or list(PANELS):
        build(pid)
