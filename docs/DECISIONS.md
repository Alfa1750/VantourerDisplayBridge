# Decisions and constraints

This log records project decisions. Items marked **reported** still need confirmation against the live files/system.

## D-001 — Pi is BLE Peripheral, ESP32 is BLE Central
**Status:** Reported tested  
The Raspberry Pi runs the GATT server and advertises `VantourerBridge`. The ESP32 connects as a central/client.

## D-002 — Keep the existing Python BLE GATT server
**Status:** Reported tested  
The existing Python/D-Bus/BlueZ/GLib implementation is the proven BLE foundation. Do not replace it with an alternative Node-RED BLE package without a compelling, tested reason.

## D-003 — Node-RED communicates with the display bridge over TCP
**Status:** Chosen; TCP test proven, bridge integration pending  
The intended display path is Node-RED ↔ Python display bridge over TCP. Do not confuse this with the separate JK-BMS telemetry connection.

## D-004 — MQTT is not required for the initial display transport
**Status:** Chosen  
The camper must not depend on Wi-Fi. A later Wi-Fi/MQTT option for the ESP32 display may be considered, but it is not a dependency for JK-BMS monitoring or charging protection.

## D-005 — JK-BMS devices are read directly by the Raspberry Pi
**Status:** Chosen  
A separate Python service on the Pi will act as BLE client for both JK-BMS devices. The ESP32 will not read the JK-BMS devices in the target architecture. The Pi monitor will only collect and forward telemetry; it will not make charging decisions or control Victron equipment.

## D-006 — JK-BMS monitor is a separate, independent package/repository
**Status:** Chosen  
VantourerJKMonitor will be developed in its own GitHub repository and installed as its own SetupHelper/PackageManager package. It must not depend on VantourerDisplayBridge, and VantourerDisplayBridge must not depend on it. Each has its own process, runit service, logs, lifecycle and updates. Both may use the shared OS-provided BlueZ stack and physical Bluetooth adapter.

## D-007 — JK-BMS telemetry is sent to Node-RED over TCP
**Status:** Chosen; protocol/implementation pending  
The monitor will initiate/maintain a TCP connection to Node-RED and send structured telemetry (planned JSON). Node-RED can receive it using standard TCP In and JSON nodes; no custom Node-RED node is required. Message framing, port, schema, reconnect and timeout behavior must be specified and tested.

## D-008 — Node-RED owns all charging logic
**Status:** Chosen  
The JK-BMS monitor is telemetry-only. Node-RED owns manual battery selection, interpretation of the telemetry, charging block/release policy and control of Orion XS plus both MPPTs. Node-RED flows are imported manually and are not installed by PackageManager.

## D-009 — Purpose of low-temperature monitoring
**Status:** Chosen  
The purpose is specifically:
1. Prevent false SmartShunt synchronization to 100% when a cold BMS blocks its own charging while the chargers continue charging the other parallel battery.
2. Prevent a potentially harmful equalization/inrush current between the parallel batteries if one battery becomes much fuller while the other is blocked and later becomes charge-enabled.

The JK-BMS devices already protect their own cells. The external monitor is not intended to replace that protection.

## D-010 — Charging block behavior
**Status:** Chosen; Node-RED flow not yet implemented  
If any selected/active battery reports a low-temperature charge block, Node-RED must disable all charging sources: Orion XS and both MPPTs. Charging may resume only when every selected/active battery is confirmed clear and the Node-RED recovery policy allows restart. A disconnected or stale selected BMS must be treated as unknown/untrusted by Node-RED, not as absent or safe. A non-selected battery must not trigger the policy.

## D-011 — SmartShunts remain authoritative for current, power and SOC
**Status:** Chosen  
The JK-BMS monitor does not need to provide current, power or SOC for this design. Those values continue to come from the two SmartShunts.

## D-012 — Do not register JK-BMS devices as Venus OS BMS devices
**Status:** Chosen  
The JK-BMS monitor must read the devices independently without exposing them to Venus OS as managed BMS devices. This avoids unwanted DVCC/BMS behavior from an integration that is not a native CAN BMS connection.

## D-013 — Battery selection must be explicit
**Status:** Chosen  
Node-RED must allow manual choice of both batteries, only 187 Ah, or only 314 Ah. BLE disconnection must never be treated as proof of physical absence.

## D-014 — Do not require camper Wi-Fi
**Status:** Constraint  
The initial monitoring and charging-protection path uses local BLE and local TCP; it must not require Wi-Fi.

## D-015 — vesmart-server interfered with BLE discovery
**Status:** Reported finding; persistent fix unverified  
Stopping `vesmart-server` allowed the ESP32 to find/connect to the Pi BLE server. Whether this service must be stopped on all target systems remains an open question.

## D-016 — SetupHelper is the final Pi installer
**Status:** Required project goal  
Each Pi application package must install on a clean Venus OS Raspberry Pi through SetupHelper/PackageManager. A manually configured development Pi alone is not an acceptable deliverable.

## D-017 — GitHub is the source of truth
**Status:** Adopted  
Source code, installer files, documentation, decisions and test evidence are maintained in GitHub. The reference Pi must not be changed destructively during initial capture.

## D-018 — PackageManager and Node-RED flows are separate
**Status:** Chosen  
PackageManager installs only Raspberry Pi application software/services. Node-RED flows are distributed separately and imported manually by the user.

## D-019 — Keep version namespaces separate
**Status:** Required  
ESP32 firmware versions, display-bridge package versions and future JK-BMS monitor package versions are independent. Do not conflate their version numbers.

## D-020 — Test helpers are not production behavior
**Status:** Required  
Fake telemetry, fixed greeting messages, TCP echo and manual test clients must be classified as test-only and not shipped as active production behavior.
## D-021 — Compact binary BLE display frames and MTU target
**Status:** Design agreed; implementation and live negotiation not yet verified
The Pi ↔ ESP32 display data path will use a versioned, fixed-layout binary frame rather than textual numeric values or JSON. Numeric measurements should use documented scaled integers where appropriate (for example 12.85 V as 1285 with scale ×100). Every field must define its device/source, measurement, width, signedness, scale, unit, byte order and validity representation. The packet must include protocol/version and sequence information and distinguish valid zero values from unavailable or stale data.

The design target is an ATT MTU of 247 bytes, allowing up to 244 bytes of notification value (ATT_MTU - 3). This is a target, not a claim that the value has already been negotiated. Both Pi and ESP32 must support/request it, and the effective MTU must be checked after connection. The application sends one logical display frame; if it exceeds the available notification payload, it must be fragmented with reassembly metadata rather than truncated.

See [BLE_DISPLAY_PROTOCOL.md](BLE_DISPLAY_PROTOCOL.md) for the protocol design. Exact field offsets, types, scales, status layout and fragmentation format remain to be finalized before implementation.