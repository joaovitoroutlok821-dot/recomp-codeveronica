// Experimental same-process AArch64 fiber backend.
// This is deliberately standalone and is NOT wired into ReXGlue production.
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

namespace {
struct Context {
  uint64_t x19_x30[12];
  uint64_t sp;
  uint64_t d8_d15[8];
};
static_assert(offsetof(Context, sp) == 96);
static_assert(offsetof(Context, d8_d15) == 104);
static_assert(sizeof(Context) == 168);

extern "C" void rex_fiber_swap(Context* from, const Context* to);

struct Fiber {
  Context context{};
  std::vector<uint8_t> stack;
  void (*entry)(void*) = nullptr;
  void* arg = nullptr;
  Fiber* return_to = nullptr;
  bool is_thread = false;
};

thread_local Fiber* current_fiber = nullptr;

[[noreturn]] void FiberTrampoline() {
  Fiber* self = current_fiber;
  if (!self || !self->entry || !self->return_to) std::abort();
  self->entry(self->arg);
  Fiber* destination = self->return_to;
  // A completed fiber must never be resumed by this prototype.
  current_fiber = destination;
  rex_fiber_swap(&self->context, &destination->context);
  std::abort();
}
}  // namespace

extern "C" Fiber* rex_fiber_convert_current_thread() {
  if (current_fiber) return nullptr;
  auto* fiber = new Fiber();
  fiber->is_thread = true;
  current_fiber = fiber;
  return fiber;
}

extern "C" Fiber* rex_fiber_create(size_t stack_size, void (*entry)(void*),
                                    void* arg, Fiber* return_to) {
  if (!entry || !return_to || stack_size < 16384) return nullptr;
  auto* fiber = new Fiber();
  fiber->stack.resize(stack_size);
  fiber->entry = entry;
  fiber->arg = arg;
  fiber->return_to = return_to;

  uintptr_t top = reinterpret_cast<uintptr_t>(fiber->stack.data() + fiber->stack.size());
  top &= ~uintptr_t(15);  // AAPCS64 stack alignment.
  fiber->context.sp = top;
  fiber->context.x19_x30[11] =
      reinterpret_cast<uintptr_t>(&FiberTrampoline);  // x30 / initial PC via RET
  return fiber;
}

extern "C" void rex_fiber_switch(Fiber* target) {
  if (!current_fiber || !target || target == current_fiber) std::abort();
  Fiber* from = current_fiber;
  current_fiber = target;
  rex_fiber_swap(&from->context, &target->context);
}

extern "C" void rex_fiber_destroy(Fiber* fiber) {
  if (!fiber || fiber == current_fiber) std::abort();
  if (fiber->is_thread) std::abort();  // Owner-thread teardown is intentionally explicit.
  delete fiber;
}

extern "C" void rex_fiber_release_current_thread(Fiber* fiber) {
  if (!fiber || fiber != current_fiber || !fiber->is_thread) std::abort();
  current_fiber = nullptr;
  delete fiber;
}
