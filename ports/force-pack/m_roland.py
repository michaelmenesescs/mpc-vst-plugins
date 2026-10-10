"""Hardware pages for the Roland-style machines (hwpanel.Page). Positions are taken from front-panel photos, scaled
to the 1280 x 628 plugin area; each function says which photo. Names on the panels are the plugins' own."""
from hwpanel import (Page, T, rect, line, circle, path, ticks, dots, numbers, screw, led, brushed, grain, wood,
                     knob_img, svg_doc, pt, SANS, NARROW, ROUND)


# ---- shared bits -------------------------------------------------------------------------------------------------
METAL = ('<defs><linearGradient id="mb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fafafa"/>'
         '<stop offset="0.5" stop-color="#c4c6c8"/><stop offset="1" stop-color="#8a8d8f"/></linearGradient></defs>')


def tri(x, y, s=5, fill="#111"):
    return path("M%g %g L%g %g L%g %g Z" % (x, y - s, x - s, y + s * 0.8, x + s, y + s * 0.8), fill)


def silver_knob_base(rr=0.92, knurl_n=40):
    """The 303's knobs: an aluminium flat top inside a knurled skirt (still), lit from the top left."""
    R = 48 * rr
    return svg_doc(96, 96, (
        '<defs><radialGradient id="t" cx="0.42" cy="0.38" r="0.7"><stop offset="0" stop-color="#ffffff"/>'
        '<stop offset="0.55" stop-color="#d9dbdc"/><stop offset="1" stop-color="#9da0a2"/></radialGradient>'
        '<linearGradient id="s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f4f4"/>'
        '<stop offset="0.5" stop-color="#a9acae"/><stop offset="1" stop-color="#5d6062"/></linearGradient></defs>'
        '<circle cx="48" cy="48" r="%g" fill="#e9ebeb" stroke="#1a1a1a" stroke-width="3.2"/>'
        '<circle cx="48" cy="50" r="%g" fill="#000" opacity="0.35"/>'
        '<circle cx="48" cy="48" r="%g" fill="url(#s)" stroke="#4a4c4e" stroke-width="1.2"/>'
        '<circle cx="48" cy="48" r="%g" fill="none" stroke="#6d7072" stroke-width="7" stroke-dasharray="2.2 2.2"/>'
        '<circle cx="48" cy="48" r="%g" fill="url(#t)" stroke="#8a8d8f" stroke-width="1"/>'
        % (R, R * 0.86, R * 0.86, R * 0.86 - 5, R * 0.6)))


def pointer_img(rr=0.92, c="#2b2b2b", w=4.5, r0=0.05, r1=0.62, notch=False):
    """The pointer that turns: a line, or (notch) the 303's cut in the knob's top: a dark slot with a lit edge."""
    R = 48 * rr
    if notch:
        return svg_doc(96, 96, '<line x1="48" y1="%g" x2="48" y2="%g" stroke="#55585a" stroke-width="%g" stroke-linecap="butt"/>'
                       '<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#ffffff" stroke-width="1.6"/>' % (
                           48 - R * 0.22, 48 - R * 0.78, w, 48 + w / 2, 48 - R * 0.22, 48 + w / 2, 48 - R * 0.78))
    return svg_doc(96, 96, '<line x1="48" y1="%g" x2="48" y2="%g" stroke="%s" stroke-width="%g" stroke-linecap="round"/>' % (
        48 - R * r0, 48 - R * r1, c, w))


# ---- TB-303 -------------------------------------------------------------------------------------------------------
# Reference: Wikimedia Commons "Roland TB-303 Panel.jpg" (1656 x 814, nearly the plugin area's shape: x 0.773).
# Top strip: rear-jack legends with the WAVEFORM switch, then TUNING, CUT OFF FREQ, RESONANCE, ENV MOD, DECAY,
# ACCENT, and the big lettering at the right. Middle strip: where TEMPO / PATT.GROUP / MODE sit, the Devil Fish
# knobs and the drive stage (a Devil Fish puts its extra pots on this panel too), the "Computer Controlled"
# lettering and VOLUME at its place. Lower panel: the keyboard section, with DEVIL MOD in the PITCH MODE block and
# the drive model on the TRANSPOSE DOWN / UP buttons.
def p303(_):
    p = Page("303", vink="#222222", lab=dict(size=13, fill="#1a1a1a", font=SANS, weight=700, sp=0.01), seg_text=False)
    kb = p.asset("k303.svg", silver_knob_base())
    kp = p.asset("k303p.svg", pointer_img(notch=True, w=5))
    # body: aluminium, a darker rim, the groove under the top strip
    p.add(rect(0, 0, 1280, 628, "#8d9092"),
          brushed(6, 4, 1268, 620, "#c8cacb"),
          rect(6, 4, 1268, 620, "url(#hw-vshade)", rx=10),
          rect(6.5, 4.5, 1267, 619, "none", rx=10, stroke="#6f7274", sw=1.5),
          line(12, 124, 1268, 124, "#7b7e80", 2), line(12, 126.5, 1268, 126.5, "#eef0f0", 1.5))
    # top strip: jack legends
    for x, s in ((70, "MIX IN"), (160, "WAVEFORM"), (259, "SYNC IN"), (931, "CV"), (985, "GATE"), (1051, "HEADPHONE"),
                 (1123, "OUTPUT"), (1196, "DC 9V")):
        p.add(tri(x, 20, 4.5), T(x, 36, s, 11, "#1a1a1a", 700, sp=0.02))
    p.add(line(327, 24, 327, 116, "#2a2a2a", 1.6), line(910, 24, 910, 116, "#2a2a2a", 1.6))
    # the waveform switch, on the rear edge under its legend: a slide switch (saw | square)
    slot = p.asset("sw303.svg", svg_doc(40, 22, rect(0, 4, 40, 14, "#1d1d1d", rx=2) + rect(0, 4, 40, 3, "#000", extra=' opacity="0.5"')))
    nub = p.asset("sw303on.svg", svg_doc(40, 22, rect(0, 4, 40, 14, "#1d1d1d", rx=2) +
                                         rect(6, 1, 28, 20, "#d8dadb", rx=2, stroke="#55585a", sw=1) +
                                         "".join(line(12 + i * 4, 4, 12 + i * 4, 18, "#8d9092", 1.2) for i in range(5))))
    p.switch("waveform", 160, 62, 2, vertical=False, sw=40, sh=22, img=slot, img_on=nub)
    p.add(path("M84 70 L96 54 L96 70 L108 54 L108 70", stroke="#1a1a1a", sw=2.2),          # saw
          path("M212 70 L212 55 L224 55 L224 70 L236 70 L236 55", stroke="#1a1a1a", sw=2.2))  # square
    p.add(T(102, 92, "SAW", 10, "#1a1a1a", 700), T(224, 92, "SQUARE", 10, "#1a1a1a", 700))
    # the six knobs
    row = [("tuning", "TUNING"), ("cutoff", "CUT OFF FREQ"), ("resonance", "RESONANCE"), ("env_mod", "ENV MOD"),
           ("decay", "DECAY"), ("accent", "ACCENT")]
    for i, (k, lab) in enumerate(row):
        x = 381 + i * 94.5
        p.add(ticks(x, 80, 36, 42, 11, "#1a1a1a", 1.8, major=None), rect(x - 3, 40, 6, 6, "#1a1a1a"))
        p.knob(k, x, 80, 31, lab, img=kp, base=kb, lab=-51, font=NARROW, size=13)
    p.add(T(1078, 90, "303", 60, "#1b1b1b", 700, font=ROUND, sp=0.04))
    # middle strip: Devil Fish pots, drive, lettering, VOLUME
    def block(x, y, s, w):
        p.add(rect(x - w / 2, y - 10, w, 20, "#1c1c1c", rx=1), T(x, y, s, 12, "#eceeee", 700, sp=0.06))
    block(195, 150, "DEVIL FISH", 120)
    p.add(line(40, 150, 135, 150, "#1a1a1a", 1.4), line(255, 150, 440, 150, "#1a1a1a", 1.4))
    dfk = [("normal_decay", "NORM DECAY"), ("accent_decay", "ACC DECAY"), ("feedback_hpf", "FDBK HPF"),
           ("soft_attack", "SOFT ATTACK"), ("slide_time", "SLIDE TIME")]
    for i, (k, lab) in enumerate(dfk):
        x = 58 + i * 92
        p.add(ticks(x, 236, 33, 39, 11, "#1a1a1a", 1.6))
        p.knob(k, x, 236, 27, lab, img=kp, base=kb, lab=-50)
    block(625, 150, "DRIVE", 80)
    p.add(line(520, 150, 580, 150, "#1a1a1a", 1.4), line(670, 150, 730, 150, "#1a1a1a", 1.4))
    for i, (k, lab) in enumerate((("drive", "DRIVE"), ("drive_mix", "MIX"), ("tanh_shaper_drive", "SHAPER"))):
        x = 535 + i * 90
        p.add(ticks(x, 236, 33, 39, 11, "#1a1a1a", 1.6), T(x - 26, 274, "MIN", 9, "#1a1a1a", 700), T(x + 26, 274, "MAX", 9, "#1a1a1a", 700))
        p.knob(k, x, 236, 27, lab, img=kp, base=kb, lab=-50)
    p.add(T(1000, 210, "Devil Fish", 40, "#1b1b1b", 400, font=SANS, anchor="end", sp=0.0, stretch=0.92),
          line(762, 232, 1000, 232, "#1b1b1b", 1.6),
          T(880, 250, "Computer Controlled", 27, "#1b1b1b", 400, font=SANS, sp=0.0))
    p.add(ticks(1109, 230, 50, 57, 11, "#1a1a1a", 2), T(1040, 278, "OFF /", 10, "#1a1a1a", 700),
          T(1176, 278, "\\ MAX", 10, "#1a1a1a", 700), T(1109, 160, "", 1, "#000"))
    p.knob("volume", 1109, 230, 44, "VOLUME", img=p.asset("k303pv.svg", pointer_img(notch=True, w=5)), base=kb, lab=-82, bw=96)
    # lower panel: the keyboard section (artwork) round DEVIL MOD and the drive-model buttons
    p.add(rect(31, 316, 1218, 266, "#d3d5d6", rx=3, stroke="#7e8183", sw=2), grain(31, 316, 1218, 266),
          rect(36, 321, 1208, 256, "none", rx=2, stroke="#f4f5f5", sw=1))
    # left column (BAR RESET / RUN-STOP as printed), PITCH MODE block = DEVIL MOD
    p.add(rect(38, 326, 120, 92, "none", stroke="#555", sw=1), rect(38, 422, 120, 150, "none", stroke="#555", sw=1),
          rect(42, 334, 30, 16, "none", stroke="#1a1a1a", sw=1), T(57, 342, "D.C.", 10, "#1a1a1a", 700, italic=True, font="serif"),
          rect(76, 334, 76, 16, "none", stroke="#1a1a1a", sw=1), T(114, 342, "BAR RESET", 10, "#1a1a1a", 400),
          T(98, 366, "PATTERN CLEAR", 10, "#1a1a1a", 400),
          rect(70, 384, 56, 24, "url(#hw-screw)", rx=2, stroke="#555"),
          T(98, 440, "RUN  ●  BATTERY", 9, "#1a1a1a", 700), rect(58, 462, 80, 40, "url(#hw-screw)", rx=2, stroke="#555"),
          T(98, 528, "RUN/STOP", 11, "#1a1a1a", 700))
    p.add(rect(162, 326, 120, 92, "#1c1c1c"), T(222, 340, "DEVIL MOD", 13, "#eeeeee", 700, sp=0.02))
    btn = svg_doc(50, 64, METAL + rect(5, 30, 40, 26, "url(#mb)", rx=2, stroke="#55585a", sw=1.2) + rect(7, 32, 36, 6, "#fff", rx=2, extra=' opacity="0.6"'))
    off = p.asset("btn303.svg", svg_doc(50, 64, '<circle cx="25" cy="12" r="6" fill="#4a0d08" stroke="#160403"/>' + btn[btn.index(">") + 1:-6]))
    on = p.asset("btn303on.svg", svg_doc(50, 64, '<circle cx="25" cy="12" r="10" fill="#ff3a22" opacity="0.3"/>'
                                         '<circle cx="25" cy="12" r="6" fill="#ff3a22" stroke="#5a0d08"/>' + btn[btn.index(">") + 1:-6]))
    p.toggle("devil_mod_switch", 222, 384, "DEVIL MOD", img=off, img_on=on, w=50, h=64)
    p.add(T(253, 458, "NORMAL", 9, "#1a1a1a", 400), T(253, 468, "MODE", 9, "#1a1a1a", 400),
          path("M232 478 V520", stroke="#1a1a1a", sw=1.2))
    p.add(rect(162, 422, 120, 150, "none", stroke="#555", sw=1), T(205, 438, "FUNCTION", 12, "#1a1a1a", 400),
          led(262, 438, 4), rect(180, 462, 40, 40, "url(#hw-screw)", rx=2, stroke="#555"), rect(181, 518, 30, 16, "#1c1c1c"),
          T(196, 526, "BAR", 10, "#eee", 700))
    # the keyboard: white keys, black keys with LEDs, the PATTERN / SELECTOR bars
    kx = [319, 388, 457, 526, 594, 663, 732, 801]
    p.add(rect(282, 336, 568, 186, "#f3f3f1"), rect(282, 326, 568, 14, "#1c1c1c"))
    for i, n in enumerate("C C# D D# E F F# G G# A A# B C".split()):
        x = 300 + i * 41.5
        p.add(T(x + 4, 333, n, 10, "#eee", 700))
    for x in kx:
        p.add(line(x + 34.5, 340, x + 34.5, 522, "#b8b9b9", 1), led(x, 438, 4.5),
              rect(x - 13, 462, 26, 40, "url(#hw-screw)", rx=2, stroke="#555"))
    for x in (355, 423, 561, 630, 699):
        p.add(rect(x - 26, 340, 52, 100, "#1c1c1c"), led(x, 352, 4.5), rect(x - 12, 368, 24, 40, "url(#hw-screw)", rx=2, stroke="#555"))
    p.add(T(355, 424, "DEL", 10, "#eee", 700), T(423, 424, "INS", 10, "#eee", 700))
    p.add(rect(232, 520, 618, 22, "#1c1c1c"), T(266, 531, "PATTERN", 11, "#e8452a", 700))
    for i, x in enumerate(kx):
        p.add(T(x, 531, str(i + 1), 14, "#e8452a", 700))
    p.add(T(262, 556, "SELECTOR", 13, "#1a1a1a", 400))
    for i, x in enumerate(kx):
        p.add(rect(x - 9, 548, 18, 16, "#1c1c1c"), T(x, 556, str(i + 1), 11, "#eee", 700))
    for x, s_ in ((353, "DEL"), (423, "INS")):
        p.add(rect(x - 15, 543, 30, 14, "#1c1c1c", rx=2), T(x, 550, s_, 9, "#eee", 700))
    # TIME MODE area as printed (time symbols, ACCENT / SLIDE, PATT. SECTION); TRANSPOSE DOWN / UP = the drive model
    BK = "#1c1c1c"
    p.add(rect(850, 326, 264, 246, "none", stroke="#555", sw=1), T(978, 342, "TIME MODE", 13, "#1a1a1a", 400), led(978, 358, 4.5),
          line(905, 370, 905, 396, "#1a1a1a", 1), line(977, 370, 977, 396, "#1a1a1a", 1), line(1045, 370, 1045, 396, "#1a1a1a", 1),
          circle(862, 384, 3.5, "#1a1a1a"), note(876, 384, "8", "#1a1a1a", 0.9), circle(930, 384, 3.5, "none", "#1a1a1a", 1.2),
          note(944, 384, "8", "#1a1a1a", 0.9), line(998, 384, 1008, 384, "#1a1a1a", 2),
          circle(1017, 378, 2.6, "#1a1a1a"), path("M1018 380 L1026 377 L1019 393", stroke="#1a1a1a", sw=1.6),
          rect(1054, 372, 48, 20, "url(#hw-screw)", rx=2, stroke="#555"),
          rect(850, 396, 126, 26, BK), T(908, 402, "DRIVE MODEL", 8, "#eee", 700), line(856, 408, 970, 408, "#eee", 0.8),
          T(874, 415, "SOFT", 10, "#eee", 700),
          T(942, 415, "RAT", 10, "#eee", 700), line(908, 409, 908, 421, "#eee", 1), rect(979, 400, 135, 22, BK),
          T(1013, 412, "ACCENT", 11, "#eee", 700), T(1082, 412, "SLIDE", 11, "#eee", 700), line(1047, 404, 1047, 420, "#eee", 1),
          led(1013, 438, 4.5), led(1082, 438, 4.5),
          rect(1001, 462, 26, 40, "url(#hw-screw)", rx=2, stroke="#555"), rect(1069, 462, 26, 40, "url(#hw-screw)", rx=2, stroke="#555"),
          T(874, 528, "STEP", 11, "#1a1a1a", 400))
    for k in range(3):
        p.add(note(930 + k * 9, 518, "8", "#1a1a1a", 0.8))
    p.add(path("M930 530 v3 h22 v-3", stroke="#1a1a1a", sw=1), T(941, 538, "3", 8, "#1a1a1a", 700),
          rect(979, 512, 135, 30, BK), T(1013, 520, "A", 10, "#e8452a", 700), T(1082, 520, "B", 10, "#e8452a", 700),
          T(1047, 534, "PATT. SECTION", 10, "#e8452a", 700))
    for x, s_, c in ((874, "9", "#eee"), (942, "0", "#eee"), (1013, "100", "#ff7a4a"), (1082, "200", "#ff7a4a")):
        p.add(rect(x - 15, 548, 30, 16, BK), T(x, 556, s_, 11, c, 700))
    segoff = p.asset("seg303.svg", svg_doc(66, 80, '<circle cx="33" cy="16" r="5" fill="#4a0d08" stroke="#160403"/>' +
                                           METAL + rect(20, 40, 26, 40, "url(#mb)", rx=2, stroke="#55585a", sw=1.2)))
    segon = p.asset("seg303on.svg", svg_doc(66, 80, '<circle cx="33" cy="16" r="9" fill="#ff3a22" opacity="0.3"/>'
                                          '<circle cx="33" cy="16" r="5" fill="#ff3a22" stroke="#5a0d08"/>' +
                                          METAL + rect(20, 40, 26, 40, "url(#mb)", rx=2, stroke="#55585a", sw=1.2)))
    p.switch("drive_model", 908, 462, 2, vertical=False, sw=66, sh=80, img=segoff, img_on=segon)
    # right column: BACK under the segno, WRITE/NEXT under D.S.
    p.add(rect(1121, 326, 116, 92, "none", stroke="#555", sw=1), rect(1162, 334, 34, 16, "none", stroke="#1a1a1a", sw=1),
          T(1179, 342, "\u00a7", 11, "#1a1a1a", 700), T(1179, 362, "BACK", 11, "#1a1a1a", 400),
          rect(1159, 380, 40, 22, "url(#hw-screw)", rx=2, stroke="#555"),
          rect(1121, 422, 116, 150, "none", stroke="#555", sw=1), rect(1162, 430, 34, 16, "none", stroke="#1a1a1a", sw=1),
          T(1179, 438, "D.S.", 10, "#1a1a1a", 700, italic=True, font="serif"),
          rect(1140, 456, 78, 48, "url(#hw-screw)", rx=2, stroke="#555"), rect(1132, 518, 94, 18, "none", stroke="#1a1a1a", sw=1),
          T(1179, 527, "WRITE/NEXT", 11, "#1a1a1a", 400), T(1179, 552, "TAP", 11, "#1a1a1a", 400))
    for x, y in ((20, 16), (1260, 16), (20, 612), (1260, 612)):
        p.add(screw(x, y, 5))
    p.qrow("waveform", "tuning", "cutoff", "resonance", "env_mod", "decay", "accent", "volume")
    p.qrow("normal_decay", "accent_decay", "feedback_hpf", "soft_attack", "slide_time", "drive", "drive_mix", "tanh_shaper_drive")
    return [p]


