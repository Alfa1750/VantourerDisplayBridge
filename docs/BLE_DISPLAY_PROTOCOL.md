# BLE display protocol — design decisions

**Status:** Design direction agreed; packet layout and implementation not yet finalized or tested.  
**Scope:** Raspberry Pi VantourerDisplayBridge ↔ ESP32-S3 Waveshare 7B display.

## Transport roles

- Raspberry Pi: BLE Peripheral / GATT Server.
- ESP32-S3: BLE Central / GATT Client.
- Pi-to-ESP32 display data uses the TX GATT characteristic with notifications.
- ESP32-to-Pi commands use the RX GATT characteristic with writes.

## Compact binary representation

The display transport should use compact binary data rather than textual numbers or JSON. Numeric measurements should normally be encoded as scaled integers, for example:

- 12.85 V → 1285 (scale ×100; decode by dividing by 100).
- 24.7 °C → 247 (scale ×10; decode by dividing by 10).
- -12.5 A → -125 (signed integer, scale ×10).

The scale, signedness, width and unit must be specified for every field in the protocol. The implementation must also define byte order (endianness), representation of unavailable/invalid values, and field validity/status. Do not assume that every field can safely use the same integer type or scale.

## Device and field identification

Use a versioned, fixed-layout packet definition shared by the Pi and ESP32 firmware. Each field's meaning is determined by its documented position and type in that version of the packet. The definition must identify the source device and measurement explicitly (for example SmartShunt 1 voltage, Orion XS input voltage, MPPT 1 battery voltage, JK-BMS 1 temperature, cabin temperature and outside temperature).

Include packet-level metadata such as protocol version and sequence number. Include sufficient validity/availability information so the display can distinguish a valid zero from a missing, stale or unavailable measurement. Device connection/data freshness must not be inferred from a measurement value.

## ATT MTU and notification size

**Design target: ATT MTU 247 bytes.** An ATT Handle Value Notification carries up to ATT_MTU − 3 bytes, so at MTU 247 the notification value can contain up to **244 bytes**.

This is a target, not a claim that 247 has already been negotiated on the live Pi/ESP32 connection. Both endpoints must be configured to support/request the target and the negotiated MTU must be checked after connection. The effective value is negotiated for the connection; configuring only the Raspberry Pi is insufficient.

The ESP32-S3 and its ESP-IDF BLE stack are the intended client platform. The final effective MTU must be verified with the actual firmware and BlueZ/Pi implementation. Do not assume a 256-byte ATT MTU or infer it from a local configuration setting.

## One logical frame, possibly multiple notifications

The application should assemble all current display measurements into one logical, versioned data frame. If the complete frame fits within the negotiated notification payload, send it as one notification. If it does not fit, fragment it into multiple notifications with enough metadata to reassemble safely (for example frame sequence, fragment index and fragment count or byte offset). The ESP32 must process a frame only after receiving and validating all its fragments.

At the design target of MTU 247, the maximum notification value is 244 bytes. If a smaller MTU is negotiated, use the correspondingly smaller payload and fragmentation; do not silently truncate fields or frames.

## Status

The following are design decisions only; they are not yet implemented or verified:

- Binary, fixed-layout, versioned display data frame.
- Scaled integers for numeric measurements where appropriate.
- Explicit device/measurement mapping and validity information.
- ATT MTU 247 as the target, giving up to 244 notification-data bytes.
- One logical frame, with fragmentation when required by the negotiated MTU.

The exact field list, offsets, integer widths, scales, status-bit layout, byte order and fragmentation header must be finalized before implementation.
