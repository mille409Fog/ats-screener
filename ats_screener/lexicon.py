"""Skills lexicon: canonical term -> spellings to match.

Matching is case-insensitive. Each spelling is matched as a whole token, so "Go"
does not match "good" and "Java" does not match "JavaScript". Extend freely:
any term you add is picked up from postings and resumes automatically.
"""

LEXICON: dict[str, list[str]] = {
    # Languages
    "TypeScript": ["typescript", "ts"],
    "JavaScript": ["javascript", "js"],
    "Python": ["python", "python 3", "python3"],
    "Java": ["java"],
    "C#": ["c#", "csharp"],
    "F#": ["f#"],
    "Go": ["go", "golang", "go lang"],
    "Rust": ["rust"],
    "Ruby": ["ruby"],
    "Kotlin": ["kotlin"],
    "Swift": ["swift"],
    "Scala": ["scala"],
    "PHP": ["php"],
    "C++": ["c++"],
    "SQL": ["sql"],
    "R": ["r language", "r programming"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    # Frontend
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular"],
    "Vue": ["vue", "vue.js", "vuejs"],
    "Next.js": ["next.js", "nextjs", "next"],
    "Remix": ["remix"],
    "Svelte": ["svelte"],
    "Redux": ["redux"],
    "RxJS": ["rxjs"],
    "Tailwind CSS": ["tailwind", "tailwind css"],
    "React Query": ["react query", "tanstack query"],
    "React Native": ["react native"],
    "iOS": ["ios", "swiftui", "uikit"],
    "Android": ["android", "jetpack compose"],
    "Mobile": ["mobile app", "mobile apps", "mobile application", "mobile applications"],
    "Blazor": ["blazor"],
    "Figma": ["figma"],
    "Accessibility": ["accessibility", "accessible", "a11y", "wcag"],
    "Component library": ["component library", "component libraries", "design system", "design systems"],
    # Backend
    "Node.js": ["node", "node.js", "nodejs"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Rails": ["rails", "ruby on rails"],
    ".NET": [".net", "dotnet", "asp.net", "asp.net core"],
    "Spring": ["spring", "spring boot"],
    "GraphQL": ["graphql"],
    "REST APIs": ["rest", "restful", "rest api", "rest apis"],
    "Microservices": ["microservice", "microservices"],
    "Distributed systems": ["distributed system", "distributed systems"],
    "SQLAlchemy": ["sqlalchemy"],
    "Prisma": ["prisma"],
    "Celery": ["celery"],
    "Event-driven systems": ["event-driven", "event driven"],
    # Data
    "PostgreSQL": ["postgres", "postgresql"],
    "MySQL": ["mysql"],
    "SQL Server": ["sql server", "mssql", "t-sql"],
    "Redis": ["redis"],
    "MongoDB": ["mongodb", "mongo"],
    "NoSQL": ["nosql"],
    "Elasticsearch": ["elasticsearch", "opensearch"],
    "Snowflake": ["snowflake"],
    "Databricks": ["databricks"],
    "Spark": ["spark", "pyspark"],
    "dbt": ["dbt"],
    "Kafka": ["kafka"],
    "ClickHouse": ["clickhouse"],
    "Data pipelines": ["data pipeline", "data pipelines", "etl", "elt"],
    "Data modeling": ["data model", "data models", "data modeling", "data modelling", "schema design"],
    # Cloud & infra
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud", "google cloud platform"],
    "Docker": ["docker", "containerization", "containers"],
    "Kubernetes": ["kubernetes", "k8s", "eks", "aks", "gke"],
    "Terraform": ["terraform"],
    "Infrastructure as code": ["iac", "infrastructure as code", "bicep", "arm templates", "cloudformation"],
    "Temporal": ["temporal"],
    "Istio": ["istio"],
    "Vercel": ["vercel"],
    "CI/CD": ["ci/cd", "ci", "continuous integration", "continuous delivery", "github actions", "gitlab ci"],
    "Git": ["git"],
    "GitLab": ["gitlab"],
    "GitHub": ["github"],
    # Observability & ops
    "Datadog": ["datadog"],
    "Sentry": ["sentry"],
    "PagerDuty": ["pagerduty"],
    "Observability": ["observability", "monitoring"],
    "On-call": ["on-call", "on call"],
    "Feature flags": ["feature flag", "feature flags", "feature flagging", "feature management"],
    "Experimentation": ["a/b test", "a/b tests", "a/b testing", "experimentation", "experiments"],
    "Progressive delivery": ["canary", "canaries", "canary deployment", "canary deployments", "canary releases",
                             "gradual rollout", "gradual rollouts", "progressive delivery", "release gradually"],
    # Testing
    "Automated testing": ["automated tests", "automated testing", "writing tests", "write tests", "test coverage", "unit tests", "unit testing", "integration tests"],
    "Jest": ["jest"],
    "Playwright": ["playwright"],
    "Cypress": ["cypress"],
    "Selenium": ["selenium"],
    "xUnit": ["xunit"],
    "JUnit": ["junit"],
    "pytest": ["pytest"],
    "TDD": ["tdd", "test-driven"],
    # AI
    "AI coding tools": ["ai coding", "ai-assisted", "ai assisted", "ai tools", "coding assistants", "ai coding assistants"],
    "Claude": ["claude", "claude code"],
    "Cursor": ["cursor"],
    "LLMs": ["llm", "llms", "large language model", "large language models"],
    "AI agents": ["agent", "agents", "agentic", "ai agent", "ai agents", "sub-agents", "subagents"],
    "MCP": ["mcp", "model context protocol"],
    # Practice
    "Agile": ["agile", "scrum", "kanban"],
    "Code review": ["code review", "code reviews"],
    "Mentoring": ["mentor", "mentored", "mentoring", "mentorship", "coaching"],
    "Design docs": ["design doc", "design docs", "design documents", "technical design"],
    "System architecture": ["architecture", "system design"],
    "Security": ["security", "secure"],
    "HIPAA": ["hipaa"],
    "Payments": ["payment", "payments", "billing"],
    "Healthcare": ["healthcare", "health care", "clinical"],
    "Insurance": ["insurance", "claims", "payer", "payers"],
}

# Short or ambiguous spellings that also mean ordinary English words. They only
# count when written in their technical casing (e.g. "Go", not "go to").
CASE_SENSITIVE = {"go", "rust", "swift", "spring", "next", "remix", "node", "agent", "agents",
                  "temporal", "cursor", "ci", "ts", "js", "rest", "snowflake", "flask", "celery"}

# Domain / industry words. Reported separately as context signals and left out of
# the skills score: a posting's mission statement can repeat "healthcare" ten times
# without that being a resume keyword.
DOMAIN_TERMS = {"Healthcare", "Insurance", "Payments", "HIPAA", "Security"}

# Phrases that contain a lexicon word but mean something else. Masked before matching.
IGNORE_PHRASES = ["spark capital", "next week", "next month", "next year", "next chapter", "next level",
                  "next frontier", "go-to", "go to market", "go-to-market", "rest of", "at rest"]
