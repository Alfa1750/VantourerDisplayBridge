# Changelog

## v0.1.2 — Node-RED TCP ↔ BLE transport (in development)
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
