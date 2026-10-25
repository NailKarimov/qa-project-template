import pytest

from bus_lab.crc import crc16_modbus, crc_bytes


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(b"123456789", 0x4B37, id="standard check value"),
        pytest.param(bytes.fromhex("01 03 00 00 00 02"), 0x0BC4, id="Modbus read 2 registers"),
        pytest.param(b"", 0xFFFF, id="empty input keeps the initial value"),
        pytest.param(b"\x00", 0x40BF, id="one zero byte"),
    ],
)
def test_crc_matches_known_vectors(data: bytes, expected: int) -> None:
    assert crc16_modbus(data) == expected


def test_crc_goes_on_the_wire_low_byte_first() -> None:
    assert crc_bytes(bytes.fromhex("01 03 00 00 00 02")) == bytes.fromhex("C4 0B")
