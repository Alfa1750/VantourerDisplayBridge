# Changelog

## Live validation note — ESP32 v0.3.9 + Pi v0.1.4 + Node-RED battery test (2026-11-24)
- User confirmed the live battery telemetry test works on the camper setup with ESP32 firmware v0.3.9 and Raspberry Pi bridge package v0.1.4.
- Pi log showed 272–274-byte battery JSON records sent as 20 BLE fragments; the ESP32 received and displayed the battery data.
- The complete test tab "BLE echte data test", including MQTT input, normalization, Debug nodes, TCP server and routing Functions, is documented in docs/NODERED_LIVE_TEST_FLOW.md.
- MQTT topic: N/b827eb14d4ec/system/0/Batteries; SmartShunt instances 293 and 294 plus starter battery; temporary USB JK BMS instance 2 excluded.
- MQTT message intervals were observed to be irregular at the MQTT Input itself. Solar/charging-related value changes are a plausible explanation, not a proven publication rule. The bridge is not established as the cause.
- This is a successful development test, not a production release or SetupHelper clean-install/reboot acceptance. The Node-RED flow remains independently managed on the live Node-RED system.
- No Pi runtime, Node-RED flow, firmware, build or flash was changed by this documentation commit.


## v0.1.4 — v0.3.9 battery telemetry transport and Node-RED nodes (development)
- Add a Node-RED Function that maps SmartShunt instances 293 and 294 plus starter battery voltage to the compact JSON contract expected by ESP32 firmware v0.3.9.
- Add an importable Node-RED tab containing the normalization Function, a Debug node, and wiring instructions. It reuses the existing MQTT input, active TCP-client routing Function, and TCP server; no broker credentials or duplicate server are included.
- Add a shared Pi BLE framing helper. Each notification is at most 20 bytes and carries the `VD` versioned fragment header, so the sender works at the minimum ATT MTU of 23.
- Queue fragments at 10 ms intervals; reject empty or oversized logical messages instead of truncating them.
- Add source-level tests for the framing helper and Node-RED normalization Function. Synthetic JavaScript fixtures were exercised in the ChatGPT JavaScript runtime. GitHub Actions run `45443182121` passed Python syntax, TCP client tests, Node-RED Function tests, flow JSON validation, and package-layout checks. The live Node-RED runtime and Pi BLE link have not been tested.
- Raspberry Pi package version marker: v0.1.4. This is independent of ESP32 firmware v0.3.9.
- Build/install/deployment on the Raspberry Pi: not performed. Hardware BLE validation: pending.


## Development note — Venus OS MQTT battery input investigation (2026-11-24; not a package version)
- Confirmed the test Pi and camper Pi both run Venus OS 3.85 and are on the same LAN. The camper Pi broker at 192.168.1.113 was successfully paired; MQTT over TLS port 8883 reached Connected in Node-RED. Pairing secrets are intentionally not recorded.
- Confirmed the MQTT broker is a reusable broker configuration, not a wired flow node. MQTT Input nodes select that broker configuration.
- Confirmed recurring messages arrive approximately every five seconds from `N/b827eb14d4ec/system/0/Batteries`, including after the Inject node was disconnected. No Inject/keepalive click is required for these observed recurring messages.
- Identified battery entries: 187Ah accu (battery instance 293, active battery service), Startaccu (voltage-only entry), Shunt 2 (instance 294), and a temporary USB-connected JK BMS (instance 2).
- Agreed design: one MQTT Input for `N/b827eb14d4ec/system/0/Batteries` feeds one Function node that selects Shunt 1 (293), Shunt 2 (294), and starter battery voltage by stable identity. Exclude the temporary USB JK BMS entry.
- JK BMS 1 and JK BMS 2 will instead be read directly over BLE by a separate Raspberry Pi JK-BMS monitor; they are not part of this MQTT normalization Function.
- The existing individual wildcard MQTT Input nodes for instances 293 and 294 have already been created and tested; do not recreate them. Their quoted output showed Shunt 1 voltage/current/power and time-since-full, and Shunt 2 current/power and time-since-full. The system battery overview separately showed SOC for both shunts and starter battery voltage.
- Future camper deployment is intended to retain the same MQTT Input + Function design and select the local Venus OS MQTT broker instead of the remote camper-Pi broker. Local broker configuration details remain to be verified.
- **Confirmed duplicate-message cause (2026-11-24):** MQTT Input `Camper-Pi MQTT – Testdata` subscribed to wildcard `N/+/system/0/#` using the same broker configuration as `alle accus`, which subscribed to exact topic `N/b827eb14d4ec/system/0/Batteries`. The wildcard also matched the exact battery-overview topic. Both enabled inputs caused identical payloads to appear twice with different Node-RED `msg._msgid` values. Disabling (not deleting) `Camper-Pi MQTT – Testdata` and deploying the flow restored one message approximately every five seconds. For future duplicate-output investigations, check all enabled MQTT Input nodes sharing the broker for overlapping exact/wildcard filters (`+` and `#`) before blaming the publisher. Different `_msgid` values alone do not prove duplicate publication by Venus OS.
- No Node-RED flow export was committed; no Pi files/configuration/services or firmware were changed. This note records the observed design and progress only; no production Function, JSON schema, freshness policy or release was implemented.


