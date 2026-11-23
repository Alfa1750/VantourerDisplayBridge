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
## D-022 — Bidirectional ESP32 display control is a foundational requirement
**Status:** Core requirement; active Pi implementation is the reference, package parity pending
VantourerDisplayBridge has been bidirectional from the beginning: the Pi sends telemetry to the ESP32 using GATT notifications, and the ESP32 sends commands to the Pi using GATT writes. The ESP32 must be able to operate supported devices through the Pi and Node-RED, not merely display telemetry. This is a core purpose of the bridge, not a newly introduced feature.

The currently running, manually developed software on the reference Pi is the technical reference. Inspect the active files actually used by its running services and establish their behavior from that live installation. The only Pi project files excluded from inspection/comparison are `/data/VantourerDisplayBridge/src/gatt_server_backup.py` and `/data/VantourerDisplayBridge/src/gatt_server_v0.3.6.py`. Paragon full-SD backups of the Pi are permitted and should be used as recovery/restore points; they are not excluded. Bring the SetupHelper/PackageManager version into functional parity with the active Pi implementation. Do not reconstruct the command path from memory, redesign it unnecessarily, or describe bidirectional operation as new scope.

Specific controls being inventoried include MPPT enable/disable and Orion XS enable/disable plus adjustable configured charging-current limit. Actual state/setpoint feedback must be represented separately from a requested command. Exact command encoding and response behavior must be captured from the confirmed active Pi implementation before changes are made. Node-RED safety and JK-BMS charging-protection logic remain authoritative.

## D-023 — BLE notification MTU truncation fixed in ESP32 firmware v0.3.6
**Status:** Reported tested successfully; version applies to ESP32 firmware only
The initial Pi-to-ESP32 notification test was limited to 20 bytes (`Hallo vanaf Raspberr`), consistent with the default ATT MTU of 23. This was fixed on the **ESP32 client side** in ESP32 `ble_bridge.c` by explicitly starting MTU exchange on connection with `ble_gattc_exchange_mtu(s_conn_handle, on_mtu_exchange, NULL)`. The `on_mtu_exchange(...)` callback logs the result and starts `discover_service()` only after MTU exchange; service discovery was moved to that callback path. After flashing, the ESP32 received the complete message `Hallo vanaf de Raspberry Pi`. The user identified this working **ESP32 firmware** as **v0.3.6**.

**Versioning distinction:** v0.3.6 is exclusively the ESP32 firmware version. It is not a version of the Raspberry Pi bridge or its package. During the original Pi-side development, changes were made manually and no consistent Pi software versioning scheme was maintained. The Pi bridge involved in these tests must therefore be described as the manually developed, unversioned Pi implementation; do not assign it v0.3.6 or imply a corresponding Pi release.

The reverse text direction had also been tested: the Pi received/logged `Hallo vanaf ESP32` after the ESP32 enabled notifications. Together, these tests establish bidirectional BLE text transport between the manually developed Pi bridge and ESP32 firmware v0.3.6. The exact negotiated MTU value is not recorded and must not be guessed.

This does **not** prove that actual Victron commands were forwarded to Node-RED or that MPPT/Orion controls were tested. It also does not mean the future binary display-frame format or its fragmentation is implemented. See [BLE_DISPLAY_PROTOCOL.md](BLE_DISPLAY_PROTOCOL.md) for the detailed test history and the distinction between the proven ESP32 v0.3.6 text transport and the future binary protocol design.

**Do not repeat the 20-byte truncation investigation or reimplement this ESP32-side fix without first inspecting the ESP32 v0.3.6 reference code. Preserve the manually developed Pi implementation separately when bringing the SetupHelper/PackageManager Pi package to parity.**


## D-024 — Raspberry Pi software version baseline and parity milestone
**Status:** Adopted; GitHub baseline set to v0.1.0
The Raspberry Pi VantourerDisplayBridge software represented in this GitHub branch is now version **v0.1.0**. The root `version` file is the PackageManager version marker for the Pi software.

The original Pi-side development was performed through manual changes without consistent versioning. Do not assign the ESP32 firmware version to the Pi implementation. The historical `pi-snapshot/version` marker is retained as snapshot evidence and is not the current root package version.

