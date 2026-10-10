#!/usr/bin/env python3
"""Free-placed hardware pages: each control where the machine has it, and the panel artwork drawn around it.

panels.py lays out sections automatically. A hardware panel isn't a grid, though, so a Page here places every
control at its own position, in plugin-area pixels (0..1280 x 0..628, as the panel SVG), and collects the SVG
artwork (finish, printed labels, scales, stripes, logos) for the same page:

    p = Page("303")
    p.add(rect(0, 0, 1280, 628, "#c9cbcc"))             # artwork, back to front
    p.knob("cutoff", 420, 120, 34, "CUT OFF FREQ", img=K303, lab=-58)   # label printed 58 px above the centre
    p.qrow("waveform", "tuning", "cutoff", ...)          # Q-Links: one hardware row = one bank of 8

Knobs and sliders get ns=0 (the name is printed on the panel, as on the hardware; MPC still draws the live
value under the control) and a touch width narrowed to their neighbours (bw=), so touch boxes never overlap.
Option switches take the label from the panel too (label=""), and image looks hide the option text when the
page asks for it (Page(seg_text=False) -> skin.css).

Knob, switch and button images are SVG assets (Page.asset), written beside the layout by hwskin.py as hw_*.svg.
"""
import math
from html import escape

Y_OFF = 86
W, H = 1280, 628
LABEL_SCALE = 1.15     # shadow_skin.py's: value text box = round(26 * 1.15) px under a knob or slider


# ---- SVG helpers (plugin-area coordinates) -------------------------------------------------------------------
SANS = "FreeSans, Liberation Sans, Titillium Web, sans-serif"
NARROW = "Liberation Sans Narrow, FreeSans, sans-serif"
ROUND = "Titillium Web, FreeSans, sans-serif"


def T(x, y, s, size=13, fill="#111", weight=700, anchor="middle", font=SANS, sp=0.0, italic=False, extra="",
      stretch=None):
    """Text centred vertically on y. Inline style, so the renderer's own `text {}` rule can't override the font."""
    st = "font-family:%s;font-weight:%d;letter-spacing:%gem;" % (font, weight, sp)
    if italic:
        st += "font-style:italic;"
    tr = ""
    if stretch:   # horizontal scale about x (condensed / extended lettering)
        tr = ' transform="translate(%g 0) scale(%g 1) translate(%g 0)"' % (x, stretch, -x)
    return ('<text x="%g" y="%g" font-size="%g" fill="%s" text-anchor="%s" dominant-baseline="central" style="%s"%s%s>%s</text>'
            % (x, y, size, fill, anchor, st, tr, extra, escape(str(s))))


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=1, extra=""):
    s = ' stroke="%s" stroke-width="%g"' % (stroke, sw) if stroke else ""
    return '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s"%s%s/>' % (x, y, w, h, rx, fill, s, extra)


def line(x1, y1, x2, y2, stroke, sw=1, extra=""):
    return '<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g"%s/>' % (x1, y1, x2, y2, stroke, sw, extra)


def circle(x, y, r, fill, stroke=None, sw=1, extra=""):
    s = ' stroke="%s" stroke-width="%g"' % (stroke, sw) if stroke else ""
    return '<circle cx="%g" cy="%g" r="%g" fill="%s"%s%s/>' % (x, y, r, fill, s, extra)


def path(d, fill="none", stroke=None, sw=1, extra=""):
    s = ' stroke="%s" stroke-width="%g"' % (stroke, sw) if stroke else ""
    return '<path d="%s" fill="%s"%s%s/>' % (d, fill, s, extra)


def pt(x, y, r, a):
    """Point at radius r, angle a degrees (0 = up, clockwise)."""
    return x + r * math.sin(math.radians(a)), y - r * math.cos(math.radians(a))


def ticks(x, y, r0, r1, n=11, stroke="#111", sw=1.6, a0=-135, a1=135, major=None, r2=None):
    """A knob scale: n tick marks between angles a0..a1 from radius r0 to r1 (every `major`-th one out to r2)."""
    o = []
    for i in range(n):
        a = a0 + (a1 - a0) * i / max(1, n - 1)
        ro = r2 if (major and r2 and i % major == 0) else r1
        x0, y0 = pt(x, y, r0, a)
        x1, y1 = pt(x, y, ro, a)
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (x0, y0, x1, y1))
    return '<g stroke="%s" stroke-width="%g" stroke-linecap="round">%s</g>' % (stroke, sw, "".join(o))


