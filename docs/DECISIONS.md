# Decisions and constraints

This log records decisions and constraints reconstructed from the development conversation. Items marked **reported** still need confirmation against the live files/system.

## D-001 — Pi is BLE Peripheral, ESP32 is BLE Central
**Status:** Reported tested  
The Raspberry Pi runs the GATT server and advertises `VantourerBridge`. The ESP32 connects as a central/client.

## D-002 — Keep the existing Python BLE GATT server
**Status:** Reported tested  
The existing Python/D-Bus/BlueZ/GLib implementation is the proven BLE foundation. Do not replace it with an alternative Node-RED BLE package without a compelling, tested reason.

## D-003 — Node-RED communicates with Python over TCP
**Status:** Chosen; TCP test proven, bridge integration pending  
A TCP server on Node-RED port 5005 was tested bidirectionally. The Python bridge must become a persistent TCP client or the roles must be deliberately redesigned and documented. Avoid adding MQTT as a second transport.

## D-004 — MQTT is not the display transport
**Status:** Chosen  
MQTT was investigated but is not the intended path for display communication. Node-RED uses Victron nodes to collect Venus OS data; it forwards the required payloads over TCP.

## D-005 — JK-BMS values are read directly by ESP32
**Status:** Chosen  
The ESP32 reads both JK-BMS devices directly over BLE.

## D-006 — Battery selection must be explicit
**Status:** Chosen  
Node-RED must allow manual choice of both batteries, only 187 Ah, or only 314 Ah. BLE disconnection must never be treated as proof of physical absence.

## D-007 — Do not require camper Wi-Fi
**Status:** Constraint  
The camper communication path must not rely on Wi-Fi.

## D-008 — vesmart-server interfered with BLE discovery
**Status:** Reported finding; persistent fix unverified  
Stopping `vesmart-server` allowed the ESP32 to find/connect to the Pi BLE server. VictronConnect remained usable according to the test. Whether the service was disabled permanently and whether this is required on all target systems remain open questions.

## D-009 — SetupHelper is the final installer
**Status:** Required project goal  
The final result must install from a clean Venus OS Raspberry Pi through SetupHelper. A manually configured development Pi alone is not an acceptable deliverable.

## D-010 — GitHub is the source of truth
**Status:** Adopted  
Source code, installer files, documentation, decisions, and test evidence are to be maintained in this private repository. Changes must be committed and tested; the reference Pi is not to be changed destructively during initial capture.

## D-011 — Keep version namespaces separate
**Status:** Required  
ESP32 project v0.3.6 is not the Python bridge version. Python bridge's observed local version marker is v0.1d. Do not rename Python files using the ESP32 version.

## D-012 — Test helpers are not production behavior
**Status:** Required  
Fake telemetry, fixed greeting messages, TCP echo, and manual test clients must be classified as test-only and not shipped as active production behavior.