# ---- TR-808 -------------------------------------------------------------------------------------------------------
# Reference: Wikimedia Commons "Roland TR-808 (large).jpg". The instrument section is twelve columns, left to right
# ACCENT, BASS DRUM, SNARE DRUM, LOW TOM / LOW CONGA, MID TOM / MID CONGA, HI TOM / HI CONGA, RIM SHOT / CLAVES,
# HAND CLAP / MARACAS, COW BELL, CYMBAL, OPEN HIHAT, CLSD HIHAT: LEVEL knobs (orange caps) on top, TONE / TUNING
# and DECAY / SNAPPY (white caps) under them where the 808 has them, cream name plates (the switched voice's plate
# above the instrument-select switch), "Rhythm Composer" lettering, MASTER VOLUME, and the grey step section with
# the red / orange / yellow / white keys. The rhythm-programming block on the 808's left is left out (the plugin
# plays from MPC's pads), so the twelve columns take the full width. Knobs the 808 doesn't have go on the next
# pages in the same columns, so each voice stays where it is on the machine.
C808 = ["ACcent", "BassDrum", "SnareDrum", "LowTom", "MidTom", "HiTom", "RimShot", "handClaP", "CowBell", "CYmbal",
        "OpenHihat", "Cls'dHihat"]
ALT808 = {3: "LowConga", 4: "MidConga", 5: "HiConga", 6: "CLaves", 7: "MAracas"}
SHORT808 = {3: "LO CONGA", 4: "MID CONGA", 5: "HI CONGA", 6: "CLAVES", 7: "MARACAS"}
# the photo's own columns (x 1280 / 1920): dividers from x 335 every 70.1 px; rows LEVEL / TONE / DECAY
X808 = [370 + 70.1 * i for i in range(12)]
CW808 = 70.1


def y808(y):
    """Photo y (1280-wide scale) -> panel y: the instrument section is stretched 1.11x so MPC's value line fits under
    each knob; the step section keeps its size and moves down to match."""
    if y <= 85:
        return y
    if y <= 396:
        return 85 + (y - 85) * 1.109
    return y + 36


R808 = [y808(113), y808(180), y808(245)]


def plate_text(x, y, s, big=15, small=10.5, fill="#151515"):
    """The 808's plate lettering: capitals large, the rest as small capitals ("BassDrum")."""
    spans = "".join('<tspan font-size="%g">%s</tspan>' % (big if ch.isupper() or not ch.isalpha() else small, ch.upper())
                    for ch in s)
    return ('<text x="%g" y="%g" fill="%s" text-anchor="middle" dominant-baseline="central" '
            'style="font-family:%s;font-weight:400;letter-spacing:0.01em;">%s</text>' % (x, y, fill, SANS, spans))


def k808(cap):
    return knob_img(body="#161616", edge="#000", knurl="#2c2c2c", knurl_n=24, cap=cap, cap_r=0.62, cap_edge="#000",
                    line_c="#111", line=(0.05, 0.6), line_w=6, shine=0.22, rr=0.9)


def notes808(p, y0):
    """The 808's note-value rows: light grey boxes with dark notes, four rows over the sixteen keys."""
    sx = [350 + 46.87 * i for i in range(16)]
    x0 = lambda i: 330 + 46.87 * i
    rows = [(3, list(range(16)), "8"), (6, [i for i in range(16) if i % 2 == 0], "8"), (4, [0, 4, 8, 12], "4"),
            (8, [0, 8], "4")]
    for r, (g, steps, kind) in enumerate(rows):
        y = y0 + r * 17
        for a in range(0, 16, g):
            b = min(16, a + g)
            p.add(rect(x0(a) + 2, y - 7, 46.87 * (b - a) - 6, 14, "#aeb0b1", rx=3))
            xs = [sx[st] for st in steps if a <= st < b]
            for x in xs:
                p.add(note(x - 2, y - 3, kind, "#1e1e1e", 0.7))
            if len(xs) > 1:
                p.add(path("M%g %g Q %g %g %g %g" % (xs[0] + 4, y - 7, (xs[0] + xs[-1]) / 2, y - 11, xs[-1] - 2, y - 7),
                           stroke="#1e1e1e", sw=1))


def chrome808(p, plates=True, title=None, alt=True, left=True, swap=False):
    """The TR-808 as the photo: black case, the programming block at the left, twelve instrument columns, the
    lettering and the grey step section. The left block is printed (the plugin plays from MPC's pads)."""
    Y = y808
    ink, red = "#d8d8d8", "#ef5a24"
    p.add(rect(0, 0, 1280, 628, "#0c0c0c"), rect(10, 0, 1260, 628, "#262626"), grain(10, 0, 1260, 628),
          rect(10, 0, 1260, 628, "url(#hw-vshade)"))
    for x in (5, 1275):
        p.add(rect(x - 5, 0, 10, 628, "#111"))
    for x, y in ((30, 22), (470, 22), (830, 22), (30, Y(560)), (640, Y(572)), (1250, 22)):
        p.add(screw(x, y, 4.5, head="#777"))
    # top: POWER, the name at the right
    p.add(T(152, 16, "POWER", 10, ink, 700), rect(130, 30, 44, 26, "#0a0a0a", rx=2), rect(136, 38, 22, 10, "#3a3a3a", rx=1),
          T(196, 36, "■ ON", 8, ink, 700, anchor="start"), T(196, 50, "■ OFF", 8, ink, 700, anchor="start"))
    p.add(T(1036, 64, "8W8", 36, red, 700, anchor="end", font=SANS, sp=0.02, stretch=1.1))
    if title:
        p.add(T(360, 50, title, 13, "#bdbdbd", 700, anchor="start", sp=0.12))
    p.add(line(110, Y(85), 1180, Y(85), "#8a8a8a", 2))
    # instrument section: column rules
    for i in range(13):
        x = 335 + CW808 * i
        p.add(line(x, Y(88), x, Y(312), "#707070", 1.3))
    if plates:
        for i, s in enumerate(C808):   # swap: the switched voices' plates where the switch selects them
            s = ALT808.get(i, s) if swap else s
            p.add(rect(X808[i] - 31, Y(291), 62, 19, "#ece4c4", rx=2), plate_text(X808[i], Y(300.5), s, 12.5, 8.5))
        for i, s in (ALT808.items() if alt else []):
            p.add(rect(X808[i] - 31, Y(238), 62, 19, "#ece4c4", rx=2), plate_text(X808[i], Y(247.5), s, 12.5, 8.5),
                  rect(X808[i] - 5, Y(262), 10, 22, "#0a0a0a", rx=2), rect(X808[i] - 3.5, Y(265), 7, 8, "#3a3a3a", rx=1))
    p.add(line(340, Y(357), 1080, Y(357), "#e8501f", 2),
          T(668, Y(344), "Rhythm Composer", 30, red, 400, anchor="start", font=SANS, sp=0.01, stretch=0.95),
          T(962, Y(345), "8W8", 24, red, 700, anchor="start", font=SANS),
          T(1036, Y(370), "Computer Controlled", 17, "#a8a8a8", 400, anchor="end", font=SANS))
    if left:
        # the programming block: MODE and INSTRUMENT-SELECT rotaries, PATTERN CLEAR, AUTO FILL IN, TEMPO
        o, red2 = "#e8dcae", "#e5432a"
        p.add(path("M110 %g H330 V%g H213 V%g H110 Z" % (Y(88), Y(235), Y(392)), stroke="#5d5d5d", sw=1.4),
              path("M330 %g V%g" % (Y(235), Y(392)), stroke="#5d5d5d", sw=1.4))
        p.add(rect(128, Y(87), 70, 12, "none", stroke=o, sw=1), T(163, Y(93), "PATTERN WRITE", 7.5, o, 700),
              T(276, Y(93), "INSTRUMENT-SELECT", 7.5, o, 700), rect(240, Y(98), 72, 10, "none", stroke=red2, sw=1),
              T(276, Y(103), "RHYTHM TRACK", 7, red2, 700))
        def blackknob(x, y, r, angle, mark="#e5432a"):
            return (circle(x, y + 2, r + 6, "#000", extra=' opacity="0.5"') + circle(x, y, r + 5, "#141414", "#000", 1) +
                    '<circle cx="%g" cy="%g" r="%g" fill="none" stroke="#2c2c2c" stroke-width="4" stroke-dasharray="2 2"/>' % (x, y, r + 2) +
                    circle(x, y, r - 1, "#1d1d1d", "#000", 1) + circle(x - r * .3, y - r * .3, r * .5, "#fff", extra=' opacity="0.06"') +
                    line(*pt(x, y, r * 0.3, angle), *pt(x, y, r * 0.95, angle), mark, 2.5))
        p.add(blackknob(165, Y(135), 20, -20), T(122, Y(122), "1st", 7.5, o, 700), T(122, Y(130), "PART", 7.5, o, 700),
              T(140, Y(108), "2nd PART", 7.5, o, 700), rect(180, Y(104), 34, 16, "none", stroke="#777", sw=1),
              T(197, Y(109), "MANUAL", 6.5, "#999", 700), T(197, Y(115), "PLAY", 6.5, "#999", 700),
              T(212, Y(124), "PLAY", 7.5, red2, 700), T(212, Y(136), "COM-", 7.5, red2, 700), T(212, Y(143), "POSE", 7.5, red2, 700))
        p.add(blackknob(277, Y(132), 15, 30))
        chips = [("HT", 262, 113), ("RS", 295, 113), ("MT", 240, 126), ("CP", 318, 126), ("LT", 240, 139), ("CB", 320, 139),
                 ("SD", 235, 153), ("CY", 320, 153), ("BD", 240, 167), ("OH", 320, 167), ("AC", 262, 181), ("CH", 295, 181)]
        for s_, x, y in chips:
            p.add(rect(x - 10, Y(y) - 5.5, 20, 11, o, rx=2), T(x, Y(y), s_, 7.5, "#151515", 700))
        p.add(rect(128, Y(180), 70, 12, "none", stroke=o, sw=1), T(163, Y(186), "PATTERN CLEAR", 7.5, o, 700),
              T(132, Y(198), "STEP", 7, o, 700), T(132, Y(205), "NUMBER", 7, o, 700), T(132, Y(213), "PRE-", 7, o, 700),
              T(132, Y(220), "SCALE", 7, o, 700), circle(166, Y(206), 7, "#c4190e", "#400"), circle(164, Y(204), 2.5, "#fff", extra=' opacity="0.35"'),
              T(192, Y(203), "TRACK", 7.5, red2, 700), T(192, Y(211), "CLEAR", 7.5, red2, 700))
        p.add(blackknob(277, Y(228), 14, 5), T(240, Y(226), "MANUAL", 6.5, ink, 700), T(262, Y(210), "16", 7, ink, 700),
              T(296, Y(210), "1", 7, ink, 700), T(304, Y(220), "4", 7, ink, 700), T(306, Y(232), "2", 7, ink, 700),
              T(277, Y(258), "MEASURES", 6.5, ink, 700), T(277, Y(266), "AUTO FILL IN", 7.5, ink, 700))
        # TEMPO: the big knob in its numbered ring, the fine knob and the beat LED
        cx, cy = 177, Y(320)
        p.add(T(cx, cy - 80, "TEMPO", 9, ink, 700), circle(cx, cy, 70, "#9c9c9c"), circle(cx, cy, 51, "#262626"),
              dots(cx, cy, 54, 41, "#e8e8e8", 1, -150, 150), numbers(cx, cy, 62, [str(i) for i in range(11)], 10, "#1e1e1e", -150, 150),
              blackknob(cx, cy, 40, 30))
        p.add(circle(287, Y(292), 4, "#5a4a2a", "#000"), blackknob(290, Y(332), 13, -40), dots(290, Y(332), 22, 9, ink, 1.2),
              T(268, Y(366), "SLOW", 7, ink, 700), T(312, Y(366), "FAST", 7, ink, 700))
    # the step section: grey panel and its blocks (photo y + 36)
    g, dk = "#8b8d8e", "#2a2a2a"
    p.add(rect(110, 432, 1070, 172, g, rx=3), grain(110, 432, 1070, 172), rect(110, 432, 1070, 2, "#b5b7b8"))
    p.add(rect(115, 434, 135, 72, "none", stroke="#4a4a4a", sw=1.2), T(182, 446, "BASIC-VARIATION", 8, dk, 700),
          rect(170, 452, 30, 14, "#1a1a1a", rx=2), rect(178, 450, 10, 18, "#d0d0d0", rx=1),
          T(168, 480, "A", 7.5, dk, 700), T(185, 480, "AB", 7.5, dk, 700), T(202, 480, "B", 7.5, dk, 700),
          rect(155, 488, 60, 12, "#1a1a1a", rx=2), circle(166, 494, 3, "#e8321e"), circle(204, 494, 3, "#e8321e"),
          rect(115, 511, 135, 66, "none", stroke="#4a4a4a", sw=1.2),
          rect(140, 524, 90, 42, "#f1d43a", rx=3, stroke="#6a5a10"), rect(143, 527, 84, 14, "#fff", rx=2, extra=' opacity="0.35"'),
          T(185, 538, "START", 9, dk, 700), T(185, 550, "STOP", 9, dk, 700))
    p.add(T(290, 446, "PRE-SCALE", 8, dk, 700), rect(282, 452, 14, 38, "#1a1a1a", rx=2), rect(284, 470, 10, 14, "#d0d0d0", rx=1))
    for i, y in enumerate((456, 465, 474, 483)):
        p.add(T(304, y, str(i + 1), 6.5, dk, 700), line(308, y, 326, y - 4, dk, 0.8))
    notes808(p, 446)
    p.add(path("M262 506 h56 l8 7 l-8 7 h-56 z", fill="#2a2a2a"), T(288, 513, "STEP NO", 8, "#e0e0e0", 700),
          circle(290, 530, 4.5, "#e8321e", "#400"), T(290, 543, "1st PART", 7.5, dk, 700),
          circle(290, 558, 4.5, "#5a0c06", "#200"), T(290, 571, "2nd PART", 7.5, dk, 700))
    cols = ["#e5341c"] * 4 + ["#f07a1c"] * 4 + ["#e6dc2a"] * 4 + ["#efede4"] * 4
    for i in range(16):
        x = 350 + 46.87 * i
        p.add(T(x, 513, str(i + 1), 8.5, dk, 700), rect(x - 19, 522, 38, 50, cols[i], rx=2, stroke="#3a3a3a"),
              rect(x - 17, 524, 34, 12, "#fff", rx=2, extra=' opacity="0.25"'), circle(x, 530, 2.6, "#5a0c06"),
              rect(x - 19, 566, 38, 6, "#000", extra=' opacity="0.2"'))
    p.add(path("M190 584 h104 l9 7 l-9 7 h-104 z", fill="#2a2a2a"), T(242, 591, "BASIC RHYTHM", 8, "#e0e0e0", 700))
    for i in range(12):
        p.add(T(350 + 46.87 * i, 591, str(i + 1), 15, dk, 400))
    p.add(rect(890, 580, 186, 22, "none", stroke=dk, sw=1.2))
    for i in range(4):
        p.add(T(350 + 46.87 * (12 + i), 591, str(i + 1), 15, dk, 400))
    p.add(path("M1172 584 h-58 l-9 7 l9 7 h58 z", fill="#2a2a2a"), T(1140, 591, "INTRO/FILL IN", 7.5, "#e0e0e0", 700))
    p.add(rect(1080, 434, 95, 72, "none", stroke="#4a4a4a", sw=1.2), T(1128, 446, "I / F-VARIATION", 7.5, dk, 700),
          rect(1114, 456, 30, 14, "#1a1a1a", rx=2), rect(1130, 454, 10, 18, "#d0d0d0", rx=1),
          T(1118, 482, "A", 7.5, dk, 700), T(1140, 482, "B", 7.5, dk, 700),
          rect(1080, 501, 95, 76, "none", stroke="#4a4a4a", sw=1.2), T(1128, 509, "INTRO SET", 7.5, dk, 700),
          T(1128, 518, "FILL IN TRIGGER", 7.5, dk, 700), rect(1110, 526, 46, 40, "#f1d43a", rx=3, stroke="#6a5a10"),
          T(1133, 546, "TAP", 9, dk, 700))


