/* fxdsp.c — implementations for fxdsp.h. Fresh clean-room DSP. */
#include "fxdsp.h"

#define TAU 6.283185307179586f

/* --- biquads (RBJ cookbook) --- */
static void bq_norm(bq_t *f, float b0, float b1, float b2, float a0, float a1, float a2) {
    f->b0 = b0 / a0; f->b1 = b1 / a0; f->b2 = b2 / a0; f->a1 = a1 / a0; f->a2 = a2 / a0;
}
void bq_lowshelf(bq_t *f, float freq, float db) {
    float A = powf(10.0f, db / 40.0f), w = TAU * freq / FX_SR, c = cosf(w), s = sinf(w);
    float b = 2.0f * sqrtf(A), a0 = (A + 1.0f) + (A - 1.0f) * c + b * s;
    bq_norm(f, A * ((A + 1.0f) - (A - 1.0f) * c + b * s), 2.0f * A * ((A - 1.0f) - (A + 1.0f) * c),
            A * ((A + 1.0f) - (A - 1.0f) * c - b * s), a0, -2.0f * ((A - 1.0f) + (A + 1.0f) * c), (A + 1.0f) + (A - 1.0f) * c - b * s);
}
void bq_highshelf(bq_t *f, float freq, float db) {
    float A = powf(10.0f, db / 40.0f), w = TAU * freq / FX_SR, c = cosf(w), s = sinf(w);
    float b = 2.0f * sqrtf(A), a0 = (A + 1.0f) - (A - 1.0f) * c + b * s;
    bq_norm(f, A * ((A + 1.0f) + (A - 1.0f) * c + b * s), -2.0f * A * ((A - 1.0f) + (A + 1.0f) * c),
            A * ((A + 1.0f) + (A - 1.0f) * c - b * s), a0, 2.0f * ((A - 1.0f) - (A + 1.0f) * c), (A + 1.0f) - (A - 1.0f) * c - b * s);
}
void bq_peak(bq_t *f, float freq, float q, float db) {
    float A = powf(10.0f, db / 40.0f), w = TAU * freq / FX_SR, c = cosf(w), s = sinf(w), al = s / (2.0f * q);
    bq_norm(f, 1.0f + al * A, -2.0f * c, 1.0f - al * A, 1.0f + al / A, -2.0f * c, 1.0f - al / A);
}
void bq_lowpass(bq_t *f, float freq, float q) {
    float w = TAU * freq / FX_SR, c = cosf(w), s = sinf(w), al = s / (2.0f * q);
    bq_norm(f, (1.0f - c) / 2.0f, 1.0f - c, (1.0f - c) / 2.0f, 1.0f + al, -2.0f * c, 1.0f - al);
}
void bq_highpass(bq_t *f, float freq, float q) {
    float w = TAU * freq / FX_SR, c = cosf(w), s = sinf(w), al = s / (2.0f * q);
    bq_norm(f, (1.0f + c) / 2.0f, -(1.0f + c), (1.0f + c) / 2.0f, 1.0f + al, -2.0f * c, 1.0f - al);
}
void bq_bandpass(bq_t *f, float freq, float q) {
    float w = TAU * freq / FX_SR, c = cosf(w), s = sinf(w), al = s / (2.0f * q);
    bq_norm(f, al, 0.0f, -al, 1.0f + al, -2.0f * c, 1.0f - al);
}

