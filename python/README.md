# <project-name>

[![Tests](https://github.com/NailKarimov/<project-name>/actions/workflows/tests.yml/badge.svg)](https://github.com/NailKarimov/<project-name>/actions/workflows/tests.yml)
[![Allure report](https://img.shields.io/badge/report-Allure-orange)](https://nailkarimov.github.io/<project-name>/)

Python + pytest starter for protocol and device testing. One suite runs on three links: in memory, over virtual
serial ports made by socat, and on a real board at the bench. The example system is a small echo device with
CRC-16/MODBUS frames; replace it with the protocol of your project.

## At a glance

| Row                | Content                                                                             |
| ------------------ | ----------------------------------------------------------------------------------- |
| System under test  | Example: own echo-device simulator (`src/bus_lab/device.py`) and ESP32 firmware     |
| Language and tools | Python 3.12; pytest, Hypothesis, pyserial, socat, Allure, ruff, mypy                |
| Types of testing   | Unit (CRC, framing), property-based, device behaviour, transport, hardware-in-loop  |
| Tests              | 30 automated + 2 hardware-only                                                      |
| Test quality       | 8/8 planted bugs caught on both transports (`scripts/mutants.py`)                   |
| Reports            | [Allure](https://nailkarimov.github.io/<project-name>/) · mutation table in the run |

## What is tested

| Suite                    | Tool               | What it proves                                                                       |
| ------------------------ | ------------------ | ------------------------------------------------------------------------------------ |
| `tests/test_crc.py`      | pytest             | CRC-16/MODBUS matches the published check value and a real Modbus frame              |
| `tests/test_frame.py`    | pytest, Hypothesis | Any frame round-trips; any single bit flip is detected; size and address limits      |
| `tests/test_device.py`   | pytest, socat      | The device answers only its address, keeps silent on broadcast and bad CRC, recovers |
| `tests/test_hardware.py` | pytest, real UART  | No frame lost in 200 round trips; median round trip under 50 ms                      |

## Findings

None yet. Each defect gets an id (`BUG-001`), a test, and a line in [`docs/test-report.md`](docs/test-report.md).

## Running it

Requirements: Python 3.12+, socat (`sudo apt install socat`) for the serial-port run.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"

pytest                                  # in memory
BUS_URL=socat:// pytest                 # through two virtual serial ports
BUS_URL=/dev/ttyUSB0 HIL=1 pytest       # on the bench, with the board flashed from bench/uart-echo
pytest -m smoke                         # critical path only
python scripts/mutants.py               # plant bugs one at a time
bash scripts/check-env.sh               # what is missing on this machine

ruff check . && ruff format --check . && mypy src tests scripts
```

## Project structure

```text
src/bus_lab/     frame format, CRC, transports, device simulator
tests/           conftest.py chooses the link from BUS_URL; one file per suite
scripts/         mutants.py, check-env.sh
docs/            test plan, test report, guides
.github/         CI: both transports, mutation check, Allure to Pages
```

## Design decisions

- **One suite, many links.** Tests see only a `Transport` with `write` and `read`. `BUS_URL` decides whether it is
  a socket pair, a socat pseudo-terminal or `/dev/ttyUSB0`, so the cloud run and the bench run are the same tests.
- **Two markers.** `simulator` tests read the simulator's counters and are skipped on hardware. `hardware` tests
  need a real line and are skipped unless `HIL=1`.
- **Silence is a result.** Many protocols answer a bad frame with nothing. `assert_silence()` waits a fixed
  window and fails on any byte, so "no answer" is checked, not assumed.

## CI

Push, pull request, nightly and manual runs. Lint and types, then the suite in memory and over socat, then the
mutation check. The Allure report with history goes to `gh-pages`. A commented `hil` job runs on a self-hosted
runner at the bench, on schedule and manually only, never on pull requests.

## Documentation

| File                                         | What it is                      |
| -------------------------------------------- | ------------------------------- |
| [`docs/test-plan.md`](docs/test-plan.md)     | Test plan, ISO/IEC/IEEE 29119-3 |
| [`docs/test-report.md`](docs/test-report.md) | Latest run, defects, deviations |

## Part of a portfolio

One of the test automation projects of [Nail Karimov](https://github.com/NailKarimov):
[all projects](https://github.com/NailKarimov) ·
[testing map](https://nailkarimov.github.io/api-test-automation/testing-map.html) ·
[toolbox](https://nailkarimov.github.io/api-test-automation/toolbox.html).
