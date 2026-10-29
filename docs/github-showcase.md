# GitHub as a QA showcase: issues, releases, Codespaces

How the portfolio uses GitHub beyond code and CI, and how to repeat it in a new repository. The interactive version
of this guide is [`github-showcase.html`](https://nailkarimov.github.io/qa-project-template/github-showcase.html).

## Why

A reviewer opens a repository for a minute. In that minute the README shows the tests, but the sidebar and the
tabs show whether the work behaves like a real QA process: are defects reported, is there a release, can the
suite be run without a local setup. Four GitHub features answer that without extra tools.

| Feature                 | What a reviewer sees                                                                       | Where it lives                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| Issues as a bug tracker | Defects written as bug reports: steps, expected, actual, severity, the test that pins them | Issues tab of each repository; `.github/ISSUE_TEMPLATE/bug_report.yml`                |
| Projects board          | Every defect of the portfolio on one public board, by status                               | [QA defects](https://github.com/users/NailKarimov/projects/2)                         |
| Releases                | A version with a summary of the suite, results and defects                                 | Releases in the sidebar; `.github/releases/<tag>.md`, `.github/workflows/release.yml` |
| Codespaces              | A button that opens the repository with its tools in the browser                           | `.devcontainer/devcontainer.json`, badge in the README                                |
| Social preview          | A card with the numbers when a link is pasted into LinkedIn or Slack                       | Settings → General → Social preview                                                   |

## Issues as a bug tracker

Every defect already has an id, a test that pins it and a row in `docs/test-report.md`. The issue adds the part a
developer reads: a bug report.

- **Title:** `[ID] what is wrong`, for example `[SS-13] BOLA: anyone can read another customer's card and address`.
- **Body:** severity, area, environment; steps to reproduce; expected result with its source (spec, WCAG
  criterion, RFC); actual result; a link to the test line; where the defect is recorded.
- **Labels:** `bug`, `severity: critical | major | minor | trivial`, `area: security | accessibility | …`.
- **Closed issues** are history too: a defect the vendor fixes is closed as completed, a
  sandbox problem (DEF-3…5 on Petstore) is closed as not planned, with the reason in the body.

The issue form `bug_report.yml` asks for the same fields, so a defect reported by hand looks like the generated
ones. Severity measures impact, priority measures order of fixing; the form asks for both.

### Severity scale

| Severity | Meaning                                             | Example                                             |
| -------- | --------------------------------------------------- | --------------------------------------------------- |
| critical | security or data loss, or a core flow is blocked    | full card number and CCV returned by the API (SS-4) |
| major    | a feature is wrong or unusable for a group of users | burger menu unreachable by keyboard (BUG-002)       |
| minor    | wrong, but there is a workaround                    | `Riga, , LV1050` in the address card (UI-TXT-1)     |
| trivial  | cosmetic or wording                                 | "1 Days" (UI-TXT-2)                                 |

## Projects board

[QA defects](https://github.com/users/NailKarimov/projects/2) was created from the Bug tracker template and filled
with the search `is:issue user:NailKarimov label:bug`. Open defects start in _To triage_, closed ones are in _Done_.
The board is public and reads issues from all repositories, so a new defect appears there after it is added to the
project from the issue's sidebar.

## Releases

A release is published by committing its notes:

1. Write `.github/releases/v1.1.0.md`: what the suite covers, the numbers from the latest CI run, the defects.
2. Push to `main`. The `Release` workflow sees the new file, creates the tag `v1.1.0` on that commit and the GitHub
   release with the file as its notes, and marks the newest one as latest.
3. A release that already exists is skipped, so the workflow is safe to re-run; `workflow_dispatch` takes a tag
   for a manual run.

The notes live in git, so they are reviewed like code, and the release needs no personal token: the workflow uses
`GITHUB_TOKEN` with `contents: write`.

## Codespaces

`.devcontainer/devcontainer.json` uses the `universal` image (Node, Python, Java, .NET, Go) with Docker inside, and
runs the install command once when the codespace is created. The README badge opens it with `quickstart=1`, which
reuses an existing codespace. Personal accounts have a free monthly quota; a stopped codespace costs only storage.

Not every suite fits: android-testing needs an Android emulator with hardware acceleration, which Codespaces does
not provide, so it has no devcontainer. microservices-testing asks for a 4-core machine because it starts 13
containers.

## Social preview

GitHub shows a 1280×640 image when a repository link is shared. The cards are generated with Pillow from the same
numbers as the README (tests, defects, mutation score) and uploaded in Settings → General → Social preview.
Regenerate them when the numbers change.

## Demo pull request

[python-testing PR #6](https://github.com/NailKarimov/python-testing/pull/6) is kept open on purpose. It replaces
`quantize(CENT, rounding=ROUND_HALF_UP)` with the built-in `round(value, 2)`: a three-line refactor that passes the
linters and mypy, but `round()` on a `Decimal` rounds half to even. 76 of 77 tests stay green; the Hypothesis test
that compares the service with an independent oracle fails and shrinks the case to two items at 0.01 with the
SAVE25 coupon (discount 0.00 instead of 0.01).

What the reviewer sees without reading any log:

| Place            | What appears                                                                                                                           | How                                                                       |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Checks tab       | red `test` job, a run summary with the verdict and the failing test                                                                    | `scripts/ci_report.py` writes Markdown to `$GITHUB_STEP_SUMMARY`          |
| Checks, run page | an error annotation on the line of the failed test, with the shrunk example (shown in Files changed too when the PR touches that file) | `::error file=…,line=…::` workflow commands                               |
| Conversation     | one CI comment, updated on every push: passed, failed, time, example                                                                   | `gh pr comment`, or a PATCH of the comment marked `<!-- test-summary -->` |

The script reads pytest's `--junitxml` output, so the same step works for any runner that writes JUnit XML
(Playwright, Maven Surefire, `dotnet test --logger junit`). In an interview, one link shows the whole loop:
change, checks, evidence, the decision not to merge.

## Limits

- Issues and the board repeat what `docs/test-report.md` already says. The test report stays the source of truth;
  when a defect changes, update both.
- The Codespaces configuration was not started from this session; the first launch is its test.
- Social preview images and the board settings are made in the browser; there is no file in the repository that
  restores them.

## Sources

- [Issue forms syntax](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)
- [About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)
- [Managing releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Introduction to dev containers](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers)
- [Customizing the social media preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)
