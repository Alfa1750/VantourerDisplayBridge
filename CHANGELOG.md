# Changelog

## v0.1.1 — Active Pi BLE behavior parity

- Match the active Raspberry Pi GATT server's two-second test-notification behavior: after the ESP32 enables notifications, send `Hallo vanaf Raspberry Pi` every two seconds; stop the timer callback after notifications are disabled.
- Keep the existing BLE service UUIDs, characteristic UUIDs, advertisement name, and GATT behavior unchanged.
- This step does not add or claim Node-RED/TCP integration. The TCP test flow remains separate from the active Pi GATT server.
- This is an in-progress parity step, not the v0.2.0 functional-parity milestone.

This changelog tracks the **Raspberry Pi VantourerDisplayBridge software** in this repository. It does not track ESP32 firmware versions.

## v0.1.0 — GitHub Pi software baseline

- Establish the current Raspberry Pi-side software state represented in this GitHub branch as the first consistently versioned baseline.
- This is a repository/Pi-software baseline, not a claim that the SetupHelper package has reached functional parity with the manually developed Pi implementation.
- Subsequent Pi-side development increments the patch version: v0.1.1, v0.1.2, v0.1.3, and so on.
- When the GitHub Pi implementation has reached functional parity with the manually developed reference implementation, mark that milestone as v0.2.0.

## Versioning rules

- The root version file is the PackageManager version marker for the Raspberry Pi software.
- Pi software development before this baseline was performed through manual changes without a consistent versioning scheme. Do not retroactively assign those changes ESP32 version numbers.
- v0.1.x is the development series leading toward functional parity with the manual Pi implementation.
- v0.2.0 is reserved for the verified functional-parity milestone.
- ESP32 firmware has its own independent version numbering. ESP32 firmware v0.3.6 is unrelated to Pi software v0.1.0.
- Node-RED flows and future JK-BMS monitor software have their own independent version histories.

## Development and recovery-point rules

- A new distinct Pi development step receives its version number when that step begins.
- Keep that version number unchanged during all edits, debugging and repeated tests within the same step. Do not create a new version for every test or code correction.
- Record meaningful intermediate changes with Git commits.
- When a step is successfully tested and accepted, create a Git tag for that version. The tag is a known-good recovery point.
- Increment to the next patch version only when beginning the next distinct development step.
- The PackageManager branch may contain the current in-development, not-yet-tested version so it can be installed through GUI v1 and tested on the separate test Pi. Do not wait for acceptance before making a development step installable. Create a Git tag only after the user confirms successful testing and acceptance; the tag marks a known-good recovery point.
