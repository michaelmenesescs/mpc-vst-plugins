# Vendored sources

## src/dsp/Generator.hpp (+ LICENSE-MIT)

- Upstream: https://github.com/mattsp1290/acid-generator
- Commit: `795b1fcf7e359b95ad41b649de71e8d5c9144468` (2026-02-11)
- License: MIT — see `src/dsp/LICENSE-MIT` (upstream LICENSE, unmodified)
- What it is: a deterministic, seeded, weighted-probability TB-303-style pattern
  generator. Self-contained C++ header (only `<cstdint>`, `<cmath>`, `<algorithm>`);
  no heap allocation in the generation path. The upstream project describes it as
  heavily inspired by the STING by Skinnerbox Max for Live device.
- What we use: `SFC32` (seeded PRNG), `Scale` / `SCALES`, `SequenceStep`
  (`note` = scale degree or -1 rest, `octave` -1/0/1, `accent`, `slide`),
  `GeneratorParams` (density, spread, accentsDensity, slidesDensity, seed),
  `Pattern`, `getNoteInScale()`, and `generate()`. The `MasterPattern` /
  voltage-conversion helpers are unused.
- Local changes: none — the header is used as-is.