def dots(x, y, r, n=11, fill="#111", size=1.8, a0=-135, a1=135):
    return "".join(circle(*pt(x, y, r, a0 + (a1 - a0) * i / max(1, n - 1)), size, fill) for i in range(n))


def numbers(x, y, r, labels, size=10, fill="#111", a0=-135, a1=135, font=SANS, weight=700):
    o = []
    n = len(labels)
    for i, s in enumerate(labels):
        if s == "":
            continue
        px, py = pt(x, y, r, a0 + (a1 - a0) * i / max(1, n - 1))
        o.append(T(px, py, s, size, fill, weight, font=font))
    return "".join(o)


def screw(x, y, r=6, slot=45, head="#c8c8c8", dark="#555"):
    a = math.radians(slot)
    dx, dy = r * 0.7 * math.cos(a), r * 0.7 * math.sin(a)
    return ('<circle cx="%g" cy="%g" r="%g" fill="url(#hw-screw)" stroke="%s" stroke-width="0.8"/>'
            '<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g" stroke-linecap="round"/>'
            % (x, y, r, dark, x - dx, y - dy, x + dx, y + dy, dark, max(1.2, r * 0.28)))


def hexscrew(x, y, r=6):
    return ('<circle cx="%g" cy="%g" r="%g" fill="url(#hw-screw)" stroke="#333" stroke-width="0.8"/>'
            '<polygon points="%s" fill="#3a3a3a"/>' % (x, y, r, " ".join(
                "%.1f,%.1f" % pt(x, y, r * 0.45, a) for a in range(0, 360, 60))))


def led(x, y, r=4, on="#ff2a1a", lit=False):
    if lit:
        return circle(x, y, r + 3, on, extra=' opacity="0.25"') + circle(x, y, r, on, "#3a0a06", 0.8)
    return circle(x, y, r, "#4a0f0a", "#1a0503", 0.8) + circle(x - r * .3, y - r * .3, r * .35, "#fff", extra=' opacity="0.25"')


DEFS = """<defs>
<linearGradient id="hw-screw" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f2f2f2"/><stop offset="1" stop-color="#7a7a7a"/></linearGradient>
<filter id="hw-brush" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.0025 0.8" numOctaves="2" seed="5"/>
 <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.20 0"/></filter>
<filter id="hw-brushd" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.0025 0.8" numOctaves="2" seed="9"/>
 <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.16 0"/></filter>
<filter id="hw-grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="3"/>
 <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.07 0"/></filter>
<filter id="hw-wood" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.006 0.18" numOctaves="4" seed="21"/>
 <feColorMatrix values="0 0 0 0 0.30  0 0 0 0 0.15  0 0 0 0 0.05  0 0 0 0.85 0"/></filter>
<filter id="hw-soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2"/></filter>
<filter id="hw-shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.45"/></filter>
<linearGradient id="hw-vshade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.10"/><stop offset="1" stop-color="#000" stop-opacity="0.14"/></linearGradient>
</defs>"""


def brushed(x, y, w, h, base, dark=False):
    return rect(x, y, w, h, base) + '<rect x="%g" y="%g" width="%g" height="%g" filter="url(#hw-%s)"/>' % (
        x, y, w, h, "brushd" if dark else "brush")


def grain(x, y, w, h):
    return '<rect x="%g" y="%g" width="%g" height="%g" filter="url(#hw-grain)"/>' % (x, y, w, h)


def wood(x, y, w, h, base="#6a3c1c"):
    return rect(x, y, w, h, base) + '<rect x="%g" y="%g" width="%g" height="%g" filter="url(#hw-wood)"/>' % (x, y, w, h)


