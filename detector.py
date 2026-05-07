"""
claude-code-adaptive-skills — detector.py
==========================================
Scans a project folder, detects the tech stack, discovers which Claude Code
skills, agents, and commands are actually installed, and writes a tailored
CLAUDE.md that activates the right skills and agents for the project.

The CLAUDE.md includes a Dynamic Skill Selection Guide so Claude Code picks
the right skills, agents, and slash commands automatically based on what the
user is asking for — not just the project stack. No user intervention required.

Usage:
    python detector.py [project_path] [--claude-dir PATH] [--dry-run] [--force]

Flags:
    --dry-run     Print the generated CLAUDE.md without writing it
    --force       Overwrite even a manually-edited CLAUDE.md
    --claude-dir  Path to ~/.claude (default: auto-detected)
"""

import json
import os
import sys
from pathlib import Path

VERSION = "4.0.0"
MARKER = "<!-- claude-code-adaptive-skills -->"
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB limit to prevent memory exhaustion

# ── Stack → skills (which skills are relevant for each detected stack key) ────
SKILL_MAP: dict[str, list[str]] = {
    "python": ["python-pro", "python-patterns", "python-testing"],
    "nodejs": ["javascript-pro"],
    "typescript": ["typescript-pro"],
    "rust": ["rust-patterns", "rust-testing"],
    "go": ["golang-patterns", "golang-testing"],
    "cpp": ["cpp-coding-standards", "cpp-testing"],
    "java": ["java-coding-standards"],
    "kotlin": ["kotlin-patterns", "kotlin-testing"],
    "dart": ["dart-flutter-patterns"],
    "csharp": ["dotnet-patterns", "csharp-testing"],
    "php": ["laravel-patterns"],
    "flask": ["python-pro", "backend-patterns"],
    "fastapi": ["fastapi-expert", "python-pro"],
    "django": ["django-patterns", "django-tdd"],
    "react": ["react-expert", "frontend-patterns"],
    "nextjs": ["nextjs-developer", "react-expert"],
    "vue": ["frontend-patterns"],
    "express": ["backend-patterns"],
    "nestjs": ["nestjs-expert", "nestjs-patterns"],
    "springboot": ["springboot-patterns", "springboot-tdd"],
    "ktor": ["kotlin-patterns"],
    "laravel": ["laravel-patterns"],
    "flutter": ["dart-flutter-patterns"],
    "pytorch": ["python-pro"],
    "tensorflow": ["python-pro"],
    "huggingface": ["python-pro"],
    "llm-api": ["python-pro", "claude-api", "mcp-server-patterns"],
    "data-science": ["python-pro", "python-patterns"],
    "vector-db": ["python-pro", "backend-patterns"],
    "ai-ml-generic": ["python-pro"],
    "mcp": ["mcp-server-patterns", "mcp-builder"],
    "android": ["android-clean-architecture"],
    "fullstack": ["fullstack-guardian"],
    "tdd": ["tdd-workflow"],
    "e2e": ["e2e-testing"],
    "api-design": ["api-design"],
}

# ── Stack → agents ─────────────────────────────────────────────────────────────
AGENT_MAP: dict[str, list[str]] = {
    "python": ["python-reviewer", "build-error-resolver"],
    "nodejs": ["build-error-resolver", "typescript-reviewer"],
    "typescript": ["typescript-reviewer"],
    "react": ["build-error-resolver", "typescript-reviewer", "frontend-developer"],
    "pytorch": ["pytorch-build-resolver", "python-reviewer"],
    "rust": ["rust-build-resolver", "rust-reviewer"],
    "go": ["go-build-resolver", "go-reviewer"],
    "java": ["java-build-resolver", "java-reviewer"],
    "kotlin": ["kotlin-build-resolver", "kotlin-reviewer"],
    "cpp": ["build-error-resolver"],
    "dart": ["flutter-reviewer"],
    "fullstack": ["code-reviewer", "performance-optimizer"],
    "tdd": ["tdd-guide", "pr-test-analyzer", "tdd-orchestrator"],
    "fastapi": ["fastapi-pro", "python-reviewer"],
    "django": ["django-pro", "python-reviewer"],
    "nextjs": ["typescript-reviewer", "frontend-developer"],
    "llm-api": ["loop-operator"],
    "mcp": ["dx-optimizer"],
}

