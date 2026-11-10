#include <cstdint>
#include <cstddef>
struct Fiber;
extern "C" Fiber* rex_fiber_convert_current_thread();
extern "C" Fiber* rex_fiber_create(size_t, void (*)(void*), void*, Fiber*);
extern "C" void rex_fiber_switch(Fiber*);
extern "C" void rex_fiber_destroy(Fiber*);
extern "C" void rex_fiber_release_current_thread(Fiber*);
struct State { Fiber* main=nullptr; uintptr_t inner_address=0; uint64_t outer_value=0; unsigned phase=0; unsigned switches=0; bool failed=false; };
__attribute__((noinline)) static void Nested(State* s) {
  volatile uint64_t local=0xA1B2C3D4E5F60718ull; s->inner_address=reinterpret_cast<uintptr_t>(&local);
  for(unsigned i=0;i!=8;++i){ if(local!=0xA1B2C3D4E5F60718ull)s->failed=true; ++s->switches; rex_fiber_switch(s->main); }
  if(reinterpret_cast<uintptr_t>(&local)!=s->inner_address)s->failed=true; s->phase=2;
}
__attribute__((noinline)) static void Outer(State* s) {
  volatile uint64_t local=0x1029384756ABCDEFull; s->outer_value=local; Nested(s);
  if(local!=s->outer_value)s->failed=true; s->phase=3;
}
static void Entry(void* p){Outer(static_cast<State*>(p));}
extern "C" int rex_run_android_arm64_fiber_test(){
#if !defined(__aarch64__)
 return 77;
#else
 State state; state.main=rex_fiber_convert_current_thread(); if(!state.main)return 1;
 Fiber* worker=rex_fiber_create(1024*1024,Entry,&state,state.main);
 if(!worker){rex_fiber_release_current_thread(state.main);return 2;}
 for(unsigned i=0;i!=8;++i){rex_fiber_switch(worker);if(state.phase!=0||state.switches!=i+1)state.failed=true;}
 rex_fiber_switch(worker);
 const bool passed=!state.failed&&state.phase==3&&state.switches==8;
 rex_fiber_destroy(worker); rex_fiber_release_current_thread(state.main); return passed?0:4;
#endif
}
