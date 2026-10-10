#!/usr/bin/env python3
"""Hardware-style skins for the Force ports: one theme per plugin, modelled on the machine it emulates.

For each port it reads the port's current layout (saved once as skins/base/<id>.conf, so reruns start from the same
geometry), and writes into the port's vst/ folder:
  layout.conf      the same controls and Q-Links, squeezed down 50 px to make room for a header strip, with
                   theme_* colours, knob/toggle looks, art_css= and one `art file=` panel drawing per tab
  skin.css         the renderer stylesheet (frame titles, knob colours, text)
  panel_<n>.svg    the page artwork: panel finish, header lettering, a section plate under every frame
and sets vst.json "layout": "layout.conf", "art": "html". Control positions only move vertically by the squeeze, so
every Q-Link, touch box and parameter binding stays the same.

    hwskin.py [id ...]      (default: every port in THEMES)
"""
import json
import os
import re
import shutil
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
BASE = os.path.join(HERE, "base")

Y0, Y1 = 92, 708          # the auto layouts' content area (Force Shadow coords)
Y_OFF = 86                # plugin area top (shadow_skin.Y_OFF); the panel SVG is 1280 x 628 from here
HEAD = 50                 # header strip height taken from the top of the content area
SCALE = (Y1 - Y0 - HEAD) / (Y1 - Y0)

PORTS = {   # id -> vst folder
    "303": "modules/schwung-303/vst", "8w8": "modules/schwung-8W8/vst", "6w6": "modules/schwung-6W6/vst",
    "9w9": "modules/schwung-9W9/vst", "cw78": "modules/schwung-cw-78/vst", "braids": "modules/schwung-braids/vst",
    "plaits": "modules/move-anything-plaits/vst", "mrhyde": "modules/move-everything-mrhyde/vst",
    "denis": "modules/denis-move/vst", "hush1": "modules/schwung-hush1/vst", "hank": "modules/schwung-hank/vst",
    "chiptune": "modules/schwung-chiptune/vst", "libpo32": "modules/schwung-libpo32/vst",
    "weird": "modules/weird-dreams-move/vst", "midiverb": "modules/schwung-midiverb/vst",
    "psxverb": "modules/schwung-psxverb/vst", "tapedelay": "modules/schwung-space-delay/vst",
    "juno": "modules/schwung-junologue-chorus/vst", "busdriver": "modules/schwung-busdriver/vst",
    "4keq": "modules/schwung-4keq/vst", "ducker": "modules/schwung-ducker/vst", "filter": "modules/schwung-filter/vst",
    "tapescam": "modules/schwung-tapescam/vst", "ml185": "ml185/vst",
    "breakslicer": "mpc-vst-plugins/ports/breakslicer/vst",
}

