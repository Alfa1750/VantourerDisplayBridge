# SetupHelper installation plan

## Objective

A clean Venus OS Raspberry Pi must be installable through the project's SetupHelper option without relying on undocumented manual steps from the development Pi.

## Known installation footprint

Observed paths on the development Pi:
- `/data/setupOptions/VantourerDisplayBridge`
- `/data/VantourerDisplayBridge`
- `/data/VantourerDisplayBridge/services/VantourerDisplayBridge`
- `/service/VantourerDisplayBridge`
- `/data/log/VictronBLE`

The project setup entry point currently shown in conversation sources SetupHelper's `IncludeHelpers`. The exact full setup option and helper calls have not yet been captured.

## Installer responsibilities to establish

The final installer must be based on inspected, tested requirements. Likely areas to verify and implement:

1. Validate supported Venus OS / architecture prerequisites.
2. Install or verify Python and required Python system modules.
3. Install or verify D-Bus, BlueZ, GLib and any Python bindings required by the active bridge.
4. Install project files into the intended data directory.
5. Install runit service files and configure log handling.
6. Enable/start service using the supported SetupHelper/Venus OS conventions.
7. Implement and test persistent handling of the `vesmart-server` BLE conflict: it was only stopped manually on the reference Pi, it restarts after reboot, and the persistent handling must be version-controlled in this repository. Verify side effects before disabling it; necessity on other Venus OS versions remains unknown until tested after an OS update.
8. Configure Node-RED TCP endpoint/port and document matching flow setup.
9. Provide safe update/reinstall behavior.
10. Provide a documented removal/rollback strategy if supported by SetupHelper conventions.

Do not assume any of these steps are already implemented merely because the relevant path exists.

## Current blockers

- Full SetupHelper option directory not captured.
- Full project source tree not captured.
- Full service directory not captured.
- Active runit `run` script not captured.
- Runtime dependencies not inventoried.
- Bluetooth and `vesmart-server` state not fully documented.
- Python TCP integration not implemented.
- Final Node-RED flow not available in repository.

## Acceptance criteria

A release candidate is accepted only when all of the following are demonstrated on a separate clean test Pi:

- SetupHelper discovers and installs the option.
- All dependencies are installed or verified without undocumented manual intervention.
- BLE server advertises and accepts ESP32 connection.
- Notifications and writes work in both directions.
- Node-RED and Python maintain the intended TCP connection.
- Node-RED data reaches ESP32 and ESP32 data reaches Node-RED.
- The service starts automatically after reboot.
- The `vesmart-server` handling is validated and does not cause unacceptable loss of functionality.
- Re-running the installer/update process does not damage the installation.
- Logs and diagnostics are usable for troubleshooting.

## Safety rules

- Never test installer changes first on the only working reference Pi.
- Back up the complete current project and service state before any modification.
- Do not stop/disable system services as part of an installer until the behavior has been tested and justified.
- Do not copy temporary test code into production by accident.


## External SetupHelper reference (not a project dependency)

The authoritative framework reference is the public upstream repository:
- https://github.com/kwindrem/SetupHelper
- Package development guide: https://github.com/kwindrem/SetupHelper/blob/main/PackageDevelopmentGuidelines.md

We will consult this repository and its documentation only to implement a compatible VantourerDisplayBridge package. We will **not** copy SetupHelper source files into this repository, vendor the framework, or make it part of the bridge's install payload. SetupHelper remains an existing Venus OS package installed separately on the device.

Relevant documented conventions in the upstream v6.0 package guide:
- A PackageManager package has a version file and an executable setup script; it should also have gitHubInfo containing the GitHub user and default branch.
- The setup script sources /data/SetupHelper/HelperResources/IncludeHelpers.
- Setting standardPromptAndActions='yes' before sourcing IncludeHelpers delegates the standard install/uninstall actions to SetupHelper.
- From SetupHelper v6.0, service directories under the package's services/ directory are automatically installed and tracked for uninstall; the service directory name determines the runit service name.
- The setup script is expected to support safe install/uninstall/reinstall behavior and use SetupHelper's completion/exit handling.

Important compatibility check still required on the reference Pi: inspect the installed SetupHelper version, gitHubInfo, and relevant local files before relying on the current upstream main documentation. The local package layout strongly resembles the v6+ service-directory convention, but the installed framework version has not yet been confirmed.

The goal is not to reproduce SetupHelper. The goal is to make this project's own package conform to the installed framework's supported package interface.
