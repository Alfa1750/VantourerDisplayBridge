# Project status and reconstruction

**Status:** Initial reconstruction from the conversation and command output. Not a verified system backup.

## Target outcome

## Current user priority — 2026-11-24 (supersedes the Nov 20 SetupHelper-first sequence)

The user explicitly changed the immediate development priority: finish ESP32 firmware **v0.3.9**, its matching Node-RED battery telemetry nodes, and the supporting Pi BLE transport/documentation first. The earlier Nov 20 instruction to finish SetupHelper acceptance before Node-RED/TCP work is superseded for the current phase. Do not pause v0.3.9 work to return to SetupHelper. SetupHelper clean-install/update/uninstall/reboot acceptance remains a later, separate milestone.

### Current v0.3.9 implementation in progress
- ESP32 firmware branch: `VictronDisplay7/v0.3.9-battery-display`.
- Pi bridge branch: `VantourerDisplayBridge/setuphelper-package`.
- ESP32 source parses compact battery JSON and displays SmartShunt 1 (293), SmartShunt 2 (294), and starter battery voltage.
- Pi Node-RED Function emits the matching compact schema. An importable Node-RED tab provides the Function and Debug node; it must be wired to the existing MQTT Input `alle accus` and existing `gebruik actieve TCP-client` Function. Do not recreate either existing node or the TCP server.
- Pi BLE GATT TX now fragments logical messages into <=20-byte notifications; ESP32 firmware reassembles the frames before JSON parsing. This avoids reliance on the unconfirmed negotiated ATT MTU.
- Pi package marker is now v0.1.4. It is independent of ESP32 v0.3.9 and Node-RED flow versioning.

### Validation still required
- The Node-RED Function has only been exercised against synthetic fixtures. The complete raw live MQTT payload structure was not preserved; confirm the actual field shape in the existing Debug path before calling the mapping live-validated.
- No ESP-IDF build or flash has been run for v0.3.9. User controls both.
- No live Node-RED import/deploy, Raspberry Pi package update, or Pi service restart has been performed.
- No live BLE fragmentation/reassembly test has been performed.
- The SetupHelper package acceptance sequence remains pending and is not the current priority.


## Agreed development order (Nov 20, 2026)

SetupHelper is the immediate priority. Complete and validate the SetupHelper package for the current BLE-only bridge before beginning Node-RED/TCP development. During this phase, do not implement Python TCP integration or modify/import Node-RED flows. Node-RED flow files remain independently version-controlled and outside SetupHelper. Once the SetupHelper phase is accepted, proceed with Node-RED/TCP integration and update the package later if the bridge gains new runtime components.

A clean Raspberry Pi running Venus OS must be installable through SetupHelper. Phase 1 is to install/configure dependencies, Bluetooth prerequisites, the current Python BLE bridge, runit service, logging, and required system settings through SetupHelper. Node-RED/TCP integration is deliberately deferred until this SetupHelper package has passed its own clean-install, update, uninstall, and reboot acceptance tests. Node-RED flows remain separate from the installer.

## Confirmed repository/account facts

- GitHub repository: `Alfa1750/VantourerDisplayBridge`
- Visibility: public.
- Default branch: `main`.
- ChatGPT Codex Connector has been installed and granted access to this selected repository.
- Repository was empty when first inspected.

## Raspberry Pi paths observed

The following paths were returned by a BusyBox `find` command on the reference Pi:

- `/data/setupOptions/VantourerDisplayBridge`
- `/data/VantourerDisplayBridge`
- `/data/VantourerDisplayBridge/services/VantourerDisplayBridge`
- `/data/log/VantourerDisplayBridge`
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

The exact package service scripts have been captured in GitHub. The active and persistent service directories were subsequently inspected and compared:
- Both paths are separate ordinary directories, not symlinks.
- Active and persistent `run` files are byte-for-byte identical (`cmp` exit code 0).
- Active and persistent `log/run` files are byte-for-byte identical (`cmp` exit code 0).
- The active directory contains `supervise/`; the persistent directory does not.