# ---- themes --------------------------------------------------------------------------------------------------
# finish: brushed | flat | wood (whole panel) ; cheeks: wood side cheeks ; plate: section plate fill (None = none)
# plate_line: plate outline ; title: frame-title colour ; title_bg: a badge behind each frame title (list cycles)
# logo / sub / tag: header lettering ; stripes: colour bands in the header ; deco: extra drawings (see DECO)
THEMES = {
    "303": dict(finish="brushed", bg="c3c6c8", ink="1b1b1b", ink_dim="3d3f41", accent="d1361f", accent_hi="e8502e",
                plate="d4d6d7", plate_line="1b1b1b", title="1b1b1b", knob="moog", toggle="led",
                logo="303", sub="ACID BASS LINE SYNTHESIZER", tag="COMPUTER CONTROLLED", head_bg="2a2b2c",
                head_ink="e9e9e6", stripes=["d1361f"], lcd="1e1f20"),
    "8w8": dict(title_size=12, title_sp=0.04, finish="flat", bg="1b1b1b", ink="f1ece0", ink_dim="b8b2a4", accent="f08a24", accent_hi="f6a33a",
                plate="262626", plate_line="3a3a3a", title="111111",
                title_bg=["d93a2b", "ee7a2a", "f2c12e", "ece4d1"], knob="cap", knob_ring="d8d1bf", knob_dot="ece6d6",
                knob_line="1b1b1b", toggle="led", logo="8W8", sub="RHYTHM COMPOSER", tag="ANALOG DRUM MODELS",
                head_bg="161616", head_ink="f1ece0", stripes=["d93a2b", "ee7a2a", "f2c12e", "ece4d1"]),
    "6w6": dict(title_size=12, title_sp=0.04, finish="brushed", bg="b9bcbe", ink="1a1a1a", ink_dim="3a3c3e", accent="c33a22", accent_hi="e04a30",
                plate="d0d2d3", plate_line="55585a", title="1a1a1a", plate_ink="1a1a1a", lcd="1e1f20",
                knob="moog", toggle="led", logo="6W6", sub="RHYTHM MACHINE", tag="", head_bg="b9bcbe",
                head_ink="161616", stripes=["c33a22", "161616"]),
    "9w9": dict(title_size=12, title_sp=0.04, finish="flat", bg="8e9192", ink="141414", ink_dim="2e3031", accent="f2701c", accent_hi="ff8a33",
                plate="a3a6a7", plate_line="2a2b2c", title="141414", title_bg=["f2701c"], knob="cap",
                knob_ring="2b2b2b", knob_dot="3a3a3a", knob_line="f2f2f2", toggle="led", logo="9W9",
                sub="RHYTHM COMPOSER", tag="ANALOG / SAMPLE", head_bg="2b2c2d", head_ink="f2701c",
                stripes=["f2701c"]),
    "cw78": dict(title_size=12, title_sp=0.04, finish="flat", cheeks=True, bg="1c1916", ink="efe3c8", ink_dim="bfae8c", accent="e07b2c",
                 accent_hi="f0953f", plate="2a241e", plate_line="5b4b38", title="1c1916",
                 title_bg=["e8d7b0", "e07b2c"], knob="chicken", toggle="switch", logo="CW-78",
                 sub="COMPURHYTHM", tag="RHYTHM COMPUTER", head_bg="1c1916", head_ink="e8d7b0",
                 stripes=["e07b2c", "b4562a"]),
    "braids": dict(finish="brushed", bg="c9cccd", ink="141414", ink_dim="3b3d3f", accent="1f6fd1", accent_hi="3a86e4",
                   plate=None, plate_line="141414", title="141414", knob="metal", toggle="led", logo="Braids",
                   sub="macro oscillator", tag="", head_bg=None, head_ink="141414", rails=True, logo_font="italic"),
    "plaits": dict(finish="flat", bg="e9e8e3", ink="161616", ink_dim="4a4a48", accent="2a2a2a", accent_hi="d94a2a",
                   plate=None, plate_line="161616", title="161616", knob="cap", knob_ring="cfcfca",
                   knob_dot="f7f7f4", knob_line="161616", toggle="led", logo="Plaits", sub="macro-oscillator 2",
                   tag="", head_bg=None, head_ink="161616", rails=True, logo_font="italic"),
    "mrhyde": dict(finish="flat", bg="161616", ink="f2f2f2", ink_dim="9a9a9a", accent="ff6a1f", accent_hi="ff8a45",
                   plate="1f1f1f", plate_line="ff6a1f", title="ff6a1f", knob="cap", knob_ring="2e2e2e",
                   knob_dot="4a4a4a", knob_line="ff6a1f", toggle="led", logo="MrHyde", sub="EXPERIMENTAL SYNTHESIZER",
                   tag="DIGITAL OSCILLATOR / ANALOG FILTER", head_bg="161616", head_ink="f2f2f2", stripes=["ff6a1f"]),
    "denis": dict(finish="flat", bg="13161c", ink="e6e9ef", ink_dim="9aa3b3", accent="3f8ce0", accent_hi="5aa2f0",
                  plate="1a1f27", plate_line="3a4250", title="e6e9ef",
                  title_bg=["c2372e", "2f6fc9", "2f9a55", "d9b02a"], knob="moog", toggle="led", logo="DENIS",
                  sub="WEST COAST MONOPHONIC", tag="COMPLEX OSCILLATOR / LOW PASS GATE", head_bg="0d0f13",
                  head_ink="e6e9ef", jacks=True),
    "hush1": dict(title_size=12, title_sp=0.04, finish="flat", bg="3a3c3f", ink="eeeeec", ink_dim="b3b5b6", accent="d8382e", accent_hi="ec4a3f",
                  plate="45484b", plate_line="1f2022", title="eeeeec", title_bg=["4a6fb5", "d8382e", "8a8d90"],
                  knob="cap", knob_ring="1b1c1d", knob_dot="2c2d2f", knob_line="eeeeec", toggle="switch",
                  logo="HUSH ONE", sub="SYNTHESIZER", tag="MONOPHONIC", head_bg="2a2c2e", head_ink="eeeeec",
                  stripes=["4a6fb5", "d8382e"]),
    "hank": dict(finish="flat", bg="2c2723", ink="efe7da", ink_dim="b9ab95", accent="3fb3a2", accent_hi="5ccbbb",
                 plate="36302b", plate_line="574b40", title="2c2723", title_bg=["3fb3a2", "a33a3a"], knob="cap",
                 knob_ring="1a1714", knob_dot="463d36", knob_line="3fb3a2", toggle="led", logo="HANK",
                 sub="2-OPERATOR FM", tag="DIGITAL PROGRAMMABLE ALGORITHM", head_bg="1f1b18", head_ink="efe7da",
                 stripes=["3fb3a2", "a33a3a"]),
    "chiptune": dict(finish="flat", bg="c4c3bf", ink="23232b", ink_dim="54556a", accent="9a2257", accent_hi="b8306c",
                     plate="a3b468", plate_line="54556a", plate_frame="54556a", title="0f380f", seg_off="c9d39c", knob="cap",
                     knob_ring="5a5a66", knob_dot="9a2257", knob_line="f2f2f2", toggle="led", logo="Chiptune",
                     sub="DOT MATRIX WITH STEREO SOUND", tag="", head_bg=None, head_ink="2b2d8c", logo_font="italic",
                     lcd="8bac0f", plate_ink="0f380f"),
    "libpo32": dict(finish="pcb", bg="1f4a2c", ink="f4f1e6", ink_dim="b9c7b0", accent="e8c547", accent_hi="f4d968",
                    plate=None, plate_line="f4f1e6", title="f4f1e6", knob="cap", knob_ring="111111",
                    knob_dot="222222", knob_line="e8c547", toggle="led", logo="libpo32", sub="tonic drum synth",
                    tag="pocket operator format", head_bg=None, head_ink="f4f1e6", logo_font="italic"),
    "weird": dict(finish="gradient", bg="1a1030", bg2="3a1a4a", ink="f3e9ff", ink_dim="b9a6d6", accent="ff4fb4",
                  accent_hi="ff77c8", plate="24163d", plate_line="5a3f87", title="f3e9ff",
                  title_bg=["ff4fb4", "36d1dc", "8a5cf5"], knob="cap", knob_ring="140b26", knob_dot="2a1b47",
                  knob_line="36d1dc", toggle="led", logo="Weird Dreams", sub="8 VOICE DRUM MACHINE", tag="",
                  head_bg=None, head_ink="f3e9ff", logo_font="italic", stripes=["ff4fb4", "36d1dc"]),
    "midiverb": dict(finish="flat", bg="161616", ink="e8e8e8", ink_dim="9b9b9b", accent="ff2a1a", accent_hi="ff4a3a",
                     plate="1e1e1e", plate_line="333333", title="e8e8e8", knob="metal", toggle="led",
                     logo="MIDIVERB", sub="DIGITAL REVERB / EFFECTS", tag="16 BIT", head_bg="0e0e0e",
                     head_ink="e8e8e8", rack=True, lcd="200806"),
    "psxverb": dict(finish="flat", bg="c8c7c3", ink="2b2b33", ink_dim="5c5c66", accent="2f5fb0", accent_hi="4a78c8",
                    plate="b9b8b4", plate_line="8f8e8a", title="2b2b33", knob="cap", knob_ring="3b3b44",
                    knob_dot="56565f", knob_line="e9e9ee", toggle="led", logo="PSX Verb",
                    sub="SPU REVERB", tag="", head_bg=None, head_ink="2b2b33", logo_font="italic", psx=True),
    "tapedelay": dict(finish="flat", bg="1c2620", ink="ece6d3", ink_dim="b5ae98", accent="d8b04a", accent_hi="ecc65f",
                      plate="25312a", plate_line="8e9a92", title="ece6d3", knob="moog", toggle="switch",
                      logo="TAPE DELAY", sub="SPACE ECHO", tag="MULTI HEAD TAPE ECHO", head_bg="b8bcba",
                      head_ink="1c2620", stripes=["d8b04a"]),
    "juno": dict(finish="flat", bg="1a1a1a", ink="eeeeee", ink_dim="a8a8a8", accent="e8522b", accent_hi="f26a40",
                 plate="232323", plate_line="3a3a3a", title="1a1a1a", title_bg=["e8522b", "f2a12b", "e9d84a"],
                 knob="cap", knob_ring="0f0f0f", knob_dot="dcdcdc", knob_line="1a1a1a", toggle="led",
                 logo="JUNOLOGUE", sub="CHORUS", tag="I / II / I+II", head_bg="1a1a1a", head_ink="eeeeee",
                 stripes=["e8522b", "f2a12b", "e9d84a", "3a9fd8"]),
    "busdriver": dict(finish="flat", bg="1e1e1e", ink="e6e6e6", ink_dim="9a9a9a", accent="ff764d", accent_hi="ff9270",
                      plate="262626", plate_line="363636", title="b5b5b5", knob="drawn", toggle="led",
                      logo="Bus Driver", sub="DRUM BUSS", tag="", head_bg=None, head_ink="e6e6e6",
                      knob_face="3c3c3c", knob_ring="111111", knob_dot="ff764d"),
    "4keq": dict(finish="flat", bg="3a3d40", ink="eeeeec", ink_dim="b5b7b8", accent="d33a2c", accent_hi="e8503f",
                 plate="44484b", plate_line="25272a", title="eeeeec",
                 title_bg=["d33a2c", "2f9a55", "2f6fc9", "1a1a1a", "8a6a3a"], knob="cap", knob_ring="1b1c1e",
                 knob_dot="d33a2c", knob_line="f4f4f2", toggle="led", logo="4K EQ", sub="CHANNEL EQUALISER",
                 tag="E / G SERIES", head_bg="25272a", head_ink="eeeeec", lcd="1a1b1c"),
    "ducker": dict(finish="flat", bg="18202a", ink="e4edf5", ink_dim="94a6b8", accent="2ec4d6", accent_hi="52d8e8",
                   plate="1f2935", plate_line="2f3d4d", title="2ec4d6", knob="drawn", toggle="led", logo="DUCKER",
                   sub="SIDECHAIN DYNAMICS", tag="", head_bg=None, head_ink="e4edf5", knob_face="2a3644",
                   knob_ring="0d1218", knob_dot="2ec4d6"),
    "breakslicer": dict(finish="flat", bg="efe6d2", ink="2a1c12", ink_dim="6a5644", accent="e0582a", accent_hi="f07040",
                        plate="e6dbc3", plate_line="b9a582", title="2a1c12", knob="drawn", toggle="led", logo="BREAKSLICER",
                        sub="BREAK CHOPPER", tag="", head_bg=None, head_ink="2a1c12", knob_face="1d1916",
                        knob_ring="0a0807", knob_dot="f4ead6"),
    "filter": dict(finish="flat", cheeks=True, bg="141414", ink="f0ede6", ink_dim="aaa69e", accent="e0a83a",
                   accent_hi="f0bf55", plate="1c1c1c", plate_line="3a3a3a", title="f0ede6", knob="moog",
                   toggle="switch", logo="FILTER", sub="MULTIMODE STATE VARIABLE", tag="", head_bg="141414",
                   head_ink="f0ede6"),
    "tapescam": dict(finish="brushed", bg="bfc2c4", ink="161616", ink_dim="3d3f41", accent="d4262a", accent_hi="e83a3e",
                     plate="e9e2c9", plate_line="2a2a2a", title="161616", knob="metal", toggle="led",
                     logo="TAPESCAM", sub="CASSETTE TAPE DECK", tag="TYPE I / NORMAL BIAS", head_bg="161616",
                     head_ink="eeeeec", stripes=["d4262a"]),
    "ml185": dict(finish="flat", bg="141414", ink="f2f2f2", ink_dim="a0a0a0", accent="f2c230", accent_hi="ffd84f",
                  plate="1b1b1b", plate_line="3a3a3a", title="f2c230", knob="metal", toggle="led", logo="ML-185",
                  sub="STAGE SEQUENCER", tag="8 STAGES / PULSES / GATES", head_bg=None, head_ink="f2f2f2",
                  rails=True),
}

