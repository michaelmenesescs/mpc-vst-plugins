/* quadraverb: a QuadraVerb-inspired multi-FX for MPC OS.
 *
 * Clean-room reimplementation of the *concept* of the Alesis QuadraVerb (1990s
 * rack multi-FX): a curated set of series/parallel signal-path configurations
 * combining reverb, delay, chorus, flanger, phaser, pitch shift, EQ, resonator,
 * ring modulation and tremolo, with a slightly grainy character. No Alesis code,
 * presets, or assets are used or copied; all DSP here is fresh C (src/dsp/).
 *
 * Effect port: the wrapper (PLUG_EFFECT) feeds 128-frame int16 stereo blocks to
 * process(). Structural params (config) take effect at the next block; time-based
 * params are de-clicked inside the DSP blocks.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include "engine.h"
#include "dsp/fxdsp.h"

/* config ids */
enum { CFG_PITCH_DLY_VERB, CFG_CHORUS_DLY_VERB, CFG_FLANGE_DLY_VERB,
       CFG_PHASER_VERB, CFG_TREM_DLY_VERB, CFG_RESO_RING_VERB, NCFG };
static const char *CFG_NAMES[NCFG] = {
    "Pitch>Dly>Verb", "Chorus>Dly>Verb", "Flange>Dly>Verb",
    "Phaser>Verb", "Trem>Dly>Verb", "Reso+Ring>Verb"
};
static const char *REV_NAMES[4] = { "Room", "Hall", "Plate", "Small" };
static const char *SYNC_NAMES[6] = { "Off", "1/8", "1/4D", "1/4", "1/2D", "1/2" };
static const double SYNC_BEATS[6] = { 0, 0.5, 0.75, 1.0, 1.5, 2.0 };
static const char *STAGE_NAMES[3] = { "4", "6", "8" };
static const int STAGE_VALS[3] = { 4, 6, 8 };
static const char *TREM_NAMES[2] = { "Tremolo", "AutoPan" };

typedef struct {
    /* params */
    int config, rev_type, dly_sync, pha_stages, trem_mode;
    float eq_low, eq_mid, eq_midfq, eq_high;
    float rev_size, rev_decay, rev_damp, rev_mix;
    float dly_ms, dly_fb, dly_damp, dly_mix;
    float cho_rate, cho_depth, cho_mix;
    float fla_rate, fla_depth, fla_fb, fla_mix;
    float pha_rate, pha_depth, pha_mix;
    float pit_semi, pit_mix;
    float res_freq, res_reso, res_mix;
    float ring_rate, ring_mix;
    float trem_rate, trem_depth;
    float mix;
    double bpm;
    /* dsp */
    eq3_t eq;
    fxr_t rev;
    fxd_t dly;
    fxm_t cho, fla;
    fxp_t pha;
    pxs_t pit;
    fxres_t res;
    fxring_t ring;
    fxtrem_t trem;
    fxs_t wet;   /* smoothed master wet */
} qv_t;

static float clampf(float v, float lo, float hi) { return v < lo ? lo : v > hi ? hi : v; }
/* option value: wrapper sends the index ("2"); accept a name too */
static int opt(const char **names, int n, const char *v) {
    for (int i = 0; i < n; i++) if (!strcasecmp(names[i], v)) return i;
    if (v[0] >= '0' && v[0] <= '9') { int i = atoi(v); return i >= 0 && i < n ? i : -1; }
    return -1;
}

static void *create(const char *dir) {
    (void)dir;
    qv_t *s = (qv_t *)calloc(1, sizeof *s);
    if (!s) return NULL;
    fxr_init(&s->rev);
    fxd_init(&s->dly, 2000);
    fxm_init(&s->cho); fxm_init(&s->fla);
    fxp_init(&s->pha);
    s->bpm = 120.0;
    s->wet.cur = s->wet.tgt = 0.5f;
    /* defaults (also in params.json) */
    s->config = 1; s->rev_type = 1; s->dly_sync = 3; s->pha_stages = 1;
    s->eq_low = 0; s->eq_mid = 0; s->eq_midfq = 800; s->eq_high = 0;
    s->rev_size = 70; s->rev_decay = 55; s->rev_damp = 40; s->rev_mix = 35;
    s->dly_ms = 375; s->dly_fb = 35; s->dly_damp = 25; s->dly_mix = 30;
    s->cho_rate = 0.8f; s->cho_depth = 60; s->cho_mix = 40;
    s->fla_rate = 0.4f; s->fla_depth = 70; s->fla_fb = 40; s->fla_mix = 0;
    s->pha_rate = 0.5f; s->pha_depth = 70; s->pha_mix = 0;
    s->pit_semi = 0; s->pit_mix = 0;
    s->res_freq = 800; s->res_reso = 60; s->res_mix = 0;
    s->ring_rate = 220; s->ring_mix = 0;
    s->trem_rate = 4; s->trem_depth = 60;
    s->mix = 60;
    return s;
}

