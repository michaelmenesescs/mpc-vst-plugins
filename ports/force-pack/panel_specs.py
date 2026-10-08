"""Front panels, written left to right and top to bottom as on the hardware each plugin models (see panels.py).

Where the plugin has more controls than the machine (drive, sends, mods), the machine's own panel comes first and
the extras follow on their own pages, grouped the way the machine groups its voices."""
from panels import page, band, sec


def S(title, *rows, w=None):
    return sec(title, *rows, w=w)


# ---- drum-machine helpers -------------------------------------------------------------------------------------
def drive_page(voices, name="DRIVE"):
    """Per-voice drive knob over its distortion type, in two rows of up to 8 voices (one Q-Link bank each)."""
    bands = []
    for i in range(0, len(voices), 8):
        bands.append(band(*[S(t, "%s_drive=DRIVE" % v, "%s_dist_type:p=TYPE" % v) for v, t in voices[i:i + 8]]))
    return page(name, bands)


def sends_page(voices, rev="%s_rev", dly="%s_dly", name="SENDS"):
    return page(name, [band(*[S(t, (rev % v) + "=REV", (dly % v) + "=DLY") for v, t in voices])])


def master_page(extra_master, rev=True, dly=True, name="MASTER"):
    secs = [S("MASTER", *extra_master)]
    if rev:
        secs.append(S("REVERB", ["rev_decay=DECAY", "rev_tone=TONE"], ["rev_hpf=HPF", "rev_level=LEVEL"]))
    if dly:
        secs.append(S("DELAY", ["dly_time:p=TIME", "dly_fdbk=FEEDBACK"], ["dly_tone=TONE", "dly_hpf=HPF", "dly_level=LEVEL"]))
    return page(name, [band(*secs)])


# ---- TB-303 ---------------------------------------------------------------------------------------------------
# Panel, left to right: WAVEFORM switch, TUNING, CUT OFF FREQ, RESONANCE, ENV MOD, DECAY, ACCENT ... VOLUME.
# Under it the Devil Fish mod's extra knobs, then the drive stage.
P303 = [page("303", [
    band(S("", "waveform:e=WAVEFORM", w=1), S("", "tuning=TUNING"),
         S("", ["cutoff=CUT OFF FREQ", "resonance=RESONANCE", "env_mod=ENV MOD", "decay=DECAY"], w=4),
         S("", "accent=ACCENT"), S("", "volume=VOLUME")),
    band(S("DEVIL FISH", ["normal_decay=NORMAL DECAY", "accent_decay=ACCENT DECAY", "feedback_hpf=FEEDBACK HPF",
                          "soft_attack=SOFT ATTACK", "slide_time=SLIDE TIME", "devil_mod_switch:t=DEVIL MOD"]),
         S("DRIVE", ["drive_model:e=MODEL", "drive=DRIVE", "drive_mix=MIX", "tanh_shaper_drive=SHAPER"])),
])]


