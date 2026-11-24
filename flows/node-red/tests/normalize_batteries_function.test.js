const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const test = require("node:test");

const functionSource = fs.readFileSync(
    path.join(__dirname, "..", "normalize_batteries_function.js"), "utf8");

function runFunction(payload) {
    const warnings = [];
    const context = {
        msg: { payload },
        node: { warn: message => warnings.push(message) }
    };
    const result = vm.runInNewContext(
        "(function(msg, node) {\n" + functionSource + "\n})(msg, node)", context);
    return { result, warnings };
}

test("maps Shunt 1, Shunt 2 and starter battery; excludes USB JK BMS", () => {
    const input = { value: [
        { name: "187Ah accu", id: "com.victronenergy.battery.ttyUSB4",
          instance: 293, voltage: 13.68, current: 22.9, power: 313.272, soc: 82 },
        { name: "Startaccu", id: "com.victronenergy.battery.ttyUSB4:1", voltage: 12.97 },
        { name: "Shunt 2", id: "com.victronenergy.battery.ttyUSB5",
          instance: 294, voltage: 13.60, current: 34.4, power: 467.84, soc: 81.4 },
        { name: "JK BMS", id: "com.victronenergy.battery.ttyUSB6",
          instance: 2, voltage: 99, current: 99, power: 99, soc: 99 }
    ] };
    const { result } = runFunction(input);
    const packet = JSON.parse(result.payload);
    assert.equal(packet.source, "VantourerDisplay");
    assert.equal(packet.type, "battery");
    assert.equal(packet.schema, 1);
    assert.deepEqual(JSON.parse(JSON.stringify(packet.s1)),
        { v: 13.68, i: 22.9, p: 313.272, soc: 82 });
    assert.deepEqual(JSON.parse(JSON.stringify(packet.s2)),
        { v: 13.6, i: 34.4, p: 467.84, soc: 81.4 });
    assert.deepEqual(JSON.parse(JSON.stringify(packet.st)), { v: 12.97 });
});

test("supports nested value wrappers, partial inventory and real zero values", () => {
    const input = { value: [
        { instance: 293, values: {
            Voltage: { value: 13.5 }, Current: { value: 0 },
            Power: { value: 0 }, SOC: { value: 0 }
        } }
    ] };
    const { result, warnings } = runFunction(input);
    const packet = JSON.parse(result.payload);
    assert.equal(packet.s1.v, 13.5);
    assert.equal(packet.s1.i, 0);
    assert.equal(packet.s1.p, 0);
    assert.equal(packet.s1.soc, 0);
    assert.deepEqual(JSON.parse(JSON.stringify(packet.s2)),
        { v: null, i: null, p: null, soc: null });
    assert.deepEqual(JSON.parse(JSON.stringify(packet.st)), { v: null });
    assert.equal(warnings.length, 1);
});

test("rejects missing inventory and inventory without usable measurements", () => {
    assert.equal(runFunction({}).result, null);
    assert.equal(runFunction({ value: [{ instance: 293, voltage: "not-a-number" }] }).result, null);
});

