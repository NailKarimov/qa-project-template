# qa-project-template

[![Tests](https://github.com/NailKarimov/qa-project-template/actions/workflows/tests.yml/badge.svg)](https://github.com/NailKarimov/qa-project-template/actions/workflows/tests.yml)
[![Allure report](https://img.shields.io/badge/report-Allure-orange)](https://nailkarimov.github.io/qa-project-template/)
[![Release](https://img.shields.io/github/v/release/NailKarimov/qa-project-template)](https://github.com/NailKarimov/qa-project-template/releases)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/NailKarimov/qa-project-template?quickstart=1)

### ▶ Open online

| Page                                                                                              | What it is                  |
| ------------------------------------------------------------------------------------------------- | --------------------------- |
| **[Allure test report](https://nailkarimov.github.io/qa-project-template/)**                      | example run of the template |
| [Protocol bench starter](https://nailkarimov.github.io/qa-project-template/protocol-starter.html) | interactive guide           |
| [GitHub as a QA showcase](https://nailkarimov.github.io/qa-project-template/github-showcase.html) | interactive guide           |

Click these links: opening an `.html` file in the file list shows its source code, GitHub does not run it.

The template behind a portfolio of test-automation projects. It ships **two starters** in one repository:

1. **Protocol and device testing** (`python/`) — the backbone of the hardware and energy track: one pytest suite
   that runs in memory, over virtual serial ports, and on a real board.
2. **Web UI and API testing** (`src/`) — Playwright + TypeScript, UI and API in one suite.

Both share the same **GitHub Actions** CI, **Allure** reporting with history, code-quality gates on every commit, and
the portfolio's Definition of Done. Click **Use this template** to start a new project with everything already set up.

## Protocol and device testing — the primary starter

[`python/`](python/): **Python 3.12 + pytest**, Hypothesis, pyserial, socat, Allure, ruff and mypy. The example
system under test is a small echo device that speaks CRC-16/MODBUS frames — replace it with the protocol of your
project (Modbus, inverters, batteries, EV charging).

The idea of this starter: **one suite, three links**, selected by the `BUS_URL` environment variable, so the same
tests run from the cloud all the way to the bench.

| Link           | `BUS_URL`                | Where it runs                                           |
| -------------- | ------------------------ | ------------------------------------------------------- |
| In memory      | `memory://` (default)    | unit and logic, green in CI                             |
| Virtual serial | `socat://`               | two linked PTYs, the serial path exercised, green in CI |
| Real board     | `/dev/ttyUSB0` + `HIL=1` | hardware-in-the-loop on a flashed ESP32 at the bench    |

The ESP32 firmware twin is in [`bench/uart-echo/`](bench/uart-echo/). **30 automated tests + 2 hardware-only**, and
**8/8 planted bugs caught** on both virtual links (`scripts/mutants.py`). The two hardware tests run once a board is
flashed and connected.

| Suite                    | Tool               | What it proves                                                                       |
| ------------------------ | ------------------ | ------------------------------------------------------------------------------------ |
| `tests/test_crc.py`      | pytest             | CRC-16/MODBUS matches the published check value and a real Modbus frame              |
| `tests/test_frame.py`    | pytest, Hypothesis | Any frame round-trips; any single bit flip is detected; size and address limits      |
| `tests/test_device.py`   | pytest, socat      | The device answers only its address, stays silent on broadcast and bad CRC, recovers |
| `tests/test_hardware.py` | pytest, real UART  | No frame lost in 200 round trips; median round trip under 50 ms (bench only)         |

To use it, copy the contents of `python/` to the root of a new repository. Guides:
[`docs/protocol-starter.md`](docs/protocol-starter.md) ·
[interactive](https://nailkarimov.github.io/qa-project-template/protocol-starter.html).

## Web UI and API testing — Playwright + TypeScript

The second starter (`src/`, `tests/`): UI and API tests in one suite, with Allure reporting and the same CI.

| Area          | Files                                              | Details                                                                                                                                                     |
| ------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Page objects  | `src/pages`                                        | `BasePage` plus one class per page; locators use `data-test` attributes                                                                                     |
| API clients   | `src/api`                                          | `ApiClient` attaches every request and response to the report; one client per resource                                                                      |
| Test data     | `src/data`                                         | Factories built on Faker; override fields for boundary and negative cases                                                                                   |
| Fixtures      | `src/fixtures.ts`                                  | Tests receive ready objects: `async ({ loginPage, posts }) => …`                                                                                            |
| Configuration | `config/env.ts`, `.env.example`                    | Every URL and credential can be overridden by an environment variable                                                                                       |
| Tests         | `tests/ui`, `tests/api`                            | Two Playwright projects; `@smoke` tag for the critical path                                                                                                 |
| Code quality  | `eslint.config.mjs`, `.prettierrc.json`, `.husky/` | ESLint with Playwright rules, Prettier, pre-commit checks via lint-staged                                                                                   |
| CI            | `.github/workflows/tests.yml`                      | Runs on push, PR, nightly and on demand; lint, type check, tests; Allure to GitHub Pages                                                                    |
| Documentation | `docs/test-plan.md`, `docs/test-report.md`         | Templates based on ISO/IEC/IEEE 29119-3; the portfolio layout in `docs/portfolio-standard.md`; issues, releases and Codespaces in `docs/github-showcase.md` |

The example tests run against public demo targets: [Sauce Demo](https://www.saucedemo.com) for UI and
[JSONPlaceholder](https://jsonplaceholder.typicode.com) for API. Replace them with your system under test.

## Getting started

No local setup: the **Open in GitHub Codespaces** badge starts a browser VS Code with this repository, Node, Python, Java and Docker; the container installs the dependencies and Chromium on creation, then `npm test` works in the terminal.

Requirements: Node.js 22+, Java 17+ (for the Allure CLI); Python 3.12+ and socat for the protocol starter.

```bash
# Web UI + API starter
npm ci
npx playwright install chromium
cp .env.example .env      # optional: change targets or credentials

npm test                  # all tests
npm run test:api          # API tests only
npm run test:ui           # UI tests only
npm run test:smoke        # @smoke tests only
npm run test:headed       # UI tests with a visible browser

npm run lint              # ESLint
npm run format            # Prettier
npm run typecheck         # TypeScript

npm run allure:generate && npm run allure:open
```

```bash
# Protocol + device starter
cd python
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"

pytest                                  # in memory
BUS_URL=socat:// pytest                 # through two virtual serial ports
BUS_URL=/dev/ttyUSB0 HIL=1 pytest       # on the bench, board flashed from bench/uart-echo
python scripts/mutants.py               # plant bugs one at a time
```

## Starting a new project from this template

1. **Use this template** → name the repository → clone it.
2. Pick the starter you need: `src/` for web UI and API, or `python/` for protocol and device testing.
3. Set the targets (`.env.example` and `config/env.ts`, or the device under test in `python/src/bus_lab`).
4. Replace the example page objects, API clients, tests or device model.
5. Fill in `docs/test-plan.md` before writing tests and `docs/test-report.md` after the first full run.
6. In the new repository: **Settings → Pages → Deploy from a branch → `gh-pages` / `(root)`**
   to publish the Allure report.
7. Update the badges and links at the top of this README.

## Definition of Done for a portfolio project

Every repository of the portfolio follows one layout: [`docs/portfolio-standard.md`](docs/portfolio-standard.md).

- [ ] README in the common order: at a glance, what is tested, findings, running it, structure, CI, documentation
- [ ] Test plan and test summary report in `docs/` (ISO/IEC/IEEE 29119-3)
- [ ] A text guide and an interactive guide for every tool or approach
- [ ] Tests run with one command locally and in CI; reports published on GitHub Pages
- [ ] A mutation check: bugs planted one at a time, and every one is caught
- [ ] Defects found are bug reports in Issues (`.github/ISSUE_TEMPLATE/bug_report.yml`), linked from Findings
- [ ] A release: commit `.github/releases/<tag>.md` and the Release workflow publishes the tag and the release
- [ ] Lint, format and type checks pass; no secrets in the repository

## Conventions

- Tests contain actions and assertions only; selectors live in page objects.
- No fixed sleeps: rely on Playwright auto-waiting (`playwright/no-wait-for-timeout` is an error).
- Test names describe expected behaviour: _"locked out user gets an error message"_.
- One retry in CI only; retries stay visible in the report.

## Part of a portfolio

The template behind the 13 test automation projects of [Nail Karimov](https://github.com/NailKarimov):
[all projects](https://github.com/NailKarimov) ·
[testing map](https://nailkarimov.github.io/api-test-automation/testing-map.html) ·
[toolbox](https://nailkarimov.github.io/api-test-automation/toolbox.html).
