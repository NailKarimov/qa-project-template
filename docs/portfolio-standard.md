# Portfolio standard: one layout for every repository

Every test automation repository in the portfolio follows the same layout. A reader who has seen one can find
everything in the next in seconds.

## Files

| File                                    | Required                | What it is                                                                                                                                             |
| --------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `README.md`                             | yes                     | Sections below, in this order                                                                                                                          |
| `LICENSE`                               | yes                     | MIT                                                                                                                                                    |
| `.editorconfig`                         | yes                     | UTF-8, LF, final newline, indentation of the language                                                                                                  |
| `docs/test-plan.md`                     | yes                     | Test plan, ISO/IEC/IEEE 29119-3, short                                                                                                                 |
| `docs/test-report.md`                   | yes                     | Test summary report: latest results, defects, deviations, recommendations                                                                              |
| `docs/<topic>.md`                       | yes                     | One text guide per tool or approach                                                                                                                    |
| `docs/<topic>.html`                     | yes                     | The same guide as an interactive page, published on GitHub Pages                                                                                       |
| `.github/workflows/tests.yml`           | yes                     | Push, pull request, a schedule and manual runs; publishes reports to `gh-pages`                                                                        |
| `.github/ISSUE_TEMPLATE/bug_report.yml` | where defects are found | Issue form for bug reports: severity, priority, environment, steps, expected and actual result, the test that pins it                                  |
| Mutation check                          | yes                     | Bugs planted one at a time, every one must fail the suite: `scripts/mutants.*` where the suite is fast, otherwise a table of planted bugs in the guide |

## README sections

1. **Title and badges:** the repository name; badges for the Tests workflow (and any other workflow) and the
   report on Pages.
   Right under the badges, an **Open online** table: one row per page published on Pages (the report first, then
   the other reports and the interactive guides), each a direct link.
2. **One-paragraph summary:** what is tested, on which system, in which language.
3. **At a glance:** a two-column table:

   | Row                | Content                                                      |
   | ------------------ | ------------------------------------------------------------ |
   | System under test  | the system, and whether it is our own or third-party         |
   | Language and tools | the language, then the main tools                            |
   | Types of testing   | the types of testing covered                                 |
   | Tests              | the number of tests from the latest CI run                   |
   | Test quality       | the mutation result, for example "12/12 planted bugs caught" |
   | Reports            | links to the reports on Pages                                |

4. **What is tested:** a table with the columns Suite, Tool and What it proves.
5. **Findings:** defects and lessons found by the tests, each with its id, and a link to the bug reports in Issues.
6. **Running it:** requirements, then one command block.
7. **Project structure:** a short tree with one line per folder.
8. **Design decisions** (optional): why the suite is built the way it is, when that is not obvious.
9. **CI:** jobs, triggers, and what is published.
10. **Documentation:** a table of every file in `docs/`, the test plan and report first.
11. **Part of a portfolio:** the same closing line in every repository, with links to the profile, the testing
    map and the toolbox.

## Writing

- English, plain sentences, numbers from the latest CI run.
- A defect gets an id and a test (`test.fail()` or `knownDefect()`), and it is listed in `docs/test-report.md`.
- Each defect is also an issue titled `[ID] summary`, labelled `bug`, `severity: …` and `area: …`. A defect fixed by
  the vendor, or one that turned out to be an environment problem, is closed with the reason in a comment.
- The docs table and the visual guides use the same names, so a link from the README never leads to 404.
