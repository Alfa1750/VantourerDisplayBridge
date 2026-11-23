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


## v0.1.2 implementation checks

| ID | Area | Test | Result | Evidence status |
|---|---|---|---|---|
| T-008 | TCP client | Persistent Pi TCP client connects to Node-RED server on 127.0.0.1:5005 | Implemented; not yet run on Venus OS | Pending user test |
| T-009 | Node-RED → BLE | Newline-delimited JSON record is forwarded to BLE TX notification | Implemented; end-to-end test pending | Pending user test |
| T-010 | BLE → Node-RED | ESP32 RX write is forwarded as a newline-delimited TCP record | Implemented; end-to-end test pending | Pending user test |
| T-011 | TCP recovery | Client retries after Node-RED TCP server is unavailable/restarted | Implemented; automated test pending | Pending validation |

v0.1.2 remains an in-development step. No Git tag is created until the user confirms successful testing and acceptance.