# ---- TR-808 ---------------------------------------------------------------------------------------------------
# The 808's top row: one column per instrument, LEVEL on top, then TONE/TUNING and DECAY/SNAPPY under it, in panel
# order BD SD LT MT HT RS CP CB CY OH CH. Its switchable voices (congas, claves, maracas) get the same columns on page 2.
def p808(_):
    cols = [("BASS DRUM", "bd", ["bd_level=LEVEL", "bd_tone=TONE", "bd_decay=DECAY"]),
            ("SNARE DRUM", "sd", ["sd_level=LEVEL", "sd_tune=TONE", "sd_snappy=SNAPPY"]),
            ("LOW TOM", "lt", ["lt_level=LEVEL", "lt_tune=TUNING", "lt_decay=DECAY"]),
            ("MID TOM", "mt", ["mt_level=LEVEL", "mt_tune=TUNING", "mt_decay=DECAY"]),
            ("HI TOM", "ht", ["ht_level=LEVEL", "ht_tune=TUNING", "ht_decay=DECAY"]),
            ("RIM SHOT", "rs", ["rs_level=LEVEL", "rs_tune=TUNING", "rs_decay=DECAY"]),
            ("HAND CLAP", "cp", ["cp_level=LEVEL", "cp_tune=TUNING", "cp_decay=DECAY"]),
            ("COW BELL", "cb", ["cb_level=LEVEL", "cb_tune=TUNING", "cb_decay=DECAY"]),
            ("CYMBAL", "cy", ["cy_level=LEVEL", "cy_tune=TONE", "cy_decay=DECAY"]),
            ("OPEN HIHAT", "oh", ["oh_level=LEVEL", "oh_tune=TUNING", "oh_decay=DECAY"]),
            ("CLSD HIHAT", "ch", ["ch_level=LEVEL", "ch_tune=TUNING", "ch_decay=DECAY"])]
    alt = [("LOW CONGA", "lc", ["lc_level=LEVEL", "lc_tune=TUNING", "lc_decay=DECAY"]),
           ("MID CONGA", "mc", ["mc_level=LEVEL", "mc_tune=TUNING", "mc_decay=DECAY"]),
           ("HI CONGA", "hc", ["hc_level=LEVEL", "hc_tune=TUNING", "hc_decay=DECAY"]),
           ("CLAVES", "cl", ["cl_level=LEVEL", "cl_tune=TUNING", "cl_decay=DECAY"]),
           ("MARACAS", "ma", ["ma_level=LEVEL", "ma_tune=TUNING", "ma_decay=DECAY", "ma_attack=ATTACK"]),
           ("EXTRA", "bd", ["bd_tune=BD TUNING", "bd_attack=BD ATTACK", "sd_decay=SD DECAY"]),
           ("HIHAT", "hh", ["hh_choke:e=CHOKE"])]
    voices = [("BD", "bd"), ("SD", "sd"), ("LT", "lt"), ("MT", "mt"), ("HT", "ht"), ("RS", "rs"), ("CP", "cp"), ("CB", "cb"),
              ("CY", "cy"), ("OH", "oh"), ("CH", "ch"), ("LC", "lc"), ("MC", "mc"), ("HC", "hc"), ("CL", "cl"), ("MA", "ma")]
    sends = [(t, v) for t, v in voices if v != "bd"]
    return [
        page("808", [band(*[S(t, *ctls) for t, _, ctls in cols])]),
        page("CONGA / CLAVES", [band(*[S(t, *ctls) for t, _, ctls in alt])]),
        drive_page([(v, t) for t, v in voices]),
        page("SENDS", [band(*[S(t, "%s_rev=REV" % v, "%s_dly=DLY" % v) for t, v in sends[:8]]),
                       band(*[S(t, "%s_rev=REV" % v, "%s_dly=DLY" % v) for t, v in sends[8:]])]),
        master_page([["volume=VOLUME", "comp=COMP", "vel_depth=VEL DEPTH"],
                     ["master_dist:p=MASTER DIST", "master_drive=DRIVE", "note_map:e=NOTE MAP"],
                     ["ui_focus=FOCUS", "mutes=MUTES"]]),
    ]


# ---- TR-606 ---------------------------------------------------------------------------------------------------
# The 606 has one LEVEL knob per instrument, left to right BD SD LT HT CY OH CH; here each column adds what this
# version can shape under its level.
def p606(_):
    cols = [("BASS DRUM", ["bd_level=LEVEL", "bd_tune=TUNE", "bd_decay=DECAY", "bd_attack=ATTACK"]),
            ("SNARE DRUM", ["sd_level=LEVEL", "sd_tune=TUNE", "sd_tone=TONE", "sd_snappy=SNAPPY"]),
            ("LOW TOM", ["lt_level=LEVEL", "lt_tune=TUNE", "lt_decay=DECAY"]),
            ("HIGH TOM", ["ht_level=LEVEL", "ht_tune=TUNE", "ht_decay=DECAY"]),
            ("CYMBAL", ["cy_level=LEVEL", "cy_tune=TUNE", "cy_decay=DECAY"]),
            ("OPEN HIHAT", ["oh_level=LEVEL", "oh_tune=TUNE", "oh_decay=DECAY"]),
            ("CLSD HIHAT", ["ch_level=LEVEL", "ch_tune=TUNE", "ch_decay=DECAY", "hh_choke:e=CHOKE"]),
            ("CLAP", ["cp_level=LEVEL", "cp_tune=TUNE", "cp_decay=DECAY", "cp_noise=NOISE"])]
    voices = [("BD", "bd"), ("SD", "sd"), ("LT", "lt"), ("HT", "ht"), ("CY", "cy"), ("OH", "oh"), ("CH", "ch"), ("CP", "cp")]
    return [
        page("606", [band(*[S(t, *c) for t, c in cols])]),
        drive_page([(v, t) for t, v in voices]),
        page("SENDS", [band(*[S(t, "%s_rev=REV" % v, "%s_dly=DLY" % v) for t, v in voices])]),
        master_page([["volume=VOLUME", "comp=COMP", "vel_depth=VEL DEPTH", "sd_decay=SD DECAY"],
                     ["master_dist:p=MASTER DIST", "master_drive=DRIVE", "note_map:e=NOTE MAP"],
                     ["ui_focus=FOCUS", "mutes=MUTES"]]),
    ]


