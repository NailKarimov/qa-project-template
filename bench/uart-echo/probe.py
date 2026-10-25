"""Send a few frames to the echo board and print what comes back. Use it with PulseView running.

    pip install pyserial
    python probe.py /dev/ttyUSB0          # Linux (on WSL2 attach the port with usbipd first)
    python probe.py COM5                  # Windows

What to look for in PulseView (UART decoder, 115200 8N1):
  1. 0x55 'U' — alternating bits 01010101: the cleanest way to check the baud rate on the screen.
  2. The frame 11 04 70 69 6E 67 + CRC on RX, and the same bytes back on TX.
  3. A frame with a broken CRC on RX and no answer on TX.
"""

import sys
import time

import serial

MAX_PAYLOAD = 32


def crc16_modbus(data: bytes) -> bytes:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc.to_bytes(2, "little")


def frame(address: int, payload: bytes) -> bytes:
    body = bytes([address, len(payload)]) + payload
    return body + crc16_modbus(body)


def show(label: str, data: bytes) -> None:
    print(f"{label:<10} {data.hex(' ').upper() or '(nothing)'}")


def main() -> None:
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
    with serial.Serial(port, 115200, timeout=0.5) as link:
        time.sleep(2)  # the board resets when the port opens
        link.reset_input_buffer()

        show("sent", b"UUUU")
        link.write(b"UUUU")  # not a frame: the board treats it as junk, nothing comes back
        time.sleep(0.6)
        link.reset_input_buffer()

        good = frame(0x11, b"ping")
        show("sent", good)
        link.write(good)
        start = time.perf_counter()
        reply = link.read(len(good))
        show("received", reply)
        print(f"{'':<10} round trip {(time.perf_counter() - start) * 1000:.1f} ms, match: {reply == good}")

        bad = bytearray(good)
        bad[-1] ^= 0xFF
        show("sent", bytes(bad))
        link.write(bytes(bad))
        show("received", link.read(len(good)))


if __name__ == "__main__":
    main()
