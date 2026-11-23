import socket
import sys
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tcp_client import NodeRedTcpClient

class TcpClientTests(unittest.TestCase):
    def test_bidirectional_newline_framing(self):
        listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        listener.bind(("127.0.0.1",0))
        listener.listen(1)
        port=listener.getsockname()[1]
        received=[]
        accepted=threading.Event()
        response_seen=threading.Event()

        def server():
            try:
                conn,_=listener.accept()
                with conn:
                    conn.settimeout(2)
                    conn.sendall(b'{"from":"node-')
                    time.sleep(0.03)
                    conn.sendall(b'red"}\n')
                    stream=conn.makefile("rb")
                    received.append(stream.readline())
                    accepted.set()
                    response_seen.wait(1)
            finally:
                listener.close()

        thread=threading.Thread(target=server,daemon=True)
        thread.start()
        messages=[]
        client=NodeRedTcpClient("127.0.0.1",port,
            lambda message:(messages.append(message),response_seen.set()),
            reconnect_seconds=0.1)
        try:
            client.start()
            deadline=time.time()+3
            while time.time()<deadline and not messages:
                time.sleep(0.01)
            self.assertEqual(messages,[b'{"from":"node-red"}'])
            self.assertTrue(client.connected)
            self.assertTrue(client.send(b'{"from":"esp32"}'))
            self.assertTrue(accepted.wait(2))
            self.assertEqual(received,[b'{"from":"esp32"}\n'])
        finally:
            client.stop()
            listener.close()
            thread.join(timeout=2)

    def test_rejects_multiline_and_invalid_utf8(self):
        listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listener.bind(("127.0.0.1",0))
        listener.listen(1)
        port=listener.getsockname()[1]
        accepted=threading.Event()
        def server():
            conn,_=listener.accept()
            accepted.set()
            time.sleep(0.3)
            conn.close()
            listener.close()
        thread=threading.Thread(target=server,daemon=True)
        thread.start()
        client=NodeRedTcpClient("127.0.0.1",port,lambda message:None)
        try:
            client.start()
            self.assertTrue(accepted.wait(2))
            deadline=time.time()+2
            while not client.connected and time.time()<deadline:
                time.sleep(0.01)
            self.assertFalse(client.send(b"two\nlines"))
            self.assertFalse(client.send(b"\xff"))
        finally:
            client.stop()
            thread.join(timeout=2)

if __name__=="__main__":
    unittest.main()
