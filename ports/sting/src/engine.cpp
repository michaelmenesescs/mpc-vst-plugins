/* sting: a generative acid sequencer for MPC OS, as a MIDI generator.
 *
 * Clean-room reimplementation of the STING by Skinnerbox (Iftah Gabbai) Max for Live
 * device concept: a seeded, deterministic 303-style pattern generator (pitch / velocity /
 * gate / octave / slide / accent per step). The generation core is vendored from
 * mattsp1290/acid-generator (MIT), which is itself explicitly Sting-inspired:
 * deterministic seeded SFC32 PRNG, weighted-probability note choice favouring root and
 * fifth, downbeat-prioritised rhythm mask, per-step accent/slide probabilities.
 * See src/VENDORED.md. No Max patch code is used or copied.
 *
 * MPC OS ignores VST MIDI out, so notes go out through the plugin's own ALSA sequencer
 * port (docs/NOTES.md, "MIDI-output plugins"): pick "sting <n>" as the MIDI input of the
 * track to play. libasound is opened with dlopen so the build needs no ALSA headers; on
 * a host without it the plugin just stays silent.
 *
 * Clock: the wrapper passes the host tempo ("lfo_bpm", HAS_LFO_BPM) and transport
 * ("transport", HAS_TRANSPORT); the engine counts samples from the play start, so it is
 * in time with MPC to one 128-frame block (the same approach as ports/ml185). */

#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

extern "C" {
#include "engine.h"
} /* the wrapper is C: its declaration of mpc_engine() needs C linkage too */
#include "dsp/Generator.hpp"

#define SR 44100.0
#define MAXSTEPS 32

/* --- ALSA sequencer, the few calls we need (layouts from alsa/seq_event.h, stable ABI) --- */
typedef struct {
    unsigned char type, flags, tag, queue;
    unsigned int time[2];
    unsigned char src_client, src_port, dst_client, dst_port;
    union {
        struct { unsigned char channel, note, velocity, off_velocity; unsigned int duration; } note;
        unsigned char raw8[12];
    } data;
} seq_ev_t;   /* snd_seq_event_t: 28 bytes */
enum { EV_NOTEON = 6, EV_NOTEOFF = 7, QUEUE_DIRECT = 253, ADDR_SUBSCRIBERS = 254, ADDR_UNKNOWN = 253 };
enum { OPEN_OUTPUT = 1, CAP_READ = 1 << 0, CAP_SUBS_READ = 1 << 5, TYPE_MIDI_GENERIC = 1 << 1, TYPE_APPLICATION = 1 << 20 };

static struct {
    int tried, ok;
    int (*open)(void **, const char *, int, int);
    int (*close)(void *);
    int (*set_name)(void *, const char *);
    int (*port)(void *, const char *, unsigned int, unsigned int);
    int (*out)(void *, seq_ev_t *);
    int (*client_id)(void *);
} A;

static void alsa_load(void) {
    if (A.tried) return;
    A.tried = 1;
    void *h = dlopen("libasound.so.2", RTLD_NOW | RTLD_LOCAL);
    if (!h) return;
    A.open = (int (*)(void **, const char *, int, int))dlsym(h, "snd_seq_open");
    A.close = (int (*)(void *))dlsym(h, "snd_seq_close");
    A.set_name = (int (*)(void *, const char *))dlsym(h, "snd_seq_set_client_name");
    A.port = (int (*)(void *, const char *, unsigned int, unsigned int))dlsym(h, "snd_seq_create_simple_port");
    A.out = (int (*)(void *, seq_ev_t *))dlsym(h, "snd_seq_event_output_direct");
    A.client_id = (int (*)(void *))dlsym(h, "snd_seq_client_id");
    A.ok = A.open && A.close && A.set_name && A.port && A.out && A.client_id;
}

/* --- musical tables --- */
/* our 12 scale options -> AcidGenerator::Scale (see Generator.hpp enum order) */
static const int SCALE_MAP[12] = {22, 0, 1, 2, 5, 4, 3, 7, 19, 18, 20, 21};
static const char *SCALE_NAMES[] = {"Chromatic", "Major", "Minor", "Dorian", "Phrygian", "Lydian",
                                    "Mixolydian", "Harm Minor", "Pent Major", "Pent Minor", "Blues", "Whole Tone"};
#define NSCALES 12
static const char *NOTE_NAMES[] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
static const char *RATE_NAMES[] = {"1/32", "1/16T", "1/16", "1/8T", "1/8", "1/4"};
static const double RATE_BEATS[] = {0.125, 1.0 / 6, 0.25, 1.0 / 3, 0.5, 1.0};
static const char *ONOFF[] = {"Off", "On"};

