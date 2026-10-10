/* BreakSlicer: a tempo-synced slice / rearrange / reverse effect for MPC OS (wrapper/engine.h, "effect": true).
 *
 * The incoming audio is recorded into a ring buffer and cut into slices on the host's bar grid (song position from
 * songpos(), HAS_SONGPOS; free-running at the last tempo while the transport is stopped). At each slice boundary a
 * slice is either played live or replaced by an earlier slice of the recording, and may be reversed, rolled
 * (its start repeated), pitched, panned or given an effect (bit crush, low-pass sweep, tape stop), each by its own
 * probability. GATE shortens every slice into a stutter. With SLICE off the audio passes through unchanged.
 * Boundaries crossfade over 2 ms, so a changed slice never clicks.
 *
 * Written for this repo from the behaviour of audio slicers such as Audio Blast's BreadSlicer (no code from it). */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "engine.h"

#define SR 44100.0
#define RB (1 << 19)          /* ring buffer frames: 11.9 s, two bars at 40 BPM */
#define RB_MASK (RB - 1)
#define XF 96                 /* boundary crossfade, frames (2.2 ms) */
#define GATE_FADE 88.0        /* gate fade-out, frames (2 ms) */

static const char *ONOFF[] = {"Off", "On"};
static const char *SIZES[] = {"1/4", "1/8", "1/16", "1/32"};
static const double SIZE_BEATS[] = {1.0, 0.5, 0.25, 0.125};   /* 1/4 bar = one beat (4/4) */
static const double RATES[] = {0.5, 0.7491535, 1.3348399, 2.0};   /* -12, -5, +5, +12 semitones */

enum { FX_NONE, FX_CRUSH, FX_SWEEP, FX_STOP };

typedef struct {
    double start;      /* absolute frame (recording counter) the source slice starts at */
    double len;        /* slice length in frames */
    double roll;       /* roll length in frames (0: no roll) */
    double rate;       /* playback rate (1: unpitched) */
    int rev, fx;
    float gl, gr;      /* pan gains */
    float lp_l, lp_r;  /* sweep filter state */
    int16_t hold_l, hold_r;   /* crush sample-and-hold */
    int hold_n;
} voice_t;

typedef struct {
    int16_t *rb;           /* interleaved stereo recording */
    int64_t wr;            /* frames recorded so far */
    int slice_on, size;
    float gate, shuffle, reverse, roll, pitch, pan, fx, mix;   /* 0..1 */
    double bpm, host_ppq, free_ppq;
    int host_ok, playing;
    int64_t cur_idx;       /* slice index on the grid */
    double cur_t0;         /* ppq where the current slice started */
    voice_t cur, prev;
    int xf_left;           /* frames of crossfade still to run */
    double prev_p;         /* the previous voice's position, carried through the crossfade */
    int forced;            /* SLICE switched: start a new slice on the next frame */
    uint32_t rng;
    long slices;           /* slices started (test hook) */
} bs_t;

static float clampf(float v, float lo, float hi) { return v < lo ? lo : v > hi ? hi : v; }
static int find(const char **names, int n, const char *v) {
    for (int i = 0; i < n; i++) if (!strcmp(names[i], v)) return i;
    int i = atoi(v);
    return (v[0] >= '0' && v[0] <= '9' && i < n) ? i : -1;
}
static float rnd(bs_t *s) {   /* xorshift32, 0..1 */
    uint32_t x = s->rng;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    s->rng = x;
    return (x >> 8) * (1.0f / 16777216.0f);
}

static void *create(const char *dir) {
    (void)dir;
    bs_t *s = calloc(1, sizeof *s);
    if (!s) return NULL;
    s->rb = calloc((size_t)RB * 2, sizeof(int16_t));
    if (!s->rb) { free(s); return NULL; }
    s->slice_on = 1; s->size = 1; s->gate = 1.0f; s->shuffle = 0.6f; s->reverse = 0.25f; s->roll = 0.15f;
    s->pitch = 0; s->pan = 0; s->fx = 0; s->mix = 1.0f;
    s->bpm = 120; s->cur_idx = -1;
    s->rng = 0x9E3779B9u ^ (uint32_t)(uintptr_t)s;
    s->cur.rate = s->prev.rate = 1; s->cur.gl = s->cur.gr = s->prev.gl = s->prev.gr = 1;
    return s;
}
static void destroy(void *p) { bs_t *s = p; if (s) { free(s->rb); free(s); } }
static void midi(void *p, const uint8_t *m, int n) { (void)p; (void)m; (void)n; }