## v0.1.3 — TCP framing correction and bidirectional end-to-end test confirmed (2026-11-24)
- Append the required newline to every Node-RED-to-Pi TCP record in the manual test flow, including periodic JSON, manual test text, and echo responses.
- Keep the TCP connection persistent instead of allowing unterminated records to accumulate until the 8192-byte limit forces a reconnect.
- Keep the existing BLE GATT service and characteristic UUIDs and the bidirectional transport unchanged.
- Live end-to-end test confirmed: Node-RED → TCP → Pi → BLE notification → ESP32-S3, and ESP32-S3 → BLE write → Pi → TCP → Node-RED Debug.
- The Pi log showed Node-RED test telemetry (13.4 V, -2.5 A, 85% SOC; counter 52596 then 52597) forwarded to the ESP32. The user confirmed the v0.3.8 Demo screen displayed the values and increasing counter.
- The Pi received ESP32 JSON `{"source":"VictronDisplay7","type":"test","firmware":"v0.3.8","counter":49}`, logged forwarding 75 bytes to Node-RED, and the user confirmed the same message appeared in Node-RED Debug.
- This verifies the test transport on the current setup only. It is not the final production protocol and does not validate reconnect/restart recovery or SetupHelper installation/reboot acceptance.
- Raspberry Pi package version remains v0.1.3; ESP32 firmware version remains v0.3.8. Version histories are independent.

## v0.1.2 — Node-RED TCP ↔ BLE transport (initial implementation)
- Add a persistent Pi TCP client connecting to the Node-RED TCP server on port 5005.
- Forward newline-delimited UTF-8 records from Node-RED to the existing BLE TX notification characteristic.
- Forward UTF-8 writes from ESP32 BLE RX back to Node-RED over the same TCP connection.
- Retry automatically after Node-RED restarts or temporary connection loss.
- Remove the periodic fixed BLE greeting; display notifications now come from Node-RED.
- Update the manual Node-RED test flow to serialize and send its changing JSON test payload.
- This is a transport test, not the final binary display protocol or Victron command implementation.

## v0.1.1 — Active Pi BLE behavior parity
- Match the active Pi GATT server's two-second test-notification behavior: after ESP32 enables notifications, send Hallo vanaf Raspberry Pi every two seconds; stop the timer after notifications are disabled.
- Keep BLE UUIDs, advertisement name, and GATT behavior unchanged.
- No Node-RED/TCP integration is included in v0.1.1.

This changelog tracks Raspberry Pi VantourerDisplayBridge software, not ESP32 firmware.

## v0.1.0 — GitHub Pi software baseline
- Establish the first consistently versioned Raspberry Pi-side baseline.
- v0.1.x is the incremental development series; v0.2.0 is reserved for verified functional parity with the manually developed reference implementation.

## Versioning and recovery
- The root version file is the PackageManager version marker.
- Keep a version number unchanged through coding, debugging, and tests for one development step.
- Record meaningful intermediate states as Git commits.
- Create a Git tag only after the user confirms successful testing and acceptance.
- The in-development branch may expose the current version through GUI v1 PackageManager for testing.
- ESP32 firmware and Node-RED flows have independent version histories.
