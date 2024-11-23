
#include "tsequencer.h"
#include <inttypes.h>

mp_obj_t sequencer_callbacks[SEQUENCER_SLOTS];
uint8_t sequencer_dividers[SEQUENCER_SLOTS];

mp_obj_t defer_callbacks[DEFER_SLOTS];
mp_obj_t defer_args[DEFER_SLOTS];
uint32_t defer_sysclock[DEFER_SLOTS];
#ifdef AMY_IS_EXTERNAL
uint32_t sequencer_tick_count = 0;
#endif

void tulip_amy_sequencer_hook(uint32_t tick_count) {
    #ifdef AMY_IS_EXTERNAL
        sequencer_tick_count = tick_count;
    #endif
    for(uint8_t i=0;i<DEFER_SLOTS;i++) {
        if(defer_callbacks[i] != NULL && get_ticks_ms() > defer_sysclock[i]) {
            //fprintf(stderr, "calling defer with sysclock %" PRIu32 " and actual %" PRIu32"\n", defer_sysclock[i], get_ticks_ms() );
            mp_sched_schedule(defer_callbacks[i], defer_args[i]);
            defer_callbacks[i] = NULL; defer_sysclock[i] = 0; defer_args[i] = NULL;
        }
    }

    for(uint8_t i=0;i<SEQUENCER_SLOTS;i++) {
        if(sequencer_dividers[i]!=0) {
            if(tick_count % sequencer_dividers[i] == 0) {
                //fprintf(stderr, "scheduling cb with time %" PRIu64 ", lag %" PRIi32 " tick %" PRIu32 "\n",(next_amy_tick_us/1000)+sequencer_latency_ms, lag, sequencer_tick_count );
                mp_sched_schedule(sequencer_callbacks[i], mp_obj_new_int(tick_count));
            }
        }
    }
}


void tsequencer_init() {
    for(uint8_t i=0;i<SEQUENCER_SLOTS;i++) { sequencer_callbacks[i] = NULL; sequencer_dividers[i] = 0; }
    for(uint8_t i=0;i<DEFER_SLOTS;i++) { defer_callbacks[i] = NULL; defer_sysclock[i] = 0; }
    #ifndef AMY_IS_EXTERNAL
    amy_external_sequencer_hook = tulip_amy_sequencer_hook;
    #endif
}