/* --- reverb --- */
/* Freeverb-ish tunings (samples @44.1k); type scales decay/damping character. */
static const int RC_TUNE[FXR_NCOMB] = { 1116, 1188, 1277, 1356 };
static const int RA_TUNE[FXR_NAP] = { 556, 441 };
void fxr_init(fxr_t *r) {
    memset(r, 0, sizeof *r);
    for (int i = 0; i < FXR_NCOMB; i++) {
        r->clen[i] = (int)(RC_TUNE[i] * 1.5f) + 8;
        for (int c = 0; c < 2; c++) { r->cb[i][c] = (float *)calloc((size_t)r->clen[i], sizeof(float)); }
    }
    for (int i = 0; i < FXR_NAP; i++) {
        r->alen[i] = (int)(RA_TUNE[i] * 1.5f) + 8;
        for (int c = 0; c < 2; c++) { r->ab[i][c] = (float *)calloc((size_t)r->alen[i], sizeof(float)); }
    }
    r->size = 1.0f; r->decay = 0.5f; r->damp = 0.5f;
}
void fxr_free(fxr_t *r) {
    for (int i = 0; i < FXR_NCOMB; i++) for (int c = 0; c < 2; c++) free(r->cb[i][c]);
    for (int i = 0; i < FXR_NAP; i++) for (int c = 0; c < 2; c++) free(r->ab[i][c]);
    memset(r, 0, sizeof *r);
}
void fxr_set(fxr_t *r, int type, float size, float decay, float damp) {
    /* type: 0 Room, 1 Hall, 2 Plate, 3 Small — character multipliers */
    static const float tdec[4] = { 0.82f, 1.0f, 0.9f, 0.62f };
    static const float tdmp[4] = { 0.55f, 0.35f, 0.25f, 0.7f };
    type &= 3;
    r->size = fx_clampf(size, 0.4f, 1.6f);
    r->decay = fx_clampf(decay, 0.0f, 0.985f) * tdec[type];
    if (r->decay > 0.985f) r->decay = 0.985f;
    r->damp = fx_clampf(damp, 0.0f, 1.0f) * 0.6f + tdmp[type] * 0.4f;
    for (int i = 0; i < FXR_NCOMB; i++) r->cfb[i] = r->decay;
}
void fxr_run(fxr_t *r, float l, float rr, float *ol, float *orr) {
    float wet[2] = { 0.0f, 0.0f };
    float in[2] = { l, rr };
    for (int c = 0; c < 2; c++) {
        float acc = 0.0f;
        for (int i = 0; i < FXR_NCOMB; i++) {
            int len = (int)(RC_TUNE[i] * r->size);
            if (len >= r->clen[i]) len = r->clen[i] - 1;
            if (len < 8) len = 8;
            int p = r->cp[i][c] % len;
            float v = r->cb[i][c][p];
            /* damping: one-pole lowpass in the feedback path (damp 0 = bright, 1 = dark) */
            float k = 1.0f - r->damp * 0.97f;
            r->cdamp[i][c] += k * (v - r->cdamp[i][c]);
            float fbv = fx_zap(r->cdamp[i][c]);
            r->cb[i][c][p] = in[c] + fbv * r->cfb[i];
            if (++r->cp[i][c] >= r->clen[i]) r->cp[i][c] = 0;
            acc += v;
        }
        /* series allpasses */
        for (int i = 0; i < FXR_NAP; i++) {
            int len = (int)(RA_TUNE[i] * r->size);
            if (len >= r->alen[i]) len = r->alen[i] - 1;
            if (len < 8) len = 8;
            int p = r->ap[i][c] % len;
            float bv = r->ab[i][c][p];
            float y = -0.5f * acc + bv;
            r->ab[i][c][p] = acc + 0.5f * bv;
            r->ap[i][c]++;
            acc = y;
        }
        wet[c] = acc * 0.25f;
    }
    *ol = wet[0]; *orr = wet[1];
}

/* --- delay --- */
void fxd_init(fxd_t *d, int maxms) {
    memset(d, 0, sizeof *d);
    d->n = (int)(FX_SR * maxms / 1000.0f) + 8;
    d->b = (float *)calloc((size_t)d->n * 2, sizeof(float));
    d->t_cur = d->t_tgt = FX_SR * 0.375f;
}
void fxd_free(fxd_t *d) { free(d->b); memset(d, 0, sizeof *d); }
void fxd_set(fxd_t *d, float ms, float fb, float damp, int pingpong) {
    d->t_tgt = fx_clampf(ms, 1.0f, (d->n - 8) * 1000.0f / FX_SR) * FX_SR / 1000.0f;
    d->fb = fx_clampf(fb, 0.0f, 0.95f);
    d->damp = fx_clampf(damp, 0.0f, 1.0f);
    d->pingpong = pingpong ? 1 : 0;
}
void fxd_run(fxd_t *d, float l, float rr, float *ol, float *orr) {
    d->t_cur += (d->t_tgt - d->t_cur) * 0.004f;   /* de-click time changes */
    float t = d->t_cur;
    int i0 = (int)t, f = (int)((t - i0) * 256.0f);
    float out[2];
    for (int c = 0; c < 2; c++) {
        int rp = d->w - i0;
        while (rp < 0) rp += d->n;
        int rp2 = rp - 1; if (rp2 < 0) rp2 += d->n;
        float v = d->b[rp * 2 + c] + (d->b[rp2 * 2 + c] - d->b[rp * 2 + c]) * (f / 256.0f);
        out[c] = fx_zap(v);
    }
    /* feedback with damping; ping-pong crosses the feedback between channels */
    float in[2] = { l, rr };
    for (int c = 0; c < 2; c++) {
        float fbsrc = d->pingpong ? out[c ^ 1] : out[c];
        d->ds[c] += (1.0f - d->damp) * 0.5f * (fbsrc - d->ds[c]);
        float fbv = fx_zap(fbsrc * (1.0f - d->damp * 0.5f) + d->ds[c] * d->damp * 0.5f);
        d->b[d->w * 2 + c] = in[c] + fbv * d->fb;
    }
    d->w = (d->w + 1) % d->n;
    *ol = out[0]; *orr = out[1];
}

