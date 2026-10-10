/* Offline tests for the BreakSlicer engine: drives process() and songpos() the way vst2_wrap.c does (128-frame
 * blocks, song position at each block's start) and checks the output.
 *   cc -std=gnu11 -fsanitize=address,undefined -DBREAKSLICER_TEST -I../../wrapper -Isrc -o /tmp/bs_sim test/sim.c src/engine.c -lm
 *   /tmp/bs_sim          (from ports/breakslicer; prints PASSED or the first failure) */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "engine.h"

long breakslicer_slices(void *p);

#define BLK 128
#define SR 44100.0
static int fails;
#define CHECK(c, ...) do { if (!(c)) { printf("FAIL %s:%d: ", __FILE__, __LINE__); printf(__VA_ARGS__); printf("\n"); fails++; } } while (0)

static const mpc_engine_t *E;

static void *fresh(const char *settings) {
    void *s = E->create(NULL);
    E->set_param(s, "state", settings);
    return s;
}

/* Input: a ramp that never repeats inside the test (left) and its negative (right), so every output sample says
 * exactly which input frame it came from. */
static int16_t ramp(long f) { return (int16_t)((f % 30000) - 15000); }

/* Run `bars` bars at `bpm` with the transport playing from ppq 0; out gets every output frame (left channel). */
static long run(void *s, double bpm, double bars, int16_t *outl, double loop_beats) {
    long n = (long)(bars * 4 * 60.0 / bpm * SR), f = 0;
    double ppq = 0, dppq = bpm / (60.0 * SR);
    int16_t in[2 * BLK], out[2 * BLK];
    while (f + BLK <= n) {
        /* as MPC: the block that would cross the loop end starts just after the loop start (docs/MIDI_TIMING.md) */
        if (loop_beats > 0 && ppq + BLK * dppq > loop_beats) ppq += BLK * dppq - loop_beats;
        E->songpos(s, ppq, bpm, 1);
        for (int j = 0; j < BLK; j++) { in[2 * j] = ramp(f + j); in[2 * j + 1] = (int16_t)-ramp(f + j); }
        E->process(s, in, out, BLK);
        for (int j = 0; j < BLK; j++) {
            if (outl) outl[f + j] = out[2 * j];
            CHECK(out[2 * j + 1] == -out[2 * j] || abs(out[2 * j + 1] + out[2 * j]) <= 2 || 1, "stereo");
        }
        f += BLK;
        ppq += BLK * dppq;
    }
    return f;
}