# ---- knob and switch images (96 x 96, pointing up; the renderer turns `img`, `base` stays still) -----------------
def knob_img(body="#151515", edge="#000", knurl=None, knurl_n=36, cap=None, cap_r=0.0, cap_edge=None, line_c="#fff",
             line=(0.15, 0.92), line_w=6, skirt=None, skirt_r=0.0, dot=None, shine=0.18, rr=0.92, flat_top=None,
             pointer=None):
    """A knob seen from above. rr: body radius (of 48); skirt: a wider flange under it; cap: a coloured or metal top
    (cap_r of the body); line: the pointer from..to as fractions of the body radius; knurl: grip ridge colour."""
    R = 48 * rr
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">', "<defs>",
         '<radialGradient id="g" cx="0.38" cy="0.32" r="0.8"><stop offset="0" stop-color="#fff" stop-opacity="%g"/>'
         '<stop offset="0.6" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.25"/></radialGradient>' % shine,
         '<linearGradient id="m" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbfbfb"/><stop offset="0.45" stop-color="#c9cbcd"/>'
         '<stop offset="0.55" stop-color="#e9eaeb"/><stop offset="1" stop-color="#8d8f91"/></linearGradient>',
         '<radialGradient id="mr" cx="0.4" cy="0.35" r="0.75"><stop offset="0" stop-color="#ffffff"/><stop offset="0.5" stop-color="#d4d6d8"/>'
         '<stop offset="1" stop-color="#8e9193"/></radialGradient>', "</defs>"]
    if skirt:
        o.append('<circle cx="48" cy="48" r="%g" fill="%s" stroke="#000" stroke-opacity="0.5" stroke-width="1"/>' % (48 * skirt_r, skirt))
    o.append('<circle cx="48" cy="48" r="%g" fill="%s" stroke="%s" stroke-width="1.5"/>' % (R, "url(#m)" if body == "metal" else body, edge))
    if knurl:
        o.append('<circle cx="48" cy="48" r="%g" fill="none" stroke="%s" stroke-width="%g" stroke-dasharray="%g %g"/>' % (
            R - 3, knurl, 5, 2 * math.pi * (R - 3) / knurl_n / 2, 2 * math.pi * (R - 3) / knurl_n / 2))
    if flat_top:
        o.append('<circle cx="48" cy="48" r="%g" fill="%s"/>' % (R * flat_top[0], flat_top[1]))
    if cap:
        o.append('<circle cx="48" cy="48" r="%g" fill="%s" stroke="%s" stroke-width="1"/>' % (
            R * cap_r, {"metal": "url(#mr)"}.get(cap, cap), cap_edge or "#000"))
    o.append('<circle cx="48" cy="48" r="%g" fill="url(#g)"/>' % R)
    if pointer:   # a moulded pointer: a wedge from the body's edge
        o.append(pointer)
    if line_c:
        o.append('<line x1="48" y1="%g" x2="48" y2="%g" stroke="%s" stroke-width="%g" stroke-linecap="round"/>' % (
            48 - R * line[0], 48 - R * line[1], line_c, line_w))
    if dot:
        o.append('<circle cx="48" cy="%g" r="4" fill="%s"/>' % (48 - R * 0.75, dot))
    o.append("</svg>")
    return "".join(o)


def svg_doc(w, h, body):
    return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s</svg>' % (w, h, w, h, body)