def p808(params):
    ko, kw_ = "k808o.svg", "k808w.svg"
    lab = dict(size=9.5, fill="#dcdcdc", font=SANS, weight=700, sp=0.04)

    def page(name, title=None, alt=True, plates=True, swap=False):
        p = Page(name, vink="#f0a050", lab=lab)
        p.asset(ko, k808("#f06a2a"))
        p.asset(kw_, k808("#f2f2ee"))
        chrome808(p, title=title, alt=alt, plates=plates, swap=swap)
        return p

    def kn(p, key, col, row, label, cap="w", r=14, x=None, y=None, **kw):
        x = X808[col] if x is None else x
        y = R808[row] if y is None else y
        p.add(ticks(x, y, r + 4, r + 8, 11, "#e0e0e0", 1.3))
        if cap == "o":
            p.add(circle(x + r + 7, y - 5, 2, "#f06a2a"))
        kw.setdefault("bw", 66)
        if len(label) > 7:
            kw.setdefault("size", 8)
            kw.setdefault("font", NARROW)
        p.knob(key, x, y, r, label, img="hw_" + (ko if cap == "o" else kw_), lab=-(r + 15), **kw)

    # page 1: the 808's own knobs
    p = page("808")
    levels = [("vel_depth", 0), ("bd_level", 1), ("sd_level", 2), ("lt_level", 3), ("mt_level", 4), ("ht_level", 5),
              ("rs_level", 6), ("cp_level", 7), ("cb_level", 8), ("cy_level", 9), ("oh_level", 10), ("ch_level", 11)]
    for k, c in levels:
        kn(p, k, c, 0, "LEVEL", "o")
    row2 = [("bd_tone", 1, "TONE"), ("sd_tune", 2, "TUNING"), ("lt_tune", 3, "TUNING"), ("mt_tune", 4, "TUNING"),
            ("ht_tune", 5, "TUNING"), ("cy_tune", 9, "TONE")]
    row3 = [("bd_decay", 1, "DECAY"), ("sd_snappy", 2, "SNAPPY"), ("cy_decay", 9, "DECAY"), ("oh_decay", 10, "DECAY")]
    for k, c, l in row2:
        kn(p, k, c, 1, l)
    for k, c, l in row3:
        kn(p, k, c, 2, l)
    vx, vy = 1140, y808(350)
    p.add(ticks(vx, vy, 18, 22, 11, "#e0e0e0", 1.3), T(vx - 26, vy + 14, "MIN", 7, "#dcdcdc"), T(vx + 26, vy + 14, "MAX", 7, "#dcdcdc"),
          T(vx, vy - 24, "MASTER VOLUME", 7.5, "#dcdcdc", 700))
    p.knob("volume", vx, vy, 13, "MASTER VOLUME", img="hw_" + kw_, bw=80)
    p.qrow(*[k for k, _ in levels], "volume")
    p.qrow(*[k for k, _, _ in row2])
    p.qrow(*[k for k, _, _ in row3])
    pages = [p]

    # page 2: the knobs the plugin adds to the 808's voices, in the same columns
    p = page("808 MORE", "EXTENDED VOICE CONTROLS")
    r1 = [("bd_tune", 1, "TUNING"), ("rs_tune", 6, "TUNING"), ("cp_tune", 7, "TUNING"), ("cb_tune", 8, "TUNING"),
          ("oh_tune", 10, "TUNING"), ("ch_tune", 11, "TUNING")]
    r2 = [("sd_decay", 2, "DECAY"), ("lt_decay", 3, "DECAY"), ("mt_decay", 4, "DECAY"), ("ht_decay", 5, "DECAY"),
          ("rs_decay", 6, "DECAY"), ("cp_decay", 7, "DECAY"), ("cb_decay", 8, "DECAY"), ("ch_decay", 11, "DECAY")]
    for k, c, l in r1:
        kn(p, k, c, 0, l)
    for k, c, l in r2:
        kn(p, k, c, 1, l)
    kn(p, "bd_attack", 1, 2, "ATTACK")
    hs = hh_switch(p)
    p.add(T((X808[10] + X808[11]) / 2, R808[2] - 26, "HIHAT CHOKE", 9, "#dcdcdc", 700))
    p.switch("hh_choke", (X808[10] + X808[11]) / 2, R808[2], 3, vertical=False, sw=44, sh=30, img=hs[0], img_on=hs[1],
             options=["OFF", "CH>OH", "MUT"])
    p.qrow(*[k for k, _, _ in r1])
    p.qrow(*[k for k, _, _ in r2])
    p.qrow("bd_attack")
    pages.append(p)

    # page 3: the switched voices (congas, claves, maracas) in the columns that switch to them
    p = page("CONGAS", "INSTRUMENT SELECT: CONGAS / CLAVES / MARACAS", alt=False, swap=True)
    alt = [("lc", 3), ("mc", 4), ("hc", 5), ("cl", 6), ("ma", 7)]
    for v, c in alt:
        kn(p, v + "_level", c, 0, "LEVEL", "o")
        kn(p, v + "_tune", c, 1, "TUNING")
        kn(p, v + "_decay", c, 2, "DECAY")
    kn(p, "ma_attack", 8, 2, "MA ATTACK")
    p.qrow(*[v + "_level" for v, _ in alt])
    p.qrow(*[v + "_tune" for v, _ in alt])
    p.qrow(*[v + "_decay" for v, _ in alt], "ma_attack")
    pages.append(p)

    # page 4: drive per voice (knob + type), the switched voices on the lower row
    order = ["bd", "sd", "lt", "mt", "ht", "rs", "cp", "cb", "cy", "oh", "ch"]
    p = page("DRIVE", "DRIVE PER VOICE", alt=False, plates=False)
    for i, v in enumerate(order):
        kn(p, v + "_drive", i + 1, 0, "DRIVE")
        p.popup(v + "_dist_type", X808[i + 1], 182, 64, 28, label="TYPE", accent="#f0a050")
    for v, c in alt:
        kn(p, v + "_drive", c, 0, SHORT808[c], y=258)
        p.popup(v + "_dist_type", X808[c], 322, 64, 28, label="TYPE", accent="#f0a050")
    
    p.qset("DRIVE", [v + "_drive" for v in order] + [v + "_drive" for v, _ in alt])
    pages.append(p)

    # page 5: reverb / delay sends
    p = page("SENDS", "REVERB / DELAY SENDS", alt=False, plates=False)
    for i, v in enumerate(order[1:]):
        kn(p, v + "_rev", i + 2, 0, "REVERB")
        kn(p, v + "_dly", i + 2, 1, "DELAY")
    for v, c in alt:
        kn(p, v + "_rev", c, 2, SHORT808[c] + " REV")
    for (v, c), col in zip(alt, [0, 8, 9, 10, 11]):   # their delay sends on the same row, in the free columns
        kn(p, v + "_dly", col, 2, SHORT808[c] + " DLY")
    p.qset("REVERB", [v + "_rev" for v in order[1:]] + [v + "_rev" for v, _ in alt])
    p.qset("DELAY", [v + "_dly" for v in order[1:]] + [v + "_dly" for v, _ in alt])
    pages.append(p)

    # page 6: master section and the effects
    p = page("MASTER", "MASTER / REVERB / DELAY", alt=False, plates=False)
    kn(p, "comp", 0, 0, "COMP")
    kn(p, "master_drive", 1, 0, "DRIVE")
    p.popup("master_dist", X808[1], R808[1], 64, 28, label="DIST", accent="#f0a050")
    p.add(T(X808[0], R808[1] - 30, "NOTE MAP", 8, "#dcdcdc", 700))
    p.switch("note_map", X808[0], R808[1], 2, vertical=True, sw=64, sh=24)
    for j, (k, l) in enumerate([("rev_decay", "DECAY"), ("rev_tone", "TONE"), ("rev_hpf", "HPF"), ("rev_level", "LEVEL")]):
        kn(p, k, 3 + j, 0, l)
    p.add(T((X808[3] + X808[6]) / 2, 74, "REVERB", 11, "#ef5a24", 700, sp=0.2))
    p.popup("dly_time", X808[7], R808[1], 64, 28, label="TIME", accent="#f0a050")
    for j, (k, l) in enumerate([("dly_fdbk", "FEEDBACK"), ("dly_tone", "TONE"), ("dly_hpf", "HPF"), ("dly_level", "LEVEL")]):
        kn(p, k, 8 + j, 0, l)
    p.add(T((X808[8] + X808[11]) / 2, 74, "DELAY", 11, "#ef5a24", 700, sp=0.2))
    p.qrow("comp", "master_drive", "rev_decay", "rev_tone", "rev_hpf", "rev_level", "dly_fdbk", "dly_tone")
    p.qrow("dly_hpf", "dly_level")
    pages.append(p)
    return pages


def hh_switch(p):
    off = p.asset("seg808.svg", svg_doc(56, 34, rect(2, 2, 52, 30, "#1a1a1a", rx=3, stroke="#555")))
    on = p.asset("seg808on.svg", svg_doc(56, 34, rect(2, 2, 52, 30, "#1a1a1a", rx=3, stroke="#555") +
                                       rect(14, 6, 28, 22, "#d8d8d8", rx=2)))
    return off, on


# ---- TR-909 -------------------------------------------------------------------------------------------------------
# Reference: Wikimedia Commons "Roland TR-909 (large).jpg". Instrument section, left to right, each under a slate bar
# with an orange name: TOTAL ACCENT; BASS DRUM (TUNE LEVEL / ATTACK DECAY); SNARE DRUM (TUNE LEVEL / TONE SNAPPY);
# LOW, MID, HI TOM (TUNE LEVEL / DECAY); RIM SHOT  HAND CLAP (LEVEL LEVEL); HI HAT (LEVEL / CH DECAY OH DECAY: the
# plugin's two hat levels take the top row); CYMBAL (LEVEL LEVEL / CRASH TUNE RIDE TUNE). Under it the START,
# STOP/CONT, the MEAS/TEMPO display, TEMPO and VOLUME row, then the cream step keys. Section widths are the photo's,
# x 0.774 to fill the width.
S909 = [("TOTAL ACCENT", 97, 182), ("BASS DRUM", 186, 302), ("SNARE DRUM", 307, 425), ("LOW TOM", 429, 545),
        ("MID TOM", 550, 667), ("HI TOM", 671, 787), ("RIM SHOT  HAND CLAP", 792, 909), ("HI HAT", 914, 1030),
        ("CYMBAL", 1035, 1154)]
# rows: the photo's 245 / 288 spread to 200 / 270 so MPC's value line fits under the upper knob (section bars and
# lettering move up by the same amount); the button row keeps its place, the step section is 20 px lower.
TOP909, BOT909, BAR909 = 200, 270, 150


def sec909():
    return [(name, x0, x1 - x0) for name, x0, x1 in S909]


def col909(si, col):
    """A knob's x in its section: col 0 / 1 = the photo's left / right knob, None = centred."""
    name, x, w = sec909()[si]
    return x + w / 2 if col is None else x + (34 if col == 0 else 89) * w / 116


def chrome909(p, title=None, sub=None):
    ink, slate, orange = "#3e444d", "#4b5566", "#f58a2a"
    p.add(rect(0, 0, 1280, 628, "#b9b8ae"), rect(8, 0, 1264, 612, "#e9e7df"), grain(8, 0, 1264, 612),
          rect(8, 0, 1264, 612, "url(#hw-vshade)"), rect(8, 606, 1264, 22, "#c9c8bf"), rect(8, 606, 1264, 2, "#a5a49b"))
    p.add(T(90, 92, "9W9", 64, ink, 700, anchor="start", font=SANS, sp=0.04, stretch=1.45),
          T(1160, 100, "RHYTHM COMPOSER", 26, ink, 400, anchor="end", font=SANS, sp=0.06, stretch=1.3))
    if title:
        p.add(T(420, 100, title, 13, "#f07a1c", 700, anchor="start", sp=0.14))
    for name, x, w in sec909():
        p.add(rect(x, BAR909 - 9, w, 18, slate), T(x + w / 2, BAR909, name, 11 if len(name) < 14 else 10, orange, 700, sp=0.02,
                                                  stretch=1 if len(name) < 14 else 0.9))
    for x in (92, 184, 305, 427, 548, 669, 790, 911, 1032, 1159):
        p.add(line(x, BAR909 - 9, x, 322, "#5a606a", 1.2))
    if sub:
        sub(p)