typedef struct {
    /* parameters */
    int seed, steps, rate, scale, root;
    int density, chaos, accent_amt, slide_prob;
    int gate_len, swing, octave, chan, vel, accvel;
    /* generator state */
    AcidGenerator::Pattern pat;
    int pat_valid;
    /* sequencer state */
    double bpm, pos, next_step, off_at;
    int playing, step_idx, cur_note, display_rev;
    uint32_t rng;
    /* ALSA */
    void *seq;
    int port;
    char port_name[32];
} sting_t;

static int clampi(int v, int lo, int hi) { return v < lo ? lo : v > hi ? hi : v; }
/* an option value: the wrapper sends its index ("2"); a name ("Minor") is accepted too */
static int find(const char **names, int n, const char *v) {
    for (int i = 0; i < n; i++) if (!strcasecmp(names[i], v)) return i;   /* names first: "1/16" is a name */
    if (v[0] >= '0' && v[0] <= '9') { int i = atoi(v); return i >= 0 && i < n ? i : -1; }
    return -1;
}
static uint32_t rnd(sting_t *s) { s->rng ^= s->rng << 13; s->rng ^= s->rng >> 17; s->rng ^= s->rng << 5; return s->rng; }

static void regenerate(sting_t *s) {
    AcidGenerator::GeneratorParams p;
    p.patternLength = clampi(s->steps, 1, MAXSTEPS);
    p.density = (float)clampi(s->density, 0, 100);
    p.spread = (float)clampi(s->chaos, 0, 100);
    p.accentsDensity = (float)clampi(s->accent_amt, 0, 100);
    p.slidesDensity = (float)clampi(s->slide_prob, 0, 100);
    p.seed = (uint32_t)s->seed;
    AcidGenerator::generate(p, s->pat);
    s->pat_valid = 1;
}

#ifdef STING_TEST   /* offline test: print events with their sample time instead of sending them */
static double test_now;
#endif
static void send(sting_t *s, int type, int note, int vel) {
#ifdef STING_TEST
    printf("%9.0f %s %3d v%d\n", test_now, type == EV_NOTEON ? "ON " : "off", note, vel);
#endif
    if (!s->seq) return;
    seq_ev_t ev;
    memset(&ev, 0, sizeof ev);
    ev.type = (unsigned char)type;
    ev.queue = QUEUE_DIRECT;
    ev.src_port = (unsigned char)s->port;
    ev.dst_client = ADDR_SUBSCRIBERS;
    ev.dst_port = ADDR_UNKNOWN;
    ev.data.note.channel = (unsigned char)((s->chan - 1) & 15);
    ev.data.note.note = (unsigned char)note;
    ev.data.note.velocity = (unsigned char)vel;
    A.out(s->seq, &ev);
}

static void note_off(sting_t *s) {
    if (s->cur_note >= 0) send(s, EV_NOTEOFF, s->cur_note, 0);
    s->cur_note = -1;
}

static void note_on(sting_t *s, int note, int vel, int slide) {
    int old = s->cur_note;
    if (slide && old >= 0) {          /* 303 slide: new note first, then release the old one */
        send(s, EV_NOTEON, note, vel);
        if (old != note) send(s, EV_NOTEOFF, old, 0);
    } else {
        note_off(s);
        send(s, EV_NOTEON, note, vel);
    }
    s->cur_note = note;
}

static double step_len(sting_t *s) {
    double bpm = s->bpm > 1 ? s->bpm : 120;
    return 60.0 / bpm * SR * RATE_BEATS[clampi(s->rate, 0, 5)];
}

/* one sequencer step at sample position s->pos */
static void step(sting_t *s) {
    if (!s->pat_valid) regenerate(s);
    int n = clampi(s->steps, 1, MAXSTEPS);
    int i = s->step_idx % n;
    const AcidGenerator::SequenceStep &st = s->pat.steps[i];
    double slen = step_len(s);
    if (!st.isRest()) {
        AcidGenerator::Scale sc = (AcidGenerator::Scale)SCALE_MAP[clampi(s->scale, 0, NSCALES - 1)];
        int semis = AcidGenerator::getNoteInScale(st.note, sc, clampi(s->root, 0, 11), st.octave);
        int note = clampi(12 * (s->octave + 1) + semis, 0, 127);
        note_on(s, note, st.accent ? s->accvel : s->vel, st.slide);
        s->off_at = s->pos + slen * clampi(s->gate_len, 5, 100) / 100.0;
    }
    s->step_idx++;
    /* swing delays every second step, advances the others: net period preserved over two steps */
    double sw = slen * clampi(s->swing, 0, 75) / 100.0 * 0.5;
    s->next_step += slen + ((s->step_idx & 1) ? sw : -sw);
}

