#!/usr/bin/env python3
"""Remove the obsolete pre-API-26 thread-name call from the Android SDK build."""
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-thread-name-compat.py /path/to/rexglue-sdk")

src = Path(sys.argv[1]).resolve() / "src/core/threading_posix.cpp"
if not src.is_file():
    raise SystemExit(f"[android-thread-name] missing source: {src}")

s = src.read_text(encoding="utf-8")
before = s

# The target is Android API 26+, where pthread_setname_np is available.
# Remove the unavailable header and any source line invoking the old helper.
s = s.replace("#include <rex/main_android.h>\n", "")
s, removed_calls = re.subn(
    r"^[ \t]*.*SetAndroidPreApi26Name\(name\);[ \t]*\n",
    "",
    s,
    flags=re.MULTILINE,
)

if "#include <rex/main_android.h>" in s:
    raise SystemExit("[android-thread-name] obsolete header reference remains")
if re.search(r"^[ \t]*.*SetAndroidPreApi26Name\(name\);", s, flags=re.MULTILINE):
    raise SystemExit("[android-thread-name] obsolete helper call remains")
if "pthread_setname_np(thread_, std::string(name).c_str());" not in s:
    raise SystemExit("[android-thread-name] expected Android thread naming call missing")

if s == before:
    print("[android-thread-name] patch already applied")
    raise SystemExit(0)
if removed_calls == 0 and "SetAndroidPreApi26Name" in before:
    raise SystemExit("[android-thread-name] obsolete helper reference found but no call line was removed")

# Android NDK builds do not expose the SDK's legacy API-level helper.
# Use the NDK API and avoid Linux-only robust pthread mutex APIs on Android.
thread_src = src
threading = thread_src.read_text(encoding="utf-8")
threading_before = threading
if "#include <android/api-level.h>" not in threading:
    anchor = "#include <pthread.h>\n"
    if anchor not in threading:
        raise SystemExit("[android-thread-name] pthread include anchor missing")
    threading = threading.replace(anchor, anchor + "#if defined(__ANDROID__)\n#include <android/api-level.h>\n#endif\n", 1)
threading = threading.replace("rex::GetAndroidApiLevel()", "android_get_device_api_level()")
threading = threading.replace(
    "#if REX_PLATFORM_LINUX\n    // Use robust mutexes so waits can recover if owner thread terminates.",
    "#if REX_PLATFORM_LINUX && !REX_PLATFORM_ANDROID\n    // Use robust mutexes so waits can recover if owner thread terminates."
)
threading = threading.replace(
    "#if REX_PLATFORM_LINUX\n    auto native_mutex = static_cast<pthread_mutex_t*>(mutex_.native_handle());",
    "#if REX_PLATFORM_LINUX && !REX_PLATFORM_ANDROID\n    auto native_mutex = static_cast<pthread_mutex_t*>(mutex_.native_handle());"
)
threading = threading.replace(
    "#if REX_PLATFORM_LINUX\n        auto native_mutex = static_cast<pthread_mutex_t*>(handles[i]->mutex_.native_handle());",
    "#if REX_PLATFORM_LINUX && !REX_PLATFORM_ANDROID\n        auto native_mutex = static_cast<pthread_mutex_t*>(handles[i]->mutex_.native_handle());"
)
if "rex::GetAndroidApiLevel()" in threading:
    raise SystemExit("[android-thread-name] obsolete API-level helper remains in threading_posix.cpp")
if "pthread_mutexattr_setrobust(&attr, PTHREAD_MUTEX_ROBUST)" in threading and "#if REX_PLATFORM_LINUX && !REX_PLATFORM_ANDROID\n    // Use robust mutexes" not in threading:
    raise SystemExit("[android-thread-name] Linux robust mutex constructor guard was not applied")
if threading == threading_before:
    print("[android-thread-name] threading_posix.cpp already patched")
else:
    thread_src.write_text(threading, encoding="utf-8")
    print("[android-thread-name] patched NDK API level and Linux-only robust mutex paths")

src.write_text(s, encoding="utf-8")
print("[android-thread-name] removed obsolete pre-API-26 helper call")
