"""Behaviour of the device on the link. These tests run on every transport:
in memory, through socat, and on the real board (``BUS_URL=/dev/ttyUSB0``)."""

import time

import pytest

from bus_lab.frame import BROADCAST, MAX_PAYLOAD, Frame, decode, encode
from conftest import REPLY_TIMEOUT, Bus, assert_silence


def request(bus: Bus, frame: Frame) -> Frame:
    bus.client.write(encode(frame))
    raw = bus.client.read(4 + len(frame.payload), timeout=REPLY_TIMEOUT)
    return decode(raw)


@pytest.mark.smoke
def test_device_echoes_a_frame_sent_to_its_address(bus: Bus) -> None:
    assert request(bus, Frame(bus.address, b"ping")) == Frame(bus.address, b"ping")


@pytest.mark.parametrize("size", [0, MAX_PAYLOAD])
def test_device_echoes_empty_and_largest_payload(bus: Bus, size: int) -> None:
    payload = bytes(range(size))
    assert request(bus, Frame(bus.address, payload)).payload == payload


def test_device_ignores_frames_for_another_address(bus: Bus) -> None:
    bus.client.write(encode(Frame(bus.address + 1, b"not for you")))
    assert_silence(bus.client)


def test_device_never_answers_a_broadcast(bus: Bus) -> None:
    bus.client.write(encode(Frame(BROADCAST, b"all")))
    assert_silence(bus.client)


@pytest.mark.simulator
def test_device_executes_a_broadcast(bus: Bus) -> None:
    assert bus.device is not None
    bus.client.write(encode(Frame(BROADCAST, b"all")))
    assert_silence(bus.client)
    assert bus.device.broadcasts == 1


def test_frame_with_a_wrong_crc_gets_no_answer(bus: Bus) -> None:
    raw = bytearray(encode(Frame(bus.address, b"ping")))
    raw[-1] ^= 0xFF
    bus.client.write(bytes(raw))
    assert_silence(bus.client)


@pytest.mark.simulator
def test_wrong_crc_is_counted(bus: Bus) -> None:
    assert bus.device is not None
    raw = bytearray(encode(Frame(bus.address, b"ping")))
    raw[2] ^= 0x01
    bus.client.write(bytes(raw))
    assert_silence(bus.client)
    assert bus.device.crc_errors == 1


def test_device_recovers_after_a_bad_frame(bus: Bus) -> None:
    raw = bytearray(encode(Frame(bus.address, b"bad")))
    raw[-2] ^= 0x55
    bus.client.write(bytes(raw))
    assert_silence(bus.client)
    assert request(bus, Frame(bus.address, b"good")).payload == b"good"


def test_device_recovers_after_an_impossible_length_byte(bus: Bus) -> None:
    # The junk after the bad header looks like the start of a 16-byte frame.
    # Unless the device flushes its input, it waits for that frame and swallows the next request.
    bus.client.write(bytes([bus.address, 0xFF, bus.address, 0x10]))
    assert_silence(bus.client)
    time.sleep(0.1)
    assert request(bus, Frame(bus.address, b"again")).payload == b"again"


def test_twenty_frames_back_to_back_all_get_their_own_answer(bus: Bus) -> None:
    for n in range(20):
        payload = n.to_bytes(2, "big")
        assert request(bus, Frame(bus.address, payload)).payload == payload
