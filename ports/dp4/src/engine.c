/* dp4: a clean-room Ensoniq DP/4-inspired 4-unit multi-FX for MPC OS.
 *
 * Architecture (behavioral recreation of the DP/4's, per its reference manual
 * Section 3 "Config Parameters" and the Temecula DSP DEEP/4's documented
 * behavior — serial / parallel / feedback routing, four A/B/C/D units, per-unit
 * algorithms and params; all DSP here is fresh C, nothing copied):
 *
 *   - Four slots A/B/C/D, each running one of 10 algorithms with 6 params + mix.
 *   - AB pair routing: Serial / Parallel / Feedback 1 / Feedback 2 (the two
 *     feedback modes differ in how dry is mixed into the wet loop, as on the
 *     hardware; the feedback tap is all-wet, taken before the dry mix).
 *   - CD pair routing: same four modes.
 *   - AB->CD link: Serial / Parallel.
 *   - Feedback amount + master mix.
 *
 * The Phaser-DDL algorithm is the marquee: its parameter set (Rate, Center,
 * Width, bipolar Feedback, Notch depth, Sample&Hold) follows the DP/4+
 * manual's Phaser-DDL, with the Dusty Devices Phaser-DDL (a cycle-accurate
 * DP/4 phaser emulation) as the behavioral reference. Clean-room throughout.
 *
 * Effect port: the wrapper (PLUG_EFFECT) feeds 128-frame int16 stereo blocks
 * to process(). Structural params (algorithm select) take effect at the next
 * block; time-based params are de-clicked inside the DSP blocks. No malloc on
 * the audio thread (all voices allocated in create()).
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <math.h>
#include "engine.h"
#include "dsp/fxdsp.h"

/* algorithms */
enum { ALG_OFF, ALG_VERB, ALG_DLY, ALG_CHO, ALG_FLA, ALG_PHA, ALG_PIT,
       ALG_DST, ALG_EQ, ALG_TREM, NALG };
static const char *ALG_NAMES[NALG] = {
    "Off", "Hall Reverb", "Tempo Delay", "Chorus", "Flanger",
    "Phaser-DDL", "Pitch Shift", "Distortion", "Para EQ", "Tremolo"
};
/* dynamic P1..P6 names per algorithm */
static const char *PNAMES[NALG][6] = {
    { "-", "-", "-", "-", "-", "-" },
    { "Size", "Decay", "Damp", "PreDelay", "Tone", "Width" },
    { "Note", "Feedback", "Damp", "PingPong", "Tone", "Width" },
    { "Rate", "Depth", "Center", "Tone", "Width", "Fdbk" },
    { "Rate", "Depth", "Fdbk", "Tone", "Width", "Center" },
    { "Rate", "Center", "Width", "Feedback", "Notch", "S&H" },
    { "Semis", "Fine", "Tone", "Regen", "Width", "Spread" },
    { "Drive", "Tone", "Level", "Bite", "Body", "Width" },
    { "Low", "Mid", "MidFreq", "High", "LowFreq", "HighFreq" },
    { "Rate", "Depth", "Mode", "Sync", "Shape", "Width" },
};
static const char *ROUTE_NAMES[4] = { "Serial", "Parallel", "Feedback 1", "Feedback 2" };
static const char *LINK_NAMES[2] = { "Serial", "Parallel" };
static const char *DLY_NOTES[6] = { "1/8", "1/4D", "1/4", "1/2D", "1/2", "1/1" };
static const float DLY_BEATS[6] = { 0.5f, 0.75f, 1.0f, 1.5f, 2.0f, 4.0f };
static const char *TSYNC_NAMES[5] = { "Off", "1/8", "1/4", "1/2", "1/1" };
static const float TSYNC_BEATS[5] = { 0.0f, 0.5f, 1.0f, 2.0f, 4.0f };

/* musical P1..P6 defaults per algorithm (also the params.json defaults) */
static const float DP_DEF[NALG][6] = {
    { 0, 0, 0, 0, 0, 0 },          /* Off */
    { 55, 60, 45, 0, 60, 70 },     /* Hall Reverb */
    { 50, 35, 40, 70, 60, 70 },    /* Tempo Delay: 1/4, ping-pong */
    { 25, 55, 45, 60, 70, 15 },    /* Chorus */
    { 25, 55, 45, 60, 70, 20 },    /* Flanger */
    { 30, 55, 65, 60, 75, 0 },     /* Phaser-DDL: the marquee */
    { 62, 50, 65, 0, 70, 50 },     /* Pitch Shift: +3 st-ish */
    { 45, 55, 70, 30, 30, 70 },    /* Distortion */
    { 50, 50, 50, 50, 50, 50 },    /* Para EQ: flat */
    { 30, 65, 0, 0, 0, 70 },       /* Tremolo */
};

