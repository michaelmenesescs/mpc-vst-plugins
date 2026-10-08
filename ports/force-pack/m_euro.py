"""Eurorack and desktop-synth pages (hwpanel.Page): Braids, Plaits, MicroFreak, Serge, the ML-185 sequencer.
Each function names its reference. Module coordinates are taken from the reference drawing and scaled; the plugins'
extra controls are drawn as sister modules in the same finish, side by side in a rack with rails."""
from hwpanel import (Page, T, rect, line, circle, path, ticks, dots, numbers, screw, hexscrew, led, brushed, grain, wood,
                     knob_img, svg_doc, pt, SANS, NARROW, ROUND)

THIN = "Titillium Web, FreeSans, sans-serif"


def rails(p, ink="#9a9a9a"):
    p.add(rect(0, 0, 1280, 628, "#101010"))
    for y in (0, 616):
        p.add(rect(0, y, 1280, 12, "#b9bbbd"), rect(0, y + 5, 1280, 2, "#7d7f81"))
        for x in range(24, 1280, 64):
            p.add(circle(x, y + 6, 3, "#5d5f61"))


def mi_panel(p, x, y, w, h, name, sub=None):
    """A Mutable-style aluminium panel: brushed, a faint ornament band under the name, two mounting screws."""
    p.add(brushed(x, y, w, h, "#d9dadb"), rect(x, y, w, h, "none", stroke="#9a9c9e", sw=1),
          rect(x + 2, y + 48, w - 4, 6, "#c9cacb"),
          '<rect x="%g" y="%g" width="%g" height="6" fill="url(#hw-orn)"/>' % (x + 2, y + 48, w - 4))
    p.add(circle(x + 22, y + 16, 7, "#1a1a1a"), circle(x + w - 22, y + 16, 7, "#1a1a1a"),
          circle(x + 22, y + h - 16, 7, "#1a1a1a"), circle(x + w - 22, y + h - 16, 7, "#1a1a1a"))
    if sub:
        p.add(T(x + 40, y + 30, name, 32, "#222", 400, font=THIN, sp=0.01, anchor="start"),
              T(x + 52 + len(name) * 15, y + 35, sub, 14, "#222", 600, font=THIN, anchor="start"))
    else:
        p.add(T(x + w / 2, y + 30, name, 32, "#222", 400, font=THIN, sp=0.01))


ORN = ('<defs><pattern id="hw-orn" width="10" height="6" patternUnits="userSpaceOnUse">'
       '<path d="M0 3 L5 0 L10 3 L5 6 Z" fill="none" stroke="#a8aaac" stroke-width="0.8"/></pattern></defs>')


def mi_knob(cap="#eeeeee", rr=0.95, big=False):
    """Mutable knob: a black skirt and a coloured or white cap, the pointer a white line through the skirt."""
    return knob_img(body="#151515", edge="#000", cap=cap, cap_r=0.66 if big else 0.6, cap_edge="#000",
                    line_c="#f4f4f4", line=(0.6 if big else 0.55, 1.0), line_w=6, shine=0.25, rr=rr)


def jack(x, y, r=13, ring="#c8c8c8"):
    return circle(x, y, r, "url(#hw-screw)", "#666", 1) + circle(x, y, r * 0.55, "#111") + circle(x, y, r * 0.75, "none", ring, 1.5)


def badge(p, x, y, s, c, w=None):
    w = w or len(s) * 9 + 18
    p.add(rect(x - w / 2, y - 10, w, 20, c, rx=3), T(x, y, s, 12, "#fff", 700, sp=0.04))


