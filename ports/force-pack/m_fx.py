"""Hardware pages for the effect plugins (hwpanel.Page), drawn from the units they model. Each function names its
reference. Names on the panels are the plugins' own; no manufacturer logos."""
from hwpanel import (Page, T, rect, line, circle, path, ticks, dots, numbers, screw, hexscrew, led, brushed, grain, wood,
                     knob_img, svg_doc, pt, SANS, NARROW, ROUND)


def chrome_knob(angle=None, rr=0.95, pointer=True):
    """The Space Echo's knob: a chrome skirt, a black ring, a spun-aluminium cap and a black pointer."""
    R = 48 * rr
    body = ('<defs><linearGradient id="c" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fdfdfd"/><stop offset="0.45" stop-color="#b9bcbe"/>'
            '<stop offset="0.6" stop-color="#eceeef"/><stop offset="1" stop-color="#76797b"/></linearGradient>'
            '<radialGradient id="s" cx="0.45" cy="0.4" r="0.7"><stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#cfd2d4"/>'
            '<stop offset="1" stop-color="#9a9da0"/></radialGradient></defs>'
            '<circle cx="48" cy="49.5" r="%g" fill="#000" opacity="0.4"/>'
            '<circle cx="48" cy="48" r="%g" fill="url(#c)" stroke="#555" stroke-width="1"/>'
            '<circle cx="48" cy="48" r="%g" fill="#111"/>'
            '<circle cx="48" cy="48" r="%g" fill="url(#s)" stroke="#666" stroke-width="0.8"/>'
            % (R, R, R * 0.8, R * 0.66))
    for i in range(12):   # the cap's spun rings
        body += '<circle cx="48" cy="48" r="%g" fill="none" stroke="#fff" stroke-opacity="0.18" stroke-width="0.6"/>' % (R * 0.05 * (i + 1))
    ptr = '<line x1="48" y1="48" x2="48" y2="%g" stroke="#111" stroke-width="4" stroke-linecap="round"/>' % (48 - R * 0.62)
    if angle is not None:
        ptr = '<g transform="rotate(%g 48 48)">%s</g>' % (angle, ptr)
    return svg_doc(96, 96, body + (ptr if pointer else ""))


def chrome_still():
    return chrome_knob(pointer=False)


def chrome_ptr():
    return svg_doc(96, 96, '<line x1="48" y1="48" x2="48" y2="%g" stroke="#111" stroke-width="4" stroke-linecap="round"/>' % (48 - 48 * 0.95 * 0.62))