/* --- chorus / flanger --- */
void fxm_init(fxm_t *m) {
    memset(m, 0, sizeof *m);
    m->n = (int)(FX_SR * 60.0f / 1000.0f) + 8;
    m->b = (float *)calloc((size_t)m->n * 2, sizeof(float));
    m->base_ms = 15.0f;
}
void fxm_free(fxm_t *m) { free(m->b); memset(m, 0, sizeof *m); }
void fxm_set(fxm_t *m, int flanger, float base_ms, float depth_ms, float rate, float fb) {
    m->flanger = flanger;
    m->base_ms = fx_clampf(base_ms, 0.5f, 40.0f);
    m->depth_ms = fx_clampf(depth_ms, 0.0f, 20.0f);
    m->rate = fx_clampf(rate, 0.02f, 10.0f);
    m->fb = fx_clampf(fb, 0.0f, 0.85f);
}
void fxm_run(fxm_t *m, float l, float rr, float *ol, float *orr) {
    m->ph += m->rate / FX_SR;
    if (m->ph >= 1.0f) m->ph -= 1.0f;
    float s = sinf(TAU * m->ph), s2 = sinf(TAU * m->ph + 3.14159265f);  /* stereo offset */
    float in[2] = { l, rr }, sw[2] = { s, s2 }, out[2];
    for (int c = 0; c < 2; c++) {
        float t = (m->base_ms + m->depth_ms * sw[c]) * FX_SR / 1000.0f;
        if (t < 1.0f) t = 1.0f;
        if (t > m->n - 2) t = (float)(m->n - 2);
        int i0 = (int)t, f = (int)((t - i0) * 256.0f);
        int rp = m->w - i0; while (rp < 0) rp += m->n;
        int rp2 = rp - 1; if (rp2 < 0) rp2 += m->n;
        float v = m->b[rp * 2 + c] + (m->b[rp2 * 2 + c] - m->b[rp * 2 + c]) * (f / 256.0f);
        out[c] = fx_zap(v);
        m->b[m->w * 2 + c] = in[c] + out[c] * m->fb;
    }
    m->w = (m->w + 1) % m->n;
    *ol = out[0]; *orr = out[1];
}

/* --- phaser (DP/4 Phaser-DDL-inspired) ---
 * LFO-swept allpass chain (up to 12 stages) with bipolar feedback, notch depth,
 * stereo LFO phase, sample-and-hold on the LFO, and a tempo-synced ping-pong
 * DDL tail. Behavioral reference only: the DP/4+ manual's Phaser-DDL params
 * (center, width, feedback, notch depth, L/R LFO phase, S&H rate, L/R delay,
 * DDL feedback) and the Dusty Devices Phaser-DDL (cycle-accurate DP/4 phaser
 * emulation). No code copied. */