BAND_COLOURS = {"hf": "d33a2c", "hmf": "2f9a55", "lmf": "2f6fc9", "lf": "2a2a2a", "hp": "8a6a3a", "lp": "8a6a3a",
                "io": "8a8d90"}


def C(h):
    return "#" + h


# ---- layout ------------------------------------------------------------------------------------------------------
def sy(v):
    return int(round(Y0 + HEAD + (v - Y0) * SCALE))


def squeeze(line):
    """Move one layout line down into the squeezed content area (y/cy positions; frame and art heights)."""
    def rep(m):
        k, v = m.group(1), int(m.group(2))
        if k in ("y", "cy"):
            return "%s=%d" % (k, sy(v))
        if k == "h" and line.startswith(("frame", "art")):
            return "h=%d" % int(round(v * SCALE))
        return m.group(0)
    return re.sub(r"\b(y|cy|h)=(-?\d+)", rep, line)


CONTROL = ("knob", "toggle", "button", "enum_h", "enum_v", "slider_v", "slider_h", "popup", "readout", "stepper", "menu")


def param_names(vdir):
    """key -> full display name, from the generated params.h (the auto layout cuts labels at 10 characters)."""
    p = os.path.join(vdir, "build", "params.h")
    if not os.path.exists(p):
        return {}
    return dict(re.findall(r'\{\s*"([^"]+)",\s*"([^"]*)"', open(p).read()))


