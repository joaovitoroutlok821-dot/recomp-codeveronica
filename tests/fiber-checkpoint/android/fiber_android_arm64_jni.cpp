#include <jni.h>
#include <string>
extern "C" int rex_run_android_arm64_fiber_test();
extern "C" JNIEXPORT jstring JNICALL Java_org_rexglue_fiberprobe_MainActivity_runFiberTest(JNIEnv* env,jobject){
 const int r=rex_run_android_arm64_fiber_test();
 const std::string s=r==0?"ANDROID_ARM64_FIBER_RESUME=PASS\n32 ciclos concluídos; 256 alternâncias.\nVariáveis locais/endereço e registradores x19-x29, d8-d15 preservados.":"ANDROID_ARM64_FIBER_RESUME=FAIL\nCódigo: "+std::to_string(r);
 return env->NewStringUTF(s.c_str());
}