# ---- TR-909 ---------------------------------------------------------------------------------------------------
# The 909's top panel, left to right: ACCENT; BASS DRUM (TUNE LEVEL / ATTACK DECAY); SNARE (TUNE LEVEL / TONE
# SNAPPY); LOW, MID, HI TOM (TUNE LEVEL / DECAY); RIM SHOT and HAND CLAP (LEVEL); HI HAT (CH LEVEL, OH LEVEL / CH
# DECAY, OH DECAY); CRASH and RIDE (LEVEL / TUNE); VOLUME.
def p909(_):
    def tom(t, v):
        return S(t, ["%s_c_tune=TUNE" % v, "%s_c_level=LEVEL" % v], ["%s_c_decay=DECAY" % v, "-"])
    top = band(S("ACCENT", "accent=ACCENT", "-"),
               S("BASS DRUM", ["bd_c_tune=TUNE", "bd_c_level=LEVEL"], ["bd_c_attack=ATTACK", "bd_c_decay=DECAY"]),
               S("SNARE DRUM", ["sd_c_tune=TUNE", "sd_c_level=LEVEL"], ["sd_c_noise_decay=TONE", "sd_c_snappy=SNAPPY"]),
               tom("LOW TOM", "lt"), tom("MID TOM", "mt"), tom("HI TOM", "ht"),
               S("RIM", "rs_volume=LEVEL", "rs_tune=TUNE"), S("CLAP", "hc_volume=LEVEL", "hc_decay=DECAY"),
               S("HI HAT", ["chh_volume=CH LVL", "ohh_volume=OH LVL"], ["chh_decay=CH DEC", "ohh_decay=OH DEC"]),
               S("CRASH", "cr_volume=LEVEL", "cr_pitch=TUNE"), S("RIDE", "rc_volume=LEVEL", "rc_pitch=TUNE"),
               S("", "volume=VOLUME", "-"))
    more = band(S("BASS DRUM", ["bd_c_sweep_depth=SWEEP", "bd_c_pitch_mod=PITCH MOD"]),
                S("TOMS", ["lt_c_attack=LT ATTACK", "mt_c_attack=MT ATTACK", "ht_c_attack=HT ATTACK"]),
                S("RIM / CLAP", ["rs_saturation=RIM SAT", "hc_tune=CLAP TUNE"]),
                S("CYMBALS", ["chh_pitch=CH TUNE", "ohh_pitch=OH TUNE", "cr_decay=CRASH DEC", "rc_decay=RIDE DEC"]))
    voices = [("BD", "bd_c"), ("SD", "sd_c"), ("LT", "lt_c"), ("MT", "mt_c"), ("HT", "ht_c"), ("RS", "rs"), ("CP", "hc"),
              ("CH", "chh"), ("OH", "ohh"), ("CR", "cr"), ("RD", "rc")]
    drives = []
    for t, v in voices:
        d = "rs_saturation" if v == "rs" else "%s_drive" % v
        drives.append((t, v, d))
    dp = [band(*[S(t, ("%s=DRIVE" % d) if v != "rs" else "-", "%s_dist_type:p=TYPE" % v) for t, v, d in drives[i:i + 8]])
          for i in (0, 8)]
    return [
        page("909", [top]),
        page("909 MORE", [more]),
        page("DRIVE", dp),
        page("SENDS", [band(*[S(t, "%s_rev=REV" % v, "%s_dly=DLY" % v) for t, v in voices[1:]])]),
        master_page([["master_comp=COMP", "vel_depth=VEL DEPTH", "note_map:e=NOTE MAP"],
                     ["master_dist:p=MASTER DIST", "master_drive=DRIVE"]]),
    ]


# ---- CR-78 ----------------------------------------------------------------------------------------------------
# The CR-78 is played from its rhythm selector (rhythm buttons, A/B variation, accent, balance, tempo); the
# instruments have level sliders here, in the machine's own instrument order.
def pcr78(_):
    inst = [("BD", "bd"), ("SD", "sd"), ("RS", "rs"), ("HH", "hh"), ("CY", "cy"), ("MA", "ma"), ("CL", "cl"),
            ("HB", "hb"), ("LB", "lb"), ("LC", "lc"), ("CB", "cb"), ("TB", "tb"), ("GU", "gu"), ("MB", "mb")]
    names = {"bd": "BASS DRUM", "sd": "SNARE", "rs": "RIM SHOT", "hh": "HI-HAT", "cy": "CYMBAL", "ma": "MARACAS",
             "cl": "CLAVES", "hb": "HI BONGO", "lb": "LO BONGO", "lc": "LO CONGA", "cb": "COWBELL", "tb": "TAMB",
             "gu": "GUIRO", "mb": "METAL BEAT"}
    rhythm = band(S("RHYTHM SELECTOR", ["rhy_style:p=RHYTHM I", "rhy_style2:p=RHYTHM II"], w=3),
                  S("VARIATION", ["rhy_ab:e=A / B", "rhy_mode:e=MODE"], w=2),
                  S("", ["volume=VOLUME", "comp=ACCENT COMP"], w=2))
    levels = band(*[S(t, "%s_level:s=%s" % (v, t)) for t, v in inst])
    voice_cols = [S(names[v], "%s_tune=TUNE" % v, "%s_decay=DECAY" % v) for _, v in inst]
    voice_cols[12] = S("GUIRO", ["gu_tune=TUNE", "gu_rate=RATE"], "gu_decay=DECAY")
    voice_cols[1] = S("SNARE", ["sd_tune=TUNE", "sd_snappy=SNAPPY"], "sd_decay=DECAY")
    voices = [(t, v) for t, v in inst]
    return [
        page("CR-78", [rhythm, levels]),
        page("VOICES", [band(*voice_cols[:7]), band(*voice_cols[7:])]),
        drive_page([(v, t) for t, v in voices]),
        page("SENDS", [band(*[S(t, "%s_rev=REV" % v, "%s_dly=DLY" % v) for t, v in voices[1:]])]),
        master_page([["vel_depth=VEL DEPTH", "note_map:e=NOTE MAP", "hat_choke:e=CHOKE"],
                     ["master_dist:p=MASTER DIST", "master_drive=DRIVE"], ["ui_focus=FOCUS", "mutes=MUTES"]]),
    ]


