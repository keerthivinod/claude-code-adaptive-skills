# claude-code-adaptive-skills

> Automatically generates a tailored `CLAUDE.md` every time you `cd` into a project — giving Claude Code **dynamic skill selection** so it picks the right skills, agents, and slash commands based on what you ask, with zero user intervention.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![PowerShell 7+](https://img.shields.io/badge/PowerShell-7%2B-blue.svg)](https://github.com/PowerShell/PowerShell)
[![Version](https://img.shields.io/badge/version-4.0.0-green.svg)](https://github.com/keerthivinod/claude-code-adaptive-skills/releases)

---

## The problem this solves

Claude Code has a powerful skill system — but by default it doesn't know which skills, agents, or slash commands to apply or when. You end up manually specifying them, or Claude Code ignores them entirely.

This plugin fixes that in two ways:

1. **Stack detection** — scans your project and activates the right skills for your language and framework automatically
2. **Dynamic skill selection** — generates a routing guide so Claude Code picks skills, agents, AND slash commands based on *what you ask*, not just *what files you have*

The result: say *"improve the frontend"* and Claude Code activates frontend skills and runs accessibility audits. Say *"write tests"* and it switches to TDD skills and invokes `/tdd`. Say *"plan this feature"* and it pulls in architect agents and runs `/plan`. All automatically, for every project — no intervention needed.

---

## What's new in v4.0.0

- **Slash commands included** — the generated `CLAUDE.md` now lists which `/commands` to run for each intent, not just skills and agents
- **20 intent categories** — expanded from 10 to cover documents, visual design, MCP building, planning, team workflows, debugging, code review, data science, content/SEO, and more
- **Full inventory coverage** — maps every installed skill, agent, and command including `docx`, `pdf`, `pptx`, `xlsx`, `canvas-design`, `algorithmic-art`, `mcp-builder`, `web-artifacts-builder`, `internal-comms`, `linkedin`, and all 100+ agents and commands from [everything-claude-code](https://github.com/Jeffallan/everything-claude-code)
- **`discover_commands()`** — new function scans `~/.claude/commands/` and only lists commands you actually have installed
- **Richer status line** — shows command count on install: `| commands: 103`

---

## How it works

When you `cd` into a project:

1. **Detects** your stack from project files (`package.json`, `requirements.txt`, `Cargo.toml`, etc.)
2. **Discovers** which skills, agents, commands, and rules you have installed in `~/.claude/`
3. **Writes** a `CLAUDE.md` with two sections:
   - **Always-active skills** — matched to your detected stack, applied every session
   - **Dynamic Skill Selection Guide** — tells Claude Code which skills, agents, and `/commands` to activate based on the user's task intent

---

## Dynamic Skill Selection Guide (v4.0.0)

The generated `CLAUDE.md` contains a guide like this (only listing resources you actually have installed):

```markdown
## Dynamic Skill Selection

Read the user's request and activate the appropriate skills, agents, and slash commands below.
Match the user's task to the closest intent category and use everything listed. No user
intervention required — apply automatically.

### Frontend / UI / Styling / Components / Design
*Triggers: frontend, UI, styling, CSS, layout, design, component, animation...*
**Skills:** `react-expert`, `frontend-patterns`, `typescript-pro`, `senior-frontend`
**Agents:** `typescript-reviewer`, `performance-optimizer`, `a11y-architect`
**Commands:** `/accessibility-audit`, `/code-review`, `/performance-optimization`

### Backend / API / Server / Routes / Business Logic
*Triggers: backend, API, server, route, endpoint, authentication...*
**Skills:** `fastapi-expert`, `python-pro`, `backend-patterns`, `api-design`
**Agents:** `python-reviewer`, `build-error-resolver`, `fastapi-pro`, `graphql-architect`
**Commands:** `/code-review`, `/api-mock`, `/feature-dev`

### Testing / TDD / Unit Tests / E2E / Coverage
*Triggers: test, TDD, unit test, e2e, coverage, mock, pytest, Jest...*
**Skills:** `tdd-workflow`, `e2e-testing`, `python-testing`, `django-tdd`
**Agents:** `tdd-guide`, `pr-test-analyzer`, `tdd-orchestrator`, `test-automator`
**Commands:** `/tdd`, `/e2e`, `/test-coverage`, `/quality-gate`, `/verify`

### AI / LLM / Prompts / Agents / RAG / Embeddings / MCP
*Triggers: AI, LLM, prompt, Claude, OpenAI, embedding, RAG, vector, MCP...*
**Skills:** `claude-api`, `python-pro`, `mcp-server-patterns`, `mcp-builder`
**Agents:** `python-reviewer`, `loop-operator`, `dx-optimizer`
**Commands:** `/prompt-optimize`, `/multi-agent-optimize`, `/loop-start`, `/orchestrate`

### Documents / Reports / Word / PDF / Presentations / Spreadsheets
*Triggers: document, Word, DOCX, PDF, PowerPoint, PPTX, slide, Excel, XLSX...*
**Skills:** `docx`, `pdf`, `pptx`, `xlsx`, `doc-coauthoring`
**Agents:** `doc-updater`
**Commands:** `/doc-generate`, `/update-docs`

### Planning / Architecture / System Design / Roadmap / PRD
*Triggers: plan, architecture, system design, PRD, spec, C4 diagram...*
**Skills:** `senior-architect`, `fullstack-guardian`, `api-design`
**Agents:** `architect`, `planner`, `business-analyst`, `code-architect`
**Commands:** `/plan`, `/c4-architecture`, `/feature-dev`, `/prp-prd`

### Team Workflows / Multi-Agent / Delegation / Orchestration
*Triggers: team, multi-agent, delegate, parallel, spawn, coordinate, workflow...*
**Agents:** `team-lead`, `team-debugger`, `chief-of-staff`, `loop-operator`
**Commands:** `/team-debug`, `/team-feature`, `/workflow-automate`, `/orchestrate`

### Debugging / Error Resolution / Bug Fixing
*Triggers: bug, error, exception, crash, fix, debug, traceback, not working...*
**Skills:** `verification-loop`, `impeccable`
**Agents:** `debugger`, `build-error-resolver`, `silent-failure-hunter`
**Commands:** `/build-fix`, `/verify`, `/code-explain`

### Visual Design / Generative Art / GIF / Branding / Themes
*Triggers: art, poster, graphic, generative, GIF, brand, theme, colour palette...*
**Skills:** `canvas-design`, `algorithmic-art`, `slack-gif-creator`, `theme-factory`

### ... and 11 more intent categories
```

Claude Code reads this guide at the start of every session and follows it for every request — no prompting needed.

---

## Full list of intent categories (v4.0.0)

| Category | What it covers |
|---|---|
| Frontend / UI | React, CSS, design, components, accessibility |
| Backend / API | REST, GraphQL, auth, microservices |
| Database | SQL, ORM, schema, migrations |
| Testing / TDD | Unit, E2E, coverage, mocking |
| Performance | Speed, bundle size, profiling |
| Security | Auth, OWASP, secrets, vulnerabilities |
| AI / LLM / MCP | Prompts, agents, RAG, embeddings, MCP servers |
| DevOps | Docker, CI/CD, Kubernetes, Terraform |
| Refactoring | Code quality, patterns, technical debt |
| Mobile | Flutter, Android, iOS, React Native |
| Documents | Word, PDF, PowerPoint, Excel |
| Visual Design | Canvas art, GIFs, branding, themes |
| Web Artifacts | HTML artifacts, React components, dashboards |
| MCP / Tool Building | MCP servers, plugins, integrations |
| Planning / Architecture | System design, PRDs, C4 diagrams |
| Team Workflows | Multi-agent, delegation, orchestration |
| Documentation | README, API docs, tutorials |
| Content / SEO | Blog, marketing, LinkedIn, internal comms |
| Debugging | Bug fixing, error resolution, root cause |
| Code Review | PR review, quality gates, linting |
| Data / ML | Data science, analytics, GAN, notebooks |

---

## Installation

### Prerequisites

- Python 3.10+
- PowerShell 7+ (Windows)
- [Claude Code](https://claude.ai/code) installed
- Optionally: [everything-claude-code](https://github.com/Jeffallan/everything-claude-code) for a full skill, agent, and command library

### One-command install (Windows / PowerShell 7)

```powershell
# 1. Clone the repo
git clone https://github.com/keerthivinod/claude-code-adaptive-skills.git
cd claude-code-adaptive-skills

# 2. Run the installer
.\install.ps1
```

The installer:
- Copies `detector.py` to `~/.claude/adaptive-skills/`
- Patches your PowerShell profile with a directory-change hook
- Runs a smoke test to verify Python can execute it

### Restart PowerShell

Close and reopen your terminal. Then `cd` into any project:

```
[adaptive-skills] ✓ my-project | stack: nodejs | skills: javascript-pro | commands: 103
```

A `CLAUDE.md` with the full Dynamic Skill Selection Guide appears in your project folder.

---

## Detection support

| File found | Detected |
|---|---|
| `requirements.txt` / `pyproject.toml` | Python |
| `fastapi` / `uvicorn` in deps | FastAPI |
| `flask` in deps | Flask |
| `django` in deps | Django |
| `torch` / `pytorch` in deps | PyTorch |
| `openai` / `anthropic` / `langchain` in deps | LLM API |
| `mcp` / `fastmcp` in deps | MCP server |
| `package.json` | Node.js |
| `react` in npm deps | React |
| `next` in npm deps | Next.js |
| `tsconfig.json` or `typescript` in deps | TypeScript |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pubspec.yaml` | Dart/Flutter |
| `*.csproj` / `*.sln` | C# / .NET |
| `pom.xml` | Java (Maven) |
| `build.gradle` | Java/Kotlin (Gradle) |
| `Dockerfile` / `docker-compose.yml` | Docker guidance |
| Both Python + Node.js | Full-stack combo |
| `tests/` / `__tests__/` dir | TDD guidance |

---

## Manual commands

```powershell
# Preview without writing (dry run)
python ~/.claude/adaptive-skills/detector.py --dry-run

# Regenerate for current directory
python ~/.claude/adaptive-skills/detector.py

# Regenerate for a specific project
python ~/.claude/adaptive-skills/detector.py D:\projects\my-app

# Force overwrite a manually-edited CLAUDE.md
python ~/.claude/adaptive-skills/detector.py --force

# Use a custom Claude directory
python ~/.claude/adaptive-skills/detector.py --claude-dir C:\custom\.claude
```

### Protecting manual edits

If you manually edit a `CLAUDE.md`, the detector will not overwrite it (it checks for the `<!-- claude-code-adaptive-skills -->` marker). Use `--force` to regenerate from scratch.

### Uninstall

```powershell
.\install.ps1 -Uninstall
```

---

## macOS / Linux

The `detector.py` script is cross-platform. Add this to your `~/.zshrc` or `~/.bashrc`:

```bash
# claude-code-adaptive-skills hook
_adaptive_skills_check() {
    python ~/.claude/adaptive-skills/detector.py "$PWD" 2>/dev/null
}
autoload -U add-zsh-hook
add-zsh-hook chpwd _adaptive_skills_check  # zsh

# For bash:
# PROMPT_COMMAND="_adaptive_skills_check; $PROMPT_COMMAND"
```

---

## Adding new intent categories

To add a new task category (e.g. "GraphQL"):

1. Open `detector.py`
2. Add an entry to `INTENT_MAP`:
```python
"graphql": {
    "label": "GraphQL / Schema / Resolvers / Subscriptions",
    "triggers": "GraphQL, schema, resolver, mutation, subscription, Apollo",
    "skills": ["graphql-patterns", "backend-patterns"],
    "agents": ["graphql-architect", "code-reviewer"],
    "commands": ["api-mock", "code-review"],
},
```
3. Re-run `.\install.ps1` to update the installed version
4. Run `python ~/.claude/adaptive-skills/detector.py --force` in your project

---

## Compatibility

| Component | Requirement |
|---|---|
| Python | 3.10+ |
| PowerShell | 7.0+ |
| Claude Code | Any version |
| everything-claude-code | Optional but recommended |
| OS | Windows (PowerShell hook); detector.py works on macOS/Linux |

---

## License

MIT © Karthik Vinod — see [LICENSE](LICENSE)