# ---- RE-201 Space Echo (TapeDelay) --------------------------------------------------------------------------------
# Reference: Wikimedia Commons "RE201 Face.JPG". Tolex case; a chrome strip with the name lettering; the black panel
# with PEAK LEVEL and the VU meter, the MIC / INSTRUMENT VOLUME knobs (printed: the plugin has no input stage),
# the green MODE SELECTOR panel (twelve positions: here the plugin's twelve delay divisions, FREE where REVERB ONLY
# is), then BASS / TREBLE / REVERB VOLUME (here TONE and WIDTH) over REPEAT RATE, INTENSITY, ECHO VOLUME, the
# power lamp and switch; the jack strip along the bottom.
def ptape(params):
    INK = "#e9eee6"
    GREEN = "#2f4a2c"
    p = Page("TAPE ECHO", vink="#f2f2ea", lab=dict(size=13, fill=INK, font=SANS, weight=700, sp=0.05))
    still = p.asset("re_k.svg", chrome_still())
    ptr = p.asset("re_p.svg", chrome_ptr())
    p.add(rect(0, 0, 1280, 628, "#151515"), '<rect width="1280" height="628" filter="url(#hw-grain)"/>',
          rect(0, 0, 1280, 628, "#000", extra=' opacity="0.15"'))
    p.add(rect(10, 6, 1260, 616, "#191c1a", rx=4))
    # chrome name strip
    p.add(brushed(10, 6, 1260, 92, "#c9cccd"), line(10, 98, 1270, 98, "#0d0d0d", 3), line(10, 108, 1270, 108, "#c9cccd", 2),
          line(10, 112, 1270, 112, "#0d0d0d", 2))
    p.add(T(78, 56, "TAPE DELAY", 46, "#1a1a1a", 700, anchor="start", font=SANS, sp=0.02, stretch=1.08),
          T(450, 62, "MULTI HEAD ECHO", 22, "#1a1a1a", 700, anchor="start", font=SANS, sp=0.04))
    # left: peak lamp, VU meter, the (printed) input volumes
    p.add(led(139, 192, 9, lit=True), T(139, 222, "PEAK", 12, INK, 700), T(139, 238, "LEVEL", 12, INK, 700))
    p.add(rect(196, 140, 168, 112, "#2b2b2b", rx=3), rect(202, 146, 156, 100, "#e9e2c8", rx=2),
          path("M222 222 A 70 70 0 0 1 338 222", stroke="#2a2a2a", sw=1.5),
          path("M300 178 A 70 70 0 0 1 338 222", stroke="#c8261a", sw=5),
          T(280, 228, "VU", 13, "#2a2a2a", 700), line(280, 244, 236, 176, "#111", 2))
    for x, s in ((110, "MIC\nVOLUME"), (232, "MIC\nVOLUME"), (358, "INSTRUMENT\nVOLUME")):
        a, b = s.split("\n")
        p.add(T(x, 316, a, 12, INK, 700), T(x, 332, b, 12, INK, 700), ticks(x, 410, 42, 49, 11, "#9fb0a0", 1.6))
        p.add('<image href="data:image/svg+xml;base64,%s" x="%g" y="%g" width="80" height="80"/>' % (_b64(chrome_knob(-140)), x - 40, 370))
    p.add(line(171, 300, 171, 480, "#2f3a30", 2), line(293, 300, 293, 480, "#2f3a30", 2))
    # mode selector panel
    p.add(rect(443, 137, 206, 349, GREEN, rx=8), T(546, 162, "MODE SELECTOR", 15, INK, 700, sp=0.06))
    opts = ["FREE", "1/1", "1/2", "1/2d", "1/4", "1/4d", "1/4t", "1/8", "1/8d", "1/8t", "1/16", "1/16t"]
    angs = [180] + [-150 + 300 * i / 10 for i in range(11)]
    cx, cy = 546, 316
    p.add(path("M%g %g A 80 80 0 1 1 %g %g" % (*pt(cx, cy, 80, -150), *pt(cx, cy, 80, 150)), stroke="#a9b8a6", sw=15, extra=' opacity="0.6"'))
    for o, a in zip(opts, angs):
        px, py = pt(cx, cy, 80, a)
        p.add(T(px, py, o if a != 180 else "", 10, "#16200f" if a != 180 else INK, 700))
        x0, y0 = pt(cx, cy, 56, a)
        x1, y1 = pt(cx, cy, 64, a)
        p.add(line(x0, y0, x1, y1, INK, 2))
    p.add(T(cx, cy + 102, "FREE", 13, INK, 700), T(cx - 88, 260, "REPEAT", 9, INK, 700, extra=' transform="rotate(-62 %g 260)"' % (cx - 88)))
    p.rotary("division", cx, cy, 44, 12, lambda a: chrome_knob(a), angles=angs, field_w=120, field_dy=136, accent="#f2f2ea")
    # right panel: tone row on black, delay row on green
    p.add(rect(659, 137, 580, 349, GREEN, rx=8), rect(668, 146, 562, 158, "#141614", rx=4))
    for x, k, l in ((795, "tone", "TONE"), (991, "stereo_width", "WIDTH")):
        p.add(ticks(x, 236, 47, 54, 11, "#c8d0c6", 1.6), circle(x, 182, 2.5, INK))
        p.knob(k, x, 236, 42, l, img=ptr, base=still, lab=-70, bw=150)
    for x, k, l in ((735, "time", "REPEAT RATE"), (855, "feedback", "INTENSITY"), (991, "mix", "ECHO VOLUME")):
        p.add(ticks(x, 400, 47, 54, 11, "#c8d0c6", 1.6))
        p.knob(k, x, 400, 42, l, img=ptr, base=still, lab=-66, bw=118 if k != "mix" else 130)
    p.add(T(930, 452, "STRAIGHT", 9, INK, 700), T(1050, 452, "ECHO", 9, INK, 700))
    p.add(T(1180, 326, "POWER", 13, INK, 700), led(1110, 400, 8, lit=True), T(1196, 372, "ON", 10, INK, 700), T(1196, 432, "OFF", 10, INK, 700),
          circle(1170, 402, 10, "url(#hw-screw)", "#444"), path("M1170 402 L1162 376", stroke="#d8d8d8", sw=6, extra=' stroke-linecap="round"'))
    # jack strip
    p.add(brushed(10, 500, 1260, 112, "#c3c6c7"))
    for x0, x1, s in ((22, 150, "MIC"), (164, 292, "MIC"), (306, 590, "INSTRUMENT"), (610, 740, "FROM P.A."), (860, 1080, "OUT PUT"),
                      (1094, 1258, "FOOT SW")):
        p.add(rect(x0, 512, x1 - x0, 88, "none", rx=4, stroke=GREEN, sw=2), T((x0 + x1) / 2 if s not in ("INSTRUMENT", "FOOT SW") else x0 + 60,
                                                                                 526, s, 11, "#1a1a1a", 700))
        jx = x0 + 52 if s in ("INSTRUMENT", "FOOT SW") else (x0 + x1) / 2
        if s == "OUT PUT":
            jx = x1 - 52
        p.add(circle(jx, 566, 22, "url(#hw-screw)", "#555", 1.5), circle(jx, 566, 13, "#111"),
              circle(jx, 566, 22, "none", {"FROM P.A.": GREEN, "OUT PUT": "#c8261a"}.get(s, "#777"), 2.5))
    p.add(T(1206, 566, "ECHO CANCEL", 11, "#1a1a1a", 700), T(500, 588, "ECHO      NORMAL", 9, "#1a1a1a", 700),
          rect(380, 562, 180, 6, "#888"), rect(522, 552, 12, 24, "#eee", rx=2, stroke="#555"),
          T(905, 532, "H  M  L", 11, "#1a1a1a", 700), rect(880, 556, 50, 20, "#1a1a1a", rx=2))
    p.qrow("division", "tone", "stereo_width", "time", "feedback", "mix")
    return [p]


