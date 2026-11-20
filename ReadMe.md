> [!CAUTION]
> **EXPERIMENTAL DEVELOPMENT — NOT WORKING / NOT READY FOR INSTALLATION**
>
> This repository contains work in progress. The SetupHelper package and BLE bridge have **not** been validated as a working, end-to-end installation. Installation, updates, reboot behavior, and live BLE operation on a clean Venus OS system are still under development and testing.
>
> **Do not install this package on a production system or rely on it for operation.** It is published publicly only so Venus OS SetupHelper can retrieve development updates during testing. The code and package may change or break without notice.

# VantourerDisplayBridge

SetupHelper package for the Raspberry Pi BLE GATT server used by the Vantourer ESP32 display.

## Scope of this package

This package currently contains the BLE-only bridge foundation:
- Raspberry Pi acts as BLE Peripheral / GATT Server.
- ESP32 acts as BLE Central / GATT Client.
- Pi-to-ESP32 notifications and ESP32-to-Pi writes use the project's custom GATT service.
- The service is managed by SetupHelper v9.7 using the package's `services/VantourerDisplayBridge/` directory.
- Logs are written to `/var/log/VantourerDisplayBridge` and rotated by multilog. The log service creates this directory with `mkdir -p` before starting multilog, so a clean installation does not depend on a manually pre-created log folder.

Node-RED flows and TCP integration are deliberately out of scope for this package phase. Node-RED flows will remain separately maintained and will not be installed or modified by SetupHelper.

## Package status

This is a development branch, not a release. The required deployment workflow is the normal GUI v1 → SetupHelper / PackageManager → Update flow. PackageManager fetches the package version from `raw.githubusercontent.com` and the source archive from `github.com/<user>/<package>/archive/<branch>.tar.gz`. These requests are unauthenticated in the inspected SetupHelper implementation. Because this repository is private, the Pi cannot currently see new GitHub versions or download updates. Do not use SD/USB archives as a development workaround. Resolve repository access before performing the first GUI update test. The `gitHubInfo` value is `Alfa1750:setuphelper-package`.

The BLE source in this package is based on the captured active reference-Pi source. The temporary periodic `Hallo vanaf Raspberry Pi` test notification has been removed. No production telemetry or TCP/Node-RED integration is implemented yet.

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
