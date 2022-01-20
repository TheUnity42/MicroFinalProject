#include <napi.h>

using namespace Napi;

class BrownianMotion : public Napi::AsyncWorker {
  public:
    BrownianMotion(Napi::Function& callback, double start, double end, double step, int seed)
      : Napi::AsyncWorker(callback), start(start), end(end), step(step), seed(seed) {}

    void Execute() {
      srand(seed);
      for (double i = start; i < end; i += step) {
        double r = (double)rand() / RAND_MAX;
        result.push_back(r);
      }
    }

    void OnOK() {
      Napi::HandleScope scope(Env());
      
      Callback().Call({Env().Undefined(), Napi::TypedArrayOf<double>::New(Env(), result.size(), Napi::ArrayBuffer::New(Env(), result.data(), result.size() * sizeof(double)), 0)});
      // 
    }
    private:
      double start;
      double end;
      double step;
      int seed;
      std::vector<double> result;
};

Napi::String runBrownianMotion(const Napi::CallbackInfo& info) {
  double start = info[0].As<Napi::Number>().DoubleValue();
  double end = info[1].As<Napi::Number>().DoubleValue();
  double step = info[2].As<Napi::Number>().DoubleValue();
  int seed = info[3].As<Napi::Number>().Int32Value();
  Napi::Function callback = info[4].As<Napi::Function>();
  BrownianMotion* worker = new BrownianMotion(callback, start, end, step, seed);
  worker->Queue();

  std::string msg = "BrownianMotion started";
  return Napi::String::New(info.Env(), msg);
}

Napi::String Method(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  return Napi::String::New(env, "world");
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  exports["hello"] = Napi::Function::New(env, Method, std::string("hello"));
  exports["runBrownianMotion"] = Napi::Function::New(env, runBrownianMotion, std::string("runBrownianMotion"));
  // exports.Set(Napi::String::New(env, "PaModule"),
  //             Napi::Function::New(env, Method));
  // exports.Set(Napi::String::New(env, "runBrownianMotion"),
  //             Napi::Function::New(env, runBrownianMotion));
  return exports;
}

NODE_API_MODULE(addon, Init)
