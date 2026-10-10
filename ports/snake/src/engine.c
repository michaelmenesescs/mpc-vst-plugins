/* snake: a cartesian step sequencer for MPC OS, as a MIDI generator.
 *
 * Clean-room reimplementation of the MDD Snake (Maxime Dangles) Max for Live device
 * concept, itself a clone of the Make Noise René cartesian sequencer: a 4x4 grid of
 * pitch nodes played by two independent clocks. The X clock steps along the chosen
 * snake path, the Y clock jumps in strides of 4 along the same path; each tick plays
 * the node it lands on (when its gate is on). Per-node pitch (scale degree), gate and
 * glide; global scale quantization, root, octave, gate length, MIDI channel, velocity.
 * No Max patch code is used or copied; the René interaction model is reimplemented
 * from its documented behaviour.
 *
 * MPC OS ignores VST MIDI out, so notes go out through the plugin's own ALSA sequencer
 * port (docs/NOTES.md, "MIDI-output plugins"): pick "snake <n>" as the MIDI input of the
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
#include "engine.h"

#define NNODES 16
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
static const char *SCALE_NAMES[] = {"Chromatic", "Major", "Minor", "Dorian", "Phrygian", "Lydian",
                                    "Mixolydian", "Harm Minor", "Pent Major", "Pent Minor", "Blues"};
static const int SCALES[][13] = {   /* steps per octave, then the semitones */
    {12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}, {7, 0, 2, 4, 5, 7, 9, 11}, {7, 0, 2, 3, 5, 7, 8, 10},
    {7, 0, 2, 3, 5, 7, 9, 10}, {7, 0, 1, 3, 5, 7, 8, 10}, {7, 0, 2, 4, 6, 7, 9, 11}, {7, 0, 2, 4, 5, 7, 9, 10},
    {7, 0, 2, 3, 5, 7, 8, 11}, {5, 0, 2, 4, 7, 9}, {5, 0, 3, 5, 7, 10}, {6, 0, 3, 5, 6, 7, 10}};
#define NSCALES ((int)(sizeof SCALES / sizeof SCALES[0]))
static const char *NOTE_NAMES[] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
static const char *PATH_NAMES[] = {"Rows", "Columns", "Spiral", "Zigzag"};
/* snake paths: order of node indices (node = row*4+col) along each shape */
static const int PATHS[4][NNODES] = {
    {0, 1, 2, 3, 7, 6, 5, 4, 8, 9, 10, 11, 15, 14, 13, 12},     /* rows, boustrophedon */
    {0, 4, 8, 12, 13, 9, 5, 1, 2, 6, 10, 14, 15, 11, 7, 3},     /* columns, boustrophedon */
    {0, 1, 2, 3, 7, 11, 15, 14, 13, 12, 8, 4, 5, 6, 10, 9},     /* inward spiral */
    {0, 1, 4, 2, 5, 8, 3, 6, 9, 12, 7, 10, 13, 11, 14, 15},     /* diagonal zigzag */
};
static const char *RATE_NAMES[] = {"1/32", "1/16T", "1/16", "1/8T", "1/8", "1/4", "1/2", "1/1"};
static const double RATE_BEATS[] = {0.125, 1.0 / 6, 0.25, 1.0 / 3, 0.5, 1.0, 2.0, 4.0};
static const char *ONOFF[] = {"Off", "On"};

typedef struct {
    /* parameters: per-node */
    int pitch[NNODES], gate[NNODES], glide[NNODES];
    /* parameters: global */
    int x_rate, y_rate, path, scale, root, gate_len, octave, chan, vel;
    /* sequencer state */
    double bpm, pos, next_x, next_y, off_at;
    int playing, path_idx, cur_note, display_rev;
    uint32_t rng;
    /* ALSA */
    void *seq;
    int port;
    char port_name[32];
} snake_t;

