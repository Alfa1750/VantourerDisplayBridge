# Live Node-RED test flow — BLE echte data test (2026-11-24)

## Purpose and status

This document records the user's actual Node-RED test tab **BLE echte data test** used for the successful live battery telemetry test with ESP32 firmware **VictronDisplay7 v0.3.9** and Raspberry Pi bridge **VantourerDisplayBridge v0.1.4**.

This is a record of the live test configuration, not a replacement for the live Node-RED flow and not a production deployment specification. Node-RED flows are maintained independently; the SetupHelper package does not import, overwrite or deploy them.

## Verified end-to-end path

~~~text
Venus OS MQTT broker
  N/b827eb14d4ec/system/0/Batteries
       |
       v
MQTT Input: "alle accus"
       |------------------------------> Debug: "data direct uit mqtt" (disabled in supplied export)
       v
Function: "Normaliseer SmartShunts + startaccu"
       |------------------------------> Debug: "v0.3.9 batterij JSON" (enabled)
       v
Function: "gebruik actieve TCP-client"
       |
       v
TCP Server: port 5005
       |
       v
Pi VantourerDisplayBridge v0.1.4 TCP client
       |
       v
Pi BLE GATT TX notifications (VD fragmentation, <=20 bytes each)
       |
       v
ESP32-S3 / VictronDisplay7 v0.3.9 (reassembly + battery display)
~~~

The user confirmed that battery data appeared on the ESP32 display. Pi logs showed 272–274-byte logical JSON messages transmitted as 20 BLE fragments.

## MQTT broker and input

### Broker configuration selected by the MQTT Input

- Broker host: 192.168.1.113
- Port: 8883
- TLS: enabled, configuration name Victron TLS
- Certificate verification: disabled in the exported TLS configuration (verifyservercert: false)
- MQTT protocol: 3.1.1 (protocolVersion 4)
- Keepalive: 60 seconds
- Client ID: vantourertestpi02
- Clean session: enabled
- No username/password or certificate private key is included in the exported flow.

The broker configuration is a Node-RED configuration node. It is selected by the MQTT Input; it is not a separate wired flow node.

### MQTT Input node "alle accus"

- Topic: N/b827eb14d4ec/system/0/Batteries
- QoS: 2
- Output datatype: auto-detect
- Retain as published: enabled
- Retain handling: 0
- Input wires:
  - to Function Normaliseer SmartShunts + startaccu
  - to Debug data direct uit mqtt (disabled in the supplied export)

## Function: Normaliseer SmartShunts + startaccu

The Function expects the inventory array at msg.payload.value. It identifies:
- SmartShunt 1: instance **293**
- SmartShunt 2: instance **294**
- Starter battery: name matching Startaccu / Starter...; if no name match exists, a unique Venus battery service identifier ending in :1 is used as fallback.
- Temporary USB-connected JK BMS instance **2** is deliberately excluded. JK-BMS 1 and 2 are handled separately by the independent Raspberry Pi JK-BMS monitor.

It searches common identity and measurement field aliases, normalizes values to finite numbers, and uses null when a measurement is missing. A numeric zero remains a valid value. If the inventory is invalid or contains no usable measurements, it warns and emits no message.

### Output JSON schema 1

~~~json
{
  "source": "VantourerDisplay",
  "type": "battery",
  "schema": 1,
  "s1": { "v": 13.36, "i": -0.20, "p": -2.672, "soc": 99.8 },
  "s2": { "v": 13.33, "i": -0.50, "p": -6.665, "soc": 98.4 },
  "st": { "v": 12.70 }
}
~~~

The numeric values above are an illustrative shape based on observed log values, not a guaranteed snapshot. Field meanings:
- s1, s2: SmartShunt 1 and 2.
- st: starter battery.
- v: volts; i: amperes; p: watts; soc: percent.
- Unavailable fields are JSON null; zero is not treated as missing.

The complete Function source is maintained in flows/node-red/normalize_batteries_function.js and was also present in the supplied live flow export.

### Function outputs