static void start(sting_t *s) {
    note_off(s);
    s->playing = 1;
    s->pos = 0;
    s->next_step = 0;
    s->step_idx = 0;
    s->off_at = -1;
}

/* --- engine interface --- */
static void *create(const char *dir) {
    (void)dir;
    static int instances;
    sting_t *s = (sting_t *)calloc(1, sizeof *s);
    if (!s) return NULL;
    s->seed = 12345; s->steps = 16; s->rate = 2; s->scale = 2; s->root = 0;
    s->density = 70; s->chaos = 50; s->accent_amt = 30; s->slide_prob = 25;
    s->gate_len = 50; s->swing = 0; s->octave = 2; s->chan = 1;
    s->vel = 100; s->accvel = 127;
    s->bpm = 120; s->cur_note = -1; s->port = -1; s->off_at = -1;
    s->rng = 0x9e3779b9u ^ (uint32_t)(uintptr_t)s;
    regenerate(s);
    alsa_load();
    if (A.ok && A.open(&s->seq, "default", OPEN_OUTPUT, 0) >= 0) {
        snprintf(s->port_name, sizeof s->port_name, "sting %d", ++instances);
        A.set_name(s->seq, s->port_name);
        s->port = A.port(s->seq, "Out", CAP_READ | CAP_SUBS_READ, TYPE_MIDI_GENERIC | TYPE_APPLICATION);
        if (s->port < 0) { A.close(s->seq); s->seq = NULL; }
    } else {
        s->seq = NULL;
        snprintf(s->port_name, sizeof s->port_name, "no MIDI port");
    }
    return s;
}

static void destroy(void *p) {
    sting_t *s = (sting_t *)p;
    if (!s) return;
    note_off(s);
    if (s->seq) A.close(s->seq);
    free(s);
}

static void midi(void *p, const uint8_t *m, int n) {
    (void)p; (void)m; (void)n;   /* a generator: notes played into its own track are ignored */
}

static void set_param(void *p, const char *k, const char *v);
static int get_param(void *p, const char *k, char *b, int n);
static const char *STATE_KEYS[] = {"seed", "steps", "rate", "scale", "root", "density", "chaos",
                                   "accent_amt", "slide_prob", "gate_len", "swing", "octave",
                                   "channel", "velocity", "accent_vel"};

/* "state": every setting as key=value;... (project save), replayed through set_param on load */
static int get_state(sting_t *s, char *b, int n) {
    int len = 0;
    char v[24];
    for (int i = 0; i < 15 && len < n; i++)
        if (get_param(s, STATE_KEYS[i], v, sizeof v) > 0)
            len += snprintf(b + len, (size_t)(n - len), "%s=%s;", STATE_KEYS[i], v);
    return len < n ? len : 0;
}
static void set_state(sting_t *s, const char *str) {
    char buf[2048], *save = NULL;
    snprintf(buf, sizeof buf, "%s", str);
    for (char *t = strtok_r(buf, ";", &save); t; t = strtok_r(NULL, ";", &save)) {
        char *eq = strchr(t, '=');
        if (!eq) continue;
        *eq = 0;
        if (strcmp(t, "state") && strcmp(t, "transport") && strcmp(t, "regenerate")) set_param(s, t, eq + 1);
    }
    regenerate(s);
    s->display_rev++;
}