# ---- Braids / Plaits (Eurorack modules) -------------------------------------------------------------------------
# Each module is drawn as its own panel: Braids has the display and encoder on top, then the big TIMBRE and COLOR
# knobs, FM below; Plaits has the model buttons, FREQUENCY and HARMONICS, TIMBRE and MORPH, then the attenuverters.
# What the plugin adds (envelopes, filter) sits on an expander panel to the right.
PBRAIDS = [page("BRAIDS", [band(
    S("BRAIDS", "engine:p=MODEL", ["octave_transpose=COARSE", "fm=FM"], ["timbre:big=TIMBRE", "color:big=COLOR"], w=2.6),
    S("AMP ENV", ["attack=ATTACK", "decay=DECAY"], ["sustain=SUSTAIN", "release=RELEASE"], "volume=VOLUME", w=2),
    S("FILTER", ["cutoff:big=CUTOFF"], ["resonance=RESONANCE", "filt_env=ENV AMT"], w=2),
    S("FILTER ENV", ["f_attack=ATTACK", "f_decay=DECAY"], ["f_sustain=SUSTAIN", "f_release=RELEASE"], w=2))])]

PPLAITS = [page("PLAITS", [band(
    S("PLAITS", "engine:p=MODEL", ["octave_transpose:big=FREQUENCY", "harmonics:big=HARMONICS"],
      ["timbre=TIMBRE", "morph=MORPH"], ["timbre_mod=TIMBRE ATT", "fm_amount=FM ATT", "morph_mod=MORPH ATT"], w=3),
    S("LPG", ["decay=DECAY", "lpg_colour=COLOUR"], ["attack=ATTACK", "aux_mix=AUX MIX"], w=2),
    S("PERFORM", "fm_preset:p=FM PRESET", ["legato:e=LEGATO", "velocity_sensitivity=VELOCITY"], w=2))])]


# ---- MicroFreak (MrHyde) ----------------------------------------------------------------------------------------
# Top row as on the MicroFreak: OSCILLATOR (type, wave, timbre, shape), FILTER (cutoff, resonance, type), CYCLING
# ENVELOPE, ENVELOPE; under it the LFO and glide. The matrix page is the MicroFreak's: destinations down, sources across.
def pmrhyde(_):
    srcs = [("lfo", "LFO"), ("env", "ENV"), ("cycle_env", "CYC ENV"), ("random", "RANDOM"), ("velocity", "VELOCITY"),
            ("poly_aftertouch", "PRESSURE")]
    dests = [("pitch", "PITCH"), ("harmonics", "WAVE"), ("timbre", "TIMBRE"), ("cutoff", "CUTOFF")]
    grid = [["txt:" + n] + ["%s_mod_%s_amt=%s" % (d, s, sl) for s, sl in srcs] for d, n in dests]
    grid += [["assign%d_target:p=ASSIGN %d" % (i, i)] + ["assign%d_mod_%s_amt=%s" % (i, s, sl) for s, sl in srcs] for i in (1, 2)]
    return [
        page("PANEL", [
            band(S("OSCILLATOR", ["model:p=TYPE", "harmonics=WAVE", "timbre=TIMBRE", "morph=SHAPE"]),
                 S("FILTER", ["filter_cutoff:big=CUTOFF", "filter_resonance=RESONANCE", "filter_mode:e=TYPE"]),
                 S("CYCLING ENV", ["cycle_attack_ms=RISE", "cycle_decay_ms=FALL", "cycle_shape:e=SHAPE"]),
                 S("ENVELOPE", ["env_attack_ms=ATTACK", "env_decay_ms=DECAY", "env_sustain=SUSTAIN", "env_release_ms=RELEASE"])),
            band(S("LFO", ["lfo_rate=RATE", "lfo_shape:p=SHAPE", "lfo_rate_mode:e=SYNC"]),
                 S("GLIDE", "glide_ms=GLIDE"),
                 S("OSC MOD", ["pitch=PITCH", "fm_amount=FM", "aux_mix=AUX MIX"]),
                 S("LPG", ["lpg_decay=DECAY", "lpg_color=COLOR"]),
                 S("", ["volume=VOLUME", "voice_mode:e=VOICE"]))]),
        page("MATRIX", [band(S("MATRIX", *grid))]),
        page("MORE", [band(S("CYCLING ENV", ["cycle_sync:e=SYNC", "cycle_retrig:e=RETRIG", "cycle_bipolar:e=BIPOLAR"]),
                           S("LFO", ["lfo_retrig:e=RETRIG", "lfo_phase=PHASE"]),
                           S("ENV", ["env_retrig:e=RETRIG"])),
                      band(S("RANDOM", ["random_mode:e=MODE", "random_rate=RATE", "random_rate_mode:e=SYNC",
                                        "random_slew=SLEW", "random_retrig:e=RETRIG"]),
                           S("CURVES", ["velocity_curve=VEL CURVE", "poly_aftertouch_curve=AT CURVE"])),
                      band(S("VOICES", ["polyphony=POLYPHONY", "unison=UNISON", "detune=DETUNE", "spread=SPREAD", "pan=PAN"]))]),
    ]