# ---- Braids --------------------------------------------------------------------------------------------------------
# Reference: Mutable Instruments' Braids manual drawing (pichenettes.github.io/mutable-instruments-documentation).
# 16HP panel: the name, the 4-character green display with the EDIT encoder (here: the model list, shown in the
# display), FINE / COARSE / FM, then TIMBRE, MODULATION, COLOR with their colour badges, then the jacks. The plugin
# has no FINE or TIMBRE-modulation pots, so those two are printed (dimmed) where the module has them. The envelope,
# filter and level the plugin adds are sister panels in the same rack.
def pbraids(params):
    p = Page("BRAIDS", vink="#1a1a1a", lab=dict(size=14, fill="#222", font=THIN, weight=700, sp=0.04))
    p.add(ORN)
    rails(p)
    s = 600 / 516.0
    X0, Y0 = 16, 14

    def B(x, y):
        return X0 + x * s, Y0 + y * s
    mi_panel(p, X0, Y0, 298 * s, 600, "Braids", "macro oscillator")
    p.asset("mi_w.svg", mi_knob())
    p.asset("mi_t.svg", mi_knob("#1f7f86"))
    p.asset("mi_r.svg", mi_knob("#a8224a"))
    # display + EDIT
    dx, dy = B(19, 68)
    p.add(rect(dx, dy, 181 * s, 67 * s, "#3b3f40", rx=6), rect(dx + 6, dy + 6, 181 * s - 12, 67 * s - 12, "#262a2a", rx=4))
    ex, ey = B(245, 105)
    p.add(circle(ex, ey, 34, "#1b1b1b", "#000"), circle(ex - 8, ey - 10, 18, "#fff", extra=' opacity="0.06"'),
          T(ex, ey + 46, "EDIT", 14, "#222", 700), line(dx + 181 * s, ey, ex - 34, ey, "#222", 1, extra=' stroke-dasharray="2 3"'))
    p.popup("engine", dx + 181 * s / 2, dy + 67 * s / 2, int(181 * s - 20), int(67 * s - 16), label="", field=False, accent="#9cf23a")

    def kn(k, x, y, img, label, r=31):
        cx, cy = B(x, y)
        if k:
            p.knob(k, cx, cy, r, label, img=img, lab=None)
        else:
            p.add('<image href="%s" x="%g" y="%g" width="%g" height="%g" opacity="0.45"/>' % ("data:image/svg+xml;base64," +
                  _b64(mi_knob()), cx - r - 4, cy - r - 4, 2 * r + 8, 2 * r + 8))
        return cx, cy
    for k, x, label in ((None, 52, "FINE"), ("octave_transpose", 149, "COARSE"), ("fm", 245, "FM")):
        cx, cy = kn(k, x, 203, "hw_mi_w.svg", label)
        p.add(T(cx, cy - 44, label, 14, "#222" if k else "#888", 700))
    cx, cy = B(245, 203)
    p.add(T(cx - 26, cy - 38, "−", 14, "#222", 700), T(cx + 26, cy - 38, "+", 14, "#222", 700))
    for k, x, img, label, c in (("timbre", 52, "hw_mi_t.svg", "TIMBRE", "#1f7f86"), (None, 149, "hw_mi_t.svg", "MODULATION", "#1f7f86"),
                                ("color", 245, "hw_mi_r.svg", "COLOR", "#a8224a")):
        cx, cy = kn(k, x, 298, img, label)
        badge(p, cx, cy - 46, label, c if k else "#8fb3b5")
    # jacks
    for x, l, c in ((30, "TRIG", None), (75, "V/OCT", None), (121, "FM", None), (167, "TIMBRE", "#1f7f86"), (213, "COLOR", "#a8224a")):
        jx, jy = B(x, 405)
        if c:
            p.add(rect(jx - 26, jy - 39, 52, 18, c, rx=3), T(jx, jy - 30, l, 10, "#fff", 700))
        else:
            p.add(T(jx, jy - 30, l, 13, "#222", 700))
        p.add(jack(jx, jy))
    ox, oy = B(268, 405)
    p.add(rect(ox - 26, oy - 50, 52, 76, "#3b3f40", rx=4), T(ox, oy - 34, "OUT", 13, "#eee", 700), jack(ox, oy))
    # sister panels: AMP ENV, FILTER, FILTER ENV
    x = X0 + 298 * s + 8
    widths = [262, 320, 262]
    p.asset("mi_wb.svg", mi_knob(big=True))

    def panel_knob(k, cx, cy, label, r=30, img="hw_mi_w.svg"):
        p.knob(k, cx, cy, r, label, img=img, lab=-(r + 18))

    # AMP ENV
    w = widths[0]
    mi_panel(p, x, Y0, w, 600, "Envelope")
    for i, (k, l) in enumerate((("attack", "ATTACK"), ("decay", "DECAY"), ("sustain", "SUSTAIN"), ("release", "RELEASE"))):
        panel_knob(k, x + w * (0.28 if i % 2 == 0 else 0.72), Y0 + 150 + (i // 2) * 140, l)
    panel_knob("volume", x + w / 2, Y0 + 440, "LEVEL", r=34, img="hw_mi_r.svg")
    badge(p, x + w / 2, Y0 + 380, "VCA", "#a8224a", 60)
    x += w + 8
    # FILTER
    w = widths[1]
    mi_panel(p, x, Y0, w, 600, "Filter")
    panel_knob("cutoff", x + w / 2, Y0 + 170, "FREQUENCY", r=52, img="hw_mi_wb.svg")
    panel_knob("resonance", x + w * 0.27, Y0 + 360, "RESONANCE")
    panel_knob("filt_env", x + w * 0.73, Y0 + 360, "ENV AMOUNT", img="hw_mi_t.svg")
    for i, l in enumerate(("IN", "FREQ", "OUT")):
        p.add(T(x + w * (0.22 + 0.28 * i), Y0 + 470, l, 13, "#222", 700), jack(x + w * (0.22 + 0.28 * i), Y0 + 500))
    x += w + 8
    # FILTER ENV
    w = widths[2]
    mi_panel(p, x, Y0, w, 600, "Envelope")
    p.add(T(x + w / 2, Y0 + 72, "FILTER", 13, "#555", 700, sp=0.2))
    for i, (k, l) in enumerate((("f_attack", "ATTACK"), ("f_decay", "DECAY"), ("f_sustain", "SUSTAIN"), ("f_release", "RELEASE"))):
        panel_knob(k, x + w * (0.28 if i % 2 == 0 else 0.72), Y0 + 150 + (i // 2) * 140, l, img="hw_mi_t.svg")
    for i, l in enumerate(("GATE", "OUT")):
        p.add(T(x + w * (0.3 + 0.4 * i), Y0 + 470, l, 13, "#222", 700), jack(x + w * (0.3 + 0.4 * i), Y0 + 500))
    p.qrow("engine", "octave_transpose", "fm", "timbre", "color", "cutoff", "resonance", "filt_env")
    p.qrow("attack", "decay", "sustain", "release", "f_attack", "f_decay", "f_sustain", "f_release")
    p.qrow("volume")
    return [p]


def _b64(s):
    import base64
    return base64.b64encode(s.encode()).decode()


# ---- Plaits --------------------------------------------------------------------------------------------------------
# Reference: Mutable Instruments' Plaits manual drawing. 12HP: the two model buttons over a column of eight LEDs with
# the model icons either side, FREQUENCY and HARMONICS (large), TIMBRE and MORPH, the three FM / modulation
# attenuverters, the jacks. The plugin's 24 models are Plaits 1.2's three banks (the LED shows the bank's colour at
# the model's position: here a picture per model) and the model name under the column opens the full list. The LPG,
# AUX and play settings are a sister panel.
P_BANK = ["#f2a516", "#3fd15a", "#e8344a"]


def leds_plaits(sel):
    o = []
    for i in range(8):
        y = 14 + i * 26
        lit = sel % 8 == i
        c = P_BANK[sel // 8] if lit else "#5a5a5a"
        if lit:
            o.append(circle(18, y, 13, c, extra=' opacity="0.35"'))
        o.append(circle(18, y, 8, c, "#222", 1.2))
    return svg_doc(36, 220, "".join(o))


def pplaits(params):
    p = Page("PLAITS", vink="#1a1a1a", lab=dict(size=15, fill="#222", font=THIN, weight=700, sp=0.04))
    p.add(ORN)
    rails(p)
    s = 600 / 534.0
    X0, Y0 = 16, 14

    def P(x, y):
        return X0 + x * s, Y0 + y * s
    W = 324 * s
    mi_panel(p, X0, Y0, W, 600, "Plaits")
    p.asset("mi_w.svg", mi_knob())
    p.asset("mi_wb.svg", mi_knob(big=True))
    p.asset("mi_s.svg", knob_img(body="#1a1a1a", edge="#000", line_c="#f4f4f4", line=(0.2, 1.0), line_w=8, shine=0.3, rr=0.9))
    lx, ly = P(163, 104)

    files = [p.asset("pl_led_%d.svg" % i, leds_plaits(i)) for i in range(24)]
    p.picture("engine", int(lx - 18), int(ly - 14), 36, 220, files)
    icons = ["~", "∿", "⌁", "△", "≋", "▦", "!", "◇"]
    for i in range(8):
        y = ly + i * 26
        p.add(circle(lx - 34, y, 9, "#1f8f8a"), T(lx - 34, y, icons[i], 10, "#fff", 700),
              circle(lx + 34, y, 9, "#e8344a"), T(lx + 34, y, icons[7 - i], 10, "#fff", 700))
    p.popup("engine", lx, Y0 + 69, 100, 26, label="", field=False, accent="#1a1a1a")
    for k, x, y, r, img, l in (("octave_transpose", 88, 121, 46, "hw_mi_wb.svg", "FREQUENCY"), ("harmonics", 244, 121, 46, "hw_mi_wb.svg", "HARMONICS"),
                               ("timbre", 82, 236, 33, "hw_mi_w.svg", "TIMBRE"), ("morph", 244, 236, 33, "hw_mi_w.svg", "MORPH")):
        cx, cy = P(x, y)
        cx = min(max(cx, X0 + 70), X0 + W - 70)
        p.knob(k, cx, cy, r, l, img=img, lab=None)
        p.add(T(cx, cy - r - 16 if r < 40 else cy - r - 14, l, 15, "#222", 700))
    fx, fy = P(163, 303)
    p.add(T(fx, fy, "FM", 15, "#222", 700))
    for k, x, l in (("timbre_mod", 84, "TIMBRE"), ("fm_amount", 163, "FM"), ("morph_mod", 243, "MORPH")):
        cx, cy = P(x, 340)
        p.add(T(cx - 18, cy - 24, "−", 11, "#222"), T(cx + 18, cy - 24, "+", 11, "#222"))
        p.knob(k, cx, cy, 17, l, img="hw_mi_s.svg", lab=None, vs=14)
    for i, (x, l) in enumerate(((67, "MODEL"), (116, ""), (163, ""), (209, ""), (257, "HARMO"))):
        jx, jy = P(x, 418)
        p.add(T(jx, jy - 22, l, 12, "#222", 700), jack(jx, jy, 12))
    for x, l in ((67, "TRIG"), (116, "LEVEL"), (163, "V/OCT")):
        jx, jy = P(x, 478)
        p.add(T(jx, jy - 22, l, 12, "#222", 700), jack(jx, jy, 12))
    ox, oy = P(209, 456)
    p.add(rect(ox - 26, oy, 120, 56, "#3b3f40", rx=4))
    for x, l in ((209, "OUT"), (257, "AUX")):
        jx, jy = P(x, 478)
        p.add(T(jx, jy - 20, l, 12, "#eee", 700), jack(jx, jy, 12))
    # sister panel: LPG / AUX / play
    x = X0 + W + 10
    w = 1264 - x
    mi_panel(p, x, Y0, w, 600, "Plaits", "low pass gate · play")
    sec = [("LOW PASS GATE", [("decay", "DECAY"), ("lpg_colour", "COLOUR"), ("attack", "ATTACK")], "#1f7f86"),
           ("OUTPUT", [("aux_mix", "AUX MIX"), ("velocity_sensitivity", "VELOCITY")], "#a8224a")]
    cx = x + 40
    for name, ks, c in sec:
        sw_ = len(ks) * 150
        badge(p, cx + sw_ / 2, Y0 + 100, name, c, sw_ - 30)
        for i, (k, l) in enumerate(ks):
            kx = cx + 75 + i * 150
            p.knob(k, kx, Y0 + 210, 40, l, img="hw_mi_w.svg", lab=-62)
        cx += sw_ + 20
    p.add(T(x + 150, Y0 + 330, "FM PRESET", 14, "#222", 700))
    p.popup("fm_preset", x + 150, Y0 + 372, 230, 44, label="", accent="#1a1a1a")
    p.add(T(x + 450, Y0 + 330, "LEGATO", 14, "#222", 700))
    p.switch("legato", x + 450, Y0 + 372, 2, vertical=False, sw=90, sh=40)
    for i in range(6):
        jx = x + 80 + i * (w - 160) / 5
        p.add(jack(jx, Y0 + 520, 12))
    p.qrow("engine", "octave_transpose", "harmonics", "timbre", "morph", "timbre_mod", "fm_amount", "morph_mod")
    p.qrow("decay", "lpg_colour", "attack", "aux_mix", "velocity_sensitivity", "fm_preset")
    return [p]


# ---- Arturia MicroFreak (MrHyde) -----------------------------------------------------------------------------------
# Reference: Wikimedia Commons "MicroFreak.jpg" and the MicroFreak's panel legend. Dark slate panel, white legends:
# top row GLIDE (black) | DIGITAL OSCILLATOR: TYPE, WAVE, TIMBRE, SHAPE (orange) | the printed MATRIX grid | the
# OLED display (here showing the oscillator type) with PARAPHONIC (the plugin's voice mode). Lower row: (the ARP/SEQ
# corner, which the plugin doesn't have, carries its pitch, FM and aux) ANALOG FILTER (TYPE button with LP/BP/HP
# LEDs, CUTOFF, RESONANCE) | LFO (SHAPE LEDs, RATE white, SYNC) | CYCLING ENVELOPE (MODE LEDs, RISE, FALL) |
# ENVELOPE (ATTACK, DECAY, SUSTAIN, RELEASE) | MASTER. The MATRIX page is the panel's grid: sources down, destinations
# across, an amount in each cell; MORE holds the rest in the same finish.
MF_BG, MF_INK, MF_DIM, MF_BLUE, MF_OR = "#2e3338", "#f2f4f6", "#9aa3ad", "#52b6ff", "#f26a1b"


def mf_knob(c, line_c):
    return svg_doc(96, 96, '<circle cx="48" cy="50" r="40" fill="#000" opacity="0.4"/>' +
                   '<polygon points="%s" fill="%s" stroke="#000" stroke-opacity="0.4" stroke-width="1"/>' % (
                       " ".join("%.1f,%.1f" % pt(48, 48, 40, a) for a in range(0, 360, 15)), c) +
                   '<circle cx="48" cy="48" r="32" fill="%s"/><circle cx="40" cy="38" r="20" fill="#fff" opacity="0.12"/>' % c +
                   '<line x1="48" y1="10" x2="48" y2="34" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % line_c)


def mf_leds(n, sel=None):
    pass


def mf_page(name):
    p = Page(name, vink="#f2f4f6", lab=dict(size=12, fill=MF_INK, font=SANS, weight=700, sp=0.03), seg_text=False)
    p.add(rect(0, 0, 1280, 628, "#1d2024"), rect(6, 6, 1268, 616, MF_BG, rx=10), grain(6, 6, 1268, 616))
    p.asset("mf_or.svg", mf_knob(MF_OR, "#2a1a10"))
    p.asset("mf_wh.svg", mf_knob("#eceae4", "#222"))
    p.asset("mf_bk.svg", mf_knob("#151719", "#f2f2f2"))
    p.asset("mf_led.svg", svg_doc(70, 22, circle(10, 11, 5, "#3a4148", "#111")))
    p.asset("mf_ledon.svg", svg_doc(70, 22, circle(10, 11, 8, MF_BLUE, extra=' opacity="0.35"') + circle(10, 11, 5, MF_BLUE, "#123")))
    return p


def mf_section(p, x0, x1, y, name):
    p.add(line(x0, y, x1, y, MF_DIM, 1.2), rect((x0 + x1) / 2 - len(name) * 5.2 - 8, y - 9, len(name) * 10.4 + 16, 18, MF_BG),
          T((x0 + x1) / 2, y, name, 13, MF_INK, 700, sp=0.12))


def mf_ledsw(p, key, x, y, names, label):
    """A MicroFreak selector: a button that steps, LEDs beside it naming each position (tap an LED's row)."""
    n = len(names)
    p.add(rect(x - 46, y - n * 12 - 4, 22, 22, "#4a525a", rx=11, stroke="#111") if False else "")
    p.switch(key, x, y, n, vertical=True, sw=70, sh=22, img="hw_mf_led.svg", img_on="hw_mf_ledon.svg")
    for i, s in enumerate(names):
        p.add(T(x - 14, y - n * 12 + 12 + i * 24, s, 10, MF_INK, 700, anchor="start"))
    p.add(T(x, y - n * 12 - 14, label, 11, MF_DIM, 700))


def pmrhyde(params):
    srcs = [("lfo", "LFO"), ("env", "ENV"), ("cycle_env", "CYC ENV"), ("random", "RANDOM"), ("velocity", "VELOCITY"),
            ("poly_aftertouch", "PRESS")]
    dests = [("pitch", "PITCH"), ("harmonics", "WAVE"), ("timbre", "TIMBRE"), ("cutoff", "CUTOFF"), ("assign1", "ASSIGN 1"),
             ("assign2", "ASSIGN 2")]

    def K(p, k, x, y, r, c, label, lab=-48, **kw):
        p.knob(k, x, y, r, label, img="hw_mf_%s.svg" % c, lab=lab, **kw)

    p = mf_page("PANEL")
    # top row
    K(p, "glide_ms", 64, 112, 28, "bk", "GLIDE")
    p.add(T(64, 196, "OCTAVE", 11, MF_INK, 700), circle(44, 222, 11, "#4a525a", "#111"), circle(84, 222, 11, "#4a525a", "#111"),
          T(44, 222, "‹", 14, MF_INK), T(84, 222, "›", 14, MF_INK))
    mf_section(p, 130, 640, 44, "DIGITAL OSCILLATOR")
    p.rotary("model", 196, 112, 30, 17, lambda a: mf_knob(MF_OR, "#2a1a10").replace('<line', '<g transform="rotate(%g 48 48)"><line' % a).replace('round"/>', 'round"/></g>'),
             a0=-150, a1=150, field_w=124, field_dy=54, label="TYPE")
    p.add(T(196, 66, "TYPE", 12, MF_INK, 700))
    for k, x, l in (("harmonics", 318, "WAVE"), ("timbre", 436, "TIMBRE"), ("morph", 554, "SHAPE")):
        K(p, k, x, 112, 30, "or", l, lab=-46)
    # matrix grid (printed)
    gx, gy = 670, 64
    p.add(T(gx + 150, 44, "MATRIX", 13, MF_INK, 700, sp=0.12))
    for j, (_, dl) in enumerate(dests):
        p.add(T(gx + 82 + j * 38, gy + 4, dl.split()[0] if j < 4 else "ASGN%d" % (j - 3), 9, MF_INK, 700))
    for i, (_, sl) in enumerate(srcs):
        y = gy + 24 + i * 22
        p.add(T(gx + 54, y, sl, 9, MF_INK, 700, anchor="end"))
        for j in range(6):
            p.add(circle(gx + 82 + j * 38, y, 3.5, "#4a525a"), line(gx + 60, y, gx + 290, y, "#41484f", 0.8))
    # display + voice mode
    p.add(rect(980, 52, 200, 96, "#0b0d0f", rx=6, stroke="#555"), rect(990, 62, 180, 76, "#03080c", rx=3))
    p.readout("model", 1080, 100, 170, 56, "")
    p.add(T(1080, 170, "PARAPHONIC", 11, MF_BLUE, 700))
    p.switch("voice_mode", 1080, 210, 3, vertical=False, sw=70, sh=22, img="hw_mf_led.svg", img_on="hw_mf_ledon.svg")
    for i, s in enumerate(("MONO", "POLY", "LEGATO")):
        p.add(T(1080 + (i - 1) * 72 + 8, 230, s, 9, MF_INK, 700))
    p.add(line(20, 262, 1260, 262, "#41484f", 1.5))
    # lower row
    mf_section(p, 20, 220, 296, "OSC MOD")
    K(p, "pitch", 70, 380, 26, "wh", "PITCH", lab=-44)
    K(p, "fm_amount", 170, 380, 26, "wh", "FM", lab=-44)
    K(p, "aux_mix", 120, 520, 26, "wh", "AUX MIX", lab=-44)
    mf_section(p, 240, 500, 296, "ANALOG FILTER")
    mf_ledsw(p, "filter_mode", 290, 400, ["LPF", "BPF", "HPF"], "TYPE")
    K(p, "filter_cutoff", 410, 380, 36, "bk", "CUTOFF", lab=-54)
    K(p, "filter_resonance", 410, 530, 26, "bk", "RESONANCE", lab=-44)
    mf_section(p, 520, 740, 296, "LFO")
    mf_ledsw(p, "lfo_shape", 570, 420, ["SINE", "TRI", "SAW", "SQR", "RAND", "SMTH"], "SHAPE")
    K(p, "lfo_rate", 680, 380, 30, "wh", "RATE", lab=-48)
    p.add(T(680, 470, "SYNC", 11, MF_DIM, 700))
    p.switch("lfo_rate_mode", 690, 512, 2, vertical=True, sw=70, sh=22, img="hw_mf_led.svg", img_on="hw_mf_ledon.svg")
    p.add(T(676, 501, "FREE", 10, MF_INK, 700, anchor="start"), T(676, 525, "SYNC", 10, MF_INK, 700, anchor="start"))
    mf_section(p, 760, 980, 296, "CYCLING ENVELOPE")
    mf_ledsw(p, "cycle_shape", 806, 400, ["LIN", "EXP", "LOG"], "SHAPE")
    K(p, "cycle_attack_ms", 920, 380, 28, "bk", "RISE", lab=-46)
    K(p, "cycle_decay_ms", 920, 530, 28, "bk", "FALL", lab=-46)
    mf_section(p, 1000, 1180, 296, "ENVELOPE")
    K(p, "env_attack_ms", 1040, 380, 26, "bk", "ATTACK", lab=-44)
    K(p, "env_decay_ms", 1136, 380, 26, "bk", "DECAY", lab=-44)
    K(p, "env_sustain", 1040, 530, 26, "bk", "SUSTAIN", lab=-44)
    K(p, "env_release_ms", 1136, 530, 26, "bk", "RELEASE", lab=-44)
    K(p, "volume", 1230, 380, 26, "bk", "MASTER", lab=-44)
    p.add(T(640, 604, "MrHyde", 18, MF_DIM, 700, sp=0.3))
    p.qrow("glide_ms", "model", "harmonics", "timbre", "morph", "voice_mode")
    p.qrow("pitch", "fm_amount", "filter_cutoff", "filter_resonance", "lfo_rate", "cycle_attack_ms", "cycle_decay_ms", "env_attack_ms")
    p.qrow("aux_mix", "env_decay_ms", "env_sustain", "env_release_ms", "volume", "filter_mode", "lfo_shape", "cycle_shape")
    pages = [p]

    # MATRIX: the panel's grid
    p = mf_page("MATRIX")
    mf_section(p, 20, 1260, 34, "MATRIX")
    X0, DX, Y0, DY = 250, 168, 140, 80
    for j, (d, dl) in enumerate(dests):
        x = X0 + j * DX
        p.add(T(x, 70, dl, 15, MF_INK, 700, sp=0.08))
        if d.startswith("assign"):
            p.popup(d + "_target", x, 104, 150, 32, label="", accent=MF_BLUE)
    for i, (s, sl) in enumerate(srcs):
        y = Y0 + 30 + i * DY
        p.add(line(150, y, 1240, y, "#41484f", 1), T(150, y, sl, 15, MF_INK, 700, anchor="end"))
        for j, (d, dl) in enumerate(dests):
            x = X0 + j * DX
            p.knob("%s_mod_%s_amt" % (d, s), x, y, 20, "", img="hw_mf_wh.svg" if j < 4 else "hw_mf_or.svg", vs=15, bw=130)
    for i, (s, sl) in enumerate(srcs):
        p.qrow(*["%s_mod_%s_amt" % (d, s) for d, _ in dests])
    pages.append(p)

    # MORE
    p = mf_page("MORE")
    groups = [("LOW PASS GATE", 20, 270), ("LFO", 290, 520), ("CYCLING ENV", 540, 820), ("ENV", 840, 960), ("CURVES", 980, 1260)]
    for n, a, b in groups:
        mf_section(p, a, b, 40, n)
    K(p, "lpg_decay", 90, 130, 30, "wh", "DECAY")
    K(p, "lpg_color", 200, 130, 30, "wh", "COLOR")

    def onoff(k, x, y, l, names=("OFF", "ON")):
        p.add(T(x, y - 40, l, 11, MF_DIM, 700))
        p.switch(k, x + 10, y, 2, vertical=True, sw=70, sh=22, img="hw_mf_led.svg", img_on="hw_mf_ledon.svg")
        p.add(T(x - 4, y - 11, names[0], 10, MF_INK, 700, anchor="start"), T(x - 4, y + 13, names[1], 10, MF_INK, 700, anchor="start"))
    onoff("lfo_retrig", 340, 140, "RETRIG")
    K(p, "lfo_phase", 460, 130, 30, "wh", "PHASE")
    onoff("cycle_sync", 590, 140, "SYNC")
    onoff("cycle_retrig", 680, 140, "RETRIG")
    onoff("cycle_bipolar", 770, 140, "BIPOLAR")
    onoff("env_retrig", 890, 140, "RETRIG")
    K(p, "velocity_curve", 1060, 130, 30, "bk", "VELOCITY")
    K(p, "poly_aftertouch_curve", 1180, 130, 30, "bk", "PRESSURE")
    mf_section(p, 20, 640, 270, "RANDOM")
    mf_ledsw(p, "random_mode", 70, 390, ["S&H", "SMOOTH", "DRIFT"], "MODE")
    K(p, "random_rate", 230, 380, 30, "wh", "RATE")
    onoff("random_rate_mode", 340, 390, "SYNC", ("FREE", "SYNC"))
    K(p, "random_slew", 460, 380, 30, "wh", "SLEW")
    onoff("random_retrig", 570, 390, "RETRIG")
    mf_section(p, 660, 1260, 270, "VOICES")
    for i, (k, l) in enumerate((("polyphony", "POLYPHONY"), ("unison", "UNISON"), ("detune", "DETUNE"), ("spread", "SPREAD"), ("pan", "PAN"))):
        K(p, k, 720 + i * 120, 380, 30, "bk", l)
    p.add(T(640, 604, "MrHyde", 18, MF_DIM, 700, sp=0.3))
    p.qrow("lpg_decay", "lpg_color", "lfo_phase", "velocity_curve", "poly_aftertouch_curve")
    p.qrow("random_rate", "random_slew", "polyphony", "unison", "detune", "spread", "pan")
    pages.append(p)
    return pages


# ---- Serge (Denis) ----------------------------------------------------------------------------------------------------
# Reference: Wikimedia Commons "Serge Modular.jpg" and the Serge "paperface" panels: cream panels in a wooden boat,
# black module names, small black knobs, banana jacks in black (audio), blue (CV in) and red (out), joined to their
# knobs by printed lines. One 4U row of the plugin's modules, left to right as its signal runs: the complex
# oscillator, the modulator, the mixer, the wave multiplier (folder), the VCFQ filter, the envelope and the
# smooth & stepped / LFO module. The MATRIX page is a Serge-style patch grid (a source per row, a destination per
# column, an amount knob at each crossing); PATCH holds presets, play mode and the random buttons.
SG_PAPER, SG_INK, SG_BLUE, SG_RED = "#e8e1c9", "#181818", "#2f5fb0", "#c8302a"


def serge_knob():
    return knob_img(body="#161616", edge="#000", knurl="#262626", knurl_n=18, cap="#202020", cap_r=0.7, cap_edge="#000",
                    line_c="#f2f2f2", line=(0.1, 0.9), line_w=5, shine=0.22, rr=0.86)


def banana(x, y, c="#111", r=7):
    return circle(x, y, r + 3, "#b9b2a0", "#6a6454", 1) + circle(x, y, r, c, "#000", 1) + circle(x, y, r * 0.35, "#000")


def serge_case(p):
    p.add(wood(0, 0, 1280, 628, "#7a4a22"), rect(10, 10, 1260, 608, "#2a1a10", rx=4))


def serge_module(p, x, w, name, y=18, h=592):
    p.add(rect(x, y, w, h, SG_PAPER), grain(x, y, w, h), rect(x, y, w, h, "none", stroke="#9a937f", sw=1),
          rect(x + 6, y + 8, w - 12, 30, SG_INK, rx=2), T(x + w / 2, y + 23, name, 13 if len(name) < 14 else 11, SG_PAPER, 700, sp=0.08),
          circle(x + 10, y + h - 10, 3.5, "#8a8370"), circle(x + w - 10, y + h - 10, 3.5, "#8a8370"))


def pdenis(params):
    p = Page("DENIS", vink="#181818", lab=dict(size=12, fill=SG_INK, font=SANS, weight=700, sp=0.06))
    p.asset("sg_k.svg", serge_knob())
    serge_case(p)
    mods = [("COMPLEX OSC", 180), ("MODULATOR", 170), ("MIXER", 170), ("WAVE MULT", 170), ("VCFQ", 190), ("ENVELOPE", 200),
            ("SMOOTH & STEP", 164)]
    xs = []
    x = 14
    for n, w in mods:
        serge_module(p, x, w - 4, n)
        xs.append((x, w - 4))
        x += w

    def K(k, mi, fx, y, l, r=26, jack=SG_BLUE):
        mx, mw = xs[mi]
        cx = mx + mw * fx
        p.knob(k, cx, y, r, l, img="hw_sg_k.svg", lab=-(r + 18))
        if jack:   # its CV input jack, joined by a printed line
            jx = cx + (r + 22 if fx <= 0.5 else -(r + 22))
            p.add(line(cx, y, jx, y, SG_INK, 1.2), banana(jx, y, jack))

    def jacks(mi, labels):
        mx, mw = xs[mi]
        n = len(labels)
        for i, (l, c) in enumerate(labels):
            jx = mx + mw * (i + 0.5) / n
            p.add(T(jx, 548, l, 9, SG_INK, 700), banana(jx, 570, c))
        p.add(line(mx + 10, 530, mx + mw - 10, 530, SG_INK, 1))

    K("osc1_freq", 0, 0.42, 120, "FREQUENCY", r=34)
    K("osc1_timbre", 0, 0.42, 260, "TIMBRE")
    p.add(T(xs[0][0] + xs[0][1] / 2, 360, "∿  △  ⊓  ⩘", 18, SG_INK, 700))
    jacks(0, [("1V/OCT", SG_BLUE), ("FM", SG_BLUE), ("SINE", SG_RED), ("OUT", SG_RED)])
    K("osc2_pitch", 1, 0.42, 120, "PITCH", r=34)
    K("osc2_harmonics", 1, 0.42, 260, "HARMONICS")
    jacks(1, [("CV", SG_BLUE), ("SYNC", "#111"), ("OUT", SG_RED)])
    K("osc_mix", 2, 0.42, 120, "OSC MIX")
    K("noise_mix", 2, 0.42, 250, "NOISE")
    mx, mw = xs[2]
    p.add(T(mx + mw / 2, 330, "NOISE COLOUR", 11, SG_INK, 700))
    p.switch("noise_type", mx + mw / 2, 400, 3, vertical=True, sw=110, sh=28)
    jacks(2, [("IN 1", "#111"), ("IN 2", "#111"), ("OUT", SG_RED)])
    K("fold_depth", 3, 0.42, 120, "DEPTH", r=34)
    K("fold_type", 3, 0.42, 260, "SYMMETRY")
    jacks(3, [("IN", "#111"), ("CV", SG_BLUE), ("OUT", SG_RED)])
    K("filter_cutoff", 4, 0.42, 120, "FREQUENCY", r=34)
    K("filter_q", 4, 0.42, 250, "Q")
    mx, mw = xs[4]
    p.add(T(mx + mw / 2, 330, "RESPONSE", 11, SG_INK, 700))
    p.switch("filter_type", mx + mw / 2, 412, 4, vertical=True, sw=120, sh=26)
    jacks(4, [("IN", "#111"), ("CV", SG_BLUE), ("LP", SG_RED), ("BP", SG_RED)])
    mx, mw = xs[5]
    for i, (k, l) in enumerate((("attack", "RISE"), ("decay", "FALL"), ("sustain", "SUSTAIN"), ("release", "RELEASE"))):
        p.knob(k, mx + mw * (0.27 if i % 2 == 0 else 0.73), 120 + (i // 2) * 130, 24, l, img="hw_sg_k.svg", lab=-42)
    p.knob("vel_to_filter", mx + mw / 2, 400, 24, "VEL > FILTER", img="hw_sg_k.svg", lab=-42)
    jacks(5, [("GATE", SG_BLUE), ("TRIG", SG_BLUE), ("OUT", SG_RED)])
    mx, mw = xs[6]
    for i, (k, l) in enumerate((("lfo_rate", "LFO RATE"), ("sh_rate", "S&H RATE"), ("mod_depth_env", "ENV DEPTH"), ("mod_depth_noise", "NOISE DEPTH"))):
        p.knob(k, mx + mw / 2, 104 + i * 112, 22, l, img="hw_sg_k.svg", lab=-38)
    jacks(6, [("IN", "#111"), ("SMOOTH", SG_RED), ("STEP", SG_RED)])
    p.add(T(1262, 612, "DENIS", 11, "#d8c8a0", 700, anchor="end", sp=0.3))
    p.qrow("osc1_freq", "osc1_timbre", "osc2_pitch", "osc2_harmonics", "osc_mix", "noise_mix", "fold_depth", "fold_type")
    p.qrow("filter_cutoff", "filter_q", "attack", "decay", "sustain", "release", "vel_to_filter", "lfo_rate")
    p.qrow("sh_rate", "mod_depth_env", "mod_depth_noise")
    pages = [p]

    # MATRIX: the patch grid
    p = Page("MATRIX", vink="#181818", lab=dict(size=12, fill=SG_INK, font=SANS, weight=700, sp=0.06))
    p.asset("sg_k.svg", serge_knob())
    serge_case(p)
    serge_module(p, 14, 1252, "MODULATION MATRIX")
    dest = ["PITCH 1", "TIMBRE", "PITCH 2", "HARMONICS", "FOLD", "FOLD TYPE", "CUTOFF", "LEVEL"]
    src = [("ENVELOPE", SG_RED), ("LFO", SG_BLUE), ("S & H", "#2f9a55"), ("NOISE", "#111")]
    for c, d in enumerate(dest):
        x = 250 + c * 128
        p.add(T(x, 78, d, 12, SG_INK, 700), banana(x, 100, SG_BLUE), line(x, 108, x, 560, "#b3ab93", 1))
    for r, (s, col) in enumerate(src):
        y = 170 + r * 120
        p.add(T(130, y, s, 14, SG_INK, 700), banana(196, y, col), line(204, y, 1240, y, "#b3ab93", 1))
        for c in range(8):
            p.knob("mat_%d_%d" % (r, c), 250 + c * 128, y, 24, "", img="hw_sg_k.svg", vs=15)
        p.qrow(*["mat_%d_%d" % (r, c) for c in range(8)])
    pages.append(p)

    # PATCH: presets, play mode, random
    p = Page("PATCH", vink="#181818", lab=dict(size=13, fill=SG_INK, font=SANS, weight=700, sp=0.06))
    p.asset("sg_k.svg", serge_knob())
    serge_case(p)
    serge_module(p, 14, 420, "PRESET")
    p.add(T(224, 120, "PATCH", 13, SG_INK, 700))
    p.popup("preset", 224, 170, 340, 48, label="", accent="#c8302a")
    serge_module(p, 438, 380, "PLAY")
    p.knob("portamento", 540, 170, 30, "PORTAMENTO", img="hw_sg_k.svg", lab=-48)
    p.add(T(720, 120, "LEGATO", 12, SG_INK, 700), T(720, 300, "PADS", 12, SG_INK, 700))
    p.switch("legato", 720, 170, 2, vertical=True, sw=110, sh=30)
    p.switch("patch_mode", 720, 350, 2, vertical=True, sw=110, sh=30)
    serge_module(p, 822, 444, "RANDOM")
    for i, (k, l) in enumerate((("rnd_denis", "RND DENIS"), ("rnd_mod", "RND MOD"), ("rnd_patch", "RND PATCH"), ("matrix_reset", "RESET MATRIX"))):
        p.button(k, 940 + (i % 2) * 210, 150 + (i // 2) * 120, l, color="c8302a" if i < 3 else "181818")
    p.qrow("portamento", "preset", "legato", "patch_mode")
    pages.append(p)
    return pages