/* ---- parameters ---------------------------------------------------------------------------------------------- */
static float pct(const char *v) { return clampf((float)atof(v) / 100.0f, 0, 1); }
static void set_param(void *p, const char *k, const char *v) {
    bs_t *s = p;
    int i;
    if (!strcmp(k, "slice")) { if ((i = find(ONOFF, 2, v)) >= 0 && i != s->slice_on) { s->slice_on = i; s->forced = 1; } }
    else if (!strcmp(k, "size")) { if ((i = find(SIZES, 4, v)) >= 0) s->size = i; }
    else if (!strcmp(k, "gate")) s->gate = pct(v);
    else if (!strcmp(k, "shuffle")) s->shuffle = pct(v);
    else if (!strcmp(k, "reverse")) s->reverse = pct(v);
    else if (!strcmp(k, "roll")) s->roll = pct(v);
    else if (!strcmp(k, "pitch")) s->pitch = pct(v);
    else if (!strcmp(k, "pan")) s->pan = pct(v);
    else if (!strcmp(k, "fx")) s->fx = pct(v);
    else if (!strcmp(k, "mix")) s->mix = pct(v);
    else if (!strcmp(k, "state")) {   /* key=value;... */
        char buf[512];
        snprintf(buf, sizeof buf, "%s", v);
        for (char *t = strtok(buf, ";"); t; t = strtok(NULL, ";")) {
            char *eq = strchr(t, '=');
            if (!eq) continue;
            *eq = 0;
            if (strcmp(t, "state")) set_param(s, t, eq + 1);
        }
    }
}

static int get_param(void *p, const char *k, char *b, int n) {
    bs_t *s = p;
    if (!strcmp(k, "slice")) return snprintf(b, n, "%s", ONOFF[s->slice_on]);
    if (!strcmp(k, "size")) return snprintf(b, n, "%d", s->size);   /* the index: the wrapper reads a leading digit as one */
    struct { const char *k; float v; } pc[] = {{"gate", s->gate}, {"shuffle", s->shuffle}, {"reverse", s->reverse},
        {"roll", s->roll}, {"pitch", s->pitch}, {"pan", s->pan}, {"fx", s->fx}, {"mix", s->mix}};
    for (unsigned i = 0; i < sizeof pc / sizeof pc[0]; i++)
        if (!strcmp(k, pc[i].k)) return snprintf(b, n, "%d", (int)lrintf(pc[i].v * 100));
    if (!strcmp(k, "state"))
        return snprintf(b, n, "slice=%s;size=%s;gate=%d;shuffle=%d;reverse=%d;roll=%d;pitch=%d;pan=%d;fx=%d;mix=%d",
                        ONOFF[s->slice_on], SIZES[s->size], (int)lrintf(s->gate * 100), (int)lrintf(s->shuffle * 100),
                        (int)lrintf(s->reverse * 100), (int)lrintf(s->roll * 100), (int)lrintf(s->pitch * 100),
                        (int)lrintf(s->pan * 100), (int)lrintf(s->fx * 100), (int)lrintf(s->mix * 100));
    return 0;
}

static void songpos(void *p, double ppq, double bpm, int playing) {
    bs_t *s = p;
    if (bpm > 1) s->bpm = bpm;
    s->playing = playing;
    s->host_ok = playing && ppq >= 0;
    if (s->host_ok) s->host_ppq = ppq;
}

/* ---- slices -------------------------------------------------------------------------------------------------- */
/* A new slice: decide what plays for it. len: its length in frames; first: the bar's first slice. */
static void decide(bs_t *s, voice_t *v, double start_abs, double len, int first) {
    memset(v, 0, sizeof *v);
    v->len = len; v->rate = 1; v->gl = v->gr = 1;
    v->start = start_abs;   /* live: the slice being recorded now */
    if (!s->slice_on) return;
    int per_bar = (int)lrint(4.0 / SIZE_BEATS[s->size]);
    double hist = (double)(s->wr < RB ? s->wr : RB) - len - XF;   /* frames of recording a slice may come from */
    int kmax = hist > 0 ? (int)(hist / len) : 0;
    if (kmax > per_bar) kmax = per_bar;
    int k = 0;
    if (kmax > 0 && rnd(s) < s->shuffle * (first ? 0.5f : 1.0f)) k = 1 + (int)(rnd(s) * kmax);
    if (kmax > 0 && rnd(s) < s->reverse) { v->rev = 1; if (!k) k = 1; }
    if (rnd(s) < s->roll) v->roll = len / (s->size == 3 ? 2 : 2 + (int)(rnd(s) * 3));   /* 1/2, 1/3 or 1/4 */
    if (kmax > 0 && rnd(s) < s->pitch) { v->rate = RATES[(int)(rnd(s) * 4) & 3]; if (!k) k = 1; }
    if (rnd(s) < s->pan) {
        float a = (rnd(s) * 2 - 1) * 0.785398f + 0.785398f;   /* constant power, 0..pi/2 */
        v->gl = cosf(a) * 1.41421356f; v->gr = sinf(a) * 1.41421356f;
    }
    if (rnd(s) < s->fx) {
        v->fx = 1 + (int)(rnd(s) * 3);
        if (v->fx == FX_STOP && kmax == 0) v->fx = FX_CRUSH;
        if (v->fx == FX_STOP && !k) k = 1;
    }
    v->start = start_abs - k * len;
}