# ── Intent → skills / agents / commands ───────────────────────────────────────
# The complete routing guide. Claude Code reads this and picks skills/agents/
# commands automatically based on the user's task intent (keywords/triggers).
# All entries reference real installed resources — the guide only outputs those
# that are actually present on the machine.
INTENT_MAP: dict[str, dict] = {
    # ── Frontend / UI ──────────────────────────────────────────────────────────
    "frontend": {
        "label": "Frontend / UI / Styling / Components / Design",
        "triggers": (
            "frontend, UI, styling, CSS, layout, design, component, animation, "
            "responsive, theme, colour, color, button, navbar, hero, landing page, "
            "improve the look, redesign, visual, Tailwind, SCSS, styled-components, "
            "Figma, wireframe, mockup, prototype, interface"
        ),
        "skills": [
            "react-expert",
            "nextjs-developer",
            "frontend-patterns",
            "typescript-pro",
            "javascript-pro",
            "frontend-design",
            "web-design-guidelines",
            "distinctive-frontend",
            "senior-frontend",
            "ui-design-system",
            "ux-researcher-designer",
            "frontend-slides",
        ],
        "agents": [
            "typescript-reviewer",
            "performance-optimizer",
            "frontend-developer",
            "a11y-architect",
            "ui-visual-validator",
            "type-design-analyzer",
        ],
        "commands": [
            "accessibility-audit",
            "code-review",
            "performance-optimization",
        ],
    },
    # ── Backend / API ──────────────────────────────────────────────────────────
    "backend": {
        "label": "Backend / API / Server / Routes / Business Logic",
        "triggers": (
            "backend, API, server, route, endpoint, controller, middleware, REST, "
            "GraphQL, authentication, authorization, login, session, service, "
            "microservice, handler, request, response, webhook, RPC, gRPC"
        ),
        "skills": [
            "fastapi-expert",
            "python-pro",
            "backend-patterns",
            "django-patterns",
            "nestjs-expert",
            "nestjs-patterns",
            "springboot-patterns",
            "api-design",
            "golang-patterns",
            "rust-patterns",
            "laravel-patterns",
            "senior-backend",
            "python-patterns",
        ],
        "agents": [
            "python-reviewer",
            "build-error-resolver",
            "fastapi-pro",
            "django-pro",
            "backend-architect",
            "graphql-architect",
            "sql-pro",
        ],
        "commands": [
            "code-review",
            "api-mock",
            "python-review",
            "feature-dev",
        ],
    },
    # ── Database ───────────────────────────────────────────────────────────────
    "database": {
        "label": "Database / ORM / Queries / Schema / Migrations",
        "triggers": (
            "database, DB, SQL, ORM, query, migration, schema, model, table, index, "
            "relation, join, Prisma, SQLAlchemy, TypeORM, Mongoose, PostgreSQL, "
            "MySQL, SQLite, MongoDB, Redis, Cassandra, DynamoDB, supabase"
        ),
        "skills": [
            "backend-patterns",
            "python-patterns",
            "python-pro",
        ],
        "agents": [
            "database-architect",
            "database-optimizer",
            "database-reviewer",
            "database-admin",
            "sql-pro",
            "data-engineer",
        ],
        "commands": [
            "code-review",
        ],
    },
    # ── Testing / TDD ──────────────────────────────────────────────────────────
    "testing": {
        "label": "Testing / TDD / Unit Tests / E2E / Coverage",
        "triggers": (
            "test, TDD, unit test, integration test, e2e, end-to-end, coverage, "
            "mock, stub, fixture, spec, assert, pytest, Jest, Vitest, Playwright, "
            "Cypress, Selenium, test suite, write tests, add tests, failing test"
        ),
        "skills": [
            "tdd-workflow",
            "e2e-testing",
            "python-testing",
            "golang-testing",
            "rust-testing",
            "cpp-testing",
            "csharp-testing",
            "kotlin-testing",
            "django-tdd",
            "springboot-tdd",
            "python-patterns",
        ],
        "agents": [
            "tdd-guide",
            "pr-test-analyzer",
            "tdd-orchestrator",
            "test-automator",
            "e2e-runner",
        ],
        "commands": [
            "tdd",
            "e2e",
            "test-coverage",
            "quality-gate",
            "verify",
        ],
    },
    # ── Performance / Optimisation ─────────────────────────────────────────────
    "performance": {
        "label": "Performance / Optimisation / Speed / Bundle Size / Profiling",
        "triggers": (
            "performance, optimise, optimize, slow, speed, loading, bundle size, "
            "memory leak, cache, lazy load, profiling, benchmark, throughput, "
            "latency, bottleneck, time complexity, big-O, Core Web Vitals"
        ),
        "skills": [
            "python-patterns",
            "frontend-patterns",
            "golang-patterns",
            "rust-patterns",
            "backend-patterns",
        ],
        "agents": [
            "performance-optimizer",
            "performance-engineer",
            "observability-engineer",
            "silent-failure-hunter",
        ],
        "commands": [
            "performance-optimization",
        ],
    },
    # ── Security ───────────────────────────────────────────────────────────────
    "security": {
        "label": "Security / Auth / Vulnerabilities / Secrets / OWASP",
        "triggers": (
            "security, vulnerability, auth, authentication, JWT, OAuth, CSRF, XSS, "
            "SQL injection, secrets, .env, encryption, HTTPS, CORS, sanitize, "
            "penetration, OWASP, CVE, dependency audit, rate limit, brute force"
        ),
        "skills": [
            "python-patterns",
            "backend-patterns",
            "coding-standards",
        ],
        "agents": [
            "security-auditor",
            "security-reviewer",
            "backend-security-coder",
        ],
        "commands": [
            "deps-audit",
            "code-review",
        ],
    },
    # ── AI / LLM / Agents ──────────────────────────────────────────────────────
    "ai_llm": {
        "label": "AI / LLM / Prompts / Agents / RAG / Embeddings / MCP",
        "triggers": (
            "AI, LLM, prompt, Claude, OpenAI, GPT, Gemini, embedding, RAG, "
            "vector, agent, tool call, function calling, memory, chat, streaming, "
            "fine-tune, inference, model, chain, workflow, orchestrate, multi-agent, "
            "MCP, tool server, context, system prompt, langchain, llamaindex"
        ),
        "skills": [
            "claude-api",
            "python-pro",
            "mcp-server-patterns",
            "python-patterns",
            "mcp-builder",
            "agent-introspection-debugging",
        ],
        "agents": [
            "python-reviewer",
            "loop-operator",
            "dx-optimizer",
        ],
        "commands": [
            "prompt-optimize",
            "multi-agent-optimize",
            "loop-start",
            "loop-status",
            "orchestrate",
            "model-route",
            "agent-sort",
            "improve-agent",
        ],
    },
    # ── DevOps / Infrastructure ────────────────────────────────────────────────
    "devops": {
        "label": "DevOps / Docker / CI/CD / Deployment / Infrastructure / Build",
        "triggers": (
            "Docker, container, deploy, deployment, CI/CD, GitHub Actions, "
            "GitLab CI, Jenkins, build, pipeline, Kubernetes, k8s, cloud, "
            "AWS, GCP, Azure, environment, production, staging, Terraform, "
            "Ansible, Helm, serverless, Lambda, VM, VPS"
        ),
        "skills": [
            "python-patterns",
            "backend-patterns",
            "golang-patterns",
        ],
        "agents": [
            "build-error-resolver",
            "deployment-engineer",
            "devops-troubleshooter",
            "cloud-architect",
            "kubernetes-architect",
            "terraform-specialist",
            "service-mesh-expert",
            "network-engineer",
            "observability-engineer",
        ],
        "commands": [
            "build-fix",
            "devfleet",
            "pm2",
        ],
    },
    # ── Refactoring / Code Quality ─────────────────────────────────────────────
    "refactor": {
        "label": "Refactoring / Code Quality / Architecture / Patterns / Technical Debt",
        "triggers": (
            "refactor, clean up, restructure, improve code, architecture, patterns, "
            "SOLID, DRY, readability, maintainability, code smell, dead code, "
            "technical debt, simplify, extract, rename, decouple, dependency"
        ),
        "skills": [
            "python-patterns",
            "frontend-patterns",
            "backend-patterns",
            "fullstack-guardian",
            "coding-standards",
            "impeccable",
            "senior-architect",
            "verification-loop",
        ],
        "agents": [
            "code-reviewer",
            "performance-optimizer",
            "refactor-cleaner",
            "code-simplifier",
            "legacy-modernizer",
            "code-architect",
            "architect",
        ],
        "commands": [
            "refactor-clean",
            "code-review",
            "tech-debt",
            "quality-gate",
            "code-explain",
            "rules-distill",
        ],
    },
    # ── Mobile ─────────────────────────────────────────────────────────────────
    "mobile": {
        "label": "Mobile / Flutter / Android / iOS / React Native",
        "triggers": (
            "mobile, Flutter, Android, iOS, widget, screen, navigation, app store, "
            "React Native, Kotlin, Swift, Jetpack Compose, SwiftUI, push notification, "
            "offline, native, APK, IPA"
        ),
        "skills": [
            "dart-flutter-patterns",
            "android-clean-architecture",
            "kotlin-patterns",
            "kotlin-testing",
        ],
        "agents": [
            "flutter-reviewer",
            "kotlin-build-resolver",
            "kotlin-reviewer",
        ],
        "commands": [
            "flutter-build",
            "flutter-review",
            "flutter-test",
            "kotlin-build",
            "kotlin-review",
            "kotlin-test",
        ],
    },
    # ── Documents / Office ─────────────────────────────────────────────────────
    "documents": {
        "label": "Documents / Reports / Word / PDF / Presentations / Spreadsheets",
        "triggers": (
            "document, report, Word, DOCX, PDF, PowerPoint, PPTX, slide, deck, "
            "presentation, spreadsheet, Excel, XLSX, table, memo, letter, proposal, "
            "write a doc, create a report, generate a PDF, make slides, fill form"
        ),
        "skills": [
            "docx",
            "pdf",
            "pptx",
            "xlsx",
            "doc-coauthoring",
        ],
        "agents": [
            "doc-updater",
        ],
        "commands": [
            "doc-generate",
            "update-docs",
        ],
    },
    # ── Visual Design / Art ────────────────────────────────────────────────────
    "visual_design": {
        "label": "Visual Design / Generative Art / GIF / Branding / Themes",
        "triggers": (
            "art, illustration, poster, graphic, generative, algorithmic, p5.js, "
            "canvas, GIF, animated GIF, Slack GIF, brand, branding, theme, colour "
            "palette, style guide, visual identity, logo, banner, background"
        ),
        "skills": [
            "canvas-design",
            "algorithmic-art",
            "slack-gif-creator",
            "theme-factory",
            "brand-guidelines",
        ],
        "agents": [
            "type-design-analyzer",
            "ui-visual-validator",
        ],
        "commands": [],
    },
    # ── Web Artifacts / Interactive UIs ────────────────────────────────────────
    "web_artifacts": {
        "label": "Web Artifacts / Interactive Apps / HTML / React Components",
        "triggers": (
            "HTML artifact, interactive, dashboard, widget, chart, visualization, "
            "web app, single-page, React component, shadcn, Tailwind component, "
            "calculator, form, tool, embed, prototype, live preview"
        ),
        "skills": [
            "web-artifacts-builder",
            "react-expert",
            "frontend-patterns",
            "javascript-pro",
            "typescript-pro",
        ],
        "agents": [
            "frontend-developer",
            "ui-visual-validator",
        ],
        "commands": [],
    },
    # ── MCP / Tool Building ────────────────────────────────────────────────────
    "mcp_tools": {
        "label": "MCP Servers / Claude Tools / Plugin Building / Integrations",
        "triggers": (
            "MCP server, MCP tool, build a tool, Claude plugin, tool definition, "
            "FastMCP, tool server, integration, connector, stdio, SSE, resource, "
            "tool schema, Anthropic SDK, tool_use, build plugin, skill creator"
        ),
        "skills": [
            "mcp-server-patterns",
            "mcp-builder",
            "python-pro",
        ],
        "agents": [
            "dx-optimizer",
        ],
        "commands": [
            "hookify",
            "skill-create",
            "skill-health",
            "improve-agent",
        ],
    },
    # ── Planning / Architecture ─────────────────────────────────────────────────
    "planning": {
        "label": "Planning / Architecture / System Design / Roadmap / PRD",
        "triggers": (
            "plan, planning, architecture, system design, design doc, roadmap, "
            "PRD, spec, proposal, diagram, C4, sequence diagram, ADR, decision, "
            "strategy, approach, breakdown, scaffold, greenfield, start a project"
        ),
        "skills": [
            "senior-architect",
            "fullstack-guardian",
            "coding-standards",
            "api-design",
        ],
        "agents": [
            "architect",
            "planner",
            "business-analyst",
            "chief-of-staff",
            "code-architect",
            "monorepo-architect",
            "backend-architect",
            "cloud-architect",
            "event-sourcing-architect",
        ],
        "commands": [
            "plan",
            "c4-architecture",
            "feature-dev",
            "feature-development",
            "prp-plan",
            "prp-prd",
            "prp-pr",
        ],
    },
    # ── Team Workflows / Multi-Agent ───────────────────────────────────────────
    "team_workflow": {
        "label": "Team Workflows / Multi-Agent / Delegation / Orchestration",
        "triggers": (
            "team, multi-agent, delegate, orchestrate, parallel, spawn, coordinate, "
            "run agents, sub-agent, workflow, pipeline, automate, batch, loop, "
            "concurrent, distribute, hand off, assign task"
        ),
        "skills": [
            "fullstack-guardian",
        ],
        "agents": [
            "team-lead",
            "team-debugger",
            "team-implementer",
            "team-reviewer",
            "chief-of-staff",
            "loop-operator",
            "planner",
        ],
        "commands": [
            "team-debug",
            "team-delegate",
            "team-feature",
            "team-review",
            "team-spawn",
            "team-status",
            "team-shutdown",
            "workflow-automate",
            "multi-backend",
            "multi-frontend",
            "multi-execute",
            "multi-plan",
            "multi-workflow",
            "orchestrate",
            "devfleet",
        ],
    },
    # ── Documentation / Docs Writing ───────────────────────────────────────────
    "documentation": {
        "label": "Documentation / README / API Docs / Tutorials / Changelogs",
        "triggers": (
            "documentation, docs, README, API docs, tutorial, guide, changelog, "
            "write docs, generate docs, update docs, JSDoc, docstring, Swagger, "
            "OpenAPI, Storybook, wiki, knowledge base, how-to"
        ),
        "skills": [
            "doc-coauthoring",
            "coding-standards",
        ],
        "agents": [
            "docs-architect",
            "docs-lookup",
            "doc-updater",
            "tutorial-engineer",
        ],
        "commands": [
            "docs",
            "doc-generate",
            "update-docs",
        ],
    },
    # ── Content / Marketing / SEO ──────────────────────────────────────────────
    "content": {
        "label": "Content / Marketing / SEO / Social Media / Internal Comms",
        "triggers": (
            "content, blog post, article, marketing, SEO, social media, LinkedIn, "
            "email campaign, newsletter, copywriting, announcement, press release, "
            "internal comms, memo, status update, team update"
        ),
        "skills": [
            "internal-comms",
            "linkedin",
        ],
        "agents": [
            "content-marketer",
            "seo-specialist",
            "search-specialist",
        ],
        "commands": [],
    },
    # ── Debugging / Error Resolution ───────────────────────────────────────────
    "debugging": {
        "label": "Debugging / Error Resolution / Bug Fixing / Root Cause Analysis",
        "triggers": (
            "bug, error, exception, crash, broken, fix, debug, traceback, "
            "stack trace, not working, fails, unexpected, regression, "
            "root cause, reproduce, investigate, why is this, help me fix"
        ),
        "skills": [
            "verification-loop",
            "impeccable",
            "python-patterns",
        ],
        "agents": [
            "debugger",
            "build-error-resolver",
            "silent-failure-hunter",
            "team-debugger",
            "devops-troubleshooter",
        ],
        "commands": [
            "build-fix",
            "verify",
            "code-explain",
        ],
    },
    # ── Code Review / PR Review ────────────────────────────────────────────────
    "code_review": {
        "label": "Code Review / PR Review / Quality Gate / Linting",
        "triggers": (
            "review, PR, pull request, code review, check this, feedback, "
            "what do you think, lint, quality, smell, anti-pattern, best practices, "
            "LGTM, suggest improvements, critique"
        ),
        "skills": [
            "coding-standards",
            "impeccable",
            "verification-loop",
        ],
        "agents": [
            "code-reviewer",
            "refactor-cleaner",
            "code-simplifier",
            "pr-test-analyzer",
            "healthcare-reviewer",
        ],
        "commands": [
            "code-review",
            "review-pr",
            "quality-gate",
            "eval",
        ],
    },
    # ── Data / Analytics / ML ──────────────────────────────────────────────────
    "data_ml": {
        "label": "Data Science / Analytics / Machine Learning / Jupyter",
        "triggers": (
            "data, dataset, analytics, machine learning, ML, model training, "
            "Jupyter, notebook, pandas, numpy, matplotlib, seaborn, scikit-learn, "
            "neural network, deep learning, GAN, LSTM, transformer, EDA, pipeline"
        ),
        "skills": [
            "python-pro",
            "python-patterns",
            "python-testing",
        ],
        "agents": [
            "data-engineer",
            "python-reviewer",
            "gan-evaluator",
            "gan-generator",
            "gan-planner",
        ],
        "commands": [
            "python-review",
        ],
    },
}