The SetupHelper v9.7 service-management implementation has now been inspected. Its documented behavior explains this layout: `/opt/victronenergy/service` is persistent storage; Venus OS copies service definitions into the temporary `/service` filesystem at boot. SetupHelper copies package service definitions into both locations during installation and updates the active `run` and `log/run` scripts when an existing service is reinstalled. See `docs/SETUPHELPER_V9.7_REFERENCE.md` for the source-level details.

The earlier log-directory naming issue is resolved on the reference Pi. The old directory was renamed, all three log scripts were updated, and the logger was restarted and verified. The `/var/log` path is valid here because `/var/log` is a symlink to `/data/log`. See “Log directory rename completed on reference Pi” below.

## SetupHelper — partially observed

The setup option and project paths exist as listed above. The directory `/data/setupOptions/VantourerDisplayBridge` was listed and contained only an empty `optionsSet` file (observed Nov 20, 2026).

The recursive listing of `/data/VantourerDisplayBridge/services` (provided Nov 20, 2026) confirms:
- `/data/VantourerDisplayBridge/services/VantourerDisplayBridge/run` — executable, 81 bytes.
- `/data/VantourerDisplayBridge/services/VantourerDisplayBridge/log/run` — executable, 56 bytes.
- `/data/VantourerDisplayBridge/services/VantourerDisplayBridge/log/` — directory.

The exact contents were subsequently read from the Pi and copied into the repository under `pi-snapshot/services/VantourerDisplayBridge/`:

- `run` executes `python3 /data/VantourerDisplayBridge/src/gatt_server.py` and redirects stderr to stdout.
- `log/run` executes `multilog t s25000 n4 /var/log/VantourerDisplayBridge`.

The original Pi listing showed both scripts as executable. GitHub's file snapshots preserve their text, but the executable permission must be set explicitly when installing/restoring them. The log-directory rename on the reference Pi is complete: the former `/data/log/VictronBLE` directory is now `/data/log/VantourerDisplayBridge`, and all three log scripts use `/var/log/VantourerDisplayBridge`. On this system, `/var/log` is a symlink to `/data/log`, so both paths address the same directory. The project root `/data/VantourerDisplayBridge` was listed and contained `ReadMe.md` (222 bytes), `services/`, `setup` (103 bytes), `src/`, and `version` (6 bytes). The recursive listing of `/data/VantourerDisplayBridge/src` (provided Nov 20, 2026) confirms:
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
- The Bluetooth daemon is running as PID 711: `/usr/libexec/bluetooth/bluetoothd -E -f /etc/bluetoo...` (the process listing truncated the config-file argument).
- Daemon executable exists at `/usr/libexec/bluetooth/bluetoothd` (930,428 bytes; timestamp shown as Oct 22 16:48).
- `bluetoothctl` and `btmgmt` are available at `/usr/bin/bluetoothctl` and `/usr/bin/btmgmt`.
- `command -v bluetoothd` returned no path because the executable is not in the command search path under that name.
- System D-Bus lists `org.bluez`, confirming BlueZ is registered on the system bus.
- `bluetoothctl list` reports one default controller: MAC address `43:45:C0:00:1F:AC`, name `Vantourer`.
- `bluetoothctl show` reports the controller as public, powered/on, discoverable, and not pairable; alias `Vantourer`; controller name `BlueZ 5.72`.
- The controller reports both roles: `central` and `peripheral`.
- The controller's UUID list includes the project's custom service UUID `8f7a0001-6d5b-4c3a-9e2f-1a0b2c3d4e5f`, plus standard Bluetooth profiles. This is an observation from the command output; do not infer from it alone that the ESP32 is currently connected.
- Advertising capabilities: 1 active instance out of 4 supported; supports TX power, appearance, and local-name includes; maximum advertising and scan-response lengths are both 31 bytes.
- Discoverable timeout is 0 (no timeout shown); discovery scan is currently inactive (`Discovering: no`).
- BlueZ daemon version: `5.72`, obtained by running `/usr/libexec/bluetooth/bluetoothd --version`.
- Full daemon command line read from `/proc/711/cmdline`: `/usr/libexec/bluetooth/bluetoothd -E -f /etc/bluetooth/ble.conf`.
- The complete contents of `/etc/bluetooth/ble.conf` were read. Active (uncommented) settings in `[General]`:
  - `ReverseServiceDiscovery = false`
  - `Privacy = device`
  - `ControllerMode = le`
