/**
 * Node-RED Function: normalize Venus OS system/0/Batteries for ESP32 v0.3.9.
 *
 * Input: msg.payload.value from N/<portal>/system/0/Batteries.
 * Output: compact battery JSON expected by VictronDisplay7 v0.3.9.
 * Connect to the existing TCP-client routing Function; it appends the newline.
 *
 * Selected sources: SmartShunt instances 293 and 294, plus the starter battery.
 * The temporary USB-connected JK BMS (instance 2) is intentionally excluded.
 * Missing measurements are null; zero remains a valid measurement.
 */
const inventory = msg.payload && msg.payload.value;
if (!Array.isArray(inventory)) {
    node.warn("Accu-overzicht: msg.payload.value is geen array");
    return null;
}

function isRecord(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
}

function firstDefined(object, keys) {
    if (!isRecord(object)) return undefined;
    for (const key of keys) {
        if (Object.prototype.hasOwnProperty.call(object, key) &&
            object[key] !== null && object[key] !== undefined && object[key] !== "") {
            return object[key];
        }
    }
    return undefined;
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
        const id = identity(item);
        return Number(id.instance) === instance ||
            id.id.endsWith(":" + instance) ||
            id.id.endsWith("battery." + instance);
    });
}

function findStarter() {
    const named = inventory.find(item =>
        /startaccu|starter(?: battery| accu)?/i.test(identity(item).name));
    if (named) return named;

    // Service instance suffix :1 is a fallback only; USB adapter names are not stable.
    const fallback = inventory.filter(item =>
        /com\.victronenergy\.battery\.[^:]+:1$/.test(identity(item).id));
    return fallback.length === 1 ? fallback[0] : undefined;
}

function normalizedKey(key) {
    return String(key).toLowerCase().replace(/[^a-z0-9]/g, "");
}

function unwrapNumber(raw) {
    if (isRecord(raw)) raw = firstDefined(raw, ["value", "Value"]);
    if (typeof raw !== "number" && typeof raw !== "string") return null;
    if (typeof raw === "string" && raw.trim() === "") return null;
    const value = Number(raw);
    return Number.isFinite(value) ? value : null;
}

function metric(item, aliases) {
    const wanted = new Set(aliases.map(normalizedKey));
    const containers = [item];
    for (const key of ["values", "measurements", "data", "value"]) {
        const nested = firstDefined(item, [key]);
        if (isRecord(nested)) containers.push(nested);
    }

    for (const container of containers) {
        if (!isRecord(container)) continue;
        for (const key of Object.keys(container)) {
            if (wanted.has(normalizedKey(key))) {
                const value = unwrapNumber(container[key]);
                if (value !== null) return value;
            }
        }
    }
    return null;
}

function shuntMeasurements(item) {
    return {
        v: metric(item, ["voltage", "dc_voltage", "Dc/0/Voltage", "v"]),
        i: metric(item, ["current", "dc_current", "Dc/0/Current", "i"]),
        p: metric(item, ["power", "dc_power", "Dc/0/Power", "p"]),
        soc: metric(item, ["soc", "state_of_charge", "StateOfCharge"])
    };
}

const shunt1 = findShunt(293);
const shunt2 = findShunt(294);
const starter = findStarter();
const s1 = shuntMeasurements(shunt1);
const s2 = shuntMeasurements(shunt2);
const st = { v: metric(starter, ["voltage", "dc_voltage", "Dc/0/Voltage", "v"]) };

const hasMeasurements = [s1.v, s1.i, s1.p, s1.soc, s2.v, s2.i, s2.p, s2.soc, st.v]
    .some(value => value !== null);
if (!hasMeasurements) {
    node.warn("Accu-overzicht: geen bruikbare SmartShunt/startaccu-meetwaarden gevonden");
    return null;
}

if (!shunt1 || !shunt2 || !starter) {
    node.warn("Accu-overzicht gedeeltelijk: shunt1=" + !!shunt1 +
        ", shunt2=" + !!shunt2 + ", startaccu=" + !!starter);
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
