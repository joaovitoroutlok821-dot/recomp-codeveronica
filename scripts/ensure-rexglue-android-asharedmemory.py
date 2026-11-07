#!/usr/bin/env python3
"""Ensure ReXGlue initializes Android ASharedMemory before creating file mappings.

The pinned SDK defines AndroidInitialize() but does not call it from
CreateFileMappingHandle(). On API 29+ the legacy /dev/ashmem fallback is
unavailable to ordinary apps, so initialize the API-26+ function lazily and
thread-safely at the allocation site.
"""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-asharedmemory.py /path/to/rexglue-sdk")

sdk = Path(sys.argv[1]).resolve()
source = sdk / "src/core/memory_posix.cpp"
if not source.is_file():
    raise SystemExit(f"ReXGlue POSIX memory source not found: {source}")

text = source.read_text()
include_anchor = "#include <functional>\n"
include_new = include_anchor + "#include <mutex>\n"
if "#include <mutex>" not in text:
    if text.count(include_anchor) != 1:
        raise SystemExit("Could not uniquely locate standard include anchor")
    text = text.replace(include_anchor, include_new, 1)

old_init = """// May be null if no dynamically loaded functions are required.
static void* libandroid_;
// API 26+.
static int (*android_ASharedMemory_create_)(const char* name, size_t size);

void AndroidInitialize() {
  if (rex::GetAndroidApiLevel() >= 26) {
    libandroid_ = dlopen("libandroid.so", RTLD_NOW);
    assert_not_null(libandroid_);
    if (libandroid_) {
      android_ASharedMemory_create_ = reinterpret_cast<decltype(android_ASharedMemory_create_)>(
          dlsym(libandroid_, "ASharedMemory_create"));
      assert_not_null(android_ASharedMemory_create_);
    }
  }
}
"""
new_init = """// May be null if no dynamically loaded functions are required.
static void* libandroid_;
// API 26+.
static int (*android_ASharedMemory_create_)(const char* name, size_t size);
static std::once_flag android_memory_api_once;
static bool android_memory_api_initialized = false;

void AndroidInitialize() {
  std::call_once(android_memory_api_once, [] {
    if (rex::GetAndroidApiLevel() < 26) {
      android_memory_api_initialized = true;
      return;
    }

    libandroid_ = dlopen("libandroid.so", RTLD_NOW);
    if (!libandroid_) {
      REXSYS_ERROR("Android memory: dlopen(libandroid.so) failed: {}", dlerror());
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

    android_memory_api_initialized = true;
    REXSYS_INFO("Android memory: ASharedMemory_create initialized");
  });
}
"""
if old_init in text:
    text = text.replace(old_init, new_init, 1)
elif new_init not in text:
    raise SystemExit("AndroidInitialize block did not match the pinned SDK; refusing an unsafe patch")

old_create = """#if REX_PLATFORM_ANDROID
  // TODO(Triang3l): Check if memfd can be used instead on API 30+.
  if (android_ASharedMemory_create_) {
"""
new_create = """#if REX_PLATFORM_ANDROID
  // Ensure API-26+ shared memory is loaded before any mapping is created.
  // std::call_once inside AndroidInitialize makes this safe across threads.
  AndroidInitialize();

  // TODO(Triang3l): Check if memfd can be used instead on API 30+.
  if (android_ASharedMemory_create_) {
"""
if old_create in text:
    text = text.replace(old_create, new_create, 1)
elif new_create not in text:
    raise SystemExit("CreateFileMappingHandle Android anchor did not match; refusing an unsafe patch")

# Do not silently fall back to /dev/ashmem on API 26+ if the modern API failed.
old_fallback = """  // Use /dev/ashmem on API versions below 26, which added ASharedMemory.
  // /dev/ashmem was disabled on API 29 for apps targeting it.
"""
new_fallback = """  // ASharedMemory is mandatory on API 26+ for modern target SDKs.
  // Do not fall back to /dev/ashmem if loading the supported API failed.
  if (rex::GetAndroidApiLevel() >= 26) {
    REXSYS_ERROR("Android memory: ASharedMemory_create unavailable on API {}",
                 rex::GetAndroidApiLevel());
    return kFileMappingHandleInvalid;
  }

  // Use /dev/ashmem only on API versions below 26.
"""
if old_fallback in text:
    text = text.replace(old_fallback, new_fallback, 1)
elif new_fallback not in text:
    raise SystemExit("ashmem fallback anchor did not match; refusing an unsafe patch")

if text.count("AndroidInitialize();") != 1:
    raise SystemExit("Expected exactly one lazy AndroidInitialize call")
if "std::call_once(android_memory_api_once" not in text:
    raise SystemExit("Thread-safe initialization verification failed")
if "ASharedMemory_create unavailable on API" not in text:
    raise SystemExit("Modern API failure guard verification failed")

source.write_text(text)
print("ReXGlue Android ASharedMemory initialization patch: PASS")
