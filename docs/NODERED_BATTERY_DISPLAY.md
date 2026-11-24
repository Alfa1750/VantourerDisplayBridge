# Node-RED battery display nodes — ESP32 v0.3.9

## Purpose

Convert the existing Venus OS battery overview MQTT message into the compact JSON contract consumed by VictronDisplay7 firmware v0.3.9. The flow uses the existing MQTT broker, MQTT input, TCP server, and active-client routing Function; it must not create duplicate brokers or TCP servers.

## Existing input and source selection

- MQTT topic: `N/b827eb14d4ec/system/0/Batteries` (use the existing portal/device topic configured in the live flow).
- MQTT updates are received from the live input without an Inject/keepalive node. Observed intervals are variable (examples ranged from about 5 to 50 seconds); the reason is not yet proven.
- SmartShunt 1 is selected by battery instance 293.
- SmartShunt 2 is selected by battery instance 294.
- Starter battery is selected by its Startaccu/Starter name; a unique Venus battery service suffix `:1` is a fallback.
- The temporary USB-connected JK BMS (instance 2) is excluded. JK BMS 1 and 2 remain the responsibility of the separate Raspberry Pi BLE monitor.

## Node chain

1. Existing MQTT Input `alle accus` on `N/<portal>/system/0/Batteries`.
2. New Function node `Normaliseer SmartShunts + startaccu` using `normalize_batteries_function.js`.
3. Existing `gebruik actieve TCP-client` Function, which routes to the connected TCP client and appends the newline.
4. Existing Node-RED TCP Server on port 5005.

The import template `flows/node-red/battery-display-v039-import.json` contains a new tab, the Function node, a Debug node and a wiring comment. It deliberately contains no MQTT broker configuration or TCP server. After importing, connect the existing MQTT Input to the new Function and connect the Function output to the existing TCP-client routing Function. Keep the Debug output connected during the first validation.

## Output contract

```json
{
  "source": "VantourerDisplay",
  "type": "battery",
  "schema": 1,
  "s1": {"v": 13.68, "i": 22.9, "p": 313.272, "soc": 82},
  "s2": {"v": 13.6, "i": 34.4, "p": 467.84, "soc": 81.4},
  "st": {"v": 12.97}
}
```

- `v`: voltage in volts.
- `i`: current in amperes.
- `p`: power in watts.
- `soc`: state of charge in percent.
- Missing measurements are JSON `null`, not zero. A measured zero remains zero.
- The ESP32 parser accepts this exact source/type/schema and field naming.

## Validation boundary

**Live test confirmed on 2026-11-24:** the user confirmed that the v0.3.9 battery JSON reached the ESP32 display with Pi bridge v0.1.4. The Pi log recorded 272–274-byte logical messages split into 20 BLE fragments. This confirms the live tested path on that setup; it does not prove compatibility with every possible Venus OS payload shape or production readiness. The complete live test tab and its wiring are documented in docs/NODERED_LIVE_TEST_FLOW.md.

## Existing flow safety

- Do not recreate the MQTT Input; it already exists.
- Do not re-enable the overlapping wildcard test input `Camper-Pi MQTT – Testdata`; it caused duplicate battery overview messages.
- Do not create another TCP server or broker configuration.
- Node-RED flows are independently maintained and are not installed by the Raspberry Pi SetupHelper package.


For the complete live test flow (including the actual MQTT/TCP settings and the two pre-existing TCP routing Functions), see [NODERED_LIVE_TEST_FLOW.md](NODERED_LIVE_TEST_FLOW.md).