#define NSLOT 4
#define REV_PD_N 4410   /* reverb predelay ring: 100 ms */

typedef struct {
    int   algo;
    float p[6];     /* 0..100 */
    float mix;      /* 0..1 */
    struct { fxr_t r; float *pd; int pdw, pdlen; bq_t tone[2]; float width; } rev;
    struct { fxd_t d; bq_t tone[2]; float width; } dly;
    struct { fxm_t m; bq_t tone[2]; float width; } mod;
    fxp_t pha;
    struct { pxs_t pl, pr; float regen, fb[2]; bq_t tone[2]; float width; } pit;
    struct { fxdst_t d; float drive, tone, level, width; bq_t bite[2], body[2]; } dst;
    eq3_t eq;
    struct { fxtrem_t t; float rate, depth, width; int pan; } trem;
} slot_t;

typedef struct {
    mpc_engine_t base;
    double bpm;
    slot_t slot[NSLOT];
    int ab_route, cd_route, ab_cd;
    float feedback;             /* 0..0.95 */
    float mix, mix_sm;          /* master mix, smoothed */
    float fb_ab[2], fb_cd[2];   /* per-pair feedback-loop state */
    int disp_rev;               /* HAS_DISPLAY_REV: bump on algo change */
} dp4_t;

static float clampf(float v, float lo, float hi) { return v < lo ? lo : v > hi ? hi : v; }
static float logmap(float v, float lo, float hi) { return lo * powf(hi / lo, v / 100.0f); }
/* option value: wrapper sends the index ("2"); accept a name too */
static int opt(const char **names, int n, const char *v) {
    for (int i = 0; i < n; i++) if (!strcasecmp(names[i], v)) return i;
    if (v[0] >= '0' && v[0] <= '9') { int i = atoi(v); return i >= 0 && i < n ? i : -1; }
    return -1;
}
static void apply_width(float *l, float *r, float w01) {
    float mid = (*l + *r) * 0.5f, side = (*l - *r) * 0.5f;
    side *= w01 * 2.0f;         /* 0.5 = normal stereo */
    *l = mid + side; *r = mid - side;
}
static void tone_set(bq_t t[2], float v) {
    float f = 2000.0f + v / 100.0f * 14000.0f;
    bq_lowpass(&t[0], f, 0.7f); bq_lowpass(&t[1], f, 0.7f);
}

