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


### Fixed — GUI v1 white screen on test Pi (Nov 25, 2026)
- On the test Raspberry Pi running Venus OS 3.85, replaced `import QtQuick 1.1` with `import QtQuick 2` in six battery-related QML files: PageBattery, PageBatteryCellVoltages, PageBatteryParameters, PageBatterySettings, PageBatterySetup, and PageLynxIonIo.
- Created per-file rollback copies using the suffix `.before-qtquick-fix`.
- Restarted `/service/gui`; user confirmed GUI v1 returned and displayed normally.
- Documented as a verified test-Pi fix to repeat only after checking the camper Pi's version and files. Camper Pi remains unmodified.


### Documented — clean test-Pi baseline procedure (Nov 26, 2026)
- Added the verified sequence for uninstalling dbus-serialbattery, rebooting, checking removal, and correcting the GUI v1 QtQuick imports if needed.
- The procedure retains overlay-fs and includes only the commands used and confirmed in this cleanup.