def tidy(body, names):
    """Full parameter names as control labels (up to 13 characters), and no title on a frame that holds one
    control: the control's own label already says it, and a lone cut-off word ("TANH", "SOFT") reads badly."""
    def lab(l):
        m = re.search(r"key=(\S+)", l)
        n = names.get(m.group(1)) if m else None
        if n and len(n) <= 13 and l.split(" ", 1)[0] in CONTROL and 'label="' in l:
            l = re.sub(r'label="[^"]*"', 'label="%s"' % n.upper().replace('"', ""), l, count=1)
        return l
    body = [lab(l) for l in body]
    frames = [(i, dict((k, int(v)) for k, v in re.findall(r"(\w+)=(-?\d+)", l))) for i, l in enumerate(body) if l.startswith("frame ")]
    for i, f in frames:
        inside = 0
        for l in body:
            if l.split(" ", 1)[0] not in CONTROL:
                continue
            g = dict((k, int(v)) for k, v in re.findall(r"(\w+)=(-?\d+)", l))
            if f["x"] <= g.get("cx", -1) <= f["x"] + f["w"] and f["y"] <= g.get("cy", -1) <= f["y"] + f["h"]:
                inside += 1
        if inside == 1:
            body[i] = re.sub(r'\s*title="[^"]*"', "", body[i])
    return body