def _b64(s):
    import base64
    return base64.b64encode(s.encode()).decode()


# ---- Juno-60 chorus (Junologue Chorus) ------------------------------------------------------------------------------
# Reference: Wikimedia Commons "Roland Juno-60.jpg". The Juno-60's black panel between wood end cheeks, red stripe
# and section bars (blue for ARPEGGIO / MEMORY), the CHORUS section's square buttons in cream, yellow and orange with
# their LEDs, black faders with a white line over 0-10 scales, the outlined name lettering at the top right and the
# blue rule under the panel. The plugin is that chorus alone, so its section fills the page: CHORUS I / I+II / II,
# then MIX and BRIGHTNESS faders in a LEVEL section; the rest of the Juno's bar is printed, dimmed, for context.
def juno_fader_cap():
    return svg_doc(34, 52, rect(1, 1, 32, 50, "#151515", rx=3, stroke="#000") + rect(3, 3, 28, 14, "#2a2a2a", rx=2) +
                   rect(1, 24, 32, 4, "#f2f2f2"))


def pjuno(params):
    INK = "#ececec"
    RED, BLUE = "#c8322a", "#2f62b4"
    p = Page("CHORUS", vink="#f2f2f2", lab=dict(size=14, fill=INK, font=SANS, weight=700, sp=0.06), seg_text=False)
    p.add(wood(0, 0, 40, 628), wood(1240, 0, 40, 628), rect(40, 0, 1200, 628, "#141414"), grain(40, 0, 1200, 628))
    p.add(T(70, 52, "JUNOLOGUE", 22, INK, 700, anchor="start", sp=0.08),
          '<text x="1212" y="58" text-anchor="end" dominant-baseline="central" style="font-family:%s;font-weight:700;'
          'letter-spacing:0.02em;font-size:64px;fill:none;stroke:#e8e8e8;stroke-width:2.2" transform="translate(1212 0) scale(1.25 1) '
          'translate(-1212 0)">CHORUS</text>' % SANS)
    # the Juno's section bar, dimmed except CHORUS
    bar = [("ARPEGGIO", BLUE, 130), ("LFO", RED, 80), ("DCO", RED, 150), ("HPF", RED, 50), ("VCF", RED, 130), ("VCA", RED, 60),
           ("ENV", RED, 110), ("CHORUS", RED, 90), ("MEMORY", BLUE, 200)]
    tot = sum(w for _, _, w in bar)
    x = 60
    for n, c, w in bar:
        ww = 1160 * w / tot
        p.add(rect(x, 108, ww - 4, 14, c, extra=' opacity="%g"' % (1 if n == "CHORUS" else 0.45)),
              T(x + ww / 2, 115, n, 9, "#111" if n == "CHORUS" else "#1a1a1a", 700))
        x += ww
    p.add(rect(60, 98, 1160, 4, RED))
    # big CHORUS section
    p.add(rect(80, 160, 560, 34, RED), T(360, 177, "CHORUS", 20, "#111", 700, sp=0.2))
    p.add(rect(80, 194, 560, 300, "none", stroke="#3a3a3a", sw=1.5))
    cols = ["#efe7cf", "#f2c63a", "#ef7a28"]
    xs = [200, 360, 520]
    for x, c, s in zip(xs, cols, ["I", "I + II", "II"]):
        p.add(T(x, 228, s, 22, INK, 700), rect(x - 52, 300, 104, 104, c, rx=6, stroke="#000", sw=2),
              rect(x - 46, 306, 92, 30, "#fff", rx=4, extra=' opacity="0.28"'), rect(x - 52, 396, 104, 8, "#000", rx=3, extra=' opacity="0.25"'))
    off = p.asset("juno_led.svg", svg_doc(158, 220, '<circle cx="79" cy="40" r="9" fill="#3a0a06" stroke="#000"/>'))
    on = p.asset("juno_ledon.svg", svg_doc(158, 220, '<circle cx="79" cy="40" r="20" fill="#ff3a22" opacity="0.3"/>'
                                         '<circle cx="79" cy="40" r="9" fill="#ff3a22" stroke="#5a0d08"/>'
                                         '<rect x="27" y="70" width="104" height="104" rx="6" fill="#fff" opacity="0.18"/>'))
    p.switch("mode", 360, 340, 3, vertical=False, sw=158, sh=220, img=off, img_on=on)
    # LEVEL section: two Juno faders
    p.add(rect(700, 160, 440, 34, RED), T(920, 177, "LEVEL", 20, "#111", 700, sp=0.2), rect(700, 194, 440, 300, "none", stroke="#3a3a3a", sw=1.5))
    tr = p.asset("juno_tr.svg", svg_doc(34, 230, rect(13, 0, 8, 230, "#050505", rx=3)))
    cap = p.asset("juno_cap.svg", juno_fader_cap())
    for x, k, l in ((840, "mix", "MIX"), (1000, "brightness", "BRIGHTNESS")):
        for i in range(11):
            yy = 236 + 202 * i / 10
            p.add(line(x - 34, yy, x - 22, yy, "#bdbdbd", 1.2), line(x + 22, yy, x + 34, yy, "#bdbdbd", 1.2))
        p.add(T(x - 48, 236, "10", 10, INK, 700), T(x - 46, 438, "0", 10, INK, 700))
        p.slider(k, x, 337, 34, 230, l, img=cap, base=tr, lab=-122, bw=150)
    p.add(rect(60, 530, 1160, 6, BLUE), rect(60, 540, 1160, 3, RED),
          T(1210, 566, "STEREO CHORUS ENSEMBLE", 16, INK, 700, anchor="end", sp=0.14))
    for x in (60, 1220):
        p.add(hexscrew(x, 590, 6))
    p.qrow("mode", "mix", "brightness")
    return [p]