static void destroy(void *p) {
    qv_t *s = (qv_t *)p;
    fxr_free(&s->rev); fxd_free(&s->dly); fxm_free(&s->cho); fxm_free(&s->fla);
    fxp_free(&s->pha);
    free(s);
}

static void midi(void *p, const uint8_t *m, int n) { (void)p; (void)m; (void)n; }

/* apply current params to the dsp blocks (called at block start) */
static void apply(qv_t *s) {
    eq3_set(&s->eq, s->eq_low, s->eq_mid, s->eq_midfq, s->eq_high);
    fxr_set(&s->rev, s->rev_type, s->rev_size / 100.0f * 1.2f + 0.2f,
            s->rev_decay / 100.0f, s->rev_damp / 100.0f);
    float dms = s->dly_ms;
    /* sync values are in beats (0.5 = 8th); a beat is 60000/bpm ms */
    if (s->dly_sync > 0 && s->bpm > 1.0)
        dms = (float)(SYNC_BEATS[s->dly_sync] * 60000.0 / s->bpm);
    fxd_set(&s->dly, dms, s->dly_fb / 100.0f, s->dly_damp / 100.0f, 0);
    fxm_set(&s->cho, 0, 14.0f, s->cho_depth / 100.0f * 9.0f, s->cho_rate, 0.0f);
    fxm_set(&s->fla, 1, 3.5f, s->fla_depth / 100.0f * 3.0f, s->fla_rate, s->fla_fb / 100.0f);
    s->pha.bpm = (float)s->bpm;
    fxp_set(&s->pha, s->pha_rate, 900.0f, s->pha_depth / 100.0f, 0.45f, 0.85f, 0.0f,
            STAGE_VALS[s->pha_stages]);
    pxs_set(&s->pit, s->pit_semi);
    fxres_set(&s->res, s->res_freq, s->res_reso / 100.0f);
    fxs_set(&s->wet, s->mix / 100.0f);
}

static void set_param(void *p, const char *k, const char *v) {
    qv_t *s = (qv_t *)p;
    int o;
    if (!strcmp(k, "config")) { o = opt(CFG_NAMES, NCFG, v); if (o >= 0) s->config = o; }
    else if (!strcmp(k, "eq_low")) s->eq_low = clampf(atof(v), -12, 12);
    else if (!strcmp(k, "eq_mid")) s->eq_mid = clampf(atof(v), -12, 12);
    else if (!strcmp(k, "eq_midfreq")) s->eq_midfq = clampf(atof(v), 200, 4000);
    else if (!strcmp(k, "eq_high")) s->eq_high = clampf(atof(v), -12, 12);
    else if (!strcmp(k, "rev_type")) { o = opt(REV_NAMES, 4, v); if (o >= 0) s->rev_type = o; }
    else if (!strcmp(k, "rev_size")) s->rev_size = clampf(atof(v), 20, 100);
    else if (!strcmp(k, "rev_decay")) s->rev_decay = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "rev_damp")) s->rev_damp = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "rev_mix")) s->rev_mix = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "dly_sync")) { o = opt(SYNC_NAMES, 6, v); if (o >= 0) s->dly_sync = o; }
    else if (!strcmp(k, "dly_time")) s->dly_ms = clampf(atof(v), 1, 2000);
    else if (!strcmp(k, "dly_fb")) s->dly_fb = clampf(atof(v), 0, 95);
    else if (!strcmp(k, "dly_damp")) s->dly_damp = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "dly_mix")) s->dly_mix = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "cho_rate")) s->cho_rate = clampf(atof(v), 0.05f, 5);
    else if (!strcmp(k, "cho_depth")) s->cho_depth = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "cho_mix")) s->cho_mix = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "fla_rate")) s->fla_rate = clampf(atof(v), 0.05f, 5);
    else if (!strcmp(k, "fla_depth")) s->fla_depth = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "fla_fb")) s->fla_fb = clampf(atof(v), 0, 80);
    else if (!strcmp(k, "fla_mix")) s->fla_mix = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "pha_rate")) s->pha_rate = clampf(atof(v), 0.05f, 5);
    else if (!strcmp(k, "pha_depth")) s->pha_depth = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "pha_stages")) { o = opt(STAGE_NAMES, 3, v); if (o >= 0) s->pha_stages = o; }
    else if (!strcmp(k, "pha_mix")) s->pha_mix = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "pit_semi")) s->pit_semi = clampf(atof(v), -12, 12);
    else if (!strcmp(k, "pit_mix")) s->pit_mix = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "res_freq")) s->res_freq = clampf(atof(v), 100, 8000);
    else if (!strcmp(k, "res_reso")) s->res_reso = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "res_mix")) s->res_mix = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "ring_rate")) s->ring_rate = clampf(atof(v), 0.5f, 2000);
    else if (!strcmp(k, "ring_mix")) s->ring_mix = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "trem_rate")) s->trem_rate = clampf(atof(v), 0.1f, 10);
    else if (!strcmp(k, "trem_depth")) s->trem_depth = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "trem_mode")) { o = opt(TREM_NAMES, 2, v); if (o >= 0) s->trem_mode = o; }
    else if (!strcmp(k, "mix")) s->mix = clampf(atof(v), 0, 100);
    else if (!strcmp(k, "lfo_bpm")) { double b = atof(v); if (b > 1) s->bpm = b; }
}

