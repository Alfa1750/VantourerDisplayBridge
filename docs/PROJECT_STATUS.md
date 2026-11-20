# Project status and reconstruction

**Status:** Initial reconstruction from the conversation and command output. Not a verified system backup.

## Target outcome

A clean Raspberry Pi running Venus OS must be installable through SetupHelper. The installation must install/configure dependencies, Bluetooth prerequisites, the Python bridge, runit service, Node-RED integration, and required system settings. It must survive reboot and pass end-to-end tests.

## Confirmed repository/account facts

- GitHub repository: `Alfa1750/VantourerDisplayBridge`
- Visibility: private.
- Default branch: `main`.
- ChatGPT Codex Connector has been installed and granted access to this selected repository.
- Repository was empty when first inspected.

## Raspberry Pi paths observed

The following paths were returned by a BusyBox `find` command on the reference Pi:

- `/data/setupOptions/VantourerDisplayBridge`
- `/data/VantourerDisplayBridge`
- `/data/VantourerDisplayBridge/services/VantourerDisplayBridge`
- `/data/log/VictronBLE`
- `/service/VantourerDisplayBridge`

The directory `/service/VantourerDisplayBridge` contained:
- `run` (81 bytes, executable)
- `log/`
- `supervise/`

The file `/data/VantourerDisplayBridge/setup` was shown as:

```bash
#!/bin/bash

standardPromptAndActions='yes'

source "/data/SetupHelper/HelperResources/IncludeHelpers"
```

This confirms a SetupHelper-related setup entry point exists, but does not prove the full installation is complete.

The file `/data/VantourerDisplayBridge/version` was reported to contain `v0.1d`. This is the Python bridge's local version marker as observed in the conversation; do not conflate it with the ESP32 version.

## BLE implementation — reported tested

- Pi role: BLE Peripheral / GATT Server.
- ESP32 role: BLE Central / GATT Client.
- Service UUID: `8f7a0001-6d5b-4c3a-9e2f-1a0b2c3d4e5f`
- TX Pi → ESP32: `8f7a0002-6d5b-4c3a-9e2f-1a0b2c3d4e5f`
- RX ESP32 → Pi: `8f7a0003-6d5b-4c3a-9e2f-1a0b2c3d4e5f`
- BLE advertised local name: `VantourerBridge`.
- Python implementation uses D-Bus, BlueZ, and GLib.
- GATT discovery, notification subscription, and ESP32 writes were tested.
- ESP32 MTU exchange was added using `ble_gattc_exchange_mtu()`. A notification longer than the original 20-byte payload was subsequently received. The exact negotiated MTU value is not confirmed by the log evidence currently available.

The active Python source was pasted in the conversation, but the live file has not yet been captured into this repository. The pasted version includes a periodic test notification. Before treating it as production source, compare it against the actual active file and classify/remove test-only behavior deliberately.

## Service — reported running

The runit service `/service/VantourerDisplayBridge` was previously checked with `svstat` and reported `up`.

Pending inspection:
- Exact contents of `/service/VantourerDisplayBridge/run`.
- Exact contents of `/data/VantourerDisplayBridge/services/VantourerDisplayBridge`.
- How the service directory is installed/linked by SetupHelper.
- Log service configuration and active log destination.

## SetupHelper — partially observed

The setup option and project paths exist as listed above. The directory `/data/setupOptions/VantourerDisplayBridge` was listed and contained only an empty `optionsSet` file (observed Nov 20, 2026). The project root `/data/VantourerDisplayBridge` was listed and contained `ReadMe.md` (222 bytes), `services/`, `setup` (103 bytes), `src/`, and `version` (6 bytes). The recursive contents of `services/` and `src/` have not yet been captured. No claim is made that a clean installation currently works.

## Node-RED / TCP — test completed, integration pending

Reported test environment:
- Raspberry Pi 3B+ with Venus OS 3.85.
- Test Pi IP: `192.168.1.26`.
- Node-RED accessed at `https://192.168.1.26:1881`.
- `node-red-contrib-tcp-client2` installed.
- Node-RED TCP server tested on port `5005`.
- A persistent TCP connection was tested in both directions using PuTTY / `nc` and a Node-RED Function node.

This proves the Node-RED TCP test path works. It does **not** prove that the Python BLE bridge is connected to Node-RED yet.

## Bluetooth system interaction — important reported finding

During development, `vesmart-server` was stopped because it interfered with the ESP32 BLE scan/discovery. After it was stopped, the ESP32 could find and connect to the Pi GATT server. VictronConnect was reported to remain usable without `vesmart-server`.

Still unknown:
- Whether the service was only stopped or also disabled persistently.
- Whether the state survives reboot.
- Whether this is necessary on all target Venus OS versions/hardware.
- Whether a less disruptive solution exists.

Do not silently omit this finding from the SetupHelper analysis. Do not blindly disable it in an installer until the behavior and side effects are verified.

## Versions and naming

- ESP32 project: `VictronDisplay7`, version `v0.3.6` (VS Code project only).
- Python bridge version marker: `v0.1d`.
- Node-RED test flow: no version recorded.
- SetupHelper package: no release recorded.
- Repository: newly created; initial documentation baseline only.

Naming discrepancy:
- Project and service use `VantourerDisplayBridge`.
- README previously began with `VictronBLE`.
- Log path `/data/log/VictronBLE` was found.
- It is not yet known whether the old log name is still referenced by active service/configuration code.

## Temporary tests — do not ship as production behavior by default

- Periodic Pi notification: `Hallo vanaf Raspberry Pi`.
- ESP32 write test: `Hallo vanaf ESP32`.
- Node-RED Inject/Function fake telemetry (test label, counter, 13.4 V, -2.5 A, SOC 85).
- TCP echo response: `Ontvangen door Node-RED`.
- Manual `nc` and PuTTY testing.

These were test aids. They must be removed, gated, or replaced when production data handling is implemented.

## Investigated but not selected

- MQTT as the display transport was not selected.
- Alternative Node-RED BLE packages, including Epi Bluetooth, were investigated but not selected.
- Existing Python BLE GATT server remains the proven BLE foundation.

## Remaining implementation work

1. Capture the exact active Pi project and SetupHelper files.
2. Capture and review the active runit service script and log configuration.
3. Verify the `vesmart-server` state and reboot behavior.
4. Identify all runtime dependencies and OS/BlueZ assumptions.
5. Implement the persistent TCP client in the Python bridge.
6. Define and document the bidirectional message protocol.
7. Connect Node-RED messages to BLE notifications and BLE writes to Node-RED.
8. Export and document the final Node-RED flow.
9. Capture ESP32 source/version separately.
10. Implement the complete SetupHelper install/update/uninstall behavior as appropriate.
11. Test upgrade/reinstall and reboot behavior.
12. Test from a clean Pi.

## Safety

The current reference Pi is valuable and must remain untouched until a verified backup is made. Do not delete, rename, overwrite, stop, disable, install, or reconfigure anything on it as part of this repository setup.
