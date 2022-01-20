const PaModule = require("../lib/binding.js");
const assert = require("assert");

assert(PaModule.hello, "The expected function 'hello' is undefined");
assert(PaModule.runBrownianMotion, "The expected function 'runBrownianMotion' is undefined");

function testBasic() {
  const result = PaModule.hello();
  assert.strictEqual(result, "world", "Unexpected value returned");
}

function testBrownian() {
    console.log(PaModule.runBrownianMotion(0, 15, 0.5, 0, (err, result) => {
        console.log(result);
        assert(result);
     }));
}

assert.doesNotThrow(testBasic, undefined, "testBasic threw an expection");
assert.doesNotThrow(testBrownian, undefined, "testBrownian threw an expection");

console.log("Tests passed- everything looks OK!");