static int get_param(void *p, const char *k, char *b, int n) {
    qv_t *s = (qv_t *)p;
    if (!strcmp(k, "config")) return snprintf(b, n, "%s", CFG_NAMES[s->config]);
    if (!strcmp(k, "eq_low")) return snprintf(b, n, "%.1f", s->eq_low);
    if (!strcmp(k, "eq_mid")) return snprintf(b, n, "%.1f", s->eq_mid);
    if (!strcmp(k, "eq_midfreq")) return snprintf(b, n, "%.0f", s->eq_midfq);
    if (!strcmp(k, "eq_high")) return snprintf(b, n, "%.1f", s->eq_high);
    if (!strcmp(k, "rev_type")) return snprintf(b, n, "%s", REV_NAMES[s->rev_type]);
    if (!strcmp(k, "rev_size")) return snprintf(b, n, "%.0f", s->rev_size);
    if (!strcmp(k, "rev_decay")) return snprintf(b, n, "%.0f", s->rev_decay);
    if (!strcmp(k, "rev_damp")) return snprintf(b, n, "%.0f", s->rev_damp);
    if (!strcmp(k, "rev_mix")) return snprintf(b, n, "%.0f", s->rev_mix);
    if (!strcmp(k, "dly_sync")) return snprintf(b, n, "%s", SYNC_NAMES[s->dly_sync]);
    if (!strcmp(k, "dly_time")) return snprintf(b, n, "%.0f", s->dly_ms);
    if (!strcmp(k, "dly_fb")) return snprintf(b, n, "%.0f", s->dly_fb);
    if (!strcmp(k, "dly_damp")) return snprintf(b, n, "%.0f", s->dly_damp);
    if (!strcmp(k, "dly_mix")) return snprintf(b, n, "%.0f", s->dly_mix);
    if (!strcmp(k, "cho_rate")) return snprintf(b, n, "%.2f", s->cho_rate);
    if (!strcmp(k, "cho_depth")) return snprintf(b, n, "%.0f", s->cho_depth);
    if (!strcmp(k, "cho_mix")) return snprintf(b, n, "%.0f", s->cho_mix);
    if (!strcmp(k, "fla_rate")) return snprintf(b, n, "%.2f", s->fla_rate);
    if (!strcmp(k, "fla_depth")) return snprintf(b, n, "%.0f", s->fla_depth);
    if (!strcmp(k, "fla_fb")) return snprintf(b, n, "%.0f", s->fla_fb);
    if (!strcmp(k, "fla_mix")) return snprintf(b, n, "%.0f", s->fla_mix);
    if (!strcmp(k, "pha_rate")) return snprintf(b, n, "%.2f", s->pha_rate);
    if (!strcmp(k, "pha_depth")) return snprintf(b, n, "%.0f", s->pha_depth);
    if (!strcmp(k, "pha_stages")) return snprintf(b, n, "%s", STAGE_NAMES[s->pha_stages]);
    if (!strcmp(k, "pha_mix")) return snprintf(b, n, "%.0f", s->pha_mix);
    if (!strcmp(k, "pit_semi")) return snprintf(b, n, "%.0f", s->pit_semi);
    if (!strcmp(k, "pit_mix")) return snprintf(b, n, "%.0f", s->pit_mix);
    if (!strcmp(k, "res_freq")) return snprintf(b, n, "%.0f", s->res_freq);
    if (!strcmp(k, "res_reso")) return snprintf(b, n, "%.0f", s->res_reso);
    if (!strcmp(k, "res_mix")) return snprintf(b, n, "%.0f", s->res_mix);
    if (!strcmp(k, "ring_rate")) return snprintf(b, n, "%.1f", s->ring_rate);
    if (!strcmp(k, "ring_mix")) return snprintf(b, n, "%.0f", s->ring_mix);
    if (!strcmp(k, "trem_rate")) return snprintf(b, n, "%.2f", s->trem_rate);
    if (!strcmp(k, "trem_depth")) return snprintf(b, n, "%.0f", s->trem_depth);
    if (!strcmp(k, "trem_mode")) return snprintf(b, n, "%s", TREM_NAMES[s->trem_mode]);
    if (!strcmp(k, "mix")) return snprintf(b, n, "%.0f", s->mix);
    return 0;
}

