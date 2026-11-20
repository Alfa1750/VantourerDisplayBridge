# JK-BMS Monitor — design specification

**Status:** Architecture agreed; implementation not started in this repository.  
**Target repository:** A separate future GitHub repository for VantourerJKMonitor.

## Purpose

Read two JK-BMS devices directly from the Raspberry Pi over BLE and forward selected telemetry to Node-RED. The monitor must not register either JK-BMS as a managed BMS device in Venus OS.

The purpose of low-temperature monitoring is not to replace the JK-BMS cell protection. The BMS devices retain their own internal cell protection. External monitoring is required for two system-level reasons:
1. Prevent a false SmartShunt synchronization to 100% when one cold battery blocks charging but the chargers continue charging the other parallel battery.
2. Prevent a potentially harmful equalization/inrush current between the parallel batteries if one battery becomes much fuller while the other is charge-blocked and later becomes charge-enabled.

## Package and repository separation

- VantourerJKMonitor will have its own GitHub repository.
- It will be installed as a separate SetupHelper/PackageManager package.
- It is fully independent of VantourerDisplayBridge; neither package is a prerequisite for the other.
- Each application has its own Python process, runit service, logs, updates and lifecycle.
- Both may use the OS-provided BlueZ stack and the same physical Bluetooth adapter.
- PackageManager installs Pi software only. It does not install or import Node-RED flows.

## JK-BMS monitor responsibilities

The Pi service acts as BLE client for both JK-BMS devices and:
- Identifies each BMS by its configured identity/name.
- Reads temperature.
- Reads low-temperature charge-block status.
- Reads high-temperature status/alarm.
- Reads cell voltages.
- Reads other available alarm states.
- Tracks each BMS connection independently.
- Marks data with timestamps/sequence information and exposes whether it is current.
- Sends telemetry to Node-RED.

It must **not**:
- Decide whether charging is allowed.
- Turn Orion XS or MPPTs on/off.
- Apply the manual battery selection.
- Replace or override the JK-BMS internal cell protection.
- Expose the JK-BMS devices to Venus OS as managed BMS devices.
- Require the ESP32 to be powered or connected.

The SmartShunts remain authoritative for current (A), power (W) and SOC.

## Node-RED responsibilities

Node-RED alone:
- Provides manual battery configuration: both batteries, only 187 Ah, or only 314 Ah.
- Determines which BMS telemetry is relevant based on that manual selection.
- Treats a disconnected or stale selected BMS as unknown/untrusted, never as physically absent or safe.
- Blocks charging if any selected BMS reports low-temperature charge block.
- Controls Orion XS and both MPPTs.
- Decides when charging can resume after all selected BMS devices are confirmed clear.
- Implements all recovery delays, hysteresis, alarms and user-visible status.

A non-selected battery must not trigger the charging-protection policy.

## Telemetry transport to Node-RED

Initial transport: local TCP, initiated by the JK-BMS monitor as a persistent client connection to Node-RED.

Node-RED receives messages using standard TCP In and JSON nodes. No custom Node-RED node is required.

The implementation must define and test:
- TCP port and bind address.
- Message framing (recommended initial format: one JSON object per newline-delimited record).
- JSON schema and field types.
- Per-BMS connection state and data timestamps.
- Reconnect behavior after Node-RED or monitor restart.
- Stale-data timeout and how Node-RED detects missing messages.
- Startup ordering and behavior when Node-RED is not yet listening.

The monitor sends telemetry only. All charging decisions remain in Node-RED.

## Future display transport

The ESP32 display is not part of the JK-BMS acquisition or charging-protection path. The Pi may later forward selected data to the ESP32 using VantourerDisplayBridge. A future Wi-Fi/MQTT display transport may be considered, but it is optional and must not be required for JK-BMS monitoring or charging protection.

## Implementation status

No JK-BMS monitor code, SetupHelper package, TCP protocol or Node-RED flow is claimed to exist yet. This document records the agreed target design only.
