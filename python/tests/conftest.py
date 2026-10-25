"""Fixtures shared by all tests.

``BUS_URL`` decides where the device lives:

- ``memory://`` (default) — the simulator on an in-memory link
- ``socat://``            — the simulator behind two virtual serial ports made by socat
- ``/dev/ttyUSB0?baud=115200`` — a real device on the bench; simulator-only tests are skipped

``HIL=1`` enables tests marked ``hardware``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest

from bus_lab.device import EchoDevice
from bus_lab.transport import Transport, memory_pair, open_serial

DEVICE_ADDRESS = int(os.getenv("DEVICE_ADDRESS", "0x11"), 0)
BUS_URL = os.getenv("BUS_URL", "memory://")
REPLY_TIMEOUT = float(os.getenv("REPLY_TIMEOUT", "1.0"))
SILENCE = float(os.getenv("SILENCE", "0.3"))


@dataclass
class Bus:
    client: Transport
    device: EchoDevice | None  # None on real hardware: the board is the device
    address: int
    kind: str


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    on_hardware = BUS_URL not in ("memory://", "socat://")
    skip_hw = pytest.mark.skip(reason="needs the bench: set HIL=1 and BUS_URL to a real port")
    skip_sim = pytest.mark.skip(reason="reads simulator internals; not available on a real device")
    for item in items:
        if "hardware" in item.keywords and os.getenv("HIL") != "1":
            item.add_marker(skip_hw)
        if "simulator" in item.keywords and on_hardware:
            item.add_marker(skip_sim)


@pytest.fixture
def socat_ports() -> Iterator[tuple[str, str]]:
    if shutil.which("socat") is None:
        pytest.skip("socat is not installed")
    tmp = Path(tempfile.mkdtemp())
    a, b = tmp / "ttyV0", tmp / "ttyV1"
    proc = subprocess.Popen(
        ["socat", "-d0", f"pty,raw,echo=0,link={a}", f"pty,raw,echo=0,link={b}"],
    )
    deadline = time.monotonic() + 5
    while not (a.exists() and b.exists()):
        if time.monotonic() > deadline:
            proc.kill()
            pytest.fail("socat did not create the virtual ports")
        time.sleep(0.05)
    yield str(a), str(b)
    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture
def bus(request: pytest.FixtureRequest) -> Iterator[Bus]:
    client: Transport
    side: Transport
    if BUS_URL == "memory://":
        client, side = memory_pair()
        device = EchoDevice(side, DEVICE_ADDRESS).start()
        yield Bus(client, device, DEVICE_ADDRESS, "memory")
        device.stop()
        client.close()
        side.close()
    elif BUS_URL == "socat://":
        port_a, port_b = request.getfixturevalue("socat_ports")
        client, side = open_serial(port_a), open_serial(port_b)
        device = EchoDevice(side, DEVICE_ADDRESS).start()
        yield Bus(client, device, DEVICE_ADDRESS, "socat")
        device.stop()
        client.close()
        side.close()
    else:
        client = open_serial(BUS_URL)
        time.sleep(2)  # many boards reset when the port opens
        client.reset_input()
        yield Bus(client, None, DEVICE_ADDRESS, "hardware")
        client.close()


def assert_silence(link: Transport, seconds: float = SILENCE) -> None:
    """Nothing arrives within ``seconds``."""
    try:
        data = link.read(1, timeout=seconds)
    except TimeoutError:
        return
    raise AssertionError(f"expected silence, got {data.hex(' ')}")
