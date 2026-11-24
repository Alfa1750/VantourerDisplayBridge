> [!CAUTION]
> **EXPERIMENTAL DEVELOPMENT — NOT A PRODUCTION RELEASE**
>
> This repository contains work in progress. A live battery telemetry path has been confirmed on the existing development setup with ESP32 firmware v0.3.9 and Pi bridge v0.1.4. However, clean-system installation, SetupHelper install/update/uninstall acceptance, reboot behavior, and recovery testing are still incomplete.
>
> **Do not treat this package as a production release or install it on a production system.** It is published publicly so Venus OS SetupHelper can retrieve development updates during testing. The code and package may change or break without notice.

# VantourerDisplayBridge

SetupHelper package for the Raspberry Pi BLE GATT server used by the Vantourer ESP32 display.

## Scope of this package

This package contains the Raspberry Pi bridge used by the ESP32 display:
- Raspberry Pi acts as BLE Peripheral / GATT Server.
- ESP32 acts as BLE Central / GATT Client.
- Pi-to-ESP32 notifications and ESP32-to-Pi writes use the project's custom GATT service. Pi-to-ESP32 messages are application-fragmented into 20-byte notifications, so the transport does not depend on a negotiated large ATT MTU.
- A persistent TCP client connects to the existing Node-RED TCP server on port 5005 and bridges newline-delimited records to/from BLE.
- The service is managed by SetupHelper v9.7 using the package's `services/VantourerDisplayBridge/` directory.
- Logs are written to `/var/log/VantourerDisplayBridge` and rotated by multilog. The log service creates this directory with `mkdir -p` before starting multilog, so a clean installation does not depend on a manually pre-created log folder.

Node-RED flows remain separately maintained and are not installed or modified by SetupHelper. The Pi bridge package contains the TCP transport; Node-RED flow nodes are imported and wired separately. See `docs/NODERED_BATTERY_DISPLAY.md`.

## Package status

This is a development branch, not a release. The required deployment workflow is the normal GUI v1 → SetupHelper / PackageManager → Update flow. PackageManager fetches the package version from `raw.githubusercontent.com` and the source archive from `github.com/<user>/<package>/archive/<branch>.tar.gz`. These requests are unauthenticated in the inspected SetupHelper implementation. The repository is now public, so these endpoints can be accessed without GitHub authentication. Do not use SD/USB archives as a development workaround. The configured `gitHubInfo` value is `Alfa1750:setuphelper-package`.

The BLE GATT server and TCP client are project-owned source. Pi-to-ESP32 BLE notifications use the versioned `VD` application-fragment header. The current v0.3.9 development flow normalizes SmartShunt 1, SmartShunt 2 and starter battery telemetry to the ESP32 JSON contract. A live battery telemetry test has been confirmed with ESP32 firmware v0.3.9 and Pi bridge v0.1.4; see docs/NODERED_LIVE_TEST_FLOW.md and docs/PROJECT_STATUS.md. This does not establish clean-install or production acceptance.

## Runtime prerequisites observed on the reference device

The reference Raspberry Pi was running Venus OS 3.85 and had:
- Python 3.12.15
- Python modules `dbus`, `dbus.mainloop.glib`, and `gi`
- GLib 2.78
- BlueZ 5.72 and the system D-Bus service `org.bluez`

These are observations from one development device, not yet a complete cross-version compatibility matrix. The package does not vendor or install SetupHelper, BlueZ, D-Bus, Python, or GLib.

## Installation

The setup entry point uses the installed SetupHelper framework and retains its standard install/uninstall prompt. Before installing, it checks for Python 3, the D-Bus/GLib Python bindings, the BlueZ system-bus name, a powered adapter exposing GATT and LE advertising managers, and `multilog`. If a preflight check fails, it exits before changing the existing service. SetupHelper v9.7 discovers the service under `services/` and installs it into its persistent and active runit service locations.

Do not consider this package release-ready until the installer has been tested on a separate clean Venus OS test device, including install, update/reinstall, uninstall, and reboot behavior.

## Important development notes

- Do not install or test this branch on the only working reference Pi.
- The installer only warns if `vesmart-server` is running; it does not stop or disable it. Persistent handling remains unresolved until its conflict and side effects have been validated on a separate test device.
- The log rotation configuration is `multilog t s25000 n4`, approximately 100 kB retained in steady state.
- Preserve executable permissions on `setup`, `services/VantourerDisplayBridge/run`, and `services/VantourerDisplayBridge/log/run`.
