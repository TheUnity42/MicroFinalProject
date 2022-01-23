#include <napi.h>
#include "../resources/include/portaudio.h"
#include "include/effectsBinding.hh"

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  exports["simplePlayback"] = Napi::Function::New(env, EffectsLibBinding::CreateSimple);
  return exports;
}

NODE_API_MODULE(addon, Init)