# ---- Denis (Serge style modules) ---------------------------------------------------------------------------------
# A Serge-style row of modules, each a tall panel with its knobs down the middle; the 4 x 8 matrix page has a
# row per source (ENV, LFO, S&H, NOISE) and a column per destination, so each row is one Q-Link bank.
def pdenis(_):
    dest = ["PITCH 1", "TIMBRE", "PITCH 2", "HARM", "FOLD", "F TYPE", "CUTOFF", "LEVEL"]
    src = ["ENV", "LFO", "S&H", "NOISE"]
    return [
        page("DENIS", [band(
            S("COMPLEX OSC", "osc1_freq:big=FREQ", "osc1_timbre=TIMBRE"),
            S("MODULATOR", "osc2_pitch:big=PITCH", "osc2_harmonics=HARMONICS"),
            S("MIXER", "osc_mix=OSC MIX", "noise_mix=NOISE", "noise_type:e=NOISE TYPE"),
            S("WAVEFOLDER", "fold_depth:big=DEPTH", "fold_type=TYPE"),
            S("FILTER", "filter_cutoff:big=CUTOFF", "filter_q=Q", "filter_type:e=TYPE"),
            S("ENVELOPE", ["attack=A", "decay=D"], ["sustain=S", "release=R"], "vel_to_filter=VEL>FILT"),
            S("MOD", "lfo_rate=LFO RATE", "sh_rate=S&H RATE", ["mod_depth_env=ENV", "mod_depth_noise=NOISE"]))]),
        page("MATRIX", [band(S(s, ["mat_%d_%d=%s" % (r, c, d) for c, d in enumerate(dest)])) for r, s in enumerate(src)]),
        page("PATCH", [band(S("PRESET", "preset=PRESET"), S("PLAY", ["portamento=GLIDE", "legato:e=LEGATO", "patch_mode:e=PADS"]),
                            S("RANDOM", ["rnd_denis:b=RND DENIS", "rnd_mod:b=RND MOD"], ["rnd_patch:b=RND PATCH", "matrix_reset:b=RESET MATRIX"]))]),
    ]


# ---- SH-101 (HUSH ONE) ------------------------------------------------------------------------------------------
# Sliders in the 101's sections, left to right: MODULATOR, VCO, SOURCE MIXER, VCF, VCA, ENV, with each section's
# switches under its sliders; the controller side (glide, bender, transpose) and the extras on page 2.
PHUSH = [
    page("SH-101", [band(
        S("MODULATOR", "lfo_rate:s=RATE", "lfo_waveform:e=WAVE"),
        S("VCO", ["lfo_pitch:s=MOD", "pulse_width:s=PW"], ["octave_transpose=RANGE", "pwm_mode:e=PWM"]),
        S("SOURCE MIXER", ["pulse:s=PULSE", "saw:s=SAW", "sub:s=SUB", "noise:s=NOISE"], ["sub_mode:e=SUB", "white_noise:t=WHITE"]),
        S("VCF", ["cutoff:s=FREQ", "resonance:s=RES", "env_amt:s=ENV", "lfo_filter:s=MOD", "key_follow:s=KYBD"],
          ["filter_velocity_sens=VEL", "filter_env_polarity:t=ENV INV"]),
        S("VCA", "volume:s=LEVEL", "vca_mode:e=MODE"),
        S("ENV", ["attack:s=A", "decay:s=D", "sustain:s=S", "release:s=R"], ["gate_trig_mode:e=GATE/TRIG", "velocity_sens=VEL"]))]),
    page("CONTROLLER", [
        band(S("PORTAMENTO", ["glide=GLIDE", "portamento_mode:e=MODE", "portamento_linear:t=LINEAR"]),
             S("BENDER", ["bend_range=RANGE", "transpose=TRANSPOSE", "fine_tune=FINE"]),
             S("PLAY", ["priority:e=PRIORITY", "retrigger:t=RETRIG", "hold:t=HOLD", "same_note_quirk:t=SAME NOTE"])),
        band(S("FILTER ENV", ["f_attack=A", "f_decay=D", "f_sustain=S", "f_release=R", "filter_env_full_range:t=FULL"]),
             S("PWM", ["pwm_depth=LFO DEPTH", "pwm_env_depth=ENV DEPTH"]),
             S("LFO", ["lfo_trigger:t=TRIG", "lfo_sync:t=SYNC", "lfo_invert:t=INVERT", "lfo_pitch_snap:t=SNAP", "lfo_pwm=PWM MOD"])),
        band(S("VOICE", ["preset=PRESET", "velocity_mode:e=VELOCITY", "adsr_declick=DECLICK", "filter_volume_correction=VOL COMP"]))]),
]