def seg7(x, y, h, lit="#ff3b25", dim="#5a1210"):
    """An unlit 7-segment '8' (the 909's display at rest)."""
    w = h * 0.55
    segs = [(x, y - h / 2, x + w, y - h / 2), (x + w, y - h / 2, x + w, y), (x + w, y, x + w, y + h / 2),
            (x, y + h / 2, x + w, y + h / 2), (x, y, x, y + h / 2), (x, y - h / 2, x, y), (x, y, x + w, y)]
    return "".join(line(*sg, dim, 3.2, extra=' stroke-linecap="round"') for sg in segs)


def row909(p):
    """The button row (START, STOP/CONT, MEAS/TEMPO, TEMPO, TRACK / PATTERN PLAY, the function keys, CARTRIDGE) and
    the step section, as the photo (artwork: the plugin plays from MPC's pads)."""
    ink, slate, orange, key = "#3e444d", "#4b5566", "#f58a2a", "#efe9d3"

    def sq(x, y, s=20, c="#cfa7a0"):
        return rect(x - s / 2 - 2, y - s / 2 - 2, s + 4, s + 4, "#5b5b5b", rx=2) + rect(x - s / 2, y - s / 2, s, s, c, rx=1) + \
            rect(x - s / 2 + 2, y - s / 2 + 2, s - 4, 4, "#fff", rx=1, extra=' opacity="0.4"')

    def obar(x0, x1, y, *lines):
        o = rect(x0, y - 6, x1 - x0, 12 if len(lines) == 1 else 20, orange)
        for i, l in enumerate(lines):
            o += T((x0 + x1) / 2, y + i * 9 - (4 if len(lines) > 1 else 0), l, 6.5, "#fff3e6", 700)
        return o
    p.add(T(130, 346, "START", 8.5, ink, 400), rect(106, 360, 48, 40, key, rx=2, stroke="#8e8c80"),
          rect(108, 362, 44, 10, "#fff", rx=2, extra=' opacity="0.5"'),
          T(196, 346, "STOP/CONT", 8.5, ink, 400), rect(172, 360, 48, 40, key, rx=2, stroke="#8e8c80"),
          rect(174, 362, 44, 10, "#fff", rx=2, extra=' opacity="0.5"'),
          T(302, 346, "MEAS/TEMPO", 8.5, ink, 400), rect(250, 358, 104, 44, "#7a1410", rx=1), rect(252, 360, 100, 40, "#8c1a14"))
    for i in range(3):
        p.add(seg7(268 + i * 26, 380, 26))
    p.add(T(420, 340, "TEMPO", 8.5, ink, 400), ticks(422, 368, 31, 38, 25, "#8a8e94", 1, -140, 140),
          circle(422, 370, 28, "#000", extra=' opacity="0.25"'), circle(422, 368, 27, "#1f2530", "#0b0d10", 1.5),
          circle(415, 361, 12, "#fff", extra=' opacity="0.07"'), line(*pt(422, 368, 12, 40), *pt(422, 368, 25, 40), "#f39a3a", 3),
          T(390, 408, "SLOW", 7, ink, 400), T(452, 408, "FAST", 7, ink, 400))
    p.add(T(555, 348, "TRACK PLAY", 7.5, ink, 400), T(685, 348, "PATTERN PLAY", 7.5, ink, 400))
    for i, x in enumerate((506, 538, 570, 601)):
        p.add(sq(x, 369), T(x, 388, str(i + 1), 7, ink, 400))
    for i, x in enumerate((649, 681, 713)):
        p.add(sq(x, 369), T(x, 388, str(i + 1), 7, ink, 400))
    p.add(sq(745, 369), obar(495, 614, 400, "TRACK  WRITE"), obar(637, 725, 400, "PATTERN WRITE"), obar(733, 758, 400, "EXT", "INST"))
    fk = [(791, "TEMPO", "STEP"), (823, "BACK", "TAP"), (855, "FWD", "I"), (886, "AVAILABLE MEAS", "II"),
          (923, "CYCLE /GUIDE", ""), (955, "TAPE SYNC", "")]
    for x, top, bot in fk:
        tw = top.split(" ")
        for j, t in enumerate(tw):
            p.add(T(x, 348 + j * 8 - (4 if len(tw) > 1 else 0), t, 6.5, ink, 400))
        p.add(sq(x, 369, c="#c9a19a" if x != 855 else "#e08a8a"))
        if bot:
            p.add(T(x, 388, bot, 7, ink, 400))
    p.add(obar(780, 836, 400, "PATTERN WRITE", "MODE"), obar(842, 900, 400, "BANK"), obar(911, 936, 400, "LAST", "MEAS"),
          obar(943, 969, 400, "TEMPO", "MODE"))
    p.add(T(1016, 344, "CARTRIDGE", 8, ink, 400), T(1016, 353, "/ENTER", 8, ink, 400),
          rect(991, 361, 50, 40, "#d8d5c8", rx=2, stroke="#8e8c80"), rect(1008, 365, 16, 6, "#3e444d"),
          T(1016, 410, "TOTAL ACCENT", 6.5, ink, 400))
    # the step section (photo y + 20)
    Y = lambda y: y + 20
    for r, (g, steps, kind) in enumerate([(6, [0, 2, 4, 6, 8, 10, 12, 14], "8"), (3, list(range(16)), "8"),
                                          (8, [0, 8], "4"), (4, [0, 4, 8, 12], "4")]):
        y = Y(422 + r * 17)
        for a in range(0, 16, g):
            b = min(16, a + g)
            x0, x1 = 185 + 60.6 * a, 185 + 60.6 * b
            p.add(rect(x0 + 1, y - 7, x1 - x0 - 2, 14, slate, rx=1))
            xs = [215 + 60.6 * st for st in steps if a <= st < b]
            for x in xs:
                p.add(note(x - 2, y - 3, kind, "#f2f2f2", 0.7))
            if len(xs) > 1:
                p.add(path("M%g %g Q %g %g %g %g" % (xs[0] + 4, y - 6, (xs[0] + xs[-1]) / 2, y - 10, xs[-1] - 2, y - 6),
                           stroke="#f2f2f2", sw=1))
        p.add(circle(180, y, 2.5, "#7a1a10"))
    for i in range(16):
        x = 215 + 60.6 * i
        p.add(T(x, Y(488), str(i + 1), 7.5, ink, 400), rect(x - 21, Y(497), 42, 40, "#7d7b70", rx=2),
              rect(x - 20, Y(497), 40, 38, key, rx=2), rect(x - 18, Y(499), 36, 9, "#fff", rx=2, extra=' opacity="0.55"'),
              rect(x - 6, Y(501), 12, 4, "#3e4a6a", rx=1))
        if i % 2 == 0 and i:
            p.add(line(x - 30, Y(480), x - 30, Y(492), "#8a8e94", 1))
    p.add(rect(185, Y(545), 970, 12, slate))
    for i, s_ in enumerate(["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "COPY", "INS", "DEL", "SAVE", "VERIFY", "LOAD"]):
        p.add(T(215 + 60.6 * i, Y(551), s_, 7.5, "#f2f2f2", 700))
    for i, s_ in enumerate(["BASS DRUM", "SNARE DRUM", "LOW TOM", "MID TOM", "HI TOM", "RIM SHOT    HAND CLAP",
                            "CLOSED   OPEN   CLOSED", "CRASH         RIDE"]):
        x = 215 + 60.6 * (2 * i) + 30.3
        p.add(rect(x - 55, Y(561), 110, 13, "none", rx=2, stroke=slate, sw=1), T(x, Y(567.5), s_, 6.5 if i > 4 else 7, ink, 400))
    for (x, y, s_, c) in ((118, 432, "LAST STEP", ink), (158, 432, "SCALE", ink), (118, 470, "SHUFFLE /FLAM", ink),
                          (158, 470, "CLEAR", ink), (118, 508, "INSTRUMENT SELECT", ink), (158, 508, "SHIFT", orange)):
        p.add(sq(x, Y(y), 16, "#c9c3b0"))
        ws = s_.split(" ")
        for j, w_ in enumerate(ws):
            if c == orange:
                p.add(rect(x - 12, Y(y + 13), 24, 9, orange), T(x, Y(y + 17.5), w_, 6, "#fff", 700))
            else:
                p.add(T(x, Y(y + 16 + j * 7), w_, 6, ink, 400))
    p.add(rect(98, Y(412), 80, 170, "none", stroke="#9a9a90", sw=1, rx=2))


def k909():
    return knob_img(body="#1f232a", edge="#08090b", knurl="#2d323b", knurl_n=20, cap="#2a2f38", cap_r=0.74,
                    cap_edge="#14171c", line_c="#f39a3a", line=(0.0, 0.95), line_w=5, shine=0.2, rr=0.88)


def p909(params):
    lab = dict(size=8.5, fill="#3e444d", font=SANS, weight=400, sp=0.03)
    secs = sec909()
    TOP, BOT = TOP909, BOT909

    def page(name, title=None, steps=True):
        p = Page(name, vink="#2f343c", lab=lab)
        p.asset("k909.svg", k909())
        chrome909(p, title)
        if steps:
            row909(p)
        return p

    def kn(p, key, si, col, row, label, r=15, **kw):
        name, x, w = secs[si]
        cx = col909(si, col)
        y = row if row > 2 else (TOP if row == 0 else BOT)
        p.add(ticks(cx, y, r + 3, r + 8, 11, "#8a8e94", 1.2))
        kw.setdefault("bw", 52 if col is not None else int(w - 6))
        if len(label) > 6 and col is not None:
            kw.setdefault("size", 7.5)
            kw.setdefault("font", NARROW)
        p.knob(key, cx, y, r, label, img="hw_k909.svg", lab=-(r + 9), **kw)

    p = page("909")
    top = [("bd_c_tune", 1, 0, "TUNE"), ("bd_c_level", 1, 1, "LEVEL"), ("sd_c_tune", 2, 0, "TUNE"), ("sd_c_level", 2, 1, "LEVEL"),
           ("lt_c_tune", 3, 0, "TUNE"), ("lt_c_level", 3, 1, "LEVEL"), ("mt_c_tune", 4, 0, "TUNE"), ("mt_c_level", 4, 1, "LEVEL"),
           ("ht_c_tune", 5, 0, "TUNE"), ("ht_c_level", 5, 1, "LEVEL"), ("rs_volume", 6, 0, "LEVEL"), ("hc_volume", 6, 1, "LEVEL"),
           ("chh_volume", 7, 0, "CH LEVEL"), ("ohh_volume", 7, 1, "OH LEVEL"), ("cr_volume", 8, 0, "LEVEL"), ("rc_volume", 8, 1, "LEVEL")]
    bot = [("accent", 0, None, ""), ("bd_c_attack", 1, 0, "ATTACK"), ("bd_c_decay", 1, 1, "DECAY"), ("sd_c_noise_decay", 2, 0, "TONE"),
           ("sd_c_snappy", 2, 1, "SNAPPY"), ("lt_c_decay", 3, 0, "DECAY"), ("mt_c_decay", 4, 0, "DECAY"), ("ht_c_decay", 5, 0, "DECAY"),
           ("chh_decay", 7, 0, "CH DECAY"), ("ohh_decay", 7, 1, "OH DECAY"), ("cr_pitch", 8, 0, "CRASH TUNE"), ("rc_pitch", 8, 1, "RIDE TUNE")]
    for k, si, c, l in top:
        kn(p, k, si, c, 0, l)
    for k, si, c, l in bot:
        kn(p, k, si, c, 1, l)
    p.add(T(1126, 330, "VOLUME", 8.5, "#3e444d", 400), ticks(1126, 364, 27, 34, 25, "#8a8e94", 1, -140, 140),
          T(1092, 392, "MIN", 7, "#3e444d"), T(1160, 392, "MAX", 7, "#3e444d"))
    p.knob("volume", 1126, 364, 24, "VOLUME", img="hw_k909.svg", bw=110, vs=16)
    p.qrow(*[k for k, *_ in top])
    p.qrow(*[k for k, *_ in bot], "volume")
    pages = [p]

    p = page("909 MORE", "EXTENDED VOICE CONTROLS")
    more = [("vel_depth", 0, None, 0, "VELOCITY"), ("bd_c_sweep_depth", 1, 0, 0, "SWEEP"), ("bd_c_pitch_mod", 1, 1, 0, "PITCH MOD"),
            ("lt_c_attack", 3, 0, 0, "ATTACK"), ("mt_c_attack", 4, 0, 0, "ATTACK"), ("ht_c_attack", 5, 0, 0, "ATTACK"),
            ("rs_tune", 6, 0, 0, "RIM TUNE"), ("hc_tune", 6, 1, 0, "CLAP TUNE"), ("chh_pitch", 7, 0, 0, "CH TUNE"),
            ("ohh_pitch", 7, 1, 0, "OH TUNE"), ("cr_decay", 8, 0, 0, "CRASH DEC"), ("rc_decay", 8, 1, 0, "RIDE DEC"),
            ("hc_decay", 6, 1, 1, "CLAP DECAY")]
    for k, si, c, row, l in more:
        kn(p, k, si, c, row, l)
    p.qrow(*[k for k, si, c, row, l in more if row == 0])
    p.qrow("hc_decay")
    pages.append(p)

    voices = [("bd_c", 1, 0), ("sd_c", 2, 0), ("lt_c", 3, 0), ("mt_c", 4, 0), ("ht_c", 5, 0), ("rs", 6, 0), ("hc", 6, 1),
              ("chh", 7, 0), ("ohh", 7, 1), ("cr", 8, 0), ("rc", 8, 1)]
    p = page("DRIVE", "DRIVE PER VOICE")
    dk = []
    names = {"rs": "RIM", "hc": "CLAP", "chh": "CH", "ohh": "OH", "cr": "CRASH", "rc": "RIDE"}
    for v, si, c in voices:
        k = "rs_saturation" if v == "rs" else v + "_drive"
        dk.append(k)
        name, x, w = secs[si]
        pair = si in (6, 7, 8)
        kn(p, k, si, c if pair else None, 0, ("SAT" if v == "rs" else "DRIVE") if not pair else names[v] + " " + ("SAT" if v == "rs" else "DRIVE"),
           bw=52 if pair else int(w - 6))
        if pair:
            py = 270 if c == 0 else 306
            p.popup(v + "_dist_type", x + w / 2 + 14, py, int(w - 40), 26, label="", accent="#f07a1c")
            p.text(x + 4, py, names[v], size=7.5, anchor="start")
        else:
            p.popup(v + "_dist_type", x + w / 2, 284, int(w - 16), 30, label="", accent="#f07a1c")
            p.text(x + w / 2, 262, "TYPE", size=8.5)
    kn(p, "master_drive", 0, None, 0, "MASTER DRIVE")
    p.popup("master_dist", secs[0][1] + secs[0][2] / 2, 284, int(secs[0][2] - 14), 30, label="", accent="#f07a1c")
    p.text(secs[0][1] + secs[0][2] / 2, 262, "TYPE", size=8.5)
    p.qset("DRIVE", dk + ["master_drive"])
    pages.append(p)

    p = page("SENDS", "REVERB / DELAY SENDS")
    sv = voices[1:]
    for v, si, c in sv:
        pair = si in (6, 7, 8)
        tag = (names[v] + " ") if pair else ""
        kn(p, v + "_rev", si, c if pair else None, 0, tag + "REVERB", bw=52 if pair else 110)
        kn(p, v + "_dly", si, c if pair else None, 1, tag + "DELAY", bw=52 if pair else 110)
    p.qset("REVERB", [v + "_rev" for v, _, _ in sv])
    p.qset("DELAY", [v + "_dly" for v, _, _ in sv])
    pages.append(p)

    # the master page: the same chassis, three sections in place of the instrument bars
    p = Page("MASTER", vink="#2f343c", lab=lab)
    p.asset("k909.svg", k909())
    chrome909(p, "MASTER / REVERB / DELAY")
    p.add(rect(92, BAR909 - 10, 1070, 182, "#e9e7df"), grain(92, BAR909 - 10, 1070, 182))
    groups = [("MASTER", 92, 300), ("REVERB", 396, 330), ("DELAY", 730, 429)]
    for name, x, w in groups:
        p.add(rect(x + 2, BAR909 - 9, w - 4, 18, "#4b5566"), T(x + w / 2, BAR909, name, 11, "#f58a2a", 700, sp=0.04),
              line(x + 2, BAR909 - 9, x + 2, 322, "#5a606a", 1.2))
    p.add(line(1159, BAR909 - 9, 1159, 322, "#5a606a", 1.2))

    def mk(k, x, y, l):
        p.add(ticks(x, y, 18, 23, 11, "#8a8e94", 1.2))
        p.knob(k, x, y, 15, l, img="hw_k909.svg", lab=-24, bw=70)
    mk("master_comp", 150, TOP, "COMP")
    p.add(T(290, TOP - 24, "NOTE MAP", 8.5, "#3e444d", 400))
    p.switch("note_map", 290, TOP + 16, 2, vertical=True, sw=130, sh=26)
    for i, (k, l) in enumerate([("rev_decay", "DECAY"), ("rev_tone", "TONE"), ("rev_hpf", "HPF"), ("rev_level", "LEVEL")]):
        mk(k, 440 + i * 80, TOP, l)
    p.popup("dly_time", 790, BOT + 4, 100, 30, label="", accent="#f07a1c")
    p.text(790, BOT - 18, "TIME", size=8.5)
    for i, (k, l) in enumerate([("dly_fdbk", "FEEDBACK"), ("dly_tone", "TONE"), ("dly_hpf", "HPF"), ("dly_level", "LEVEL")]):
        mk(k, 790 + i * 100, TOP, l)
    row909(p)
    p.qrow("master_comp", "rev_decay", "rev_tone", "rev_hpf", "rev_level", "dly_fdbk", "dly_tone", "dly_hpf")
    p.qrow("dly_level")
    pages.append(p)
    return pages


# ---- TR-606 -------------------------------------------------------------------------------------------------------
# Reference: Wikimedia Commons "Roland TR-606.jpg" (x 1.14). Same family as the 303: a silver top strip with the
# instrument level knobs (ACcent, BassDrum, SnareDrum, L.H.Tom, CYmbal, O.C.Hihat, lettered in the 606's mixed
# capitals), jack legends left and right, the name at the right; a silver middle strip with TEMPO, the INSTRUMENT
# and MODE selectors, "Computer Controlled" and VOLUME; the black step section with sixteen silver keys and red LEDs.
# The plugin has a level per voice (the 606 shares L.H.Tom and O.C.Hihat knobs, and has no clap), so the top row
# carries nine; the middle strip carries each voice's TUNE in the same column (where the 606 has its selectors),
# and the later pages use the same two rows.
X606 = [252 + 94.5 * i for i in range(9)]


def chrome606(p, title=None):
    p.add(rect(0, 0, 1280, 628, "#7d8082"), brushed(6, 4, 1268, 620, "#c4c6c7"),
          rect(6, 4, 1268, 620, "url(#hw-vshade)", rx=10), rect(6.5, 4.5, 1267, 619, "none", rx=10, stroke="#6f7274", sw=1.5),
          line(12, 124, 1268, 124, "#76797b", 2), line(12, 126.5, 1268, 126.5, "#eef0f0", 1.5))
    for x, s in ((42, "RUN/STOP"), (118, "INPUT"), (176, "SYNC")):
        p.add(tri(x, 18, 4), T(x, 32, s, 10, "#1a1a1a", 700))
    p.add(line(206, 16, 206, 116, "#2a2a2a", 1.5), line(1052, 16, 1052, 116, "#2a2a2a", 1.5))
    for x, s in ((1082, "TRIGGER OUT"), (1160, "HEADPHONE"), (1230, "OUTPUT")):
        p.add(tri(x, 18, 4), T(x, 32, s, 10, "#1a1a1a", 700))
    p.add(T(1156, 84, "6W6", 52, "#2a2b2c", 700, font=ROUND, sp=0.03))
    if title:
        p.add(T(106, 70, title, 13, "#2a2b2c", 700, sp=0.06))
    step606(p)


def note(x, y, kind="8", c="#f0f0f0", s=1.0):
    """A printed note: '8' an eighth (head, stem, flag), '4' a quarter."""
    o = ('<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s" transform="rotate(-20 %g %g)"/>' % (x, y + 4 * s, 4.2 * s, 3 * s, c, x, y + 4 * s)
         + line(x + 3.6 * s, y + 3 * s, x + 3.6 * s, y - 9 * s, c, 1.4 * s))
    if kind == "8":
        o += path("M%g %g q %g %g %g %g" % (x + 3.6 * s, y - 9 * s, 6 * s, 4 * s, 3 * s, 10 * s), stroke=c, sw=1.5 * s)
    return o


SX606 = [249 + 56.9 * i for i in range(16)]


def step606(p):
    """The TR-606 step section as the photo: black, the note-value rows, silver key cells (artwork)."""
    W_ = "#f0f0f0"
    p.add(rect(14, 316, 1252, 284, "#9c9fa1", rx=4), rect(24, 322, 1232, 262, "#151515", rx=2))
    # left: D.C. BAR RESET / PATTERN CLEAR, RUN / STOP
    p.add(rect(30, 328, 122, 96, "none", stroke="#cfcfcf", sw=1.2), rect(36, 343, 30, 16, "none", stroke=W_, sw=1),
          T(51, 351, "D.C.", 10, W_, 700, italic=True, font="serif"), rect(70, 343, 78, 16, "none", stroke=W_, sw=1),
          T(109, 351, "BAR RESET", 10, W_, 700), T(92, 373, "PATTERN CLEAR", 10.5, W_, 700),
          rect(66, 386, 52, 24, "url(#hw-screw)", rx=2, stroke="#000"),
          rect(30, 430, 122, 148, "none", stroke="#cfcfcf", sw=1.2), T(70, 443, "RUN", 9, W_, 700), led(93, 443, 4),
          T(124, 443, "BATTERY", 9, W_, 700), rect(52, 460, 78, 50, "url(#hw-screw)", rx=2, stroke="#000"),
          rect(55, 463, 72, 10, "#fff", rx=2, extra=' opacity="0.35"'), T(92, 531, "RUN/STOP", 11, W_, 700))
    # SCALE switch and FUNCTION
    for i, y in enumerate((352, 372, 392, 408)):
        p.add(T(168, y, "%d•" % (4 - i), 10, W_, 700))
    p.add(rect(180, 340, 14, 76, "#2a2a2a", stroke="#555"), rect(181, 396, 12, 16, "url(#hw-screw)", rx=1),
          path("M200 344 l8 -8 l12 0 M200 364 l8 -8 l12 0 M200 384 l8 -8 l12 0 M200 404 l8 -8 l12 0", stroke=W_, sw=1),
          T(188, 430, "SCALE", 11, W_, 700), T(188, 450, "FUNCTION", 11, W_, 700),
          rect(175, 466, 24, 46, "url(#hw-screw)", rx=2, stroke="#000"))
    # note-value rows: boxes split where the beats fall, notes over the steps
    rows = [(343, [(0, 6), (6, 12), (12, 16)], [0, 2, 4, 6, 8, 10, 12, 14], "8"),
            (373, [(0, 3), (3, 6), (6, 9), (9, 12), (12, 15), (15, 16)], list(range(16)), "8"),
            (396, [(0, 8), (8, 16)], [0, 8], "4"),
            (416, [(0, 4), (4, 8), (8, 12), (12, 16)], [0, 4, 8, 12], "4")]
    x0 = lambda i: 220 + 56.9 * i
    for y, groups, _, _ in rows:
        p.add(line(220, y + 11, 1128, y + 11, W_, 1))
        for a, b in groups:
            p.add(line(x0(a), y - 11, x0(a), y + 11, W_, 1))
    p.add(line(1128, 332, 1128, 427, W_, 1), line(220, 332, 1128, 332, W_, 1))
    # the notes sit over their steps; a tie arcs over the notes of one box
    for y, groups, steps, kind in rows:
        for st in steps:
            p.add(note(SX606[st] - 2, y - 2, kind, W_, 0.95))
        for a, b in groups:
            xs = [SX606[st] for st in steps if a <= st < b]
            if len(xs) > 1:
                p.add(path("M%g %g Q %g %g %g %g" % (xs[0] + 6, y - 12, (xs[0] + xs[-1]) / 2, y - 17, xs[-1] - 4, y - 12),
                           stroke=W_, sw=1.2))
    # key cells
    p.add(rect(220, 428, 908, 94, "#a7aaac"), rect(220, 546, 908, 28, "#a7aaac"))
    for i, x in enumerate(SX606):
        p.add(line(x0(i), 428, x0(i), 522, "#5d6062", 2), led(x, 442, 4.5),
              rect(x - 14, 460, 28, 52, "#2c2d2e", rx=2), rect(x - 12, 462, 24, 48, "url(#hw-screw)", rx=2),
              rect(x - 10, 464, 20, 8, "#fff", rx=1, extra=' opacity="0.35"'),
              T(x, 535, str(i + 1), 11, "#e8452a", 700))
        lab = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "100", "200", "/", "/", "DEL", "INS"][i]
        p.add(rect(x - 13, 552, 26, 16, "#151515" if i < 10 else "#f4f4f2", rx=2, stroke="#151515", sw=1),
              T(x, 560, lab if lab != "/" else "", 10, "#f0f0f0" if i < 10 else "#151515", 700))
        if lab == "/":
            p.add(line(x - 8, 565, x + 8, 555, "#151515", 1.6))
    p.add(path("M160 527 h58 l8 8 l-8 8 h-58 z", stroke="#e8452a", sw=1.2), T(190, 535, "LAST STEP", 9.5, "#e8452a", 700),
          path("M164 552 h50 l8 8 l-8 8 h-50 z", fill="#f0f0f0"), T(186, 560, "BAR", 9.5, "#151515", 700))
    # right: PATTERN GROUP, WRITE/NEXT
    p.add(rect(1134, 328, 116, 96, "none", stroke="#cfcfcf", sw=1.2), rect(1180, 336, 24, 18, "none", stroke=W_, sw=1),
          T(1192, 345, "§", 12, W_, 700), T(1150, 364, "I", 11, W_, 700, font="serif"), led(1168, 364, 4), led(1214, 364, 4),
          T(1232, 364, "II", 11, W_, 700, font="serif"), T(1192, 380, "PATTERN GROUP", 10.5, W_, 700),
          rect(1170, 390, 44, 22, "url(#hw-screw)", rx=2, stroke="#000"),
          rect(1134, 430, 116, 148, "none", stroke="#cfcfcf", sw=1.2), rect(1174, 438, 36, 18, "none", stroke=W_, sw=1),
          T(1192, 447, "D.S.", 10, W_, 700, italic=True, font="serif"),
          rect(1152, 462, 80, 48, "url(#hw-screw)", rx=2, stroke="#000"), rect(1155, 465, 74, 10, "#fff", rx=2, extra=' opacity="0.35"'),
          rect(1148, 516, 88, 18, "none", stroke=W_, sw=1), T(1192, 525, "WRITE/NEXT", 10.5, W_, 700),
          T(1192, 545, "TAP", 10.5, W_, 700), T(1192, 561, "STEP RESET", 10.5, W_, 700))


def p606(params):
    lab = dict(size=13, fill="#1a1a1a", font=SANS, weight=400, sp=0.0)
    names = ["ACcent", "BassDrum", "SnareDrum", "LowTom", "HiTom", "CYmbal", "OpenHihat", "Cls'dHihat", "handClaP"]
    voices = ["ac", "bd", "sd", "lt", "ht", "cy", "oh", "ch", "cp"]
    kb, kp = "hw_k606.svg", "hw_k606p.svg"

    def page(name, title=None):
        p = Page(name, vink="#1f1f1f", lab=lab)
        p.asset(kb, silver_knob_base())
        p.asset(kp, pointer_img())
        chrome606(p, title)
        return p

    def top(p, key, i, label=None):
        x = X606[i]
        p.add(ticks(x, 78, 35, 41, 11, "#1a1a1a", 1.7), tri(x, 44, 3.2))
        p.add(plate_text(x, 20, label or names[i], 15, 10.5, "#1a1a1a"))
        p.knob(key, x, 78, 29, label or names[i], img=kp, base=kb, bw=92)

    def mid(p, key, i, label, x=None):
        x = X606[i] if x is None else x
        p.add(ticks(x, 226, 32, 38, 11, "#1a1a1a", 1.6))
        p.knob(key, x, 226, 26, label, img=kp, base=kb, lab=-50, bw=92)

    def lettering(p):
        p.add(T(150, 196, "6W6", 40, "#1d1d1d", 400, font=SANS, sp=0.03, stretch=0.9), line(40, 218, 200, 218, "#1d1d1d", 1.6),
              T(120, 238, "Computer Controlled", 18, "#1d1d1d", 400, font=SANS))

    def volume(p):
        p.add(ticks(1156, 226, 44, 51, 11, "#1a1a1a", 1.8), T(1156, 152, "VOLUME", 13, "#1a1a1a", 700),
              T(1104, 282, "OFF /", 10, "#1a1a1a", 700), T(1210, 282, "\\ MAX", 10, "#1a1a1a", 700))
        p.knob("volume", 1156, 226, 38, "VOLUME", img=kp, base=kb, bw=96)

    p = page("606")
    lv = ["vel_depth"] + [v + "_level" for v in voices[1:]]
    for i, k in enumerate(lv):
        top(p, k, i)
    tunes = [v + "_tune" for v in voices[1:]]
    p.add(T(X606[0], 182, "TUNE", 13, "#1a1a1a", 700), path("M%g 196 L%g 196" % (X606[0] + 30, X606[8] + 40), stroke="#1a1a1a", sw=1))
    for i, k in enumerate(tunes):
        mid(p, k, i + 1, "")
    lettering(p)
    volume(p)
    p.qrow(*lv)
    p.qrow(*tunes, "volume")
    pages = [p]

    p = page("606 MORE", "VOICE SHAPING")
    dec = [v + "_decay" for v in voices[1:]]
    p.add(T(X606[0], 78, "DECAY", 13, "#1a1a1a", 700))
    for i, k in enumerate(dec):
        top(p, k, i + 1)
    extras = [("bd_attack", 1, "ATTACK"), ("sd_tone", 2, "TONE"), ("sd_snappy", 3, "SNAPPY"), ("cp_noise", 8, "NOISE")]
    p.add(T(X606[3], 166, "(SNARE)", 9, "#1a1a1a", 700))
    for k, i, l in extras:
        mid(p, k, i, l)
    p.add(T((X606[6] + X606[7]) / 2, 182, "HIHAT CHOKE", 12, "#1a1a1a", 700))
    off = p.asset("seg606.svg", svg_doc(60, 30, rect(2, 2, 56, 26, "#e4e5e6", rx=2, stroke="#55585a", sw=1.2)))
    on = p.asset("seg606on.svg", svg_doc(60, 30, rect(2, 2, 56, 26, "#2a2a2a", rx=2, stroke="#111", sw=1.2)))
    p.switch("hh_choke", (X606[6] + X606[7]) / 2, 230, 3, vertical=False, sw=60, sh=30, img=off, img_on=on)
    lettering(p)
    p.qrow(*dec)
    p.qrow(*[k for k, _, _ in extras])
    pages.append(p)

    p = page("DRIVE", "DRIVE PER VOICE")
    p.add(T(106, 98, "DRIVE / TYPE", 11, "#2a2b2c", 700))
    for i, v in enumerate(voices[1:]):
        top(p, v + "_drive", i + 1)
        p.popup(v + "_dist_type", X606[i + 1], 226, 88, 34, label="TYPE", accent="#c33a22")
    p.popup("master_dist", X606[0], 226, 88, 34, label="MASTER", accent="#c33a22")
    top(p, "master_drive", 0, "MASTER")
    p.qrow(*[v + "_drive" for v in voices[1:]])
    p.qrow("master_drive")
    pages.append(p)

    p = page("SENDS", "REVERB / DELAY SENDS")
    p.add(T(X606[0], 78, "REVERB", 13, "#1a1a1a", 700), T(X606[0], 226, "DELAY", 13, "#1a1a1a", 700))
    for i, v in enumerate(voices[1:]):
        top(p, v + "_rev", i + 1)
        mid(p, v + "_dly", i + 1, "")
    p.qrow(*[v + "_rev" for v in voices[1:]])
    p.qrow(*[v + "_dly" for v in voices[1:]])
    pages.append(p)

    p = page("MASTER", "MASTER / EFFECTS")
    tk = [("comp", "COMP"), ("vel_depth", None), ("rev_decay", "REV DECAY"), ("rev_tone", "REV TONE"), ("rev_hpf", "REV HPF"),
          ("rev_level", "REV LEVEL")]
    tk = [t for t in tk if t[0] != "vel_depth"]
    for i, (k, l) in enumerate(tk):
        x = X606[i]
        p.add(ticks(x, 78, 35, 41, 11, "#1a1a1a", 1.7), T(x, 20, l, 12, "#1a1a1a", 700))
        p.knob(k, x, 78, 29, l, img=kp, base=kb, bw=92)
    for i, (k, l) in enumerate([("dly_fdbk", "FEEDBACK"), ("dly_tone", "TONE"), ("dly_hpf", "HPF"), ("dly_level", "LEVEL")]):
        mid(p, k, i + 4, "DLY " + l)
    p.popup("dly_time", X606[8], 226, 88, 34, label="DLY TIME", accent="#c33a22")
    p.add(T(X606[0], 166, "NOTE MAP", 11, "#1a1a1a", 700))
    p.switch("note_map", X606[0], 216, 2, vertical=True, sw=120, sh=28)
    p.qrow(*[k for k, _ in tk], "dly_fdbk", "dly_tone")
    p.qrow("dly_hpf", "dly_level")
    pages.append(p)
    return pages


# ---- SH-101 (HUSH ONE) ----------------------------------------------------------------------------------------------
# Reference: Wikimedia Commons "Roland SH-101.jpg". Grey panel, white section titles in a bar across the top:
# TUNE | MODULATOR (LFO/CLK RATE slider, WAVE FORM rotary) | VCO (MOD slider, RANGE rotary, PULSE WIDTH slider and
# its LFO/MAN/ENV switch) | SOURCE MIXER (pulse, saw, SUB OSC sliders, the sub-octave switch, NOISE) | VCF (FREQ RES
# ENV MOD KYBD) | VCA (ENV/GATE switch) | ENV (GATE+TRIG/GATE/LFO switch, A D S R). Black slider caps with an orange
# line (green in the mixer), 0-5-10 scales. Under it the button row (HOLD works; the sequencer / arpeggio keys are
# printed), the striped name lettering, and at the bottom left the performance panel: VOLUME, PORTAMENTO and its
# AUTO/OFF/ON switch, TRANSPOSE, the BENDER's VCO range; the keyboard beside it.
def k101(angle=None, rr=0.86):
    body = knob_img(body="#1b1b1b", edge="#000", knurl="#2b2b2b", knurl_n=26, line_c="#f08a24", line=(0.2, 0.95),
                    line_w=7, shine=0.16, rr=rr)
    if angle is None:
        return body
    i = body.index("<line")
    return body[:i] + '<g transform="rotate(%g 48 48)">' % angle + body[i:-6] + "</g></svg>"


def cap101(c="#f08a24"):
    return svg_doc(28, 40, rect(1, 1, 26, 38, "#1a1a1a", rx=3, stroke="#000") + rect(3, 3, 22, 8, "#3a3a3a", rx=2) +
                   rect(1, 18, 26, 4, c))


def p101(params):
    INK = "#f2f2f2"
    lab = dict(size=12, fill=INK, font=SANS, weight=700, sp=0.02)

    def page(name):
        p = Page(name, vink="#ffb35a", lab=lab, seg_text=False)
        p.add(rect(0, 0, 1280, 628, "#4c4e50"), rect(4, 2, 1272, 624, "#6a6c6e", rx=6), grain(4, 2, 1272, 624),
              rect(4, 2, 1272, 624, "url(#hw-vshade)", rx=6))
        return p

    track = svg_doc(28, 200, rect(11, 0, 6, 200, "#0d0d0d", rx=2))
    p = page("SH-101")
    tr = p.asset("tr101.svg", track)
    co = p.asset("cap101o.svg", cap101())
    cg = p.asset("cap101g.svg", cap101("#3cc35a"))
    slot = p.asset("sl101.svg", svg_doc(28, 24, rect(9, 0, 10, 24, "#141414")))
    slon = p.asset("sl101on.svg", svg_doc(28, 24, rect(9, 0, 10, 24, "#141414") + rect(4, 2, 20, 20, "#1c1c1c", rx=2, stroke="#000") +
                                         rect(4, 10, 20, 3, "#f08a24")))
    p.asset("k101.svg", k101())
    # section bar
    secs = [("", 10, 100), ("MODULATOR", 100, 250), ("VCO", 250, 500), ("SOURCE MIXER", 500, 742), ("VCF", 742, 958),
            ("VCA", 958, 1018), ("ENV", 1018, 1270)]
    p.add(rect(10, 14, 1260, 34, "#5b5d5f"), line(10, 48, 1270, 48, "#d8d8d8", 1.5), line(10, 392, 1270, 392, "#d8d8d8", 1.5))
    for name, x0, x1 in secs:
        p.add(T((x0 + x1) / 2, 31, name, 17, INK, 700, sp=0.02))
        if x0 > 10:
            p.add(line(x0, 14, x0, 392, "#d8d8d8", 1.3))

    SY, SH = 238, 200   # slider centre and length

    def sl(key, x, label, green=False, nums=False):
        p.add(ticks_v(x, SY, SH, nums=nums))
        p.slider(key, x, SY, 28, SH, label, img=cg if green else co, base=tr, lab=-SH / 2 - 22, vs=16)

    def sw(key, x, y, n, names):
        p.switch(key, x, y, n, vertical=True, sw=28, sh=24, img=slot, img_on=slon)
        for i, s_ in enumerate(names):
            p.add(T(x + 18, y - n * 13 + 12 + i * 26, s_, 10, INK, 700, anchor="start"))

    # TUNE
    p.add(T(55, 92, "TUNE", 14, INK, 700), ticks(55, 250, 36, 41, 11, "#e8e8e8", 1.4), T(28, 292, "♭", 16, INK), T(82, 292, "♯", 16, INK))
    p.knob("fine_tune", 55, 250, 30, "TUNE", img="hw_k101.svg", bw=88, vs=16)
    # MODULATOR
    p.add(T(128, 72, "LFO/CLK", 11, INK, 700), rect(146, 120, 14, 6, "#5a1008"))
    sl("lfo_rate", 128, "RATE", nums=True)
    p.add(T(205, 92, "WAVE FORM", 12, INK, 700))
    wf = [-60, -20, 20, 60]
    p.rotary("lfo_waveform", 205, 190, 30, 4, lambda a: k101(a), angles=wf, field_w=88, field_dy=48)
    for a, g in zip(wf, ["tri", "sq", "RANDOM", "NOISE"]):
        px, py = pt(205, 190, 44, a)
        if g == "tri":
            p.add(path("M%g %g l5 -8 l5 8" % (px - 5, py + 4), stroke=INK, sw=1.6))
        elif g == "sq":
            p.add(path("M%g %g v-8 h6 v8 h6" % (px - 6, py + 4), stroke=INK, sw=1.6))
        else:
            p.add(T(px + 2, py - (6 if a < 40 else 0), g, 8, INK, 700, anchor="start"))
    # VCO
    sl("lfo_pitch", 275, "MOD", nums=True)
    p.add(T(342, 92, "RANGE", 12, INK, 700), ticks(342, 190, 35, 40, 5, "#e8e8e8", 1.4, -100, 100),
          numbers(342, 190, 52, ["32'", "16'", "8'", "4'", "2'"], 10, INK, -100, 100))
    p.knob("octave_transpose", 342, 190, 28, "RANGE", img="hw_k101.svg", bw=80, vs=16)
    sl("pulse_width", 408, "PULSE WIDTH")
    p.add(path("M432 110 h6 v-8 h6 v8", stroke=INK, sw=1.5))
    opts = [o.upper()[:3] for o in ("Env", "Manual", "LFO")]
    sw("pwm_mode", 455, 238, 3, opts)
    p.add(T(462, 300, "PWM", 10, INK, 700))
    # SOURCE MIXER
    p.add(path("M512 110 v-8 h6 v8 h6 v-8", stroke=INK, sw=1.5), path("M548 110 l8 -9 v9 l8 -9", stroke=INK, sw=1.5))
    sl("pulse", 522, "", nums=True)
    sl("saw", 558, "")
    sl("sub", 597, "SUB OSC", green=True)
    sw("sub_mode", 635, 238, 3, ["2 OCT ⊓", "2 OCT", "1 OCT"])
    sl("noise", 708, "NOISE", green=True)
    p.add(T(668, 312, "WHITE", 9, INK, 700))
    p.toggle("white_noise", 668, 336, "WHITE", img=slot, img_on=slon, w=28, h=24)
    # VCF
    for x, k, l in ((762, "cutoff", "FREQ"), (802, "resonance", "RES"), (846, "env_amt", "ENV"), (888, "lfo_filter", "MOD"),
                    (930, "key_follow", "KYBD")):
        sl(k, x, l, nums=k == "cutoff")
    # VCA
    sw("vca_mode", 988, 238, 2, ["GATE", "ENV"])
    # ENV
    sw("gate_trig_mode", 1040, 238, 3, ["GATE", "G+T", "LFO"])
    for x, k, l in ((1108, "attack", "A"), (1148, "decay", "D"), (1188, "sustain", "S"), (1228, "release", "R")):
        sl(k, x, l)
    # button row: HOLD works, the rest printed
    for i, (x, s_) in enumerate(((430, "LOAD"), (472, "PLAY"), (540, "DOWN"), (582, "U & D"), (624, "UP"))):
        p.add(rect(x - 16, 414, 32, 18, "#d9d4c4", rx=2, stroke="#333"), led(x, 404, 3), T(x, 444, s_, 9, INK, 700))
    p.add(T(451, 462, "SEQUENCER", 10, INK, 700), T(582, 462, "ARPEGGIO", 10, INK, 700), T(690, 462, "LEGATO", 10, INK, 700))
    hb = p.asset("hold101.svg", svg_doc(40, 40, '<circle cx="20" cy="7" r="4" fill="#4a0d08"/>' + rect(4, 18, 32, 18, "#d9d4c4", rx=2, stroke="#333")))
    hbo = p.asset("hold101on.svg", svg_doc(40, 40, '<circle cx="20" cy="7" r="7" fill="#ff3a22" opacity="0.35"/><circle cx="20" cy="7" r="4" fill="#ff3a22"/>' +
                                           rect(4, 18, 32, 18, "#d9d4c4", rx=2, stroke="#333")))
    p.toggle("hold", 690, 418, "HOLD", img=hb, img_on=hbo, w=40, h=40)
    p.add(T(690, 444, "HOLD", 9, INK, 700))
    # the name, striped like the 101's
    p.add('<defs><pattern id="hw-str" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2.4" fill="#e4e4e4"/></pattern></defs>',
          T(1250, 432, "HUSH ONE", 64, "url(#hw-str)", 700, anchor="end", font=SANS, sp=0.04, stretch=1.1))
    # performance panel and keyboard
    p.add(rect(10, 476, 330, 140, "#626466", rx=3), line(340, 476, 340, 616, "#3a3a3a", 1))
    p.add(T(40, 486, "VOLUME", 11, INK, 700), ticks(40, 522, 26, 30, 11, "#e8e8e8", 1.2))
    p.knob("volume", 40, 522, 21, "VOLUME", img="hw_k101.svg", vs=15)
    p.add(T(108, 486, "PORTAMENTO", 10, INK, 700), ticks(108, 522, 26, 30, 11, "#e8e8e8", 1.2))
    p.knob("glide", 108, 522, 21, "PORTAMENTO", img="hw_k101.svg", vs=15)
    pm = p.asset("pm101.svg", svg_doc(30, 22, rect(0, 7, 30, 8, "#141414")))
    pmo = p.asset("pm101on.svg", svg_doc(30, 22, rect(0, 7, 30, 8, "#141414") + circle(15, 11, 8, "#cfd1d2", "#555")))
    p.add(T(180, 494, "PORTAMENTO", 9, INK, 700))
    p.switch("portamento_mode", 180, 516, 3, vertical=False, sw=30, sh=22, img=pm, img_on=pmo)
    p.add(T(148, 536, "OFF", 8, INK, 700), T(180, 536, "ON", 8, INK, 700), T(212, 536, "AUTO", 8, INK, 700))
    p.add(T(262, 486, "TRANSPOSE", 9, INK, 700), ticks(262, 520, 24, 28, 9, "#e8e8e8", 1.2))
    p.knob("transpose", 262, 520, 19, "TRANSPOSE", img="hw_k101.svg", vs=15)
    bt = p.asset("trb101.svg", svg_doc(22, 80, rect(8, 0, 6, 80, "#0d0d0d", rx=2)))
    bc = p.asset("capb101.svg", svg_doc(22, 26, rect(1, 1, 20, 24, "#1a1a1a", rx=2) + rect(1, 11, 20, 4, "#f08a24")))
    p.add(T(318, 486, "VCO", 9, INK, 700))
    p.slider("bend_range", 318, 536, 22, 70, "BEND", img=bc, base=bt, vs=13)
    p.add(T(150, 574, "BENDER", 10, INK, 700), rect(110, 590, 124, 18, "#141414", rx=3), rect(164, 586, 16, 26, "#2a2a2a", rx=2),
          path("M118 580 h108", stroke=INK, sw=1), T(172, 616, "↔", 10, INK))
    # keyboard (artwork)
    kx0, kw = 352, 916 / 21
    p.add(rect(346, 476, 924, 148, "#3a3a3a", rx=2))
    for i in range(21):
        p.add(rect(kx0 + i * kw, 482, kw - 2, 140, "#f4f4f2", rx=2))
    for i in range(21):
        if i % 7 in (0, 1, 3, 4, 5) and i < 20:
            p.add(rect(kx0 + (i + 1) * kw - kw * 0.32, 482, kw * 0.6, 88, "#141414", rx=2))
    p.qrow("fine_tune", "lfo_rate", "lfo_pitch", "octave_transpose", "pulse_width", "pulse", "saw", "sub")
    p.qrow("noise", "cutoff", "resonance", "env_amt", "lfo_filter", "key_follow")
    p.qrow("attack", "decay", "sustain", "release", "volume", "glide", "transpose", "bend_range")
    pages = [p]
    pages += p101_more(params, page, track)
    return pages


def ticks_v(x, y, h, side=-1, ink="#e8e8e8", nums=True):
    """A slider's printed scale: 11 ticks beside the slot, 10 / 5 / 0 at the long ones."""
    o = []
    for i in range(11):
        yy = y - h / 2 + 8 + (h - 16) * i / 10
        ln = 9 if i % 5 == 0 else 5
        o.append(line(x + side * 16, yy, x + side * (16 + ln), yy, ink, 1.1))
    if nums:
        o.append(T(x + side * 33, y - h / 2 + 8, "10", 8, ink, 700))
        o.append(T(x + side * 30, y, "5", 8, ink, 700))
        o.append(T(x + side * 30, y + h / 2 - 8, "0", 8, ink, 700))
    return "".join(o)


def p101_more(params, page, track):
    """The plugin's extras, in the 101's own sections and slider style."""
    INK = "#f2f2f2"
    p = page("MORE")
    tr = p.asset("tr101s.svg", svg_doc(28, 150, rect(11, 0, 6, 150, "#0d0d0d", rx=2)))
    co = p.asset("cap101o.svg", cap101())
    slot = p.asset("sl101.svg", svg_doc(28, 24, rect(9, 0, 10, 24, "#141414")))
    slon = p.asset("sl101on.svg", svg_doc(28, 24, rect(9, 0, 10, 24, "#141414") + rect(4, 2, 20, 20, "#1c1c1c", rx=2, stroke="#000") +
                                         rect(4, 10, 20, 3, "#f08a24")))
    p.asset("k101.svg", k101())
    secs = [("FILTER ENV", 10, 300), ("PWM", 300, 420), ("LFO", 420, 760), ("VELOCITY", 760, 1010), ("VOICE", 1010, 1270)]
    p.add(rect(10, 14, 1260, 34, "#5b5d5f"), line(10, 48, 1270, 48, "#d8d8d8", 1.5), line(10, 300, 1270, 300, "#d8d8d8", 1.5))
    for name, x0, x1 in secs:
        p.add(T((x0 + x1) / 2, 31, name, 17, INK, 700))
        if x0 > 10:
            p.add(line(x0, 14, x0, 300, "#d8d8d8", 1.3))
    SY, SH = 172, 150

    def sl(key, x, label):
        p.add(ticks_v(x, SY, SH))
        p.slider(key, x, SY, 28, SH, label, img=co, base=tr, lab=-SH / 2 - 20, vs=15)

    def tg(key, x, y, label, names):
        p.switch(key, x, y, 2, vertical=True, sw=28, sh=24, img=slot, img_on=slon)
        p.add(T(x, y - 42, label, 10, INK, 700))
        for i, s_ in enumerate(names):
            p.add(T(x + 18, y - 13 + i * 26, s_, 9, INK, 700, anchor="start"))

    for x, k, l in ((56, "f_attack", "A"), (106, "f_decay", "D"), (156, "f_sustain", "S"), (206, "f_release", "R")):
        sl(k, x, l)
    tg("filter_env_full_range", 256, 172, "RANGE", ["STD", "FULL"])
    sl("pwm_depth", 336, "LFO")
    sl("pwm_env_depth", 384, "ENV")
    sl("lfo_pwm", 456, "PWM MOD")
    for i, (k, l, n) in enumerate((("lfo_trigger", "TRIG", ["FREE", "RTRG"]), ("lfo_sync", "SYNC", ["FREE", "SYNC"]),
                                   ("lfo_invert", "INVERT", ["OFF", "ON"]), ("lfo_pitch_snap", "SNAP", ["OFF", "ON"]))):
        tg(k, 512 + i * 62, 172, l, n)
    sl("filter_velocity_sens", 790, "VCF")
    sl("velocity_sens", 840, "VCA")
    p.add(T(920, 92, "MODE", 10, INK, 700))
    p.switch("velocity_mode", 905, 172, 3, vertical=True, sw=28, sh=24, img=slot, img_on=slon)
    for i, s_ in enumerate(["OFF", "TRIG", "ACTIVE"]):
        p.add(T(923, 146 + i * 26, s_, 9, INK, 700, anchor="start"))
    tg("filter_env_polarity", 975, 172, "ENV POL", ["+", "−"])
    tg("priority", 1040, 172, "PRIORITY", ["LAST", "LOW"])
    tg("retrigger", 1100, 172, "LEGATO", ["LEG", "TRIG"])
    tg("same_note_quirk", 1160, 172, "SAME NOTE", ["OFF", "ON"])
    tg("portamento_linear", 1222, 172, "GLIDE", ["EXP", "LIN"])
    # lower half: knobs for the rest
    for x, k, l in ((80, "preset", "PRESET"), (220, "adsr_declick", "DECLICK"), (360, "filter_volume_correction", "VOL COMP")):
        p.add(T(x, 340, l, 12, INK, 700), ticks(x, 392, 36, 41, 11, "#e8e8e8", 1.4))
        p.knob(k, x, 392, 30, l, img="hw_k101.svg", bw=120, vs=16)
    p.add('<defs><pattern id="hw-str" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2.4" fill="#e4e4e4"/></pattern></defs>',
          T(1250, 560, "HUSH ONE", 64, "url(#hw-str)", 700, anchor="end", font=SANS, sp=0.04, stretch=1.1))
    p.qrow("f_attack", "f_decay", "f_sustain", "f_release", "pwm_depth", "pwm_env_depth", "lfo_pwm", "filter_velocity_sens")
    p.qrow("velocity_sens", "preset", "adsr_declick", "filter_volume_correction")
    return [p]


# ---- CR-78 (CW-78) ------------------------------------------------------------------------------------------------
# Reference: a CR-78 product photo (polynominal.com) and its published control list; Commons has no panel photo.
# Black panel in a black case: the left column with the variation lever and START/STOP, slide faders across the
# top, the white-outlined programmable box, the orange name lettering, ACCENT and TEMPO knobs, the four white
# CANCEL buttons, and the rhythm selector: rows of square buttons in grey/white (WALTZ ... ENKA), green (BOSSANOVA ...
# BEGUINE), blue (ROCK 1-4), yellow (DISCO 1-2), red at the end. The plugin's RHYTHM I list is those seventeen
# rhythms in that order, and RHYTHM II the second button (the CR-78 combines two pressed rhythms), so each is a row
# of the coloured buttons. Instrument levels are CR-78-style faders on the next page, then tune / decay, drive, sends.
CR_GROUPS = [("#d9d9d4", 1), ("#f4f4ef", 6), ("#3fb36a", 4), ("#3f86d8", 4), ("#f2cf35", 2)]
CR_NAMES = ["WALTZ", "SHUFFLE", "SLOW ROCK", "SWING", "FOXTROT TANGO", "BOOGIE", "ENKA", "BOSSA NOVA", "SAMBA",
            "MAMBO CHA-CHA", "BEGUINE RHUMBA", "ROCK 1", "ROCK 2", "ROCK 3", "ROCK 4", "DISCO 1", "DISCO 2"]


def cr_row(p, key, y, with_off, label):
    names = (["OFF"] if with_off else []) + CR_NAMES
    cols = (["#d8342a"] if with_off else []) + [c for c, n in CR_GROUPS for _ in range(n)]
    n = len(names)
    sw = int((1236 - 2 * (n - 1)) / n)
    x0 = 640 - (n * sw + (n - 1) * 2) / 2
    p.add(T(22, y - 46, label, 12, "#e8e8e8", 700, anchor="start", sp=0.12))
    for i, (s, c) in enumerate(zip(names, cols)):
        x = x0 + i * (sw + 2)
        words = s.split()
        for j, w in enumerate(words):
            p.add(T(x + sw / 2, y - 34 + j * 11 - (len(words) - 1) * 5.5, w, 8.5, "#e8e8e8", 700))
        p.add(rect(x + 3, y - 20, sw - 6, 44, c, rx=3, stroke="#000", sw=1.2), rect(x + 5, y - 18, sw - 10, 12, "#fff", rx=2, extra=' opacity="0.3"'))
    off = p.asset("cr_btn.svg", svg_doc(sw, 50, ""))
    on = p.asset("cr_btnon.svg", svg_doc(sw, 50, rect(3, 3, sw - 6, 44, "none", rx=3, stroke="#ff8a2a", sw=4) +
                                         circle(sw / 2, 34, 4.5, "#ff3a22", "#5a0d08")))
    p.switch(key, 640, y + 2, n, vertical=False, sw=sw, sh=50, img=off, img_on=on)


CR_CAP = svg_doc(30, 30, '<path d="M9 2 h12 q3 0 3 4 v14 q0 8 -9 8 q-9 0 -9 -8 v-14 q0 -4 3 -4 z" fill="#efe8cf" '
         'stroke="#6a6450" stroke-width="1"/><rect x="10" y="5" width="4" height="18" rx="2" fill="#fff" opacity="0.6"/>')


def cr78_rhythms(p, key, pts):
    """The rhythm buttons as one option set, each at its own place (at=): unlit = printed, lit = an orange rim + LED."""
    off = p.asset("cr_btn.svg", svg_doc(58, 50, ""))
    on = p.asset("cr_btnon.svg", svg_doc(58, 50, rect(1, 1, 56, 48, "none", rx=4, stroke="#ff8a2a", sw=3.5) +
                                         circle(29, 38, 4.5, "#ff3a22", "#5a0d08")))
    p.switch(key, pts[0][0], pts[0][1], len(pts), vertical=False, sw=58, sh=50, img=off, img_on=on, at=pts)


def cr78_panel(p, INK, OR, programmer=True, caps=False):
    """The CR-78's face as the photo: silver rails, VARIATION / MEASURE, the slider block, the PROGRAMMER box, the
    lettering, CANCEL VOICE, POWER / FADE, and the coloured rhythm buttons (printed; the plugin's controls go on top)."""
    SIL = "#a9abad"
    p.add(rect(0, 0, 1280, 628, "#4a2a16"), wood(0, 0, 1280, 628, "#5a3218"), rect(22, 0, 1236, 628, "#161616"),
          grain(22, 0, 1236, 628))
    for x in (30, 232, 665, 1105, 1250):
        p.add(line(x, 6, x, 622, SIL, 2.5))
    p.add(line(670, 145, 1100, 145, SIL, 2), line(1110, 145, 1245, 145, SIL, 2), line(670, 332, 1100, 332, SIL, 2))
    # VARIATION: FILL IN ring, the knob
    cx, cy = 140, 152
    p.add(T(135, 32, "VARIATION", 12, INK, 700), T(140, 66, "FILL IN", 10, INK, 700))
    for i in range(7):
        a = -95 + i * 26
        x0, y0 = pt(cx, cy, 52, a)
        x1, y1 = pt(cx, cy, 64, a)
        p.add(line(x0, y0, x1, y1, "#e8e8e8", 7), T(*pt(cx, cy, 44, a), str(i + 1), 9, INK, 700))
    p.add(T(78, 172, "BREAK", 8, INK, 700), T(88, 190, "R", 8, INK, 700), T(80, 204, "(A)", 8, INK, 700),
          T(156, 208, "OFF", 8, INK, 700), T(198, 172, "HB", 8, INK, 700), T(198, 192, "SD", 8, INK, 700),
          T(218, 208, "ROLLING", 8, INK, 700), path("M206 172 h18 v20 h-14", stroke=INK, sw=1))
    p.add(circle(cx, cy + 3, 33, "#000", extra=' opacity="0.5"'), circle(cx, cy, 31, "#121212", "#000", 1),
          '<circle cx="%g" cy="%g" r="27" fill="none" stroke="#2a2a2a" stroke-width="5" stroke-dasharray="2 2"/>' % (cx, cy),
          line(*pt(cx, cy, 14, 200), *pt(cx, cy, 28, 200), "#e5432a", 3))
    # MEASURE
    mx, my = 168, 370
    p.add(T(172, 284, "MEASURE", 12, INK, 700), ticks(mx, my, 34, 44, 5, INK, 2, -80, 80),
          numbers(mx, my, 56, ["2", "4", "8", "12", "16"], 10, INK, -80, 80),
          circle(mx, my + 3, 36, "#000", extra=' opacity="0.5"'), circle(mx, my, 34, "#121212", "#000", 1),
          '<circle cx="%g" cy="%g" r="30" fill="none" stroke="#2a2a2a" stroke-width="5" stroke-dasharray="2 2"/>' % (mx, my),
          line(*pt(mx, my, 16, -80), *pt(mx, my, 31, -80), "#e5432a", 3))
    p.add(rect(186, 450, 18, 60, "#050505", rx=4), rect(189, 478, 12, 50, "url(#hw-screw)", rx=5),
          T(232, 456, "• AUTO", 8, INK, 700, anchor="end"), T(270, 478, "• MANUAL", 8, INK, 700, anchor="end"),
          rect(175, 540, 76, 70, "#efe8cf", rx=3, stroke="#000", sw=1.5), rect(179, 544, 68, 20, "#fff", rx=2, extra=' opacity="0.45"'))
    # slider block: scales, labels, ADD VOICE bracket
    for x in (297, 382, 500, 552, 604):
        p.add(rect(x - 4, 82, 8, 122, "#050505", rx=2))
        for t in range(11):
            yy = 88 + 110 * t / 10
            p.add(line(x - 26, yy, x - 14, yy, "#bdbdbd", 1), line(x + 14, yy, x + 26, yy, "#bdbdbd", 1))
        if caps:   # printed caps at rest where the page has no live sliders
            p.add('<g transform="translate(%g 182)">%s</g>' % (x - 15, CR_CAP[CR_CAP.index(">") + 1:-6]))
    for x, a_, b_ in ((262, "10", "0"), (330, "10", "0"), (348, "5", "5"), (420, "5", "5"), (470, "10", "0"), (640, "10", "0")):
        p.add(T(x, 100, a_, 9, INK, 700), T(x, 143, "5" if a_ == "10" else "0", 9, INK, 700), T(x, 186, b_, 9, INK, 700))
    p.add(T(475, 45, "CY HH", 10, OR, 700), T(475, 57, "METALLIC", 10, OR, 700), T(475, 69, "BEAT", 10, OR, 700),
          T(580, 33, "ADD VOICE", 12, INK, 700), path("M552 44 v-4 h52 v4 M578 40 v-4", stroke=INK, sw=1.2),
          T(552, 70, "TAMBOURINE", 10, INK, 700), T(608, 70, "GUIRO", 10, INK, 700))
    if programmer:
        p.add(rect(262, 222, 398, 218, "none", rx=6, stroke="#9a9a9a", sw=3), rect(275, 227, 372, 12, "#191919"),
              line(280, 233, 395, 233, OR, 1.5), line(528, 233, 642, 233, OR, 1.5), T(461, 233, "PROGRAMMER", 12, OR, 700),
              rect(272, 244, 380, 188, "none", rx=4, stroke="#7a7a7a", sw=1.5), T(470, 258, "TRACK", 9, INK, 700))
        for i, x in enumerate((395, 445, 495, 545)):
            p.add(led(x, 275, 5, lit=True), T(x, 292, str(i + 1), 9, INK, 700))
        ix, iy = 375, 380
        for i, s_ in enumerate(["S", "RS", "HH", "CY", "M", "C", "HB", "LB", "LC", "ACCENT"]):
            a = -120 + i * 240 / 9
            p.add(T(*pt(ix, iy, 58, a), s_, 9, OR if s_ != "ACCENT" else OR, 700))
        p.add(circle(ix, iy + 3, 34, "#000", extra=' opacity="0.5"'), circle(ix, iy, 32, "#121212", "#000", 1),
              '<circle cx="%g" cy="%g" r="28" fill="none" stroke="#2a2a2a" stroke-width="5" stroke-dasharray="2 2"/>' % (ix, iy),
              line(*pt(ix, iy, 14, 200), *pt(ix, iy, 29, 200), "#e5432a", 3),
              T(330, 428, "INSTR.", 9, INK, 700), T(435, 428, "SELECTOR", 9, INK, 700),
              rect(500, 320, 20, 120, "#050505", rx=4), rect(503, 390, 14, 50, "#1d1d1d", rx=3),
              T(540, 337, "• MEMORY", 8, INK, 700, anchor="start"), T(540, 357, "• PLAY", 8, INK, 700, anchor="start"),
              T(540, 377, "• ALL", 8, INK, 700, anchor="start"), T(610, 372, "CLEAR", 10, INK, 700),
              circle(608, 408, 22, "#efe8cf", "#000", 1.2), circle(602, 400, 8, "#fff", extra=' opacity="0.45"'))
    # PROGRAM RHYTHM I-IV
    p.add(rect(290, 445, 290, 98, "none", rx=6, stroke="#9a9a9a", sw=3), T(435, 455, "PROGRAM RHYTHM", 9, INK, 700))
    for i, x in enumerate((337, 401, 465, 529)):
        p.add(T(x, 470, ["I", "II", "III", "IV"][i], 11, OR, 700, font="serif"),
              rect(x - 29, 480, 58, 50, "#f3b51e", rx=3, stroke="#000", sw=1.2), rect(x - 26, 483, 52, 12, "#fff", rx=2, extra=' opacity="0.3"'))
    # the rhythm button rows (colours as the photo)
    p.add(rect(585, 455, 625, 95, "none", rx=6, stroke="#7a7a7a", sw=1.5), rect(300, 540, 790, 80, "none", rx=6, stroke="#7a7a7a", sw=1.5))
    up = [(655, "ROCK-1", "#2f6fd0"), (720, "ROCK-2", "#2f6fd0"), (785, "ROCK-3", "#2f6fd0"), (848, "ROCK-4", "#2f6fd0"),
          (912, "DISCO-1", "#f3b51e"), (975, "DISCO-2", "#f3b51e"), (1040, "CANCEL", "#d8342a")]
    low = [(343, "WALTZ", "#8a8a88"), (407, "SHUFFLE", "#ecebe6"), (470, "SLOW ROCK", "#ecebe6"), (532, "SWING", "#ecebe6"),
           (596, "A-FOX TROT B-TANGO", "#ecebe6"), (657, "BOOGIE", "#ecebe6"), (720, "ENKA", "#ecebe6"),
           (782, "BOSSA NOVA", "#1f9e4a"), (845, "SAMBA", "#1f9e4a"), (908, "A-MAMBO B-CHACHA", "#1f9e4a"),
           (970, "A-BEGUINE B-RHUMBA", "#1f9e4a"), (1035, "CANCEL", "#d8342a")]
    for row, y in ((up, 505), (low, 580)):
        for x, s_, c in row:
            ws = s_.replace("A-", "|A-").replace("B-", "|B-").strip("|").split("|") if "A-" in s_ else s_.split(" ")
            for j, w in enumerate(ws):
                p.add(T(x, y - 37 + j * 10 - (len(ws) - 1) * 5, w, 8, INK, 700))
            p.add(rect(x - 29, y - 25, 58, 50, c, rx=3, stroke="#000", sw=1.2), rect(x - 26, y - 22, 52, 12, "#fff", rx=2, extra=' opacity="0.3"'))
    # lettering, CANCEL VOICE
    p.add(T(968, 84, "CompuRhythm", 30, OR, 400, font=SANS), line(672, 100, 1100, 100, OR, 1.5), T(968, 120, "CW-78", 26, OR, 400))
    p.add(T(868, 346, "CANCEL VOICE", 11, INK, 700), path("M762 362 v-10 h70 M904 352 h90 v10", stroke=INK, sw=1))
    for x, s_ in ((762, "CYMBAL|HIGH HAT"), (838, "BASS DRUM"), (915, "SNARE DRUM"), (993, "COW BELL|CLAVES")):
        ws = s_.split("|")
        for j, w in enumerate(ws):
            p.add(T(x, 370 + j * 11 - (len(ws) - 1) * 5, w, 8.5, INK, 700))
        p.add(circle(x, 408, 23, "#efe8cf", "#000", 1.2), circle(x - 6, 400, 9, "#fff", extra=' opacity="0.45"'))
    # right column: POWER, FADE, START/STOP and RHYTHM legends
    p.add(T(1200, 32, "POWER", 12, INK, 700), T(1200, 56, "▲ ON", 8, INK, 700), circle(1192, 100, 26, "#0c0c0c", "#000"),
          circle(1186, 92, 9, "#fff", extra=' opacity="0.06"'),
          T(1185, 160, "FADE", 12, INK, 700), path("M1135 196 v-30 h30 M1205 166 h30 v30", stroke=INK, sw=1.2),
          T(1130, 212, "IN", 10, INK, 700), T(1218, 212, "OUT", 10, INK, 700))
    for x in (1130, 1205):
        p.add(rect(x - 10, 232, 20, 50, "#050505", rx=4), rect(x - 6, 256, 12, 50, "url(#hw-screw)", rx=5))
    p.add(T(1170, 238, "LONG", 7.5, INK, 700), T(1170, 262, "SHORT", 7.5, INK, 700), T(1170, 284, "OFF", 7.5, INK, 700),
          T(1155, 354, "START", 11, INK, 700, anchor="end"), path("M1157 360 l14 -14", stroke=INK, sw=1.5),
          T(1173, 356, "STOP", 11, INK, 700, anchor="start"),
          T(1128, 515, "RHYTHM", 10, INK, 700), T(1150, 542, "• A", 8, INK, 700, anchor="start"),
          T(1150, 566, "• B", 8, INK, 700, anchor="start"))


def k78(cap="#e9e9e4"):
    return knob_img(body="#151515", edge="#000", knurl="#2a2a2a", knurl_n=30, cap="#1b1b1b", cap_r=0.75,
                    line_c="#f07a2a", line=(0.1, 0.95), line_w=5, shine=0.2, rr=0.9)


def pcr78(params):
    INK, OR = "#ececec", "#f0872c"
    lab = dict(size=11, fill=INK, font=SANS, weight=700, sp=0.06)
    inst = [("bd", "BASS DRUM"), ("sd", "SNARE"), ("rs", "RIM SHOT"), ("hh", "HI-HAT"), ("cy", "CYMBAL"), ("ma", "MARACAS"),
            ("cl", "CLAVES"), ("hb", "HI BONGO"), ("lb", "LO BONGO"), ("lc", "LO CONGA"), ("cb", "COWBELL"), ("tb", "TAMB"),
            ("gu", "GUIRO"), ("mb", "METAL BEAT")]

    def page(name):
        p = Page(name, vink="#f4b06a", lab=lab, seg_text=False)
        p.add(rect(0, 0, 1280, 628, "#0c0c0c"), rect(10, 6, 1260, 616, "#191919", rx=4), grain(10, 6, 1260, 616))
        p.asset("k78.svg", k78())
        p.asset("cr_tr.svg", svg_doc(30, 150, rect(12, 0, 6, 150, "#050505", rx=2)))
        p.asset("cr_cap.svg", CR_CAP)
        return p

    def lettering(p, x=1240, y=56):
        p.add(T(x, y, "CW-78", 40, OR, 700, anchor="end", font=SANS, italic=True, sp=0.02),
              line(x - 330, y + 26, x, y + 26, OR, 2), T(x, y + 44, "RHYTHM COMPUTER", 14, INK, 700, anchor="end", sp=0.2))

    # page 1: the CR-78's own panel (Soundgas product photo, cropped to the panel): every control the plugin has at
    # its place, the rest printed. RHYTHM I = the rhythm buttons (lower row WALTZ .. BEGUINE, upper row ROCK / DISCO).
    LOW = [343, 407, 470, 532, 596, 657, 720, 782, 845, 908, 970]
    UP = [655, 720, 785, 848, 912, 975]
    p = page("CR-78")
    cr78_panel(p, INK, OR)
    for x, k, l in ((297, "volume", "VOLUME"), (382, "comp", "COMP"), (500, "mb_level", ""), (552, "tb_level", ""),
                    (604, "gu_level", "")):
        p.slider(k, x, 138, 30, 112, l or k, img="hw_cr_cap.svg", base="hw_cr_tr.svg", vs=13, bw=50)
    p.add(T(297, 68, "VOLUME", 12, INK, 700), T(382, 68, "COMP", 12, INK, 700))
    cr78_rhythms(p, "rhy_style", [(x, 580) for x in LOW] + [(x, 505) for x in UP])
    # ACCENT, and DRIVE in TEMPO's place (the plugin follows MPC's tempo)
    p.add(T(770, 160, "ACCENT", 12, INK, 700), ticks(762, 262, 38, 50, 7, INK, 2.2, -120, 60))
    p.knob("vel_depth", 762, 262, 34, "ACCENT", img="hw_k78.svg", bw=120, vs=14)
    p.add(T(970, 160, "DRIVE", 12, INK, 700), ticks(965, 262, 42, 56, 33, INK, 1.6, -135, 135),
          numbers(965, 262, 66, [str(i) for i in range(1, 10)], 11, INK, -135, 135), led(1062, 190, 5, lit=True))
    p.knob("master_drive", 965, 262, 38, "DRIVE", img="hw_k78.svg", bw=150, vs=14)
    # START/STOP = play, RHYTHM A/B
    ss = p.asset("cr_ss.svg", svg_doc(84, 76, rect(4, 4, 76, 68, "#efe8cf", rx=3, stroke="#000", sw=1.5) +
                                      rect(8, 8, 68, 22, "#fff", rx=2, extra=' opacity="0.45"')))
    sson = p.asset("cr_sson.svg", svg_doc(84, 76, rect(0, 0, 84, 76, "#ff9a3a", rx=5, extra=' opacity="0.35"') +
                                          rect(4, 4, 76, 68, "#fff4d6", rx=3, stroke="#000", sw=1.5) + circle(42, 56, 5, "#ff3a22")))
    p.toggle("rhy_mode", 1150, 405, "START / STOP", img=ss, img_on=sson, w=84, h=76)
    lev = p.asset("cr_ab.svg", svg_doc(30, 26, ""))
    levon = p.asset("cr_abon.svg", svg_doc(30, 26, rect(9, 1, 12, 24, "#d8d8d4", rx=5, stroke="#444")))
    p.add(rect(1121, 530, 18, 48, "#050505", rx=4))
    p.switch("rhy_ab", 1130, 554, 2, vertical=True, sw=30, sh=22, img=lev, img_on=levon)
    p.qrow("rhy_style", "rhy_ab", "volume", "comp", "mb_level", "tb_level", "gu_level", "vel_depth")
    p.qrow("master_drive", "rhy_mode")
    pages = [p]

    # page 2: RHYTHM II, the second pressed button (the CR-78 plays two rhythms at once); lower CANCEL = off.
    # The PROGRAMMER box holds the plugin's master switches.
    p = page("RHYTHM II")
    cr78_panel(p, INK, OR, programmer=False, caps=True)
    for x, r in ((762, 34), (965, 38)):   # ACCENT and DRIVE, printed at rest
        p.add(circle(x, 265, r, "#000", extra=' opacity="0.5"'), circle(x, 262, r, "#151515", "#000", 1),
              '<circle cx="%g" cy="262" r="%g" fill="none" stroke="#2a2a2a" stroke-width="5" stroke-dasharray="2 2"/>' % (x, r - 4),
              line(*pt(x, 262, r * 0.3, -135), *pt(x, 262, r * 0.95, -135), "#f07a2a", 4))
    p.add(T(770, 160, "ACCENT", 12, INK, 700), T(970, 160, "DRIVE", 12, INK, 700),
          rect(1108, 367, 84, 76, "#efe8cf", rx=3, stroke="#000", sw=1.5), rect(1112, 371, 76, 22, "#fff", rx=2, extra=' opacity="0.45"'),
          rect(1121, 530, 18, 48, "#050505", rx=4), rect(1124, 532, 12, 22, "#d8d8d4", rx=5))
    cr78_rhythms(p, "rhy_style2", [(1035, 580)] + [(x, 580) for x in LOW] + [(x, 505) for x in UP])
    p.add(rect(262, 222, 398, 218, "none", rx=6, stroke="#9a9a9a", sw=3), rect(275, 226, 372, 14, "#191919"),
          T(461, 233, "MASTER", 12, OR, 700, sp=0.2))
    p.add(T(330, 262, "HAT CHOKE", 10, INK, 700), T(470, 262, "NOTE MAP", 10, INK, 700), T(590, 262, "DISTORTION", 10, INK, 700))
    p.switch("hat_choke", 330, 330, 3, vertical=True, sw=96, sh=26)
    p.switch("note_map", 470, 316, 2, vertical=True, sw=96, sh=26)
    p.popup("master_dist", 590, 300, 110, 32, label="", accent=OR)
    p.qrow("rhy_style2", "hat_choke", "note_map", "master_dist")
    pages.append(p)

    # instrument levels: CR-78 faders, one per voice
    p = page("LEVELS")
    lettering(p, 1250, 50)
    p.add(T(30, 50, "INSTRUMENT LEVEL", 16, INK, 700, anchor="start", sp=0.16))
    for i, (v, n) in enumerate(inst):
        x = 60 + i * 89
        for t in range(11):
            yy = 190 + 300 * t / 10
            p.add(line(x - 24, yy, x - 18, yy, "#8a8a8a", 1))
        words = n.split()
        for j, w in enumerate(words):
            p.add(T(x, 150 + j * 13 - (len(words) - 1) * 6, w, 10, INK, 700))
        p.slider(v + "_level", x, 340, 30, 300, n, img="hw_cr_cap.svg", base="hw_cr_tr.svg", vs=14)
    p.qrow(*[v + "_level" for v, _ in inst])
    pages.append(p)

    # tune / decay per voice
    p = page("VOICES")
    lettering(p, 1250, 50)
    p.add(T(30, 50, "INSTRUMENT VOICING", 16, INK, 700, anchor="start", sp=0.16))
    for i, (v, n) in enumerate(inst):
        x = 50 + i * 90.7
        words = n.split()
        for j, w in enumerate(words):
            p.add(T(x, 128 + j * 13 - (len(words) - 1) * 6, w, 10, OR, 700))
        p.add(line(x + 45, 110, x + 45, 600, "#333", 1))
        p.knob(v + "_tune", x, 200, 24, "TUNE", img="hw_k78.svg", lab=-38)
        p.knob(v + "_decay", x, 330, 24, "DECAY", img="hw_k78.svg", lab=-38)
    p.knob("sd_snappy", 50 + 90.7, 460, 24, "SNAPPY", img="hw_k78.svg", lab=-38)
    p.knob("gu_rate", 50 + 12 * 90.7, 460, 24, "RATE", img="hw_k78.svg", lab=-38)
    p.qrow(*[v + "_tune" for v, _ in inst])
    p.qrow(*[v + "_decay" for v, _ in inst], "sd_snappy", "gu_rate")
    pages.append(p)

    # drive per voice
    p = page("DRIVE")
    lettering(p, 1250, 50)
    p.add(T(30, 50, "DRIVE PER INSTRUMENT", 16, INK, 700, anchor="start", sp=0.16))
    for i, (v, n) in enumerate(inst):
        x = 50 + i * 90.7
        y = 220 if i < 14 else 0
        words = n.split()
        for j, w in enumerate(words):
            p.add(T(x, 128 + j * 13 - (len(words) - 1) * 6, w, 10, OR, 700))
        p.knob(v + "_drive", x, 210, 24, "DRIVE", img="hw_k78.svg", lab=-38)
        p.popup(v + "_dist_type", x, 330 if i % 2 == 0 else 400, 86, 34, label="TYPE", accent=OR)
    p.qrow(*[v + "_drive" for v, _ in inst])
    pages.append(p)

    # sends
    p = page("SENDS")
    lettering(p, 1250, 50)
    p.add(T(30, 50, "REVERB / DELAY SENDS", 16, INK, 700, anchor="start", sp=0.16))
    for i, (v, n) in enumerate(inst[1:]):
        x = 60 + i * 96
        words = n.split()
        for j, w in enumerate(words):
            p.add(T(x, 128 + j * 13 - (len(words) - 1) * 6, w, 10, OR, 700))
        p.knob(v + "_rev", x, 210, 24, "REVERB", img="hw_k78.svg", lab=-38)
        p.knob(v + "_dly", x, 340, 24, "DELAY", img="hw_k78.svg", lab=-38)
    for i, (k, l) in enumerate((("rev_decay", "REV DECAY"), ("rev_tone", "REV TONE"), ("rev_hpf", "REV HPF"), ("rev_level", "REV LEVEL"),
                                ("dly_fdbk", "DLY FDBK"), ("dly_tone", "DLY TONE"), ("dly_hpf", "DLY HPF"), ("dly_level", "DLY LEVEL"))):
        p.knob(k, 100 + i * 120, 500, 26, l, img="hw_k78.svg", lab=-40)
    p.popup("dly_time", 1150, 500, 160, 40, label="DELAY TIME", accent=OR)
    p.qrow(*[v + "_rev" for v, _ in inst[1:]])
    p.qrow(*[v + "_dly" for v, _ in inst[1:]])
    p.qrow("rev_decay", "rev_tone", "rev_hpf", "rev_level", "dly_fdbk", "dly_tone", "dly_hpf", "dly_level")
    pages.append(p)
    return pages
