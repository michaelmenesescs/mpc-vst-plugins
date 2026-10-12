// blargg's Gb_Snd_Emu as one translation unit with its buffer classes renamed. The NES library in the same .so has
// its own, different Blip_Buffer and blip_eq_t; linked side by side, one library's constructor ran on the other's
// layout, left the sample rate 0 and aborted in Blip_Buffer::clock_rate_factor when the plugin was created.
// Upstream's build.sh avoids it with `ld -r` + `objcopy --localize-hidden`; the port build has no such step.
#define Blip_Buffer Gb_Blip_Buffer
#define blip_eq_t gb_blip_eq_t
#define Blip_Synth Gb_Blip_Synth
#define Blip_Synth_ Gb_Blip_Synth_
#define Blip_Reader Gb_Blip_Reader
#define Blip_Impulse_ Gb_Blip_Impulse_

#include "../src/libs/gb_snd_emu/Blip_Buffer.cpp"
#include "../src/libs/gb_snd_emu/Multi_Buffer.cpp"
#include "../src/libs/gb_snd_emu/Gb_Oscs.cpp"
#include "../src/libs/gb_snd_emu/Gb_Apu.cpp"
#include "../src/libs/gb_snd_emu/gb_apu_wrapper.cpp"
