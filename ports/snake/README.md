# snake

A cartesian step sequencer for MPC OS, as a MIDI generator plugin.

**Concept:** a clean-room reimplementation of the [MDD Snake](https://maxforlive.com/library/device/4771/mdd-snake)
(Maxime Dangles) Max for Live device idea, itself a clone of the Make Noise René
cartesian sequencer: a 4x4 grid of pitch nodes played by two independent clocks. The X
clock steps along the chosen snake path, the Y clock jumps in strides of 4 along the
same path; each tick plays the node it lands on (when its gate is on). Per-node pitch
(scale degree), gate and glide; global scale quantization, root, octave, gate length,
MIDI channel and velocity. No Max patch code is used or copied; the René interaction
model is reimplemented from its documented behaviour.

**Snake paths:** Rows (boustrophedon), Columns, inward Spiral, diagonal Zigzag.

**How it works:** dial in 16 node pitches on the GRID tab, set the X/Y clock divisions
on the CLOCK tab, and let the two clocks walk the grid. Put snake on a track, pick its
ALSA port (`snake <n>`, shown on the CLOCK tab) as another track's MIDI input. Glide
nodes come out as legato overlaps.

**Parameters:** pitch/gate/glide per node (16 each), X rate, Y rate, path, scale (11),
root, gate length, octave, MIDI channel, velocity, randomize (momentary), port readout.

**Build and test (from the repo root):**

    tools/build_port.sh ports/snake/vst/vst.json     # needs Docker (ARM cross-compile + skin)
    tools/test_port.sh ports/snake/vst/vst.json      # offline x86 ASan/UBSan host test -> PASSED

Offline simulator: `cc -DSNAKE_TEST -I../../wrapper -Isrc -o /tmp/sim test/sim.c
src/engine.c -lm -ldl` prints the notes it would send over two bars at 120 BPM.

**Status (2026-10-10):** offline host test PASSED. Not yet on a device: install,
ALSA MIDI out to another track, Q-Links, and skin rendering still need a check on the
Force. The layout is hand-written and has not been previewed (no Docker here).
