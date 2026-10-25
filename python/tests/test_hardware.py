"""Checks that only make sense on a real line. Skipped unless ``HIL=1``."""

import time

import pytest

from bus_lab.frame import MAX_PAYLOAD, Frame, decode, encode
from conftest import REPLY_TIMEOUT, Bus


@pytest.mark.hardware
def test_no_frame_is_lost_in_two_hundred_round_trips(bus: Bus) -> None:
    lost = 0
    for n in range(200):
        payload = bytes([n % 256]) * (n % (MAX_PAYLOAD + 1))
        bus.client.write(encode(Frame(bus.address, payload)))
        try:
            reply = decode(bus.client.read(4 + len(payload), timeout=REPLY_TIMEOUT))
        except (TimeoutError, ValueError):
            lost += 1
            bus.client.reset_input()
            continue
        assert reply.payload == payload
    assert lost == 0, f"{lost} of 200 frames lost or corrupted"


@pytest.mark.hardware
def test_round_trip_is_under_fifty_milliseconds(bus: Bus) -> None:
    timings = []
    for _ in range(20):
        start = time.perf_counter()
        bus.client.write(encode(Frame(bus.address, b"t")))
        bus.client.read(5, timeout=REPLY_TIMEOUT)
        timings.append(time.perf_counter() - start)
    timings.sort()
    assert timings[len(timings) // 2] < 0.05, f"median {timings[len(timings) // 2] * 1000:.1f} ms"
