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
        '<circle cx="48" cy="50" r="%g" fill="#000" opacity="0.35"/>'
        '<circle cx="48" cy="48" r="%g" fill="url(#s)" stroke="#4a4c4e" stroke-width="1.2"/>'
        '<circle cx="48" cy="48" r="%g" fill="none" stroke="#6d7072" stroke-width="7" stroke-dasharray="2.2 2.2"/>'
        '<circle cx="48" cy="48" r="%g" fill="url(#t)" stroke="#8a8d8f" stroke-width="1"/>'
        % (R, R, R - 5, R * 0.66)))


def pointer_img(rr=0.92, c="#2b2b2b", w=4.5, r0=0.05, r1=0.62):
    R = 48 * rr
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
    kp = p.asset("k303p.svg", pointer_img())
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
        p.add(ticks(x, 80, 37, 43, 11, "#1a1a1a", 1.8), tri(x, 44, 3.5))
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
    p.knob("volume", 1109, 230, 44, "VOLUME", img=p.asset("k303pv.svg", pointer_img(w=4)), base=kb, lab=-82, bw=96)
    # lower panel: the keyboard section (artwork) round DEVIL MOD and the drive-model buttons
    p.add(rect(31, 316, 1218, 266, "#d3d5d6", rx=3, stroke="#7e8183", sw=2), grain(31, 316, 1218, 266),
          rect(36, 321, 1208, 256, "none", rx=2, stroke="#f4f5f5", sw=1))
    # left column (BAR RESET / RUN-STOP as printed), PITCH MODE block = DEVIL MOD
    p.add(rect(38, 326, 120, 92, "none", stroke="#555", sw=1), rect(38, 422, 120, 150, "none", stroke="#555", sw=1),
          T(98, 342, "D.C.  BAR RESET", 10, "#1a1a1a", 700), T(98, 366, "PATTERN CLEAR", 10, "#1a1a1a", 700),
          rect(70, 384, 56, 24, "url(#hw-screw)", rx=2, stroke="#555"),
          T(98, 440, "RUN  ●  BATTERY", 9, "#1a1a1a", 700), rect(58, 462, 80, 40, "url(#hw-screw)", rx=2, stroke="#555"),
          T(98, 528, "RUN/STOP", 11, "#1a1a1a", 700))
    p.add(rect(162, 326, 120, 92, "#1c1c1c"), T(222, 340, "DEVIL MOD", 13, "#eeeeee", 700, sp=0.02))
    btn = svg_doc(50, 64, METAL + rect(5, 30, 40, 26, "url(#mb)", rx=2, stroke="#55585a", sw=1.2) + rect(7, 32, 36, 6, "#fff", rx=2, extra=' opacity="0.6"'))
    off = p.asset("btn303.svg", svg_doc(50, 64, '<circle cx="25" cy="12" r="6" fill="#4a0d08" stroke="#160403"/>' + btn[btn.index(">") + 1:-6]))
    on = p.asset("btn303on.svg", svg_doc(50, 64, '<circle cx="25" cy="12" r="10" fill="#ff3a22" opacity="0.3"/>'
                                         '<circle cx="25" cy="12" r="6" fill="#ff3a22" stroke="#5a0d08"/>' + btn[btn.index(">") + 1:-6]))
    p.toggle("devil_mod_switch", 222, 384, "DEVIL MOD", img=off, img_on=on, w=50, h=64)
    p.add(rect(162, 422, 120, 150, "none", stroke="#555", sw=1), T(205, 438, "FUNCTION", 12, "#1a1a1a", 400),
          led(262, 438, 4), rect(180, 462, 40, 40, "url(#hw-screw)", rx=2, stroke="#555"), rect(205, 518, 30, 16, "#1c1c1c"),
          T(220, 526, "BAR", 10, "#eee", 700))
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
    # TIME MODE area: TRANSPOSE DOWN / UP = the drive model, ACCENT / SLIDE as printed
    p.add(rect(850, 326, 264, 246, "none", stroke="#555", sw=1), T(978, 342, "TIME MODE", 13, "#1a1a1a", 400), led(978, 358, 4.5),
          rect(850, 400, 136, 22, "#1c1c1c"), T(918, 388, "DRIVE MODEL", 11, "#1a1a1a", 700), T(884, 411, "SOFT", 11, "#eee", 700),
          T(952, 411, "RAT", 11, "#eee", 700), rect(988, 400, 126, 22, "#1c1c1c"), T(1018, 411, "ACCENT", 11, "#eee", 700),
          T(1082, 411, "SLIDE", 11, "#eee", 700), led(1013, 438, 4.5), led(1082, 438, 4.5),
          rect(1001, 462, 26, 40, "url(#hw-screw)", rx=2, stroke="#555"), rect(1069, 462, 26, 40, "url(#hw-screw)", rx=2, stroke="#555"),
          T(884, 528, "STEP", 11, "#1a1a1a", 400), rect(988, 520, 126, 22, "#c33a22"), T(1050, 531, "PATT. SECTION", 10, "#eee", 700))
    segoff = p.asset("seg303.svg", svg_doc(66, 80, '<circle cx="33" cy="16" r="5" fill="#4a0d08" stroke="#160403"/>' +
                                           METAL + rect(20, 40, 26, 40, "url(#mb)", rx=2, stroke="#55585a", sw=1.2)))
    segon = p.asset("seg303on.svg", svg_doc(66, 80, '<circle cx="33" cy="16" r="9" fill="#ff3a22" opacity="0.3"/>'
                                          '<circle cx="33" cy="16" r="5" fill="#ff3a22" stroke="#5a0d08"/>' +
                                          METAL + rect(20, 40, 26, 40, "url(#mb)", rx=2, stroke="#55585a", sw=1.2)))
    p.switch("drive_model", 917, 462, 2, vertical=False, sw=66, sh=80, img=segoff, img_on=segon)
    p.add(rect(1121, 326, 116, 92, "none", stroke="#555", sw=1), rect(1121, 422, 116, 150, "none", stroke="#555", sw=1),
          T(1179, 360, "BACK", 11, "#1a1a1a", 400), rect(1159, 384, 40, 24, "url(#hw-screw)", rx=2, stroke="#555"),
          rect(1139, 462, 80, 40, "url(#hw-screw)", rx=2, stroke="#555"), T(1179, 528, "WRITE/NEXT", 11, "#1a1a1a", 700),
          T(1179, 552, "TAP", 11, "#1a1a1a", 400))
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
X808 = [20 + 103.33 * (i + 0.5) for i in range(12)]
R808 = [96, 204, 312]