/* run one block through the active config; tmp holds the wet path */
static void run_config(qv_t *s, float l, float rr, float *ol, float *orr) {
    float a[2], b[2], w[2];
    int cfg = s->config;
    /* input EQ first, always */
    eq3_run(&s->eq, l, rr, &a[0], &a[1]);
    if (cfg == CFG_PITCH_DLY_VERB) {
        pxs_run(&s->pit, a[0], a[1], &b[0], &b[1]);
        a[0] += b[0] * (s->pit_mix / 100.0f); a[1] += b[1] * (s->pit_mix / 100.0f);
    }
    if (cfg == CFG_CHORUS_DLY_VERB) {
        fxm_run(&s->cho, a[0], a[1], &b[0], &b[1]);
        a[0] += b[0] * (s->cho_mix / 100.0f); a[1] += b[1] * (s->cho_mix / 100.0f);
    }
    if (cfg == CFG_FLANGE_DLY_VERB) {
        fxm_run(&s->fla, a[0], a[1], &b[0], &b[1]);
        a[0] += b[0] * (s->fla_mix / 100.0f); a[1] += b[1] * (s->fla_mix / 100.0f);
    }
    if (cfg == CFG_TREM_DLY_VERB)
        fxtrem_run(&s->trem, s->trem_rate, s->trem_depth / 100.0f, s->trem_mode, a[0], a[1], &a[0], &a[1]);
    if (cfg == CFG_PITCH_DLY_VERB || cfg == CFG_CHORUS_DLY_VERB ||
        cfg == CFG_FLANGE_DLY_VERB || cfg == CFG_TREM_DLY_VERB) {
        fxd_run(&s->dly, a[0], a[1], &b[0], &b[1]);
        a[0] += b[0] * (s->dly_mix / 100.0f); a[1] += b[1] * (s->dly_mix / 100.0f);
    }
    if (cfg == CFG_PHASER_VERB) {
        fxp_run(&s->pha, a[0], a[1], &b[0], &b[1]);
        a[0] += b[0] * (s->pha_mix / 100.0f); a[1] += b[1] * (s->pha_mix / 100.0f);
    }
    if (cfg == CFG_RESO_RING_VERB) {
        float r1[2], r2[2];
        fxres_run(&s->res, a[0], a[1], &r1[0], &r1[1]);
        fxring_run(&s->ring, s->ring_rate, a[0], a[1], &r2[0], &r2[1]);
        a[0] += r1[0] * (s->res_mix / 100.0f) + r2[0] * (s->ring_mix / 100.0f);
        a[1] += r1[1] * (s->res_mix / 100.0f) + r2[1] * (s->ring_mix / 100.0f);
    }
    fxr_run(&s->rev, a[0], a[1], &b[0], &b[1]);
    a[0] += b[0] * (s->rev_mix / 100.0f); a[1] += b[1] * (s->rev_mix / 100.0f);
    w[0] = a[0]; w[1] = a[1];
    /* master wet/dry against the original input */
    float m = fxs_next(&s->wet);
    *ol = l * (1.0f - m) + w[0] * m;
    *orr = rr * (1.0f - m) + w[1] * m;
}

static void render(void *p, int16_t *out, int frames) {
    (void)p; memset(out, 0, (size_t)frames * 4);   /* effect: unused */
}

static void process(void *p, const int16_t *in, int16_t *out, int frames) {
    qv_t *s = (qv_t *)p;
    apply(s);
    for (int i = 0; i < frames; i++) {
        float l = in[2 * i] * (1.0f / 32768.0f);
        float r = in[2 * i + 1] * (1.0f / 32768.0f);
        float ol, orr;
        run_config(s, l, r, &ol, &orr);
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