void fxp_init(fxp_t *p) {
    memset(p, 0, sizeof *p);
    fxd_init(&p->ddl, 1000);
    p->bpm = 120.0f;
    p->stages = 8;
}
void fxp_free(fxp_t *p) { fxd_free(&p->ddl); }
void fxp_set(fxp_t *p, float rate_hz, float center_hz, float width_01,
             float fb_bipolar, float notch_01, float sh_rate_hz, int stages) {
    p->rate = fx_clampf(rate_hz, 0.02f, 10.0f);
    p->center = fx_clampf(center_hz, 80.0f, 8000.0f);
    p->width = fx_clampf(width_01, 0.0f, 1.0f);
    p->fb = fx_clampf(fb_bipolar, -0.95f, 0.95f);
    p->notch = fx_clampf(notch_01, 0.0f, 1.0f);
    p->sh_rate = sh_rate_hz < 0.05f ? 0.0f : fx_clampf(sh_rate_hz, 0.1f, 15.0f);
    p->stages = stages < 2 ? 2 : stages > FXP_MAX ? FXP_MAX : stages;
    /* DDL: tempo-synced ping-pong (8th note), feedback follows |fb| */
    if (p->bpm > 1.0f)
        fxd_set(&p->ddl, 60000.0f / p->bpm * 0.5f, 0.0f, 0.3f, 1);
    else
        fxd_set(&p->ddl, 250.0f, 0.0f, 0.3f, 1);
    p->ddl.fb = fabsf(p->fb) * 0.45f;
}
void fxp_run(fxp_t *p, float l, float rr, float *ol, float *orr) {
    p->ph += p->rate / FX_SR;
    if (p->ph >= 1.0f) p->ph -= floorf(p->ph);
    /* sample-and-hold on the LFO: stepped modulation, fixed notches between steps */
    float lfo;
    if (p->sh_rate > 0.0f) {
        p->sh_timer += 1.0f / FX_SR;
        if (p->sh_timer >= 1.0f / p->sh_rate) { p->sh_timer = 0.0f; p->sh_val = sinf(TAU * p->ph); }
        lfo = p->sh_val;
    } else {
        lfo = sinf(TAU * p->ph);
    }
    /* center Hz -> allpass coefficient base (log map: higher center -> lower a) */
    float lc = logf(p->center / 80.0f) / logf(8000.0f / 80.0f);   /* 0..1 */
    float a_base = 0.92f - lc * 0.84f;                             /* 0.92..0.08 */
    float in[2] = { l + p->fbs[0] * p->fb, rr + p->fbs[1] * p->fb };
    float sw[2] = { lfo, -lfo };   /* L/R LFO out of phase: the wide stereo woosh */
    float out[2];
    for (int c = 0; c < 2; c++) {
        float a = a_base + p->width * 0.35f * sw[c];
        if (a < 0.02f) a = 0.02f;
        if (a > 0.98f) a = 0.98f;
        float x = in[c];
        for (int s = 0; s < p->stages; s++) {
            float y = -a * x + p->x1[s][c] + a * p->y1[s][c];
            p->x1[s][c] = x; p->y1[s][c] = fx_zap(y);
            x = y;
        }
        p->fbs[c] = fx_zap(x);
        /* notch depth: 0 = pure phase modulation (doppler), 1 = deep 50/50 notches */
        float dry = c ? rr : l;
        out[c] = dry * (p->notch * 0.5f) + x * (1.0f - p->notch * 0.5f);
    }
    /* DDL tail: ping-pong the phased signal, mixed under it */
    float d0, d1;
    fxd_run(&p->ddl, out[0], out[1], &d0, &d1);
    *ol = out[0] + d0 * 0.35f;
    *orr = out[1] + d1 * 0.35f;
}

