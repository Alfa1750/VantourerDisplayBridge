# BLE display protocol — design decisions

**Status:** Bidirectional text transport verified on the manual ESP32 firmware v0.3.6; binary display protocol design not yet finalized.  
**Scope:** Raspberry Pi VantourerDisplayBridge ↔ ESP32-S3 Waveshare 7B display.

## Transport roles

- Raspberry Pi: BLE Peripheral / GATT Server.
- ESP32-S3: BLE Central / GATT Client.
- Pi-to-ESP32 display data uses the TX GATT characteristic with notifications.
- ESP32-to-Pi commands use the RX GATT characteristic with writes.

## Verified transport milestone — ESP32 firmware v0.3.6

The earlier 20-byte notification truncation was fixed. Do not reopen this as an unresolved issue or repeat the MTU investigation without first checking this milestone and its implementation.

Test history from the conversation **“ESP IDF versie instellen” (20 November 2026)**:

1. Initially, the ESP32 received only 20 bytes of the Pi's message, e.g. `Hallo vanaf Raspberr`. This matched the default ATT MTU of 23 bytes, which leaves 20 bytes for the notification value.
2. The fix was implemented in the ESP32 BLE client in `ble_bridge.c`: explicitly start MTU exchange on connection using `ble_gattc_exchange_mtu(s_conn_handle, on_mtu_exchange, NULL);`.
3. The MTU-exchange callback `on_mtu_exchange(...)` logs the result and starts `discover_service()` only after the exchange. Service discovery was therefore moved to after MTU exchange.
4. After flashing, the ESP32 received the complete Pi message `Hallo vanaf de Raspberry Pi`. The user identified this working ESP32 firmware as **v0.3.6**.

The reverse direction had also been tested: the Pi log showed the ESP32 enabling notifications and receiving the ESP32 text `Hallo vanaf ESP32`. This demonstrates text transport in both directions between the manual implementation and ESP32.

**Evidence boundary:** These tests prove bidirectional BLE text transport and that the 20-byte truncation was resolved in firmware v0.3.6. They do not, by themselves, prove actual Victron command forwarding through Node-RED or operation of MPPT/Orion controls. The exact negotiated MTU value is not recorded here; do not invent it. This milestone is separate from the later binary-frame design below.

## Compact binary representation

The display transport should use compact binary data rather than textual numbers or JSON. Numeric measurements should normally be encoded as scaled integers, for example:

- 12.85 V → 1285 (scale ×100; decode by dividing by 100).
- 24.7 °C → 247 (scale ×10; decode by dividing by 10).
- -12.5 A → -125 (signed integer, scale ×10).

The scale, signedness, width and unit must be specified for every field in the protocol. The implementation must also define byte order (endianness), representation of unavailable/invalid values, and field validity/status. Do not assume that every field can safely use the same integer type or scale.

## Device and field identification

Use a versioned, fixed-layout packet definition shared by the Pi and ESP32 firmware. Each field's meaning is determined by its documented position and type in that version of the packet. The definition must identify the source device and measurement explicitly (for example SmartShunt 1 voltage, Orion XS input voltage, MPPT 1 battery voltage, JK-BMS 1 temperature, cabin temperature and outside temperature).

Include packet-level metadata such as protocol version and sequence number. Include sufficient validity/availability information so the display can distinguish a valid zero from a missing, stale or unavailable measurement. Device connection/data freshness must not be inferred from a measurement value.

## ATT MTU and notification size — future binary protocol design

**Design target: ATT MTU 247 bytes.** An ATT Handle Value Notification carries up to ATT_MTU − 3 bytes, so at MTU 247 the notification value can contain up to **244 bytes**.

This is a target for the future binary display frame, not a claim that 247 has already been negotiated on the live Pi/ESP32 connection or that v0.3.6 used exactly this value. Both endpoints must be configured to support/request the target and the negotiated MTU must be checked after connection. The effective value is negotiated for the connection; configuring only the Raspberry Pi is insufficient.

The ESP32-S3 and its ESP-IDF BLE stack are the intended client platform. The final effective MTU must be verified with the actual firmware and BlueZ/Pi implementation. Do not assume a 256-byte ATT MTU or infer it from a local configuration setting.

## One logical frame, possibly multiple notifications

The application should assemble all current display measurements into one logical, versioned data frame. If the complete frame fits within the negotiated notification payload, send it as one notification. If it does not fit, fragment it into multiple notifications with enough metadata to reassemble safely (for example frame sequence, fragment index and fragment count or byte offset). The ESP32 must process a frame only after receiving and validating all its fragments.

At the design target of MTU 247, the maximum notification value is 244 bytes. If a smaller MTU is negotiated, use the correspondingly smaller payload and fragmentation; do not silently truncate fields or frames.

## Remaining design work

The following are future design/implementation tasks, not prerequisites for the already-proven text transport:

- Binary, fixed-layout, versioned display data frame.
- Scaled integers for numeric measurements where appropriate.
- Explicit device/measurement mapping and validity information.
- Confirm the actual negotiated MTU on the target Pi/ESP32 setup; 247 remains the design target.
- One logical frame, with fragmentation when required by the negotiated MTU.
- Finalize exact field list, offsets, integer widths, scales, status-bit layout, byte order and fragmentation header.