/* refresh one slot's mapped voice state from its params (called at block start) */
static void slot_apply(dp4_t *s, slot_t *sl) {
    float *P = sl->p;
    int c;
    switch (sl->algo) {
    case ALG_VERB:
        fxr_set(&sl->rev.r, 1, 0.4f + P[0] / 100.0f * 1.2f, P[1] / 100.0f, P[2] / 100.0f);
        sl->rev.pdlen = (int)(P[3] / 100.0f * 80.0f * 44.1f);
        if (sl->rev.pdlen >= REV_PD_N) sl->rev.pdlen = REV_PD_N - 1;
        tone_set(sl->rev.tone, P[4]);
        sl->rev.width = P[5] / 100.0f;
        break;
    case ALG_DLY: {
        int ni = (int)(P[0] / 100.0f * 5 + 0.5f); if (ni > 5) ni = 5;
        fxd_set(&sl->dly.d, DLY_BEATS[ni] * 60000.0f / (float)s->bpm,
                P[1] / 100.0f * 0.9f, P[2] / 100.0f, P[3] > 50.0f);
        tone_set(sl->dly.tone, P[4]);
        sl->dly.width = P[5] / 100.0f;
        break; }
    case ALG_CHO:
        fxm_set(&sl->mod.m, 0, 5.0f + P[2] / 100.0f * 20.0f, P[1] / 100.0f * 8.0f,
                logmap(P[0], 0.05f, 5.0f), P[5] / 100.0f * 0.4f);
        tone_set(sl->mod.tone, P[3]);
        sl->mod.width = P[4] / 100.0f;
        break;
    case ALG_FLA:
        fxm_set(&sl->mod.m, 1, 0.5f + P[5] / 100.0f * 7.5f, P[1] / 100.0f * 4.0f,
                logmap(P[0], 0.05f, 5.0f), P[2] / 100.0f * 0.85f);
        tone_set(sl->mod.tone, P[3]);
        sl->mod.width = P[4] / 100.0f;
        break;
    case ALG_PHA:
        sl->pha.bpm = (float)s->bpm;
        fxp_set(&sl->pha, logmap(P[0], 0.05f, 8.0f), logmap(P[1], 100.0f, 5000.0f),
                P[2] / 100.0f, P[3] / 100.0f * 1.9f - 0.95f, P[4] / 100.0f,
                P[5] < 1.0f ? 0.0f : logmap(P[5], 0.5f, 12.0f), 12);
        break;
    case ALG_PIT: {
        float st = P[0] / 100.0f * 24.0f - 12.0f + (P[1] / 100.0f * 100.0f - 50.0f) / 100.0f;
        float spread = (P[5] / 100.0f * 20.0f - 10.0f) / 100.0f;  /* +/-0.1 st L/R */
        pxs_set(&sl->pit.pl, st - spread * 0.5f);
        pxs_set(&sl->pit.pr, st + spread * 0.5f);
        sl->pit.regen = P[3] / 100.0f * 0.8f;
        tone_set(sl->pit.tone, P[2]);
        sl->pit.width = P[4] / 100.0f;
        break; }
    case ALG_DST:
        for (c = 0; c < 2; c++) {
            bq_highshelf(&sl->dst.bite[c], 4000.0f, P[3] / 100.0f * 12.0f);
            bq_lowshelf(&sl->dst.body[c], 200.0f, P[4] / 100.0f * 12.0f);
        }
        sl->dst.drive = P[0] / 100.0f;
        sl->dst.tone = P[1] / 100.0f;
        sl->dst.level = P[2] / 100.0f * 1.5f;
        sl->dst.width = P[5] / 100.0f;
        break;
    case ALG_EQ:
        for (c = 0; c < 2; c++) {
            bq_lowshelf(&sl->eq.lo[c], logmap(P[4], 40.0f, 500.0f), P[0] / 100.0f * 24.0f - 12.0f);
            bq_peak(&sl->eq.mi[c], logmap(P[2], 200.0f, 4000.0f), 1.0f, P[1] / 100.0f * 24.0f - 12.0f);
            bq_highshelf(&sl->eq.hi[c], logmap(P[5], 2000.0f, 16000.0f), P[3] / 100.0f * 24.0f - 12.0f);
        }
        break;
    case ALG_TREM: {
        int sni = (int)(P[3] / 100.0f * 4 + 0.5f); if (sni > 4) sni = 4;
        sl->trem.rate = sni == 0 ? logmap(P[0], 0.1f, 10.0f)
                                 : TSYNC_BEATS[sni] * (float)s->bpm / 60.0f;
        sl->trem.depth = P[1] / 100.0f;
        sl->trem.pan = P[2] > 50.0f;
        sl->trem.t.shape = P[4] / 100.0f;
        sl->trem.width = P[5] / 100.0f;
        break; }
    default: break;
    }
}

