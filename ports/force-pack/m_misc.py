"""Hardware pages for the small and the invented machines (hwpanel.Page): PO-32, Game Boy, 2-op FM (Hank), WeirdDrums,
PlayStation SPU reverb, Drum Buss, the sidechain ducker, the SVF filter and the cassette deck. Each names its
reference. No manufacturer logos: the panels carry the plugins' names."""
from hwpanel import (Page, T, rect, line, circle, path, ticks, dots, numbers, screw, hexscrew, led, brushed, grain, wood,
                     knob_img, svg_doc, pt, SANS, NARROW, ROUND)

MONO = "Liberation Mono, FreeMono, monospace"


# ---- PO-32 tonic (libpo32) ------------------------------------------------------------------------------------------
# Reference: the PO-32's published description (Sound On Sound review: "a surface-mounted screen and a 5 x 5 grid of
# controls, two of which are small pots") and the Pocket Operator layout: a bare circuit board, the segment LCD at
# the top, knobs A and B at the top right, sound / pattern / bpm along the top row, the 16 numbered keys in a 4 x 4
# grid with the special / play / fx / write column at the right, white silkscreen, gold pads. Here the LCD shows the
# kit, A and B are LEVEL and DECAY, and each numbered key carries its sound's level knob. A page per sound uses the
# same board: its twelve synthesis knobs on the key grid, as the PO-32 edits a sound with the keys and A/B.
PO_PCB, PO_INK, PO_PAD = "#1d201f", "#f2f2ee", "#c8a84a"


def po_board(p, title):
    p.add(rect(0, 0, 1280, 628, "#0a0a0a"), rect(150, 6, 980, 616, PO_PCB, rx=26), grain(150, 6, 980, 616))
    for x, y in ((176, 32), (1104, 32), (176, 596), (1104, 596)):
        p.add(circle(x, y, 11, PO_PAD), circle(x, y, 6, "#0a0a0a"))
    # traces
    p.add('<g stroke="#2e3431" stroke-width="3" fill="none">%s</g>' % "".join(
        '<path d="M%d %d h%d v%d"/>' % (180 + i * 61, 150, 30, 440 - i * 9) for i in range(15)))
    # LCD
    p.add(rect(200, 34, 480, 132, "#0d0f0e", rx=6), rect(212, 44, 456, 112, "#a9b4a6", rx=3),
          rect(212, 44, 456, 112, "url(#hw-vshade)", rx=3))
    p.add(T(186, 600, "libpo32", 22, PO_INK, 700, anchor="start", italic=True), T(1094, 600, title, 12, PO_INK, 700, anchor="end", sp=0.2))


GRID_X = [300, 450, 600, 750, 950]
GRID_Y = [250, 345, 440, 535]


def po_key(p, x, y, label, sub=""):
    p.add(rect(x - 50, y - 40, 100, 80, "none", rx=8, stroke="#4a504c", sw=1.5),
          T(x - 40, y - 30, label, 13, PO_INK, 700, anchor="start"), T(x + 40, y - 30, sub, 9, PO_INK, 700, anchor="end"))


def po_knob():
    return knob_img(body="#d8d8d4", edge="#555", cap="#efefea", cap_r=0.8, cap_edge="#888", line_c="#1a1a1a",
                    line=(0.2, 0.95), line_w=7, shine=0.3, rr=0.9)


