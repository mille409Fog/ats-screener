"""Keyword coverage: which of the posting's terms appear on your resume.

Recruiters search an ATS by keyword, and AI rankers weigh how well a resume's
language lines up with the posting's. This module finds the posting's terms,
sorts them into required and nice-to-have, and reports which ones your resume
covers. It also surfaces years-of-experience requirements and the logistics a
form is likely to ask about (knockout questions).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .lexicon import CASE_SENSITIVE, DOMAIN_TERMS, IGNORE_PHRASES, LEXICON

STACK_MARKERS = ("our stack", "tech stack", "technology", "technologies", "tools we use", "our tools")
# Sections that describe the company's side of the deal, not the candidate. Their words
# ("life insurance", "every 2 years", "please don't use AI tools in interviews") are not
# requirements, so they are skipped for keywords and years. Knockouts still scan everything.
SKIP_MARKERS = ("perks", "benefits", "pay:", "pay ranges", "what we offer", "what you'll get", "what you’ll get", "interview process",
                "pay transparency", "compensation", "salary", "equal opportunity", "eeo", "important notice",
                "how we reward", "why you'll love", "why you’ll love", "our values", "diversity")
NICE_MARKERS = ("nice to have", "nice-to-have", "bonus", "a plus", "preferred", "plus if", "not required")
REQUIRED_MARKERS = ("requirement", "required", "must have", "what we're looking for", "what we’re looking for",
                    "who you are", "about you", "qualifications", "you have", "what you've done", "what you’ve done")

KNOCKOUT_PATTERNS = {
    "Work authorization / sponsorship": r"\b(visa|sponsor\w*|work authori[sz]ation|e-verify)\b",
    "Security clearance": r"\bclearance\b",
    "Export control (EAR/ITAR, usually U.S. person)": r"\b(itar|ear/itar|export[- ]controlled|u\.?s\.? person)\b",
    "Location / on-site": r"\b(on-?site|hybrid|in[- ]office|office days|relocat\w*|reside|must live|approved locations?)\b",
    "Travel": r"\btravel\b",
    "Compensation": r"(\$\s?\d{2,3}(?:,\d{3}|k)\b|\bsalary\b|\bpay range\b|\bbase pay\b|\bon-target earnings\b)",
}

YEARS_RE = re.compile(
    r"\b\d{1,2}\s*\+\s*years?\b"                                    # "5+ years"
    r"|\b\d{1,2}(?:\s*(?:-|to)\s*\d{1,2})?\s*years?\s+(?:of|in|with|experience|professional|hands-on|industry)\b"
    r"|\bminimum of \d{1,2} years?\b|\bat least \d{1,2} years?\b",
    re.I,
)


@dataclass
class TermHit:
    term: str
    tier: str               # "required", "stack" (listed tech stack) or "nice"; "skip" lines are ignored
    domain: bool            # industry/context word, excluded from the score
    posting_count: int
    on_resume: bool
    resume_context: str | None = None


@dataclass
class CoverageReport:
    hits: list[TermHit] = field(default_factory=list)
    years_requirements: list[str] = field(default_factory=list)
    knockouts: dict[str, list[str]] = field(default_factory=dict)

    def tier(self, tier: str) -> list[TermHit]:
        return [h for h in self.hits if h.tier == tier and not h.domain]

    def domain(self) -> list[TermHit]:
        return [h for h in self.hits if h.domain]

    def scored_terms(self) -> int:
        return sum(1 for h in self.hits if not h.domain)

    def score(self) -> float:
        """Weighted coverage, 0-100. Required terms count double; frequent terms count more."""
        total = covered = 0.0
        for h in self.hits:
            if h.domain:
                continue
            w = (2.0 if h.tier == "required" else 1.0) * (1 + min(h.posting_count, 4) / 4)
            total += w
            covered += w if h.on_resume else 0
        return round(100 * covered / total, 1) if total else 0.0


def _pattern(spelling: str) -> re.Pattern[str]:
    body = re.escape(spelling).replace(r"\ ", r"[\s-]+")
    return re.compile(rf"(?<![\w#+.\-/]){body}(?![\w#+])", re.I)


_COMPILED = {term: [(s, _pattern(s)) for s in spellings] for term, spellings in LEXICON.items()}


def find_terms(text: str) -> dict[str, list[re.Match[str]]]:
    """Return {canonical term: [matches]} for every lexicon term present in text."""
    found: dict[str, list[re.Match[str]]] = {}
    for phrase in IGNORE_PHRASES:  # mask false friends, keeping offsets intact
        text = re.sub(re.escape(phrase), lambda m: " " * len(m.group(0)), text, flags=re.I)
    for term, patterns in _COMPILED.items():
        matches = []
        for spelling, rx in patterns:
            for m in rx.finditer(text):
                if spelling in CASE_SENSITIVE and not m.group(0)[0].isupper():
                    continue  # "go to the store" is not Go
                matches.append(m)
        if matches:
            found[term] = _drop_overlaps(matches)
    return found


def _drop_overlaps(matches: list[re.Match[str]]) -> list[re.Match[str]]:
    """Keep one match per stretch of text, preferring the longest ("rest apis" over "rest")."""
    kept: list[re.Match[str]] = []
    for m in sorted(matches, key=lambda m: (m.start() - m.end(), m.start())):
        if all(m.end() <= k.start() or m.start() >= k.end() for k in kept):
            kept.append(m)
    return sorted(kept, key=lambda m: m.start())


def _is_heading(line: str) -> bool:
    """Short, label-like lines: no sentence punctuation, no numbers or prices, few words."""
    s = line.strip().rstrip(":")
    return (0 < len(s) <= 50 and len(s.split()) <= 6 and not s.endswith((".", ",", ";"))
            and not re.search(r"[\d$]", s) and not s.startswith(("-", "•", "*")))


# Headings that start a new, non-optional section (so a preceding "Nice to have" block ends).
SECTION_RESET_MARKERS = REQUIRED_MARKERS + ("about", "the role", "responsibilities", "what you'll do",
                                            "what you’ll do", "location", "why ", "how we",
                                            "the position", "the work", "position")


def tier_lines(posting: str) -> list[tuple[str, str]]:
    """Label each posting line 'required', 'stack' or 'nice'.

    A heading containing a nice-to-have marker switches to 'nice'; a heading that
    clearly starts another section switches back. Other short lines (often bullet
    items) leave the current section alone. Inline markers ("... is a plus") make
    just that line 'nice'.
    """
    current = "required"
    out = []
    for line in posting.splitlines():
        low = line.lower().strip()
        if _is_heading(line):
            if any(m in low for m in SKIP_MARKERS):
                current = "skip"
            elif any(m in low for m in NICE_MARKERS):
                current = "nice"
            elif any(m in low for m in STACK_MARKERS):
                current = "stack"
            elif any(low.startswith(m) or m in low for m in SECTION_RESET_MARKERS):
                current = "required"
        line_tier = "nice" if current != "skip" and any(m in low for m in NICE_MARKERS) else current
        out.append((line, line_tier))
    return out


def _context(text: str, m: re.Match[str], width: int = 50) -> str:
    start, end = max(0, m.start() - width), min(len(text), m.end() + width)
    return " ".join(text[start:end].split())


def coverage(posting: str, resume: str) -> CoverageReport:
    report = CoverageReport()

    term_tier: dict[str, str] = {}
    term_count: dict[str, int] = {}
    tiered = tier_lines(posting)
    for line, tier in tiered:
        if tier == "skip":
            continue
        for term, matches in find_terms(line).items():
            term_count[term] = term_count.get(term, 0) + len(matches)
            rank = {"required": 0, "stack": 1, "nice": 2}
            if term not in term_tier or rank[tier] < rank[term_tier[term]]:  # strongest mention wins
                term_tier[term] = tier

    resume_terms = find_terms(resume)
    order = {"required": 0, "stack": 1, "nice": 2}
    for term in sorted(term_tier, key=lambda t: (order[term_tier[t]], -term_count[t], t)):
        m = resume_terms.get(term)
        report.hits.append(TermHit(term, term_tier[term], term in DOMAIN_TERMS, term_count[term], bool(m),
                                   _context(resume, m[0]) if m else None))

    for line, tier in tiered:
        if tier != "skip" and YEARS_RE.search(line) and len(line.strip()) < 300:
            report.years_requirements.append(" ".join(line.split()))

    for label, rx in KNOCKOUT_PATTERNS.items():
        lines = [" ".join(l.split()) for l in posting.splitlines() if re.search(rx, l, re.I)]
        if lines:
            report.knockouts[label] = [l[:220] for l in lines[:3]]

    return report