/* one slot, one sample; wet_only=1 for the feedback-loop path (all-wet) */
static void slot_run(dp4_t *s, slot_t *sl, float il, float ir,
                     float *ol, float *or, int wet_only) {
    (void)s;
    float wl = 0.0f, wr = 0.0f, t0, t1;
    switch (sl->algo) {
    case ALG_OFF: wl = il; wr = ir; break;
    case ALG_VERB: {
        int rp = sl->rev.pdw - sl->rev.pdlen;
        while (rp < 0) rp += REV_PD_N;
        float pl = sl->rev.pd[rp * 2], pr = sl->rev.pd[rp * 2 + 1];
        sl->rev.pd[sl->rev.pdw * 2] = il; sl->rev.pd[sl->rev.pdw * 2 + 1] = ir;
        sl->rev.pdw = (sl->rev.pdw + 1) % REV_PD_N;
        fxr_run(&sl->rev.r, pl, pr, &wl, &wr);
        wl = bq_run(&sl->rev.tone[0], wl); wr = bq_run(&sl->rev.tone[1], wr);
        apply_width(&wl, &wr, sl->rev.width);
        break; }
    case ALG_DLY:
        fxd_run(&sl->dly.d, il, ir, &wl, &wr);
        wl = bq_run(&sl->dly.tone[0], wl); wr = bq_run(&sl->dly.tone[1], wr);
        apply_width(&wl, &wr, sl->dly.width);
        break;
    case ALG_CHO: case ALG_FLA:
        fxm_run(&sl->mod.m, il, ir, &wl, &wr);
        wl = bq_run(&sl->mod.tone[0], wl); wr = bq_run(&sl->mod.tone[1], wr);
        apply_width(&wl, &wr, sl->mod.width);
        break;
    case ALG_PHA:
        fxp_run(&sl->pha, il, ir, &wl, &wr);
        apply_width(&wl, &wr, sl->p[2] / 100.0f);
        break;
    case ALG_PIT:
        pxs_run(&sl->pit.pl, il + fx_zap(sl->pit.fb[0]) * sl->pit.regen, 0.0f, &wl, &t0);
        pxs_run(&sl->pit.pr, ir + fx_zap(sl->pit.fb[1]) * sl->pit.regen, 0.0f, &t1, &wr);
        sl->pit.fb[0] = fx_zap(wl); sl->pit.fb[1] = fx_zap(wr);
        wl = bq_run(&sl->pit.tone[0], wl); wr = bq_run(&sl->pit.tone[1], wr);
        apply_width(&wl, &wr, sl->pit.width);
        break;
    case ALG_DST: {
        float x0 = bq_run(&sl->dst.body[0], bq_run(&sl->dst.bite[0], il));
        float x1 = bq_run(&sl->dst.body[1], bq_run(&sl->dst.bite[1], ir));
        fxdst_run(&sl->dst.d, sl->dst.drive, sl->dst.tone, sl->dst.level, x0, x1, &wl, &wr);
        apply_width(&wl, &wr, sl->dst.width);
        break; }
    case ALG_EQ:
        eq3_run(&sl->eq, il, ir, &wl, &wr);
        break;
    case ALG_TREM:
        fxtrem_run(&sl->trem.t, sl->trem.rate, sl->trem.depth, sl->trem.pan, il, ir, &wl, &wr);
        apply_width(&wl, &wr, sl->trem.width);
        break;
    }
    if (wet_only) { *ol = wl; *or = wr; }
    else { float m = sl->mix; *ol = il * (1.0f - m) + wl * m; *or = ir * (1.0f - m) + wr * m; }
}

/* one pair (A/B or C/D), one sample */
static void pair_run(dp4_t *s, int ia, int ib, float il, float ir,
                     int route, float *ol, float *or, float *fb) {
    slot_t *A = &s->slot[ia], *B = &s->slot[ib];
    float t0, t1, u0, u1;
    if (route == 0) {                        /* serial */
        slot_run(s, A, il, ir, &t0, &t1, 0);
        slot_run(s, B, t0, t1, ol, or, 0);
    } else if (route == 1) {                 /* parallel */
        slot_run(s, A, il, ir, &t0, &t1, 0);
        slot_run(s, B, il, ir, &u0, &u1, 0);
        *ol = (t0 + u0) * 0.5f; *or = (t1 + u1) * 0.5f;
    } else {                                 /* feedback 1 / 2: all-wet loop */
        float fa = fx_zap(fb[0]), fbv = fx_zap(fb[1]);
        slot_run(s, A, il + fa * s->feedback, ir + fbv * s->feedback, &t0, &t1, 1);
        slot_run(s, B, t0, t1, &u0, &u1, 1);
        fb[0] = fx_zap(u0); fb[1] = fx_zap(u1);
        float m = (A->mix + B->mix) * 0.5f;
        if (route == 2) { *ol = il * (1.0f - m) + u0 * m; *or = ir * (1.0f - m) + u1 * m; }
        else { *ol = u0; *or = u1; }         /* feedback 2: the wash */
    }
}