static void read_at(bs_t *s, double pos, float *l, float *r) {
    double lo = (double)(s->wr - RB + 2), hi = (double)(s->wr - 1);
    if (pos < lo) pos = lo;
    if (pos > hi) pos = hi;
    if (pos < 0) pos = 0;
    int64_t i = (int64_t)pos;
    float f = (float)(pos - (double)i);
    const int16_t *a = s->rb + 2 * (i & RB_MASK), *b = s->rb + 2 * ((i + 1 < s->wr ? i + 1 : i) & RB_MASK);
    *l = a[0] + (b[0] - a[0]) * f;
    *r = a[1] + (b[1] - a[1]) * f;
}

/* One frame of a voice at position p (frames since its slice started). */
static void voice_frame(bs_t *s, voice_t *v, double p, float *ol, float *or_) {
    double q = p;
    if (v->roll > 0) q = fmod(p, v->roll);
    if (v->fx == FX_STOP) q = q - q * q / (2 * v->len);   /* rate falls 1 -> 0 over the slice */
    else if (v->rate != 1) q = fmod(q * v->rate, v->len);
    if (v->rev) q = v->len - 1 - q;
    float l, r;
    read_at(s, v->start + q, &l, &r);
    if (v->fx == FX_CRUSH) {   /* 5 bits at a quarter of the rate */
        if (v->hold_n-- <= 0) { v->hold_n = 3; v->hold_l = (int16_t)((int)l & ~0x7FF); v->hold_r = (int16_t)((int)r & ~0x7FF); }
        l = v->hold_l; r = v->hold_r;
    } else if (v->fx == FX_SWEEP) {   /* one-pole low-pass closing from ~9 kHz to ~250 Hz over the slice */
        double t = p / v->len;
        float c = (float)(0.75 * pow(0.0476, t > 1 ? 1 : t));
        v->lp_l += c * (l - v->lp_l); v->lp_r += c * (r - v->lp_r);
        l = v->lp_l; r = v->lp_r;
    }
    float g = 1;
    if (s->slice_on && s->gate < 1) {   /* GATE: the slice's first part only, 2 ms fade */
        double end = v->len * (s->gate < 0.05f ? 0.05f : s->gate);
        g = (float)((end - p) / GATE_FADE);
        g = g > 1 ? 1 : g < 0 ? 0 : g;
    }
    *ol = l * v->gl * g;
    *or_ = r * v->gr * g;
}

static void process(void *p, const int16_t *in, int16_t *out, int frames) {
    bs_t *s = p;
    double dppq = s->bpm / (60.0 * SR);
    double slen = SIZE_BEATS[s->size];
    double ppq = s->host_ok ? s->host_ppq : s->free_ppq;
    for (int j = 0; j < frames; j++, ppq += dppq) {
        s->rb[2 * (s->wr & RB_MASK)] = in[2 * j];
        s->rb[2 * (s->wr & RB_MASK) + 1] = in[2 * j + 1];
        s->wr++;
        int64_t idx = (int64_t)floor(ppq / slen + 1e-9);
        if (idx != s->cur_idx || s->forced) {
            double into = (ppq - idx * slen) / dppq;   /* frames already past this boundary (a mid-slice start) */
            s->prev = s->cur;
            s->prev_p = s->cur_idx >= 0 ? (ppq - s->cur_t0) / dppq : 0;
            s->xf_left = s->cur_idx >= 0 && (s->slice_on || s->forced) ? XF : 0;
            int per_bar = (int)lrint(4.0 / slen);
            int first = ((idx % per_bar) + per_bar) % per_bar == 0;
            decide(s, &s->cur, (double)(s->wr - 1) - into, slen / dppq, first);
            s->cur_idx = idx;
            s->cur_t0 = idx * slen;
            s->forced = 0;
            s->slices++;
        }
        double pos = (ppq - s->cur_t0) / dppq;
        float l, r;
        if (!s->slice_on && !s->xf_left) { out[2 * j] = in[2 * j]; out[2 * j + 1] = in[2 * j + 1]; continue; }
        voice_frame(s, &s->cur, pos, &l, &r);
        if (s->xf_left > 0) {
            float pl, pr, a = (float)(XF - s->xf_left) / XF;
            voice_frame(s, &s->prev, s->prev_p, &pl, &pr);
            s->prev_p += 1;
            l = l * a + pl * (1 - a);
            r = r * a + pr * (1 - a);
            s->xf_left--;
        }
        float dry = s->slice_on ? 1 - s->mix : 0, wet = s->slice_on ? s->mix : 1;
        float ol = in[2 * j] * dry + l * wet, or_ = in[2 * j + 1] * dry + r * wet;
        out[2 * j] = (int16_t)(ol > 32767 ? 32767 : ol < -32768 ? -32768 : ol);
        out[2 * j + 1] = (int16_t)(or_ > 32767 ? 32767 : or_ < -32768 ? -32768 : or_);
    }
    s->free_ppq = ppq;   /* continues from here when the transport stops */
}

static void render(void *p, int16_t *out, int frames) { (void)p; memset(out, 0, (size_t)frames * 4); }

static const mpc_engine_t ENGINE = {create, destroy, midi, set_param, get_param, render, process, songpos};
const mpc_engine_t *mpc_engine(void) { return &ENGINE; }

#ifdef BREAKSLICER_TEST
long breakslicer_slices(void *p) { return ((bs_t *)p)->slices; }
#endif
