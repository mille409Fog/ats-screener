# ats-screener

[![tests](https://github.com/mille409Fog/ats-screener/actions/workflows/tests.yml/badge.svg)](https://github.com/mille409Fog/ats-screener/actions/workflows/tests.yml)

Check a resume against a job posting before you apply, the way an applicant
tracking system (ATS) and a busy recruiter might.

Most applications are filtered before a person reads them. This tool runs the same
kinds of checks so you can fix problems first:

1. **Parse check.** Extracts your PDF's text the way an ATS does and flags anything
   that would trip it up: missing contact details, missing section headings, too few
   dates, garbled or unmappable characters, or a near-empty text layer.
2. **Keyword coverage.** Finds the technologies and practices the posting names,
   sorts them into *required*, *listed tech stack* and *nice to have*, and shows which
   ones your resume covers. Industry words ("healthcare", "payments") are reported
   separately, so a mission statement doesn't skew the score.
3. **Before you submit.** Pulls out years-of-experience lines and the logistics a form
   is likely to ask as knockout questions (sponsorship, location, clearance, salary).
4. **Recruiter-style screen (optional).** A rubric prompt that asks Claude to screen
   the resume like a recruiter would, rating each core requirement Met/Partial/Missing
   with quoted evidence, and suggesting changes **without inventing experience**.

## Install

Requires Python 3.10 or newer. From a clone of this repository:

```bash
pip install -e .             # installs pypdf and the ats-screener command
pip install -e ".[llm]"      # optional: adds anthropic, for --llm
```

## Usage

```bash
ats-screener resume.pdf posting.txt
ats-screener resume.pdf posting.txt -o report.md
ats-screener resume.pdf posting.txt --prompt-out prompt.txt   # paste into Claude
ANTHROPIC_API_KEY=... ats-screener resume.pdf posting.txt --llm
```

`python -m ats_screener` works the same way without installing. Use `--model` to pick
the Claude model for `--llm`.

Save the posting by copying its text into a `.txt` file.

## Example

`examples/` has a fictional posting and a resume for an invented person
(regenerate the PDF with `scripts/make_sample_resume.py`, which needs `reportlab`):

```bash
ats-screener examples/sample_resume.pdf examples/sample_posting.txt
```

Excerpt of the output:

```
## 2. Keyword coverage

**Skills score: 86.1 / 100** (weighted share of the posting's terms that appear on the resume; required terms count double)

### Nice to have

| Term | On resume | Mentions in posting |
| --- | --- | --- |
| Datadog | **missing** | 1 |
| Event-driven systems | **missing** | 1 |
| Kafka | **missing** | 1 |
| Terraform | **missing** | 1 |
```

The report also lists the required and tech-stack terms, the years-of-experience
line, and likely knockout questions (here, the hybrid location and the salary range).

## How the matching works

Terms live in `ats_screener/lexicon.py` as a canonical name and its spellings
("PostgreSQL": postgres, postgresql). Matching is whole-token, so Java doesn't match
JavaScript. Short words that are also ordinary English (Go, Rest, Spring, Next) only
count in their capitalized technical form, and known false friends ("Spark Capital")
are masked. Add terms to the lexicon and they're picked up everywhere.

The score is a relative guide, not a prediction: the weighted share of the posting's
terms that appear on the resume, with required terms counting double.

## Use it honestly

Add a missing keyword only when it's true. If you have the experience under a
different name, use the posting's word for it. Hidden text and keyword stuffing are
detected by modern systems, look like fraud to recruiters, and won't survive an
interview.

## Tests

```bash
pip install -e ".[dev]"
python -m pytest
```

Known issues are tracked in [ENGINEERING.md](ENGINEERING.md).

## Built with

This project was developed with AI assistance (Claude). All code was reviewed and
tested by me.

## License

[MIT](LICENSE) © 2026 Jacob E. Miller