static void *create(const char *dir) {
    (void)dir;
    dp4_t *s = (dp4_t *)calloc(1, sizeof *s);
    if (!s) return NULL;
    s->bpm = 120.0;
    s->mix = 1.0f; s->mix_sm = 1.0f;
    s->feedback = 0.2f;
    /* default patch: Phaser-DDL > Tempo Delay > Hall Reverb, D off */
    static const int dalg[NSLOT] = { ALG_PHA, ALG_DLY, ALG_VERB, ALG_OFF };
    for (int i = 0; i < NSLOT; i++) {
        slot_t *sl = &s->slot[i];
        sl->algo = dalg[i];
        sl->mix = 1.0f;
        memcpy(sl->p, DP_DEF[dalg[i]], sizeof sl->p);
        fxr_init(&sl->rev.r);
        sl->rev.pd = (float *)calloc((size_t)REV_PD_N * 2, sizeof(float));
        fxd_init(&sl->dly.d, 2000);
        fxm_init(&sl->mod.m);
        fxp_init(&sl->pha);
        /* pxs_t needs no init: zeroed state is valid, pxs_set() runs per block */
        sl->dst.d.tone_set = -1.0f;        /* force tone biquad init on first run */
    }
    for (int i = 0; i < NSLOT; i++) slot_apply(s, &s->slot[i]);
    return s;
}

static void destroy(void *p) {
    dp4_t *s = (dp4_t *)p;
    for (int i = 0; i < NSLOT; i++) {
        slot_t *sl = &s->slot[i];
        fxr_free(&sl->rev.r);
        free(sl->rev.pd);
        fxd_free(&sl->dly.d);
        fxm_free(&sl->mod.m);
        fxp_free(&sl->pha);
    }
    free(s);
}

static void midi(void *p, const uint8_t *m, int n) { (void)p; (void)m; (void)n; }

static void set_param(void *p, const char *k, const char *v) {
    dp4_t *s = (dp4_t *)p;
    int o;
    if (!strcmp(k, "lfo_bpm")) { double b = atof(v); if (b > 1) s->bpm = b; return; }
    if (!strcmp(k, "ab_route")) { o = opt(ROUTE_NAMES, 4, v); if (o >= 0) s->ab_route = o; return; }
    if (!strcmp(k, "cd_route")) { o = opt(ROUTE_NAMES, 4, v); if (o >= 0) s->cd_route = o; return; }
    if (!strcmp(k, "ab_cd"))    { o = opt(LINK_NAMES, 2, v);  if (o >= 0) s->ab_cd = o;    return; }
    if (!strcmp(k, "feedback")) { s->feedback = clampf((float)atof(v), 0, 95) / 100.0f; return; }
    if (!strcmp(k, "mix"))     { s->mix = clampf((float)atof(v), 0, 100) / 100.0f;      return; }
    if (k[0] >= 'a' && k[0] <= 'd' && k[1] == '_') {
        slot_t *sl = &s->slot[k[0] - 'a'];
        const char *sub = k + 2;
        if (!strcmp(sub, "algo")) {
            o = opt(ALG_NAMES, NALG, v);
            if (o >= 0 && o != sl->algo) {
                sl->algo = o;
                memcpy(sl->p, DP_DEF[o], sizeof sl->p);  /* fresh musical defaults */
                s->disp_rev++;  /* wrapper re-reads moved P values + dynamic names */
            }
            return;
        }
        if (!strcmp(sub, "mix")) { sl->mix = clampf((float)atof(v), 0, 100) / 100.0f; return; }
        if (sub[0] == 'p' && sub[1] >= '1' && sub[1] <= '6' && sub[2] == 0) {
            sl->p[sub[1] - '1'] = clampf((float)atof(v), 0, 100);
            return;
        }
    }
}

