# Architecture

## Scope of this repository

This repository contains the Raspberry Pi software for the Vantourer display bridge. It does not contain the JK-BMS monitor or Node-RED flows.

The future JK-BMS monitor will be developed in a separate, independent GitHub repository and installed as a separate SetupHelper/PackageManager package.

## Display data path

```text
Venus OS MQTT battery overview (system/0/Batteries)
        |
        v
Node-RED MQTT Input + normalization Function
        |
        | TCP (Node-RED server :5005; persistent Pi client)
        v
Python bridge on Raspberry Pi
        |
        | BLE GATT (notifications + writes)
        v
ESP32-S3 Waveshare 7B display
```

For the current remote test, the test Pi subscribes to the camper Pi's Venus OS MQTT broker over the LAN using a paired MQTT token and TLS. In the final camper deployment, Node-RED is intended to use the local Venus OS MQTT broker. The same MQTT Input and normalization Function are intended to remain; only the broker selection/connection configuration changes. See `docs/NODERED_MQTT_TEST_STATUS.md` for the observed broker settings, battery inventory and current development state.

The display-data MQTT normalization is based on the `system/0/Batteries` inventory. It selects SmartShunt 1 (instance 293), SmartShunt 2 (instance 294), and the starter battery voltage. The temporary USB-connected JK BMS entry is excluded; both JK BMS devices will be read separately by the independent Raspberry Pi BLE JK-BMS monitor.

## Roles

### Raspberry Pi / Venus OS
- Runs the Python BLE Peripheral / GATT Server for the ESP32 display.
- Hosts Node-RED.
- The display bridge and future JK-BMS monitor are separate processes and separate packages.
- The display bridge must not be a dependency of the JK-BMS monitor, or vice versa.
- Camper operation must not depend on Wi-Fi.

### ESP32-S3
- BLE Central and GATT Client for the Pi display bridge.
- Receives display data through the Pi's TX notification characteristic.
- Sends commands/data through the Pi's RX write characteristic.
- Does **not** read the JK-BMS devices in the target architecture.
- Must not be required for JK-BMS monitoring or charging-protection decisions.

### Node-RED
- Uses MQTT Input to receive Venus OS battery inventory and a Function node to normalize the two SmartShunts and starter battery voltage.
- Receives JK-BMS telemetry from the separate Raspberry Pi BLE JK-BMS monitor.
- Owns battery selection, charging-protection logic and Victron charger control.
- Node-RED flows are imported manually; they are not installed by PackageManager.

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

- Node-RED hosts the TCP server on port 5005; the Python display bridge maintains a reconnecting TCP client to 127.0.0.1:5005 by default.
- TCP records are newline-delimited UTF-8 text. The Pi forwards Node-RED records to BLE TX notifications and ESP32 BLE RX writes back to Node-RED.
- The v0.1.2 test integration does not yet implement the final binary display frame, BLE fragmentation, command schemas, or Victron device-control logic.
- The future JK-BMS monitor will independently connect to both JK-BMS devices over BLE and send telemetry to Node-RED over TCP.
- The JK-BMS monitor is telemetry-only: it does not decide whether charging is allowed and does not control Victron equipment.
- MQTT is used inside Node-RED to read Venus OS values; it is not the ESP32 display transport. The display transport remains TCP from Node-RED to the Pi bridge and BLE from the Pi to the ESP32.

## JK-BMS data and charging-protection boundary

The JK-BMS monitor will forward only the required information, including BMS identity, temperature, low-temperature charge-block status, high-temperature alarm/status, cell voltages, other alarm states, per-BMS connection state and data freshness.

The SmartShunts remain the source of battery current, power and SOC. Venus OS must not register the JK-BMS devices as managed BMS devices; the design must avoid the unwanted DVCC/BMS integration behavior associated with treating them as native BMS devices.

Node-RED alone owns the charging decision. The specific purpose of monitoring the low-temperature charge-block state is:
1. Preventing a false SmartShunt 100% synchronization when one cold BMS blocks charging but the chargers continue charging the other battery.
2. Preventing a large equalization/inrush current between the parallel batteries if one battery becomes substantially fuller while the other is blocked, then the blocked battery later permits charging again.

When any selected/active battery reports a low-temperature charge block, Node-RED must block all charging sources (Orion XS and both MPPTs). Charging may resume only after all selected/active batteries are confirmed clear and the Node-RED recovery policy permits restart.

The JK-BMS devices retain responsibility for their own cell protection. The external monitor is not intended to replace the BMS's internal protection or to make additional cell-protection decisions.

## TCP framing and reliability

The JK-BMS monitor → Node-RED TCP protocol must define message framing (for example, one JSON object per newline-delimited record), reconnection behavior, per-BMS connection status, timestamps/sequence numbers and stale-data handling. These details must be documented and tested before implementation is considered complete.

The display bridge and JK-BMS monitor must each reconnect independently if Node-RED restarts. Failure of the ESP32 or display BLE link must not affect JK-BMS monitoring or charging-protection decisions.

## BLE recovery and reconnection requirement

The ESP32 display must recover automatically when the Raspberry Pi BLE GATT server or its advertising becomes temporarily unavailable and later returns. After a lost connection or failed discovery, the ESP32 must resume scanning/retry discovery with an appropriate retry strategy and reconnect when `VantourerBridge` becomes available again. Recovery must not require a manual ESP32 reboot or power cycle. The implementation must handle both an established connection being lost and the Pi becoming unavailable before a connection is established. This is a design requirement; automatic recovery behavior is not yet implemented or verified.


## JK-BMS acquisition — alternative under evaluation (2026-11-25)

Before implementing the separate custom JK-BMS monitor, test the existing installed dbus-serialbattery package's `Jkbms_Ble` capability with both JK BMS devices simultaneously. Multi-BMS BLE support appears to be available upstream, but simultaneous compatibility and stable behavior with the user's specific devices and Venus OS 3.85 / Raspberry Pi 4B are not yet verified. This is a test-first alternative, not an architecture decision or confirmed success.

A manual Bluetooth-release control is required for the monitor regardless of implementation choice: temporarily suppress the Pi's connection and automatic reconnect attempts to release the JK BMS devices for phone access (e.g. changing settings), then resume and reconnect to both. Avoid disabling the entire Bluetooth adapter or disrupting unrelated BLE devices. The exact control mechanism, status feedback, and recovery behavior must be researched and tested.
