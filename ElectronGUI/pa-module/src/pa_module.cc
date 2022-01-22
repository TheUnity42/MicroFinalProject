#include <chrono>
#include <napi.h>
#include <stdio.h>
#include <portaudio.h>
#include <thread>
#include "include/effectsBinding.hh"

constexpr size_t ARRAY_LENGTH = 10;

struct TsfnContext {

  TsfnContext(Napi::Env env) : deferred(Napi::Promise::Deferred::New(env)) {
    for(int i = 0; i < ARRAY_LENGTH; i++) {
      ints[i] = Pa_GetVersion();
    }
  }

  Napi::Promise::Deferred deferred;

  std::thread nativeThread;

  int ints[ARRAY_LENGTH];

  Napi::ThreadSafeFunction tsfn;
};

// The thread entry point. This takes as its arguments the specific
// threadsafe-function context created inside the main thread.
void threadEntry(TsfnContext *context);

// The thread-safe function finalizer callback. This callback executes
// at destruction of thread-safe function, taking as arguments the finalizer
// data and threadsafe-function context.
void FinalizerCallback(Napi::Env env, void *finalizeData, TsfnContext *context);

// Exported JavaScript function. Creates the thread-safe function and native
// thread. Promise is resolved in the thread-safe function's finalizer.
Napi::Value CreateTSFN(const Napi::CallbackInfo &info) {
  Napi::Env env = info.Env();

  auto context = new TsfnContext(env);

  // Create the thread-safe function.
  context->tsfn = Napi::ThreadSafeFunction::New(env, info[0].As<Napi::Function>(), "tsfn", 1, 1,
												context, FinalizerCallback, (void *)nullptr);

  // Create the native thread.
  context->nativeThread = std::thread(threadEntry, context);

  // Return the promise.
  return context->deferred.Promise();
}

void threadEntry(TsfnContext *context) {
  
  auto callback = [](Napi::Env env, Napi::Function jsCallback, int *data) {
    jsCallback.Call({Napi::Number::New(env, *data)});
  };

  for (int i = 0; i < ARRAY_LENGTH; i++) {
    napi_status status = context->tsfn.BlockingCall(&context->ints[i], callback);

    if (status != napi_ok) {
      Napi::Error::Fatal("ThreadEntry", "Failed to call thread-safe function");
    }

	fprintf(stdout, "Sleeping...");
	std::this_thread::sleep_for(std::chrono::milliseconds(200));
  }

  context->tsfn.Release();
}

void FinalizerCallback(Napi::Env env, void *finalizeData, TsfnContext *context) {
  // join threads
  context->nativeThread.join();

  context->deferred.Resolve(Napi::Boolean::New(env, true));
  delete context;
}



Napi::Object Init(Napi::Env env, Napi::Object exports) {
  exports["createTSFN"] = Napi::Function::New(env, CreateTSFN);
  exports["simplePlayback"] = Napi::Function::New(env, EffectsLibBinding::CreateSimple);
  return exports;
}

NODE_API_MODULE(addon, Init)
