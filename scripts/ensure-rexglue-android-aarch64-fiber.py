#!/usr/bin/env python3
"""Install a small AArch64 Android fiber context-switch backend in the pinned ReXGlue SDK."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-aarch64-fiber.py /path/to/rexglue-sdk")

root = Path(sys.argv[1]).resolve()
src = root / "src/core/fiber_posix.cpp"
if not src.is_file():
    raise SystemExit(f"[android-fiber] missing source: {src}")

s = src.read_text(encoding="utf-8")
if "[android-fiber] AArch64 context switch" in s:
    print("[android-fiber] AArch64 backend already installed")
    raise SystemExit(0)

anchor = "#include <cassert>\n"
if anchor not in s:
    raise SystemExit("[android-fiber] expected include anchor not found")

backend = r"""
#if defined(__ANDROID__) && defined(__aarch64__)
// Bionic does not provide makecontext/swapcontext on AArch64. Save the
// callee-saved integer/floating-point registers and SP in storage owned by
// Fiber::context_. This follows the AArch64 procedure-call standard.
#include <cstdint>
#include <cstring>
#include <type_traits>

namespace {
struct AndroidAArch64FiberContext {
  uint64_t x19_x30[12];
  uint64_t sp;
  uint64_t d8_d15[8];
};
static_assert(sizeof(AndroidAArch64FiberContext) <= sizeof(ucontext_t),
              "Fiber context storage is too small for AArch64");

extern "C" void rex_android_aarch64_fiber_switch(
    AndroidAArch64FiberContext* from, AndroidAArch64FiberContext* to);

#if defined(__GNUC__) || defined(__clang__)
__asm__(
    ".text\n"
    ".align 2\n"
    ".global rex_android_aarch64_fiber_switch\n"
    ".type rex_android_aarch64_fiber_switch, %function\n"
    "rex_android_aarch64_fiber_switch:\n"
    "stp x19, x20, [x0, #0]\n"
    "stp x21, x22, [x0, #16]\n"
    "stp x23, x24, [x0, #32]\n"
    "stp x25, x26, [x0, #48]\n"
    "stp x27, x28, [x0, #64]\n"
    "stp x29, x30, [x0, #80]\n"
    "mov x9, sp\n"
    "str x9, [x0, #96]\n"
    "stp d8, d9, [x0, #104]\n"
    "stp d10, d11, [x0, #120]\n"
    "stp d12, d13, [x0, #136]\n"
    "stp d14, d15, [x0, #152]\n"
    "ldp x19, x20, [x1, #0]\n"
    "ldp x21, x22, [x1, #16]\n"
    "ldp x23, x24, [x1, #32]\n"
    "ldp x25, x26, [x1, #48]\n"
    "ldp x27, x28, [x1, #64]\n"
    "ldp x29, x30, [x1, #80]\n"
    "ldp d8, d9, [x1, #104]\n"
    "ldp d10, d11, [x1, #120]\n"
    "ldp d12, d13, [x1, #136]\n"
    "ldp d14, d15, [x1, #152]\n"
    "ldr x9, [x1, #96]\n"
    "mov sp, x9\n"
    "ret\n"
    ".size rex_android_aarch64_fiber_switch, .-rex_android_aarch64_fiber_switch\n");
#endif

AndroidAArch64FiberContext* AndroidContext(ucontext_t* context) {
  return reinterpret_cast<AndroidAArch64FiberContext*>(context);
}
}  // namespace
#endif  // __ANDROID__ && __aarch64__

"""
s = s.replace(anchor, anchor + backend, 1)

s = s.replace("""  if (getcontext(&f->context_) == -1) {
    delete f;
    return nullptr;
  }
  f->is_thread_fiber_ = true;""", """#if defined(__ANDROID__) && defined(__aarch64__)
  std::memset(&f->context_, 0, sizeof(f->context_));
#else
  if (getcontext(&f->context_) == -1) {
    delete f;
    return nullptr;
  }
#endif
  f->is_thread_fiber_ = true;""", 1)

s = s.replace("""  if (getcontext(&f->context_) == -1) {
    delete f;
    return nullptr;
  }
  f->context_.uc_stack.ss_sp = f->stack_.data();
  f->context_.uc_stack.ss_size = f->stack_.size();
  f->context_.uc_link = nullptr;
  // Trampoline reads entry_/arg_ from tls_current_ — no pointer splitting needed.
  makecontext(&f->context_, &Fiber::Trampoline, 0);""", """#if defined(__ANDROID__) && defined(__aarch64__)
  std::memset(&f->context_, 0, sizeof(f->context_));
  auto* context = AndroidContext(&f->context_);
  const uintptr_t stack_top =
      (reinterpret_cast<uintptr_t>(f->stack_.data() + f->stack_.size())) & ~uintptr_t(0xF);
  context->sp = static_cast<uint64_t>(stack_top);
  context->x19_x30[11] = reinterpret_cast<uintptr_t>(&Fiber::Trampoline);
#else
  if (getcontext(&f->context_) == -1) {
    delete f;
    return nullptr;
  }
  f->context_.uc_stack.ss_sp = f->stack_.data();
  f->context_.uc_stack.ss_size = f->stack_.size();
  f->context_.uc_link = nullptr;
  // Trampoline reads entry_/arg_ from tls_current_ — no pointer splitting needed.
  makecontext(&f->context_, &Fiber::Trampoline, 0);
#endif""", 1)

s = s.replace("""  tls_current_ = target;
  swapcontext(&from->context_, &target->context_);""", """  tls_current_ = target;
#if defined(__ANDROID__) && defined(__aarch64__)
  rex_android_aarch64_fiber_switch(AndroidContext(&from->context_),
                                   AndroidContext(&target->context_));
#else
  swapcontext(&from->context_, &target->context_);
#endif""", 1)

if s == src.read_text(encoding="utf-8"):
    raise SystemExit("[android-fiber] no changes applied; expected source anchors did not match")

for required in [
    "rex_android_aarch64_fiber_switch",
    "context->sp = static_cast<uint64_t>(stack_top);",
    "AndroidContext(&target->context_)",
    "#else\n  swapcontext(&from->context_, &target->context_);",
]:
    if required not in s:
        raise SystemExit(f"[android-fiber] sanity check failed; missing {required!r}")

src.write_text(s, encoding="utf-8")
print("[android-fiber] installed AArch64 Android context-switch backend")
