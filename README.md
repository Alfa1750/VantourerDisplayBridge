# Vantourer Display Bridge

Private project repository for the Raspberry Pi / Venus OS bridge used by the ESP32-S3 Victron display.

## Goal

Deliver a reproducible installation through Venus OS SetupHelper that can configure a clean Raspberry Pi, start the bridge automatically, and support bidirectional communication between Node-RED and the ESP32 over TCP and BLE.

**The project is not yet installation-complete.** This repository is the controlled documentation and source-code home. The current Raspberry Pi is the reference system and must not be modified destructively during the initial capture.

## Current known architecture

- Raspberry Pi: BLE Peripheral / GATT Server.
- ESP32-S3: BLE Central / GATT Client.
- Node-RED: collects Venus OS / Victron data and handles display commands.
- Python bridge: intended to connect Node-RED over TCP to the existing BLE GATT server.
- ESP32 reads JK-BMS devices directly over BLE.
- Wi-Fi is not intended as the camper display transport.

See [Architecture](docs/ARCHITECTURE.md), [Project status](docs/PROJECT_STATUS.md), and [SetupHelper plan](docs/SETUPHELPER_PLAN.md).

## Repository rules

1. Do not treat test code or test messages as production functionality.
2. Do not change the working reference Pi until a verified backup/snapshot exists.
3. Record every confirmed implementation, system change, test, and rollback point here.
4. Do not invent missing source files, settings, dependencies, or installation steps. Mark them as unknown until inspected.
5. Keep ESP32 firmware versioning separate from the Python bridge and SetupHelper.
6. A change is not complete until it is tested on the reference system and documented.
7. The project is only installation-complete after a clean-Pi SetupHelper installation, reboot test, and bidirectional end-to-end test.

## Status labels

- **Verified:** directly observed or successfully tested.
- **Reported:** stated in the project conversation but supporting files/logs still need capture.
- **Pending inspection:** not yet confirmed from the active system.
- **Not implemented:** planned, but not yet built.

## Initial repository baseline

This first commit contains project documentation only. It does **not** yet contain the live Raspberry Pi source, complete SetupHelper installer, Node-RED flow export, or ESP32 project. Those must be captured from their actual locations before being represented as implementation.
