"""Small, MTU-independent application framing for Pi-to-ESP32 BLE notifications."""

FRAME_MAGIC = b"VD"
FRAME_VERSION = 1
NOTIFICATION_VALUE_MAX = 20
FRAME_HEADER_SIZE = 6
FRAME_DATA_SIZE = NOTIFICATION_VALUE_MAX - FRAME_HEADER_SIZE
MAX_MESSAGE_SIZE = FRAME_DATA_SIZE * 255


def fragment_message(data, message_id):
    """Split one byte message into ordered frames, each no larger than 20 bytes.

    Frame layout: magic[2], version[1], message_id[1], index[1], count[1], data[0..14].
    """
    data = bytes(data)
    if not data:
        raise ValueError("BLE message must not be empty")
    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError("BLE message exceeds the framing limit of {} bytes".format(
            MAX_MESSAGE_SIZE))
    if not 0 <= int(message_id) <= 255:
        raise ValueError("message_id must fit in one byte")

    count = (len(data) + FRAME_DATA_SIZE - 1) // FRAME_DATA_SIZE
    frames = []
    for index in range(count):
        start = index * FRAME_DATA_SIZE
        payload = data[start:start + FRAME_DATA_SIZE]
        frames.append(FRAME_MAGIC + bytes((FRAME_VERSION, int(message_id), index, count)) + payload)
    return frames
