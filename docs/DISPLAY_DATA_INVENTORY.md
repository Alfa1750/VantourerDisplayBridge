# Display data and control inventory

**Status:** Working inventory; confirmed additions below, remaining fields still to be reviewed.  
**Scope:** Values and commands exchanged between Node-RED / Raspberry Pi display bridge and the ESP32-S3 Waveshare 7B.

## Foundational project requirement: bidirectional communication

Bidirectional communication is a core requirement of VantourerDisplayBridge from the beginning of the project, not a newly added feature. The ESP32 must both receive telemetry from the Raspberry Pi and send commands back through the Pi to Node-RED / the relevant device-control interface.

The existing manually developed version on the user's SD-card backup already implements sending and receiving. That backup is the functional reference for restoring the package version to parity. Do not redesign, recreate from memory, or treat bidirectional control as new work. First recover and preserve the working implementation from the backup, then integrate it into the SetupHelper package without regression.

The existing GATT design already reflects both directions:
- TX notification: Raspberry Pi → ESP32.
- RX write: ESP32 → Raspberry Pi.

## Confirmed inventory additions

| Device / source as exposed to Node-RED | Direction | Required field or command | Notes |
|---|---|---|---|
| SmartShunt 1 and 2 | Pi → ESP32 | Battery capacity (Ah) | In addition to the other SmartShunt values still to be finalized. |
| Each MPPT | ESP32 → Pi / Node-RED | Charger enable/disable | Display control requirement; part of the foundational bidirectional control capability. |
| Each MPPT | Pi → ESP32 | Charger on/off state | Display should show the reported state. |
| Orion XS | ESP32 → Pi / Node-RED | Charger enable/disable | Display control requirement; part of the foundational bidirectional control capability. |
| Orion XS | ESP32 → Pi / Node-RED | Configured charging-current limit | The display must allow the set charging current to be adjusted. |
| Orion XS | Pi → ESP32 | Actual charger state and configured current limit | Feedback should reflect reported/configured values after a command. |
| Raspberry Pi | Pi → ESP32 | CPU temperature | Already available through a Venus OS package installed on the system; reuse that existing source. |
| Water tank | Pi → ESP32 | Tank level (%) | Logical tank value exposed by Venus OS / Node-RED. |
| WC tank | Pi → ESP32 | Tank level (%) | Separate logical tank value exposed by Venus OS / Node-RED. |

## Tank representation correction

Do not model “Tank 140” as one separate display data source. Venus OS exposes the two tank levels as Water and WC. The display inventory and protocol should use those two logical values.

## Control-path requirements

- Preserve the existing ESP32 → Pi command path from the manual implementation.
- Commands are routed through the Pi bridge to Node-RED / the agreed device-control interface; the ESP32 does not directly control Victron devices over BLE.
- For MPPT and Orion controls, show the reported actual state/setpoint as feedback, separately from the command requested by the ESP32.
- Capture the existing command format, handling and response behavior from the SD-card backup before changing or extending it. Do not invent a replacement protocol from assumptions.
- Charger controls must respect the JK-BMS charging-protection and other safety logic owned by Node-RED.

## Still to be finalized

This is not yet the complete field map. For each device, confirm the exact telemetry fields, source path, units, scale, update rate, validity/freshness behavior, and whether each field is displayed or only used internally. Exact binary packet offsets and command identifiers belong in the BLE protocol specification after the inventory is agreed and the existing manual implementation has been captured.