PROJECT_INDICATORS = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "Pipfile",
    "Cargo.toml",
    "go.mod",
    "Makefile",
    "CMakeLists.txt",
    "build.gradle",
    "pom.xml",
    ".git",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "composer.json",
    "Gemfile",
    "pubspec.yaml",
}


def find_claude_dir() -> "Path | None":
    candidates = [Path.home() / ".claude"]
    for var in ("USERPROFILE", "HOME"):
        val = os.environ.get(var, "").strip()
        if val:
            candidates.append(Path(val) / ".claude")
    for c in candidates:
        if c.is_dir():
            return c
    return None


def discover_skills(claude_dir: Path) -> set:
    skills: set = set()
    skills_dir = claude_dir / "skills"
    if not skills_dir.is_dir():
        return skills
    for item in skills_dir.iterdir():
        if item.is_file() and item.suffix == ".md":
            skills.add(item.stem)
        elif item.is_dir() and (item / "SKILL.md").exists():
            skills.add(item.name)
    return skills


def discover_agents(claude_dir: Path) -> set:
    agents: set = set()
    agents_dir = claude_dir / "agents"
    if not agents_dir.is_dir():
        return agents
    for item in agents_dir.iterdir():
        if item.is_file() and item.suffix == ".md":
            agents.add(item.stem)
    return agents


