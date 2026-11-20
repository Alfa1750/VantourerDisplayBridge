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

The setup option and project paths exist as listed above. The directory `/data/setupOptions/VantourerDisplayBridge` was listed and contained only an empty `optionsSet` file (observed Nov 20, 2026).

The recursive listing of `/data/VantourerDisplayBridge/services` (provided Nov 20, 2026) confirms:
- `/data/VantourerDisplayBridge/services/VantourerDisplayBridge/run` — executable, 81 bytes.
- `/data/VantourerDisplayBridge/services/VantourerDisplayBridge/log/run` — executable, 56 bytes.
- `/data/VantourerDisplayBridge/services/VantourerDisplayBridge/log/` — directory.

The exact contents were subsequently read from the Pi and copied into the repository under `pi-snapshot/services/VantourerDisplayBridge/`:

- `run` executes `python3 /data/VantourerDisplayBridge/src/gatt_server.py` and redirects stderr to stdout.
- `log/run` executes `multilog t s25000 n4 /var/log/VictronBLE`.

The original Pi listing showed both scripts as executable. GitHub's file snapshots preserve their text, but the executable permission must be set explicitly when installing/restoring them. The log script writes to `/var/log/VictronBLE`, whereas an earlier inventory found `/data/log/VictronBLE`; this path discrepancy is unresolved and must be checked before changing anything. The project root `/data/VantourerDisplayBridge` was listed and contained `ReadMe.md` (222 bytes), `services/`, `setup` (103 bytes), `src/`, and `version` (6 bytes). The recursive listing of `/data/VantourerDisplayBridge/src` (provided Nov 20, 2026) confirms:
- `gatt_server.py` — 7,367 bytes, modified Nov 20 at 11:05; this is the active source path referenced by the runit `run` script.
- `gatt_server_backup.py` — 6,912 bytes, modified Nov 20 at 10:54.
- `gatt_server_v0.3.6.py` — 7,367 bytes, modified Nov 20 at 11:05. Likely a naming/version-control mistake that reused the ESP32 firmware version `v0.3.6`; this is a user-suggested explanation, not yet verified by comparing file contents.
- `__pycache__/gatt_server.cpython-312.pyc` — compiled Python cache, 14,256 bytes.

The two 7,367-byte Python files have matching sizes and timestamps, but their contents have not yet been compared; do not assume they are identical. The backup is also not yet inspected. The active source `/data/VantourerDisplayBridge/src/gatt_server.py` was read in full from the Pi on Nov 20, 2026 and copied verbatim to `pi-snapshot/src/gatt_server.py` in GitHub. It implements the BLE GATT service/advertisement and currently sends the test notification `Hallo vanaf Raspberry Pi` every two seconds after `StartNotify`; received ESP32 writes are only printed to stdout. There is no TCP/Node-RED integration in this captured active source. The backup and `gatt_server_v0.3.6.py` have not yet been read or compared. No claim is made that a clean installation currently works.

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

During development, `vesmart-server` was stopped because it interfered with the ESP32 BLE scan/discovery. After it was stopped, the ESP32 could find and connect to the Pi GATT server. VictronConnect was reported to remain usable while `vesmart-server` was stopped.

**Clarification from the user (Nov 20, 2026):**
- On the reference Pi, `vesmart-server` was **stopped only**; it was not disabled persistently.
- Because it was not disabled, it starts again after a reboot. The BLE conflict therefore returns after reboot unless the service is stopped again.
- A persistent disable/handling mechanism still needs to be implemented and version-controlled in this project's GitHub repository, then tested. It has not yet been implemented.
- Whether this is also necessary on other Venus OS versions is unknown. The user expects that to be established only after a Venus OS update and subsequent testing.

Implementation and validation still required:
- Determine the safest supported way to keep `vesmart-server` from interfering after reboot, and implement that behavior in the project (not as an undocumented manual step).
- Verify side effects, including VictronConnect and other Venus OS functionality, before making persistent changes.
- Re-test after reboot.
- Re-evaluate behavior after a Venus OS update; do not assume the same workaround is needed on every version.

Do not silently omit this finding from the SetupHelper analysis. Do not blindly disable the service in an installer before the required behavior and side effects are validated.


### Runtime inventory from reference Pi (Nov 20, 2026)

Read-only checks on the reference Pi returned:

- Python: `Python 3.12.15`.
- `dbus`: import succeeds; module path `/usr/lib/python3.12/site-packages/dbus/__init__.py`.
- `dbus.mainloop.glib`: import succeeds.
- `gi`: import succeeds; module path `/usr/lib/python3.12/site-packages/gi/__init__.py`.
- `GLib`: import succeeds; reported GLib major/minor version `2.78`.
- `bluetoothd --version`: command was not found (`-sh: bluetoothd: command not found`). This only establishes that the command was not available under that command name/PATH; it does **not** establish that BlueZ or the Bluetooth daemon is absent.
- `/service/VantourerDisplayBridge`: reported `up`, PID 20694, uptime 27805 seconds at the time of the check.
- `/service/vesmart-server`: reported `down 30099 seconds, normally up`. This confirms it was currently down while its runit configuration says it is normally up. The user has clarified that it was manually stopped, not persistently disabled; it is expected to start again after reboot.

Still to identify: the actual BlueZ daemon executable/package/version and how it is exposed on this Venus OS image. Do not infer its absence from the failed `bluetoothd --version` command.

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


### Python source comparison (inspected Nov 20, 2026)

The user ran a byte comparison on the reference Pi between the active `src/gatt_server.py` and the two other Python files:

- `gatt_server_v0.3.6.py` is **byte-for-byte identical** to the active `gatt_server.py` (`cmp -s` returned identical). It is not a distinct implementation. Its filename should not be treated as evidence that the Python bridge has version `v0.3.6`; that version belongs to the ESP32 project.
- `gatt_server_backup.py` differs from the active file only in the test-notification additions shown by the user's `diff -u` output:
  - The active file initializes `self.notify_timer_id = None`; the backup does not.
  - The active `StartNotify()` starts a two-second GLib timer; the backup does not.
  - The active file defines `send_test_notification()`, which sends `Hallo vanaf Raspberry Pi`; the backup does not.
- No other differences appeared in the supplied unified diff. This establishes that the backup retains the same BLE structure while omitting the periodic test notification code.
- The `md5sum` command was included in the user's terminal output, but its resulting checksum lines were not included in the pasted output. No checksum values are recorded.

The active `gatt_server.py` remains the file used by the runit service and is already captured as `pi-snapshot/src/gatt_server.py`. The `v0.3.6` duplicate does not need a separate source snapshot. The backup file's complete contents have not yet been captured into GitHub; preserve it as a historical reference only if/when its exact contents are copied from the Pi. Do not substitute it for the active source without an explicit decision.

