from pathlib import Path

import pytest

from ats_screener.keywords import coverage, find_terms, tier_lines
from ats_screener.parse import check_text, parse_resume
from ats_screener.screen import build_prompt

EXAMPLES = Path(__file__).parent.parent / "examples"

RESUME = """AVERY QUILL
Millbrook, OR | 503-555-0142 | avery.quill@example.com | linkedin.com/in/avery-quill-sample
Professional Summary
Senior engineer building TypeScript and React front ends with Python/FastAPI and PostgreSQL on AWS.
Technical Skills
Languages: TypeScript, Python, C#, SQL
Professional Experience
Senior Software Engineer | Example Co | June 2023 – October 2026
Built payment flows and mentored engineers. """ + "Shipped features reliably. " * 30 + """
Education
B.S. Mathematics, 2016
"""


# ---- parse ---------------------------------------------------------------

def test_clean_resume_has_no_problems():
    r = check_text(RESUME)
    assert r.ok, r.problems
    assert r.found["email"] == "avery.quill@example.com"
    assert r.found["phone"] == "503-555-0142"
    assert all(r.sections.values())


def test_flags_nearly_empty_text():
    assert any("words extracted" in p for p in check_text("AVERY QUILL").problems)


def test_flags_control_characters():
    r = check_text(RESUME.replace("|", "\x7f"))
    assert any("Control characters" in p for p in r.problems)


def test_flags_missing_contact_details():
    r = check_text(RESUME.replace("avery.quill@example.com", "").replace("503-555-0142", ""))
    assert any("email" in p for p in r.problems)
    assert any("phone" in p for p in r.problems)


# ---- term matching ---------------------------------------------------------

@pytest.mark.parametrize("text,term,expected", [
    ("Experience with Go services", "Go", True),
    ("we go to great lengths", "Go", False),
    ("JavaScript and TypeScript", "Java", False),
    ("Java and Spring Boot", "Java", True),
    ("Built in C# and .NET", "C#", True),
    ("Built in C# and .NET", ".NET", True),
    ("REST and GraphQL APIs", "REST APIs", True),
    ("get some rest", "REST APIs", False),
    ("backed by Spark Capital", "Spark", False),
    ("pipelines in Apache Spark", "Spark", True),
    ("AWS EKS clusters", "Kubernetes", True),
    ("Node.js services", "Node.js", True),
])
def test_term_matching(text, term, expected):
    assert (term in find_terms(text)) is expected


# ---- tiers -----------------------------------------------------------------

def test_tiers_follow_headings():
    posting = """What we're looking for
5+ years with React
Our Stack
Python, Postgres
Nice to have
Experience with Go
Kafka
Benefits
Health insurance"""
    tiers = dict(tier_lines(posting))
    assert tiers["5+ years with React"] == "required"
    assert tiers["Python, Postgres"] == "stack"
    assert tiers["Experience with Go"] == "nice"
    assert tiers["Kafka"] == "nice"          # a short bullet must not reset the section
    assert tiers["Health insurance"] == "skip"     # benefits are the company's side, not requirements


def test_inline_nice_marker():
    tiers = dict(tier_lines("Requirements\nExperience with Vercel (Nice to have)"))
    assert tiers["Experience with Vercel (Nice to have)"] == "nice"


# ---- coverage --------------------------------------------------------------

def test_coverage_scores_and_reports_missing_terms():
    posting = "Requirements\n5+ years of TypeScript and React\nExperience with Kafka\nSalary: $150,000 - $180,000"
    cov = coverage(posting, RESUME)
    by_term = {h.term: h for h in cov.hits}
    assert by_term["TypeScript"].on_resume and by_term["React"].on_resume
    assert not by_term["Kafka"].on_resume
    assert 0 < cov.score() < 100
    assert cov.years_requirements == ["5+ years of TypeScript and React"]
    assert "Compensation" in cov.knockouts


def test_funding_amount_is_not_a_salary():
    cov = coverage("We raised $325M+ in funding.", RESUME)
    assert "Compensation" not in cov.knockouts


def test_domain_terms_do_not_affect_score():
    base = coverage("Requirements\nReact", RESUME).score()
    with_domain = coverage("Requirements\nReact\nhealthcare healthcare healthcare", RESUME).score()
    assert base == with_domain == 100.0


# ---- screen prompt -----------------------------------------------------------

def test_prompt_contains_inputs_and_forbids_invention():
    p = build_prompt("POSTING TEXT", "RESUME TEXT")
    assert "POSTING TEXT" in p and "RESUME TEXT" in p
    assert "Never suggest inventing" in p


# ---- sample files ----------------------------------------------------------

def test_sample_resume_parses():
    r = parse_resume(EXAMPLES / "sample_resume.pdf")
    assert r.word_count > 400
    assert r.found["email"] and r.found["github"]


def test_perks_and_interview_policy_are_not_requirements():
    posting = """Who You Are
Experience with TypeScript and Node.js
Perks
Technology stipend - $4,000 every 2 years
Life insurance
Our Interview Process & AI
Please refrain from using AI tools during interviews."""
    cov = coverage(posting, RESUME)
    terms = {h.term for h in cov.hits}
    assert "TypeScript" in terms and "Node.js" in terms
    assert "AI coding tools" not in terms and "Insurance" not in terms
    assert cov.years_requirements == []


@pytest.mark.parametrize("line,expected", [
    ("5+ years of production Python", True),
    ("At least 6 years of experience in both front-end and back-end", True),
    ("2-5 years of relevant work experience", True),
    ("$4,000 every 2 years after your start", False),
    ("We've been around for 10 years.", False),
])
def test_years_regex(line, expected):
    from ats_screener.keywords import YEARS_RE
    assert bool(YEARS_RE.search(line)) is expected


def test_plain_language_posting_is_not_scored_as_zero():
    from ats_screener.parse import check_text
    from ats_screener.report import render
    cov = coverage("You care about outcomes and talk to users.", RESUME)
    text = render(check_text(RESUME), cov, "r.pdf", "p.txt")
    assert "not enough terms to score" in text


def test_ai_agents_and_distributed_systems():
    found = find_terms("You know how to build systems with AI agents and have refactored distributed systems.")
    assert "AI agents" in found and "Distributed systems" in found
