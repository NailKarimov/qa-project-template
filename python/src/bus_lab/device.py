"""A simulated device: the system under test of the example.

Rules (each is checked by a test and broken by a mutant in ``scripts/mutants.py``):

1. It answers only frames sent to its own address, with the same payload (echo).
2. A broadcast (address 0) is executed but never answered.
3. A frame with a wrong CRC is ignored: silence, and the error counter goes up.
4. A length byte above the maximum is a framing error: the input is flushed.
"""

from __future__ import annotations

import threading

from bus_lab.frame import BROADCAST, HEADER, Frame, FrameError, decode, encode, frame_length
from bus_lab.transport import Transport


class EchoDevice:
    def __init__(self, transport: Transport, address: int) -> None:
        self.transport = transport
        self.address = address
        self.crc_errors = 0
        self.framing_errors = 0
        self.broadcasts = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> EchoDevice:
        self._thread.start()
        return self

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=2)

    def handle(self, raw: bytes) -> bytes | None:
        """Process one complete frame and return the reply, if any."""
        try:
            frame = decode(raw)
        except FrameError:
            self.crc_errors += 1
            return None
        if frame.address == BROADCAST:
            self.broadcasts += 1
            return None
        if frame.address != self.address:
            return None
        return encode(Frame(self.address, frame.payload))

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                header = self.transport.read(HEADER, timeout=0.1)
            except TimeoutError:
                continue
            try:
                total = frame_length(header)
            except FrameError:
                self.framing_errors += 1
                self.transport.reset_input()
                continue
            try:
                rest = self.transport.read(total - HEADER, timeout=0.5)
            except TimeoutError:
                self.framing_errors += 1
                continue
            reply = self.handle(header + rest)
            if reply is not None:
                self.transport.write(reply)
