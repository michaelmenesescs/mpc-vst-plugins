# sting

A generative acid sequencer for MPC OS, as a MIDI generator plugin.

**Concept:** a clean-room reimplementation of the [STING by Skinnerbox](https://maxforlive.com/library/device/4260/sting-by-skinnerbox)
(Iftah Gabbai) Max for Live device idea — a seeded, deterministic 303-style pattern
generator with per-step pitch, octave, accent and slide. No Max patch code is used or
copied. The generation core is vendored from
[mattsp1290/acid-generator](https://github.com/mattsp1290/acid-generator) (MIT), which
is itself explicitly Sting-inspired: deterministic seeded SFC32 PRNG, weighted-probability
note choice favouring root and fifth, downbeat-prioritised rhythm mask, per-step
accent/slide probabilities. See `src/VENDORED.md`.

**How it works:** set a seed (or hit Regenerate), pick steps / rate / scale / root, and
shape the pattern with density, chaos (note spread), accent and slide probabilities.
The pattern regenerates live whenever a generation parameter moves. Put sting on a
track, pick its ALSA port (`sting <n>`, shown on the SETUP tab) as another track's MIDI
input, and drive a 303-style synth with it — slides come out as legato overlaps, so a
mono synth with glide slides between them.

**Parameters:** seed, steps (1–32), rate, scale (12), root, density, chaos, accents,
slides, gate length, swing, octave, MIDI channel, velocity, accent velocity, regenerate
(momentary), port readout.

**Build and test (from the repo root):**

    tools/build_port.sh ports/sting/vst/vst.json     # needs Docker (ARM cross-compile + skin)
    tools/test_port.sh ports/sting/vst/vst.json      # offline x86 ASan/UBSan host test -> PASSED

Offline simulator: `g++ -DSTING_TEST -I../../wrapper -Isrc -Isrc/dsp -o /tmp/sim test/sim.cpp
src/engine.cpp -lm -ldl` prints the notes it would send over two bars at 120 BPM.

**Status (2026-10-10):** offline host test PASSED. Not yet on a device: install,
ALSA MIDI out to another track, Q-Links, and skin rendering still need a check on the
Force. The layout is hand-written and has not been previewed (no Docker here).
