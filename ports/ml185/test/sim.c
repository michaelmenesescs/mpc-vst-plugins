#include <stdio.h>
#include <stdint.h>
#include "engine.h"
int main(int argc, char **argv) {
    const mpc_engine_t *e = mpc_engine();
    void *s = e->create(NULL);
    for (int i = 1; i + 1 < argc; i += 2) e->set_param(s, argv[i], argv[i + 1]);
    char b[64]; e->get_param(s, "status", b, sizeof b); printf("# %s\n", b);
    e->set_param(s, "lfo_bpm", "120"); e->set_param(s, "transport", "1");
    int16_t buf[256];
    for (int blk = 0; blk < 44100 * 4 / 128; blk++) e->render(s, buf, 128);   /* 4 s = 2 bars at 120 */
    e->set_param(s, "transport", "0");
    e->destroy(s);
}
