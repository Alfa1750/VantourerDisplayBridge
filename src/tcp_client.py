#!/usr/bin/env python3
"""Persistent newline-delimited TCP client for the Node-RED TCP server."""
import queue
import socket
import threading

class NodeRedTcpClient:
    def __init__(self, host, port, on_message, reconnect_seconds=3.0,
                 connect_timeout=5.0, max_line_bytes=8192):
        self.host, self.port, self.on_message = host, int(port), on_message
        self.reconnect_seconds = float(reconnect_seconds)
        self.connect_timeout = float(connect_timeout)
        self.max_line_bytes = int(max_line_bytes)
        self._stop = threading.Event()
        self._connected = threading.Event()
        self._outgoing = queue.Queue(maxsize=100)
        self._lock = threading.Lock()
        self._socket = None
        self._thread = None

    @property
    def connected(self):
        return self._connected.is_set()

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="NodeRedTcpClient", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        with self._lock:
            sock = self._socket
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def send(self, payload):
        if not isinstance(payload, bytes):
            payload = bytes(payload)
        try:
            payload.decode("utf-8")
        except UnicodeDecodeError:
            print("TCP: ESP32-bericht is geen geldige UTF-8; niet doorgestuurd", flush=True)
            return False
        if not payload or b"\n" in payload or b"\r" in payload:
            print("TCP: leeg bericht of regeleinde in BLE-bericht; niet doorgestuurd", flush=True)
            return False
        if not self.connected:
            print("TCP: Node-RED niet verbonden; ESP32-bericht niet doorgestuurd", flush=True)
            return False
        try:
            self._outgoing.put_nowait(payload)
            return True
        except queue.Full:
            print("TCP: verzendwachtrij vol; ESP32-bericht verworpen", flush=True)
            return False

    def _run(self):
        while not self._stop.is_set():
            sock = None
            try:
                sock = socket.create_connection((self.host, self.port), timeout=self.connect_timeout)
                sock.settimeout(0.25)
                with self._lock:
                    self._socket = sock
                self._connected.set()
                print("TCP: verbonden met Node-RED {}:{}".format(self.host, self.port), flush=True)
                self._serve(sock)
            except (OSError, ConnectionError, ValueError) as error:
                if not self._stop.is_set():
                    print("TCP: verbinding verbroken/fout: {}".format(error), flush=True)
            finally:
                self._connected.clear()
                with self._lock:
                    if self._socket is sock:
                        self._socket = None
                if sock is not None:
                    try:
                        sock.close()
                    except OSError:
                        pass
                self._discard_queue()
            if not self._stop.is_set():
                self._stop.wait(self.reconnect_seconds)
        print("TCP: client gestopt", flush=True)

    def _serve(self, sock):
        buffer = bytearray()
        while not self._stop.is_set():
            while True:
                try:
                    record = self._outgoing.get_nowait()
                except queue.Empty:
                    break
                sock.sendall(record + b"\n")
                print("TCP: ESP32 -> Node-RED: {} bytes".format(len(record)), flush=True)
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                continue
            if not chunk:
                raise ConnectionError("Node-RED heeft de TCP-verbinding gesloten")
            buffer.extend(chunk)
            while b"\n" in buffer:
                line, _, remainder = buffer.partition(b"\n")
                buffer = bytearray(remainder)
                if line.endswith(b"\r"):
                    line = line[:-1]
                if not line:
                    continue
                if len(line) > self.max_line_bytes:
                    raise ValueError("TCP-bericht overschrijdt de maximale regellengte")
                try:
                    self.on_message(line)
                except Exception as error:
                    print("TCP: verwerken ontvangen bericht mislukt: {}".format(error), flush=True)
            if len(buffer) > self.max_line_bytes:
                raise ValueError("TCP-bericht overschrijdt de maximale regellengte")

    def _discard_queue(self):
        # Never replay old commands or telemetry after a reconnect.
        while True:
            try:
                self._outgoing.get_nowait()
            except queue.Empty:
                return
