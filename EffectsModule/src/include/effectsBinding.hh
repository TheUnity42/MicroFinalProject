#include "effectslib.hh"
#include <chrono>
#include <napi.h>
#include <stdio.h>
#include <thread>

namespace EffectsLibBinding {
struct TsEffectsContext {

	TsEffectsContext(Napi::Env env) : deferred(Napi::Promise::Deferred::New(env)) {}

	uint16_t duration;

	Napi::Promise::Deferred deferred;

	std::thread nativeThread;

	Napi::ThreadSafeFunction tsfn;

    EffectsLib::EffectsException exception;
};

void threadEntry(TsEffectsContext *context);

void FinalizerCallback(Napi::Env env, void *finalizeData, TsEffectsContext *context);

Napi::Value CreateSimple(const Napi::CallbackInfo &info);

} // namespace EffectsLibBinding