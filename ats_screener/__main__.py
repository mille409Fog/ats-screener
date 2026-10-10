"""Command line: python -m ats_screener RESUME.pdf POSTING.txt [options]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .keywords import coverage
from .parse import parse_resume
from .report import render
from .screen import DEFAULT_MODEL, build_prompt, can_call_api, run_screen


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ats_screener",
                                 description="Check a resume against a job posting before you apply.")
    ap.add_argument("resume", type=Path, help="resume PDF")
    ap.add_argument("posting", type=Path, help="job posting as a .txt file")
    ap.add_argument("-o", "--out", type=Path, help="also write the report to this Markdown file")
    ap.add_argument("--llm", action="store_true",
                    help="run the recruiter-style screen with Claude (needs ANTHROPIC_API_KEY and the anthropic package)")
    ap.add_argument("--prompt-out", type=Path,
                    help="write the recruiter-screen prompt to this file, to paste into Claude yourself")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"Claude model for --llm (default {DEFAULT_MODEL})")
    args = ap.parse_args(argv)

    for p in (args.resume, args.posting):
        if not p.exists():
            ap.error(f"file not found: {p}")

    parsed = parse_resume(args.resume)
    posting = args.posting.read_text(encoding="utf-8")
    report = render(parsed, coverage(posting, parsed.text), args.resume.name, args.posting.name)

    prompt = build_prompt(posting, parsed.text)
    if args.llm:
        if can_call_api():
            report += "\n## 4. Recruiter-style screen (Claude)\n\n" + run_screen(prompt, args.model) + "\n"
        else:
            report += ("\n## 4. Recruiter-style screen\n\nSkipped: set ANTHROPIC_API_KEY and "
                       "`pip install anthropic`, or use --prompt-out and paste the prompt into Claude.\n")
    if args.prompt_out:
        args.prompt_out.write_text(prompt, encoding="utf-8")
        report += f"\nRecruiter-screen prompt written to {args.prompt_out}. Paste it into Claude.\n"

    print(report)
    if args.out:
        args.out.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
