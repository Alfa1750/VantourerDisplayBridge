# Changelog

All notable project changes will be recorded here.

## Unreleased
### Design recorded (Nov 25, 2026)
- Chosen separate GitHub project for a JK-BMS monitor-only D-Bus service on Venus OS.
- Plan to selectively reuse/adapt the necessary JK-BMS communication, parsing and telemetry methods from upstream `dbus-serialbattery`, while explicitly excluding charge/discharge control and control-limit publishing.
- Recorded verification requirement: the monitor must not trigger MPPT BMS-controlled mode or otherwise control charging.
- Implementation and repository creation remain pending.


### Added
- Private GitHub repository created.
- Initial project overview, architecture, decisions, reconstructed status, test register, and SetupHelper acceptance plan.

### Not yet included
- Live Raspberry Pi source files.
- Complete SetupHelper installer.
- Active runit service files.
- Node-RED flow export.
- ESP32 source project.
- Verified system configuration and dependency inventory.

This initial repository baseline is documentation only; it is not an installable release.