static void set_param(void *p, const char *k, const char *v) {
    sting_t *s = (sting_t *)p;
    int i, regen = 0;
    if (!strcmp(k, "seed")) { int nv = clampi(atoi(v), 0, 999999); regen = nv != s->seed; s->seed = nv; }
    else if (!strcmp(k, "steps")) s->steps = clampi(atoi(v), 1, MAXSTEPS);
    else if (!strcmp(k, "rate")) { if ((i = find(RATE_NAMES, 6, v)) >= 0) s->rate = i; }
    else if (!strcmp(k, "scale")) { if ((i = find(SCALE_NAMES, NSCALES, v)) >= 0) s->scale = i; }
    else if (!strcmp(k, "root")) { if ((i = find(NOTE_NAMES, 12, v)) >= 0) s->root = i; }
    else if (!strcmp(k, "density")) { int nv = clampi(atoi(v), 0, 100); regen = regen || nv != s->density; s->density = nv; }
    else if (!strcmp(k, "chaos")) { int nv = clampi(atoi(v), 0, 100); regen = regen || nv != s->chaos; s->chaos = nv; }
    else if (!strcmp(k, "accent_amt")) { int nv = clampi(atoi(v), 0, 100); regen = regen || nv != s->accent_amt; s->accent_amt = nv; }
    else if (!strcmp(k, "slide_prob")) { int nv = clampi(atoi(v), 0, 100); regen = regen || nv != s->slide_prob; s->slide_prob = nv; }
    else if (!strcmp(k, "gate_len")) s->gate_len = clampi(atoi(v), 5, 100);
    else if (!strcmp(k, "swing")) s->swing = clampi(atoi(v), 0, 75);
    else if (!strcmp(k, "octave")) s->octave = clampi(atoi(v), 0, 7);
    else if (!strcmp(k, "channel")) s->chan = clampi(atoi(v), 1, 16);
    else if (!strcmp(k, "velocity")) s->vel = clampi(atoi(v), 1, 127);
    else if (!strcmp(k, "accent_vel")) s->accvel = clampi(atoi(v), 1, 127);
    else if (!strcmp(k, "regenerate")) { if (atof(v) > 0.5) { s->seed = (int)(rnd(s) % 1000000u); regen = 1; } }
    else if (!strcmp(k, "state")) set_state(s, v);
    else if (!strcmp(k, "lfo_bpm")) { double b = atof(v); if (b > 1) s->bpm = b; }
    else if (!strcmp(k, "transport")) {
        if (v[0] == '1') start(s);
        else { s->playing = 0; note_off(s); }
    }
    if (regen) { regenerate(s); s->display_rev++; }
}

static int get_param(void *p, const char *k, char *b, int n) {
    sting_t *s = (sting_t *)p;
    if (!strcmp(k, "seed")) return snprintf(b, n, "%d", s->seed);
    if (!strcmp(k, "steps")) return snprintf(b, n, "%d", s->steps);
    if (!strcmp(k, "rate")) return snprintf(b, n, "%s", RATE_NAMES[s->rate]);
    if (!strcmp(k, "scale")) return snprintf(b, n, "%s", SCALE_NAMES[s->scale]);
    if (!strcmp(k, "root")) return snprintf(b, n, "%s", NOTE_NAMES[s->root]);
    if (!strcmp(k, "density")) return snprintf(b, n, "%d", s->density);
    if (!strcmp(k, "chaos")) return snprintf(b, n, "%d", s->chaos);
    if (!strcmp(k, "accent_amt")) return snprintf(b, n, "%d", s->accent_amt);
    if (!strcmp(k, "slide_prob")) return snprintf(b, n, "%d", s->slide_prob);
    if (!strcmp(k, "gate_len")) return snprintf(b, n, "%d", s->gate_len);
    if (!strcmp(k, "swing")) return snprintf(b, n, "%d", s->swing);
    if (!strcmp(k, "octave")) return snprintf(b, n, "%d", s->octave);
    if (!strcmp(k, "channel")) return snprintf(b, n, "%d", s->chan);
    if (!strcmp(k, "velocity")) return snprintf(b, n, "%d", s->vel);
    if (!strcmp(k, "accent_vel")) return snprintf(b, n, "%d", s->accvel);
    if (!strcmp(k, "regenerate")) return snprintf(b, n, "0");
    if (!strcmp(k, "state")) return get_state(s, b, n);
    if (!strcmp(k, "display_rev")) return snprintf(b, n, "%d", s->display_rev);
    if (!strcmp(k, "status")) return snprintf(b, n, "MIDI in: %s", s->port_name);
    return 0;
}

static void render(void *p, int16_t *out, int frames) {
    sting_t *s = (sting_t *)p;
    memset(out, 0, (size_t)frames * 4);
    if (!s->playing) return;
    double end = s->pos + frames;
    while (1) {
        double t = (s->off_at >= 0 && s->off_at <= s->next_step) ? s->off_at : s->next_step;
        if (t >= end) break;
        s->pos = t > s->pos ? t : s->pos;
#ifdef STING_TEST
        test_now = s->pos;
#endif
        if (s->off_at >= 0 && s->off_at <= s->next_step) { note_off(s); s->off_at = -1; }
        else step(s);
    }
    s->pos = end;
}

static const mpc_engine_t ENGINE = {create, destroy, midi, set_param, get_param, render, NULL};
extern "C" const mpc_engine_t *mpc_engine(void) { return &ENGINE; }
