# dp4

A DP/4-inspired 4-unit parallel multi-FX for MPC OS.

**Concept:** a clean-room reimplementation of the *idea* behind the Ensoniq
DP/4 (the 1990s 4-unit parallel effects processor): four independent FX units
(A/B/C/D), each running one algorithm with six parameters and a mix, combined
through the hardware's routing model — per-pair Serial / Parallel / Feedback 1
/ Feedback 2, plus a Serial / Parallel link between the AB and CD pairs, with
adjustable feedback amount and a master mix. No Ensoniq code, presets, names,
or assets are used or copied — all DSP is fresh C written for this port
(`src/dsp/fxdsp.h/.c`).

**Behavioral references (behavior only — nothing copied):**
- [Temecula DSP DEEP/4](https://www.temeculadsp.com/deep4) — the in-depth
  commercial DP/4 emulation (all 43 algorithms, serial/parallel/feedback
  routing, per-unit parameters). Used as the primary reference for the 4-unit
  architecture, the routing modes, and the parameter behavior.
- The Ensoniq DP/4+ reference manual, Section 3 (Config Parameters) — for the
  exact routing semantics (feedback 1 vs 2 dry handling, all-wet feedback tap).
- [Dusty Devices Phaser-DDL](https://dustydevices.com/product/phaser-ddl) —
  the cycle-accurate emulation of the DP/4's phaser algorithm (the
  French-touch / Daft Punk phaser sound). Used as the behavioral reference for
  the marquee **Phaser-DDL** algorithm's parameter set and character.

**How it works:** each of the four tabs (A/B/C/D) picks one of 10 algorithms —
Off, Hall Reverb, Tempo Delay, Chorus, Flanger, **Phaser-DDL**, Pitch Shift,
Distortion, Para EQ, Tremolo — and the six knobs rename themselves to that
algorithm's parameters (with real value readouts: Hz, ms, dB, note values).
The ROUTE tab wires the units: AB pair routing, CD pair routing, the AB→CD
link, feedback amount, and master mix.

**The Phaser-DDL** (the marquee algorithm): a 12-stage LFO-swept allpass chain
with bipolar feedback, notch-depth control (from pure doppler swirl to deep
50/50 notches), stereo-out-of-phase LFO, sample-and-hold on the LFO for
stepped modulation, and a tempo-synced ping-pong DDL tail whose feedback
follows the phaser feedback. Parameters: Rate, Center, Width, Feedback (±),
Notch, S&H.

**Parameters (37):** per slot — algorithm, P1–P6 (dynamic names), mix;
routing — AB routing, CD routing, AB-CD link, feedback, master mix.

**Build and test (from the repo root):**

    tools/build_port.sh ports/dp4/vst/vst.json   # needs Docker (ARM cross-compile + skin)
    tools/test_port.sh ports/dp4/vst/vst.json    # offline x86 ASan/UBSan host test -> PASSED

Offline simulator: `cc -I../../wrapper -Isrc -Isrc/dsp -o /tmp/dp4sim
test/sim.c src/engine.c src/dsp/fxdsp.c -lm` prints per-algorithm RMS through a
sine sweep.

**Status (2026-10-10):** offline host test PASSED. Not yet on a device: install,
audio quality check, Q-Links, and skin rendering still need a check on the
Force. The layout is hand-written and has not been previewed (no Docker here).
The dynamic knob names (P1–P6 rename per algorithm) depend on the wrapper's
`dynamic_name` mechanism and `HAS_DISPLAY_REV` — worth verifying on the device.
