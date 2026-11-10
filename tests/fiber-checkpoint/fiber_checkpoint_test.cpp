#include <rex/thread/fiber.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>

struct TestState {
  rex::thread::Fiber* main_fiber = nullptr;
  uintptr_t inner_stack_address = 0;
  uint64_t outer_canary = 0;
  uint64_t inner_canary = 0;
  unsigned phase = 0;
  bool completed = false;
};

#if defined(__clang__) || defined(__GNUC__)
#define TEST_NOINLINE __attribute__((noinline))
#else
#define TEST_NOINLINE
#endif

TEST_NOINLINE void RecompiledInner(TestState* state) {
  volatile uint64_t inner_local = 0x1122334455667788ull;
  state->inner_stack_address = reinterpret_cast<uintptr_t>(&inner_local);
  state->inner_canary = inner_local;
  state->phase = 1;

  // Simulate a cooperative yield from inside a nested recompiled call.
  rex::thread::Fiber::SwitchTo(state->main_fiber);

  // This line must continue on the same native call stack after resumption.
  if (inner_local != 0x1122334455667788ull ||
      state->inner_canary != 0x1122334455667788ull) {
    std::fprintf(stderr, "FAIL: inner frame was not preserved\n");
    std::abort();
  }
  state->phase = 2;
}

TEST_NOINLINE void RecompiledFunctionLike(TestState* state) {
  volatile uint64_t outer_local = 0x8877665544332211ull;
  state->outer_canary = outer_local;
  RecompiledInner(state);
  if (outer_local != 0x8877665544332211ull ||
      state->outer_canary != 0x8877665544332211ull) {
    std::fprintf(stderr, "FAIL: outer frame was not preserved\n");
    std::abort();
  }
  state->phase = 3;
}

void FiberEntry(void* opaque) {
  auto* state = static_cast<TestState*>(opaque);
  RecompiledFunctionLike(state);
  state->completed = true;
  rex::thread::Fiber::SwitchTo(state->main_fiber);
  std::fprintf(stderr, "FAIL: completed fiber unexpectedly resumed\n");
  std::abort();
}

int main() {
  TestState state;
  state.main_fiber = rex::thread::Fiber::ConvertCurrentThread();
  if (!state.main_fiber) {
    std::fprintf(stderr, "FAIL: ConvertCurrentThread failed\n");
    return 1;
  }

  auto* worker = rex::thread::Fiber::Create(1024 * 1024, FiberEntry, &state);
  if (!worker) {
    std::fprintf(stderr, "FAIL: Fiber::Create failed\n");
    state.main_fiber->Destroy();
    return 1;
  }

  rex::thread::Fiber::SwitchTo(worker);
  if (state.phase != 1 || state.completed) {
    std::fprintf(stderr, "FAIL: first yield state mismatch (phase=%u)\n", state.phase);
    return 1;
  }

  rex::thread::Fiber::SwitchTo(worker);
  if (state.phase != 3 || !state.completed) {
    std::fprintf(stderr, "FAIL: resumed execution did not complete (phase=%u)\n", state.phase);
    return 1;
  }

  worker->Destroy();
  state.main_fiber->Destroy();
  std::puts("FIBER_COOPERATIVE_RESUME=PASS");
  return 0;
}
