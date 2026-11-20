# SetupHelper v9.7 reference findings

**Checked:** 2026-11-20  
**Reference device:** Raspberry Pi running Venus OS  
**Installed SetupHelper version:** `v9.7` (read from `/data/SetupHelper/version`)  
**Upstream repository:** https://github.com/kwindrem/SetupHelper

## Scope

SetupHelper is an independently installed Venus OS package. It is consulted only as an external compatibility reference for the VantourerDisplayBridge installer. No SetupHelper source files are to be copied, vendored, or included in the VantourerDisplayBridge repository or installation payload.

## Version and documentation status

The reference Pi reports SetupHelper `v9.7`. The upstream `main` branch version file also reports `v9.7`.

The upstream `PackageDevelopmentGuidelines.md` is explicitly marked **"updated for v6.0"**. The same marker is present in the copy read from the Pi. The guide is therefore older than the installed framework version; use it as background, but verify implementation details against the actual v9.7 helper scripts.

## v9.7 implementation checked on upstream main

The following upstream files were inspected:

- `HelperResources/IncludeHelpers`
- `HelperResources/EssentialResources`
- `HelperResources/ServiceResources`
- `HelperResources/DbusSettingsResources`
- `HelperResources/CommonResources`

Relevant verified behavior:

1. `IncludeHelpers` sources `EssentialResources`, `ServiceResources`, `DbusSettingsResources`, and then `CommonResources`.
2. `standardPromptAndActions='yes'` is checked by `CommonResources`. If set, SetupHelper presents its standard action prompt when needed and calls `endScript 'INSTALL_FILES' 'INSTALL_SERVICES' 'ADD_DBUS_SETTINGS'`.
3. The actual v9.7 `endScript` implementation recognizes the exact tokens `INSTALL_FILES`, `INSTALL_SERVICES` (plural), and `ADD_DBUS_SETTINGS`.
4. `installAllServices` discovers service directories directly under the package's `services/` directory and calls `installService` for each one.
5. `installService` installs service contents into the persistent `/opt/victronenergy/service` location and the active `/service` location, subject to the framework's service-state logic.
6. During uninstall, `endScript` calls `uninstallAllFiles` and `uninstallAllServices`; installed service names are tracked for removal.
7. `endScript` records the installed package version from the package's `version` file after a successful install.

## Documentation discrepancy

The guide's example at the `endScript` section uses `INSTALL_SERVICE` (singular). The v9.7 implementation's case statement recognizes `INSTALL_SERVICES` (plural). For this project, do not copy the singular example; if explicitly calling `endScript`, use the token supported by the inspected v9.7 implementation.

## Consequence for VantourerDisplayBridge

- Build only our own package files and installer.
- Use the installed SetupHelper v9.7 interface; do not assume the v6.0 guide is fully current.
- Keep the package's service under its own `services/<service-name>/` directory if using SetupHelper's automatic service installation.
- Before designing or changing the installer, inspect the complete current `/data/VantourerDisplayBridge` package on the reference Pi, including `setup`, `version`, `gitHubInfo`, README, source, and service scripts.
- Do not modify the reference Pi during this inspection.
- Do not claim the installer is complete until a separate clean test Pi has passed installation, reboot, and end-to-end tests.

## Sources

- https://github.com/kwindrem/SetupHelper/blob/main/version
- https://github.com/kwindrem/SetupHelper/blob/main/PackageDevelopmentGuidelines.md
- https://github.com/kwindrem/SetupHelper/blob/main/HelperResources/IncludeHelpers
- https://github.com/kwindrem/SetupHelper/blob/main/HelperResources/EssentialResources
- https://github.com/kwindrem/SetupHelper/blob/main/HelperResources/ServiceResources
- https://github.com/kwindrem/SetupHelper/blob/main/HelperResources/DbusSettingsResources
- https://github.com/kwindrem/SetupHelper/blob/main/HelperResources/CommonResources
