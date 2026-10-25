# Test plan — <project name>

Structure follows ISO/IEC/IEEE 29119-3 (test plan), shortened for a single project. The text below describes the
example echo device; replace it when the template becomes a real project.

## 1. Context

- **System under test (SUT):** echo-device simulator `src/bus_lab/device.py` and its firmware twin
  `bench/uart-echo/uart_echo.ino` (ESP32).
- **Goal of testing:** show that the device follows the four framing rules on every link, and that the suite
  catches a broken rule.
- **References:** CRC-16/MODBUS (Modbus over Serial Line, V1.02, section 6.2.2); the rules in `device.py`.

## 2. Scope

| In scope                                     | Out of scope                                     |
| -------------------------------------------- | ------------------------------------------------ |
| CRC, frame encoding and decoding             | Real Modbus function codes (stage 1 of the plan) |
| Device answers, silence, recovery            | Electrical layer: voltage levels, noise, cabling |
| Same tests in memory, over socat, on a board | Throughput above 115200 baud                     |

## 3. Quality characteristics (ISO/IEC 25010)

| Characteristic         | Covered by                              | Notes                                      |
| ---------------------- | --------------------------------------- | ------------------------------------------ |
| Functional suitability | `test_crc`, `test_frame`, `test_device` | Known vectors, boundaries, rule-by-rule    |
| Reliability            | recovery tests, `test_hardware`         | Bad frame then good frame; 200 round trips |
| Performance efficiency | `test_hardware` round-trip median       | Bench only                                 |
| Compatibility          | the same suite on three transports      | memory, socat, USB serial                  |

## 4. Test approach

- **Levels:** unit (CRC, framing), component (device on a link), hardware-in-the-loop (board on the bench).
- **Test design techniques:** known-answer vectors; boundary values (payload 0, 32, 33; address −1, 256);
  property-based testing (round trip, single bit flip); state transitions (bad frame → recovery).
- **Test data:** generated per test; Hypothesis keeps failing examples in `.hypothesis/`.
- **Environments:** `BUS_URL` = `memory://`, `socat://` or a real port; `HIL=1` on the bench.
- **Test quality:** `scripts/mutants.py` plants 8 bugs one at a time; each must fail the suite.

## 5. Risks

| Risk                                   | Impact                  | Mitigation                                        |
| -------------------------------------- | ----------------------- | ------------------------------------------------- |
| Timing differs between links           | Flaky silence checks    | Silence window and reply timeout set by env vars  |
| Board prints boot messages on the port | First reads see garbage | Fixture waits 2 s and flushes input after opening |
| Self-hosted runner on a public repo    | Fork code runs at home  | HIL job on schedule and manual trigger only       |

## 6. Entry and exit criteria

- **Entry:** suite lints and type-checks; socat available for the serial run.
- **Exit:** all tests pass on memory and socat; every mutant caught; hardware run recorded when the bench exists.

## 7. Deliverables

- Automated test suite in this repository
- Allure report on GitHub Pages and the mutation table in each run
- Test summary report: [`test-report.md`](test-report.md)
