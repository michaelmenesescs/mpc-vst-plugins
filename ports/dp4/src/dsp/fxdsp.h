/* fxdsp.h — small fresh-C DSP blocks for MPC OS FX ports.
 * 44.1 kHz, float samples. Written clean-room for these ports; no third-party DSP.
 * All state lives in the structs; allocate delay memory in create() (never on the
 * audio thread) and free it in destroy(). */
#pragma once
#include <stdlib.h>
#include <string.h>
#include <math.h>

#ifndef FX_SR
#define FX_SR 44100.0f
#endif

static inline float fx_zap(float x) { return (x > -1e-18f && x < 1e-18f) ? 0.0f : x; }
static inline float fx_clampf(float x, float lo, float hi) { return x < lo ? lo : x > hi ? hi : x; }

/* --- biquad (RBJ cookbook) --- */
typedef struct { float b0, b1, b2, a1, a2, x1, x2, y1, y2; } bq_t;
void bq_lowshelf(bq_t *f, float freq, float db);
void bq_highshelf(bq_t *f, float freq, float db);
void bq_peak(bq_t *f, float freq, float q, float db);
void bq_lowpass(bq_t *f, float freq, float q);
void bq_highpass(bq_t *f, float freq, float q);
void bq_bandpass(bq_t *f, float freq, float q);
static inline float bq_run(bq_t *f, float x) {
    float y = f->b0 * x + f->b1 * f->x1 + f->b2 * f->x2 - f->a1 * f->y1 - f->a2 * f->y2;
    f->x2 = f->x1; f->x1 = x; f->y2 = f->y1; f->y1 = y;
    return y;
}
static inline void bq_reset(bq_t *f) { f->x1 = f->x2 = f->y1 = f->y2 = 0.0f; }

/* --- reverb: stereo Schroeder/Moorer (4 combs + 2 allpass per channel) --- */
#define FXR_NCOMB 4
#define FXR_NAP 2
typedef struct {
    float *cb[FXR_NCOMB][2]; int clen[FXR_NCOMB]; int cp[FXR_NCOMB][2];
    float cfb[FXR_NCOMB]; float cdamp[FXR_NCOMB][2];
    float *ab[FXR_NAP][2]; int alen[FXR_NAP]; int ap[FXR_NAP][2];
    float size, decay, damp;
} fxr_t;
void fxr_init(fxr_t *r);   /* allocates */
void fxr_free(fxr_t *r);
void fxr_set(fxr_t *r, int type, float size, float decay, float damp);
/* wet-only stereo out */
void fxr_run(fxr_t *r, float l, float rr, float *ol, float *orr);

/* --- delay: stereo, tempo-able, damped feedback, ping-pong --- */
typedef struct {
    float *b; int n, w;
    float t_cur, t_tgt;   /* delay time, samples (smoothed) */
    float fb, damp, ds[2];
    int pingpong;
} fxd_t;
void fxd_init(fxd_t *d, int maxms);  /* allocates */
void fxd_free(fxd_t *d);
void fxd_set(fxd_t *d, float ms, float fb, float damp, int pingpong);
void fxd_run(fxd_t *d, float l, float rr, float *ol, float *orr);  /* wet only */

/* --- chorus / flanger: modulated delay --- */
typedef struct {
    float *b; int n, w;
    float base_ms, depth_ms, rate, fb;
    float ph;
    int flanger;
} fxm_t;
void fxm_init(fxm_t *m);  /* allocates 60 ms */
void fxm_free(fxm_t *m);
void fxm_set(fxm_t *m, int flanger, float base_ms, float depth_ms, float rate, float fb);
void fxm_run(fxm_t *m, float l, float rr, float *ol, float *orr);  /* wet only */

/* --- phaser: DP/4 Phaser-DDL-inspired. LFO-swept allpass chain (up to 12 stages)
 * with bipolar feedback, notch depth, stereo LFO phase, sample-and-hold on the
 * LFO, and a tempo-synced ping-pong DDL tail. Behavioral reference only:
 * the DP/4+ manual's Phaser-DDL params (center, width, feedback, notch depth,
 * L/R LFO phase, S&H rate, L/R delay, DDL feedback) and the Dusty Devices
 * Phaser-DDL (cycle-accurate DP/4 phaser emulation). No code copied. */
#define FXP_MAX 12
typedef struct {
    float x1[FXP_MAX][2], y1[FXP_MAX][2];
    float ph, sh_timer, sh_val;
    float rate, center, width, fb, notch, sh_rate;
    float fbs[2];
    int stages;
    fxd_t ddl;      /* ping-pong DDL tail, tempo-synced */
    float bpm;
} fxp_t;
void fxp_init(fxp_t *p);   /* inits the DDL; call once */
void fxp_free(fxp_t *p);
void fxp_set(fxp_t *p, float rate_hz, float center_hz, float width_01,
             float fb_bipolar, float notch_01, float sh_rate_hz, int stages);
void fxp_run(fxp_t *p, float l, float rr, float *ol, float *orr);  /* wet only */

/* --- pitch shifter: granular overlap-add, +/-12 st --- */
#define PXS_G 1024
#define PXS_HOP 256
typedef struct {
    float inb[4 * PXS_G]; int iw;              /* interleaved stereo input ring */
    float acc[2 * (PXS_G + PXS_HOP)]; int ar, since;  /* interleaved stereo OLA acc */
    float st;
} pxs_t;
void pxs_set(pxs_t *p, float semitones);
void pxs_run(pxs_t *p, float l, float rr, float *ol, float *orr);  /* wet only */

/* --- 3-band EQ --- */
typedef struct { bq_t lo[2], mi[2], hi[2]; } eq3_t;
void eq3_set(eq3_t *e, float low_db, float mid_db, float mid_hz, float high_db);
static inline void eq3_run(eq3_t *e, float l, float rr, float *ol, float *orr) {
    *ol = bq_run(&e->hi[0], bq_run(&e->mi[0], bq_run(&e->lo[0], l)));
    *orr = bq_run(&e->hi[1], bq_run(&e->mi[1], bq_run(&e->lo[1], rr)));
}

/* --- resonator: 3 parallel resonant bandpasses --- */
typedef struct { bq_t b[3][2]; } fxres_t;
void fxres_set(fxres_t *r, float freq, float reso);  /* reso 0..1 */
void fxres_run(fxres_t *r, float l, float rr, float *ol, float *orr);  /* wet only */

/* --- ring modulator --- */
typedef struct { float ph; } fxring_t;
void fxring_run(fxring_t *r, float rate_hz, float l, float rr, float *ol, float *orr);

/* --- tremolo / autopan --- */
typedef struct { float ph; float shape; /* 0=sine .. 1=square-ish */ } fxtrem_t;
void fxtrem_run(fxtrem_t *t, float rate_hz, float depth, int pan, float l, float rr, float *ol, float *orr);

/* --- distortion: soft-clip waveshaper --- */
typedef struct { bq_t tone[2]; float tone_set; } fxdst_t;
void fxdst_run(fxdst_t *d, float drive, float tone, float level, float l, float rr, float *ol, float *orr);

/* --- one-pole smoothed gain --- */
typedef struct { float cur, tgt; } fxs_t;
static inline void fxs_set(fxs_t *s, float v) { s->tgt = v; }
static inline float fxs_next(fxs_t *s) { s->cur += (s->tgt - s->cur) * 0.02f; return s->cur; }
