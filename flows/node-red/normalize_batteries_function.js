/**
 * Node-RED Function node: Normalize Venus OS system/0/Batteries inventory
 * Input: msg.payload.value (array from N/<portal>/system/0/Batteries)
 * Output: compact JSON string for ESP32 v0.3.9; TCP sender adds the newline.
 *
 * Wire:
 *   MQTT Input (N/<portal>/system/0/Batteries)
 *     -> this Function
 *     -> existing "gebruik actieve TCP-client" Function
 *     -> BLE TCP Server node
 *
 * No zero defaults: unavailable measurements are emitted as null.
 */
const inventory = msg.payload && msg.payload.value;
if (!Array.isArray(inventory)) {
    node.warn("Accu-overzicht: msg.payload.value is geen array");
    return null;
}

function firstDefined(obj, keys) {
    if (!obj || typeof obj !== "object") return undefined;
    for (const key of keys) {
        if (Object.prototype.hasOwnProperty.call(obj, key) && obj[key] !== null && obj[key] !== undefined && obj[key] !== "") {
            return obj[key];
        }
    }
    return undefined;
}

function numeric(obj, keys) {
    const raw = firstDefined(obj, keys);
    if (raw === undefined) return null;
    const value = Number(raw);
    return Number.isFinite(value) ? value : null;
}

function identity(item) {
    return {
        instance: firstDefined(item, ["instance", "Instance", "device_instance"]),
        id: String(firstDefined(item, ["id", "service", "service_id", "identifier"]) || ""),
        name: String(firstDefined(item, ["name", "Name", "product_name"]) || "")
    };
}

function findShunt(instance) {
    return inventory.find(item => {
        const ident = identity(item);
        return Number(ident.instance) === instance ||
            ident.id.endsWith(":" + instance) ||
            ident.id.endsWith("battery." + instance);
    });
}

function findStarter() {
    return inventory.find(item => {
        const ident = identity(item);
        return /startaccu|starter/i.test(ident.name) ||
            /ttyUSB4:1$/.test(ident.id);
    });
}

function measurements(item) {
    // Field aliases cover the inventory property naming variants; only actual numeric values pass.
    return {
        v: numeric(item, ["voltage", "Voltage", "dc_voltage", "Dc/0/Voltage", "v"]),
        i: numeric(item, ["current", "Current", "dc_current", "Dc/0/Current", "i"]),
        p: numeric(item, ["power", "Power", "dc_power", "Dc/0/Power", "p"]),
        soc: numeric(item, ["soc", "Soc", "state_of_charge", "StateOfCharge", "SOC"])
    };
}

const shunt1 = findShunt(293);
const shunt2 = findShunt(294);
const starter = findStarter();

if (!shunt1 || !shunt2 || !starter) {
    node.warn("Accu-overzicht: bron ontbreekt; shunt1=" + !!shunt1 +
        ", shunt2=" + !!shunt2 + ", startaccu=" + !!starter);
    return null;
}

const s1 = measurements(shunt1);
const s2 = measurements(shunt2);
const st = { v: numeric(starter, ["voltage", "Voltage", "dc_voltage", "Dc/0/Voltage", "v"]) };

if (s1.v === null && s1.i === null && s1.p === null && s1.soc === null &&
    s2.v === null && s2.i === null && s2.p === null && s2.soc === null && st.v === null) {
    node.warn("Accu-overzicht: geen bruikbare meetwaarden in inventaris");
    return null;
}

msg.payload = JSON.stringify({
    source: "VantourerDisplay",
    type: "battery",
    schema: 1,
    s1: s1,
    s2: s2,
    st: st
});
return msg;
