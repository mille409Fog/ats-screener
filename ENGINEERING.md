# Engineering notes

Known issues, found but not yet fixed. Each one is planned as its own commit; remove an
item from this file in the commit that fixes it.

Both reproduce with the bundled samples:

```bash
python -m ats_screener examples/sample_resume.pdf examples/sample_posting.txt
```

## 1. Overlapping spellings count one mention more than once

**Symptom.** In the sample posting, "REST APIs", "CI/CD" and "event-driven" each appear
once, but the report's "Mentions in posting" column shows 2 for each.

**Cause.** `find_terms` (`ats_screener/keywords.py`) collects matches for every spelling of
a term independently, and never removes matches that cover the same text. Any term with
one spelling that is a prefix of another, or with both a hyphenated and a spaced form,
double-counts:

| Term | Spellings that match the same text |
| --- | --- |
| REST APIs | `rest`, `rest apis` |
| CI/CD | `ci`, `ci/cd` |
| Event-driven systems | `event-driven`, `event driven` (spaces in a spelling match hyphens too) |
| React | `react`, `react.js` |
| Python | `python`, `python 3` |
| Spring | `spring`, `spring boot` |
| Claude | `claude`, `claude code` |
| On-call | `on-call`, `on call` |

**Effect.** The count is shown to the user, and it also feeds each term's weight in
`CoverageReport.score` (`1 + min(posting_count, 4) / 4`). So affected terms are weighted too
heavily, and the skills score is skewed. The resume side is unaffected: there it only
matters whether a term appears.

**Proposed fix.** In `find_terms`, keep one match per term for overlapping spans,
preferring the longest. Add a test that "REST APIs" in a posting counts as 1. This changes
reported scores, so regenerate the README example output in the same commit.

## 2. Bullets in the posting are doubled in the report

**Symptom.** The sample report prints
`- - 5+ years of professional experience building backend services in Python`.

**Cause.** `coverage` stores posting lines with their leading bullet (`-`, `•`, `*`)
intact, and `render` (`ats_screener/report.py`) adds its own `- ` in front. Years lines
show this; knockout lines that start with a bullet would show it the same way.

**Effect.** Cosmetic only. Detection and scoring are unaffected.

**Proposed fix.** Strip leading bullet characters and whitespace when storing years and
knockout lines in `coverage`. Add a test with a bulleted years line.
