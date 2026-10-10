"""Render the checks as a Markdown report."""
from __future__ import annotations

from .keywords import CoverageReport
from .parse import ParseReport

TIER_TITLES = {
    "required": "Required (from the posting's requirements and duties)",
    "stack": "Listed tech stack (context, weighted like nice-to-have)",
    "nice": "Nice to have",
}


def render(parse: ParseReport, cov: CoverageReport, resume_name: str, posting_name: str) -> str:
    out: list[str] = [f"# Screening report: {resume_name} vs {posting_name}", ""]

    out += ["## 1. Parse check", ""]
    out.append(f"{parse.page_count} page(s), {parse.word_count} words extracted.")
    found = ", ".join(f"{k}: {v or 'NOT FOUND'}" for k, v in parse.found.items())
    out.append(f"Contact details: {found}.")
    if parse.ok:
        out.append("No parsing problems found.")
    else:
        out += ["", "Problems:"] + [f"- {p}" for p in parse.problems]
    out.append("")

    out += ["## 2. Keyword coverage", ""]
    if cov.scored_terms() < 3:
        out += [f"**Skills score: not enough terms to score** (only {cov.scored_terms()} recognized technology or "
                "practice term(s) in the posting). This posting is written in plain language; judge fit by reading it, "
                "or run the recruiter-style screen.", ""]
    else:
        out += [f"**Skills score: {cov.score()} / 100** "
                "(weighted share of the posting's terms that appear on the resume; required terms count double)", ""]
    for tier, title in TIER_TITLES.items():
        hits = cov.tier(tier)
        if not hits:
            continue
        out += [f"### {title}", "", "| Term | On resume | Mentions in posting |", "| --- | --- | --- |"]
        out += [f"| {h.term} | {'yes' if h.on_resume else '**missing**'} | {h.posting_count} |" for h in hits]
        out.append("")

    if cov.domain():
        out += ["### Domain signals (not scored)", ""]
        out += [f"- {h.term}: {'appears' if h.on_resume else 'not on resume'} "
                f"({h.posting_count} mention(s) in posting)" for h in cov.domain()]
        out.append("")

    missing = [h.term for h in cov.tier("required") if not h.on_resume]
    if missing:
        out += ["**Missing required terms:** " + ", ".join(missing) + ". "
                "Add one only if it is true; if you have the experience under a different name, "
                "use the posting's word for it.", ""]

    out += ["## 3. Before you submit", ""]
    if cov.years_requirements:
        out += ["Years-of-experience lines (forms often ask these as number fields):", ""]
        out += [f"- {y}" for y in cov.years_requirements]
        out.append("")
    if cov.knockouts:
        out += ["Likely knockout questions on the form; answer these carefully:", ""]
        for label, lines in cov.knockouts.items():
            out.append(f"- **{label}:** " + " / ".join(f"\"{l}\"" for l in lines))
        out.append("")
    if not cov.years_requirements and not cov.knockouts:
        out += ["No explicit years or logistics requirements detected.", ""]
    return "\n".join(out)
