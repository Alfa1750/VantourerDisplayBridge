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


## Detailed runit service installation behavior — inspected Nov 20, 2026

The upstream v9.7 `HelperResources/ServiceResources` source was inspected in full around `installService()`, `removeService()`, and the service-directory configuration. This explains the reference Pi's observed directory layout.

### Why there are two separate directories

The helper defines:

```bash
serviceDir="/opt/victronenergy/service"
```

Its comments state that, on Venus OS versions starting with v2.90~3, `/service` is mounted as a temporary filesystem (RAM disk). The persistent service definitions live under `/opt/victronenergy/service`; Venus OS copies these into `/service` at boot. They are not symlinks.

This is consistent with the reference Pi observations:
- Both paths are ordinary directories, not symlinks.
- The active `/service/VantourerDisplayBridge` contains the runtime `supervise/` directory.
- The persistent `/opt/victronenergy/service/VantourerDisplayBridge` does not show `supervise/`.

### What SetupHelper does during a first service installation

In `installService()`, v9.7:
1. Determines the package service source directory (for this package, `services/VantourerDisplayBridge`).
2. Removes any existing persistent destination directory `/opt/victronenergy/service/VantourerDisplayBridge`.
3. Copies the package service directory to that persistent destination.
4. If the active destination `/service/VantourerDisplayBridge` does not exist, copies the package service directory there too.
5. If the service manager is running, waits up to 10 seconds for automatic startup, then starts the logger/service with `svc -u` if needed. A `down` flag prevents automatic startup.

### What SetupHelper does when the active service directory already exists

The existing-service branch does not replace the entire active directory. It compares and updates the active `log/run` and `run` files individually when their contents differ. It then starts, stops, or restarts the logger and service according to the `down` flag and current runit status.

The persistent destination is refreshed from the package source before this branch. Thus the persistent service definition and active service can be separate physical directories while the important scripts are kept in sync by SetupHelper.

### Uninstall behavior

The helper stops the active service/logger when applicable, removes the persistent service directory, removes the active service directory, and removes the service name from its installed-services tracking list. There is a special case for removing PackageManager from within itself; that exception is not relevant to this project's service.

### What the reference Pi comparison tells us

The user's read-only checks found:
- Both service paths are separate ordinary directories.
- The active and persistent `run` files compare byte-for-byte equal (`cmp` exit code 0).
- The active and persistent `log/run` files compare byte-for-byte equal (`cmp` exit code 0).

Those observations are exactly compatible with SetupHelper v9.7's design. They do not indicate a broken symlink or an accidental duplicate. The active directory is the runtime copy; the persistent directory is the boot-persistent source.

### Project implications

- Keep the canonical service definition in the package at `services/VantourerDisplayBridge/`.
- Let SetupHelper v9.7 install it using `INSTALL_SERVICES`; do not manually create symlinks between the two Venus OS service paths.
- Preserve executable permissions on `run` and `log/run` in the package/release process.
- Do not copy or vendor SetupHelper's own source into this project.
- Any future installer changes must be tested on a separate test device; the reference Pi remains read-only.
