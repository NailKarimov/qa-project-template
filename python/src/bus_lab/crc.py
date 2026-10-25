"""CRC-16/MODBUS: the checksum used by Modbus RTU and by the example frame format."""

POLY = 0xA001  # 0x8005 reflected
INIT = 0xFFFF


def crc16_modbus(data: bytes) -> int:
    """Return the CRC-16/MODBUS of ``data``.

    On the wire the low byte goes first: for ``01 03 00 00 00 02`` the CRC is
    0x0BC4, sent as ``C4 0B``.
    """
    crc = INIT
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ POLY
            else:
                crc >>= 1
    return crc


def crc_bytes(data: bytes) -> bytes:
    """The two CRC bytes in wire order (low byte first)."""
    return crc16_modbus(data).to_bytes(2, "little")
