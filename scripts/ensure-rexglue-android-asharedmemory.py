#!/usr/bin/env python3
"""Initialize Android ASharedMemory lazily before ReXGlue file mappings."""
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-asharedmemory.py /path/to/rexglue-sdk")

source = Path(sys.argv[1]).resolve() / "src/core/memory_posix.cpp"
if not source.is_file():
    raise SystemExit(f"ReXGlue POSIX memory source not found: {source}")
text = source.read_text()

if "#include <mutex>" not in text:
    anchor = "#include <functional>\n"
    if text.count(anchor) != 1:
        raise SystemExit("Could not uniquely locate standard include anchor")
    text = text.replace(anchor, anchor + "#include <mutex>\n", 1)

if "#include <android/api-level.h>" not in text:
    anchor = "#include <mutex>\n"
    if text.count(anchor) != 1:
        raise SystemExit("Could not uniquely locate mutex include")
    text = text.replace(anchor, anchor + "#include <android/api-level.h>\n", 1)

# Replace only AndroidInitialize's body, preserving adjacent AndroidShutdown().
init_pattern = re.compile(
    r"void AndroidInitialize\(\)\s*\{.*?\n\}",
    re.S,
)
new_init = """static std::once_flag android_memory_api_once;

void AndroidInitialize() {
  std::call_once(android_memory_api_once, [] {
    if (android_get_device_api_level() < 26) {
      return;
    }

    libandroid_ = dlopen("libandroid.so", RTLD_NOW);
    if (!libandroid_) {
      const char* error = dlerror();
      REXSYS_ERROR("Android memory: dlopen(libandroid.so) failed: {}",
                   error ? error : "unknown error");
      return;
    }

    dlerror();
    android_ASharedMemory_create_ = reinterpret_cast<decltype(android_ASharedMemory_create_)>(
        dlsym(libandroid_, "ASharedMemory_create"));
    const char* symbol_error = dlerror();
    if (symbol_error || !android_ASharedMemory_create_) {
      REXSYS_ERROR("Android memory: dlsym(ASharedMemory_create) failed: {}",
                   symbol_error ? symbol_error : "symbol is null");
      android_ASharedMemory_create_ = nullptr;
      return;
    }
    REXSYS_INFO("Android memory: ASharedMemory_create initialized");
  });
}"""
if "static std::once_flag android_memory_api_once;" not in text:
    text, count = init_pattern.subn(new_init, text, count=1)
    if count != 1:
        raise SystemExit("Could not uniquely replace AndroidInitialize() in pinned SDK")
elif "Android memory: ASharedMemory_create initialized" not in text:
    raise SystemExit("Existing ASharedMemory patch is incomplete")

create_anchor = """#if REX_PLATFORM_ANDROID
  // TODO(Triang3l): Check if memfd can be used instead on API 30+."""
create_replacement = """#if REX_PLATFORM_ANDROID
  // Initialize the API-26+ shared-memory function before any mapping is created.
  AndroidInitialize();

  // TODO(Triang3l): Check if memfd can be used instead on API 30+."""
if "  AndroidInitialize();\n" not in text:
    if text.count(create_anchor) != 1:
        raise SystemExit("Could not uniquely locate Android mapping creation block")
    text = text.replace(create_anchor, create_replacement, 1)

fallback_anchor = """  // Use /dev/ashmem on API versions below 26, which added ASharedMemory.
  // /dev/ashmem was disabled on API 29 for apps targeting it."""
fallback_replacement = """  // Do not use the legacy /dev/ashmem device on API 26+.
  if (android_get_device_api_level() >= 26) {
    REXSYS_ERROR("Android memory: ASharedMemory_create unavailable on API {}",
                 android_get_device_api_level());
    return kFileMappingHandleInvalid;
  }

  // Legacy /dev/ashmem fallback for API levels below 26."""
if fallback_replacement not in text:
    if text.count(fallback_anchor) != 1:
        raise SystemExit("Could not uniquely locate legacy ashmem fallback")
    text = text.replace(fallback_anchor, fallback_replacement, 1)

if text.count("AndroidInitialize();") != 1:
    raise SystemExit("Expected exactly one lazy AndroidInitialize() call")
if text.count("static std::once_flag android_memory_api_once;") != 1:
    raise SystemExit("Expected exactly one once_flag declaration")
if "ASharedMemory_create unavailable on API" not in text:
    raise SystemExit("Modern API failure guard verification failed")

source.write_text(text)
print("ReXGlue Android ASharedMemory initialization patch: PASS")