def plate_text(x, y, s, big=15, small=10.5, fill="#151515"):
    """The 808's plate lettering: capitals large, the rest as small capitals ("BassDrum")."""
    spans = "".join('<tspan font-size="%g">%s</tspan>' % (big if ch.isupper() or not ch.isalpha() else small, ch.upper())
                    for ch in s)
    return ('<text x="%g" y="%g" fill="%s" text-anchor="middle" dominant-baseline="central" '
            'style="font-family:%s;font-weight:400;letter-spacing:0.01em;">%s</text>' % (x, y, fill, SANS, spans))


def k808(cap):
    return knob_img(body="#161616", edge="#000", knurl="#2c2c2c", knurl_n=24, cap=cap, cap_r=0.62, cap_edge="#000",
                    line_c="#111", line=(0.05, 0.6), line_w=6, shine=0.22, rr=0.9)


def chrome808(p, plates=True, title=None, alt=True):
    """The 808's case and instrument section: columns, name plates, lettering, the step-key section."""
    p.add(rect(0, 0, 1280, 628, "#0e0e0e"), rect(8, 0, 1264, 628, "#2a2a2a"), grain(8, 0, 1264, 628),
          rect(8, 0, 1264, 628, "url(#hw-vshade)"))
    for x in (14, 1266):
        p.add(rect(x - 6, 0, 12, 628, "#141414"))
    p.add(line(20, 34, 1260, 34, "#7a7a7a", 2))
    for i in range(13):
        x = 20 + 103.33 * i
        p.add(line(x, 34, x, 446, "#6a6a6a", 1.4))
    p.add(T(1250, 18, "8W8", 22, "#ef5a24", 700, anchor="end", font=SANS, sp=0.02))
    if title:
        p.add(T(26, 18, title, 13, "#bdbdbd", 700, anchor="start", sp=0.12))
    for x in (40, 460, 820):
        p.add(screw(x, 16, 4.5, head="#888"))
    if plates:
        for i, s in enumerate(C808):
            p.add(rect(X808[i] - 47, 410, 94, 28, "#ece4c4", rx=2), plate_text(X808[i], 424, s))
        for i, s in (ALT808.items() if alt else []):
            p.add(rect(X808[i] - 47, 344, 94, 28, "#ece4c4", rx=2), plate_text(X808[i], 358, s),
                  rect(X808[i] - 6, 376, 12, 26, "#0a0a0a", rx=2), rect(X808[i] - 4, 380, 8, 10, "#3a3a3a", rx=1))
    p.add(line(470, 488, 1130, 488, "#e8501f", 2),
          T(490, 470, "Rhythm Composer", 34, "#ef5a24", 400, anchor="start", font=SANS, sp=0.01, stretch=0.95),
          T(936, 470, "8W8", 30, "#ef5a24", 700, anchor="start", font=SANS),
          T(1120, 504, "Computer Controlled", 20, "#a8a8a8", 400, anchor="end", font=SANS))
    # the step section: grey panel, START/STOP, sixteen keys in four colours, TAP
    p.add(rect(20, 520, 1240, 100, "#8e9091", rx=3), grain(20, 520, 1240, 100), rect(20, 520, 1240, 2, "#b5b7b8"))
    p.add(rect(40, 536, 108, 52, "#f3d63a", rx=3, stroke="#7a6a10"), rect(44, 540, 100, 20, "#fff", rx=2, extra=' opacity="0.35"'),
          T(94, 552, "START", 12, "#2a2a2a", 700), T(94, 570, "STOP", 12, "#2a2a2a", 700))
    cols = ["#e8321e"] * 4 + ["#f07a1c"] * 4 + ["#ecd531"] * 4 + ["#f1efe6"] * 4
    for i in range(16):
        x = 222 + i * 62.5
        p.add(T(x, 530, str(i + 1), 11, "#1a1a1a", 700), rect(x - 22, 540, 44, 50, cols[i], rx=3, stroke="#3a3a3a"),
              circle(x, 552, 3.5, "#5a0c06"), rect(x - 20, 584, 40, 4, "#000", extra=' opacity="0.25"'))
    p.add(rect(40, 598, 910, 18, "#5b5d5e", rx=2), T(48, 607, "BASIC RHYTHM ➔", 10, "#eee", 700, anchor="start"))
    for i in range(12):
        p.add(T(222 + i * 62.5, 607, str(i + 1), 13, "#fff", 700))
    p.add(rect(1220 - 30, 538, 60, 50, "#f3d63a", rx=3, stroke="#7a6a10"), T(1220, 563, "TAP", 12, "#2a2a2a", 700))


