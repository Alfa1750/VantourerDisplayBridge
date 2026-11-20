# VantourerDisplayBridge

SetupHelper package for the Raspberry Pi BLE GATT server used by the Vantourer ESP32 display.

## Scope of this package

This package currently contains the BLE-only bridge foundation:
- Raspberry Pi acts as BLE Peripheral / GATT Server.
- ESP32 acts as BLE Central / GATT Client.
- Pi-to-ESP32 notifications and ESP32-to-Pi writes use the project's custom GATT service.
- The service is managed by SetupHelper v9.7 using the package's `services/VantourerDisplayBridge/` directory.
- Logs are written to `/var/log/VantourerDisplayBridge` and rotated by multilog.

Node-RED flows and TCP integration are deliberately out of scope for this package phase. Node-RED flows will remain separately maintained and will not be installed or modified by SetupHelper.

## Package status

This is a development branch, not a release. The GitHub repository is currently private, so the GX PackageManager cannot download this branch through the unauthenticated GitHub archive/raw URLs used by SetupHelper. The `gitHubInfo` value is provisional until a distribution method is agreed.

The BLE source in this package is based on the captured active reference-Pi source. The temporary periodic `Hallo vanaf Raspberry Pi` test notification has been removed. No production telemetry or TCP/Node-RED integration is implemented yet.

## Runtime prerequisites observed on the reference device

The reference Raspberry Pi was running Venus OS 3.85 and had:
- Python 3.12.15
- Python modules `dbus`, `dbus.mainloop.glib`, and `gi`
- GLib 2.78
- BlueZ 5.72 and the system D-Bus service `org.bluez`

These are observations from one development device, not yet a complete cross-version compatibility matrix. The package does not vendor or install SetupHelper, BlueZ, D-Bus, Python, or GLib.

## Installation

The setup entry point delegates the standard install/uninstall actions to the installed SetupHelper framework. SetupHelper v9.7 discovers the service under `services/` and installs it into its persistent and active runit service locations.

Do not consider this package release-ready until the installer has been tested on a separate clean Venus OS test device, including install, update/reinstall, uninstall, and reboot behavior.

## Important development notes

- Do not install or test this branch on the only working reference Pi.
- Do not disable or modify `vesmart-server` automatically until its conflict and side effects have been validated on a separate test device.
- The log rotation configuration is `multilog t s25000 n4`, approximately 100 kB retained in steady state.
- Preserve executable permissions on `setup`, `services/VantourerDisplayBridge/run`, and `services/VantourerDisplayBridge/log/run`.
