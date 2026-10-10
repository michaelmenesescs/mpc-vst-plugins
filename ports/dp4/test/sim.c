/* dp4 offline sim: feed a sine sweep through every algorithm on slot A,
 * then exercise the routing modes. Prints RMS; ASan/UBSan do the real checking. */
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include "engine.h"

static double rms_block(const mpc_engine_t *e, void *s, int blocks, float f0, float f1) {
    int16_t in[256], out[256];
    double e2 = 0; long n = 0;
    for (int b = -350; b < blocks; b++) {   /* warmup: delay lines fill, tails build */
        int bb = b < 0 ? 0 : b;
        for (int i = 0; i < 128; i++) {
            float f = f0 + (f1 - f0) * (bb * 128 + i) / (float)(blocks * 128);
            float v = 0.3f * sinf(6.2831853f * f * (bb * 128 + i) / 44100.0f);
            in[2 * i] = (int16_t)(v * 32767.0f);
            in[2 * i + 1] = (int16_t)(v * 32767.0f);
        }
        e->process(s, in, out, 128);
        if (b < 0) continue;
        for (int i = 0; i < 256; i++) { double x = out[i] / 32768.0; e2 += x * x; n++; }
    }
    return sqrt(e2 / n);
}

static void solo_a(const mpc_engine_t *e, void *s, const char *algo) {
    /* slot A = algo under test, B/C/D off, AB serial, AB->CD serial, master 100% */
    e->set_param(s, "a_algo", algo);
    e->set_param(s, "a_mix", "100");
    e->set_param(s, "b_algo", "Off"); e->set_param(s, "c_algo", "Off"); e->set_param(s, "d_algo", "Off");
    e->set_param(s, "ab_route", "Serial"); e->set_param(s, "cd_route", "Serial");
    e->set_param(s, "ab_cd", "Serial"); e->set_param(s, "mix", "100");
}

int main(void) {
    const mpc_engine_t *e = mpc_engine();
    void *s = e->create(NULL);
    e->set_param(s, "lfo_bpm", "120");
    const char *algs[] = { "Off", "Hall Reverb", "Tempo Delay", "Chorus", "Flanger",
                           "Phaser-DDL", "Pitch Shift", "Distortion", "Para EQ", "Tremolo" };
    char nb[32], db[32];
    for (int a = 0; a < 10; a++) {
        solo_a(e, s, algs[a]);
        double r = rms_block(e, s, 86, 110.0f, 880.0f);   /* ~1 s sweep */
        /* dynamic names + displays */
        e->get_param(s, "a_p1_name", nb, sizeof nb);
        e->get_param(s, "a_p1_display", db, sizeof db);
        printf("algo %-12s rms %.4f %-8s=%-10s %s\n", algs[a], r, nb, db,
               (a == 0 ? (r > 0.15 ? "ok" : "SILENT?") : (r > 0.005 ? "ok" : "SILENT?")));
    }
    /* routing modes: phaser > delay > verb, like the default patch */
    e->set_param(s, "a_algo", "Phaser-DDL"); e->set_param(s, "b_algo", "Tempo Delay");
    e->set_param(s, "c_algo", "Hall Reverb"); e->set_param(s, "d_algo", "Off");
    const char *routes[] = { "Serial", "Parallel", "Feedback 1", "Feedback 2" };
    for (int r = 0; r < 4; r++) {
        e->set_param(s, "ab_route", routes[r]);
        e->set_param(s, "feedback", "40");
        double v = rms_block(e, s, 86, 110.0f, 880.0f);
        printf("AB route %-10s rms %.4f %s\n", routes[r], v, v > 0.005 ? "ok" : "SILENT?");
    }
    e->set_param(s, "ab_route", "Serial");
    e->set_param(s, "ab_cd", "Parallel");
    printf("AB-CD parallel   rms %.4f\n", rms_block(e, s, 86, 110.0f, 880.0f));
    /* display_rev bumps on algo change */
    e->get_param(s, "display_rev", db, sizeof db);
    printf("display_rev %s\n", db);
    e->destroy(s);
    return 0;
}