static int clampi(int v, int lo, int hi) { return v < lo ? lo : v > hi ? hi : v; }
/* an option value: the wrapper sends its index ("2"); a name ("Minor") is accepted too */
static int find(const char **names, int n, const char *v) {
    for (int i = 0; i < n; i++) if (!strcasecmp(names[i], v)) return i;   /* names first: "1/16" is a name */
    if (v[0] >= '0' && v[0] <= '9') { int i = atoi(v); return i >= 0 && i < n ? i : -1; }
    return -1;
}
static uint32_t rnd(snake_t *s) { s->rng ^= s->rng << 13; s->rng ^= s->rng >> 17; s->rng ^= s->rng << 5; return s->rng; }

#ifdef SNAKE_TEST   /* offline test: print events with their sample time instead of sending them */
static double test_now;
#endif
static void send(snake_t *s, int type, int note, int vel) {
#ifdef SNAKE_TEST
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

static void note_off(snake_t *s) {
    if (s->cur_note >= 0) send(s, EV_NOTEOFF, s->cur_note, 0);
    s->cur_note = -1;
}

static void note_on(snake_t *s, int note, int legato) {
    int old = s->cur_note;
    if (legato && old >= 0) {          /* glide: new note first, then release the old one */
        send(s, EV_NOTEON, note, s->vel);
        if (old != note) send(s, EV_NOTEOFF, old, 0);
    } else {
        note_off(s);
        send(s, EV_NOTEON, note, s->vel);
    }
    s->cur_note = note;
}

static int node_note(snake_t *s, int node) {
    const int *sc = SCALES[clampi(s->scale, 0, NSCALES - 1)];
    int deg = s->pitch[node], n = sc[0];
    int semis = 12 * (deg / n) + sc[1 + deg % n];
    return clampi(12 * (s->octave + 1) + s->root + semis, 0, 127);
}

static double x_len(snake_t *s) {
    double bpm = s->bpm > 1 ? s->bpm : 120;
    return 60.0 / bpm * SR * RATE_BEATS[clampi(s->x_rate, 0, 7)];
}
static double y_len(snake_t *s) {
    double bpm = s->bpm > 1 ? s->bpm : 120;
    return 60.0 / bpm * SR * RATE_BEATS[clampi(s->y_rate, 0, 7)];
}

/* one clock tick: play the node under the playhead, then advance (X: +1, Y: +4 along the path) */
static void tick(snake_t *s, int is_y) {
    int node = PATHS[clampi(s->path, 0, 3)][s->path_idx];
    if (s->gate[node]) {
        note_on(s, node_note(s, node), s->glide[node]);
        s->off_at = s->pos + x_len(s) * clampi(s->gate_len, 5, 100) / 100.0;
    }
    if (is_y) { s->path_idx = (s->path_idx + 4) % NNODES; s->next_y += y_len(s); }
    else { s->path_idx = (s->path_idx + 1) % NNODES; s->next_x += x_len(s); }
}

static void start(snake_t *s) {
    note_off(s);
    s->playing = 1;
    s->pos = 0;
    s->path_idx = 0;
    s->next_x = 0;
    s->next_y = y_len(s);
    s->off_at = -1;
}

static void randomize(snake_t *s) {
    int n = SCALES[clampi(s->scale, 0, NSCALES - 1)][0];
    for (int i = 0; i < NNODES; i++) {
        s->pitch[i] = (int)(rnd(s) % (uint32_t)(n + 3));
        s->gate[i] = rnd(s) % 10 < 8;
        s->glide[i] = rnd(s) % 5 == 0;
    }
}

/* --- engine interface --- */
static void *create(const char *dir) {
    (void)dir;
    static int instances;
    snake_t *s = calloc(1, sizeof *s);
    if (!s) return NULL;
    static const int P[NNODES] = {0, 2, 3, 2, 4, 3, 2, 0, 0, 4, 5, 4, 2, 0, 2, 0};
    static const int G[NNODES] = {1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1};
    for (int i = 0; i < NNODES; i++) { s->pitch[i] = P[i]; s->gate[i] = G[i]; }
    s->glide[5] = 1;
    s->x_rate = 2; s->y_rate = 5; s->path = 0; s->scale = 2; s->root = 0;
    s->gate_len = 50; s->octave = 2; s->chan = 1; s->vel = 100;
    s->bpm = 120; s->cur_note = -1; s->port = -1; s->off_at = -1;
    s->rng = 0x9e3779b9u ^ (uint32_t)(uintptr_t)s;
    alsa_load();
    if (A.ok && A.open(&s->seq, "default", OPEN_OUTPUT, 0) >= 0) {
        snprintf(s->port_name, sizeof s->port_name, "snake %d", ++instances);
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
    snake_t *s = p;
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
static const char *STATE_KEYS[] = {"x_rate", "y_rate", "path", "scale", "root", "gate_len",
                                   "octave", "channel", "velocity"};
static const char *NODE_KEYS[] = {"pitch", "gate", "glide"};

/* "state": every setting as key=value;... (project save), replayed through set_param on load */
static int get_state(snake_t *s, char *b, int n) {
    int len = 0;
    char key[16], v[24];
    for (int i = 0; i < 9 + 3 * NNODES && len < n; i++) {
        if (i < 9) snprintf(key, sizeof key, "%s", STATE_KEYS[i]);
        else snprintf(key, sizeof key, "%s%d", NODE_KEYS[(i - 9) / NNODES], (i - 9) % NNODES + 1);
        if (get_param(s, key, v, sizeof v) > 0) len += snprintf(b + len, (size_t)(n - len), "%s=%s;", key, v);
    }
    return len < n ? len : 0;
}
static void set_state(snake_t *s, const char *str) {
    char buf[4096], *save = NULL;
    snprintf(buf, sizeof buf, "%s", str);
    for (char *t = strtok_r(buf, ";", &save); t; t = strtok_r(NULL, ";", &save)) {
        char *eq = strchr(t, '=');
        if (!eq) continue;
        *eq = 0;
        if (strcmp(t, "state") && strcmp(t, "transport") && strcmp(t, "randomize")) set_param(s, t, eq + 1);
    }
    s->display_rev++;
}

static int node_key(const char *k, const char *pre, int *node) {
    size_t l = strlen(pre);
    if (strncmp(k, pre, l)) return 0;
    char *end;
    long n = strtol(k + l, &end, 10);
    if (*end || n < 1 || n > NNODES) return 0;
    *node = (int)n - 1;
    return 1;
}

static void set_param(void *p, const char *k, const char *v) {
    snake_t *s = p;
    int nd, i;
    if (node_key(k, "pitch", &nd)) s->pitch[nd] = clampi(atoi(v), 0, 14);
    else if (node_key(k, "gate", &nd)) { if ((i = find(ONOFF, 2, v)) >= 0) s->gate[nd] = i; }
    else if (node_key(k, "glide", &nd)) { if ((i = find(ONOFF, 2, v)) >= 0) s->glide[nd] = i; }
    else if (!strcmp(k, "x_rate")) { if ((i = find(RATE_NAMES, 8, v)) >= 0) s->x_rate = i; }
    else if (!strcmp(k, "y_rate")) { if ((i = find(RATE_NAMES, 8, v)) >= 0) s->y_rate = i; }
    else if (!strcmp(k, "path")) { if ((i = find(PATH_NAMES, 4, v)) >= 0) s->path = i; }
    else if (!strcmp(k, "scale")) { if ((i = find(SCALE_NAMES, NSCALES, v)) >= 0) s->scale = i; }
    else if (!strcmp(k, "root")) { if ((i = find(NOTE_NAMES, 12, v)) >= 0) s->root = i; }
    else if (!strcmp(k, "gate_len")) s->gate_len = clampi(atoi(v), 5, 100);
    else if (!strcmp(k, "octave")) s->octave = clampi(atoi(v), 0, 7);
    else if (!strcmp(k, "channel")) s->chan = clampi(atoi(v), 1, 16);
    else if (!strcmp(k, "velocity")) s->vel = clampi(atoi(v), 1, 127);
    else if (!strcmp(k, "randomize")) { if (atof(v) > 0.5) { randomize(s); s->display_rev++; } }
    else if (!strcmp(k, "state")) set_state(s, v);
    else if (!strcmp(k, "lfo_bpm")) { double b = atof(v); if (b > 1) s->bpm = b; }
    else if (!strcmp(k, "transport")) {
        if (v[0] == '1') start(s);
        else { s->playing = 0; note_off(s); }
    }
}

static int get_param(void *p, const char *k, char *b, int n) {
    snake_t *s = p;
    int nd;
    if (node_key(k, "pitch", &nd)) return snprintf(b, n, "%d", s->pitch[nd]);
    size_t kl = strlen(k);
    if (kl >= 14 && !strncmp(k, "pitch", 5) && !strcmp(k + kl - 8, "_display")) {  /* "pitchN_display": note name */
        char key[16];
        snprintf(key, sizeof key, "pitch%.*s", (int)(kl - 13), k + 5);
        if (node_key(key, "pitch", &nd)) {
            int note = node_note(s, nd);
            return snprintf(b, n, "%s%d", NOTE_NAMES[note % 12], note / 12 - 1);
        }
    }
    if (node_key(k, "gate", &nd)) return snprintf(b, n, "%s", s->gate[nd] ? "On" : "Off");
    if (node_key(k, "glide", &nd)) return snprintf(b, n, "%s", s->glide[nd] ? "On" : "Off");
    if (!strcmp(k, "x_rate")) return snprintf(b, n, "%s", RATE_NAMES[s->x_rate]);
    if (!strcmp(k, "y_rate")) return snprintf(b, n, "%s", RATE_NAMES[s->y_rate]);
    if (!strcmp(k, "path")) return snprintf(b, n, "%s", PATH_NAMES[s->path]);
    if (!strcmp(k, "scale")) return snprintf(b, n, "%s", SCALE_NAMES[s->scale]);
    if (!strcmp(k, "root")) return snprintf(b, n, "%s", NOTE_NAMES[s->root]);
    if (!strcmp(k, "gate_len")) return snprintf(b, n, "%d", s->gate_len);
    if (!strcmp(k, "octave")) return snprintf(b, n, "%d", s->octave);
    if (!strcmp(k, "channel")) return snprintf(b, n, "%d", s->chan);
    if (!strcmp(k, "velocity")) return snprintf(b, n, "%d", s->vel);
    if (!strcmp(k, "randomize")) return snprintf(b, n, "0");
    if (!strcmp(k, "state")) return get_state(s, b, n);
    if (!strcmp(k, "display_rev")) return snprintf(b, n, "%d", s->display_rev);
    if (!strcmp(k, "status")) return snprintf(b, n, "MIDI in: %s", s->port_name);
    return 0;
}

static void render(void *p, int16_t *out, int frames) {
    snake_t *s = p;
    memset(out, 0, (size_t)frames * 4);
    if (!s->playing) return;
    double end = s->pos + frames;
    while (1) {
        double tnext = s->next_x < s->next_y ? s->next_x : s->next_y;
        double t = (s->off_at >= 0 && s->off_at <= tnext) ? s->off_at : tnext;
        if (t >= end) break;
        s->pos = t > s->pos ? t : s->pos;
#ifdef SNAKE_TEST
        test_now = s->pos;
#endif
        if (s->off_at >= 0 && s->off_at <= tnext) { note_off(s); s->off_at = -1; }
        else tick(s, s->next_y < s->next_x);   /* tie: the X clock wins */
    }
    s->pos = end;
}

static const mpc_engine_t ENGINE = {create, destroy, midi, set_param, get_param, render, NULL};
const mpc_engine_t *mpc_engine(void) { return &ENGINE; }