def p808(params):
    ko, kw_ = "k808o.svg", "k808w.svg"
    lab = dict(size=11, fill="#dcdcdc", font=SANS, weight=700, sp=0.04)

    def page(name, title=None, alt=True):
        p = Page(name, vink="#f0a050", lab=lab)
        p.asset(ko, k808("#f06a2a"))
        p.asset(kw_, k808("#f2f2ee"))
        chrome808(p, title=title, alt=alt)
        return p

    def kn(p, key, col, row, label, cap="w", r=22, x=None, y=None, **kw):
        x = X808[col] if x is None else x
        y = R808[row] if y is None else y
        p.add(ticks(x, y, r + 5, r + 10, 11, "#e0e0e0", 1.4))
        if cap == "o":
            p.add(circle(x + r + 9, y - 6, 2.4, "#f06a2a"))
        kw.setdefault("bw", 100)
        p.knob(key, x, y, r, label, img="hw_" + (ko if cap == "o" else kw_), lab=-(r + 22), **kw)

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
    p.add(ticks(1206, 478, 24, 29, 11, "#e0e0e0", 1.4), T(1174, 500, "MIN", 9, "#dcdcdc"), T(1238, 500, "MAX", 9, "#dcdcdc"))
    p.knob("volume", 1206, 478, 19, "MASTER VOLUME", img="hw_" + kw_, lab=-34, size=9, bw=110)
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
    p.add(T((X808[10] + X808[11]) / 2, 282, "HIHAT CHOKE", 11, "#dcdcdc", 700))
    p.switch("hh_choke", (X808[10] + X808[11]) / 2, 320, 3, vertical=False, sw=56, sh=34, img=hs[0], img_on=hs[1])
    p.qrow(*[k for k, _, _ in r1])
    p.qrow(*[k for k, _, _ in r2])
    p.qrow("bd_attack")
    pages.append(p)

    # page 3: the switched voices (congas, claves, maracas) in the columns that switch to them
    p = page("CONGAS", "INSTRUMENT SELECT: CONGAS / CLAVES / MARACAS")
    alt = [("lc", 3), ("mc", 4), ("hc", 5), ("cl", 6), ("ma", 7)]
    for v, c in alt:
        kn(p, v + "_level", c, 0, "LEVEL", "o")
        kn(p, v + "_tune", c, 1, "TUNING")
        kn(p, v + "_decay", c, 2, "DECAY")
    kn(p, "ma_attack", 8, 2, "MA ATTACK")
    for c in (3, 4, 5, 6, 7):   # the select switches thrown to the conga side
        p.add(rect(X808[c] - 4, 377, 8, 10, "#e8e8e8", rx=1))
    p.qrow(*[v + "_level" for v, _ in alt])
    p.qrow(*[v + "_tune" for v, _ in alt])
    p.qrow(*[v + "_decay" for v, _ in alt], "ma_attack")
    pages.append(p)

    # page 4: drive per voice (knob + type), the switched voices on the lower row
    order = ["bd", "sd", "lt", "mt", "ht", "rs", "cp", "cb", "cy", "oh", "ch"]
    p = page("DRIVE", "DRIVE PER VOICE", alt=False)
    for i, v in enumerate(order):
        kn(p, v + "_drive", i + 1, 0, "DRIVE", y=90)
        p.popup(v + "_dist_type", X808[i + 1], 176, 94, 34, label="TYPE", accent="#f0a050")
    for v, c in alt:
        kn(p, v + "_drive", c, 0, SHORT808[c] + " DRIVE", y=262, size=9)
        p.popup(v + "_dist_type", X808[c], 346, 94, 34, label="TYPE", accent="#f0a050")
    
    p.qset("DRIVE", [v + "_drive" for v in order] + [v + "_drive" for v, _ in alt])
    pages.append(p)

    # page 5: reverb / delay sends
    p = page("SENDS", "REVERB / DELAY SENDS", alt=False)
    for i, v in enumerate(order[1:]):
        kn(p, v + "_rev", i + 2, 0, "REVERB", y=90)
        kn(p, v + "_dly", i + 2, 1, "DELAY", y=192)
    for v, c in alt:
        kn(p, v + "_rev", c, 2, SHORT808[c] + " REV", y=300, size=9)
    for (v, c), col in zip(alt, [0, 8, 9, 10, 11]):   # their delay sends on the same row, in the free columns
        kn(p, v + "_dly", col, 2, SHORT808[c] + " DLY", y=300, size=9)
    p.qset("REVERB", [v + "_rev" for v in order[1:]] + [v + "_rev" for v, _ in alt])
    p.qset("DELAY", [v + "_dly" for v in order[1:]] + [v + "_dly" for v, _ in alt])
    pages.append(p)

    # page 6: master section and the effects
    p = page("MASTER", "MASTER / REVERB / DELAY", alt=False)
    kn(p, "comp", 0, 0, "COMP", y=120)
    kn(p, "master_drive", 1, 0, "DRIVE", y=120)
    p.popup("master_dist", X808[1], 226, 94, 34, label="DIST", accent="#f0a050")
    p.add(T(X808[0], 190, "NOTE MAP", 10, "#dcdcdc"))
    p.switch("note_map", X808[0], 226, 2, vertical=True, sw=80, sh=26)
    for j, (k, l) in enumerate([("rev_decay", "DECAY"), ("rev_tone", "TONE"), ("rev_hpf", "HPF"), ("rev_level", "LEVEL")]):
        kn(p, k, 3 + j, 0, l, y=120)
    p.add(T((X808[3] + X808[6]) / 2, 52, "REVERB", 12, "#ef5a24", 700, sp=0.2))
    p.popup("dly_time", X808[7], 226, 94, 34, label="TIME", accent="#f0a050")
    for j, (k, l) in enumerate([("dly_fdbk", "FEEDBACK"), ("dly_tone", "TONE"), ("dly_hpf", "HPF"), ("dly_level", "LEVEL")]):
        kn(p, k, 8 + j, 0, l, y=120)
    p.add(T((X808[8] + X808[11]) / 2, 52, "DELAY", 12, "#ef5a24", 700, sp=0.2))
    kn(p, "ui_focus", 0, 2, "FOCUS", y=322)
    kn(p, "mutes", 1, 2, "MUTES", y=322)
    p.qrow("comp", "master_drive", "rev_decay", "rev_tone", "rev_hpf", "rev_level", "dly_fdbk", "dly_tone")
    p.qrow("dly_hpf", "dly_level", "ui_focus", "mutes")
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
S909 = [("TOTAL ACCENT", 137), ("BASS DRUM", 175), ("SNARE DRUM", 177), ("LOW TOM", 177), ("MID TOM", 177),
        ("HI TOM", 177), ("RIM SHOT  HAND CLAP", 177), ("HI HAT", 177), ("CYMBAL", 190)]