/* value text for a slot's P1..P6 under its current algorithm */
static int p_display(slot_t *sl, int pi, char *b, int n) {
    float v = sl->p[pi];
    int ni;
    switch (sl->algo) {
    case ALG_VERB:
        switch (pi) {
        case 0: return snprintf(b, n, "%.0f%%", v);
        case 1: return snprintf(b, n, "%.0f%%", v);
        case 2: return snprintf(b, n, "%.0f%%", v);
        case 3: return snprintf(b, n, "%.0f ms", v / 100 * 80);
        case 4: return snprintf(b, n, "%.0f Hz", 2000 + v / 100 * 14000);
        default: return snprintf(b, n, "%.0f%%", v);
        }
    case ALG_DLY:
        switch (pi) {
        case 0: ni = (int)(v / 100 * 5 + 0.5f); if (ni > 5) ni = 5;
                return snprintf(b, n, "%s", DLY_NOTES[ni]);
        case 1: return snprintf(b, n, "%.0f%%", v);
        case 2: return snprintf(b, n, "%.0f%%", v);
        case 3: return snprintf(b, n, "%s", v > 50 ? "On" : "Off");
        case 4: return snprintf(b, n, "%.0f Hz", 2000 + v / 100 * 14000);
        default: return snprintf(b, n, "%.0f%%", v);
        }
    case ALG_CHO:
        switch (pi) {
        case 0: return snprintf(b, n, "%.2f Hz", logmap(v, 0.05f, 5.0f));
        case 1: return snprintf(b, n, "%.1f ms", v / 100 * 8);
        case 2: return snprintf(b, n, "%.1f ms", 5 + v / 100 * 20);
        case 3: return snprintf(b, n, "%.0f Hz", 2000 + v / 100 * 14000);
        case 4: return snprintf(b, n, "%.0f%%", v);
        default: return snprintf(b, n, "%.0f%%", v);
        }
    case ALG_FLA:
        switch (pi) {
        case 0: return snprintf(b, n, "%.2f Hz", logmap(v, 0.05f, 5.0f));
        case 1: return snprintf(b, n, "%.1f ms", v / 100 * 4);
        case 2: return snprintf(b, n, "%.0f%%", v);
        case 3: return snprintf(b, n, "%.0f Hz", 2000 + v / 100 * 14000);
        case 4: return snprintf(b, n, "%.0f%%", v);
        default: return snprintf(b, n, "%.1f ms", 0.5 + v / 100 * 7.5);
        }
    case ALG_PHA:   /* the marquee six, DP/4 Phaser-DDL-style */
        switch (pi) {
        case 0: return snprintf(b, n, "%.2f Hz", logmap(v, 0.05f, 8.0f));
        case 1: return snprintf(b, n, "%.0f Hz", logmap(v, 100.0f, 5000.0f));
        case 2: return snprintf(b, n, "%.0f%%", v);
        case 3: return snprintf(b, n, "%+.0f%%", v / 100 * 190 - 95);
        case 4: return snprintf(b, n, "%.0f%%", v);
        default: return snprintf(b, n, v < 1 ? "Off" : "%.1f Hz", logmap(v, 0.5f, 12.0f));
        }
    case ALG_PIT:
        switch (pi) {
        case 0: return snprintf(b, n, "%+.1f st", v / 100 * 24 - 12);
        case 1: return snprintf(b, n, "%+.0f ct", v / 100 * 100 - 50);
        case 2: return snprintf(b, n, "%.0f Hz", 2000 + v / 100 * 14000);
        case 3: return snprintf(b, n, "%.0f%%", v);
        case 4: return snprintf(b, n, "%.0f%%", v);
        default: return snprintf(b, n, "%+.0f ct", v / 100 * 20 - 10);
        }
    case ALG_DST:
        switch (pi) {
        case 0: return snprintf(b, n, "%.0f%%", v);
        case 1: return snprintf(b, n, "%.0f%%", v);
        case 2: return snprintf(b, n, "%.0f%%", v / 100 * 150);
        case 3: return snprintf(b, n, "%+.0f dB", v / 100 * 12);
        case 4: return snprintf(b, n, "%+.0f dB", v / 100 * 12);
        default: return snprintf(b, n, "%.0f%%", v);
        }
    case ALG_EQ:
        switch (pi) {
        case 0: return snprintf(b, n, "%+.1f dB", v / 100 * 24 - 12);
        case 1: return snprintf(b, n, "%+.1f dB", v / 100 * 24 - 12);
        case 2: return snprintf(b, n, "%.0f Hz", logmap(v, 200.0f, 4000.0f));
        case 3: return snprintf(b, n, "%+.1f dB", v / 100 * 24 - 12);
        case 4: return snprintf(b, n, "%.0f Hz", logmap(v, 40.0f, 500.0f));
        default: return snprintf(b, n, "%.0f Hz", logmap(v, 2000.0f, 16000.0f));
        }
    case ALG_TREM:
        switch (pi) {
        case 0: return snprintf(b, n, "%.2f Hz", logmap(v, 0.1f, 10.0f));
        case 1: return snprintf(b, n, "%.0f%%", v);
        case 2: return snprintf(b, n, "%s", v > 50 ? "Pan" : "Trem");
        case 3: ni = (int)(v / 100 * 4 + 0.5f); if (ni > 4) ni = 4;
                return snprintf(b, n, "%s", TSYNC_NAMES[ni]);
        case 4: return snprintf(b, n, "%.0f%%", v);
        default: return snprintf(b, n, "%.0f%%", v);
        }
    default: return snprintf(b, n, "-");
    }
}

