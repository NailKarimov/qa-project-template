# qa-project-template

[![Tests](https://github.com/NailKarimov/qa-project-template/actions/workflows/tests.yml/badge.svg)](https://github.com/NailKarimov/qa-project-template/actions/workflows/tests.yml)
[![Allure report](https://img.shields.io/badge/report-Allure-orange)](https://nailkarimov.github.io/qa-project-template/)
[![Release](https://img.shields.io/github/v/release/NailKarimov/qa-project-template)](https://github.com/NailKarimov/qa-project-template/releases)

### ▶ Open online

| Page                                                                                              | What it is                  |
| ------------------------------------------------------------------------------------------------- | --------------------------- |
| **[Allure test report](https://nailkarimov.github.io/qa-project-template/)**                      | example run of the template |
| [Protocol bench starter](https://nailkarimov.github.io/qa-project-template/protocol-starter.html) | interactive guide           |

Click these links: opening an `.html` file in the file list shows its source code, GitHub does not run it.

Starter template for test automation projects: **Playwright + TypeScript**, UI and API tests in one suite,
**Allure** reporting with history, **GitHub Actions** CI, and code quality checks on every commit.

Click **Use this template** to start a new project with everything below already set up.

## What is inside

| Area          | Files                                              | Details                                                                                       |
| ------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Page objects  | `src/pages`                                        | `BasePage` plus one class per page; locators use `data-test` attributes                       |
| API clients   | `src/api`                                          | `ApiClient` attaches every request and response to the report; one client per resource        |
| Test data     | `src/data`                                         | Factories built on Faker; override fields for boundary and negative cases                     |
| Fixtures      | `src/fixtures.ts`                                  | Tests receive ready objects: `async ({ loginPage, posts }) => …`                              |
| Configuration | `config/env.ts`, `.env.example`                    | Every URL and credential can be overridden by an environment variable                         |
| Tests         | `tests/ui`, `tests/api`                            | Two Playwright projects; `@smoke` tag for the critical path                                   |
| Code quality  | `eslint.config.mjs`, `.prettierrc.json`, `.husky/` | ESLint with Playwright rules, Prettier, pre-commit checks via lint-staged                     |
| CI            | `.github/workflows/tests.yml`                      | Runs on push, PR, nightly and on demand; lint, type check, tests; Allure to GitHub Pages      |
| Documentation | `docs/test-plan.md`, `docs/test-report.md`         | Templates based on ISO/IEC/IEEE 29119-3; the portfolio layout in `docs/portfolio-standard.md` |

The example tests run against public demo targets: [Sauce Demo](https://www.saucedemo.com) for UI and
[JSONPlaceholder](https://jsonplaceholder.typicode.com) for API. Replace them with your system under test.

## Python starter for protocol and device testing

[`python/`](python/) is a second starter: **Python 3.12 + pytest**, Hypothesis, pyserial, Allure, ruff and mypy.
One suite runs unchanged on three links, chosen by `BUS_URL`: in memory, over two virtual serial ports made by
socat, and on a real board. The example is a small echo device with CRC-16/MODBUS frames; its ESP32 firmware twin
is in [`bench/uart-echo/`](bench/uart-echo/). 30 tests, 8/8 planted bugs caught on both virtual links.

To use it, copy the contents of `python/` to the root of a new repository. Guide:
[`docs/protocol-starter.md`](docs/protocol-starter.md) ·
[interactive](https://nailkarimov.github.io/qa-project-template/protocol-starter.html).

## Getting started

Requirements: Node.js 22+, Java 17+ (for the Allure CLI).

```bash
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

## Starting a new project from this template

1. **Use this template** → name the repository → clone it.
2. Set the targets in `.env.example` and `config/env.ts`.
3. Replace the example page objects, API clients and tests.
4. Fill in `docs/test-plan.md` before writing tests and `docs/test-report.md` after the first full run.
5. In the new repository: **Settings → Pages → Deploy from a branch → `gh-pages` / `(root)`**
   to publish the Allure report.
6. Update the badges and links at the top of this README.

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