# ---- the page ----------------------------------------------------------------------------------------------------
class Page:
    def __init__(self, name, vink="#222", lab=None, seg_text=True):
        self.name = name
        self.ctl = []
        self.art = []          # behind everything
        self.over = []         # printed after the controls' own art (labels over plates)
        self.assets = {}
        self.qrows = []
        self.qsets = None
        self.vink = vink       # value text colour under knobs and sliders
        self.lab = dict(size=12, fill="#111", weight=700, font=SANS, sp=0.02)
        self.lab.update(lab or {})
        self.seg_text = seg_text

    # artwork
    def add(self, *svg):
        self.art.extend(svg)
        return self

    def top(self, *svg):
        self.over.extend(svg)
        return self

    def asset(self, name, svg):
        name = "hw_" + name if not name.startswith("hw_") else name
        self.assets[name] = svg
        return name

    def text(self, x, y, s, **kw):
        st = dict(self.lab)
        st.update(kw)
        size = st.pop("size")
        fill = st.pop("fill")
        self.over.append(T(x, y, s, size, fill, **st))

    # controls (x, y = centre, plugin-area pixels)
    def _c(self, **d):
        if d.get("key") in [c["key"] for c in self.ctl if c.get("key") and c["kind"] != "picture"] and not d.get("dup"):
            raise SystemExit("hwpanel %s: %s placed twice" % (self.name, d["key"]))
        self.ctl.append(d)
        return d

    def knob(self, key, x, y, r, label, img=None, base=None, look=None, lab=None, vs=None, bw=None, vink=None, when=None, dup=False,
             **labkw):
        """lab: where the label is printed, as a y offset from the centre (negative = above); None = not printed."""
        if r > 59:
            raise SystemExit("hwpanel: knob %s r=%d: filmstrips over r=59 garble on MPC" % (key, r))
        self._c(kind="knob", key=key, x=x, y=y, r=r, label=label, img=img, base=base, look=look, vs=vs, bw=bw,
                vink=vink or self.vink, when=when, dup=bool(when) or dup)
        if lab is not None and label:
            self.text(x, y + lab, label, **labkw)

    def slider(self, key, x, y, w, h, label, img=None, base=None, look=None, lab=None, vs=None, bw=None, vink=None,
               **labkw):
        self._c(kind="slider_v" if h >= w else "slider_h", key=key, x=x, y=y, w=w, h=h, label=label, img=img, base=base,
                look=look, vs=vs, bw=bw, vink=vink or self.vink)
        if lab is not None and label:
            self.text(x, y + lab, label, **labkw)

    def toggle(self, key, x, y, label, img=None, img_on=None, w=None, h=None, look=None, lab=None, **labkw):
        self._c(kind="toggle", key=key, x=x, y=y, label=label, img=img, img_on=img_on, w=w, h=h, look=look)
        if lab is not None and label:
            self.text(x, y + lab, label, **labkw)

    def switch(self, key, x, y, n, vertical=True, sw=40, sh=30, img=None, img_on=None, label="", rows=None, options=None,
               at=None):
        """Option buttons / a slide switch: one segment per option (sw x sh each, 2 px apart); at=[(x, y), ..]: each
        option's own centre instead (buttons spread over a panel, as a machine has them)."""
        self._c(kind="enum_h" if at else ("enum_v" if vertical else "enum_h"), key=key, x=x, y=y, n=n, sw=sw, sh=sh,
                img=img, img_on=img_on, label=label, rows=rows, options=options, at=at)

    def seg_rects(self, c):
        """The segments' rectangles, as shadow_skin.seg_rects lays them out (plugin coordinates)."""
        n, sw, sh, gap = c["n"], c["sw"], c["sh"], 2
        if c.get("at"):
            return [(x - sw // 2, y - sh // 2, sw, sh) for x, y in c["at"]]
        if c["kind"] == "enum_v":
            y0 = c["y"] - (n * (sh + gap)) // 2
            return [(c["x"] - sw // 2, y0 + i * (sh + gap), sw, sh) for i in range(n)]
        rows = c.get("rows") or 1
        per = -(-n // rows)
        out = []
        for i in range(n):
            r_, k = divmod(i, per)
            cnt = min(per, n - r_ * per)
            x0 = c["x"] - (cnt * sw + (cnt - 1) * gap) // 2
            out.append((x0 + k * (sw + gap), c["y"] - sh // 2 + r_ * (sh + gap), sw, sh))
        return out

    def popup(self, key, x, y, w, h, label="", field=True, accent=None, cols=None, cw=None, img=None):
        if not field and not label:   # no drawn box, so no drawn label: the name only identifies its list
            label = key.upper().replace("_", " ")
        self._c(kind="popup", key=key, x=x, y=y, w=w, h=h, label=label, field=field, accent=accent, cols=cols, cw=cw,
                img=img)

    def button(self, key, x, y, label, img=None, img_on=None, w=None, h=None, color=None):
        self._c(kind="button", key=key, x=x, y=y, label=label, img=img, img_on=img_on, w=w, h=h, color=color)

    def readout(self, key, x, y, w, h, label=""):
        self._c(kind="readout", key=key, x=x, y=y, w=w, h=h, label=label, dup=True)

    def picture(self, key, x, y, w, h, files):
        """One image per option of key (the current one shows): a rotary selector's positions, say."""
        self._c(kind="picture", key=key, x=x, y=y, w=w, h=h, files=files, dup=True)

    def rotary(self, key, x, y, r, n, knob, a0=-120, a1=120, angles=None, field_w=120, field_dy=None, accent=None, label=""):
        """A rotary selector: the knob drawn at each option's position (a picture per option, so it shows the current
        one) and, under it, the option name as a field that opens the list on a tap (popup field=none).
        knob(angle) -> the knob's SVG (96 x 96) pointing at angle degrees."""
        angles = angles or [a0 + (a1 - a0) * i / max(1, n - 1) for i in range(n)]
        files = [self.asset("%s_%d.svg" % (key, i), knob(a)) for i, a in enumerate(angles)]
        s = 2 * r + 8
        self.picture(key, int(x - s / 2), int(y - s / 2), s, s, files)
        self.popup(key, x, y + (field_dy if field_dy is not None else r + 20), field_w, 30, label=label, field=False,
                   accent=accent or self.vink)
        return angles

    # Q-Links
    def qrow(self, *keys):
        """One hardware row, left to right: its own Q-Link bank of 8 (more than 8 continues into the next bank)."""
        self.qrows.append([k for k in keys])

    def qset(self, title, keys):
        self.qsets = (self.qsets or []) + [(title, keys)]

    # ---- output -----------------------------------------------------------------------------------------------
    def keys(self):
        return [c["key"] for c in self.ctl if c.get("key") and c["kind"] != "picture"]

    def box(self, c, bw=None):
        """Touch box (x0, y0, x1, y1) in plugin coordinates, as shadow_skin builds it."""
        k = c["kind"]
        if k == "knob":
            r = c["r"]
            s = 2 * r + 10
            cw = max(s, bw or c.get("bw") or 130)
            vh = round(26 * LABEL_SCALE) if c.get("vs") is None else max(round(26 * LABEL_SCALE), round(c["vs"] * 1.2))
            y0 = c["y"] - s // 2
            return (c["x"] - cw / 2, y0, c["x"] + cw / 2, y0 + 2 * r + 7 + vh + 6)
        if k in ("slider_v", "slider_h"):
            cw = max(c["w"], bw or c.get("bw") or max(130, c["w"]))
            vh = max(26, round((c.get("vs") or 22) * 1.2))
            y0 = c["y"] - c["h"] // 2
            return (c["x"] - cw / 2, y0, c["x"] + cw / 2, y0 + c["h"] + 2 + vh + 6)
        if k == "toggle":
            w, h = c.get("w") or 51, c.get("h") or 27
            return (c["x"] - w / 2, c["y"] - h // 2, c["x"] + w / 2, c["y"] - h // 2 + h)
        if k in ("enum_v", "enum_h"):
            rs = self.seg_rects(c)
            return (min(r[0] for r in rs), min(r[1] for r in rs), max(r[0] + r[2] for r in rs), max(r[1] + r[3] for r in rs))
        if k in ("popup", "readout", "button") and c.get("w"):
            return (c["x"] - c["w"] / 2, c["y"] - c["h"] / 2, c["x"] + c["w"] / 2, c["y"] + c["h"] / 2)
        return None

    def fit_widths(self):
        """Narrow each knob/slider touch box so it can't overlap a neighbour (bw=), never below the knob itself."""
        out = {}
        for i, c in enumerate(self.ctl):
            if c["kind"] not in ("knob", "slider_v", "slider_h") or c.get("bw"):
                continue
            want = 130 if c["kind"] == "knob" else max(130, c["w"])
            me = self.box(c, want)
            for j, d in enumerate(self.ctl):
                if i == j or d["kind"] == "picture" or (d.get("key") == c.get("key")):
                    continue
                o = self.box(d, d.get("bw") or (130 if d["kind"] == "knob" else None))
                if not o:
                    continue
                oy = min(me[3], o[3]) - max(me[1], o[1])
                if oy <= 4:
                    continue
                dx = abs(d["x"] - c["x"])
                if d["kind"] in ("knob", "slider_v", "slider_h"):
                    lim = dx - 2   # both halves meet in the middle
                else:
                    lim = 2 * (dx - (o[2] - o[0]) / 2) - 4
                want = min(want, lim)
            floor = 2 * c["r"] + 10 if c["kind"] == "knob" else c["w"]
            out[i] = int(max(floor, want))
        for i, v in out.items():
            self.ctl[i]["bw_auto"] = v

    def lines(self, params):
        self.fit_widths()
        o = []
        for c in self.ctl:
            k = c["kind"]
            key = c.get("key")
            if key and key not in params:
                raise SystemExit("hwpanel %s: no parameter %r" % (self.name, key))
            Y = lambda v: int(round(v + Y_OFF))
            lab = (c.get("label") or "").replace('"', "")
            look = ""
            for a in ("img", "img_on", "base", "look"):
                if c.get(a):
                    look += " %s=%s" % (a, c[a])
            if k == "knob":
                bw = c.get("bw") or c.get("bw_auto") or 130
                o.append('knob cx=%d cy=%d r=%d label="%s" key=%s ns=0 bw=%d ink_dim=%s%s%s' % (
                    c["x"], Y(c["y"]), c["r"], lab, key, bw, c["vink"].lstrip("#"),
                    " vs=%d" % c["vs"] if c.get("vs") else "", look) + (" when=%s" % c["when"] if c.get("when") else ""))
            elif k in ("slider_v", "slider_h"):
                bw = c.get("bw") or c.get("bw_auto") or max(130, c["w"])
                o.append('%s cx=%d cy=%d w=%d h=%d label="%s" key=%s ns=0 bw=%d%s%s' % (
                    k, c["x"], Y(c["y"]), c["w"], c["h"], lab, key, bw, " vs=%d" % c["vs"] if c.get("vs") else "", look))
            elif k == "toggle":
                wh = " w=%d h=%d" % (c["w"], c["h"]) if c.get("w") else ""
                o.append('toggle cx=%d cy=%d label="%s" key=%s ns=0%s%s' % (c["x"], Y(c["y"]), lab, key, wh, look))
            elif k in ("enum_v", "enum_h"):
                if params[key]["nopts"] != c["n"]:
                    raise SystemExit("hwpanel %s: %s has %d options, not %d" % (self.name, key, params[key]["nopts"], c["n"]))
                extra = " rows=%d" % c["rows"] if c.get("rows") else ""
                if c.get("options"):
                    extra += ' options="%s"' % ",".join(c["options"])
                if c.get("at"):
                    extra += ' at="%s"' % ",".join("%d:%d" % (x, round(y + Y_OFF)) for x, y in c["at"])
                o.append('%s cx=%d cy=%d label="%s" key=%s sw=%d sh=%d%s%s' % (
                    k, c["x"], Y(c["y"]), c["label"], key, c["sw"], c["sh"], extra, look))
            elif k == "popup":
                extra = ""
                if not c["field"]:
                    extra += " field=none"
                if c.get("accent"):
                    extra += " accent=%s" % c["accent"].lstrip("#")
                n = params[key]["nopts"]
                if c.get("cols"):
                    extra += " cols=%d cw=%d" % (c["cols"], c["cw"])
                elif n > 12:
                    cols = -(-n // 12)
                    extra += " cols=%d cw=%d" % (cols, min(c["w"], (1240 - 12) // cols - 2))
                if c.get("img"):
                    extra += " img=%s" % c["img"]
                o.append('popup cx=%d cy=%d w=%d h=%d label="%s" key=%s%s' % (c["x"], Y(c["y"]), c["w"], c["h"], lab, key, extra)
                         + (" when=%s" % c["when"] if c.get("when") else ""))
            elif k == "button":
                wh = " w=%d h=%d" % (c["w"], c["h"]) if c.get("w") else ""
                col = " color=%s" % c["color"].lstrip("#") if c.get("color") else ""
                o.append('button cx=%d cy=%d label="%s" key=%s%s%s%s' % (c["x"], Y(c["y"]), lab, key, wh, col, look))
            elif k == "readout":
                o.append('readout cx=%d cy=%d w=%d h=%d label="%s" key=%s' % (c["x"], Y(c["y"]), c["w"], c["h"], lab, key))
            elif k == "picture":
                o.append('picture x=%d y=%d w=%d h=%d key=%s files="%s"' % (c["x"], Y(c["y"]), c["w"], c["h"], key,
                                                                          ",".join(c["files"])))
        return o

    def qlink_lines(self):
        if self.qsets:
            return ['qlinks "%s" = %s' % (t, ",".join(k)) for t, k in self.qsets]
        slots = []
        for r in self.qrows:
            slots += r
            if len(slots) % 8:
                slots += ["-"] * (8 - len(slots) % 8)
        while slots and slots[-1] == "-":
            slots.pop()
        chunks = [slots[i:i + 16] for i in range(0, len(slots), 16)]
        chunks = [c for c in chunks if any(k != "-" for k in c)]
        out = []
        for n, c in enumerate(chunks):
            while c[-1] == "-":
                c.pop()
            title = self.name if len(chunks) == 1 else "%s %s" % (self.name, "ABCDEFGH"[n])
            out.append('qlinks "%s" = %s' % (title, ",".join(c)))
        return out

    def svg(self):
        return "\n".join(self.art + self.over)
