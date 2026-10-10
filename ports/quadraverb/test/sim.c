/* quadraverb offline sim: feed a sine sweep through each config, print RMS. */
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include "engine.h"

static double rms_block(const mpc_engine_t *e, void *s, int blocks, float f0, float f1) {
    int16_t in[256], out[256];
    double e2 = 0; long n = 0;
    for (int b = 0; b < blocks; b++) {
        for (int i = 0; i < 128; i++) {
            float f = f0 + (f1 - f0) * (b * 128 + i) / (float)(blocks * 128);
            float v = 0.3f * sinf(6.2831853f * f * (b * 128 + i) / 44100.0f);
            in[2 * i] = (int16_t)(v * 32767.0f);
            in[2 * i + 1] = (int16_t)(v * 32767.0f);
        }
        e->process(s, in, out, 128);
        for (int i = 0; i < 256; i++) { double x = out[i] / 32768.0; e2 += x * x; n++; }
    }
    return sqrt(e2 / n);
}

int main(void) {
    const mpc_engine_t *e = mpc_engine();
    void *s = e->create(NULL);
    e->set_param(s, "lfo_bpm", "120");
    const char *cfgs[] = { "Pitch>Dly>Verb", "Chorus>Dly>Verb", "Flange>Dly>Verb",
                           "Phaser>Verb", "Trem>Dly>Verb", "Reso+Ring>Verb" };
    for (int c = 0; c < 6; c++) {
        e->set_param(s, "config", cfgs[c]);
        /* push the inactive blocks' mixes up so the sweep exercises them */
        e->set_param(s, "fla_mix", "50"); e->set_param(s, "pha_mix", "50");
        e->set_param(s, "pit_mix", "50"); e->set_param(s, "res_mix", "50");
        e->set_param(s, "ring_mix", "50");
        double r = rms_block(e, s, 86, 110.0f, 880.0f);   /* ~1 s sweep */
        printf("config %-16s rms %.4f %s\n", cfgs[c], r, r > 0.01 ? "ok" : "SILENT?");
    }
    e->destroy(s);
    return 0;
}
