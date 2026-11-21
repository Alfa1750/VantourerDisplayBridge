# Display data and control inventory

**Status:** Working inventory; confirmed additions below, remaining fields still to be reviewed.  
**Scope:** Values and commands exchanged between Node-RED / Raspberry Pi display bridge and the ESP32-S3 Waveshare 7B.

This document distinguishes telemetry sent to the display from control commands sent back from the ESP32. A device may require both directions.

## Confirmed additions and corrections

| Device / source as exposed to Node-RED | Direction | Required field or command | Notes |
|---|---|---|---|
| SmartShunt 1 and 2 | Pi → ESP32 | Battery capacity (Ah) | In addition to the other SmartShunt values still to be finalized. |
| Each MPPT | ESP32 → Pi / Node-RED | Charger enable/disable | Must be operable from the display, including temporarily switching a charger off for testing when no charging input is wanted. |
| Each MPPT | Pi → ESP32 | Charger on/off state | Display should be able to show the actual state, not merely the requested command. |
| Orion XS | ESP32 → Pi / Node-RED | Charger enable/disable | Same operational requirement as the MPPTs. |
| Orion XS | ESP32 → Pi / Node-RED | Configured charging-current limit | The display must allow the set charging current to be adjusted. |
| Orion XS | Pi → ESP32 | Actual charger state and configured current limit | Feedback should reflect the actual/configured values after the command is applied. |
| Raspberry Pi | Pi → ESP32 | CPU temperature | Already available through a Venus OS package installed on the system; reuse that existing source rather than introducing a new measurement method. |
| Water tank | Pi → ESP32 | Tank level (%) | Treat as a tank-level value exposed by Venus OS / Node-RED. |
| WC tank | Pi → ESP32 | Tank level (%) | Treat as a separate tank-level value exposed by Venus OS / Node-RED. |

## Tank representation correction

Do not model “Tank 140” as one separate display data source. Venus OS exposes the two tank levels as Water and WC. The display inventory and protocol should use those two logical values.

## Control-path requirements

- Commands from the ESP32 must be routed through the Pi bridge to Node-RED (or the agreed control interface); the ESP32 must not directly control Victron devices over BLE.
- For MPPT and Orion controls, distinguish requested state/setpoint from confirmed actual state/setpoint.
- Define command acknowledgement, error reporting and timeout behavior before implementing controls.
- Charger controls are intentional operational controls for testing and normal use. They must not bypass any separate safety interlocks or charging-protection logic agreed for the JK-BMS monitor and Node-RED.

## Still to be finalized

This is not yet the complete field map. For each device, confirm the exact telemetry fields, source path, units, scale, update rate, validity/freshness behavior, and whether each field is displayed or only used internally. Exact binary packet offsets and command identifiers belong in the BLE protocol specification after the inventory is agreed.