The Function output is wired to:
1. Debug node v0.3.9 batterij JSON (enabled, displays msg.payload).
2. Existing Function node gebruik actieve TCP-client.

## Existing TCP routing Function: gebruik actieve TCP-client

This pre-existing node is not recreated by the battery test tab. It uses the flow context key tcpClientTopic, set by the TCP server's connection-status Function, and sends the payload to the currently connected client.

Exact function body from the supplied live export:

~~~javascript
const topic = flow.get("tcpClientTopic");

if (!topic) {
    node.warn("Geen actieve TCP-client gevonden");
    return null;
}

if (typeof msg.payload !== "string") {
    msg.payload = JSON.stringify(msg.payload);
}
if (!msg.payload.endsWith("\n")) {
    msg.payload += "\n";
}

msg.topic = topic;
msg.action = "write";
return msg;
~~~

## Existing TCP Server and connection handling

The existing TCP Server node is named BLE TCP Server:

| Setting | Value |
|---|---|
| Port | 5005 |
| Mode | Stream |
| Data type | UTF-8 |
| Newline delimiter | LF (\\n) |
| Keep Alive Timeout | 6000 ms |
| Application Socket Timeout | 60000 ms |
| Write source | msg.payload |
| Action | msg.action |

It is opened once by Inject node start server once (action=open, once on deploy, 0.1 s delay).

The TCP server output is wired to Function TCP-clientadres onthouden. Exact function body from the supplied live export:

~~~javascript
if (msg.payload === "connected") {
    flow.set("tcpClientTopic", msg.topic);
    node.warn("TCP-client opgeslagen: " + msg.topic);
    return null;
}

msg.action = "write";
if (typeof msg.payload !== "string") {
    msg.payload = JSON.stringify(msg.payload);
}
if (!msg.payload.endsWith("\n")) {
    msg.payload += "\n";
}

return msg;
~~~

This stores the active TCP client's topic when the server reports connected. For other server output, it serializes non-string payloads and ensures newline-delimited UTF-8 output before writing.

The TCP Server output also connects to the Function TCP-clientadres onthouden. The Function output is wired back to the TCP server to perform writes.

## Other nodes in the supplied tab export

- Inject node start server once: opens the TCP server once after deploy.
- Inject node with payload Hallo vanaf Node Red: manual text test; sends through gebruik actieve TCP-client.
- Debug node v0.3.9 batterij JSON: enabled, displays normalized JSON payload.
- Debug node data direct uit mqtt: present but disabled in the supplied export; it can be enabled for raw input inspection.
- MQTT broker TLS config Victron TLS: server certificate verification is disabled in the supplied export. This is recorded as-is, not endorsed as a general security recommendation.
- TCP package dependency recorded in the export: node-red-contrib-tcp-client2 version 1.2.0.

## Live observations and interpretation

- Raw MQTT Debug and normalized JSON Debug timestamps matched in the user's comparison. In that observation, the irregular message spacing was already present at the MQTT Input output; the normalization Function was not the source of the gaps.
- Intervals varied, with examples around 5, 10, 20, 35 and 50 seconds.
- The camper was charging and solar panels were connected. Fluctuating solar/charging power and resulting measured-value changes are a plausible explanation for variable publication timing, but the exact Venus OS MQTT publication rule has not been established.
- Do not label this as a confirmed change-only publication mechanism.
- TCP disconnect/reconnect messages were also observed. Re-deploying the Node-RED flow restored operation in the user's test, but the cause of the earlier TCP closes has not been established.
- The irregular MQTT timing is not evidence by itself of a defect in Pi bridge v0.1.4.

## Reproduction boundary

This is the tested development flow, not necessarily the final production flow. It depends on the existing broker configuration, TCP server, and two existing TCP Functions. Do not import a second broker or TCP server, and do not replace the user's live flow with the import template. The live flow remains on the Node-RED system and is not deployed by GitHub or SetupHelper.

The user controls any live Node-RED edits/deploys, Pi package updates, service restarts, firmware builds and flashes.