# ---- the rest ----------------------------------------------------------------------------------------------------
PHANK = [page("HANK", [
    band(S("OPERATOR", ["ratio:p=RATIO", "bright:big=BRIGHT", "bite:big=BITE", "tone=TONE"]),
         S("ENVELOPE", ["attack=ATTACK", "decay=DECAY", "sustain=SUSTAIN"])),
    band(S("NOISE", "noise=NOISE"), S("VOICE", ["voice_count=VOICES", "glide=GLIDE", "pitch=PITCH"]),
         S("MASTER", ["volume=VOLUME", "preset=PRESET"]))])]

PCHIP = [page("CHIPTUNE", [
    band(S("CHIP", ["chip:e=CHIP", "alloc_mode:e=VOICES", "noise_mode:e=NOISE", "duty=DUTY", "wavetable=WAVE"]),
         S("ENVELOPE", ["env_attack=ATTACK", "env_decay=DECAY", "env_sustain=SUSTAIN", "env_release=RELEASE"])),
    band(S("PITCH", ["sweep=SWEEP", "vibrato_depth=VIB DEPTH", "vibrato_rate=VIB RATE", "pitch_env_depth=P ENV",
                     "pitch_env_speed=P SPEED"]),
         S("OUTPUT", ["detune=DETUNE", "channel_mask=CHANNELS", "octave_transpose=OCTAVE", "volume=VOLUME"]))])]


def ppo32(_):
    grid = [["v%02d_lvl=%d" % (r * 4 + c + 1, r * 4 + c + 1) for c in range(4)] for r in range(4)]
    pages = [page("PO-32", [band(S("DISPLAY", "kit=KIT", ["level=A  LEVEL", "decay=B  DECAY"], w=2),
                                 S("SOUNDS", *grid, w=4))], qorder="flat")]
    for v in range(1, 17):
        k = "v%02d_" % v
        pages.append(page("%d" % v, [band(
            S("TONE", ["%sfreq=FREQ" % k, "%smrate=MOD RATE" % k, "%smamt=MOD AMT" % k]),
            S("NOISE", ["%snffrq=FILT FREQ" % k, "%snfq=FILT Q" % k]),
            S("TONE ENV", ["%satk=ATTACK" % k, "%sdcy=DECAY" % k])),
            band(S("NOISE ENV", ["%sneatk=ATTACK" % k, "%snedcy=DECAY" % k]),
                 S("OUTPUT", ["%smix=MIX" % k, "%sdist=DIST" % k, "%slvl=LEVEL" % k]))]))
    return pages