# ---- SSL 4000 E/G channel EQ (4K EQ) --------------------------------------------------------------------------------
# Reference: the SL4000 E/G channel module as printed (no photo of a single strip on Commons; layout and colours as
# the console has them): FILTERS (HP / LP with their IN buttons), HF (red: GAIN, kHz, BELL), HMF (green: GAIN, kHz,
# Q), LMF (blue: GAIN, kHz, Q), LF (GAIN, Hz, BELL; brown knob on the early "E", black on the "242"/G: the plugin's
# BROWN/BLACK switch swaps it), dark grey knob bodies with coloured caps, white pointer lines and printed scales, the
# console's grey legend rail. The strip is vertical on the console; here it is turned on its side, so the bands run
# left to right in the strip's top-to-bottom order, gains on the top row, frequencies and Q under them.
def ssl_knob(cap):
    return knob_img(body="#33363a", edge="#0c0d0e", knurl="#3f4347", knurl_n=24, cap=cap, cap_r=0.62, cap_edge="#111",
                    line_c="#f4f4f2", line=(0.05, 0.9), line_w=6, shine=0.2, rr=0.9)


def ssl_button(on=False, lit="#f4f1e6"):
    face = lit if on else "#c9c9c4"
    glow = '<rect x="2" y="2" width="44" height="34" rx="3" fill="%s" opacity="0.35"/>' % lit if on else ""
    return svg_doc(48, 38, glow + rect(4, 4, 40, 30, face, rx=3, stroke="#111", sw=1.5) +
                   rect(6, 6, 36, 9, "#fff", rx=2, extra=' opacity="0.35"'))


