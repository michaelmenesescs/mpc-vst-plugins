/* Schwung audio_fx_api_v2 DSP -> mpc_engine_t (wrapper/engine.h). Linked in by build_port.sh when a
 * port's vst.json names an "adapter": "schwungfx" (effect modules that export move_audio_fx_init_v2,
 * not move_plugin_init_v2). Schwung's contract (44.1 kHz, 128-frame int16 stereo) matches the engine
 * interface; the only real difference is the effect entry point and an in-place process_block(). */
#include <stddef.h>
#include <string.h>
#include <stdint.h>
#include "../../wrapper/engine.h"

typedef struct {
    uint32_t api_version;
    void *(*create_instance)(const char *module_dir, const char *config_json);
    void (*destroy_instance)(void *instance);
    void (*process_block)(void *instance, int16_t *audio_inout, int frames);
    void (*set_param)(void *instance, const char *key, const char *val);
    int (*get_param)(void *instance, const char *key, char *buf, int buf_len);
} audio_fx_api_v2_t;
extern audio_fx_api_v2_t *move_audio_fx_init_v2(const void *host);

static audio_fx_api_v2_t *api;

static void *create(const char *dir) { return api->create_instance(dir ? dir : "", NULL); }
static void destroy(void *i) { api->destroy_instance(i); }
static void midi(void *i, const uint8_t *m, int n) { (void)i; (void)m; (void)n; }
static void set_param(void *i, const char *k, const char *v) { api->set_param(i, k, v); }
static int get_param(void *i, const char *k, char *b, int n) { return api->get_param(i, k, b, n); }
static void render(void *i, int16_t *o, int f) { (void)i; (void)o; (void)f; }
static void process(void *i, const int16_t *in, int16_t *out, int f) {
    if (in != out) memcpy(out, in, (size_t)f * 2 * sizeof(int16_t));
    api->process_block(i, out, f);
}

static const mpc_engine_t engine = { create, destroy, midi, set_param, get_param, render, process };

const mpc_engine_t *mpc_engine(void) {
    if (!api) api = move_audio_fx_init_v2(NULL);
    return api ? &engine : NULL;
}