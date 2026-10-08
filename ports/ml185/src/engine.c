/* ML-185: an 8-stage step sequencer after the RYK M185 / Metropolis idea, for MPC OS as a MIDI generator.
 *
 * Each stage has a pitch (scale degree), a pulse count (how many clock pulses the stage lasts), a gate mode
 * and a slide switch. The playhead walks the stages in the chosen direction; long stages stretch the pattern,
 * so 8 stages make melodies of 8 to 64 pulses.
 *
 * Gate modes: Off (rest for the whole stage), Single (one note on the first pulse), Multi (a note on every
 * pulse: ratchets), Hold (one note held for the whole stage).
 * Slide: the stage's note starts before the previous one ends (legato), so a mono synth with glide slides.
 *
 * MPC OS ignores VST MIDI out, so notes go out through the plugin's own ALSA sequencer port (docs/NOTES.md,
 * "MIDI-output plugins"): pick "ML-185 <n>" as the MIDI input of the track to play. libasound is opened with
 * dlopen so the build needs no ALSA headers; on a host without it the plugin just stays silent.
 *
 * Clock: the wrapper passes the host tempo ("lfo_bpm", HAS_LFO_BPM) and transport ("transport", HAS_TRANSPORT);
 * the engine counts samples from the play start, so it is in time with MPC to one 128-frame block. */
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include "engine.h"

#define NST 8
#define SR 44100.0

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
static const char *SCALE_NAMES[] = {"Chromatic", "Major", "Minor", "Dorian", "Phrygian", "Lydian", "Mixolydian",
                                    "Harm Minor", "Pent Major", "Pent Minor", "Blues"};
static const int SCALES[][13] = {   /* steps per octave, then the semitones */
    {12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}, {7, 0, 2, 4, 5, 7, 9, 11}, {7, 0, 2, 3, 5, 7, 8, 10},
    {7, 0, 2, 3, 5, 7, 9, 10}, {7, 0, 1, 3, 5, 7, 8, 10}, {7, 0, 2, 4, 6, 7, 9, 11}, {7, 0, 2, 4, 5, 7, 9, 10},
    {7, 0, 2, 3, 5, 7, 8, 11}, {5, 0, 2, 4, 7, 9}, {5, 0, 3, 5, 7, 10}, {6, 0, 3, 5, 6, 7, 10}};
#define NSCALES ((int)(sizeof SCALES / sizeof SCALES[0]))
static const char *NOTE_NAMES[] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
static const char *GATE_NAMES[] = {"Off", "Single", "Multi", "Hold"};
enum { G_OFF, G_SINGLE, G_MULTI, G_HOLD };
static const char *DIR_NAMES[] = {"Forward", "Reverse", "Pendulum", "Random"};
static const char *RATE_NAMES[] = {"1/32", "1/16T", "1/16", "1/8T", "1/8", "1/4"};
static const double RATE_BEATS[] = {0.125, 1.0 / 6, 0.25, 1.0 / 3, 0.5, 1.0};

typedef struct {
    /* parameters */
    int pitch[NST], pulses[NST], gate[NST], slide[NST], accent[NST];
    int length, dir, rate, scale, root, octave, chan, vel, accvel, gatelen, swing;
    /* sequencer state */
    double bpm, pos, next_pulse, off_at;
    int playing, stage, pulse_in_stage, pend_up, pulse_count;
    int cur_note, display_rev;
    uint32_t rng;
    /* ALSA */
    void *seq;
    int port;
    char port_name[32];
} ml_t;

static int clampi(int v, int lo, int hi) { return v < lo ? lo : v > hi ? hi : v; }
/* an option value: the wrapper sends its index ("2"); a name ("Multi") is accepted too */
static int find(const char **names, int n, const char *v) {
    for (int i = 0; i < n; i++) if (!strcasecmp(names[i], v)) return i;   /* names first: "1/16" is a name */
    if (v[0] >= '0' && v[0] <= '9') { int i = atoi(v); return i >= 0 && i < n ? i : -1; }
    return -1;
}
static const char *ONOFF[] = {"Off", "On"};
static uint32_t rnd(ml_t *s) { s->rng ^= s->rng << 13; s->rng ^= s->rng >> 17; s->rng ^= s->rng << 5; return s->rng; }