def discover_commands(claude_dir: Path) -> set:
    """Discover all slash commands installed in ~/.claude/commands/."""
    commands: set = set()
    commands_dir = claude_dir / "commands"
    if not commands_dir.is_dir():
        return commands
    for item in commands_dir.iterdir():
        if item.is_file() and item.suffix == ".md":
            commands.add(item.stem)
    return commands


def discover_rules(claude_dir: Path) -> list:
    rules: list = []
    rules_dir = claude_dir / "rules"
    if not rules_dir.is_dir():
        return rules
    for rule_file in sorted(rules_dir.rglob("*.md")):
        rel = rule_file.relative_to(claude_dir)
        rules.append(str(rel).replace("\\", "/"))
    return rules


def _read_json(path: Path) -> dict:
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return {}
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def _read_text(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        return ""


def detect_stack(project_path: Path) -> dict:
    detected: dict = {
        "languages": [],
        "frameworks": [],
        "domains": [],
        "tools": [],
        "commands": {},
        "has_env": False,
        "has_docker": False,
        "has_git": False,
        "has_tests": False,
        "has_ci": False,
    }
    try:
        entries = list(project_path.iterdir())
    except PermissionError:
        return detected

    file_names = {e.name for e in entries if e.is_file()}
    dir_names = {e.name for e in entries if e.is_dir()}

    detected["has_git"] = ".git" in dir_names
    detected["has_env"] = bool(
        file_names & {".env", ".env.example", ".env.local", ".env.sample"}
    )
    detected["has_docker"] = bool(
        file_names & {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"}
    )
    detected["has_ci"] = bool(dir_names & {".github", ".gitlab", ".circleci"})

    py_markers = {
        "requirements.txt",
        "pyproject.toml",
        "setup.py",
        "Pipfile",
        "setup.cfg",
    }
    has_python = bool(file_names & py_markers) or bool(list(project_path.glob("*.py")))

    if has_python:
        detected["languages"].append("python")
        deps = _read_text(project_path / "requirements.txt") + _read_text(
            project_path / "pyproject.toml"
        )

        for keywords, name, cmd in [
            (["flask"], "flask", "python -m flask run"),
            (["fastapi", "uvicorn"], "fastapi", "uvicorn main:app --reload"),
            (["django"], "django", "python manage.py runserver"),
        ]:
            if any(kw in deps for kw in keywords):
                detected["frameworks"].append(name)
                detected["commands"].setdefault("start", cmd)

        for keywords, domain in [
            (["torch", "pytorch", "torchvision", "torchaudio"], "pytorch"),
            (["tensorflow", "keras"], "tensorflow"),
            (["transformers", "diffusers", "huggingface_hub"], "huggingface"),
            (
                ["openai", "anthropic", "langchain", "llama_index", "groq", "together"],
                "llm-api",
            ),
            (
                ["numpy", "pandas", "sklearn", "scikit-learn", "matplotlib", "scipy"],
                "data-science",
            ),
            (
                ["zep", "mem0", "chromadb", "pinecone", "weaviate", "qdrant", "faiss"],
                "vector-db",
            ),
            (["mcp", "fastmcp"], "mcp"),
        ]:
            if any(kw in deps for kw in keywords):
                detected["domains"].append(domain)

        for keywords, tool in [
            (["pytest"], "pytest"),
            (["black"], "black"),
            (["ruff"], "ruff"),
            (["mypy"], "mypy"),
        ]:
            if any(kw in deps for kw in keywords):
                detected["tools"].append(tool)

        if "pytest" in detected["tools"] or (project_path / "tests").is_dir():
            detected["has_tests"] = True
            detected["commands"]["test"] = "pytest"

        ai_dirs = {
            "models",
            "checkpoints",
            "embeddings",
            "inference",
            "training",
            "data",
            "datasets",
            "weights",
        }
        if ai_dirs & dir_names:
            if not any(
                d in detected["domains"]
                for d in ["pytorch", "tensorflow", "huggingface"]
            ):
                detected["domains"].append("ai-ml-generic")

    if "package.json" in file_names:
        detected["languages"].append("nodejs")
        pkg = _read_json(project_path / "package.json")
        deps_dict = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        dep_str = " ".join(deps_dict.keys()).lower()
        scripts = pkg.get("scripts", {})

        for keywords, name in [
            (["react", "@types/react"], "react"),
            (["next"], "nextjs"),
            (["vue", "@vue"], "vue"),
            (["express"], "express"),
            (["@nestjs/core", "nestjs"], "nestjs"),
            (["svelte"], "svelte"),
        ]:
            if any(kw in dep_str for kw in keywords):
                detected["frameworks"].append(name)

        if "typescript" in dep_str or (project_path / "tsconfig.json").exists():
            detected["languages"].append("typescript")

        for keywords, tool in [
            (["vite"], "vite"),
            (["jest"], "jest"),
            (["vitest"], "vitest"),
            (["playwright"], "playwright"),
            (["tailwindcss"], "tailwind"),
            (["prisma"], "prisma"),
        ]:
            if any(kw in dep_str for kw in keywords):
                detected["tools"].append(tool)

        for cmd_name in ["dev", "start"]:
            if cmd_name in scripts:
                detected["commands"].setdefault("start", f"npm run {cmd_name}")
                break
        if "test" in scripts:
            detected["commands"].setdefault("test", "npm test")
            detected["has_tests"] = True
        if "build" in scripts:
            detected["commands"]["build"] = "npm run build"

    for file, lang, start_cmd, test_cmd in [
        ("Cargo.toml", "rust", "cargo run", "cargo test"),
        ("go.mod", "go", "go run .", "go test ./..."),
        ("pubspec.yaml", "dart", "flutter run", "flutter test"),
    ]:
        if file in file_names:
            detected["languages"].append(lang)
            detected["commands"].setdefault("start", start_cmd)
            detected["commands"].setdefault("test", test_cmd)

    if "CMakeLists.txt" in file_names or list(project_path.glob("*.cpp")):
        detected["languages"].append("cpp")
    if list(project_path.glob("*.csproj")) or list(project_path.glob("*.sln")):
        detected["languages"].append("csharp")
        detected["commands"].setdefault("start", "dotnet run")
        detected["commands"].setdefault("test", "dotnet test")
    if "pom.xml" in file_names:
        detected["languages"].append("java")
        detected["commands"].setdefault("start", "mvn spring-boot:run")
        detected["commands"].setdefault("test", "mvn test")
    if "build.gradle" in file_names or "build.gradle.kts" in file_names:
        lang = "kotlin" if list(project_path.glob("**/*.kt")) else "java"
        detected["languages"].append(lang)
        detected["commands"].setdefault("start", "./gradlew bootRun")
        detected["commands"].setdefault("test", "./gradlew test")
    if "composer.json" in file_names:
        detected["languages"].append("php")
        detected["commands"].setdefault("start", "php artisan serve")
        detected["commands"].setdefault("test", "php artisan test")

    if "python" in detected["languages"] and "nodejs" in detected["languages"]:
        detected["domains"].append("fullstack")

    test_dirs = {"tests", "test", "__tests__", "spec", "e2e", "cypress"}
    if test_dirs & dir_names or detected["has_tests"]:
        detected["domains"].append("tdd")

    return detected


def resolve_skills(stack: dict, available_skills: set) -> list:
    seen: set = set()
    result: list = []
    for key in stack["languages"] + stack["frameworks"] + stack["domains"]:
        for skill in SKILL_MAP.get(key, []):
            if skill not in seen and skill in available_skills:
                seen.add(skill)
                result.append(skill)
    return result


def resolve_agents(stack: dict, available_agents: set) -> list:
    seen: set = set()
    result: list = []
    universal = ["code-reviewer", "build-error-resolver", "performance-optimizer"]
    for key in stack["languages"] + stack["frameworks"] + stack["domains"]:
        for agent in AGENT_MAP.get(key, []):
            if agent not in seen and agent in available_agents:
                seen.add(agent)
                result.append(agent)
    for agent in universal:
        if agent not in seen and agent in available_agents:
            seen.add(agent)
            result.append(agent)
    return result


def build_dynamic_skill_guide(
    available_skills: set,
    available_agents: set,
    available_commands: set,
) -> list:
    """
    Build the dynamic skill selection guide section.
    Only includes intents where at least one skill, agent, or command is installed.
    Includes slash commands in the output so Claude Code runs them automatically.
    """
    lines = [
        "## Dynamic Skill Selection",
        "",
        "**Read the user's request and activate the appropriate skills, agents, "
        "and slash commands below.**",
        "Match the user's task to the closest intent category and use everything "
        "listed. No user intervention required — apply automatically.",
        "",
    ]

    found_any = False
    for intent_key, intent in INTENT_MAP.items():
        matched_skills = [s for s in intent["skills"] if s in available_skills]
        matched_agents = [a for a in intent["agents"] if a in available_agents]
        matched_commands = [c for c in intent["commands"] if c in available_commands]

        if not matched_skills and not matched_agents and not matched_commands:
            continue  # skip intents with nothing installed

        found_any = True
        lines.append(f"### {intent['label']}")
        lines.append(f"*Triggers: {intent['triggers']}*")
        lines.append("")
        if matched_skills:
            lines.append(f"**Skills:** {', '.join(f'`{s}`' for s in matched_skills)}")
        if matched_agents:
            lines.append(f"**Agents:** {', '.join(f'`{a}`' for a in matched_agents)}")
        if matched_commands:
            cmd_list = ", ".join(f"`/{c}`" for c in matched_commands)
            lines.append(f"**Commands:** {cmd_list}")
        lines.append("")

    if not found_any:
        lines += [
            "> No skills, agents, or commands installed yet. Install from:",
            "> https://github.com/Jeffallan/everything-claude-code",
            "",
        ]

    return lines


def build_claude_md(
    project_path,
    stack,
    active_skills,
    active_agents,
    active_rules,
    available_skills,
    available_agents,
    available_commands,
):
    project_name = project_path.name
    langs = ", ".join(stack["languages"]) or "unknown"
    fws = ", ".join(stack["frameworks"]) or "none"
    domains = ", ".join(stack["domains"]) or "general"

    lines = [
        MARKER,
        f"# CLAUDE.md — {project_name}",
        f"> Generated by [claude-code-adaptive-skills](https://github.com/keerthivinod/claude-code-adaptive-skills) v{VERSION}",
        "> Re-run `python ~/.claude/adaptive-skills/detector.py --force` to refresh.",
        "",
        "## How to use this file",
        "This CLAUDE.md has two parts:",
        "1. **Always-active skills** — automatically applied based on your detected project stack.",
        "2. **Dynamic Skill Selection** — pick the right skills, agents, and commands based on what the user is asking for.",
        "Read the user's request, check the Dynamic Skill Selection section, and activate the matching resources automatically.",
        "",
        "## Project Stack",
        f"- **Languages:** {langs}",
        f"- **Frameworks:** {fws}",
        f"- **Domain:** {domains}",
        "",
    ]

    if active_skills:
        lines += [
            "## Always-Active Skills",
            "These skills match your detected project stack and should always be applied:",
            "",
        ]
        for s in active_skills:
            lines.append(f"- `{s}`")
        lines.append("")
    else:
        lines += [
            "## Skills",
            "> No stack-matched skills found. Check the Dynamic Skill Selection section below.",
            "",
        ]

    if active_agents:
        lines += ["## Default Agents", ""]
        for a in active_agents:
            lines.append(f"- `{a}`")
        lines.append("")

    if active_rules:
        lines += ["## Active Rules", ""]
        for r in active_rules:
            lines.append(f"- `~/.claude/{r}`")
        lines.append("")

    cmds = stack.get("commands", {})
    if cmds:
        lines += ["## Project Commands", ""]
        for label, cmd in cmds.items():
            lines.append(f"- **{label.capitalize()}:** `{cmd}`")
        lines.append("")

    # Dynamic skill selection guide (skills + agents + commands)
    lines += build_dynamic_skill_guide(
        available_skills, available_agents, available_commands
    )

    # Stack-specific guidance
    guidance: list = []
    if "python" in stack["languages"]:
        guidance += [
            "### Python",
            "- Use virtual environment: `.\\venv\\Scripts\\activate` (Windows) or `source venv/bin/activate`",
            "- Load secrets via `python-dotenv` — never hardcode",
            "- Type hints required on all function signatures",
        ]
    if "pytorch" in stack["domains"]:
        guidance += [
            "### PyTorch",
            "- Always check `torch.cuda.is_available()` before training",
            "- Call `model.eval()` and `torch.no_grad()` during inference",
        ]
    if "llm-api" in stack["domains"]:
        guidance += [
            "### LLM API",
            "- Store all API keys in `.env` (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)",
            "- Handle rate limits with exponential backoff retry logic",
        ]
    if "fullstack" in stack["domains"]:
        guidance += [
            "### Full-Stack",
            "- Run backend and frontend in separate terminals",
            "- CORS must be configured on the backend to allow the frontend origin",
        ]
    if stack.get("has_docker"):
        guidance += [
            "### Docker",
            "- Rebuild after dependency changes: `docker-compose up --build`",
            "- Never put secrets in Dockerfile — use env files",
        ]

    if guidance:
        lines += ["## Stack Guidance", ""] + guidance + [""]

    lines += [
        "## General",
        "- Read existing code before editing — understand the pattern first",
        "- Keep changes minimal and focused; don't refactor unrelated code",
        "- Run the test suite before marking work done",
        "- Never commit `.env`, `node_modules/`, `venv/`, `__pycache__/`, or model weights",
    ]
    return "\n".join(lines) + "\n"


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    force = "--force" in args
    claude_arg = None
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--claude-dir" and i + 1 < len(args):
            claude_arg = Path(args[i + 1])
            i += 2
        elif args[i].startswith("--"):
            i += 1
        else:
            positional.append(args[i])
            i += 1

    project_path = Path(positional[0]).resolve() if positional else Path.cwd().resolve()

    if not project_path.is_dir():
        print(
            f"[adaptive-skills] ERROR: '{project_path}' is not a directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        all_names = {e.name for e in project_path.iterdir()}
    except PermissionError as exc:
        print(
            f"[adaptive-skills] ERROR: Cannot read '{project_path}': {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    is_project = (
        bool(all_names & PROJECT_INDICATORS)
        or bool(list(project_path.glob("*.csproj")))
        or bool(list(project_path.glob("*.cpp")))
    )
    if not is_project:
        sys.exit(0)

    claude_dir = claude_arg or find_claude_dir()
    available_skills = discover_skills(claude_dir) if claude_dir else set()
    available_agents = discover_agents(claude_dir) if claude_dir else set()
    available_commands = discover_commands(claude_dir) if claude_dir else set()
    available_rules = discover_rules(claude_dir) if claude_dir else []

    stack = detect_stack(project_path)
    active_skills = resolve_skills(stack, available_skills)
    active_agents = resolve_agents(stack, available_agents)

    lang_rule_map = {
        "python": "rules/python",
        "nodejs": "rules/js",
        "typescript": "rules/ts",
        "rust": "rules/rust",
        "go": "rules/go",
    }
    filtered_rules = []
    for rule in available_rules:
        for lang, prefix in lang_rule_map.items():
            if lang in stack["languages"] and rule.startswith(prefix):
                filtered_rules.append(rule)
                break
        else:
            if rule.startswith("rules/common"):
                filtered_rules.append(rule)

    content = build_claude_md(
        project_path,
        stack,
        active_skills,
        active_agents,
        filtered_rules,
        available_skills,
        available_agents,
        available_commands,
    )

    if dry_run:
        print(content)
        return

    output_path = project_path / "CLAUDE.md"
    if not force and output_path.exists():
        if output_path.stat().st_size > MAX_FILE_SIZE:
            print("[adaptive-skills] CLAUDE.md is too large. Use --force to overwrite.")
            sys.exit(0)
        existing = output_path.read_text(encoding="utf-8", errors="ignore")
        if MARKER not in existing:
            print(
                "[adaptive-skills] CLAUDE.md exists (manual edit). Use --force to overwrite."
            )
            sys.exit(0)

    output_path.write_text(content, encoding="utf-8")
    langs_str = ", ".join(stack["languages"]) or "none"
    skills_str = ", ".join(active_skills[:4]) or "none installed"
    if len(active_skills) > 4:
        skills_str += f" (+{len(active_skills) - 4} more)"
    cmds_count = len(available_commands)
    print(
        f"[adaptive-skills] ✓ {project_path.name} | stack: {langs_str} | skills: {skills_str} | commands: {cmds_count}"
    )


if __name__ == "__main__":
    main()
