# SetupHelper package distribution for testing

## Current constraint

The `VantourerDisplayBridge` GitHub repository is private. SetupHelper PackageManager's normal GitHub version/download requests use unauthenticated GitHub archive/raw URLs, so PackageManager on the GX device cannot fetch this private branch directly.

Do not make the repository public just to work around this. A documented SetupHelper alternative is to transfer a package archive from removable SD/USB media.

## Supported removable-media convention

The upstream SetupHelper PackageManager documentation and source describe these archive names:

- `<packageName>-<gitHubBranch-or-version>.tar.gz`
- `<packageName>-install.tar.gz`

For this project branch, the test archive filename is:

```text
VantourerDisplayBridge-setuphelper-package.tar.gz
```

The upstream package-development guide says to download the `.tar.gz` archive for the selected GitHub branch/tag, not the ZIP archive, copy it unchanged to SD/USB media, and insert the media. Do not unpack it manually.

PackageManager transfers and unpacks the archive into `/data/VantourerDisplayBridge`. For a new package, it can add the package to its package list. The package's `gitHubInfo` file is read when the package is first added; if a package with that name is already registered, the file is ignored.

The current package contains:

```text
gitHubInfo
Alfa1750:setuphelper-package
```

## Controlled test procedure (not yet executed)

1. Keep the repository private.
2. While signed in to GitHub with access to the repository, download the source archive for branch `setuphelper-package` as a `.tar.gz` file.
3. Rename the downloaded archive to exactly `VantourerDisplayBridge-setuphelper-package.tar.gz`.
4. Copy that archive unchanged to SD/USB media.
5. On the clean Venus OS 3.85 test installation, insert the media and allow PackageManager to detect and transfer the archive.
6. Confirm the package appears in PackageManager and its stored version is `v0.1d`.
7. Perform the installation manually from PackageManager. Do not add `AUTO_INSTALL_PACKAGES`, `AUTO_INSTALL`, or `ONE_TIME_INSTALL` trigger files for this first controlled test.
8. Verify install, service state, logs, BLE behavior, uninstall, and reboot behavior according to the acceptance checklist.

Do not treat this procedure as validated until it has been run successfully on the clean test image. Do not perform it on the original working SD card.

## Important limitation

This removable-media method bypasses PackageManager's need to download the private branch for the initial package transfer. It does **not** make private GitHub downloads or automatic updates work afterward. If the package remains registered with `Alfa1750:setuphelper-package`, PackageManager's later GitHub version checks/downloads will still fail while the repository is private. A future update can be transferred with a new SD/USB archive, or a different authenticated/public distribution strategy can be considered later with explicit approval.

## Upstream references

- [SetupHelper Package Development Guidelines](https://github.com/kwindrem/SetupHelper/blob/main/PackageDevelopmentGuidelines.md) — removable-media package archive instructions and package naming.
- [SetupHelper PackageManager.py](https://github.com/kwindrem/SetupHelper/blob/main/PackageManager.py) — archive naming, media scan, package registration, and `gitHubInfo` handling (see comments around the removable-media and package-add sections).

SetupHelper remains an external framework. No SetupHelper source is copied into this project.