#ifdef ML185_TEST   /* offline test: print events with their sample time instead of sending them */
static double test_now;
#endif
static void send(ml_t *s, int type, int note, int vel) {
#ifdef ML185_TEST
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

static void note_off(ml_t *s) {
    if (s->cur_note >= 0) send(s, EV_NOTEOFF, s->cur_note, 0);
    s->cur_note = -1;
}

static int stage_note(ml_t *s, int st) {
    const int *sc = SCALES[clampi(s->scale, 0, NSCALES - 1)];
    int deg = s->pitch[st], n = sc[0];
    int semis = 12 * (deg / n) + sc[1 + deg % n];
    return clampi(12 * (s->octave + 1) + s->root + semis, 0, 127);
}

static void note_on(ml_t *s, int st, int legato) {
    int note = stage_note(s, st), vel = s->accent[st] ? s->accvel : s->vel, old = s->cur_note;
    if (legato && old >= 0) {          /* slide: new note first, then release the old one */
        send(s, EV_NOTEON, note, vel);
        if (old != note) send(s, EV_NOTEOFF, old, 0);
    } else {
        note_off(s);
        send(s, EV_NOTEON, note, vel);
    }
    s->cur_note = note;
}

static int next_stage(ml_t *s, int st) {
    int len = clampi(s->length, 1, NST);
    switch (s->dir) {
    case 1: return (st - 1 + len) % len;
    case 2:
        if (len == 1) return 0;
        if (s->pend_up) { if (st + 1 >= len) { s->pend_up = 0; return st - 1; } return st + 1; }
        if (st - 1 < 0) { s->pend_up = 1; return st + 1; }
        return st - 1;
    case 3: return (int)(rnd(s) % (uint32_t)len);
    default: return (st + 1) % len;
    }
}

/* the stage after st without moving any state; -1 when it can't be known (Random) */
static int peek_next(ml_t *s, int st) {
    if (s->dir == 3) return -1;
    int pend = s->pend_up, r = next_stage(s, st);
    s->pend_up = pend;
    return r;
}

static double pulse_len(ml_t *s) {
    double bpm = s->bpm > 1 ? s->bpm : 120;
    return 60.0 / bpm * SR * RATE_BEATS[clampi(s->rate, 0, 5)];
}

/* one clock pulse at sample position s->pos */
static void pulse(ml_t *s) {
    double plen = pulse_len(s);
    if (s->pulse_in_stage >= clampi(s->pulses[s->stage], 1, 8)) {
        s->stage = next_stage(s, s->stage);
        s->pulse_in_stage = 0;
    }
    if (s->stage >= clampi(s->length, 1, NST)) { s->stage = 0; s->pulse_in_stage = 0; }
    int st = s->stage, k = s->pulse_in_stage, g = s->gate[st];
    double glen = plen * clampi(s->gatelen, 5, 100) / 100.0;
    if (g == G_SINGLE && k == 0) { note_on(s, st, s->slide[st]); s->off_at = s->pos + glen; }
    else if (g == G_MULTI) { note_on(s, st, k == 0 && s->slide[st]); s->off_at = s->pos + glen; }
    else if (g == G_HOLD && k == 0) { note_on(s, st, s->slide[st]); s->off_at = s->pos + plen * clampi(s->pulses[st], 1, 8) - 1; }
    else if (g == G_OFF && k == 0) note_off(s);
    /* last pulse of a stage whose successor slides: hold this note until that stage's note starts */
    if (s->cur_note >= 0 && s->off_at >= 0 && k + 1 >= clampi(s->pulses[st], 1, 8)) {
        int nx = peek_next(s, st);
        if (nx >= 0 && s->slide[nx] && s->gate[nx] != G_OFF) s->off_at = -1;
    }
    s->pulse_in_stage++;
    s->pulse_count++;
    /* swing delays every second pulse */
    double sw = (s->pulse_count & 1) ? plen * clampi(s->swing, 0, 75) / 100.0 * 0.5 : -plen * clampi(s->swing, 0, 75) / 100.0 * 0.5;
    s->next_pulse += plen + sw;
}

static void start(ml_t *s) {
    note_off(s);
    s->playing = 1;
    s->pos = 0;
    s->next_pulse = 0;
    s->stage = s->dir == 1 ? clampi(s->length, 1, NST) - 1 : 0;
    s->pulse_in_stage = 0;
    s->pulse_count = 0;
    s->pend_up = 1;
    s->off_at = -1;
}

static void randomize(ml_t *s) {
    int n = SCALES[clampi(s->scale, 0, NSCALES - 1)][0];
    for (int i = 0; i < NST; i++) {
        s->pitch[i] = (int)(rnd(s) % (uint32_t)(n + 3));
        uint32_t r = rnd(s) % 10;
        s->pulses[i] = r < 5 ? 1 : r < 8 ? 2 : (int)(rnd(s) % 4) + 1;
        r = rnd(s) % 10;
        s->gate[i] = r < 1 ? G_OFF : r < 6 ? G_SINGLE : r < 8 ? G_MULTI : G_HOLD;
        s->slide[i] = rnd(s) % 5 == 0;
        s->accent[i] = rnd(s) % 4 == 0;
    }
}

/* --- engine interface --- */
static void *create(const char *dir) {
    (void)dir;
    static int instances;
    ml_t *s = calloc(1, sizeof *s);
    if (!s) return NULL;
    static const int P[NST] = {0, 2, 4, 2, 7, 4, 5, 3};
    static const int U[NST] = {1, 1, 2, 1, 1, 2, 1, 1};
    static const int G[NST] = {G_SINGLE, G_SINGLE, G_MULTI, G_OFF, G_HOLD, G_SINGLE, G_SINGLE, G_SINGLE};
    for (int i = 0; i < NST; i++) { s->pitch[i] = P[i]; s->pulses[i] = U[i]; s->gate[i] = G[i]; }
    s->slide[5] = 1;
    s->accent[0] = 1;
    s->length = 8; s->dir = 0; s->rate = 2; s->scale = 2; s->root = 0; s->octave = 2; s->chan = 1;
    s->vel = 90; s->accvel = 127; s->gatelen = 50; s->swing = 0;
    s->bpm = 120; s->cur_note = -1; s->port = -1; s->off_at = -1;
    s->rng = 0x9e3779b9u ^ (uint32_t)(uintptr_t)s;
    alsa_load();
    if (A.ok && A.open(&s->seq, "default", OPEN_OUTPUT, 0) >= 0) {
        snprintf(s->port_name, sizeof s->port_name, "ML-185 %d", ++instances);
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
    ml_t *s = p;
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
static const char *STATE_KEYS[] = {"length", "direction", "rate", "scale", "root", "octave", "channel", "velocity",
                                   "accent_vel", "gate_len", "swing"};
static const char *STAGE_KEYS[] = {"pitch", "pulses", "gate", "slide", "accent"};

/* "state": every setting as key=value;... (project save), replayed through set_param on load */
static int get_state(ml_t *s, char *b, int n) {
    int len = 0;
    char k[16], v[24];
    for (int i = 0; i < 11 + 5 * NST && len < n; i++) {
        if (i < 11) snprintf(k, sizeof k, "%s", STATE_KEYS[i]);
        else snprintf(k, sizeof k, "%s%d", STAGE_KEYS[(i - 11) / NST], (i - 11) % NST + 1);
        if (get_param(s, k, v, sizeof v) > 0) len += snprintf(b + len, (size_t)(n - len), "%s=%s;", k, v);
    }
    return len < n ? len : 0;
}
static void set_state(ml_t *s, const char *str) {
    char buf[2048], *save = NULL;
    snprintf(buf, sizeof buf, "%s", str);
    for (char *t = strtok_r(buf, ";", &save); t; t = strtok_r(NULL, ";", &save)) {
        char *eq = strchr(t, '=');
        if (!eq) continue;
        *eq = 0;
        if (strcmp(t, "state") && strcmp(t, "transport") && strcmp(t, "randomize")) set_param(s, t, eq + 1);
    }
    s->display_rev++;
}

static int stage_key(const char *k, const char *pre, int *st) {
    size_t l = strlen(pre);
    if (strncmp(k, pre, l) || k[l] < '1' || k[l] > '8' || k[l + 1]) return 0;
    *st = k[l] - '1';
    return 1;
}

static void set_param(void *p, const char *k, const char *v) {
    ml_t *s = p;
    int st, i;
    if (stage_key(k, "pitch", &st)) s->pitch[st] = clampi(atoi(v), 0, 21);
    else if (stage_key(k, "pulses", &st)) s->pulses[st] = clampi(atoi(v), 1, 8);
    else if (stage_key(k, "gate", &st)) { if ((i = find(GATE_NAMES, 4, v)) >= 0) s->gate[st] = i; }
    else if (stage_key(k, "slide", &st)) { if ((i = find(ONOFF, 2, v)) >= 0) s->slide[st] = i; }
    else if (stage_key(k, "accent", &st)) { if ((i = find(ONOFF, 2, v)) >= 0) s->accent[st] = i; }
    else if (!strcmp(k, "length")) s->length = clampi(atoi(v), 1, NST);
    else if (!strcmp(k, "direction")) { if ((i = find(DIR_NAMES, 4, v)) >= 0) s->dir = i; }
    else if (!strcmp(k, "rate")) { if ((i = find(RATE_NAMES, 6, v)) >= 0) s->rate = i; }
    else if (!strcmp(k, "scale")) { if ((i = find(SCALE_NAMES, NSCALES, v)) >= 0) s->scale = i; }
    else if (!strcmp(k, "root")) { if ((i = find(NOTE_NAMES, 12, v)) >= 0) s->root = i; }
    else if (!strcmp(k, "octave")) s->octave = clampi(atoi(v), 0, 7);
    else if (!strcmp(k, "channel")) s->chan = clampi(atoi(v), 1, 16);
    else if (!strcmp(k, "velocity")) s->vel = clampi(atoi(v), 1, 127);
    else if (!strcmp(k, "accent_vel")) s->accvel = clampi(atoi(v), 1, 127);
    else if (!strcmp(k, "gate_len")) s->gatelen = clampi(atoi(v), 5, 100);
    else if (!strcmp(k, "swing")) s->swing = clampi(atoi(v), 0, 75);
    else if (!strcmp(k, "randomize")) { if (atof(v) > 0.5) { randomize(s); s->display_rev++; } }
    else if (!strcmp(k, "state")) set_state(s, v);
    else if (!strcmp(k, "lfo_bpm")) { double b = atof(v); if (b > 1) s->bpm = b; }
    else if (!strcmp(k, "transport")) {
        if (v[0] == '1') start(s);
        else { s->playing = 0; note_off(s); }
    }
}

static int get_param(void *p, const char *k, char *b, int n) {
    ml_t *s = p;
    int st;
    if (stage_key(k, "pitch", &st)) return snprintf(b, n, "%d", s->pitch[st]);
    size_t kl = strlen(k);
    if (kl == 14 && !strncmp(k, "pitch", 5) && !strcmp(k + 6, "_display")) {   /* "pitchN_display": the note name */
        char key[8];
        snprintf(key, sizeof key, "pitch%c", k[5]);
        if (stage_key(key, "pitch", &st)) {
            int note = stage_note(s, st);
            return snprintf(b, n, "%s%d", NOTE_NAMES[note % 12], note / 12 - 1);
        }
    }
    if (stage_key(k, "pulses", &st)) return snprintf(b, n, "%d", s->pulses[st]);
    if (stage_key(k, "gate", &st)) return snprintf(b, n, "%s", GATE_NAMES[s->gate[st]]);
    if (stage_key(k, "slide", &st)) return snprintf(b, n, "%s", s->slide[st] ? "On" : "Off");
    if (stage_key(k, "accent", &st)) return snprintf(b, n, "%s", s->accent[st] ? "On" : "Off");
    if (!strcmp(k, "length")) return snprintf(b, n, "%d", s->length);
    if (!strcmp(k, "direction")) return snprintf(b, n, "%s", DIR_NAMES[s->dir]);
    if (!strcmp(k, "rate")) return snprintf(b, n, "%s", RATE_NAMES[s->rate]);
    if (!strcmp(k, "scale")) return snprintf(b, n, "%s", SCALE_NAMES[s->scale]);
    if (!strcmp(k, "root")) return snprintf(b, n, "%s", NOTE_NAMES[s->root]);
    if (!strcmp(k, "octave")) return snprintf(b, n, "%d", s->octave);
    if (!strcmp(k, "channel")) return snprintf(b, n, "%d", s->chan);
    if (!strcmp(k, "velocity")) return snprintf(b, n, "%d", s->vel);
    if (!strcmp(k, "accent_vel")) return snprintf(b, n, "%d", s->accvel);
    if (!strcmp(k, "gate_len")) return snprintf(b, n, "%d", s->gatelen);
    if (!strcmp(k, "swing")) return snprintf(b, n, "%d", s->swing);
    if (!strcmp(k, "randomize")) return snprintf(b, n, "0");
    if (!strcmp(k, "state")) return get_state(s, b, n);
    if (!strcmp(k, "display_rev")) return snprintf(b, n, "%d", s->display_rev);
    if (!strcmp(k, "status")) return snprintf(b, n, "MIDI in: %s", s->port_name);
    return 0;
}

static void render(void *p, int16_t *out, int frames) {
    ml_t *s = p;
    memset(out, 0, (size_t)frames * 4);
    if (!s->playing) return;
    double end = s->pos + frames;
    while (1) {
        double t = s->next_pulse < s->off_at || s->off_at < 0 ? s->next_pulse : s->off_at;
        if (t >= end) break;
        s->pos = t > s->pos ? t : s->pos;
#ifdef ML185_TEST
        test_now = s->pos;
#endif
        if (s->off_at >= 0 && s->off_at <= s->next_pulse) { note_off(s); s->off_at = -1; }
        else pulse(s);
    }
    s->pos = end;
}

static const mpc_engine_t ENGINE = {create, destroy, midi, set_param, get_param, render, NULL};
const mpc_engine_t *mpc_engine(void) { return &ENGINE; }

#ifdef WRAP_TRACE
/* Diagnostic build only: log every setParameter (S) and every changed getParameter read-back (G) the host makes,
 * so a Q-Link turn on the device can be compared with a touch. /tmp/ml185.log, stops at 2 MB. */
#include <math.h>
#include <time.h>
void wrap_trace(int kind, int idx, float v) {
    static FILE *f;
    static float last[256];
    static long t0, bytes;
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    long ms = ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
    if (!f) { f = fopen("/tmp/ml185.log", "a"); t0 = ms; for (int i = 0; i < 256; i++) last[i] = -1; if (!f) return; }
    if (idx < 0 || idx >= 256 || bytes > 2000000) return;
    if (kind == 1) { if (fabsf(v - last[idx]) < 1e-6f) return; last[idx] = v; }
    bytes += fprintf(f, "%ld %c %d %.6f\n", ms - t0, kind ? 'G' : 'S', idx, v);
    fflush(f);
}
#endif
