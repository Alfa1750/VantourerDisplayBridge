# Architecture

## Intended data path

```text
Venus OS / Victron devices
        |
        v
Node-RED Victron nodes and flow logic
        |
        | TCP (persistent connection; target integration)
        v
Python bridge on Raspberry Pi
        |
        | BLE GATT (notifications + writes)
        v
ESP32-S3 Waveshare 7B display

JK-BMS 1 and JK-BMS 2 ---- BLE directly ----> ESP32-S3
```

## Roles

### Raspberry Pi / Venus OS
- BLE Peripheral and GATT Server.
- Hosts the Python bridge.
- Hosts Node-RED.
- Intended to connect Node-RED and Python over local TCP.
- Camper operation must not depend on Wi-Fi.

### ESP32-S3
- BLE Central and GATT Client for the Pi bridge.
- Receives display data through the Pi's TX notification characteristic.
- Sends commands/data through the Pi's RX write characteristic.
- Reads JK-BMS devices directly over BLE.

### Node-RED
- Uses Victron nodes to collect values from Venus OS.
- Handles selection/configuration of battery data sources.
- Exchanges messages with Python bridge over TCP.

## BLE GATT identifiers

| Item | UUID | Direction | GATT property |
|---|---|---|---|
| Service | `8f7a0001-6d5b-4c3a-9e2f-1a0b2c3d4e5f` | — | Primary service |
| TX | `8f7a0002-6d5b-4c3a-9e2f-1a0b2c3d4e5f` | Pi → ESP32 | Notify |
| RX | `8f7a0003-6d5b-4c3a-9e2f-1a0b2c3d4e5f` | ESP32 → Pi | Write |

BLE advertised local name: `VantourerBridge`.

## Battery-source selection rule

Node-RED must allow explicit manual selection of:
- Both JK-BMS batteries.
- Only the 187 Ah battery.
- Only the 314 Ah battery.

Do not infer that a battery is absent merely because its BLE connection drops. A transient BLE disconnection is not a reliable battery-presence signal.

## Transport decisions

- The intended Node-RED ↔ Python transport is TCP.
- MQTT was investigated but is not the selected display transport.
- BLE between Pi and ESP32 is already demonstrated.
- The actual Python TCP client and application protocol are not implemented/verified yet.

## TCP test details

A Node-RED TCP server was tested on port 5005 using `node-red-contrib-tcp-client2`. The test confirmed bidirectional TCP behavior with a persistent test client. The exact final deployment endpoint, framing, reconnection behavior, timeout policy, and message schema remain to be specified.

## Threading/event-loop requirement

The Python BLE server uses GLib. When TCP integration is implemented, calls that update BLE characteristics from a TCP worker thread must be marshalled safely into the GLib main loop (for example with `GLib.idle_add`), unless the chosen TCP implementation is explicitly integrated with GLib. This is an implementation consideration, not a completed feature.