def centre(body):
    """Move a tab's controls to the middle of the page when they fill only part of it (the auto layout packs a small
    effect into the top-left corner). Positions only; sizes and Q-Links are untouched."""
    xs, ys = [], []
    for l in body:
        g = dict((k, int(v)) for k, v in re.findall(r"\b(x|y|w|h|cx|cy|r)=(-?\d+)", l))
        if l.startswith("frame "):
            xs += [g["x"], g["x"] + g["w"]]
            ys += [g["y"], g["y"] + g["h"]]
        elif "cx" in g:
            xs.append(g["cx"])
            ys.append(g["cy"])
    if not xs:
        return body
    dx = (1280 - min(xs) - max(xs)) // 2 if max(xs) - min(xs) < 1000 else 0
    top = Y0 + HEAD
    dy = (top + Y1 - min(ys) - max(ys)) // 2 if max(ys) - min(ys) < 380 else 0
    if not dx and not dy:
        return body

    def mv(m):
        k, v = m.group(1), int(m.group(2))
        return "%s=%d" % (k, v + (dx if k in ("x", "cx") else dy))
    return [re.sub(r"\b(x|y|cx|cy)=(-?\d+)", mv, l) if not l.startswith(("qlinks", "art ")) else l for l in body]


def frame_rects(lines):
    out = []
    for l in lines:
        if l.startswith("frame "):
            g = dict(re.findall(r"(\w+)=(-?\d+)", l))
            t = re.search(r'title="([^"]*)"', l)
            out.append((int(g["x"]), int(g["y"]), int(g["w"]), int(g["h"]), t.group(1) if t else ""))
    return out


# ---- panel drawing ---------------------------------------------------------------------------------------------
DEFS = """<defs>
<filter id="brush" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.002 0.9"
 numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.16 0"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9"
 numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.10 0"/></filter>
<filter id="woodf" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.012 0.25"
 numOctaves="3" seed="11"/><feColorMatrix values="0 0 0 0 0.36  0 0 0 0 0.20  0 0 0 0 0.09  0 0 0 0.9 0"/></filter>
<linearGradient id="screw" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eee"/><stop offset="1" stop-color="#777"/></linearGradient>
<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.07"/>
 <stop offset="1" stop-color="#000" stop-opacity="0.12"/></linearGradient>
</defs>"""


def screw(x, y, r=6):
    return ('<circle cx="%g" cy="%g" r="%g" fill="url(#screw)" stroke="#333" stroke-width="1"/>'
            '<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#444" stroke-width="1.6"/>' % (x, y, r, x - r * .6, y - r * .6, x + r * .6, y + r * .6))


def text(x, y, s, size, fill, weight=700, anchor="start", spacing=0.08, italic=False, extra=""):
    st = "font-style:italic;" if italic else ""
    return ('<text x="%g" y="%g" font-family="Titillium Web, DejaVu Sans, sans-serif" font-size="%g" font-weight="%d" '
            'fill="%s" text-anchor="%s" dominant-baseline="central" style="letter-spacing:%gem;%s"%s>%s</text>'
            % (x, y, size, weight, fill, anchor, spacing, st, extra, escape(s)))


