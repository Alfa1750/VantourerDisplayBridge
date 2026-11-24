import unittest

from src.ble_framing import (
    FRAME_DATA_SIZE,
    FRAME_HEADER_SIZE,
    MAX_MESSAGE_SIZE,
    NOTIFICATION_VALUE_MAX,
    fragment_message,
)


class BleFramingTests(unittest.TestCase):
    def test_single_frame(self):
        payload = b'{"ok":true}'
        frames = fragment_message(payload, 7)
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0][:2], b"VD")
        self.assertEqual(frames[0][2:6], bytes((1, 7, 0, 1)))
        self.assertEqual(frames[0][FRAME_HEADER_SIZE:], payload)
        self.assertLessEqual(len(frames[0]), NOTIFICATION_VALUE_MAX)

    def test_multiple_frames_reassemble_in_order(self):
        payload = bytes(range(256))[:168]
        frames = fragment_message(payload, 255)
        self.assertGreater(len(frames), 1)
        self.assertTrue(all(len(frame) <= NOTIFICATION_VALUE_MAX for frame in frames))
        self.assertEqual(b"".join(frame[FRAME_HEADER_SIZE:] for frame in frames), payload)
        self.assertEqual([frame[4] for frame in frames], list(range(len(frames))))
        self.assertTrue(all(frame[5] == len(frames) for frame in frames))

    def test_maximum_message(self):
        frames = fragment_message(b"x" * MAX_MESSAGE_SIZE, 0)
        self.assertEqual(len(frames), 255)
        self.assertEqual(len(frames[-1]), NOTIFICATION_VALUE_MAX)

    def test_empty_and_oversized_messages_rejected(self):
        with self.assertRaises(ValueError):
            fragment_message(b"", 1)
        with self.assertRaises(ValueError):
            fragment_message(b"x" * (MAX_MESSAGE_SIZE + 1), 1)

    def test_payload_capacity_matches_header(self):
        self.assertEqual(FRAME_DATA_SIZE + FRAME_HEADER_SIZE, NOTIFICATION_VALUE_MAX)


if __name__ == "__main__":
    unittest.main()
