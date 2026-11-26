# Test log and evidence register

This file distinguishes reported test outcomes from tests still needing reproducible evidence.

## Reported successful tests

| ID | Area | Test | Result | Evidence status |
|---|---|---|---|---|
| T-001 | BLE discovery | ESP32 scans and finds Pi advertising `VantourerBridge` after stopping `vesmart-server` | Passed | Reported in conversation; capture logs/config |
| T-002 | GATT | ESP32 discovers service and characteristics | Passed | Reported; ESP32 log previously showed GATT OK |
| T-003 | BLE Notify | ESP32 enables notifications | Passed | Reported; Pi log showed notification subscription |
| T-004 | BLE Write | ESP32 writes test data to Pi RX characteristic | Passed | Reported; Pi logged received bytes |
| T-005 | BLE payload | Longer Pi notification received after ESP32 MTU exchange change | Passed | Reported; exact negotiated MTU not captured |
| T-006 | Node-RED TCP | Persistent TCP client sends data to Node-RED | Passed | Reported; PuTTY/`nc` and Debug |
| T-007 | TCP reverse | Node-RED writes a response to the same connected TCP client | Passed | Reported; client received echo response |

## Test-only behavior observed

- Pi periodically sent `Hallo vanaf Raspberry Pi`.
- ESP32 sent `Hallo vanaf ESP32`.
- Node-RED generated synthetic test values: voltage 13.4, current -2.5, SOC 85, plus a counter.
- Node-RED Function echoed `Ontvangen door Node-RED`.
- Manual PuTTY and `nc` sessions were used.

These are not final end-to-end application tests.

## Required tests before release

| ID | Area | Required test | Status |
|---|---|---|---|
| R-001 | TCP ↔ Python | Python bridge connects persistently to Node-RED TCP server | Not implemented |
| R-002 | Node-RED → ESP32 | Test JSON/value payload passes Node-RED → TCP → Python → BLE notification → ESP32 | Not implemented |
| R-003 | ESP32 → Node-RED | ESP32 write passes BLE → Python → TCP → Node-RED flow | Not implemented |
| R-004 | Reconnect | TCP reconnect after Node-RED restart | Not tested |
| R-005 | Reconnect | BLE reconnect after ESP32/Pi disconnect | Not fully documented |
| R-006 | Service | Python bridge starts after reboot | Pending verification |
| R-007 | System dependency | `vesmart-server` workaround survives reboot and has acceptable side effects | Pending verification |
| R-008 | SetupHelper | Install on clean Pi | Not tested |
| R-009 | SetupHelper | Re-run/update behavior is safe and idempotent | Not tested |
| R-010 | End-to-end | Full bidirectional system works after clean install and reboot | Not tested |

## Evidence capture policy

When a test is repeated, record:
- Date and Venus OS version.
- Hardware and connection roles.
- Exact command/configuration used.
- Relevant unedited log output.
- Expected and actual result.
- Whether it is a development-only test or production acceptance test.


## T-008 — Clean baseline after dbus-serialbattery removal and GUI correction (Nov 26, 2026)

- Restored a backup of the test Pi with neither VantourerDisplayBridge nor JK-BMS-Monitor installed.
- Ran the dbus-serialbattery uninstall script; selected removal of installation/configuration/logs and retained overlay-fs.
- Rebooted the Pi.
- Confirmed `/data/apps/` contained only `overlay-fs`; `dbus -y` showed no dbus-serialbattery service; matching service directories and serial-starter configuration were absent.
- Applied the documented QtQuick import correction in the six GUI v1 QML files under `/opt/victronenergy/gui/qml` and restarted `/service/gui`. User confirmed GUI v1 returned and worked.
- Result: clean baseline for JK-BMS-Monitor 0.2.0 testing, with overlay-fs retained.