def p4k(params):
    INK = "#f2f2ef"
    p = Page("EQ", vink="#f6f2e4", lab=dict(size=12, fill=INK, font=SANS, weight=700, sp=0.06))
    caps = {"red": "#d0342c", "green": "#2e9a56", "blue": "#2f6fc9", "black": "#1a1a1a", "brown": "#7a4a26", "grey": "#d8d8d2",
            "io": "#9a9da0"}
    for n, c in caps.items():
        p.asset("ssl_%s.svg" % n, ssl_knob(c))
    boff = p.asset("ssl_btn.svg", ssl_button())
    bon = p.asset("ssl_btnon.svg", ssl_button(True))
    bred = p.asset("ssl_btnred.svg", ssl_button(True, "#ff5a40"))
    p.add(rect(0, 0, 1280, 628, "#2b2d30"), rect(8, 8, 1264, 612, "#45494d", rx=4), grain(8, 8, 1264, 612))
    # legend rail
    p.add(brushed(8, 8, 1264, 44, "#cfd1d1"), rect(290, 16, 700, 28, "none", rx=3, stroke="#2a2a2a", sw=1.5),
          T(640, 31, "4K EQ  .  CHANNEL EQUALISER  .  E / G SERIES", 19, "#1a1a1a", 400, font=SANS, sp=0.12))
    secs = [("FILTERS", 8, 228, "#d8d8d2"), ("HF", 228, 428, "#d0342c"), ("HMF", 428, 668, "#2e9a56"), ("LMF", 668, 908, "#2f6fc9"),
            ("LF", 908, 1088, "#cfcfcf"), ("CHANNEL", 1088, 1272, "#d8d8d2")]
    for n, x0, x1, c in secs:
        p.add(line(x1, 60, x1, 600, "#2a2c2f", 2.5), line(x1 + 2, 60, x1 + 2, 600, "#5a5e62", 1),
              T((x0 + x1) / 2, 76, n, 20, c, 700, sp=0.12))

    def kn(key, x, y, r, cap, label, scale=None, when=None):
        p.add(ticks(x, y, r + 6, r + 12, 11, "#e8e8e4", 1.4))
        if scale:
            p.add(numbers(x, y, r + 23, scale, 9, "#e8e8e4"))
        p.knob(key, x, y, r, label, img="hw_ssl_%s.svg" % cap, lab=-(r + 44) if scale and scale[5] else -(r + 34), when=when)

    def btn(key, x, y, label, red=False):
        p.toggle(key, x, y, label, img=boff, img_on=bred if red else bon, w=48, h=38)
        p.add(T(x, y + 30, label, 11, INK, 700))

    g = ["-15", "", "", "", "", "0", "", "", "", "", "+15"]
    # FILTERS
    kn("hpf_freq", 88, 190, 30, "grey", "HP Hz", ["16", "", "", "", "", "", "", "", "", "", "350"])
    btn("hpf_enabled", 178, 190, "IN")
    kn("lpf_freq", 88, 400, 30, "grey", "LP kHz", ["3", "", "", "", "", "", "", "", "", "", "15"])
    btn("lpf_enabled", 178, 400, "IN")
    # HF
    kn("hf_gain", 328, 190, 38, "red", "GAIN", g)
    kn("hf_freq", 290, 400, 28, "red", "kHz", ["1.5", "", "", "", "", "", "", "", "", "", "16"])
    btn("hf_bell", 384, 400, "BELL")
    # HMF / LMF
    for x0, b, c, fr in ((428, "hm", "green", ["0.6", "", "", "", "", "", "", "", "", "", "7"]),
                         (668, "lm", "blue", ["0.2", "", "", "", "", "", "", "", "", "", "2.5"])):
        kn(b + "_gain", x0 + 120, 190, 38, c, "GAIN", g)
        kn(b + "_freq", x0 + 66, 400, 28, c, "kHz", fr)
        kn(b + "_q", x0 + 174, 400, 28, c, "Q", ["0.5", "", "", "", "", "", "", "", "", "", "3"])
    # LF: brown on the E, black on the G
    p.add(ticks(998, 190, 44, 50, 11, "#e8e8e4", 1.4), numbers(998, 190, 61, g, 9, "#e8e8e4"))
    p.knob("lf_gain", 998, 190, 38, "GAIN", img="hw_ssl_brown.svg", lab=-82, when="eq_type:0")
    p.knob("lf_gain", 998, 190, 38, "GAIN", img="hw_ssl_black.svg", when="eq_type:1")
    kn("lf_freq", 960, 400, 28, "black", "Hz", ["30", "", "", "", "", "", "", "", "", "", "450"])
    btn("lf_bell", 1046, 400, "BELL")
    # CHANNEL: input / output trims, E/G, EQ bypass, meters
    kn("input_gain", 1140, 160, 26, "io", "INPUT", ["-12", "", "", "", "", "0", "", "", "", "", "+12"])
    kn("output_gain", 1226, 160, 26, "io", "OUTPUT", ["-12", "", "", "", "", "0", "", "", "", "", "+12"])
    p.add(T(1180, 262, "KNOB", 11, INK, 700))
    p.switch("eq_type", 1180, 298, 2, vertical=False, sw=72, sh=34)
    btn("bypass", 1140, 380, "BYPASS", red=True)
    btn("auto_gain", 1226, 380, "AUTO GAIN")
    p.add(T(1180, 452, "OVERSAMPLE", 11, INK, 700))
    p.switch("oversampling", 1180, 482, 3, vertical=False, sw=52, sh=30)
    # meters along the bottom: input L/R, output L/R, clip
    p.add(rect(20, 486, 1060, 110, "#2f3235", rx=4, stroke="#1a1b1c"), T(40, 500, "METERS", 11, INK, 700, anchor="start"))
    for i, (k, l) in enumerate((("in_peak_l", "IN L"), ("in_peak_r", "IN R"), ("out_peak_l", "OUT L"), ("out_peak_r", "OUT R"),
                                ("clip", "CLIP"))):
        p.readout(k, 130 + i * 205, 552, 170, 40, l)
    p.qrow("hpf_freq", "hf_gain", "hm_gain", "lm_gain", "lf_gain", "input_gain", "output_gain")
    p.qrow("lpf_freq", "hf_freq", "hm_freq", "hm_q", "lm_freq", "lm_q", "lf_freq")
    return [p]


