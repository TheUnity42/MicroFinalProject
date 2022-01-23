#include "include/effectsBinding.hh"

namespace EffectsLibBinding {

void threadEntry(TsEffectsContext *context) {

	auto jscall = [context](Napi::Env env, Napi::Function jsCallback, EffectsLib::Buffer* buffer) {
		Napi::Value ret = jsCallback.Call({Napi::Number::New(env, buffer->framesProcessed),
        Napi::Number::New(env, buffer->timeInfo.currentTime),
		Napi::ArrayBuffer::New(env, buffer->input_buffer, buffer->input_buffer_size),
		Napi::ArrayBuffer::New(env, buffer->output_buffer, buffer->output_buffer_size)
		});

		uint8_t retval = (uint8_t) ret.As<Napi::Number>().Int32Value();
		fprintf(stdout, "JS callback returned %d\n", retval);

		if(retval != 0) {
			context->tsfn.Abort();
		}
	};

	auto callback = [context, jscall](EffectsLib::Buffer* buffer) {
		napi_status status = context->tsfn.BlockingCall(buffer, jscall);

		if(status == 1) {
			context->exception = EffectsLib::EffectsException("Aborting thread", 1);
			context->tsfn.Release();
		} else if (status != napi_ok) {			
			Napi::Error::Fatal("ThreadEntry", "Failed to call thread-safe function");
		}

		delete buffer;

		return status == napi_ok;
	};

	EffectsLib::Config config = EffectsLib::StdConfig;

	EffectsLib::ContextData data = {config, 0, (const uint32_t) (config.SAMPLE_RATE * context->duration), callback};

	EffectsLib::Container *container = new EffectsLib::Container();

	try {

		EffectsLib::init(container, data);

		EffectsLib::process(container, data);

		EffectsLib::consume(container, data);

	} catch (EffectsLib::EffectsException &e) {
		fprintf(stderr, "EffectsLib exception: %s\n", e.what());
        context->exception = e;
	}

	delete container;

	context->tsfn.Release();
}

void FinalizerCallback(Napi::Env env, void *finalizeData, TsEffectsContext *context) {
	context->nativeThread.join();

	Napi::Object response = Napi::Object::New(env);
	response.Set("code", Napi::Number::New(env, context->exception.which()));
	response.Set("message", Napi::String::New(env, context->exception.what()));

	context->deferred.Resolve(response);

	delete context;
}

Napi::Value CreateSimple(const Napi::CallbackInfo &info) {
	Napi::Env env = info.Env();

	auto context = new TsEffectsContext(env);

	context->duration = (uint16_t)info[1].As<Napi::Number>().Int32Value();

	// Create the thread-safe function.
	context->tsfn = Napi::ThreadSafeFunction::New(env, info[0].As<Napi::Function>(), "pa_simple", 1,
												  1, context, FinalizerCallback, (void *)nullptr);

	// Create the native thread.
	context->nativeThread = std::thread(threadEntry, context);

	// Return the promise.
	return context->deferred.Promise();
}
} // namespace EffectsLibBinding
