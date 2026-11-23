# Node-RED ↔ Raspberry Pi TCP protocol (v0.1.3)

## Connection roles
- Node-RED hosts the TCP server on port 5005.
- The Raspberry Pi bridge is the persistent TCP client.
- Default destination: 127.0.0.1:5005 (both processes run on Venus OS).
- The bridge retries every 3 seconds after a failure.
- Optional environment variables: VDB_NODE_RED_HOST (127.0.0.1), VDB_NODE_RED_PORT (5005), VDB_TCP_RECONNECT_SECONDS (3).

## Framing and payload
This step uses UTF-8 text records separated by newline. TCP packet boundaries are not message boundaries; partial reads are buffered and multiple records in one read are split.

The Pi does not parse payloads. A Node-RED record is forwarded unchanged as one BLE TX notification. An ESP32 RX write is forwarded as one newline-terminated TCP record.

The test flow serializes its JavaScript object with JSON.stringify(msg.payload) and appends exactly one newline before writing to the TCP server. This is a transport test, not the final binary display-frame protocol.

Current boundaries:
- UTF-8 text only.
- Empty TCP records are ignored.
- ESP32-to-Node-RED messages containing CR/LF or invalid UTF-8 are rejected.
- Maximum TCP record size: 8192 bytes.
- No BLE fragmentation is implemented. Payloads must fit the effective negotiated notification size; do not assume the design target MTU 247 until verified live.
- If BLE notifications are not enabled, incoming Node-RED records are logged and skipped, not queued.

## Node-RED to ESP32
1. Node-RED TCP server accepts the Pi bridge.
2. Node-RED sends one newline-delimited record.
3. Pi extracts the line and schedules it on the GLib main loop.
4. Existing BLE TX characteristic sends it as a notification.

## ESP32 to Node-RED
1. ESP32 writes UTF-8 text to the existing BLE RX characteristic.
2. Pi queues the record for the TCP connection and appends newline.
3. Node-RED receives it and can reply to the same client using msg.topic.

## Test flow
Import flows/node-red/ble-test-flow.json manually. It opens the TCP server on port 5005 and sends changing JSON test data once per second to the active TCP client. The shared write function appends the required newline to periodic test data and manual text; the echo path does the same. This prevents the Pi's newline-framed TCP receiver from accumulating data until its maximum record size is exceeded. It retains a manual text inject and the Node-RED echo response. PackageManager installs Pi software only; it does not import Node-RED flows.

## Reliability
- TCP reconnect is automatic.
- Queued records are discarded on disconnect; old commands are never replayed.
- Outgoing queue is limited to 100 records.
- This step does not implement binary frames, fragmentation/reassembly, acknowledgements, command schemas, or Victron device-control logic.