def sec909():
    tot = sum(w for _, w in S909)
    out, x = [], 20.0
    for name, w in S909:
        ww = 1240.0 * w / tot
        out.append((name, x, ww))
        x += ww
    return out


def chrome909(p, title=None, sub=None):
    p.add(rect(0, 0, 1280, 628, "#a9aaa4"), rect(6, 0, 1268, 628, "#e7e6df"), grain(6, 0, 1268, 628),
          rect(6, 0, 1268, 628, "url(#hw-vshade)"))
    p.add(T(24, 62, "9W9", 70, "#3e444d", 700, anchor="start", font=SANS, sp=0.02, stretch=1.25),
          T(1258, 72, "RHYTHM COMPOSER", 30, "#3e444d", 700, anchor="end", font=SANS, sp=0.04, stretch=1.15))
    if title:
        p.add(T(260, 72, title, 14, "#f07a1c", 700, anchor="start", sp=0.14))
    for name, x, w in sec909():
        p.add(rect(x + 2, 116, w - 4, 20, "#4a525e"), T(x + w / 2, 126, name, 13 if len(name) < 14 else 11, "#f58a2a", 700, sp=0.02,
                                                       stretch=1 if len(name) < 14 else 0.86),
              line(x + 2, 136, x + 2, 384, "#5a606a", 1.2))
    p.add(line(1258, 136, 1258, 384, "#5a606a", 1.2))
    if sub:
        sub(p)


