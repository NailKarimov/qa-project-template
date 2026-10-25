import pytest
from hypothesis import given
from hypothesis import strategies as st

from bus_lab.frame import MAX_PAYLOAD, Frame, FrameError, decode, encode

addresses = st.integers(min_value=0, max_value=255)
payloads = st.binary(max_size=MAX_PAYLOAD)


@given(addresses, payloads)
def test_any_frame_survives_encode_and_decode(address: int, payload: bytes) -> None:
    assert decode(encode(Frame(address, payload))) == Frame(address, payload)


@given(addresses, payloads, st.data())
def test_any_single_bit_flip_is_detected(address: int, payload: bytes, data: st.DataObject) -> None:
    raw = bytearray(encode(Frame(address, payload)))
    bit = data.draw(st.integers(min_value=0, max_value=len(raw) * 8 - 1), label="bit")
    raw[bit // 8] ^= 1 << (bit % 8)
    with pytest.raises(FrameError):
        decode(bytes(raw))


@pytest.mark.parametrize("size", [0, 1, MAX_PAYLOAD - 1, MAX_PAYLOAD])
def test_payload_sizes_up_to_the_limit_are_accepted(size: int) -> None:
    assert len(decode(encode(Frame(0x11, bytes(size)))).payload) == size


def test_payload_one_byte_over_the_limit_is_rejected() -> None:
    with pytest.raises(FrameError, match="longer than"):
        Frame(0x11, bytes(MAX_PAYLOAD + 1))


@pytest.mark.parametrize("address", [-1, 256])
def test_address_outside_one_byte_is_rejected(address: int) -> None:
    with pytest.raises(FrameError, match="outside"):
        Frame(address, b"")


def test_frame_layout_is_address_length_payload_crc() -> None:
    raw = encode(Frame(0x11, b"\xab"))
    assert raw[:3] == bytes.fromhex("11 01 ab")
    assert len(raw) == 5


@pytest.mark.parametrize(
    ("raw", "reason"),
    [
        pytest.param(b"\x11\x00\x00", "shorter", id="three bytes"),
        pytest.param(encode(Frame(0x11, b"ok")) + b"\x00", "frame says", id="trailing byte"),
        pytest.param(encode(Frame(0x11, b"ok"))[:-1], "frame says", id="missing byte"),
        pytest.param(bytes([0x11, MAX_PAYLOAD + 1]) + bytes(MAX_PAYLOAD + 3), "larger than", id="length byte too big"),
    ],
)
def test_malformed_frames_are_rejected(raw: bytes, reason: str) -> None:
    with pytest.raises(FrameError, match=reason):
        decode(raw)
