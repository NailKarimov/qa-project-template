# Test summary report — <project name>

Structure follows ISO/IEC/IEEE 29119-3 (test completion report). Numbers below are from the template's own run.

## 1. Summary

| Item         | Value                                                  |
| ------------ | ------------------------------------------------------ |
| Date         | 2026-10-25                                             |
| Build        | qa-project-template, `python/` starter                 |
| Environments | `memory://` and `socat://`, Python 3.12, Ubuntu        |
| Result       | 30 passed, 2 skipped (hardware), 0 failed on each link |
| Test quality | 8/8 planted bugs caught on both links                  |

## 2. Results by suite

| Suite         | Tests | Passed | Skipped | Notes                                   |
| ------------- | ----- | ------ | ------- | --------------------------------------- |
| test_crc      | 5     | 5      | 0       |                                         |
| test_frame    | 14    | 14     | 0       | Two Hypothesis properties, 100 examples |
| test_device   | 11    | 11     | 0       | Two read simulator counters             |
| test_hardware | 2     | 0      | 2       | Need `HIL=1` and the board              |

## 3. Mutation check

| Id  | Planted bug                    | Caught by                                |
| --- | ------------------------------ | ---------------------------------------- |
| M1  | CRC starts from 0              | known vectors                            |
| M2  | Non-reflected polynomial       | known vectors                            |
| M3  | CRC high byte first            | wire-order test                          |
| M4  | Trailing bytes accepted        | malformed-frame cases                    |
| M5  | Payload limit off by one       | boundary test at 33 bytes                |
| M6  | Device answers every address   | silence for another address              |
| M7  | Device answers a broadcast     | silence on broadcast                     |
| M8  | No flush after a framing error | recovery after an impossible length byte |

The first round left M7 and M8 alive. M7 was an equivalent mutant: the address check still blocked the reply,
so the mutant was rewritten to really answer. M8 survived because the test sent nothing after the bad header;
the test now sends bytes that look like the start of a frame, which a device without the flush swallows.

## 4. Defects

None.

## 5. Deviations and recommendations

- Hardware tests were not run: the bench is planned for stage 0 of the energy-protocols roadmap.
- When the template becomes a project, replace the example and this report after the first full run.