/* --- pitch shifter (granular overlap-add) --- */
void pxs_set(pxs_t *p, float semitones) { p->st = fx_clampf(semitones, -12.0f, 12.0f); }
void pxs_run(pxs_t *p, float l, float rr, float *ol, float *orr) {
    float in[2] = { l, rr }, out[2];
    float ratio = powf(2.0f, p->st / 12.0f);
    for (int c = 0; c < 2; c++) {
        /* push input */
        p->inb[p->iw * 2 + c] = in[c];
        /* emit */
        float v = p->acc[p->ar * 2 + c];
        p->acc[p->ar * 2 + c] = 0.0f;
        out[c] = v;
    }
    p->iw = (p->iw + 1) % (2 * PXS_G);
    p->ar = (p->ar + 1) % (PXS_G + PXS_HOP);
    if (++p->since >= PXS_HOP) {
        p->since = 0;
        for (int i = 0; i < PXS_G; i++) {
            float src = (float)i / ratio;                 /* input span G/ratio */
            int i0 = (int)src;
            float fr = src - i0;
            /* Hann-windowed overlap-add into acc at the current read position */
            float w = 0.5f - 0.5f * cosf(TAU * i / (PXS_G - 1));
            for (int c = 0; c < 2; c++) {
                int p0 = (p->iw - PXS_G + i0 + 4 * PXS_G) % (2 * PXS_G);
                int p1 = (p0 + 1) % (2 * PXS_G);
                float s = p->inb[p0 * 2 + c] + (p->inb[p1 * 2 + c] - p->inb[p0 * 2 + c]) * fr;
                int ap = (p->ar + i) % (PXS_G + PXS_HOP);
                p->acc[ap * 2 + c] += w * s * 0.9f;
            }
        }
    }
    *ol = out[0]; *orr = out[1];
}

/* --- 3-band EQ --- */
void eq3_set(eq3_t *e, float low_db, float mid_db, float mid_hz, float high_db) {
    for (int c = 0; c < 2; c++) {
        bq_lowshelf(&e->lo[c], 200.0f, low_db);
        bq_peak(&e->mi[c], mid_hz, 1.0f, mid_db);
        bq_highshelf(&e->hi[c], 6000.0f, high_db);
    }
}

/* --- resonator --- */
void fxres_set(fxres_t *r, float freq, float reso) {
    float q = 2.0f + fx_clampf(reso, 0.0f, 1.0f) * 18.0f;
    float f0 = fx_clampf(freq, 60.0f, 12000.0f);
    for (int c = 0; c < 2; c++)
        for (int i = -1; i <= 1; i++) {
            float f = f0 * powf(2.0f, (float)i * 0.5f);
            if (f > 16000.0f) f = 16000.0f;
            bq_bandpass(&r->b[i + 1][c], f, q);
        }
}
void fxres_run(fxres_t *r, float l, float rr, float *ol, float *orr) {
    float in[2] = { l, rr }, out[2] = { 0, 0 };
    for (int c = 0; c < 2; c++)
        for (int i = 0; i < 3; i++) out[c] += bq_run(&r->b[i][c], in[c]);
    *ol = out[0] * 0.5f; *orr = out[1] * 0.5f;
}

/* --- ring mod --- */
void fxring_run(fxring_t *r, float rate_hz, float l, float rr, float *ol, float *orr) {
    r->ph += rate_hz / FX_SR;
    if (r->ph >= 1.0f) r->ph -= floorf(r->ph);
    float m = sinf(TAU * r->ph);
    *ol = l * m; *orr = rr * m;
}

/* --- tremolo / autopan --- */
void fxtrem_run(fxtrem_t *t, float rate_hz, float depth, int pan, float l, float rr, float *ol, float *orr) {
    t->ph += rate_hz / FX_SR;
    if (t->ph >= 1.0f) t->ph -= floorf(t->ph);
    float s0 = sinf(TAU * t->ph), s1 = sinf(TAU * t->ph + 3.14159265f);
    if (t->shape > 0.001f) {           /* morph sine -> square */
        float k = 1.0f + t->shape * 6.0f, n = tanhf(k);
        s0 = tanhf(s0 * k) / n; s1 = tanhf(s1 * k) / n;
    }
    float g0 = 1.0f - depth * 0.5f * (1.0f + s0);
    float g1 = pan ? 1.0f - depth * 0.5f * (1.0f + s1) : g0;
    *ol = l * g0; *orr = rr * g1;
}

/* --- distortion --- */
void fxdst_run(fxdst_t *d, float drive, float tone, float level, float l, float rr, float *ol, float *orr) {
    if (tone != d->tone_set) {
        d->tone_set = tone;
        bq_lowpass(&d->tone[0], 800.0f + tone * 9200.0f, 0.7f);
        bq_lowpass(&d->tone[1], 800.0f + tone * 9200.0f, 0.7f);
    }
    float g = 1.0f + drive * 24.0f;
    *ol = bq_run(&d->tone[0], tanhf(l * g)) * level;
    *orr = bq_run(&d->tone[1], tanhf(rr * g)) * level;
}
