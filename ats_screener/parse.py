"""Parse check: read a resume the way an applicant tracking system (ATS) would.

An ATS converts your PDF to plain text before anything else happens. If that
text is garbled, out of order, or missing your contact details, every later
step (keyword search, AI ranking, a recruiter's skim) works from bad data.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w-]+", re.I)
GITHUB_RE = re.compile(r"github\.com/[\w-]+", re.I)
DATE_RE = re.compile(
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b"
    r"|\b\d{1,2}/\d{4}\b|\b(?:19|20)\d{2}\s*[–-]\s*(?:(?:19|20)\d{2}|Present)\b",
    re.I,
)

# Section headings an ATS looks for. Each entry: canonical name -> accepted spellings.
SECTIONS = {
    "experience": ["experience", "employment", "work history"],
    "education": ["education"],
    "skills": ["skills", "technical skills"],
}

# Characters that usually mean the PDF's text layer is broken.
SUSPECT_CHARS = {"�": "replacement character", "ﬁ": "fi ligature", "ﬂ": "fl ligature"}


@dataclass
class ParseReport:
    text: str
    page_count: int
    word_count: int
    found: dict[str, str | None] = field(default_factory=dict)
    sections: dict[str, bool] = field(default_factory=dict)
    date_count: int = 0
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems


def extract_text(pdf_path: str | Path) -> tuple[str, int]:
    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages), len(pages)


def check_text(text: str, page_count: int = 1) -> ParseReport:
    words = re.findall(r"\w+", text)
    report = ParseReport(text=text, page_count=page_count, word_count=len(words))

    if len(words) < 100:
        report.problems.append(
            f"Only {len(words)} words extracted. The PDF may be an image or have no text layer; "
            "an ATS would see an almost empty resume."
        )

    for ch, name in SUSPECT_CHARS.items():
        if ch in text:
            report.problems.append(f"Found a {name} ({ch!r}); some words may not match keyword searches.")

    controls = sorted({c for c in text if (ord(c) < 32 and c not in "\n\t\r") or 127 <= ord(c) < 160})
    if controls:
        shown = ", ".join(repr(c) for c in controls)
        report.problems.append(
            f"Control characters in the extracted text ({shown}); usually a symbol such as a bullet "
            "the parser couldn't map. Consider plain separators like '|' in those spots."
        )

    for label, rx in [("email", EMAIL_RE), ("phone", PHONE_RE), ("linkedin", LINKEDIN_RE), ("github", GITHUB_RE)]:
        m = rx.search(text)
        report.found[label] = m.group(0) if m else None
    for required in ("email", "phone"):
        if not report.found[required]:
            report.problems.append(f"No {required} detected in the extracted text.")

    lowered = text.lower()
    for name, spellings in SECTIONS.items():
        present = any(re.search(rf"^\s*[\w &]*{re.escape(s)}[\w &]*\s*$", lowered, re.M) for s in spellings)
        report.sections[name] = present
        if not present:
            report.problems.append(f"No '{name}' section heading found; some parsers file your content under the wrong field.")

    report.date_count = len(DATE_RE.findall(text))
    if report.date_count < 2:
        report.problems.append("Few or no recognizable dates; ATS tools use them to compute years of experience.")

    if page_count > 2:
        report.problems.append(f"{page_count} pages; most recruiters expect one or two.")

    return report


def parse_resume(pdf_path: str | Path) -> ParseReport:
    text, pages = extract_text(pdf_path)
    return check_text(text, pages)