def pweird(_):
    strips = band(*[S("%d" % v, "v%d_vol=VOL" % v, "v%d_pan=PAN" % v, "v%d_rsend=REV" % v, "v%d_dsend=DLY" % v)
                    for v in range(1, 9)], S("MASTER", "master=MASTER", "comp=COMP", "dj_filter=DJ FILTER", "-"))
    pages = [page("MIXER", [strips])]
    for v in range(1, 9):
        k = "v%d_" % v
        pages.append(page("VOICE %d" % v, [
            band(S("OSCILLATOR", ["%sfreq:big=FREQ" % k, "%swave=WAVE" % k, "%spenv=P ENV" % k, "%sprate=P RATE" % k]),
                 S("NOISE", ["%smix=MIX" % k, "%snattack=ATTACK" % k, "%sndecay=DECAY" % k])),
            band(S("FILTER", ["%sftype:e=TYPE" % k, "%scutoff=CUTOFF" % k, "%sfres=RES" % k]),
                 S("AMP", ["%sattack=ATTACK" % k, "%sdecay=DECAY" % k, "%sdist=DIST" % k, "%slevel=LEVEL" % k]),
                 S("LFO", ["%slamt=AMOUNT" % k, "%slrate=RATE" % k]), S("", "%spreset=PRESET" % k))]))
    pages.append(page("FX", [
        band(S("REVERB", ["rev_type:e=TYPE", "rev_size=SIZE", "rev_decay=DECAY", "rev_mix=MIX"]),
             S("DELAY", ["dly_rate=RATE", "dly_fdbk=FEEDBACK", "dly_tone=TONE", "dly_mix=MIX"])),
        band(S("EQ", ["eq_lo=LOW", "eq_mid=MID", "eq_hi=HIGH", "reset_eq:b=RESET"], ["lo_freq=LO FREQ", "mid_freq=MID FREQ",
                                                                                      "hi_freq=HI FREQ", "-"],
               ["q_lo=LO Q", "q_mid=MID Q", "q_hi=HI Q", "-"]))]))
    pages.append(page("KIT", [band(S("KIT", ["kit=KIT", "save_kit:e=SAVE"]),
                                   S("RANDOMIZE", ["rnd_kit:b=RND KIT", "rnd_voice:b=RND VOICE", "rnd_pitch:b=RND PITCH",
                                                   "rnd_pan:b=RND PAN"], ["init_freq:b=INIT FREQ", "same_freq:b=SAME FREQ",
                                                                          "all_mono:b=ALL MONO", "-"]))]))
    cv = [("cv_vol", "VOL"), ("cv_pan", "PAN"), ("cv_freq", "FREQ"), ("cv_wave", "WAVE"), ("cv_penv", "P ENV"),
          ("cv_prate", "P RATE"), ("cv_attack", "ATTACK"), ("cv_decay", "DECAY"), ("cv_mix", "NOISE MIX"),
          ("cv_nattack", "N ATTACK"), ("cv_ndecay", "N DECAY"), ("cv_ftype:e", "F TYPE"), ("cv_cutoff", "CUTOFF"),
          ("cv_fres", "RES"), ("cv_lamt", "LFO AMT"), ("cv_lrate", "LFO RATE"), ("cv_dist", "DIST"), ("cv_level", "LEVEL"),
          ("cv_preset", "PRESET"), ("cv_rsend", "REV"), ("cv_dsend", "DLY")]
    pages.append(page("SELECTED", [band(S("SELECTED VOICE", ["%s=%s" % c for c in cv[:7]], ["%s=%s" % c for c in cv[7:14]],
                                         ["%s=%s" % c for c in cv[14:]]))]))
    return pages


PMIDIVERB = [page("MIDIVERB", [
    band(S("MIDIVERB", ["input_gain=INPUT", "unit:e=UNIT", "program:big=PROGRAM", "mix=MIX", "output_gain=OUTPUT"])),
    band(S("EXPANDER", ["feedback=FEEDBACK", "predelay_ms=PRE-DELAY", "low_cut_hz=LOW CUT", "high_cut_hz=HIGH CUT",
                        "damping=DAMPING", "tilt=TILT", "width=WIDTH", "lfo_rate=LFO RATE", "lfo_depth=LFO DEPTH"]))])]

PPSX = [page("PSX VERB", [band(S("MODE", "model:e=MODE", w=1.2),
                                S("", ["decay:big=DECAY"], w=2.4),
                                S("", "mix=MIX", "input_gain=INPUT", "reverb_level=LEVEL", w=1))])]

# RE-201: MODE SELECTOR, REPEAT RATE, INTENSITY, ECHO VOLUME, then tone, left to right.
PTAPE = [page("SPACE ECHO", [band(S("", "division:p=MODE SELECTOR"), S("", "time:big=REPEAT RATE"),
                                  S("", "feedback:big=INTENSITY"), S("", "mix:big=ECHO VOLUME"),
                                  S("", "tone=TONE"), S("", "stereo_width=WIDTH"))])]

PJUNO = [page("CHORUS", [band(S("CHORUS", "mode:e=CHORUS", w=3), S("", ["mix:s=MIX", "brightness:s=BRIGHT"], w=1.5))])]

# Drum Buss: DRIVE (amount, type, COMP, TRIM) | CRUNCH DAMP TRANSIENTS | BOOM (amount, freq, decay) | OUTPUT, DRY/WET
PBUS = [page("DRUM BUSS", [band(S("DRIVE", "drive:big=DRIVE", "drive_type:e=TYPE", ["comp:e=COMP", "trim=TRIM"]),
                                S("", "crunch=CRUNCH", "damp=DAMP", "transients=TRANSIENTS"),
                                S("BOOM", "boom:big=BOOM", ["boom_freq=FREQ", "boom_decay=DECAY"]),
                                S("", "output=OUTPUT", "drywet=DRY/WET"))])]