static int get_param(void *p, const char *k, char *b, int n) {
    dp4_t *s = (dp4_t *)p;
    size_t kl = strlen(k);
    if (!strcmp(k, "display_rev")) return snprintf(b, n, "%d", s->disp_rev);
    if (!strcmp(k, "ab_route")) return snprintf(b, n, "%s", ROUTE_NAMES[s->ab_route]);
    if (!strcmp(k, "cd_route")) return snprintf(b, n, "%s", ROUTE_NAMES[s->cd_route]);
    if (!strcmp(k, "ab_cd"))    return snprintf(b, n, "%s", LINK_NAMES[s->ab_cd]);
    if (!strcmp(k, "feedback")) return snprintf(b, n, "%.0f", s->feedback * 100.0f);
    if (!strcmp(k, "mix"))      return snprintf(b, n, "%.0f", s->mix * 100.0f);
    if (k[0] >= 'a' && k[0] <= 'd' && k[1] == '_') {
        slot_t *sl = &s->slot[k[0] - 'a'];
        const char *sub = k + 2;
        /* "<key>_name" / "<key>_display": dynamic names + value text */
        int is_name = kl > 5 && !strcmp(k + kl - 5, "_name");
        int is_disp = kl > 8 && !strcmp(k + kl - 8, "_display");
        char base[16];
        if (is_name || is_disp) {
            size_t bl = kl - (is_name ? 5 : 8);
            if (bl >= sizeof base) return 0;
            memcpy(base, k, bl); base[bl] = 0;
            sub = base + 2;
        }
        if (!strcmp(sub, "algo")) {
            if (is_name) return snprintf(b, n, "Algorithm");
            return snprintf(b, n, "%s", ALG_NAMES[sl->algo]);
        }
        if (!strcmp(sub, "mix")) {
            if (is_name) return snprintf(b, n, "Mix");
            return snprintf(b, n, "%.0f", sl->mix * 100.0f);
        }
        if (sub[0] == 'p' && sub[1] >= '1' && sub[1] <= '6' && sub[2] == 0) {
            int pi = sub[1] - '1';
            if (is_name) return snprintf(b, n, "%s", PNAMES[sl->algo][pi]);
            if (is_disp) return p_display(sl, pi, b, n);
            return snprintf(b, n, "%.1f", sl->p[pi]);
        }
    }
    return 0;
}

static void render(void *p, int16_t *out, int frames) {
    (void)p; memset(out, 0, (size_t)frames * 4);   /* effect: unused */
}

static void process(void *p, const int16_t *in, int16_t *out, int frames) {
    dp4_t *s = (dp4_t *)p;
    for (int i = 0; i < NSLOT; i++) slot_apply(s, &s->slot[i]);
    for (int i = 0; i < frames; i++) {
        float l = in[2 * i] * (1.0f / 32768.0f);
        float r = in[2 * i + 1] * (1.0f / 32768.0f);
        float abl, abr, busl, busr;
        pair_run(s, 0, 1, l, r, s->ab_route, &abl, &abr, s->fb_ab);
        if (s->ab_cd == 0) {
            pair_run(s, 2, 3, abl, abr, s->cd_route, &busl, &busr, s->fb_cd);
        } else {
            float cdl, cdr;
            pair_run(s, 2, 3, l, r, s->cd_route, &cdl, &cdr, s->fb_cd);
            busl = (abl + cdl) * 0.5f; busr = (abr + cdr) * 0.5f;
        }
        s->mix_sm += (s->mix - s->mix_sm) * 0.02f;
        float m = s->mix_sm;
        float ol = l * (1.0f - m) + busl * m;
        float orr = r * (1.0f - m) + busr * m;
        /* soft safety limiter */
        ol = ol / (1.0f + fabsf(ol) * 0.25f);
        orr = orr / (1.0f + fabsf(orr) * 0.25f);
        int v = (int)(ol * 32767.0f), wv = (int)(orr * 32767.0f);
        out[2 * i] = v > 32767 ? 32767 : v < -32768 ? -32768 : (int16_t)v;
        out[2 * i + 1] = wv > 32767 ? 32767 : wv < -32768 ? -32768 : (int16_t)wv;
    }
}

static const mpc_engine_t ENGINE = { create, destroy, midi, set_param, get_param, render, process };
const mpc_engine_t *mpc_engine(void) { return &ENGINE; }
