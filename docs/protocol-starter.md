# Protocol testing starter: Python template, virtual links and the bench

Stage 0 of the energy-protocols roadmap: the workstation, the first piece of hardware, and the Python starter that
the four new repositories (`solar-inverter-testing`, `battery-can-testing`, `ev-charging-testing`,
`home-energy-testing`) are created from. Interactive version:
[protocol-starter.html](https://nailkarimov.github.io/qa-project-template/protocol-starter.html).

## What it is

| Part              | Where                           | Purpose                                                                    |
| ----------------- | ------------------------------- | -------------------------------------------------------------------------- |
| Python starter    | `python/`                       | pytest suite that runs unchanged in memory, over socat and on a real board |
| Environment check | `python/scripts/check-env.sh`   | Lists what is missing on the workstation, installs nothing                 |
| Echo firmware     | `bench/uart-echo/uart_echo.ino` | ESP32 twin of the simulator: same frames, same rules                       |
| Probe             | `bench/uart-echo/probe.py`      | Sends known bytes so they can be read in PulseView                         |

## Why

Protocol work has two places to fail: the logic (frames, checksums, what the device does with a bad frame) and
the line (baud rate, wiring, noise, timing). The logic is tested in the cloud on every push. The line can only be
tested at the bench. Keeping one suite for both means a green cloud run and a red bench run point straight at the
physical layer.

## How it works

```text
tests ──► Transport (write / read with timeout)
              │
              ├─ memory://          socket pair in the same process        ──► simulator
              ├─ socat://           two pseudo-terminals joined by socat   ──► simulator
              └─ /dev/ttyUSB0       USB-UART chip → TX/RX wires            ──► ESP32 firmware
```

- `BUS_URL` chooses the link. The tests do not change.
- `@pytest.mark.simulator` tests read the simulator's counters (CRC errors, broadcasts). They are skipped on a
  real board, which has no such window.
- `@pytest.mark.hardware` tests need a real line: 200 round trips without loss, round-trip median under 50 ms.
  They run only with `HIL=1`.
- `assert_silence()` waits a fixed window and fails on any byte. Many field protocols answer a bad frame with
  nothing, so silence is an expected result and must be checked.

The example protocol is deliberately small: `[address][length][payload][CRC low][CRC high]`, CRC-16/MODBUS. The
CRC test uses the same Modbus frame as stage 1 of the plan: `01 03 00 00 00 02` → `C4 0B`.

## How to run it

```bash
cd python
python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
bash scripts/check-env.sh
pytest                                 # memory
BUS_URL=socat:// pytest                # virtual serial ports
BUS_URL=/dev/ttyUSB0 HIL=1 pytest      # the ESP32 on the bench
python scripts/mutants.py
```

To start a new repository: copy the contents of `python/` to the root of the new repository, replace
`<project-name>` in the README, replace `src/bus_lab` with the real client and simulator, and rewrite the test
plan.

## The first UART exchange

1. Flash `bench/uart-echo/uart_echo.ino` to an ESP32 dev board (Arduino IDE, board "ESP32 Dev Module").
2. Connect the logic analyzer: CH0 to TX0 (GPIO1), CH1 to RX0 (GPIO3), GND to GND. The USB cable stays connected;
   the analyzer only listens.
3. PulseView: driver `fx2lafw`, 2 MHz sample rate, 1 M samples, trigger on a falling edge of CH1.
4. Add the UART decoder: 115200 baud, 8 data bits, no parity, 1 stop bit; RX = CH1, TX = CH0.
5. Run `python bench/uart-echo/probe.py /dev/ttyUSB0` (on Windows: `COM5`).
6. Expected: `55 55 55 55` with no reply, the `ping` frame on RX and the same bytes on TX, then a frame with a
   broken CRC and no reply.

`0x55` is `01010101`: with the start and stop bits every bit cell has an edge, so the bit width is easy to measure.
At 115200 baud one bit is 8.68 µs; a whole byte (10 bits) is 86.8 µs.

On WSL2 the USB port has to be attached to Linux first: `usbipd list`, then
`usbipd attach --wsl --busid <id>`. PulseView is simpler on Windows itself.

## Reading the result

| What you see                                   | Meaning                                                   |
| ---------------------------------------------- | --------------------------------------------------------- |
| Decoder shows framing errors on every byte     | Baud rate differs on the two sides or in the decoder      |
| RX traffic, nothing on TX                      | Firmware not running, wrong address, or a CRC mismatch    |
| Reply in PulseView but `probe.py` gets nothing | The script opened the wrong port or the timeout is short  |
| `memory` and `socat` green, bench red          | The problem is in the line or the firmware, not the logic |

## Mutation check

`scripts/mutants.py` plants eight bugs one at a time (CRC start value, polynomial, byte order, trailing bytes,
size limit, wrong address, broadcast reply, missing flush). All eight are caught on both virtual links. Two
survived the first round and changed the suite:

- **M7, equivalent mutant.** Removing the `return` after a broadcast changed nothing, because the next check
  (wrong address) still blocked the reply. The mutant was rewritten so the device really answers.
- **M8, missing flush.** The test sent only a bad header, so there was nothing to flush. It now sends bytes that
  look like the start of the next frame; a device without the flush swallows the following request.

## Tools of stage 0

| Tool               | What it does                                    | Alternatives                              |
| ------------------ | ----------------------------------------------- | ----------------------------------------- |
| socat              | Joins two pseudo-terminals into a virtual cable | tty0tty (Linux), com0com (Windows)        |
| pyserial           | Serial ports from Python, real or virtual       | pyserial-asyncio for async code           |
| Hypothesis         | Generates inputs for properties                 | plain parametrisation                     |
| Wireshark          | Reads Modbus TCP, OCPP over WebSocket, CAN      | tcpdump, tshark                           |
| can-utils          | `candump`, `cansend` on SocketCAN               | python-can tools                          |
| Logic analyzer     | Records digital lines; 8 channels, 24 MHz       | USB oscilloscope (analog view)            |
| PulseView (sigrok) | Shows and decodes the analyzer's capture        | Saleae Logic 2 (only for Saleae hardware) |

## Limits

- The in-memory link is a perfect cable: it never loses or delays bytes. Timing and noise are bench questions.
- socat pseudo-terminals ignore baud rate and parity, so speed mismatches can only be seen on real hardware.
- A cheap 24 MHz analyzer is enough for UART, RS-485 at Modbus speeds and CAN at 500 kbit/s; it shows logic
  levels, not voltages.

## Sources

- Modbus over Serial Line, V1.02 — CRC-16 and RTU framing: <https://modbus.org/specs.php>
- sigrok: fx2lafw driver and the UART decoder: <https://sigrok.org/wiki/Fx2lafw>
- socat manual: <http://www.dest-unreach.org/socat/doc/socat.html>
- usbipd-win, USB devices in WSL: <https://learn.microsoft.com/windows/wsl/connect-usb>