# SSL channel EQ, top to bottom on the strip, here left to right: FILTERS, HF, HMF, LMF, LF, then the I/O.
P4K = [page("EQ", [band(S("FILTERS", "hpf_freq=HPF", "hpf_enabled:t=HPF IN", "lpf_freq=LPF", "lpf_enabled:t=LPF IN"),
                        S("HF", "hf_gain:big=GAIN", "hf_freq=FREQ", "hf_bell:t=BELL"),
                        S("HMF", "hm_gain:big=GAIN", "hm_freq=FREQ", "hm_q=Q"),
                        S("LMF", "lm_gain:big=GAIN", "lm_freq=FREQ", "lm_q=Q"),
                        S("LF", "lf_gain:big=GAIN", "lf_freq=FREQ", "lf_bell:t=BELL"),
                        S("CHANNEL", "input_gain=INPUT", "output_gain=OUTPUT", ["eq_type:e=E / G", "bypass:t=IN"]))]),
       page("SETUP", [band(S("OPTIONS", ["auto_gain:t=AUTO GAIN", "oversampling:e=OVERSAMPLE"]),
                           S("METERS", ["in_peak_l:r=IN L", "in_peak_r:r=IN R"], ["out_peak_l:r=OUT L", "out_peak_r:r=OUT R"],
                             "clip:r=CLIP"))])]

PDUCK = [page("DUCKER", [band(S("TRIGGER", "channel:p=CHANNEL", "trigger_note:p=NOTE", "mode:e=MODE"),
                              S("SHAPE", ["depth:big=DEPTH", "curve:e=CURVE"], ["attack=ATTACK", "hold=HOLD", "release=RELEASE"]),
                              S("", "vel_sens=VEL SENS"))])]

PFILTER = [page("FILTER", [band(S("FILTER", ["model:e=MODEL", "mode:p=MODE"], ["cutoff:big=CUTOFF", "resonance:big=RESONANCE"],
                                  w=2.6),
                                S("DRIVE", "drive=DRIVE", "mix=MIX", "output=OUTPUT"),
                                S("ENVELOPE", "env_amount=AMOUNT", ["env_attack=ATTACK", "env_release=RELEASE"]),
                                S("LFO", ["lfo_amount=AMOUNT", "lfo_shape:p=SHAPE"], ["lfo_sync:e=SYNC", "lfo_rate_hz=RATE"],
                                  "lfo_rate_div:p=DIVISION"))])]

PTAPESCAM = [page("TAPESCAM", [
    band(S("TAPE", ["age:h=TAPE AGE", "speed:h=SPEED"]), S("DECK", ["compression:h=COMP", "widen:h=WIDEN"])),
    band(S("", ["input=INPUT", "drive:big=DRIVE", "color=COLOR", "wobble=WOBBLE", "noise=NOISE", "tone=TONE", "output=OUTPUT"]))])]

# ML-185: one column per stage, as on the hardware: PITCH slider, PULSES, GATE mode, SLIDE, ACCENT; the clock on the right.
PML185 = [page("STAGES", [band(*[S("%d" % i, "pitch%d:s=PITCH" % i, "pulses%d=PULSES" % i, "gate%d:e=GATE" % i,
                                   "slide%d:t=SLIDE" % i, "accent%d:t=ACCENT" % i) for i in range(1, 9)],
                               S("CLOCK", "length=LENGTH", "rate:p=RATE", "direction:p=DIRECTION", "randomize:b=RANDOMIZE",
                                 w=1.3))]),
          page("GLOBAL", [band(S("TIME", ["swing=SWING", "gate_len=GATE LEN"]),
                               S("KEY", ["scale:p=SCALE", "root:p=ROOT", "octave=OCTAVE"])),
                          band(S("MIDI", ["channel=CHANNEL", "velocity=VELOCITY", "accent_vel=ACCENT VEL", "status:r=TRACK INPUT"]))])]

PANELS = {"303": P303, "8w8": p808, "6w6": p606, "9w9": p909, "cw78": pcr78, "braids": PBRAIDS, "plaits": PPLAITS,
          "mrhyde": pmrhyde, "denis": pdenis, "hush1": PHUSH, "hank": PHANK, "chiptune": PCHIP, "libpo32": ppo32,
          "weird": pweird, "midiverb": PMIDIVERB, "psxverb": PPSX, "tapedelay": PTAPE, "juno": PJUNO, "busdriver": PBUS,
          "4keq": P4K, "ducker": PDUCK, "filter": PFILTER, "tapescam": PTAPESCAM, "ml185": PML185}

# ---- hardware pages (hwpanel.Page): controls at the machine's own positions, with its panel artwork ------------
import m_roland  # noqa: E402
PANELS.update({"303": m_roland.p303, "8w8": m_roland.p808, "9w9": m_roland.p909, "6w6": m_roland.p606, "hush1": m_roland.p101})
