# quadraverb

A QuadraVerb-inspired multi-FX for MPC OS.

**Concept:** a clean-room reimplementation of the *idea* behind the Alesis
QuadraVerb (the 1990s rack multi-FX): a curated set of series/parallel signal
paths combining reverb, tempo-syncable delay, chorus, flanger, phaser, pitch
shift, 3-band EQ, resonator, ring modulator and tremolo/autopan, with a slightly
grainy digital character. No Alesis code, presets, names, or assets are used or
copied — all DSP is fresh C written for this port (`src/dsp/fxdsp.h/.c`).

**How it works:** pick one of 6 configs on the CONFIG tab — Pitch>Dly>Verb,
Chorus>Dly>Verb, Flange>Dly>Verb, Phaser>Verb, Trem>Dly>Verb, or Reso+Ring>Verb —
then shape each block on its own tab. Every config starts with the input 3-band
EQ and ends with the master wet/dry mix. Delay syncs to the host tempo.

**Skin:** the PANEL tab redraws the QuadraVerb's front panel — black faceplate
with a grain finish, the green 2-line LCD with a live config readout plus
reverb type and delay sync readouts, the DATA wheel bound to the master mix,
the printed block buttons (PROG/VERB/DLY/PTCH/EQ/STOR/CONF/MIX/MIDI/BYP), and a
printed configuration chart of all six configs filling the lower half. Configs
switch via the config popup under the LCD. Each block tab (CONFIG, REVERB,
DELAY, CHORUS, PHASER, WEIRD) has its own faceplate strip with a section
header, row captions, and knob names printed on the panel (`ns=0`).

**Parameters (36):** config; EQ low/mid/mid-freq/high; reverb type (Room/Hall/
Plate/Small), size, decay, damp, mix; delay sync (Off–1/2), time, feedback,
damp, mix; chorus rate/depth/mix; flanger rate/depth/feedback/mix; phaser
rate/depth/stages/mix; pitch semitones/mix; resonator freq/resonance/mix; ring
rate/mix; tremolo rate/depth/mode; master mix.

**Build and test (from the repo root):**

    tools/build_port.sh ports/quadraverb/vst/vst.json   # needs Docker (ARM cross-compile + skin)
    tools/test_port.sh ports/quadraverb/vst/vst.json    # offline x86 ASan/UBSan host test -> PASSED

Offline simulator: `cc -I../../wrapper -Isrc -Isrc/dsp -o /tmp/qvsim
test/sim.c src/engine.c src/dsp/fxdsp.c -lm` prints per-config RMS through a sine sweep.

**Status (2026-10-10):** offline host test PASSED. Not yet on a device: install,
audio quality check, Q-Links, and skin rendering still need a check on the
Force. The layout is hand-written and has not been previewed (no Docker here).