Every subsequent Pi-side development step increments the patch version in sequence: **v0.1.1, v0.1.2, v0.1.3**, etc. The **v0.2.0** version is reserved for the explicit milestone at which the GitHub Pi implementation has reached functional parity with the manually developed Pi reference implementation. Do not declare v0.2.0 until that parity has been checked and confirmed.

ESP32 firmware versioning remains completely independent; ESP32 v0.3.6 does not identify a Pi software or PackageManager release. See [CHANGELOG.md](../CHANGELOG.md) and [PROJECT_STATUS.md](PROJECT_STATUS.md).

## D-025 — Step-based Pi versioning and tested recovery points
**Status:** Adopted

Pi software versions represent distinct, meaningful development steps, not individual test attempts.

- The current baseline is **v0.1.0**.
- When a new development step begins, assign its version number immediately (for example **v0.1.1**). Keep that same version number throughout all coding, debugging, and repeated tests belonging to that step. Do not increment the version for every code edit or test attempt.
- Record meaningful code changes and intermediate states as Git commits. Commits preserve the exact history within a development step.
- When a step has been tested successfully and is accepted as a working state, create a Git tag for that version. This tag is a known-good recovery point.
- Only when beginning the next distinct development step, increment the patch version (for example v0.1.2, then v0.1.3). If a step does not work, continue correcting and testing under its existing version number.
- Preserve all known-good tags so development can return to the most recent working intermediate step. Do not move or overwrite an existing version tag.
- The PackageManager branch may and must expose the current in-development version so it can be installed and tested through the normal GUI workflow. A version does **not** need to be tested or accepted before it is available for installation. Use commits to preserve intermediate states and keep the version number unchanged throughout one development step. A Git tag is created only after the user confirms that step is tested and accepted; tags identify known-good recovery points, not prerequisites for installation.
- The ESP32 firmware version history remains independent of Pi software versioning.

A version number therefore identifies a development step; a Git commit identifies an exact code state within that step; and a Git tag identifies an accepted, known-good state.

## D-026 — Use only active Pi software as the implementation reference
**Status:** Adopted; mandatory working rule

When comparing the manually developed Raspberry Pi implementation with GitHub v0.1.0 and preparing GitHub v0.1.1, use **only the software files that are confirmed to be active in the running Pi installation**. Determine active files from the actual running service configuration/processes and their referenced paths.

Only **two specific files** in the Raspberry Pi project directory are excluded from technical inspection and comparison:
1. `/data/VantourerDisplayBridge/src/gatt_server_backup.py`
2. `/data/VantourerDisplayBridge/src/gatt_server_v0.3.6.py`

Do not open, inspect, compare, or use those two files as implementation references. No other Pi files or backups are excluded by this rule. In particular, Paragon full-SD backups/images of the Raspberry Pi are allowed and should be used as recovery points; they may be restored when needed to recover a test system. Do not confuse those Paragon recovery backups with the two excluded files above.

The active implementation reference remains the software files confirmed to be used by running services/processes.

For this project comparison, the two authoritative sources are:
1. The confirmed active software currently running on the reference Pi.
2. The existing GitHub **v0.1.0** implementation.

All changes to bring GitHub into parity are made under GitHub **v0.1.1**, following the established versioning and recovery-point rules. The Pi is a read-only reference and must not be modified during this capture and comparison process.

This rule is persistent and applies to all subsequent investigation, code comparison, documentation and implementation work. Do not ask the user to repeat it.


## D-027 — ESP32 must recover BLE discovery and connection automatically
**Status:** Required design behavior; implementation and verification pending

The ESP32 display must automatically recover when the Pi's BLE GATT server or advertising is temporarily unavailable and later becomes available again. It must resume scanning/retry discovery and reconnect to `VantourerBridge` without requiring a manual ESP32 restart or power cycle. This applies both when an established BLE connection is lost and when the Pi is unavailable during initial discovery. The implementation must handle temporary Pi/server outages and subsequent restoration robustly.

The November 23, 2026 test provided the motivating observation: after `vesmart-server` was stopped on the Pi, the ESP32 did not find the now-available bridge until the ESP32 was restarted. This demonstrates the need for automatic recovery, but does not by itself establish the exact firmware-side cause. Do not treat the behavior as implemented until it has been tested without manually restarting the ESP32.