# ---- Alesis Midiverb (Midiverb) -------------------------------------------------------------------------------------
# Reference: Wikimedia Commons "Alesis MIDIVerb.jpg". The black unit: blue stripes round the italic name, the program
# chart printed in columns (number, decay, size, tone), and the front strip with the red program display. Here the
# chart is the plugin's own program list for the selected UNIT (Midiverb / Midifex / Midiverb II: a picture per unit,
# so it changes with the switch), and the front strip has INPUT, MIX, OUTPUT, the program display and knob, and the
# UNIT selector. The plugin's extra controls are a second page in the same finish (an expander strip).
def _names(unit):
    import os
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modules", "schwung-midiverb", "src", "dsp",
                     "names-%s.h" % unit)
    try:
        return [l.strip().strip(",").strip('"') for l in open(f) if l.strip().startswith('"')]
    except OSError:
        return []


def mv_chart(names, w=1240, h=318):
    cols = 3 if len(names) <= 66 else 4
    per = -(-len(names) // cols)
    cw = w / cols
    rh = (h - 8) / per
    o = [rect(0, 0, w, h, "#0d0d0d")]
    for c in range(cols):
        x0 = c * cw
        o.append(rect(x0 + 4, 4, cw - 8, h - 8, "none", stroke="#cfcfcf", sw=1))
        o.append(line(x0 + 44, 4, x0 + 44, h - 4, "#cfcfcf", 0.8))
        for r in range(per):
            i = c * per + r
            if i >= len(names):
                break
            y = 4 + rh * (r + 0.5)
            if r:
                o.append(line(x0 + 4, 4 + rh * r, x0 + cw - 4, 4 + rh * r, "#5a5a5a", 0.6))
            o.append(T(x0 + 24, y, str(i), min(11, rh * 0.75), "#e8e8e8", 700))
            o.append(T(x0 + 54, y, names[i].upper(), min(11, rh * 0.75), "#e8e8e8", 700, anchor="start", sp=0.06))
    return svg_doc(w, h, "".join(o))


def pmidiverb(params):
    INK = "#e8e8e8"
    BLUE = "#3a8fd8"
    p = Page("MIDIVERB", vink="#ff3a22", lab=dict(size=12, fill=INK, font=SANS, weight=700, sp=0.08))
    p.add(rect(0, 0, 1280, 628, "#0a0a0a"), rect(6, 4, 1268, 620, "#141414", rx=8), grain(6, 4, 1268, 620))

    def stripes(p, y):
        p.add(rect(6, y, 1268, 30, BLUE), rect(6, y + 36, 1268, 4, BLUE), rect(6, y + 46, 1268, 2, BLUE))

    stripes(p, 10)
    p.add(T(40, 25, "MIDIVERB", 34, "#fff", 700, anchor="start", italic=True, font=SANS, sp=0.02, stretch=1.15,
            extra=' stroke="#0a0a0a" stroke-width="1"'),
          T(1240, 25, "DIGITAL REVERB", 18, "#fff", 700, anchor="end", italic=True, sp=0.1))
    files = [p.asset("mv_chart_%d.svg" % i, mv_chart(_names(u))) for i, u in enumerate(("midiverb", "midifex", "midiverb2"))]
    p.picture("unit", 20, 66, 1240, 318, files)
    # front strip
    p.add(rect(14, 400, 1252, 216, "#1b1b1b", rx=6, stroke="#2c2c2c"), rect(14, 400, 1252, 6, BLUE))

    def kn(k, x, l):
        p.add(ticks(x, 500, 36, 42, 11, "#bdbdbd", 1.5))
        p.knob(k, x, 500, 30, l, img="hw_mv_k.svg", lab=-56, bw=140)

    p.asset("mv_k.svg", knob_img(body="#1a1a1a", edge="#000", knurl="#2b2b2b", knurl_n=30, cap="metal", cap_r=0.55,
                                 line_c="#f4f4f4", line=(0.6, 0.95), line_w=6, rr=0.9))
    kn("input_gain", 100, "INPUT")
    kn("mix", 250, "MIX")
    kn("output_gain", 400, "OUTPUT")
    p.add(led(100, 590, 4, lit=False), T(116, 590, "CLIP", 10, INK, 700, anchor="start"))
    # program display + knob
    p.add(rect(520, 440, 240, 110, "#0c0c0c", rx=4, stroke="#2c2c2c"), rect(536, 456, 208, 78, "#2a0604", rx=3),
          T(640, 432, "PROGRAM", 12, INK, 700, sp=0.14))
    p.readout("program", 640, 495, 200, 70, "")
    p.add(T(820, 456, "SELECT", 11, INK, 700), ticks(820, 500, 36, 42, 11, "#bdbdbd", 1.5))
    p.knob("program", 820, 500, 30, "PROGRAM", img="hw_mv_k.svg", vs=16, bw=110, dup=True)
    p.add(T(1040, 432, "UNIT", 12, INK, 700, sp=0.14))
    p.switch("unit", 1040, 500, 3, vertical=True, sw=220, sh=34)
    p.qrow("input_gain", "mix", "output_gain", "program", "unit")
    pages = [p]

    p = Page("EXPANDER", vink="#ff3a22", lab=dict(size=12, fill=INK, font=SANS, weight=700, sp=0.08))
    p.asset("mv_k.svg", knob_img(body="#1a1a1a", edge="#000", knurl="#2b2b2b", knurl_n=30, cap="metal", cap_r=0.55,
                                 line_c="#f4f4f4", line=(0.6, 0.95), line_w=6, rr=0.9))
    p.add(rect(0, 0, 1280, 628, "#0a0a0a"), rect(6, 4, 1268, 620, "#141414", rx=8), grain(6, 4, 1268, 620))
    stripes(p, 10)
    p.add(T(40, 25, "MIDIVERB", 34, "#fff", 700, anchor="start", italic=True, font=SANS, sp=0.02, stretch=1.15),
          T(1240, 25, "EXPANDER", 18, "#fff", 700, anchor="end", italic=True, sp=0.1))
    groups = [("REVERB", [("feedback", "FEEDBACK"), ("predelay_ms", "PRE-DELAY"), ("damping", "DAMPING")]),
              ("TONE", [("low_cut_hz", "LOW CUT"), ("high_cut_hz", "HIGH CUT"), ("tilt", "TILT")]),
              ("SPACE", [("width", "WIDTH"), ("lfo_rate", "LFO RATE"), ("lfo_depth", "LFO DEPTH")])]
    x = 30
    keys = []
    for gname, ks in groups:
        w = 400
        p.add(rect(x, 100, w - 20, 300, "#1b1b1b", rx=6, stroke="#2c2c2c"), rect(x, 100, w - 20, 6, BLUE),
              T(x + (w - 20) / 2, 132, gname, 16, INK, 700, sp=0.2))
        for i, (k, l) in enumerate(ks):
            cx = x + 70 + i * 120
            p.add(ticks(cx, 260, 40, 47, 11, "#bdbdbd", 1.5))
            p.knob(k, cx, 260, 34, l, img="hw_mv_k.svg", lab=-62, bw=116)
            keys.append(k)
        x += w + 10
    p.add(rect(6, 560, 1268, 4, BLUE), rect(6, 570, 1268, 2, BLUE))
    p.qrow(*keys)
    pages.append(p)
    return pages
