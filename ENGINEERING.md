# Engineering notes

Known issues, found but not yet fixed. Each one is planned as its own commit; remove an
item from this file in the commit that fixes it.

Reproduces with the bundled samples:

```bash
python -m ats_screener examples/sample_resume.pdf examples/sample_posting.txt
```

## 1. Bullets in the posting are doubled in the report

**Symptom.** The sample report prints
`- - 5+ years of professional experience building backend services in Python`.

**Cause.** `coverage` stores posting lines with their leading bullet (`-`, `•`, `*`)
intact, and `render` (`ats_screener/report.py`) adds its own `- ` in front. Years lines
show this; knockout lines that start with a bullet would show it the same way.

**Effect.** Cosmetic only. Detection and scoring are unaffected.

**Proposed fix.** Strip leading bullet characters and whitespace when storing years and
knockout lines in `coverage`. Add a test with a bulleted years line.