def panel_svg(t, frames):
    W, H = 1280, 628
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H), DEFS]
    bg = C(t["bg"])
    if t["finish"] == "gradient":
        o.append('<defs><linearGradient id="bgg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/>'
                 '<stop offset="1" stop-color="%s"/></linearGradient></defs><rect width="%d" height="%d" fill="url(#bgg)"/>'
                 % (bg, C(t["bg2"]), W, H))
    else:
        o.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, bg))
    if t["finish"] == "brushed":
        o.append('<rect width="%d" height="%d" filter="url(#brush)"/>' % (W, H))
    elif t["finish"] == "pcb":
        o.append(pcb_traces(W, H))
    else:
        o.append('<rect width="%d" height="%d" filter="url(#grain)"/>' % (W, H))
    o.append('<rect width="%d" height="%d" fill="url(#shade)"/>' % (W, H))
    # section plates, one per frame (frame coords are shadow coords: y - Y_OFF in the panel)
    titles = t.get("title_bg")
    for i, (x, y, w, h, title) in enumerate(frames):
        py = y - Y_OFF
        if t.get("plate"):
            o.append('<rect x="%g" y="%g" width="%g" height="%g" rx="6" fill="%s" stroke="%s" stroke-width="1.5"/>'
                     % (x + 2, py + 2, w - 4, h - 4, C(t["plate"]), C(t.get("plate_frame") or t["plate_line"])))
        else:
            o.append('<rect x="%g" y="%g" width="%g" height="%g" rx="4" fill="none" stroke="%s" stroke-opacity="0.55" '
                     'stroke-width="1.5"/>' % (x + 3, py + 3, w - 6, h - 6, C(t["plate_line"])))
        if titles and title:
            col = C(titles[i % len(titles)])
            ts = t.get("title_size", 17)
            tw = min(w - 16, int(len(title) * ts * (0.62 + t.get("title_sp", 0.12))) + 22)
            o.append('<rect x="%g" y="%g" width="%g" height="26" rx="3" fill="%s"/>' % (x + 8, py + 8, tw, col))
        if t.get("jacks"):   # Serge-style banana jacks along the bottom of each section
            cols = ["#c2372e", "#2f6fc9", "#2f9a55", "#d9b02a"]
            for j in range(max(1, (w - 30) // 40)):
                jx = x + 22 + j * 40
                if jx > x + w - 18:
                    break
                o.append('<circle cx="%g" cy="%g" r="6" fill="#0a0a0a" stroke="%s" stroke-width="2.5"/>' % (jx, py + h - 11, cols[j % 4]))
    if t.get("psx") and frames:   # the disc lid, round the biggest section's control
        x, y, w, h, _ = max(frames, key=lambda f: f[2] * f[3])
        cx, cy, rr = x + w / 2, y - Y_OFF + h / 2 + 8, min(w, h) / 2 - 26
        o.append('<circle cx="%g" cy="%g" r="%g" fill="#d3d2ce" stroke="#9a9995" stroke-width="3"/>'
                 '<circle cx="%g" cy="%g" r="%g" fill="none" stroke="#b5b4b0" stroke-width="2"/>' % (cx, cy, rr, cx, cy, rr - 14))
        o.append(text(cx, cy + rr - 34, "OPEN", 13, "#5c5c66", 600, anchor="middle", spacing=0.3))
    if t.get("psx") and frames:   # the disc lid, round the biggest section's control
        x, y, w, h, _ = max(frames, key=lambda f: f[2] * f[3])
        cx, cy, rr = x + w / 2, y - Y_OFF + h / 2 + 8, min(w, h) / 2 - 26
        o.append('<circle cx="%g" cy="%g" r="%g" fill="#d3d2ce" stroke="#9a9995" stroke-width="3"/>'
                 '<circle cx="%g" cy="%g" r="%g" fill="none" stroke="#b5b4b0" stroke-width="2"/>' % (cx, cy, rr, cx, cy, rr - 14))
        o.append(text(cx, cy + rr - 34, "OPEN", 13, "#5c5c66", 600, anchor="middle", spacing=0.3))
    # header strip
    hb = t.get("head_bg")
    if hb:
        o.append('<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (W, HEAD + 4, C(hb)))
        if t["finish"] == "brushed" and hb == t["bg"]:
            o.append('<rect x="0" y="0" width="%d" height="%d" filter="url(#brush)"/>' % (W, HEAD + 4))
    stripes = t.get("stripes") or []
    ink = C(t["head_ink"])
    italic = t.get("logo_font") == "italic"
    o.append(text(26, 30, t["logo"], 38, ink, 700, spacing=0.04, italic=italic))
    lw = len(t["logo"]) * 22 + 50
    if stripes:
        bx, bw = lw, max(60, 560 - lw)
        n = len(stripes)
        for i, s in enumerate(stripes):
            sh = 6 if n == 1 else 22 / n
            o.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>' % (bx, 27 - n * sh / 2 + i * sh, bw, sh - (1 if n > 1 else 0), C(s)))
        lw = bx + bw + 20
    o.append(text(lw, 30, t["sub"], 17, ink, 600, spacing=0.18, italic=italic and t["logo_font"] == "italic"))
    if t.get("tag"):
        o.append(text(W - 30, 30, t["tag"], 13, ink, 600, anchor="end", spacing=0.2, extra=' opacity="0.75"'))
    if t.get("psx"):   # the four face-button symbols
        cx = W - 130
        o.append('<g transform="translate(%d 30)" fill="none" stroke-width="3">'
                 '<path d="M-48,8 L-38,-9 L-28,8 Z" stroke="#2fa87a"/><circle cx="-6" cy="0" r="9" stroke="#d6383a"/>'
                 '<path d="M14,-8 L30,8 M30,-8 L14,8" stroke="#4a78c8"/><rect x="40" y="-8" width="16" height="16" stroke="#d47ab0"/></g>' % cx)
    if t.get("rails"):   # Eurorack rails and mounting screws
        for yy in (2, H - 10):
            o.append('<rect x="0" y="%d" width="%d" height="8" fill="#000" opacity="0.18"/>' % (yy, W))
        for xx in (14, W - 14):
            for yy in (6, H - 6):
                o.append(screw(xx, yy, 5))
    if t.get("rack"):
        for xx in (8, W - 8):
            for yy in (24, H - 24):
                o.append('<rect x="%d" y="%d" width="10" height="18" rx="5" fill="#050505" stroke="#444"/>' % (xx - 5, yy - 9))
    if t.get("cheeks"):   # wooden end cheeks
        for xx in (0, W - 9):   # narrow: the auto layouts' frames start 10 px from the edge
            o.append('<rect x="%d" y="0" width="9" height="%d" fill="#6b3f1d"/><rect x="%d" y="0" width="9" height="%d" filter="url(#woodf)"/>'
                     % (xx, H, xx, H))
    if not t.get("rails") and not t.get("cheeks") and not t.get("rack"):
        for xx in (10, W - 10):
            o.append(screw(xx, 10, 4.5))
    o.append("</svg>")
    return "\n".join(o)


def pcb_traces(W, H):
    import random
    rnd = random.Random(32)
    o = ['<g stroke="#c9a94a" stroke-opacity="0.35" stroke-width="2" fill="none">']
    for _ in range(46):
        x, y = rnd.randrange(0, W), rnd.randrange(0, H)
        pts = [(x, y)]
        for _ in range(rnd.randrange(2, 5)):
            if rnd.random() < 0.5:
                x += rnd.choice((-1, 1)) * rnd.randrange(40, 200)
            else:
                y += rnd.choice((-1, 1)) * rnd.randrange(30, 120)
            pts.append((x, y))
        o.append('<polyline points="%s"/>' % " ".join("%d,%d" % p for p in pts))
        o.append('<circle cx="%d" cy="%d" r="4" fill="#c9a94a" fill-opacity="0.45"/>' % pts[-1])
    o.append("</g>")
    return "".join(o)


# ---- stylesheet ----------------------------------------------------------------------------------------------
def css(t):
    title = C(t["title"])
    knob_line = C(t.get("knob_line", "f4f4f2"))
    rules = [
        "/* generated by skins/hwskin.py */",
        ".frame-border { stroke: none; fill: none; }",
        ".frame-rule { display: none; }",
        ".frame-title { fill: %s; font-size: %dpx; letter-spacing: %gem; }" % (title, t.get("title_size", 17), t.get("title_sp", 0.12)),
        ".look-line { stroke: %s; }" % knob_line,
        ".box { fill: %s; stroke: %s; }" % (C(t.get("lcd") or t.get("plate") or t["bg"]), C(t["plate_line"])),
        ".box-label { fill: %s; }" % C(t.get("plate_ink") or t["ink_dim"]),
        ".text { fill: %s; }" % C(t["ink"]),
    ]
    if t["knob"] == "metal":
        rules.append(".look-notch { stroke: #1a1a1a; }")
    return "\n".join(rules) + "\n"


def theme_lines(t):
    ink = t.get("plate_ink") or t["ink"]
    th = {
        "bg": t["bg"], "panel": t.get("plate") or t["bg"], "line": t["plate_line"], "ink": ink,
        "ink_dim": t["ink_dim"], "ink_faint": t["ink_dim"], "accent": t["accent"], "accent_hi": t["accent_hi"],
        "knob_face": t.get("knob_face", "e8e8e4"), "knob_ring": t.get("knob_ring", "2a2a2a"),
        "knob_dot": t.get("knob_dot", t["accent"]), "lcd": t.get("lcd") or "141414",
        "seg_active": t["accent"], "seg_inactive": t.get("seg_off", "0d0d0d" if _dark(t) else _tint(t.get("plate") or t["bg"], 0.55)),
        "seg_active_tx": "111111" if _light(t["accent"]) else "f6f6f4", "box": t.get("plate") or t["bg"],
        "btn_bg": t["accent"], "btn_text": "111111", "btn_text_plain": "f6f6f4",
    }
    return ["theme_%s=%s" % kv for kv in th.items()]


def _light(h):
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b > 150


def _mix(h, k):
    return "".join("%02x" % int(int(h[i:i + 2], 16) * k) for i in (0, 2, 4))


def _tint(h, k):
    """h blended k of the way to white: an off option on a light panel (its text is the dim ink)."""
    return "".join("%02x" % int(int(h[i:i + 2], 16) + (255 - int(h[i:i + 2], 16)) * k) for i in (0, 2, 4))


def _dark(t):
    return not _light(t.get("plate") or t["bg"])


# ---- main ------------------------------------------------------------------------------------------------------
def build(pid):
    t = THEMES[pid]
    vdir = os.path.join(WORK, PORTS[pid])
    vj_path = os.path.join(vdir, "vst.json")
    vj = json.load(open(vj_path))
    os.makedirs(BASE, exist_ok=True)
    base = os.path.join(BASE, pid + ".conf")
    if not os.path.exists(base):
        src = os.path.join(vdir, vj["layout"]) if vj.get("layout") and vj["layout"] != "layout.conf" else \
            os.path.join(vdir, "layout.conf") if vj.get("layout") else os.path.join(vdir, "build", "layout.auto.conf")
        shutil.copy(src, base)
    lines = open(base).read().splitlines()
    hw = bool(lines) and lines[0].startswith("# hwpanel")   # panels.py: final positions, keep as written
    names = param_names(vdir)
    top, tabs, cur = [], [], None
    for l in lines:
        if l.startswith("[tab"):
            cur = [l]
            tabs.append(cur)
        elif cur is None:
            if not l.startswith(("theme_", "style=", "art_css", "knob_look", "toggle_look")):
                top.append(l)
        else:
            cur.append(l)
    out = ["# hardware skin: generated by ~/force-work/skins/hwskin.py from skins/base/%s.conf; edit the theme there" % pid]
    out += [l for l in top if l.strip() and not l.startswith("#")]
    out += theme_lines(t)
    out.append("art_css=skin.css")
    if t["knob"] != "drawn":
        out.append("knob_look=%s" % t["knob"])
    out.append("toggle_look=%s" % t.get("toggle", "led"))
    for f in os.listdir(vdir):   # drawings of pages a previous layout had, and its hardware images
        if re.match(r"panel_\d+\.svg$", f) or f.startswith("hw_"):
            os.remove(os.path.join(vdir, f))
    ap = os.path.join(BASE, pid + ".art.json")
    hart = json.load(open(ap)) if hw and os.path.exists(ap) else {"pages": {}, "assets": {}, "seg_text": True}
    for name, body in hart["assets"].items():
        open(os.path.join(vdir, name), "w").write(body)
    for n, tab in enumerate(tabs):
        body = list(tab[1:]) if hw else centre(tidy([squeeze(l) for l in tab[1:]], names))
        frames = frame_rects(body)
        svg = "panel_%d.svg" % n
        if str(n) in hart["pages"]:   # a hardware page (hwpanel.Page): its own artwork
            import hwpanel
            art = '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="628" viewBox="0 0 1280 628">%s\n%s\n</svg>' % (
                hwpanel.DEFS, hart["pages"][str(n)])
        else:
            art = panel_svg(t, frames)
        open(os.path.join(vdir, svg), "w").write(art)
        out += ["", tab[0], "art file=%s" % svg]
        if t.get("band_knobs"):
            body = band_knob_lines(body, vdir)
        out += [l for l in body if l.strip()]
    open(os.path.join(vdir, "layout.conf"), "w").write("\n".join(out) + "\n")
    open(os.path.join(vdir, "skin.css"), "w").write(css(t) + ("" if hart.get("seg_text", True) else
                                                            ".seg.look-image .seg-tx { display: none; }\n"))
    vj["layout"] = "layout.conf"
    vj["art"] = "html"
    json.dump(vj, open(vj_path, "w"), indent=1)
    print("%-10s %s: %d tabs" % (pid, vdir, len(tabs)))


def band_knob_lines(body, vdir):
    """4K EQ: each band's knobs get its console colour (a cap image per colour)."""
    out = []
    for l in body:
        m = re.match(r"knob .*key=(\S+)", l)
        if m:
            k = m.group(1).lower()
            band = next((b for p_, b in (("hf_", "hf"), ("hm_", "hmf"), ("lm_", "lmf"), ("lf_", "lf"), ("hpf", "hp"),
                                          ("lpf", "lp"), ("input", "io"), ("output", "io")) if k.startswith(p_)), None)
            if band:
                f = "knob_%s.svg" % band
                p = os.path.join(vdir, f)
                if not os.path.exists(p):
                    open(p, "w").write(cap_svg(BAND_COLOURS[band]))
                l += " img=%s" % f
        out.append(l)
    return out


def cap_svg(col):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">'
            '<circle cx="48" cy="48" r="46" fill="#1b1c1e"/><circle cx="48" cy="48" r="36" fill="#%s"/>'
            '<circle cx="40" cy="38" r="22" fill="#fff" opacity="0.12"/>'
            '<line x1="48" y1="10" x2="48" y2="34" stroke="#f4f4f2" stroke-width="6" stroke-linecap="round"/></svg>' % col)


if __name__ == "__main__":
    for pid in sys.argv[1:] or list(THEMES):
        build(pid)
