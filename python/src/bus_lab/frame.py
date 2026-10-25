"""Example frame format: ``[address][length][payload...][crc low][crc high]``.

It is deliberately small, so the template shows the testing approach rather than a protocol.
Replace it with the real protocol of your project (pymodbus, python-can, ocpp, ...).
"""

from dataclasses import dataclass

from bus_lab.crc import crc_bytes

BROADCAST = 0x00
MAX_PAYLOAD = 32
HEADER = 2  # address + length
TRAILER = 2  # CRC


class FrameError(ValueError):
    """The bytes are not a valid frame."""


@dataclass(frozen=True)
class Frame:
    address: int
    payload: bytes

    def __post_init__(self) -> None:
        if not 0 <= self.address <= 0xFF:
            raise FrameError(f"address {self.address} is outside 0..255")
        if len(self.payload) > MAX_PAYLOAD:
            raise FrameError(f"payload of {len(self.payload)} bytes is longer than {MAX_PAYLOAD}")


def encode(frame: Frame) -> bytes:
    body = bytes([frame.address, len(frame.payload)]) + frame.payload
    return body + crc_bytes(body)


def frame_length(header: bytes) -> int:
    """Total frame length, known once the two header bytes have arrived."""
    if len(header) < HEADER:
        raise FrameError("need the address and length bytes first")
    length = header[1]
    if length > MAX_PAYLOAD:
        raise FrameError(f"length byte {length} is larger than {MAX_PAYLOAD}")
    return HEADER + length + TRAILER


def decode(raw: bytes) -> Frame:
    if len(raw) < HEADER + TRAILER:
        raise FrameError(f"{len(raw)} bytes is shorter than the smallest frame")
    expected = frame_length(raw[:HEADER])
    if len(raw) != expected:
        raise FrameError(f"frame says {expected} bytes, got {len(raw)}")
    body, crc = raw[:-TRAILER], raw[-TRAILER:]
    if crc_bytes(body) != crc:
        raise FrameError(f"CRC mismatch: got {crc.hex(' ')}, expected {crc_bytes(body).hex(' ')}")
    return Frame(address=body[0], payload=body[HEADER:])