def row909(p):
    """START, STOP/CONT, MEAS/TEMPO display, the step keys (artwork)."""
    p.add(T(70, 404, "START", 11, "#3e444d", 400), rect(40, 414, 60, 52, "#f4efd9", rx=3, stroke="#9a9888"),
          T(160, 404, "STOP/CONT", 11, "#3e444d", 400), rect(130, 414, 60, 52, "#f4efd9", rx=3, stroke="#9a9888"),
          T(290, 404, "MEAS/TEMPO", 11, "#3e444d", 400), rect(220, 414, 140, 52, "#7a1210", rx=2),
          T(290, 441, "120", 34, "#ff3b25", 700, font=SANS, extra=' opacity="0.9"'))
    p.add(rect(20, 486, 1240, 4, "#4a525e"))
    for i in range(16):
        x = 70 + i * 72.5
        p.add(T(x, 502, str(i + 1), 11, "#3e444d", 400), rect(x - 26, 512, 52, 56, "#ece7d2", rx=3, stroke="#8e8c80"),
              rect(x - 6, 518, 12, 5, "#5a1810", rx=1), rect(x - 24, 560, 48, 6, "#000", extra=' opacity="0.12"'))
    p.add(rect(30, 578, 1205, 18, "#4a525e"))
    for i, s in enumerate(["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "COPY", "INS", "DEL", "SAVE", "VERIFY", "LOAD"]):
        p.add(T(70 + i * 72.5, 587, s, 11, "#f2f2f2", 700))
    for i, s in enumerate(["BASS DRUM", "SNARE DRUM", "LOW TOM", "MID TOM", "HI TOM", "RIM  CLAP", "CLOSED  OPEN", "CRASH  RIDE"]):
        x = 70 + i * 145 + 36
        p.add(rect(x - 64, 602, 128, 18, "none", rx=2, stroke="#4a525e", sw=1.2), T(x, 611, s, 10, "#3e444d", 700))


def k909():
    return knob_img(body="#1f232a", edge="#08090b", knurl="#2d323b", knurl_n=20, cap="#2a2f38", cap_r=0.74,
                    cap_edge="#14171c", line_c="#f39a3a", line=(0.0, 0.95), line_w=5, shine=0.2, rr=0.88)


def p909(params):
    lab = dict(size=11, fill="#3e444d", font=SANS, weight=700, sp=0.03)
    secs = sec909()
    TOP, BOT = 190, 312

    def page(name, title=None, steps=True):
        p = Page(name, vink="#2f343c", lab=lab)
        p.asset("k909.svg", k909())
        chrome909(p, title)
        if steps:
            row909(p)
        return p

    def kn(p, key, si, col, row, label, r=24, **kw):
        name, x, w = secs[si]
        cx = x + w / 2 if col is None else x + w * (0.3 if col == 0 else 0.7)
        y = row if row > 2 else (TOP if row == 0 else BOT)
        p.add(ticks(cx, y, r + 5, r + 9, 11, "#8a8e94", 1.3))
        kw.setdefault("bw", int(w * 0.4 - 2) if col is not None else int(w - 6))
        if len(label) > 6 and col is not None:
            kw.setdefault("size", 9.5)
            kw.setdefault("font", NARROW)
        p.knob(key, cx, y, r, label, img="hw_k909.svg", lab=-(r + 18), **kw)

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
    p.add(T(1100, 398, "VOLUME", 12, "#3e444d", 700), ticks(1100, 434, 32, 38, 21, "#8a8e94", 1.3),
          T(1056, 462, "MIN", 9, "#3e444d"), T(1144, 462, "MAX", 9, "#3e444d"))
    p.add(T(560, 404, "TEMPO", 11, "#3e444d", 400), circle(560, 440, 24, "#1f232a", "#08090b", 1.5),
          line(560, 440, 574, 422, "#f39a3a", 4), ticks(560, 440, 28, 33, 21, "#8a8e94", 1.2))
    p.knob("volume", 1100, 434, 28, "VOLUME", img="hw_k909.svg", bw=100, vs=18)
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
    for v, si, c in voices:
        k = "rs_saturation" if v == "rs" else v + "_drive"
        dk.append(k)
        name, x, w = secs[si]
        cx = x + w * (0.3 if c == 0 else 0.7) if si in (6, 7, 8) else x + w / 2
        p.add(ticks(cx, TOP, 29, 33, 11, "#8a8e94", 1.3))
        p.knob(k, cx, TOP, 24, "SAT" if v == "rs" else "DRIVE", img="hw_k909.svg", lab=-42,
               bw=int(w * 0.4 - 2) if si in (6, 7, 8) else 120)
        names = {"rs": "RIM", "hc": "CLAP", "chh": "CH", "ohh": "OH", "cr": "CRASH", "rc": "RIDE"}
        if si in (6, 7, 8):
            p.popup(v + "_dist_type", x + w / 2, 286 if c == 0 else 344, int(w - 16), 32, label=names[v] + " TYPE", accent="#f07a1c")
        else:
            p.popup(v + "_dist_type", cx, 300, int(w - 20), 34, label="TYPE", accent="#f07a1c")
    kn(p, "master_drive", 0, None, 0, "MASTER DRIVE")
    p.popup("master_dist", secs[0][1] + secs[0][2] / 2, 300, int(secs[0][2] - 16), 34, label="MASTER", accent="#f07a1c")
    p.qset("DRIVE", dk + ["master_drive"])
    pages.append(p)

    p = page("SENDS", "REVERB / DELAY SENDS")
    sv = voices[1:]
    for v, si, c in sv:
        name, x, w = secs[si]
        cx = x + w * (0.3 if c == 0 else 0.7) if si in (6, 7, 8) else x + w / 2
        for k, y, l in ((v + "_rev", TOP, "REVERB"), (v + "_dly", BOT, "DELAY")):
            p.add(ticks(cx, y, 29, 33, 11, "#8a8e94", 1.3))
            p.knob(k, cx, y, 24, l, img="hw_k909.svg", lab=-42, bw=int(w * 0.4 - 2) if si in (6, 7, 8) else 120)
    p.qset("REVERB", [v + "_rev" for v, _, _ in sv])
    p.qset("DELAY", [v + "_dly" for v, _, _ in sv])
    pages.append(p)

    p = Page("MASTER", vink="#2f343c", lab=lab)
    p.asset("k909.svg", k909())
    chrome909(p, "MASTER / REVERB / DELAY")
    p.add(rect(20, 116, 1240, 270, "#e7e6df"))
    groups = [("MASTER", 20, 300), ("REVERB", 330, 420), ("DELAY", 760, 500)]
    for name, x, w in groups:
        p.add(rect(x + 2, 116, w - 4, 20, "#4a525e"), T(x + w / 2, 126, name, 13, "#f58a2a", 700, sp=0.04),
              line(x + 2, 136, x + 2, 384, "#5a606a", 1.2))

    def mk(k, x, y, l):
        p.add(ticks(x, y, 29, 33, 11, "#8a8e94", 1.3))
        p.knob(k, x, y, 24, l, img="hw_k909.svg", lab=-42, bw=96)
    mk("master_comp", 90, TOP, "COMP")
    p.add(T(240, 160, "NOTE MAP", 11, "#3e444d", 700))
    p.switch("note_map", 230, 200, 2, vertical=True, sw=150, sh=28)
    for i, (k, l) in enumerate([("rev_decay", "DECAY"), ("rev_tone", "TONE"), ("rev_hpf", "HPF"), ("rev_level", "LEVEL")]):
        mk(k, 383 + i * 104, TOP, l)
    p.popup("dly_time", 830, BOT - 10, 120, 36, label="TIME", accent="#f07a1c")
    for i, (k, l) in enumerate([("dly_fdbk", "FEEDBACK"), ("dly_tone", "TONE"), ("dly_hpf", "HPF"), ("dly_level", "LEVEL")]):
        mk(k, 815 + i * 120, TOP, l)
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
    # lower black section: step keys, LEDs, LAST STEP / BAR rows (artwork)
    p.add(rect(14, 316, 1252, 300, "#232323", rx=4), rect(14, 316, 1252, 300, "url(#hw-vshade)", rx=4))
    p.add(rect(24, 326, 150, 120, "none", stroke="#d8d8d8", sw=1.2), T(99, 342, "D.C.  BAR RESET", 10, "#e8e8e8", 700),
          T(99, 364, "PATTERN CLEAR", 10, "#e8e8e8", 700), rect(74, 384, 50, 26, "url(#hw-screw)", rx=2),
          rect(24, 452, 150, 154, "none", stroke="#d8d8d8", sw=1.2), T(99, 470, "RUN  ●  BATTERY", 9, "#e8e8e8", 700),
          rect(59, 492, 80, 46, "url(#hw-screw)", rx=2), T(99, 560, "RUN/STOP", 11, "#e8e8e8", 700))
    for r in range(4):
        p.add(rect(220, 336 + r * 24, 1000, 18, "none", stroke="#d8d8d8", sw=1))
    for i in range(16):
        x = 248 + i * 62.3
        p.add(led(x, 446, 4.5), rect(x - 15, 466, 30, 52, "url(#hw-screw)", rx=2, stroke="#111"),
              T(x, 534, str(i + 1), 12, "#e8452a", 700), rect(x - 14, 552, 28, 18, "#e8e8e8", rx=1),
              T(x, 561, ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "100", "200", "/", "/", "DEL", "INS"][i], 10, "#111", 700))
    p.add(rect(1230, 326, 28, 280, "#2c2c2c"))


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
    for i, (k, l) in enumerate([("ui_focus", "FOCUS"), ("mutes", "MUTES")]):
        mid(p, k, 2 + i, l)
    p.qrow(*[k for k, _ in tk], "dly_fdbk", "dly_tone")
    p.qrow("dly_hpf", "dly_level", "ui_focus", "mutes")
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
          numbers(342, 190, 52, ["-2", "-1", "0", "+1", "+2"], 10, INK, -100, 100))
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
        p.asset("cr_cap.svg", svg_doc(30, 30, circle(15, 15, 13, "#eeeeea", "#555", 1.5) + circle(12, 11, 6, "#fff", extra=' opacity="0.5"')))
        return p

    def lettering(p, x=1240, y=56):
        p.add(T(x, y, "CW-78", 40, OR, 700, anchor="end", font=SANS, italic=True, sp=0.02),
              line(x - 330, y + 26, x, y + 26, OR, 2), T(x, y + 44, "RHYTHM COMPUTER", 14, INK, 700, anchor="end", sp=0.2))

    p = page("CR-78")
    lettering(p, 1250, 50)
    # left column: variation lever, start/stop
    p.add(line(170, 20, 170, 320, "#c9c9c9", 1.5), T(90, 40, "VARIATION", 12, INK, 700))
    lev = p.asset("cr_lev.svg", svg_doc(60, 34, rect(26, 4, 8, 26, "#050505", rx=3)))
    levon = p.asset("cr_levon.svg", svg_doc(60, 34, rect(26, 4, 8, 26, "#050505", rx=3) + rect(18, 6, 24, 22, "#d9d9d6", rx=3, stroke="#555")))
    p.switch("rhy_ab", 90, 104, 2, vertical=False, sw=60, sh=34, img=lev, img_on=levon)
    p.add(T(60, 134, "A", 13, INK, 700), T(122, 134, "B", 13, INK, 700))
    p.add(T(90, 186, "START / STOP", 12, INK, 700))
    ss = p.asset("cr_ss.svg", svg_doc(80, 66, rect(6, 4, 68, 58, "#eee9d6", rx=4, stroke="#000", sw=1.5) + rect(10, 8, 60, 16, "#fff", rx=3, extra=' opacity="0.5"')))
    sson = p.asset("cr_sson.svg", svg_doc(80, 66, rect(2, 0, 76, 66, "#ff9a3a", rx=6, extra=' opacity="0.35"') +
                                          rect(6, 4, 68, 58, "#fff3d6", rx=4, stroke="#000", sw=1.5) + circle(40, 46, 5, "#ff3a22")))
    p.toggle("rhy_mode", 90, 240, "START / STOP", img=ss, img_on=sson, w=80, h=66)
    # faders
    p.add(line(470, 20, 470, 320, "#c9c9c9", 1.5))
    for i, (k, l) in enumerate((("volume", "VOLUME"), ("vel_depth", "ACCENT"), ("comp", "COMP"))):
        x = 222 + i * 92
        for t in range(11):
            yy = 72 + 150 * t / 10
            p.add(line(x - 26, yy, x - 18, yy, "#9a9a9a", 1), line(x + 18, yy, x + 26, yy, "#9a9a9a", 1))
        p.slider(k, x, 147, 30, 150, l, img="hw_cr_cap.svg", base="hw_cr_tr.svg", lab=-102, vs=15)
    # programmable box: master section
    p.add(rect(490, 30, 340, 286, "none", rx=6, stroke="#e8e8e8", sw=2), rect(560, 22, 200, 18, "#191919"),
          T(660, 31, "MASTER", 12, OR, 700, sp=0.2))
    p.add(ticks(570, 120, 36, 42, 11, OR, 1.6), T(570, 64, "DRIVE", 11, INK, 700))
    p.knob("master_drive", 570, 120, 30, "DRIVE", img="hw_k78.svg")
    p.popup("master_dist", 740, 120, 150, 40, label="DISTORTION", accent=OR)
    p.add(T(590, 222, "HAT CHOKE", 11, INK, 700), T(740, 222, "NOTE MAP", 11, INK, 700))
    p.switch("hat_choke", 590, 270, 3, vertical=True, sw=110, sh=24)
    p.switch("note_map", 740, 262, 2, vertical=True, sw=110, sh=24)
    # accent-style knobs at the right: focus / mutes (the plugin's pad focus and mute mask)
    for x, k, l in ((930, "ui_focus", "FOCUS"), (1080, "mutes", "MUTES")):
        p.add(ticks(x, 240, 36, 42, 11, OR, 1.6), T(x, 186, l, 11, INK, 700))
        p.knob(k, x, 240, 30, l, img="hw_k78.svg")
    p.add(line(20, 330, 1260, 330, "#c9c9c9", 1.5))
    cr_row(p, "rhy_style", 412, False, "RHYTHM SELECTOR  I")
    cr_row(p, "rhy_style2", 544, True, "RHYTHM SELECTOR  II  (COMBINED)")
    p.qrow("rhy_style", "rhy_style2", "rhy_ab", "volume", "vel_depth", "comp", "master_drive", "hat_choke")
    p.qrow("rhy_mode", "master_dist", "note_map", "ui_focus", "mutes")
    pages = [p]

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
