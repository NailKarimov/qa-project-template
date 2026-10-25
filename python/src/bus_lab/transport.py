"""One interface for every link: an in-memory pair, a virtual serial port, a real adapter.

Tests only know ``BUS_URL``:

- ``memory://``            — in-process socket pair (default, no tools needed)
- ``/tmp/ttyV0`` or ``/dev/ttyUSB0?baud=115200`` — a serial port, virtual (socat) or real

The same test therefore runs in the cloud on a simulator and at home on the bench.
"""

from __future__ import annotations

import socket
import time
from typing import Protocol
from urllib.parse import parse_qs, urlsplit


class Transport(Protocol):
    def write(self, data: bytes) -> None: ...

    def read(self, size: int, timeout: float) -> bytes:
        """Return exactly ``size`` bytes or raise ``TimeoutError``."""
        ...

    def reset_input(self) -> None: ...

    def close(self) -> None: ...


class SocketTransport:
    """One end of a ``socket.socketpair()``: behaves like a perfect cable."""

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock

    def write(self, data: bytes) -> None:
        self._sock.sendall(data)

    def read(self, size: int, timeout: float) -> bytes:
        deadline = time.monotonic() + timeout
        buf = b""
        while len(buf) < size:
            left = deadline - time.monotonic()
            if left <= 0:
                raise TimeoutError(f"got {len(buf)} of {size} bytes")
            self._sock.settimeout(left)
            try:
                chunk = self._sock.recv(size - len(buf))
            except TimeoutError:
                continue
            except OSError as exc:  # closed from the other side
                raise TimeoutError(str(exc)) from exc
            if not chunk:
                raise TimeoutError("link closed")
            buf += chunk
        return buf

    def reset_input(self) -> None:
        self._sock.setblocking(False)
        try:
            while self._sock.recv(4096):
                pass
        except (BlockingIOError, OSError):
            pass
        finally:
            self._sock.setblocking(True)

    def close(self) -> None:
        self._sock.close()


class SerialTransport:
    """A serial port through pyserial: a socat pseudo-terminal or a USB adapter."""

    def __init__(self, port: str, baudrate: int = 115200) -> None:
        import serial  # imported here so memory:// works without pyserial installed

        self._port = serial.Serial(port, baudrate=baudrate, timeout=0)

    def write(self, data: bytes) -> None:
        self._port.write(data)
        self._port.flush()

    def read(self, size: int, timeout: float) -> bytes:
        self._port.timeout = timeout
        data = self._port.read(size)
        if len(data) < size:
            raise TimeoutError(f"got {len(data)} of {size} bytes")
        return bytes(data)

    def reset_input(self) -> None:
        self._port.reset_input_buffer()

    def close(self) -> None:
        self._port.close()


def memory_pair() -> tuple[SocketTransport, SocketTransport]:
    a, b = socket.socketpair()
    return SocketTransport(a), SocketTransport(b)


def open_serial(url: str) -> SerialTransport:
    parts = urlsplit(url)
    baud = int(parse_qs(parts.query).get("baud", ["115200"])[0])
    return SerialTransport(parts.path, baudrate=baud)