- Other displayed settings in that file are commented examples/default references, including `EnableLE` and `AttributeServer`; they are not active settings in this configuration file.
- `/service/VantourerDisplayBridge`: reported `up`, PID 20694, uptime 27805 seconds at the time of the check.
- `/service/vesmart-server`: reported `down 30099 seconds, normally up`. This confirms it was currently down while its runit configuration says it is normally up. The user has clarified that it was manually stopped, not persistently disabled; it is expected to start again after reboot.

Still to identify: the actual BlueZ daemon executable/package/version and how it is exposed on this Venus OS image. Do not infer its absence from the failed `bluetoothd --version` command.

## Versions and naming

- **Raspberry Pi VantourerDisplayBridge software in this GitHub branch: v0.1.0.** This is the first consistently versioned GitHub baseline for the Pi-side software.
- The root `version` file is the PackageManager version marker and now contains `v0.1.0`.
- Pi-side changes before this baseline were made manually without consistent versioning. The original manually developed Pi implementation is a separate functional reference; it was not ESP32 v0.3.6.
- The `pi-snapshot/version` file preserves the historical `v0.1d` marker captured from the reference Pi. It is retained as snapshot evidence and is not the current root PackageManager version.
- Pi development after v0.1.0 increments through v0.1.1, v0.1.2, v0.1.3, etc. Reserve **v0.2.0** for the milestone when the GitHub Pi implementation has reached functional parity with the manually developed Pi reference.
- ESP32 project: `VictronDisplay7`, firmware version `v0.3.6`; this is an independent version namespace.
- Node-RED test flow: no version recorded. Future Node-RED flow and JK-BMS monitor versioning remain separate.

Naming discrepancy:
- Project and service use `VantourerDisplayBridge`.
- README previously began with `VictronBLE`.
- Log path `/data/log/VantourerDisplayBridge` was found.
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

### External research: `vesmart-server` and newer Venus OS (Nov 20, 2026)

