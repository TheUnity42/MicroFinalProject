const PaModule = require("../lib/binding.js");
const assert = require("assert");

assert(PaModule.createTSFN);
assert(PaModule.simplePlayback);

let count = 0;

const callback = (frames, time, input, output) => {
  // console.log(frames, time, new Float32Array(input), new Float32Array(output));
  return 0;
};

// console.log("Creating a new module");
// void async function () {
//   console.log(await PaModule.createTSFN(callback));
// }();

void async function () {
  console.log(await PaModule.simplePlayback(callback, 1));
}();

// assert(PaModule.hello, "The expected function 'hello' is undefined");
// assert(PaModule.runBrownianMotion, "The expected function 'runBrownianMotion' is undefined");

// function testBasic() {
//   const result = PaModule.hello();
//   assert.strictEqual(result, "world", "Unexpected value returned");
// }

// function testBrownian() {
//     console.log(PaModule.runBrownianMotion(0, 15, 0.5, 0, (err, result) => {
//         console.log(result);
//         assert(result);
//      }));
// }

// assert.doesNotThrow(testBasic, undefined, "testBasic threw an expection");
// assert.doesNotThrow(testBrownian, undefined, "testBrownian threw an expection");

console.log("Tests passed- everything looks OK!");
