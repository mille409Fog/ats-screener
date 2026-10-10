"""Recruiter-style screen: an LLM reads the posting and resume the way a busy screener would.

No company's private ranking model can be reproduced, but most first passes ask the
same questions: does this person meet the core requirements, is the evidence
visible in a quick read, and is anything a red flag? This module writes that rubric
as a prompt. With the `anthropic` package installed and ANTHROPIC_API_KEY set, it
calls Claude directly; otherwise it prints the prompt so you can paste it into
Claude yourself.
"""
from __future__ import annotations

import os

DEFAULT_MODEL = "claude-sonnet-5-5"

RUBRIC = """You are an experienced technical recruiter doing a first-pass screen. You have about \
30 seconds per resume and a large pile of applicants. Be candid and specific; flattery is useless here.

Using only the job posting and resume below:

1. List the posting's 5 to 8 most important requirements, in order of importance.
2. For each one, rate the resume Met, Partial, or Missing, and quote the resume text that \
supports your rating (or say "no evidence").
3. Give an overall decision: Advance, Maybe, or Reject, with one sentence of reasoning \
and your confidence (low/medium/high).
4. Name anything that would make you hesitate: unclear claims, gaps, mismatched seniority, \
or keywords a search would miss because the resume uses different words.
5. Suggest the 3 changes that would most improve this resume's chances for THIS posting. \
Use only facts already on the resume, or phrase the suggestion as a question for the candidate \
("If you have done X, say so"). Never suggest inventing or exaggerating experience.

<job_posting>
{posting}
</job_posting>

<resume>
{resume}
</resume>"""


def build_prompt(posting: str, resume_text: str) -> str:
    return RUBRIC.format(posting=posting.strip(), resume=resume_text.strip())


def can_call_api() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def run_screen(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 2000) -> str:
    import anthropic

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in message.content if block.type == "text")
