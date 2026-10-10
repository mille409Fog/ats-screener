"""Build examples/sample_resume.pdf: a resume for an invented person, used as sample data.

Avery Quill does not exist. The phone number is in the 555-01xx range reserved for
fiction, and the email uses the reserved example.com domain. The resume deliberately
covers some of examples/sample_posting.txt and misses some (Kafka, Terraform, Datadog),
so the report has something to show.

    pip install reportlab
    python scripts/make_sample_resume.py

reportlab is only needed to regenerate the PDF, so it is not a project dependency.
"""
from __future__ import annotations

from pathlib import Path

from reportlab import rl_config
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

rl_config.invariant = 1  # no timestamps or random IDs, so rebuilding gives identical bytes

OUT = Path(__file__).resolve().parent.parent / "examples" / "sample_resume.pdf"

NAME = "Avery Quill"
CONTACT = ("Millbrook, OR | (503) 555-0142 | avery.quill@example.com | "
           "linkedin.com/in/avery-quill-sample | github.com/avery-quill-sample")

SUMMARY = (
    "Backend engineer with seven years of experience building Python services and REST APIs "
    "for logistics and retail teams. Comfortable owning a feature from the database schema to "
    "the deployment pipeline, and happiest on small teams that write things down."
)

SKILLS = [
    "Languages: Python, SQL, TypeScript",
    "Frameworks: FastAPI, Django, React",
    "Data: PostgreSQL, Redis, data modeling, query tuning",
    "Infrastructure: Docker, AWS (ECS, RDS, S3), GitHub Actions for CI/CD",
    "Practices: automated testing with pytest, code review, design docs, mentoring",
]

EXPERIENCE = [
    ("Senior Software Engineer | Lumen Parcel Co. (fictional) | March 2021 - Present", [
        "Designed and maintained the REST APIs behind a dispatch dashboard used by forty "
        "dispatchers across three warehouses, built with FastAPI and PostgreSQL.",
        "Cut the median response time of the route lookup endpoint from 900 ms to 120 ms by "
        "adding a Redis cache and rewriting two queries after reading their plans.",
        "Introduced design docs for every change larger than a week of work, and reviewed "
        "most backend pull requests on a team of six.",
        "Mentored two junior engineers through their first on-call rotations and their first "
        "production database migrations.",
        "Moved the test suite from a nightly job into GitHub Actions so every pull request "
        "runs pytest against a real PostgreSQL container in Docker.",
        "Led the move of three services from hand-managed servers to AWS ECS, writing the "
        "runbook and the rollback plan before the first cutover.",
    ]),
    ("Software Engineer | Copperleaf Outfitters (fictional) | June 2018 - February 2021", [
        "Built order and inventory services in Django for an online outdoor gear shop, "
        "handling seasonal peaks of several thousand orders a day.",
        "Wrote the data model and migrations for a returns workflow that replaced a shared "
        "spreadsheet, and documented it for the support team.",
        "Added automated tests around the checkout path, raising coverage of that module from "
        "roughly a third to over ninety percent.",
        "Worked with the frontend team on a small React and TypeScript admin tool for "
        "adjusting stock counts.",
        "Joined the on-call rotation in my second year and wrote alerts that paged on failed "
        "payments rather than on every slow request.",
    ]),
    ("Junior Developer | Riverbend Print Shop (fictional) | July 2017 - May 2018", [
        "Maintained internal Python scripts that turned customer orders into print jobs, and "
        "replaced the riskiest of them with a small tested web service.",
        "Kept the shop's order database backed up and documented, and answered the phone when "
        "a print job went wrong, which taught me more about error messages than any course.",
    ]),
]

EDUCATION = "B.S. Computer Science | Millbrook State University (fictional) | 2017"


def build(out: Path = OUT) -> Path:
    styles = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9.5, leading=12, spaceBefore=0, spaceAfter=2)
    heading = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=12, spaceBefore=8, spaceAfter=3)
    doc = SimpleDocTemplate(str(out), pagesize=LETTER, title=f"{NAME} - Sample Resume",
                            author="ats-screener sample data", leftMargin=0.7 * inch,
                            rightMargin=0.7 * inch, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    story = [Paragraph(NAME, styles["Title"]), Paragraph(CONTACT, body), Spacer(1, 6),
             Paragraph("Summary", heading), Paragraph(SUMMARY, body),
             Paragraph("Skills", heading)]
    story += [Paragraph(line, body) for line in SKILLS]
    story.append(Paragraph("Experience", heading))
    for title, bullets in EXPERIENCE:
        story.append(Paragraph(f"<b>{title}</b>", body))
        story += [Paragraph(f"- {b}", body) for b in bullets]
    story += [Paragraph("Education", heading), Paragraph(EDUCATION, body)]
    doc.build(story)
    return out


if __name__ == "__main__":
    print(f"Wrote {build()}")