Upstream Victron issue [#1587](https://github.com/victronenergy/venus/issues/1587) documents an older keep-alive behavior that could disconnect BLE devices indiscriminately. The issue says the per-device behavior was changed for the v3.80 release line. Follow-up [#1666](https://github.com/victronenergy/venus/issues/1666) identified defects in the first 0.5.16 implementation and was closed on Sep 14, 2026. Venus OS 3.85 was released on Oct 22, 2026.

This does not establish which `vesmart-server` package version is installed on the reference Pi, nor prove that the specific BLE discovery/connection issue previously observed by the user is resolved. Do not assume the older mass-disconnect bug explains that observation. Do not automatically stop, disable, patch, or replace `vesmart-server`. First identify the installed version and reproduce the exact issue on a separate test device. Any later compatibility action must be reversible and tested for VictronConnect/VE.Smart side effects.

### Initial SetupHelper package scaffold (Nov 20, 2026)

A first package scaffold has been committed on branch `setuphelper-package` (commit `f9fecd22eabf76bc1057c694ded43b5cec56f7d2`). The `main` branch has not received these package files.

Files added at the repository root:
- `setup` — executable standard SetupHelper v9.7 entry point.
- `version` — `v0.1d`.
- `gitHubInfo` — provisional `Alfa1750:setuphelper-package`.
- `ReadMe.md`.
- `src/gatt_server.py` — based on the captured active BLE GATT source, with the periodic `Hallo vanaf Raspberry Pi` test-notification timer removed.
- `services/VantourerDisplayBridge/run`.
- `services/VantourerDisplayBridge/log/run`.

The three shell entry scripts were assigned executable Git mode `100755`. The service scripts use the observed Python source path and canonical bounded log path. The log service creates `/var/log/VantourerDisplayBridge` before launching multilog, so a fresh install does not rely on the directory having been created manually.

**Not yet accepted as a release:** v0.1.1 deliberately restores the active Pi's two-second `Hallo vanaf Raspberry Pi` notification timer. The current code has not yet passed a fresh PackageManager install and clean-test-Pi runtime test. The setup script now checks Python 3, D-Bus/GLib bindings, BlueZ D-Bus, adapter interfaces, and adapter power state, and `multilog` before changing service state; its shell syntax passed a local `bash -n` check. The `log/run` script now creates the log directory before starting multilog; both service scripts passed local `sh -n` checks. A local harness with a mocked SetupHelper include also exercised install success, preflight failure, uninstall, and PackageManager `CHECK` routing; this is a control-flow test only, not a run against the actual Venus OS helper or a Pi. A GitHub Actions workflow checks shell/Python syntax, the mocked SetupHelper control-flow scenarios (install success, preflight failure, uninstall, PackageManager `CHECK`, and interactive prompt), Python syntax, required package files, executable bits, and absence of the periodic test notification. The latest run for branch head `4b7efa9d52ed8c77e9b6beba3f5c1d0549d5252f` completed successfully; all seven substantive workflow steps passed (run `44802444028`). This is still static/mocked testing, not a live Venus OS installation. Persistent handling of the `vesmart-server` conflict is unresolved; install/update/uninstall/reboot behavior has not been tested on a clean test Pi. The required workflow is GUI v1 → SetupHelper / PackageManager → Update. Source inspection of SetupHelper v9.7 confirms unauthenticated requests to raw.githubusercontent.com for version checks and github.com archive URLs for package downloads. The repository is public, so this normal update workflow can retrieve the branch version and package archive. In-development, not-yet-tested versions are intentionally installable through PackageManager so they can be tested on the separate test Pi.

No Raspberry Pi files, services, settings, or processes were changed. No Node-RED flow or TCP integration was added.

## v0.1.1 current development state

- Package version file: `v0.1.1`.
- PackageManager branch: `setuphelper-package`, referenced by `gitHubInfo`.
- `src/gatt_server.py` includes the same periodic two-second test notification behavior as the confirmed active Pi service: timer starts on `StartNotify`, sends `Hallo vanaf Raspberry Pi`, and stops its GLib callback after notifications are disabled.
- BLE UUIDs, GATT paths, advertisement name, and runit service entry points remain unchanged.
- The static GitHub workflow was corrected to require the v0.1.1 timer and message instead of incorrectly rejecting them (that old assertion belonged to the earlier no-timer package state).
- The workflow is triggered by pushes to `setuphelper-package`. The updated workflow has been committed; its result must be checked before calling static validation passed.
- No fresh PackageManager installation, clean-test-Pi BLE test, reboot test, or uninstall/rollback test has yet been completed. Therefore v0.1.1 remains an installable development version, not an accepted release.
- No Node-RED/TCP integration is included in this step.

## Remaining implementation work

### Phase 1 — SetupHelper (do this first)

1. Capture the exact active Pi project and SetupHelper package files.
2. Complete and review the package structure, setup script, version, and gitHubInfo.
3. Identify all runtime dependencies and OS/BlueZ assumptions.
4. Verify the `vesmart-server` conflict, safe handling, side effects, and reboot behavior.
5. Implement complete SetupHelper install/update/uninstall behavior for the current BLE bridge.
6. Test upgrade/reinstall, removal/rollback, service startup after reboot, and bounded logging.
7. Validate the package on a separate clean test Pi. Do not use the only working reference Pi as the first installer test.

### Phase 2 — Node-RED/TCP (only after Phase 1 passes)

1. Implement the persistent TCP client in the Python bridge.
2. Define and document the bidirectional message protocol.
3. Connect Node-RED messages to BLE notifications and BLE writes to Node-RED.
4. Export and document the final Node-RED flow separately from SetupHelper.

### Separate work

- Capture ESP32 source/version separately.

## Safety

The reference Pi is valuable and must remain untouched during implementation comparison. A Paragon full-SD backup exists and is an approved recovery path; use it to restore the Pi/test system if required. The two specifically excluded files are only `src/gatt_server_backup.py` and `src/gatt_server_v0.3.6.py`; Paragon backups are not excluded.


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


### Active and persistent runit service locations (checked Nov 20, 2026)

The user ran read-only directory listings and a service status check on the reference Pi:

- Active runit service directory: `/service/VantourerDisplayBridge`.
  - Contains `run` (81 bytes, executable), `log/`, and `supervise/`.
- Persistent service directory: `/opt/victronenergy/service/VantourerDisplayBridge`.
  - Contains `run` (81 bytes, executable) and `log/`.
  - No `supervise/` directory was listed there.
- `svstat /service/VantourerDisplayBridge` reported `up`, PID 20694, uptime 28171 seconds at the time of this check.
- Both active and persistent directories therefore exist, and both list an executable `run` file of the same size. The output did **not** compare the contents or establish whether the active directory is a symlink or a copy of the persistent directory. Do not infer that the two `run` files are identical from equal file sizes.
- The `supervise/` directory is present in the active service directory; this is consistent with runit supervision state being maintained for the active service. Its absence from the persistent directory listing is not itself an error.
- Next verification, if needed: inspect `ls -ld` for both paths and compare the two `run` and `log/run` files with `cmp` or `md5sum`. This can be done read-only; do not modify service files or restart the service.


### BLE client discovery and pairing observations (user-reported, Nov 20, 2026)

- In the LightBlue app, the user could see the custom GATT UUIDs only after connecting to the Pi's BLE device `Vantourer` using a PIN.
- The ESP32, by contrast, was able to connect directly to `VantourerDisplayBridge` without first pairing through LightBlue.
- This records the observed behavior of those two clients. It does not establish that the GATT service or UUIDs are technically hidden until pairing; that may also depend on LightBlue's discovery/display behavior or the security configuration.
- Do not treat PIN pairing as a required prerequisite for the ESP32 connection unless later tests establish that requirement.


### Active versus persistent runit service comparison (checked Nov 20, 2026)

The user inspected both service directory types and compared the service scripts on the reference Pi:

- `ls -ld /service/VantourerDisplayBridge` reports a normal directory (`drwxr-xr-x`), not a symlink.
- `ls -ld /opt/victronenergy/service/VantourerDisplayBridge` also reports a normal directory (`drwxr-xr-x`), not a symlink.
- `cmp /service/VantourerDisplayBridge/run /opt/victronenergy/service/VantourerDisplayBridge/run` returned exit code 0: the two `run` files are byte-for-byte identical.
- `cmp /service/VantourerDisplayBridge/log/run /opt/victronenergy/service/VantourerDisplayBridge/log/run` returned exit code 0: the two `log/run` files are byte-for-byte identical.
- Thus, the active and persistent service directories are separate directories, while their `run` and `log/run` scripts are identical. The active directory also contains `supervise/`, which was not listed in the persistent directory.
- No files or service state were changed by these checks.


### SetupHelper service-copy mechanism verified (Nov 20, 2026)

The upstream SetupHelper v9.7 `ServiceResources` implementation was inspected and documented in `docs/SETUPHELPER_V9.7_REFERENCE.md`. The reference Pi's separate active/persistent service directories and matching `run` and `log/run` files are consistent with that implementation. No changes were made to the reference Pi.


### Project-owned log directory naming (Nov 20, 2026)

The previous log directory basename `VictronBLE` was an unsuitable name because it could imply an official Victron application. The project-owned name is `VantourerDisplayBridge`.

- The canonical service snapshot `pi-snapshot/services/VantourerDisplayBridge/log/run` writes to `/var/log/VantourerDisplayBridge`.
- The reference Pi has now been updated: the old log directory was renamed, and the project source, persistent service, and active service log scripts all use the new name.
- On the reference Pi, `/var/log` is a symlink to `/data/log`; the configured `/var/log/VantourerDisplayBridge` destination therefore resolves to `/data/log/VantourerDisplayBridge`.
- The ESP32 was subsequently started and the user observed new periodic `Pi -> ESP32: Hallo vanaf Raspberry Pi` records appearing in the renamed `current` log. This verifies that the new logger destination receives live records.
- Log retention is bounded by the active `multilog t s25000 n4` configuration: each current log is rotated at approximately 25,000 bytes; when rotation produces four old log files, the oldest is deleted. In steady state this leaves at most three rotated files plus `current` (approximately 100 kB total log data, subject to line-boundary overshoot).


### Log directory rename completed on reference Pi (Nov 20, 2026)

The user completed the legacy log-directory rename on the reference Pi in a controlled sequence. This section supersedes earlier statements in this document that the live Pi had not yet been changed or that the log path was still unresolved.

Verified facts from the user's terminal output:

- `/var/log` is a symbolic link to `/data/log`; both path spellings address the same underlying directory.
- The old directory `/data/log/VictronBLE` was renamed to `/data/log/VantourerDisplayBridge`. The existing multilog files were retained.
- Before editing, backups of all three log scripts were created under `/root/VantourerDisplayBridge-backup/`:
  - `run-project`
  - `run-persistent`
  - `run-active`
- The log service was stopped through its runit control FIFO with `printf d > /service/VantourerDisplayBridge/log/supervise/control`. The `sv` command was not present in the command path.
- The following three `log/run` files were updated and individually checked. All now execute `multilog t s25000 n4 /var/log/VantourerDisplayBridge`:
  - `/data/VantourerDisplayBridge/services/VantourerDisplayBridge/log/run`
  - `/opt/victronenergy/service/VantourerDisplayBridge/log/run`
  - `/service/VantourerDisplayBridge/log/run`
- The log service was restarted through its runit control FIFO with `printf u > /service/VantourerDisplayBridge/log/supervise/control`.
- BusyBox `ps` then showed PID 31388 running `multilog t s25000 n4 /var/log/VantourerDisplayBridge`.
- The renamed log directory contained the previous rotated files, `current`, `lock`, and `state`. The tail of `current` showed historical test notifications `Pi -> ESP32: Hallo vanaf Raspberry Pi` and the message `ESP32 heeft notifications uitgeschakeld`.
- Immediately after the logger restart, the `current` file was still 13,826 bytes. A subsequent ESP32 test produced a continuing stream of new `Pi -> ESP32: Hallo vanaf Raspberry Pi` lines in the renamed log, confirming that new records are appended after restart.
- An earlier process check found no running `gatt_server.py` process. Do not infer that the BLE server is currently running from the presence of old test messages in the log.

The active and persistent service scripts were not changed by this operation; only their respective `log/run` files were changed. The project snapshot in GitHub already contains the new log path. The reference Pi remains a development system; this operation does not establish clean-install or reboot acceptance.


### SetupHelper progress update (Nov 20, 2026 — evening)

- GitHub Actions warning addressed: `.github/workflows/setuphelper-static-check.yml` now uses `actions/checkout@v5` and `actions/setup-python@v6`, versions whose upstream documentation confirms Node.js 24 compatibility. The resulting workflow run `44803244365` completed successfully; every job step passed.
- SetupHelper PackageManager also supports package archives from SD/USB media, but that is not the required routine development workflow; GitHub branch updates through GUI v1 are preferred.
- The media route is documented from upstream SetupHelper guidance/source but has **not yet been tested** on Venus OS.
- The package remains development-only and has not been installed on a clean Venus OS 3.85 image. The user is preparing a clean 3.85 SD-card test image after backing up the working card.
- No Raspberry Pi or SD card was modified by this work. No Node-RED/TCP work was started.


### Required GUI v1 update workflow (Nov 20, 2026)

The user clarified that the only acceptable development/update workflow is the normal Venus OS GUI v1 route: open SetupHelper / PackageManager and select Update for VantourerDisplayBridge. Every GitHub change should be retrievable that way; repeated SD/USB archive transfers are not acceptable and must not be proposed as the development workflow.

Inspection of upstream SetupHelper v9.7 `PackageManager.py` confirms:
- Version checks use `wget` against `https://raw.githubusercontent.com/<GitHubUser>/<PackageName>/<GitHubBranch>/version`.
- Package downloads use `wget` against `https://github.com/<GitHubUser>/<PackageName>/archive/<GitHubBranch>.tar.gz`.
- The inspected code does not add GitHub authentication to either request.

The project repository is public. The GUI v1 PackageManager workflow can read the version and download the selected branch archive. The branch may intentionally contain an untested development version so the user can install and test it; acceptance and tagging happen only after successful testing.


---

## Milestone — bidirectional Node-RED ↔ Raspberry Pi ↔ ESP32 test confirmed (2026-11-24)

This update supersedes the earlier planning statements above that Node-RED/TCP integration was still deferred or pending. It records a live test performed by the user on the existing development setup; it does not claim clean-install or SetupHelper acceptance.

### Test setup and confirmed data path

- Raspberry Pi bridge package version marker: **v0.1.3** (unchanged).
- ESP32 firmware: **v0.3.8** on branch `v0.3.8-cleanup-demo`.
- Node-RED TCP server: port **5005**.
- Existing TCP framing remains newline-delimited UTF-8 records.
- Existing BLE GATT service and characteristics remain in use:
  - Service: `8f7a0001-6d5b-4c3a-9e2f-1a0b2c3d4e5f`
  - Pi TX / notify: `8f7a0002-6d5b-4c3a-9e2f-1a0b2c3d4e5f`
  - Pi RX / write: `8f7a0003-6d5b-4c3a-9e2f-1a0b2c3d4e5f`

### Pi → ESP32 direction

The user observed the Pi log receiving and forwarding the Node-RED telemetry notification:

`Pi -> ESP32: 79 bytes`

Payload:
`{"test":"VictronDisplay","teller":52596,"spanning":13.4,"stroom":-2.5,"soc":85}`

The next observed telemetry record carried counter **52597**. The user confirmed the ESP32 Demo screen displays the values and the increasing counter. Wi-Fi settings and PWM brightness controls were also confirmed working on the v0.3.8 firmware.

### ESP32 → Pi → Node-RED direction

The Pi log showed this BLE GATT write from the ESP32:

`{"source":"VictronDisplay7","type":"test","firmware":"v0.3.8","counter":49}`

The bridge then logged:

`TCP: ESP32 -> Node-RED: 75 bytes`

The user confirmed that the same JSON message appeared in the Node-RED Debug node. This confirms delivery through the TCP connection to Node-RED, not merely an attempted send recorded by the Pi.

### Result

The following complete bidirectional test path is confirmed:

1. Node-RED → TCP → Python bridge on Pi → BLE GATT notification → ESP32-S3.
2. ESP32-S3 → BLE GATT write → Python bridge on Pi → TCP → Node-RED Debug.

The transport-level integration between Node-RED, TCP, the Pi bridge, BLE, and ESP32 is therefore **verified on the current test setup**.

### Explicit limits of this milestone

- Test messages and fake telemetry are still being used; this is not the final production data/command schema.
- Production value mapping, validation, stale-data handling, and application behavior are not thereby accepted.
- BLE disconnect/reconnect and Node-RED/TCP restart recovery have not been confirmed by this milestone.
- This does not validate SetupHelper installation/update/uninstall, clean-Pi installation, or reboot behavior.
- No live Pi files, services, configuration, or Node-RED flows were changed as part of recording this documentation milestone.
- Raspberry Pi package version remains **v0.1.3**; ESP32 firmware version remains **v0.3.8**. These version histories are independent.


## Milestone — live battery telemetry test confirmed (2026-11-24, ESP32 v0.3.9 + Pi v0.1.4)

This section supersedes earlier statements in this file that live BLE fragmentation/reassembly and the v0.3.9 MQTT-to-display path were still pending. It records the user's successful test on the existing camper setup. It does not establish clean-install, SetupHelper acceptance, or production-flow acceptance.

### Exact working combination

- ESP32 display firmware: **VictronDisplay7 v0.3.9**.
- Raspberry Pi bridge package marker: **VantourerDisplayBridge v0.1.4** (the user checked /data/VantourerDisplayBridge/version).
- Pi bridge source on the development branch includes src/gatt_server.py, src/tcp_client.py and src/ble_framing.py.
- Venus OS / Node-RED environment: Venus OS 3.85; the live camper MQTT broker is reached over TLS at 192.168.1.113:8883.
- Node-RED test tab: **BLE echte data test**. The complete node configuration and wiring are recorded in docs/NODERED_LIVE_TEST_FLOW.md. The actual live Node-RED flow remains independently maintained on the Pi and is not installed by this package.
- The user verified the Pi package marker as v0.1.4, confirmed the running bridge service, and observed Pi log entries showing 272–274-byte battery JSON messages split into 20 BLE fragments per logical message.
- The ESP32 showed the received battery data on its display. This confirms the live battery telemetry path on this setup:
  Venus OS MQTT → Node-RED normalization Function → Node-RED TCP server → Pi TCP client → Pi BLE GATT notifications (application fragments) → ESP32 v0.3.9 reassembly/parser/display.

### Flow and data contract

- MQTT Input node: alle accus, topic N/b827eb14d4ec/system/0/Batteries, QoS 2, auto-detect, broker 192.168.1.113:8883 with TLS configuration Victron TLS.
- The input feeds the normalization Function and a separate raw MQTT Debug node (the raw Debug node is present but disabled in the supplied export).
- Normalization selects SmartShunt instances **293** and **294**, plus the starter battery by name (unique service-instance :1 fallback). The temporary USB-connected JK BMS instance **2** is excluded.
- Output JSON contract: source=VantourerDisplay, type=battery, schema=1; s1 and s2 each contain v/i/p/soc; st contains v. Missing measurements are null; measured zero remains zero.
- The normalized output branches to the active JSON Debug node v0.3.9 batterij JSON and to gebruik actieve TCP-client. The routing Function sends the JSON as UTF-8 with a trailing newline to the TCP server's active client.
- TCP server: port 5005, stream mode, UTF-8, newline delimiter LF, keep-alive timeout 6000 ms, application socket timeout 60000 ms.
- Full node-by-node configuration and both existing TCP routing Functions are in docs/NODERED_LIVE_TEST_FLOW.md.

### Observations and limits

- The Pi log showed logical messages of 272–274 bytes, each split into 20 BLE notifications; the ESP32 displayed the resulting battery data. BLE fragmentation and display reception are therefore live-tested for these messages.
- TCP connections were observed to close and reconnect at times. Re-deploying the Node-RED flow restored operation. This test does not prove the cause of those TCP disconnects.
- Raw MQTT Debug output and normalized JSON Debug output showed matching message timestamps in the user's test. The irregular intervals were already present at the MQTT Input output; the normalization Function was not dropping those messages in that observation.
- Message intervals varied (including approximately 5, 10, 20, 35 and 50 seconds). The camper was charging from solar and other charging sources; changing measured values are a plausible explanation, but the publication trigger/interval behavior has **not** been proven.
- Do not attribute the irregular intervals to Pi bridge v0.1.4 without further evidence.
- This milestone does not validate every possible MQTT payload shape, reconnect/restart recovery, SetupHelper clean installation, uninstall, reboot behavior, or the final production Node-RED flow.
- The user controls all live-system changes. No Node-RED flow, Pi configuration, service, firmware, build or flash was changed as part of this documentation update.
