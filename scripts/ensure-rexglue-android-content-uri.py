#!/usr/bin/env python3
"""Add JNI-backed Android ContentResolver access to the pinned ReXGlue SDK."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-content-uri.py /path/to/rexglue-sdk")

root = Path(sys.argv[1]).resolve()
src = root / "src/core/filesystem_posix.cpp"
if not src.is_file():
    raise SystemExit(f"[android-content-uri] missing source: {src}")

s = src.read_text(encoding="utf-8")
include_anchor = '#include <string.h>\n'
include_patch = '''#include <string.h>

#if REX_PLATFORM_ANDROID
#include <SDL3/SDL_system.h>
#include <jni.h>
#include <string>
#endif
'''
if "#include <SDL3/SDL_system.h>" not in s:
    if include_anchor not in s:
        raise SystemExit("[android-content-uri] include anchor not found")
    s = s.replace(include_anchor, include_patch, 1)

function = r"""
#if REX_PLATFORM_ANDROID
int OpenAndroidContentFileDescriptor(std::string_view uri, const char* mode) {
  auto* env = static_cast<JNIEnv*>(SDL_GetAndroidJNIEnv());
  auto activity = static_cast<jobject>(SDL_GetAndroidActivity());
  if (!env || !activity || !mode) {
    if (env && env->ExceptionCheck()) env->ExceptionClear();
    return -1;
  }

  jclass activity_class = nullptr;
  jobject resolver = nullptr;
  jclass uri_class = nullptr;
  jstring uri_string = nullptr;
  jobject parsed_uri = nullptr;
  jclass resolver_class = nullptr;
  jstring mode_string = nullptr;
  jobject parcel_file_descriptor = nullptr;
  jclass pfd_class = nullptr;

  auto cleanup = [&]() {
    if (pfd_class) env->DeleteLocalRef(pfd_class);
    if (parcel_file_descriptor) env->DeleteLocalRef(parcel_file_descriptor);
    if (mode_string) env->DeleteLocalRef(mode_string);
    if (resolver_class) env->DeleteLocalRef(resolver_class);
    if (parsed_uri) env->DeleteLocalRef(parsed_uri);
    if (uri_string) env->DeleteLocalRef(uri_string);
    if (uri_class) env->DeleteLocalRef(uri_class);
    if (resolver) env->DeleteLocalRef(resolver);
    if (activity_class) env->DeleteLocalRef(activity_class);
    env->DeleteLocalRef(activity);
  };
  auto fail = [&]() {
    if (env->ExceptionCheck()) env->ExceptionClear();
    cleanup();
    return -1;
  };

  activity_class = env->GetObjectClass(activity);
  if (!activity_class || env->ExceptionCheck()) return fail();
  jmethodID get_content_resolver =
      env->GetMethodID(activity_class, "getContentResolver",
                       "()Landroid/content/ContentResolver;");
  if (!get_content_resolver || env->ExceptionCheck()) return fail();
  resolver = env->CallObjectMethod(activity, get_content_resolver);
  if (!resolver || env->ExceptionCheck()) return fail();

  uri_class = env->FindClass("android/net/Uri");
  if (!uri_class || env->ExceptionCheck()) return fail();
  jmethodID uri_parse =
      env->GetStaticMethodID(uri_class, "parse",
                             "(Ljava/lang/String;)Landroid/net/Uri;");
  if (!uri_parse || env->ExceptionCheck()) return fail();
  const std::string uri_utf8(uri);
  uri_string = env->NewStringUTF(uri_utf8.c_str());
  if (!uri_string || env->ExceptionCheck()) return fail();
  parsed_uri = env->CallStaticObjectMethod(uri_class, uri_parse, uri_string);
  if (!parsed_uri || env->ExceptionCheck()) return fail();

  resolver_class = env->GetObjectClass(resolver);
  if (!resolver_class || env->ExceptionCheck()) return fail();
  jmethodID open_file_descriptor =
      env->GetMethodID(resolver_class, "openFileDescriptor",
                       "(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;");
  if (!open_file_descriptor || env->ExceptionCheck()) return fail();
  mode_string = env->NewStringUTF(mode);
  if (!mode_string || env->ExceptionCheck()) return fail();
  parcel_file_descriptor =
      env->CallObjectMethod(resolver, open_file_descriptor, parsed_uri, mode_string);
  if (!parcel_file_descriptor || env->ExceptionCheck()) return fail();

  pfd_class = env->GetObjectClass(parcel_file_descriptor);
  if (!pfd_class || env->ExceptionCheck()) return fail();
  jmethodID detach_fd = env->GetMethodID(pfd_class, "detachFd", "()I");
  if (!detach_fd || env->ExceptionCheck()) return fail();
  const jint fd = env->CallIntMethod(parcel_file_descriptor, detach_fd);
  if (env->ExceptionCheck() || fd < 0) return fail();

  cleanup();
  return static_cast<int>(fd);
}
#endif  // REX_PLATFORM_ANDROID

"""
if "int OpenAndroidContentFileDescriptor(std::string_view uri, const char* mode)" not in s:
    anchor = "}  // namespace filesystem\n}  // namespace rex"
    if anchor not in s:
        raise SystemExit("[android-content-uri] namespace anchor not found")
    s = s.replace(anchor, function + anchor, 1)

src.write_text(s, encoding="utf-8")
print("[android-content-uri] ContentResolver bridge installed")