def plibpo32(params):
    pages = []
    p = Page("PO-32", vink="#f2f2ee", lab=dict(size=12, fill=PO_INK, font=SANS, weight=700, sp=0.06))
    p.asset("po_k.svg", po_knob())
    po_board(p, "TONIC DRUM SYNTH")
    p.add(T(230, 62, "KIT", 13, "#2a302a", 700, anchor="start", font=MONO))
    p.readout("kit", 404, 108, 290, 64, "")
    p.knob("kit", 616, 102, 24, "KIT", img="hw_po_k.svg", vs=14, dup=True, bw=100)
    # A / B
    for x, k, l in ((800, "level", "A  LEVEL"), (950, "decay", "B  DECAY")):
        p.add(T(x, 46, l, 13, PO_INK, 700), circle(x, 108, 40, "none", "#4a504c", 1.5))
        p.knob(k, x, 108, 30, l, img="hw_po_k.svg", vs=15)
    for i in range(16):
        x, y = GRID_X[i % 4], GRID_Y[i // 4]
        po_key(p, x, y, str(i + 1))
        p.knob("v%02d_lvl" % (i + 1), x, y - 2, 22, str(i + 1), img="hw_po_k.svg", vs=13, bw=96)
    for y, s in zip(GRID_Y, ("special", "play", "fx", "write")):
        p.add(rect(GRID_X[4] - 50, y - 40, 100, 80, "none", rx=8, stroke="#4a504c", sw=1.5),
              rect(GRID_X[4] - 22, y - 12, 44, 30, "#e4e4de", rx=4, stroke="#777"), T(GRID_X[4], y - 26, s, 12, PO_INK, 700))
    p.add(T(1040, 62, "sound", 11, PO_INK, 700), rect(1022, 74, 36, 26, "#e4e4de", rx=4, stroke="#777"),
          T(1040, 128, "pattern", 11, PO_INK, 700), rect(1022, 140, 36, 26, "#e4e4de", rx=4, stroke="#777"))
    p.qrow("level", "decay", "kit")
    p.qrow(*["v%02d_lvl" % (i + 1) for i in range(16)])
    pages.append(p)
    rows = [[("freq", "PITCH"), ("mrate", "MOD RATE"), ("mamt", "MOD AMT"), ("mix", "NOISE MIX")],
            [("atk", "ATTACK"), ("dcy", "DECAY"), ("nffrq", "NOISE FREQ"), ("nfq", "NOISE Q")],
            [("neatk", "N ATTACK"), ("nedcy", "N DECAY"), ("dist", "DISTORT"), ("lvl", "LEVEL")]]
    for v in range(1, 17):
        k = "v%02d_" % v
        p = Page("%d" % v, vink="#f2f2ee", lab=dict(size=12, fill=PO_INK, font=SANS, weight=700, sp=0.06))
        p.asset("po_k.svg", po_knob())
        po_board(p, "SOUND %d" % v)
        p.add(T(440, 100, "SOUND %02d" % v, 40, "#2a302a", 700, font=MONO))
        for r, row in enumerate(rows):
            for c, (suf, l) in enumerate(row):
                x, y = GRID_X[c], GRID_Y[r]
                po_key(p, x, y, l)
                p.knob(k + suf, x, y + 2, 24, l, img="hw_po_k.svg", vs=13, bw=96)
        for c in range(4):
            po_key(p, GRID_X[c], GRID_Y[3], str(12 + c + 1))
        p.qrow(*[k + s for s, _ in rows[0]] + [k + s for s, _ in rows[1]])
        p.qrow(*[k + s for s, _ in rows[2]])
        pages.append(p)
    return pages


# ---- Game Boy (Chiptune) -----------------------------------------------------------------------------------------------
# Reference: Wikimedia Commons "Game-Boy-Original.jpg" (the DMG): grey case, the dark screen bezel with the purple /
# blue / red lines and the battery lamp, the green dot-matrix screen, the cross key, the magenta A and B, the
# SELECT / START pills and the speaker slots. Turned on its side so it fills the width: the screen holds the sound
# controls (drawn in the LCD's four greens), the cross key is OCTAVE / VOICES, A and B the noise mode and chip.
GB_CASE, GB_INK, GB_BEZ = "#c6c3bd", "#2a2a6e", "#5b5d6c"
LCD = ["#0f380f", "#306230", "#8bac0f", "#9bbc0f"]


def lcd_knob():
    return svg_doc(96, 96, "".join(rect(48 + x * 6 - 3, 48 + y * 6 - 3, 6, 6, LCD[0]) for x in range(-7, 8) for y in range(-7, 8)
                                   if 5.5 <= (x * x + y * y) ** 0.5 <= 7.4) +
                   "".join(rect(45, 48 - i * 6 - 3, 6, 6, LCD[0]) for i in range(1, 6)))


def pchip(params):
    p = Page("CHIPTUNE", vink=LCD[0], lab=dict(size=12, fill=LCD[0], font=MONO, weight=700, sp=0.04), seg_text=True)
    p.asset("gb_k.svg", lcd_knob())
    p.add(rect(0, 0, 1280, 628, "#8d8a84"), rect(6, 4, 1268, 620, GB_CASE, rx=22), grain(6, 4, 1268, 620),
          rect(6, 4, 1268, 620, "url(#hw-vshade)", rx=22))
    # screen bezel + LCD
    p.add(path("M30 22 H860 Q890 22 890 52 V560 Q890 600 830 606 H50 Q30 606 30 586 Z", "#5b5d6c"),
          rect(70, 40, 680, 4, "#8a2a6a"), rect(70, 48, 680, 4, "#2b3a8a"),
          T(410, 46, " DOT MATRIX WITH STEREO SOUND ", 13, "#d8d8e0", 700, sp=0.06, extra=' style="paint-order:stroke"'),
          led(56, 200, 6, "#ff3a22", lit=True), T(56, 226, "BATTERY", 8, "#d8d8e0", 700))
    p.add(rect(90, 70, 760, 500, LCD[3]), rect(90, 70, 760, 500, "url(#hw-vshade)"))
    for i in range(0, 760, 4):
        p.add(line(90 + i, 70, 90 + i, 570, LCD[2], 0.4))

    def K(k, x, y, l):
        p.knob(k, x, y, 24, l, img="hw_gb_k.svg", lab=-40, vs=15, font=MONO)

    p.add(rect(100, 80, 740, 26, LCD[0]), T(470, 93, "CHIPTUNE  -  SOUND", 14, LCD[3], 700, font=MONO, sp=0.1))
    rows = [[("duty", "DUTY"), ("wavetable", "WAVE"), ("sweep", "SWEEP"), ("detune", "DETUNE"), ("channel_mask", "CHANNELS"), ("volume", "VOLUME")],
            [("env_attack", "ATTACK"), ("env_decay", "DECAY"), ("env_sustain", "SUSTAIN"), ("env_release", "RELEASE")],
            [("vibrato_depth", "VIB DEPTH"), ("vibrato_rate", "VIB RATE"), ("pitch_env_depth", "PENV DEPTH"), ("pitch_env_speed", "PENV SPEED")]]
    for r, row in enumerate(rows):
        for c, (k, l) in enumerate(row):
            K(k, 160 + c * 124, 180 + r * 140, l)
    p.add(rect(612, 300, 220, 250, "none", stroke=LCD[0], sw=3), T(722, 320, "VOICES", 13, LCD[0], 700, font=MONO))
    p.switch("alloc_mode", 722, 400, 3, vertical=True, sw=180, sh=30)
    p.add(T(722, 470, "- - - - -", 12, LCD[1], 700, font=MONO))
    # controls side
    p.add(T(1080, 52, "Chiptune", 34, "#2b2d8c", 700, italic=True, font=SANS))
    cx, cy = 1000, 240
    p.add(rect(cx - 20, cy - 62, 40, 124, "#222", rx=5), rect(cx - 62, cy - 20, 124, 40, "#222", rx=5),
          circle(cx, cy, 10, "#333"), T(cx, cy - 88, "OCTAVE", 12, GB_INK, 700, sp=0.1))
    p.knob("octave_transpose", cx, cy, 30, "OCTAVE", img="hw_gb_dk.svg", vs=16, bw=120)
    p.asset("gb_dk.svg", svg_doc(96, 96, '<circle cx="48" cy="48" r="20" fill="#2a2a2a" stroke="#000"/>'
                                         '<path d="M48 16 l-8 12 h16 Z" fill="#555"/>'))
    for x, y, k, l in ((1210, 190, "chip", "B"), (1130, 250, "noise_mode", "A")):
        p.add(circle(x, y, 34, "#a13a6a", "#5a1a3a", 2), circle(x - 8, y - 10, 12, "#fff", extra=' opacity="0.2"'),
              T(x, y + 50, l, 18, GB_INK, 700, font=SANS, italic=True))
    p.add(T(1210, 132, "CHIP", 11, GB_INK, 700), T(1130, 192, "NOISE", 11, GB_INK, 700))
    p.switch("chip", 1210, 190, 2, vertical=True, sw=60, sh=26)
    p.switch("noise_mode", 1130, 250, 2, vertical=True, sw=60, sh=26)
    for x, s in ((1010, "SELECT"), (1110, "START")):
        p.add(rect(x - 30, 400, 60, 16, "#8a8a92", rx=8, extra=' transform="rotate(-25 %d 408)"' % x), T(x, 440, s, 12, GB_INK, 700, sp=0.1))
    for i in range(6):
        x = 1080 + i * 26
        p.add(rect(x, 480, 10, 110, "#9a978f", rx=5, extra=' transform="rotate(-30 %d 535)"' % x))
    p.qrow("duty", "wavetable", "sweep", "detune", "channel_mask", "volume", "octave_transpose", "alloc_mode")
    p.qrow("env_attack", "env_decay", "env_sustain", "env_release", "vibrato_depth", "vibrato_rate", "pitch_env_depth", "pitch_env_speed")
    return [p]


# ---- PlayStation SPU reverb (PSX Verb) --------------------------------------------------------------------------------
# Reference: the original grey PlayStation (SCPH-100x) seen from above: the round disc lid with its ridges, the OPEN,
# POWER and RESET buttons, the four face-button symbols, the controller ports along the front. The SPU's reverb
# presets are the six mode buttons; the disc in the lid is the DECAY knob (it turns), MIX / INPUT / LEVEL sit by the
# buttons.
PS_GREY, PS_DARK, PS_INK = "#c9c8c4", "#8e8d89", "#3a3a44"


def disc_knob():
    rings = "".join('<circle cx="48" cy="48" r="%g" fill="none" stroke="#fff" stroke-opacity="%g" stroke-width="0.7"/>' % (r, 0.1 + 0.02 * (r % 5))
                    for r in range(16, 46, 2))
    return svg_doc(96, 96, '<defs><linearGradient id="d" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d9dde8"/>'
                   '<stop offset="0.35" stop-color="#9fb7d8"/><stop offset="0.55" stop-color="#e8c8e0"/><stop offset="0.75" stop-color="#b8e0c8"/>'
                   '<stop offset="1" stop-color="#8a90a0"/></linearGradient></defs>'
                   '<circle cx="48" cy="48" r="46" fill="url(#d)" stroke="#555" stroke-width="1"/>' + rings +
                   '<circle cx="48" cy="48" r="12" fill="#ececec" stroke="#999"/><circle cx="48" cy="48" r="5" fill="#2a2a2a"/>'
                   '<rect x="44" y="4" width="8" height="18" rx="3" fill="#2a2a44"/>')


def ps_knob():
    return knob_img(body="#8e8d89", edge="#555", cap="#bdbcb8", cap_r=0.78, cap_edge="#777", line_c="#3a3a44",
                    line=(0.2, 0.95), line_w=7, shine=0.3, rr=0.9)


def ppsx(params):
    p = Page("PSX VERB", vink=PS_INK, lab=dict(size=13, fill=PS_INK, font=SANS, weight=700, sp=0.08), seg_text=True)
    p.asset("ps_disc.svg", disc_knob())
    p.asset("ps_k.svg", ps_knob())
    p.add(rect(0, 0, 1280, 628, "#6d6c68"), rect(8, 8, 1264, 612, PS_GREY, rx=28), grain(8, 8, 1264, 612),
          rect(8, 8, 1264, 612, "url(#hw-vshade)", rx=28))
    # lid
    cx, cy = 380, 300
    p.add(circle(cx, cy, 268, "#b9b8b4", "#9c9b97", 3), circle(cx, cy, 250, "none", "#d8d7d3", 2))
    for r in range(70, 250, 14):
        p.add(circle(cx, cy, r, "none", "#aeada9", 1))
    p.add(circle(cx, cy, 118, "#2a2a2e"), T(cx, cy - 150, "DECAY", 16, PS_INK, 700, sp=0.2))
    p.knob("decay", cx, cy, 56, "DECAY", img="hw_ps_disc.svg", bw=160, vs=20)
    p.add(T(cx, 590, "PSX VERB", 16, PS_INK, 700, sp=0.4))
    # buttons
    for x, y, s in ((760, 92, "POWER"), (900, 92, "RESET")):
        p.add(rect(x - 46, y - 18, 92, 36, "#a9a8a4", rx=18, stroke="#7d7c78"), T(x, y + 32, s, 11, PS_INK, 700))
    p.add(circle(1120, 92, 30, "#a9a8a4", "#7d7c78"), T(1120, 136, "OPEN", 11, PS_INK, 700))
    p.add('<g transform="translate(1000 196)" fill="none" stroke-width="3">'
          '<path d="M-58,10 L-46,-10 L-34,10 Z" stroke="#2fa87a"/><circle cx="-8" cy="0" r="11" stroke="#d6383a"/>'
          '<path d="M18,-10 L38,10 M38,-10 L18,10" stroke="#4a78c8"/><rect x="50" y="-10" width="20" height="20" stroke="#d47ab0"/></g>')
    p.add(T(870, 250, "REVERB MODE", 13, PS_INK, 700, sp=0.14))
    p.switch("model", 870, 390, 6, vertical=True, sw=200, sh=38)
    for i, (k, l) in enumerate((("mix", "MIX"), ("input_gain", "INPUT"), ("reverb_level", "LEVEL"))):
        y = 300 + i * 112
        p.add(T(1120, y - 42, l, 12, PS_INK, 700))
        p.knob(k, 1120, y, 28, l, img="hw_ps_k.svg", bw=150)
    for x in (760, 980):   # controller ports
        p.add(rect(x - 70, 590, 140, 28, "#3a3a3a", rx=8))
    p.qrow("decay", "mix", "input_gain", "reverb_level", "model")
    return [p]


# ---- Drum Buss (Bus Driver) -------------------------------------------------------------------------------------------
# Reference: Ableton Live's Drum Buss device (the plugin's model): the dark device panel with DRIVE and its
# Soft / Medium / Hard selector, COMP and TRIM on the left; CRUNCH, DAMP and TRANSIENTS in the middle; the yellow BOOM
# section (BOOM, FREQ, DECAY) on the right; OUTPUT and DRY/WET at the end; flat knobs with value arcs.
def pbus(params):
    BG, INK, DIM, OR, YEL = "#1f1f1f", "#d6d6d6", "#8a8a8a", "#ff764d", "#e8d44a"
    p = Page("DRUM BUSS", vink="#ffb08a", lab=dict(size=14, fill=INK, font=SANS, weight=700, sp=0.04), seg_text=True)
    p.add(rect(0, 0, 1280, 628, "#121212"), rect(10, 10, 1260, 608, BG, rx=6), rect(10, 10, 1260, 46, "#2a2a2a", rx=6),
          T(32, 33, "Bus Driver", 20, INK, 700, anchor="start"), T(1248, 33, "DRUM BUSS", 13, DIM, 700, anchor="end", sp=0.2))
    secs = [(20, 330, ""), (340, 680, ""), (690, 1060, "BOOM"), (1070, 1260, "")]
    for a, b, n in secs:
        p.add(rect(a, 66, b - a, 540, "#262626", rx=6))
    p.add(rect(690, 66, 370, 540, "#2b2a1c", rx=6), T(875, 96, "BOOM", 16, YEL, 700, sp=0.2))

    def K(k, x, y, r, l, lab=None):
        p.knob(k, x, y, r, l, lab=-(r + 22) if lab is None else lab)

    K("drive", 120, 220, 56, "DRIVE")
    p.add(T(260, 120, "TYPE", 12, DIM, 700))
    p.switch("drive_type", 260, 196, 3, vertical=True, sw=100, sh=34)
    p.add(T(110, 400, "COMP", 12, DIM, 700))
    p.switch("comp", 110, 450, 2, vertical=False, sw=60, sh=34)
    K("trim", 250, 450, 32, "TRIM")
    for i, (k, l) in enumerate((("crunch", "CRUNCH"), ("damp", "DAMP"), ("transients", "TRANSIENTS"))):
        K(k, 510, 160 + i * 150, 38, l)
    K("boom", 875, 240, 58, "BOOM")
    K("boom_freq", 790, 470, 34, "FREQ")
    K("boom_decay", 960, 470, 34, "DECAY")
    K("output", 1165, 200, 38, "OUTPUT")
    K("drywet", 1165, 420, 38, "DRY/WET")
    p.qrow("drive", "trim", "crunch", "damp", "transients", "boom", "boom_freq", "boom_decay")
    p.qrow("output", "drywet", "drive_type", "comp")
    return [p]


# ---- Ducker -----------------------------------------------------------------------------------------------------------
# A sidechain utility has no hardware of its own; it is drawn as a 2U studio rack unit of the classic gain-reduction
# kind: brushed black faceplate with rack ears, a lit gain-reduction VU, the TRIGGER section (MIDI channel, note, mode)
# and the SHAPE section (DEPTH, CURVE, ATTACK, HOLD, RELEASE), velocity sensitivity at the end.
def pduck(params):
    INK, AMB = "#e6e6e2", "#f2a43a"
    p = Page("DUCKER", vink=AMB, lab=dict(size=12, fill=INK, font=SANS, weight=700, sp=0.1), seg_text=True)
    p.asset("dk_k.svg", knob_img(body="#d8d8d6", edge="#555", knurl="#b8b8b6", knurl_n=40, cap="#efefed", cap_r=0.7,
                                 cap_edge="#888", line_c="#1a1a1a", line=(0.25, 0.95), line_w=6, shine=0.3, rr=0.92))
    p.add(rect(0, 0, 1280, 628, "#0c0c0c"), brushed(0, 60, 1280, 508, "#1d1e20", dark=True),
          rect(0, 60, 1280, 508, "url(#hw-vshade)"))
    for x in (8, 1236):
        p.add(rect(x, 60, 36, 508, "#26272a"))
        for y in (110, 520):
            p.add(rect(x + 8, y - 12, 20, 24, "#050505", rx=10))
    p.add(T(70, 100, "DUCKER", 30, INK, 700, anchor="start", sp=0.16), T(70, 128, "SIDECHAIN GAIN REDUCTION", 11, "#9a9a9a", 700, anchor="start", sp=0.2))
    # VU
    p.add(rect(980, 80, 240, 150, "#111", rx=4), rect(990, 90, 220, 130, "#f3d79a", rx=3),
          path("M1020 196 A 100 100 0 0 1 1180 196", stroke="#2a2a2a", sw=1.5), T(1100, 206, "GAIN REDUCTION", 9, "#2a2a2a", 700),
          line(1100, 214, 1150, 120, "#111", 2))
    for i, s in enumerate(("0", "-3", "-6", "-10", "-20")):
        x, y = pt(1100, 214, 92, 50 - i * 25)
        p.add(T(x, y, s, 9, "#2a2a2a", 700))
    p.add(rect(60, 250, 360, 290, "none", rx=6, stroke="#4a4a4a"), T(240, 268, "TRIGGER", 13, AMB, 700, sp=0.3),
          rect(440, 160, 520, 380, "none", rx=6, stroke="#4a4a4a"), T(700, 178, "SHAPE", 13, AMB, 700, sp=0.3))
    p.popup("channel", 150, 340, 140, 40, label="MIDI CH", accent=AMB)
    p.popup("trigger_note", 330, 340, 140, 40, label="NOTE", accent=AMB)
    p.add(T(240, 410, "MODE", 11, INK, 700))
    p.switch("mode", 240, 450, 2, vertical=False, sw=120, sh=34)
    p.knob("depth", 560, 300, 50, "DEPTH", img="hw_dk_k.svg", lab=-72)
    p.add(T(580, 440, "CURVE", 11, INK, 700))
    p.switch("curve", 580, 480, 4, vertical=False, sw=64, sh=30)
    for i, (k, l) in enumerate((("attack", "ATTACK"), ("hold", "HOLD"), ("release", "RELEASE"))):
        p.knob(k, 720 + i * 100, 300 if i != 1 else 450, 34, l, img="hw_dk_k.svg", lab=-56)
    p.knob("vel_sens", 1100, 420, 34, "VEL SENS", img="hw_dk_k.svg", lab=-56)
    p.qrow("depth", "attack", "hold", "release", "vel_sens", "curve", "mode", "channel")
    return [p]


# ---- Multimode state-variable filter (FILTER) ---------------------------------------------------------------------------
# Reference: the Oberheim SEM, the classic hardware state-variable filter: brushed aluminium module, black legends in
# boxed sections, small black knobs with silver skirts, the VCF's continuously variable mode control. Here: VCF
# (FREQUENCY, RESONANCE, the MODE selector as a rotary over LP / HP / BP / NOTCH / PEAK / AP, the SVF / ladder model
# switch), ENV (AMOUNT, ATTACK, RELEASE), LFO (AMOUNT, RATE or the synced division, SHAPE, SYNC) and the output
# stage (DRIVE, MIX, OUTPUT). Wood side cheeks as on the SEM's desktop case.
def sem_knob(angle=None):
    s = knob_img(body="#d2d4d6", edge="#666", knurl="#a8aaac", knurl_n=36, cap="#151515", cap_r=0.72, cap_edge="#000",
                 line_c="#f2f2f2", line=(0.05, 0.7), line_w=6, shine=0.25, rr=0.92)
    if angle is None:
        return s
    i = s.rindex("<line")
    return s[:i] + '<g transform="rotate(%g 48 48)">' % angle + s[i:-6] + "</g></svg>"


def pfilter(params):
    INK = "#161616"
    p = Page("FILTER", vink="#1a1a1a", lab=dict(size=13, fill=INK, font=SANS, weight=700, sp=0.06), seg_text=True)
    p.asset("sem_k.svg", sem_knob())
    p.add(wood(0, 0, 40, 628), wood(1240, 0, 40, 628), brushed(40, 0, 1200, 628, "#cfd1d2"),
          rect(40, 0, 1200, 628, "url(#hw-vshade)"))
    for x in (60, 1220):
        for y in (22, 606):
            p.add(screw(x, y, 6))
    p.add(T(640, 40, "FILTER", 30, INK, 700, sp=0.3), T(640, 70, "MULTIMODE STATE VARIABLE", 12, INK, 700, sp=0.3))

    def box(x0, y0, x1, y1, n):
        p.add(rect(x0, y0, x1 - x0, y1 - y0, "none", stroke=INK, sw=2), rect((x0 + x1) / 2 - len(n) * 6 - 10, y0 - 12, len(n) * 12 + 20, 24, "#cfd1d2"),
              T((x0 + x1) / 2, y0, n, 16, INK, 700, sp=0.2))

    def K(k, x, y, l, r=30, **kw):
        p.add(ticks(x, y, r + 6, r + 12, 11, INK, 1.4))
        p.knob(k, x, y, r, l, img="hw_sem_k.svg", lab=-(r + 26), **kw)

    box(70, 110, 640, 590, "VCF")
    K("cutoff", 200, 230, "FREQUENCY", r=50)
    K("resonance", 200, 450, "RESONANCE", r=36)
    modes = ["LP", "HP", "BP", "NOTCH", "PEAK", "AP"]
    ang = [-120 + 48 * i for i in range(6)]
    p.add(T(470, 150, "MODE", 13, INK, 700))
    for a, m in zip(ang, modes):
        x, y = pt(470, 240, 70, a)
        p.add(T(x, y, m, 11, INK, 700), line(*pt(470, 240, 50, a), *pt(470, 240, 57, a), INK, 2))
    p.rotary("mode", 470, 240, 40, 6, sem_knob, angles=ang, field_w=120, field_dy=92, accent="#1a1a1a")
    p.add(T(470, 404, "MODEL", 12, INK, 700))
    p.switch("model", 470, 450, 2, vertical=False, sw=96, sh=34)
    box(670, 110, 940, 590, "ENV")
    K("env_amount", 805, 230, "AMOUNT", r=36)
    K("env_attack", 740, 450, "ATTACK", r=28)
    K("env_release", 870, 450, "RELEASE", r=28)
    box(970, 110, 1210, 590, "LFO")
    K("lfo_amount", 1030, 200, "AMOUNT", r=26)
    K("lfo_rate_hz", 1150, 200, "RATE", r=26, when="lfo_sync:0")
    p.popup("lfo_rate_div", 1150, 210, 100, 40, label="DIVISION", accent="#1a1a1a")
    p.ctl[-1]["when"] = "lfo_sync:1"
    p.add(T(1030, 300, "SHAPE", 12, INK, 700), T(1150, 300, "SYNC", 12, INK, 700))
    p.popup("lfo_shape", 1030, 350, 100, 40, label="", accent="#1a1a1a")
    p.switch("lfo_sync", 1150, 350, 2, vertical=True, sw=90, sh=30)
    p.add(rect(980, 420, 220, 160, "none", stroke=INK, sw=1.2), T(1090, 434, "OUTPUT", 12, INK, 700, sp=0.2))
    for i, (k, l) in enumerate((("drive", "DRIVE"), ("mix", "MIX"), ("output", "OUTPUT"))):
        p.knob(k, 1018 + i * 72, 510, 20, l, img="hw_sem_k.svg", lab=-34, size=10, vs=14)
    p.qrow("cutoff", "resonance", "mode", "env_amount", "env_attack", "env_release", "lfo_amount", "lfo_rate_hz")
    p.qrow("drive", "mix", "output", "model", "lfo_shape", "lfo_sync", "lfo_rate_div")
    return [p]


# ---- Cassette deck (TAPESCAM) -------------------------------------------------------------------------------------------
# Reference: a 1980s front-loading hi-fi cassette deck: brushed silver front, the cassette well with its window (two
# reels and the tape), the piano-key transport, a pair of lit VU meters, TAPE (type) selector, NOISE REDUCTION
# selector, MPX filter switch, and the REC LEVEL / OUTPUT LEVEL knobs. Mapped to the plugin: TAPE = age (NEW / USED /
# WORN), SPEED (HIGH / STD / LOW), NR = compression (OFF / LITE / HEAVY), WIDE = stereo widen; INPUT and OUTPUT are the
# level knobs; DRIVE, COLOR, WOBBLE, NOISE and TONE are the deck's adjustment row.
def reel(cx, cy, r, ang=0):
    o = circle(cx, cy, r, "#2a2420") + circle(cx, cy, r * 0.42, "#e8e4da", "#999")
    for a in range(0, 360, 60):
        x, y = pt(cx, cy, r * 0.3, a + ang)
        o += line(cx, cy, x, y, "#777", 3)
    return o + circle(cx, cy, r * 0.12, "#555")


def ptapescam(params):
    INK = "#161616"
    p = Page("TAPESCAM", vink="#1a1a1a", lab=dict(size=12, fill=INK, font=SANS, weight=700, sp=0.08), seg_text=True)
    p.asset("tc_k.svg", knob_img(body="metal", edge="#555", knurl="#8a8c8e", knurl_n=48, cap="metal", cap_r=0.6, cap_edge="#777",
                                 line_c="#222", line=(0.3, 0.95), line_w=5, shine=0.2, rr=0.92))
    p.add(rect(0, 0, 1280, 628, "#2a2a2a"), brushed(8, 8, 1264, 612, "#c4c6c8"), rect(8, 8, 1264, 612, "url(#hw-vshade)"))
    p.add(T(40, 44, "TAPESCAM", 26, INK, 700, anchor="start", sp=0.12), T(40, 70, "STEREO CASSETTE DECK", 11, INK, 700, anchor="start", sp=0.3))
    # cassette well
    p.add(rect(40, 96, 520, 300, "#1b1b1b", rx=8), rect(56, 112, 488, 268, "#2a2826", rx=4),
          rect(110, 150, 380, 190, "#d9d2bf", rx=8, stroke="#555"), rect(130, 168, 340, 40, "#e9e3d0"),
          T(300, 188, "C-60   TYPE I  NORMAL", 12, "#333", 700, sp=0.1), rect(170, 226, 260, 80, "#1a1612", rx=30),
          reel(220, 266, 34, 10), reel(380, 266, 34, 40), rect(258, 250, 84, 30, "#3a2a1c"),
          rect(56, 112, 488, 268, "#fff", rx=4, extra=' opacity="0.06"'))
    # transport keys
    keys = ["REC", "◀◀", "▶", "▶▶", "■", "❚❚"]
    for i, s in enumerate(keys):
        x = 56 + i * 82
        p.add(rect(x, 420, 76, 46, "#2c2c2c" if s != "REC" else "#8a1a14", rx=3, stroke="#000"),
              rect(x + 3, 423, 70, 12, "#fff", rx=2, extra=' opacity="0.12"'), T(x + 38, 448, s, 16, "#eee", 700))
    p.add(T(300, 500, "COUNTER", 10, INK, 700), rect(240, 512, 120, 34, "#111", rx=3), T(300, 529, "0 4 2", 18, "#e8e8e8", 700, font=MONO))
    # VU meters
    for i, ch in enumerate(("L", "R")):
        x = 610 + i * 200
        p.add(rect(x, 96, 186, 120, "#111", rx=4), rect(x + 8, 104, 170, 104, "#f2d48a", rx=3),
              path("M%g 190 A 80 80 0 0 1 %g 190" % (x + 25, x + 161), stroke="#2a2a2a", sw=1.4),
              path("M%g 152 A 80 80 0 0 1 %g 190" % (x + 120, x + 161), stroke="#c8261a", sw=4),
              T(x + 93, 196, "VU  " + ch, 10, "#2a2a2a", 700), line(x + 93, 206, x + 50, 130, "#111", 1.6))
    p.add(T(1110, 110, "TAPE", 11, INK, 700))
    p.switch("age", 1110, 170, 3, vertical=True, sw=110, sh=30)
    p.add(T(1110, 236, "SPEED", 11, INK, 700))
    p.switch("speed", 1110, 296, 3, vertical=True, sw=110, sh=30)
    p.add(T(700, 250, "NOISE REDUCTION", 11, INK, 700))
    p.switch("compression", 700, 290, 3, vertical=False, sw=70, sh=30)
    p.add(T(930, 250, "MPX / WIDE", 11, INK, 700))
    p.switch("widen", 930, 290, 2, vertical=False, sw=70, sh=30)
    for i, (k, l) in enumerate((("input", "REC LEVEL"), ("output", "OUTPUT LEVEL"))):
        x = 700 + i * 230
        p.add(ticks(x, 410, 38, 44, 11, INK, 1.4))
        p.knob(k, x, 410, 32, l, img="hw_tc_k.svg", lab=-58)
    p.add(rect(600, 490, 650, 116, "none", rx=4, stroke="#777"), T(925, 502, "ADJUST", 10, INK, 700, sp=0.3))
    for i, (k, l) in enumerate((("drive", "DRIVE"), ("color", "COLOR"), ("wobble", "WOBBLE"), ("noise", "HISS"), ("tone", "TONE"))):
        p.knob(k, 660 + i * 130, 548, 20, l, img="hw_tc_k.svg", lab=-32, size=10, vs=14)
    p.qrow("input", "drive", "color", "wobble", "noise", "tone", "output", "age")
    p.qrow("speed", "compression", "widen")
    return [p]


# ---- 2-operator FM (Hank) ---------------------------------------------------------------------------------------------
# Reference: the Yamaha DX family (DX7 / DX100), the hardware face of FM: dark brown panel, VOLUME and DATA ENTRY
# sliders with cream caps, the green character LCD, membrane fields in maroon and teal with white legends, the
# printed algorithm chart (here the plugin's one algorithm: a modulator over a carrier). The LCD shows the operator
# ratio (tap it for the list); the maroon field is the operator (BRIGHT = modulation index, BITE, TONE), the teal
# field the envelope, then NOISE and the voice settings. DATA ENTRY is the pitch.
def phank(params):
    BR, INK, MAR, TEAL, CREAM = "#3a332d", "#efe7da", "#7d2f3e", "#2f7f76", "#ece4cf"
    p = Page("HANK", vink="#f2e6c8", lab=dict(size=12, fill=INK, font=SANS, weight=700, sp=0.08), seg_text=True)
    p.asset("hk_k.svg", knob_img(body="#1d1a17", edge="#000", knurl="#2c2824", knurl_n=24, cap="#2a2622", cap_r=0.74,
                                 line_c=CREAM, line=(0.1, 0.92), line_w=6, shine=0.2, rr=0.9))
    p.asset("hk_tr.svg", svg_doc(36, 240, rect(15, 0, 6, 240, "#0d0b09", rx=2)))
    p.asset("hk_cap.svg", svg_doc(36, 30, rect(1, 1, 34, 28, CREAM, rx=3, stroke="#555") + rect(1, 13, 34, 3, "#444")))
    p.add(rect(0, 0, 1280, 628, "#16130f"), rect(8, 8, 1264, 612, BR, rx=6), grain(8, 8, 1264, 612),
          rect(8, 8, 1264, 46, "#2b2621", rx=6))
    p.add(T(30, 32, "HANK", 26, INK, 700, anchor="start", sp=0.25),
          T(1250, 32, "DIGITAL 2-OPERATOR FM SYNTHESIZER", 13, INK, 700, anchor="end", sp=0.18))
    # sliders
    for x, k, l in ((70, "volume", "VOLUME"), (170, "pitch", "DATA ENTRY")):
        p.add(T(x, 92, l, 11, INK, 700))
        for t in range(11):
            yy = 128 + 220 * t / 10
            p.add(line(x - 30, yy, x - 22, yy, "#8a8076", 1))
        p.slider(k, x, 238, 36, 240, l, img="hw_hk_cap.svg", base="hw_hk_tr.svg", vs=15)
    p.add(T(170, 420, "PITCH", 10, "#a89c8a", 700))
    # LCD with the ratio
    p.add(rect(250, 74, 420, 130, "#141210", rx=6), rect(266, 88, 388, 102, "#8fae5a", rx=3),
          rect(266, 88, 388, 102, "url(#hw-vshade)", rx=3), T(280, 108, "RATIO  (MODULATOR : CARRIER)", 12, "#1d2a10", 700, anchor="start", font=MONO))
    p.popup("ratio", 460, 158, 360, 44, label="", field=False, accent="#1d2a10")
    # algorithm chart
    p.add(rect(700, 74, 200, 130, "#2b2621", rx=4, stroke="#6a5f52"), T(800, 90, "ALGORITHM", 11, INK, 700),
          rect(780, 112, 40, 28, "none", stroke=INK, sw=2), T(800, 126, "2", 14, INK, 700),
          line(800, 140, 800, 156, INK, 2), rect(780, 156, 40, 28, "none", stroke=INK, sw=2), T(800, 170, "1", 14, INK, 700),
          path("M820 120 h14 v-14 h-34 v6", stroke=INK, sw=1.5), line(760, 194, 840, 194, INK, 2))
    p.add(rect(930, 74, 320, 130, "#2b2621", rx=4, stroke="#6a5f52"), T(1090, 90, "MEMORY", 11, INK, 700))
    p.knob("preset", 1090, 146, 30, "PRESET", img="hw_hk_k.svg", vs=16, bw=160)
    # membrane fields with knobs
    fields = [("OPERATOR", MAR, 250, 640, [("bright", "BRIGHT"), ("bite", "BITE"), ("tone", "TONE")]),
              ("ENVELOPE", TEAL, 660, 1050, [("attack", "ATTACK"), ("decay", "DECAY"), ("sustain", "SUSTAIN")]),
              ("NOISE", MAR, 1070, 1250, [("noise", "NOISE")])]
    for n, c, a, b, ks in fields:
        p.add(rect(a, 236, b - a, 170, c, rx=4), T((a + b) / 2, 254, n, 13, "#fff", 700, sp=0.2))
        for i, (k, l) in enumerate(ks):
            x = a + (b - a) * (i + 0.5) / len(ks)
            p.knob(k, x, 330, 32, l, img="hw_hk_k.svg", lab=-50)
    p.add(rect(250, 430, 1000, 170, TEAL, rx=4), T(750, 448, "VOICE", 13, "#fff", 700, sp=0.2))
    for i, (k, l) in enumerate((("voice_count", "VOICES"), ("glide", "PORTAMENTO"))):
        p.knob(k, 420 + i * 320, 524, 32, l, img="hw_hk_k.svg", lab=-50)
    for i in range(16):   # the DX membrane switch row (printed)
        x, y = 880 + (i % 8) * 44, 490 + (i // 8) * 56
        p.add(rect(x - 18, y - 16, 36, 32, "#3d8c82" if i < 8 else "#8a3a4a", rx=2, stroke="#1a1a1a"),
              T(x, y, str(i + 1), 12, "#fff", 700))
    p.add(T(1034, 458, "INTERNAL  MEMORY", 10, "#fff", 700, sp=0.2))
    p.qrow("volume", "pitch", "ratio", "preset", "bright", "bite", "tone", "noise")
    p.qrow("attack", "decay", "sustain", "voice_count", "glide")
    return [p]


# ---- WeirdDrums (Weird Dreams) ------------------------------------------------------------------------------------------
# No hardware exists, so this is drawn as a boutique 8-voice analog drum machine in the family of the Vermona DRM /
# Jomox style: a matte black steel panel with a colour per voice, channel strips with long faders, PAN / REV / DLY
# pots and a rubber trigger pad with its LED at the foot, the master strip at the right (MASTER fader, COMP, DJ
# FILTER). Each voice has an editor page with the same panel: OSC, NOISE, FILTER, AMP, LFO sections and the voice's
# colour, a row of voice LEDs marking which one is open. FX, KIT and SELECTED (the voice under focus) follow suit.
WD_BG, WD_INK = "#151417", "#e9e6ef"
WD_COL = ["#ff4f6a", "#ff8a3a", "#f2c63a", "#7ad15a", "#36c9c3", "#3a8ff2", "#8a6af2", "#e05ad8"]


def wd_knob(c):
    return knob_img(body="#232126", edge="#000", knurl="#2f2c33", knurl_n=28, cap="#2a2730", cap_r=0.74, cap_edge="#0a0a0a",
                    line_c=c, line=(0.05, 0.95), line_w=7, shine=0.2, rr=0.9)


def wd_base(p, title):
    p.add(rect(0, 0, 1280, 628, "#0b0a0c"), rect(6, 6, 1268, 616, WD_BG, rx=8), grain(6, 6, 1268, 616))
    p.add(T(26, 30, "WEIRD DREAMS", 20, WD_INK, 700, anchor="start", sp=0.3, italic=True),
          T(1254, 30, title, 12, "#9a96a6", 700, anchor="end", sp=0.24))
    for i, c in enumerate(WD_COL):
        p.add(rect(290 + i * 28, 27, 22, 6, c, rx=3))
    for i in range(8):
        p.asset("wd_k%d.svg" % i, wd_knob(WD_COL[i]))
    p.asset("wd_kw.svg", wd_knob("#e9e6ef"))
    p.asset("wd_tr.svg", svg_doc(30, 240, rect(12, 0, 6, 240, "#050505", rx=3)))
    p.asset("wd_cap.svg", svg_doc(30, 40, rect(1, 1, 28, 38, "#2c2a30", rx=3, stroke="#000") + rect(1, 18, 28, 4, "#e9e6ef")))


def pweird(params):
    pages = []
    p = Page("MIXER", vink="#d8d2e8", lab=dict(size=12, fill=WD_INK, font=SANS, weight=700, sp=0.08), seg_text=True)
    wd_base(p, "8 VOICE DRUM MACHINE")
    for v in range(1, 9):
        x = 18 + (v - 1) * 134
        c = WD_COL[v - 1]
        k = "hw_wd_k%d.svg" % (v - 1)
        p.add(rect(x, 50, 126, 566, "#1c1b20", rx=6), rect(x, 50, 126, 26, c, rx=6), rect(x, 64, 126, 12, c),
              T(x + 63, 63, "VOICE %d" % v, 13, "#111", 700, sp=0.1))
        p.knob("v%d_pan" % v, x + 32, 116, 20, "PAN", img=k, lab=-30, size=10, vs=14)
        p.knob("v%d_rsend" % v, x + 94, 116, 20, "REV", img=k, lab=-30, size=10, vs=14)
        p.knob("v%d_dsend" % v, x + 94, 200, 20, "DLY", img=k, lab=-30, size=10, vs=14)
        for t in range(11):
            p.add(line(x + 18, 246 + 230 * t / 10, x + 26, 246 + 230 * t / 10, "#55525e", 1))
        p.slider("v%d_vol" % v, x + 40, 361, 30, 240, "VOL", img="hw_wd_cap.svg", base="hw_wd_tr.svg", vs=14, bw=60)
        p.add(T(x + 40, 234, "VOL", 10, WD_INK, 700))
        p.add(rect(x + 76, 420, 42, 120, "#2a2830", rx=6, stroke="#000"), circle(x + 97, 440, 5, c),
              T(x + 97, 556, "TRIG", 9, "#8a8696", 700) if False else "")
        p.add(rect(x + 14, 560, 98, 46, "#2c2a32", rx=8, stroke="#000"), circle(x + 63, 583, 6, c, extra=' opacity="0.8"'))
    x = 1092
    p.add(rect(x, 50, 176, 566, "#1c1b20", rx=6), rect(x, 50, 176, 26, "#e9e6ef", rx=6), rect(x, 64, 176, 12, "#e9e6ef"),
          T(x + 88, 63, "MASTER", 13, "#111", 700, sp=0.2))
    p.knob("comp", x + 46, 120, 24, "COMP", img="hw_wd_kw.svg", lab=-36)
    p.knob("dj_filter", x + 130, 120, 24, "DJ FILTER", img="hw_wd_kw.svg", lab=-36, size=10)
    for t in range(11):
        p.add(line(x + 60, 246 + 230 * t / 10, x + 70, 246 + 230 * t / 10, "#55525e", 1))
    p.slider("master", x + 88, 361, 34, 240, "MASTER", img="hw_wd_cap.svg", base="hw_wd_tr.svg", vs=15)
    p.add(T(x + 88, 234, "MASTER", 10, WD_INK, 700))
    p.qrow(*["v%d_vol" % v for v in range(1, 9)])
    p.qrow(*["v%d_pan" % v for v in range(1, 9)])
    p.qrow(*["v%d_rsend" % v for v in range(1, 9)])
    p.qrow(*["v%d_dsend" % v for v in range(1, 9)])
    p.qrow("master", "comp", "dj_filter")
    pages.append(p)

    def voice_page(name, pre, ci, title, extra=False):
        p = Page(name, vink="#d8d2e8", lab=dict(size=12, fill=WD_INK, font=SANS, weight=700, sp=0.08), seg_text=True)
        wd_base(p, title)
        c = WD_COL[ci] if ci is not None else "#e9e6ef"
        k = "hw_wd_k%d.svg" % ci if ci is not None else "hw_wd_kw.svg"
        for i in range(8):   # which voice is open
            p.add(circle(560 + i * 30, 30, 7, WD_COL[i] if (ci == i) else "#2c2a32", "#000"))
        secs = [("OSCILLATOR", 18, 470), ("NOISE", 482, 830), ("FILTER", 842, 1262)]
        secs2 = [("AMP", 18, 600), ("LFO", 612, 900), ("", 912, 1262)]
        for (n, a, b), y in [(s, 56) for s in secs] + [(s, 330) for s in secs2]:
            p.add(rect(a, y, b - a, 262, "#1c1b20", rx=6))
            if n:
                p.add(rect(a, y, b - a, 24, c, rx=6), rect(a, y + 12, b - a, 12, c), T((a + b) / 2, y + 13, n, 13, "#111", 700, sp=0.2))

        def K(key, x, y, l, r=30):
            p.knob(pre + key, x, y, r, l, img=k, lab=-(r + 20))
        K("freq", 100, 180, "FREQ", 44)
        K("wave", 220, 180, "WAVE")
        K("penv", 320, 180, "P ENV")
        K("prate", 420, 180, "P RATE")
        K("mix", 560, 180, "MIX")
        K("nattack", 670, 180, "ATTACK")
        K("ndecay", 770, 180, "DECAY")
        p.add(T(920, 110, "TYPE", 11, WD_INK, 700))
        p.switch(pre + "ftype", 920, 180, 3, vertical=True, sw=90, sh=30)
        K("cutoff", 1060, 180, "CUTOFF", 40)
        K("fres", 1190, 180, "RES")
        for i, (key, l) in enumerate((("attack", "ATTACK"), ("decay", "DECAY"), ("dist", "DIST"), ("level", "LEVEL"))):
            K(key, 90 + i * 140, 460, l)
        K("lamt", 690, 460, "AMOUNT")
        K("lrate", 820, 460, "RATE")
        K("preset", 990, 460, "PRESET")
        q1 = [pre + s for s in ("freq", "wave", "penv", "prate", "mix", "nattack", "ndecay", "cutoff")]
        q2 = [pre + s for s in ("fres", "attack", "decay", "dist", "level", "lamt", "lrate", "preset")]
        if extra:   # the selected voice's own mixer settings
            for i, (key, l) in enumerate((("vol", "VOL"), ("pan", "PAN"), ("rsend", "REV"), ("dsend", "DLY"))):
                p.knob(pre + key, 1120 + (i % 2) * 90, 400 + (i // 2) * 120, 22, l, img=k, lab=-34, size=10, vs=14)
            q2 += [pre + s for s in ("vol", "pan", "rsend", "dsend")]
            q2 = q2[:8]
            p.qrow(*q1)
            p.qrow(*q2)
            p.qrow(*[pre + s for s in ("vol", "pan", "rsend", "dsend")])
        else:
            p.qrow(*q1)
            p.qrow(*q2)
        return p

    for v in range(1, 9):
        pages.append(voice_page("VOICE %d" % v, "v%d_" % v, v - 1, "VOICE %d" % v))

    p = Page("FX", vink="#d8d2e8", lab=dict(size=12, fill=WD_INK, font=SANS, weight=700, sp=0.08), seg_text=True)
    wd_base(p, "EFFECTS")
    for n, a, b, y, h in (("REVERB", 18, 630, 56, 250), ("DELAY", 642, 1262, 56, 250), ("EQ", 18, 1262, 322, 294)):
        p.add(rect(a, y, b - a, h, "#1c1b20", rx=6), rect(a, y, b - a, 24, "#e9e6ef", rx=6), rect(a, y + 12, b - a, 12, "#e9e6ef"),
              T((a + b) / 2, y + 13, n, 13, "#111", 700, sp=0.2))
    p.add(T(90, 110, "TYPE", 11, WD_INK, 700))
    p.switch("rev_type", 90, 190, 3, vertical=True, sw=110, sh=32)
    for i, (k, l) in enumerate((("rev_size", "SIZE"), ("rev_decay", "DECAY"), ("rev_mix", "MIX"))):
        p.knob(k, 250 + i * 130, 190, 32, l, img="hw_wd_kw.svg", lab=-52)
    for i, (k, l) in enumerate((("dly_rate", "RATE"), ("dly_fdbk", "FEEDBACK"), ("dly_tone", "TONE"), ("dly_mix", "MIX"))):
        p.knob(k, 720 + i * 140, 190, 32, l, img="hw_wd_kw.svg", lab=-52)
    eq = [("eq_lo", "LOW", "lo_freq", "q_lo"), ("eq_mid", "MID", "mid_freq", "q_mid"), ("eq_hi", "HIGH", "hi_freq", "q_hi")]
    for i, (g, l, f, q) in enumerate(eq):
        x = 120 + i * 330
        p.knob(g, x, 430, 34, l, img="hw_wd_k%d.svg" % (i * 3), lab=-54)
        p.knob(f, x + 110, 430, 24, "FREQ", img="hw_wd_kw.svg", lab=-42)
        p.knob(q, x + 110, 540, 24, "Q", img="hw_wd_kw.svg", lab=-42)
    p.button("reset_eq", 1140, 470, "RESET EQ", color="ff4f6a")
    p.qrow("rev_size", "rev_decay", "rev_mix", "dly_rate", "dly_fdbk", "dly_tone", "dly_mix", "rev_type")
    p.qrow("eq_lo", "lo_freq", "q_lo", "eq_mid", "mid_freq", "q_mid", "eq_hi", "hi_freq")
    p.qrow("q_hi")
    pages.append(p)

    p = Page("KIT", vink="#d8d2e8", lab=dict(size=13, fill=WD_INK, font=SANS, weight=700, sp=0.08), seg_text=True)
    wd_base(p, "KIT")
    p.add(rect(18, 56, 400, 560, "#1c1b20", rx=6), rect(430, 56, 832, 560, "#1c1b20", rx=6),
          T(218, 80, "KIT", 14, WD_INK, 700, sp=0.3), T(846, 80, "RANDOMIZE", 14, WD_INK, 700, sp=0.3))
    p.knob("kit", 218, 220, 56, "KIT", img="hw_wd_kw.svg", lab=-80)
    p.add(T(218, 380, "MEMORY", 11, WD_INK, 700))
    p.switch("save_kit", 218, 440, 2, vertical=False, sw=110, sh=40)
    for i, (k, l) in enumerate((("rnd_kit", "RND KIT"), ("rnd_voice", "RND VOICE"), ("rnd_pitch", "RND PITCH"), ("rnd_pan", "RND PAN"),
                                ("init_freq", "INIT FREQ"), ("same_freq", "SAME FREQ"), ("all_mono", "ALL MONO"))):
        p.button(k, 560 + (i % 4) * 200, 200 + (i // 4) * 140, l, color=WD_COL[i].lstrip("#"))
    p.qrow("kit", "save_kit")
    pages.append(p)

    pages.append(voice_page("SELECTED", "cv_", None, "SELECTED VOICE", extra=True))
    return pages


# ---- BreakSlicer (breakslicer) ----------------------------------------------------------------------------------------
# No hardware: a boutique desktop unit of our own design, in the spirit of the other panels. A cream enamel face in a
# walnut case, a toasted header band with the name and a sliced-loaf print, three boxed sections: CUT (the big lit
# SLICE button and the SIZE rotary, 1/4 to 1/32 bar), SHAPE (GATE, MIX) and RANDOMISE (six chance knobs: SHUFFLE,
# REVERSE, ROLL over PITCH, PAN, FX). Black bakelite knobs with a cream pointer, a red-orange accent. The Force's eight
# knobs read the panel's two rows of four (GATE SHUFFLE REVERSE ROLL, MIX PITCH PAN FX); bank 2 = SIZE, SLICE.
def bs_knob(angle=None):
    s = knob_img(body="#1d1916", edge="#000", knurl="#2f2924", knurl_n=28, cap="#262019", cap_r=0.78, cap_edge="#0a0807",
                 line_c="#f4ead6", line=(0.15, 0.95), line_w=7, shine=0.22, rr=0.9)
    if angle is None:
        return s
    i = s.rindex("<line")
    return s[:i] + '<g transform="rotate(%g 48 48)">' % angle + s[i:-6] + "</g></svg>"


def pbreak(params):
    INK, DIM, ACC, FACE = "#2a1c12", "#6a5644", "#e0582a", "#efe6d2"
    p = Page("BREAKSLICER", vink=INK, lab=dict(size=14, fill=INK, font=SANS, weight=700, sp=0.12), seg_text=False)
    p.asset("bs_k.svg", bs_knob())
    # case and face
    p.add(wood(0, 0, 1280, 628, "#4a2a16"), rect(26, 18, 1228, 592, "#000", rx=10, extra=' opacity="0.35"'),
          rect(22, 14, 1236, 592, FACE, rx=10), grain(22, 14, 1236, 592), rect(22, 14, 1236, 592, "url(#hw-vshade)", rx=10))
    for x, y in ((42, 34), (1238, 34), (42, 586), (1238, 586)):
        p.add(screw(x, y, 6))
    # header: toasted band, the name, a loaf cut into slices
    p.add('<defs><linearGradient id="bs-toast" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b8662a"/>'
          '<stop offset="1" stop-color="#7a3a14"/></linearGradient></defs>',
          rect(22, 58, 1236, 66, "url(#bs-toast)"), rect(22, 58, 1236, 2, "#5a2a0e"), rect(22, 122, 1236, 2, "#5a2a0e"),
          T(60, 92, "BREAKSLICER", 40, "#fbefd8", 700, anchor="start", font=SANS, sp=0.06, stretch=1.05),
          T(468, 98, "TEMPO-SYNCED BREAK CHOPPER", 12, "#f6d9b4", 700, anchor="start", sp=0.3))
    # the loaf: a domed crust cut into eight slices, two of them turned round (orange)
    lx, ly, lw = 930, 112, 290
    p.add(path("M%g %g v-22 q0 -30 40 -30 h%g q40 0 40 30 v22 z" % (lx, ly, lw - 80), fill="#f3d7a8", stroke="#fbefd8", sw=2.5),
          path("M%g %g q10 -22 40 -24 h%g q30 2 40 24" % (lx + 6, ly - 26, lw - 92), stroke="#c98a4a", sw=2))
    for i in range(8):
        x0 = lx + i * lw / 8
        if i in (3, 6):
            p.add(rect(x0 + 3, ly - 40, lw / 8 - 6, 38, "#e0582a", extra=' opacity="0.55"'))
        if i:
            p.add(line(x0, ly - 50, x0, ly, "#7a3a14", 2.2))
    def section(x0, x1, title):
        p.add(rect(x0, 150, x1 - x0, 430, "none", rx=8, stroke="#b9a582", sw=2),
              rect((x0 + x1) / 2 - len(title) * 7 - 14, 140, len(title) * 14 + 28, 22, FACE),
              T((x0 + x1) / 2, 151, title, 15, ACC, 700, sp=0.3))
    section(48, 318, "CUT")
    section(338, 578, "SHAPE")
    section(598, 1232, "RANDOMISE")
    # CUT: SLICE (a big lit key), SIZE (rotary over 1/4 .. 1/32 bar)
    key = svg_doc(160, 160, rect(4, 6, 152, 152, "#000", rx=14, extra=' opacity="0.35"') +
                  rect(4, 2, 152, 152, "#c9bda4", rx=14) + rect(14, 12, 132, 132, "#efe6d2", rx=10, stroke="#8a7a5c", sw=2) +
                  rect(20, 18, 120, 30, "#fff", rx=8, extra=' opacity="0.45"') +
                  T(80, 74, "SLICE", 26, INK, 700, sp=0.12) + circle(80, 116, 9, "#5a1a0a", "#2a0a04", 1.5))
    keyon = svg_doc(160, 160, rect(0, 0, 160, 160, ACC, rx=16, extra=' opacity="0.35"') +
                    rect(4, 2, 152, 152, "#c9bda4", rx=14) + rect(14, 12, 132, 132, "#ffd9b8", rx=10, stroke=ACC, sw=3) +
                    rect(20, 18, 120, 30, "#fff", rx=8, extra=' opacity="0.55"') + T(80, 74, "SLICE", 26, INK, 700, sp=0.12) +
                    circle(80, 116, 16, "#ff5a2a", extra=' opacity="0.4"') + circle(80, 116, 9, "#ff4a1a", "#7a1a0a", 1.5))
    p.toggle("slice", 183, 272, "SLICE", img=p.asset("bs_key.svg", key), img_on=p.asset("bs_keyon.svg", keyon), w=160, h=160)
    ang = [-90, -30, 30, 90]
    p.add(T(183, 386, "SIZE", 14, INK, 700, sp=0.2), ticks(183, 470, 46, 54, 4, INK, 2.2, -90, 90),
          numbers(183, 470, 68, ["1/4", "1/8", "1/16", "1/32"], 12, INK, -90, 90), T(183, 528, "OF A BAR", 9, DIM, 700, sp=0.2))
    p.rotary("size", 183, 470, 38, 4, bs_knob, angles=ang, field_w=110, field_dy=82, accent=ACC)
    # SHAPE: GATE, MIX
    for k, y, l, lo, hi in (("gate", 270, "GATE", "STUTTER", "FULL"), ("mix", 470, "MIX", "DRY", "WET")):
        p.add(ticks(458, y, 50, 58, 11, INK, 2, -135, 135), T(458 - 58, y + 42, lo, 8.5, DIM, 700, anchor="end"),
              T(458 + 58, y + 42, hi, 8.5, DIM, 700, anchor="start"))
        p.knob(k, 458, y, 42, l, img="hw_bs_k.svg", lab=-74, bw=210)
    # RANDOMISE: the chance of each change, per slice
    for i, (k, l) in enumerate((("shuffle", "SHUFFLE"), ("reverse", "REVERSE"), ("roll", "ROLL"),
                                ("pitch", "PITCH"), ("pan", "PAN"), ("fx", "FX"))):
        x, y = 726 + (i % 3) * 190, 270 + (i // 3) * 200
        p.add(ticks(x, y, 50, 58, 11, INK, 2, -135, 135), T(x - 58, y + 42, "NEVER", 8, DIM, 700, anchor="end"),
              T(x + 58, y + 42, "ALWAYS", 8, DIM, 700, anchor="start"))
        p.knob(k, x, y, 42, l, img="hw_bs_k.svg", lab=-74, bw=180)
    p.add(T(915, 566, "CHANCE PER SLICE", 10, DIM, 700, sp=0.3))
    p.qrow("gate", "shuffle", "reverse", "roll", "mix", "pitch", "pan", "fx")
    p.qrow("size", "slice")
    return [p]
