#!/usr/bin/env python3
"""Replace std::jthread/stop_token in the pinned SDK timer queue for Android libc++."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-thread-compat.py /path/to/rexglue-sdk")

src = Path(sys.argv[1]).resolve() / "src/core/timer_queue.cpp"
if not src.is_file():
    raise SystemExit(f"[android-thread] missing source: {src}")

s = src.read_text(encoding="utf-8")
before = s

replacements = [
    ("#include <algorithm>\n#include <forward_list>",
     "#include <algorithm>\n#include <atomic>\n#include <forward_list>\n#include <thread>"),
    ("    dispatch_thread_ =\n        std::jthread([this](std::stop_token stop_token) { TimerThreadMain(stop_token); });",
     "    dispatch_thread_ = std::thread([this] { TimerThreadMain(); });"),
    ("    dispatch_thread_.request_stop();",
     "    stop_requested_.store(true, std::memory_order_release);"),
    ("    // Kick dispatch thread to check stop token",
     "    // Queue a sentinel to wake the dispatch thread so it can observe stop_requested_."),
    ("    // std::jthread auto-joins on destruction",
     "    if (dispatch_thread_.joinable()) {\n      dispatch_thread_.join();\n    }"),
    ("  void TimerThreadMain(std::stop_token stop_token) {",
     "  void TimerThreadMain() {"),
    ("    while (!stop_token.stop_requested()) {",
     "    while (!stop_requested_.load(std::memory_order_acquire)) {"),
    ("  std::jthread::id dispatch_thread_id() const { return dispatch_thread_.get_id(); }",
     "  std::thread::id dispatch_thread_id() const { return dispatch_thread_.get_id(); }"),
    ("  std::jthread dispatch_thread_;",
     "  std::atomic<bool> stop_requested_{false};\n  std::thread dispatch_thread_;"),
]

for old, new in replacements:
    if new in s:
        continue
    if old not in s:
        raise SystemExit(f"[android-thread] expected source anchor not found: {old.splitlines()[0]}")
    s = s.replace(old, new, 1)

src.write_text(s, encoding="utf-8")
final = src.read_text(encoding="utf-8")
for required in [
    "#include <atomic>",
    "dispatch_thread_ = std::thread([this] { TimerThreadMain(); });",
    "stop_requested_.store(true, std::memory_order_release);",
    "while (!stop_requested_.load(std::memory_order_acquire))",
    "std::thread::id dispatch_thread_id() const",
    "std::atomic<bool> stop_requested_{false};",
    "dispatch_thread_.join();",
]:
    if required not in final:
        raise SystemExit(f"[android-thread] sanity check failed; missing: {required}")
for forbidden in ["std::jthread", "std::stop_token", "request_stop()"]:
    if forbidden in final:
        raise SystemExit(f"[android-thread] unsupported construct remains: {forbidden}")
print("[android-thread] timer queue uses std::thread + atomic stop flag on Android: OK")