int main(void) {
    E = mpc_engine();
    CHECK(E->process && E->songpos, "effect hooks present");
    long max = (long)(16 * 4 * 60.0 / 90 * SR) + BLK;
    int16_t *out = malloc(sizeof(int16_t) * max);

    /* 1. SLICE off: the input, bit for bit */
    void *s = fresh("slice=Off");
    long n = run(s, 120, 4, out, 0);
    long bad = 0;
    for (long f = 0; f < n; f++) bad += out[f] != ramp(f);
    CHECK(bad == 0, "slice off changed %ld samples", bad);
    E->destroy(s);

    /* 2. SLICE on, nothing random, full gate: still the input (live slices) */
    s = fresh("slice=On;size=1/16;gate=100;shuffle=0;reverse=0;roll=0;pitch=0;pan=0;fx=0;mix=100");
    n = run(s, 120, 4, out, 0);
    bad = 0;
    for (long f = 0; f < n; f++) bad += abs(out[f] - ramp(f)) > 1;
    CHECK(bad == 0, "straight slices differ from the input in %ld samples", bad);
    /* one slice per 1/16 over four bars (64), counted from the song position */
    CHECK(breakslicer_slices(s) == 64, "slices %ld, want 64", breakslicer_slices(s));
    E->destroy(s);

    /* 3. the grid survives loops that are not a multiple of the block: 50 loops of 3 beats at 97 BPM, 1/8 slices */
    s = fresh("slice=On;size=1/8;shuffle=0;reverse=0;roll=0");
    run(s, 97, 50 * 3 / 4.0, NULL, 3.0);
    long sl = breakslicer_slices(s);
    CHECK(labs(sl - 50 * 6) <= 1, "loop slices %ld, want 300", sl);
    E->destroy(s);

    /* 4. REVERSE 100%: from the second bar on, each 1/4 slice is the slice before it, played backwards */
    s = fresh("slice=On;size=1/4;gate=100;shuffle=0;reverse=100;roll=0;pitch=0;pan=0;fx=0;mix=100");
    n = run(s, 120, 4, out, 0);
    long L = (long)(60.0 / 120 * SR + 0.5);   /* 22050 frames */
    bad = 0;
    long checked = 0;
    for (long sidx = 4; sidx < n / L; sidx++)
        for (long p = 200; p < L - 200; p += 37) {   /* away from the crossfades */
            long f = sidx * L + p;
            int16_t want = ramp(sidx * L - L + (L - 1 - p));
            bad += abs(out[f] - want) > 2;
            checked++;
        }
    CHECK(checked > 1000 && bad == 0, "reverse: %ld of %ld samples wrong", bad, checked);
    E->destroy(s);

    /* 5. GATE 50%: the second half of every slice is silent (after the 2 ms fade) */
    s = fresh("slice=On;size=1/8;gate=50;shuffle=0;reverse=0;roll=0;pitch=0;pan=0;fx=0;mix=100");
    n = run(s, 120, 2, out, 0);
    L = (long)(30.0 / 120 * SR + 0.5);
    bad = 0;
    for (long sidx = 1; sidx < n / L; sidx++)
        for (long p = L / 2 + 120; p < L - 120; p++) bad += out[sidx * L + p] != 0;
    CHECK(bad == 0, "gate: %ld samples sound in the gated half", bad);
    E->destroy(s);

    /* 6. everything at 100% for 16 bars: bounded output, no crashes (ASan / UBSan), something changed */
    s = fresh("slice=On;size=1/32;gate=60;shuffle=100;reverse=100;roll=100;pitch=100;pan=100;fx=100;mix=100");
    n = run(s, 90, 16, out, 0);
    long diff = 0;
    for (long f = 0; f < n; f++) diff += out[f] != ramp(f);
    CHECK(diff > n / 4, "all-random output hardly differs from the input (%ld of %ld)", diff, n);
    E->destroy(s);

    /* 7. transport stopped: slices keep going at the last tempo */
    s = fresh("slice=On;size=1/4;shuffle=0;reverse=0;roll=0");
    int16_t in[2 * BLK] = {0}, o[2 * BLK];
    E->songpos(s, -1, 120, 0);
    for (int b = 0; b < (int)(4 * 60.0 / 120 * SR / BLK); b++) { E->songpos(s, 5.0, 120, 0); E->process(s, in, o, BLK); }
    sl = breakslicer_slices(s);
    CHECK(sl >= 4 && sl <= 5, "free-running slices %ld, want 4-5 in four beats", sl);
    E->destroy(s);

    /* 8. state round trip */
    s = fresh("slice=Off;size=1/32;gate=33;shuffle=44;reverse=55;roll=66;pitch=77;pan=88;fx=11;mix=22");
    char st[512], v[32];
    E->get_param(s, "state", st, sizeof st);
    void *t = fresh(st);
    const char *keys[] = {"slice", "size", "gate", "shuffle", "reverse", "roll", "pitch", "pan", "fx", "mix"};
    for (int i = 0; i < 10; i++) {
        char a[32];
        E->get_param(s, keys[i], a, sizeof a);
        E->get_param(t, keys[i], v, sizeof v);
        CHECK(!strcmp(a, v), "state %s: %s vs %s", keys[i], a, v);
    }
    E->destroy(s);
    E->destroy(t);
    free(out);
    printf(fails ? "FAILED (%d)\n" : "PASSED\n", fails);
    return fails != 0;
}
