# SetupHelper installation plan

## Objective

## Development order and scope boundary

**Priority decision (Nov 20, 2026): finish and validate SetupHelper before starting Node-RED integration work.**

Phase 1 is the complete SetupHelper package for the currently implemented Raspberry Pi BLE bridge. This phase includes the package structure, installer lifecycle, dependencies and Bluetooth prerequisites, runit service, bounded logging, safe handling of the `vesmart-server` conflict, and clean-install/update/uninstall/reboot validation on a separate test Pi.

Node-RED is deliberately outside Phase 1:
- Do not build or modify Node-RED flows during SetupHelper work.
- Do not implement the Python TCP integration yet.
- Do not make the SetupHelper installer import, overwrite, or configure Node-RED flows.
- Preserve the intended future separation: Node-RED flows will be maintained/exported separately from the SetupHelper package.
- The future Node-RED/TCP integration may require a later bridge package update, but it is not a prerequisite for validating the current BLE-only SetupHelper package.

Only after Phase 1 passes its acceptance criteria should development move to Node-RED/TCP integration.

A clean Venus OS Raspberry Pi must be installable through the project's SetupHelper option without relying on undocumented manual steps from the development Pi.

## Known installation footprint

Observed paths on the development Pi:
- `/data/setupOptions/VantourerDisplayBridge`
- `/data/VantourerDisplayBridge`
- `/data/VantourerDisplayBridge/services/VantourerDisplayBridge`
- `/service/VantourerDisplayBridge`
- `/data/log/VantourerDisplayBridge`

The project setup entry point currently shown in conversation sources SetupHelper's `IncludeHelpers`. The exact full setup option and helper calls have not yet been captured.

## Initial package scaffold created (Nov 20, 2026)

Development is taking place on the separate branch `setuphelper-package`; `main` remains unchanged by the package scaffold.

The branch now has the initial package-root layout:
- `setup` — executable SetupHelper entry point using the verified v9.7 `standardPromptAndActions='yes'` convention.
- `version` — currently `v0.1d`, matching the version marker observed on the reference Pi.
- `gitHubInfo` — provisional value `Alfa1750:setuphelper-package`.
- `src/gatt_server.py` — captured BLE GATT server with the periodic test notification code removed.
- `services/VantourerDisplayBridge/run` and `services/VantourerDisplayBridge/log/run` — service definitions using the canonical project paths and bounded multilog configuration.
- `ReadMe.md` — package scope, observed runtime prerequisites, and development limitations.

The executable mode `100755` was assigned in the Git tree to `setup`, `services/VantourerDisplayBridge/run`, and `services/VantourerDisplayBridge/log/run`.

This is only a scaffold, not a completed or tested installer. The GATT source has not yet been run after removal of the test notification code. No files have been installed on or copied to the Raspberry Pi.

## External finding: vesmart-server behavior in newer Venus OS (Nov 20, 2026)

Upstream Victron issue [#1587](https://github.com/victronenergy/venus/issues/1587) documented a keep-alive bug in older `vesmart-server` releases that could disconnect BLE devices indiscriminately. The issue discussion says the per-device behavior was changed for the v3.80 release line. Follow-up issue [#1666](https://github.com/victronenergy/venus/issues/1666) documented defects in the first 0.5.16 implementation; that follow-up was subsequently closed on Sep 14, 2026. Venus OS 3.85 was released on Oct 22, 2026.

This does **not** prove that the discovery/connection interference observed on this project's Raspberry Pi 3B+ running Venus OS 3.85 has disappeared: the exact installed `vesmart-server` package version and the precise failure mode behind the user's earlier observation have not been captured. It does, however, mean that disabling `vesmart-server` should not be treated as a default requirement based only on older reports of the 60-second mass-disconnect bug.

Current package policy remains conservative:
- Never stop, disable, patch, or replace `vesmart-server` automatically.
- Keep the installer warning informational only.
- On a separate test device, first identify the installed package version and reproduce the exact BLE discovery/connection symptom.
- Only add an optional, reversible compatibility action if testing demonstrates it is still necessary on the target Venus OS version, and document VictronConnect/VE.Smart side effects.

## Installer responsibilities to establish

The final installer must be based on inspected, tested requirements. Likely areas to verify and implement:

1. Validate supported Venus OS / architecture prerequisites.
2. Install or verify Python and required Python system modules.
3. Install or verify D-Bus, BlueZ, GLib and any Python bindings required by the active bridge.
4. Install project files into the intended data directory.
5. Install runit service files and configure log handling.
6. Enable/start service using the supported SetupHelper/Venus OS conventions.
7. Implement and test persistent handling of the `vesmart-server` BLE conflict: it was only stopped manually on the reference Pi, it restarts after reboot, and the persistent handling must be version-controlled in this repository. Verify side effects before disabling it; necessity on other Venus OS versions remains unknown until tested after an OS update.
8. Keep Node-RED flow installation/configuration outside this package; Node-RED/TCP integration is a later development phase.
9. Provide safe update/reinstall behavior.
10. Provide a documented removal/rollback strategy if supported by SetupHelper conventions.

Do not assume any of these steps are already implemented merely because the relevant path exists.

## Current blockers

- Full SetupHelper option directory and its complete on-device installation lifecycle are not yet captured.
- Full project source tree not captured.
- The service `run` and `log/run` scripts are now included in the package scaffold; runtime installation and executable-mode preservation still need validation on a separate test device.
- The active, persistent, and project-copy `log/run` scripts on the reference Pi now use `/var/log/VantourerDisplayBridge`; the log directory rename and live logging test are complete. Installer behavior still needs to reproduce this correctly on a clean test Pi.
- Runtime dependencies have only been observed on the reference Pi; compatibility checks and installer preflight behavior are not implemented.
- Safe, persistent handling of the `vesmart-server` BLE conflict remains unresolved and must be validated before release.
- Python TCP integration and Node-RED flow are intentionally deferred until the SetupHelper package for the current BLE bridge has passed its acceptance criteria.
- The GitHub repository is private, so PackageManager cannot fetch the branch through its unauthenticated GitHub URLs. A documented SD/USB archive route is now identified for the initial controlled test; this avoids making the repository public. PackageManager's later automatic GitHub downloads/updates will still be unavailable while the repository is private. See `docs/SETUPHELPER_DISTRIBUTION.md`.
- The setup entry point now retains SetupHelper's standard install/uninstall prompt and adds a preflight for Python 3, D-Bus/GLib bindings, the BlueZ system-bus name, a powered GATT/LE-advertising-capable adapter, and `multilog`. Preflight failures are marked before any service changes so an existing install is not removed. The service-install rollback path still needs runtime testing on a separate test device.

## Acceptance criteria

A release candidate is accepted only when all of the following are demonstrated on a separate clean test Pi:

- SetupHelper discovers and installs the option.
- All dependencies are installed or verified without undocumented manual intervention.
- BLE server advertises and accepts ESP32 connection.
- Notifications and writes work in both directions.
- Node-RED/TCP end-to-end behavior is explicitly not part of Phase 1 SetupHelper acceptance; it will be tested in the later integration phase.
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
