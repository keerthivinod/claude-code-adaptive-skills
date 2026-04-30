# claude-code-adaptive-skills

> Automatically generates a tailored `CLAUDE.md` every time you `cd` into a project — giving Claude Code **dynamic skill selection** so it picks the right skills based on what you ask, not just what files you have.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![PowerShell 7+](https://img.shields.io/badge/PowerShell-7%2B-blue.svg)](https://github.com/PowerShell/PowerShell)
[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](https://github.com/keerthivinod/claude-code-adaptive-skills/releases)

---

## The problem this solves

Claude Code has a powerful skill system — but by default it doesn't know which skills to apply or when. You end up manually specifying skills, or Claude Code ignores them entirely.

This plugin fixes that in two ways:

1. **Stack detection** — scans your project and activates the right skills for your language and framework automatically
2. **Dynamic skill selection** — generates a routing guide so Claude Code picks skills based on *what you ask*, not just *what files you have*

The result: say *"improve the frontend"* and Claude Code activates frontend skills. Say *"add authentication"* and it switches to backend/security skills. Say *"write tests"* and it pulls testing skills. All automatically, for every project.

---

## How it works

When you `cd` into a project:

1. **Detects** your stack from project files (`package.json`, `requirements.txt`, `Cargo.toml`, etc.)
2. **Discovers** which skills, agents, and rules you have installed in `~/.claude/`
3. **Writes** a `CLAUDE.md` with two sections:
   - **Always-active skills** — matched to your detected stack, applied every session
   - **Dynamic Skill Selection Guide** — tells Claude Code which skills to activate based on the user's task intent

---

## Dynamic Skill Selection Guide

This is the core of v3.0.0. The generated `CLAUDE.md` contains a guide like this (only listing skills you actually have installed):

```markdown
## Dynamic Skill Selection

Read the user's request and activate the appropriate skills below.

### Frontend / UI / Styling / Components / Design
Triggers: frontend, UI, styling, CSS, layout, design, component, animation, responsive...
Skills: `react-expert`, `frontend-patterns`, `typescript-pro`
Agents: `typescript-reviewer`, `performance-optimizer`

### Backend / API / Server / Routes / Business Logic
Triggers: backend, API, server, route, endpoint, authentication, authorisation...
Skills: `fastapi-expert`, `python-pro`, `backend-patterns`
Agents: `python-reviewer`, `build-error-resolver`

### Testing / TDD / Unit Tests / E2E / Coverage
Triggers: test, TDD, unit test, coverage, mock, pytest, Jest, Playwright...
Skills: `tdd-workflow`, `e2e-testing`
Agents: `tdd-guide`, `pr-test-analyzer`

### Performance / Optimisation / Speed / Bundle Size
Triggers: performance, optimise, slow, speed, loading, bundle size, cache...
Agents: `performance-optimizer`

### Security / Auth / Vulnerabilities / Secrets
Triggers: security, vulnerability, JWT, OAuth, CSRF, XSS, SQL injection...
Skills: `python-patterns`, `backend-patterns`
Agents: `code-reviewer`

### AI / LLM / Prompts / Agents / RAG / Embeddings
Triggers: AI, LLM, prompt, Claude, OpenAI, embedding, RAG, vector, agent...
Skills: `claude-api`, `python-pro`, `mcp-server-patterns`

### Refactoring / Code Quality / Architecture
Triggers: refactor, clean up, restructure, architecture, patterns, SOLID...
Skills: `python-patterns`, `frontend-patterns`, `fullstack-guardian`
Agents: `code-reviewer`, `performance-optimizer`
```

Claude Code reads this guide at the start of every session and follows it for every request.

---

## Example CLAUDE.md output

For a Node.js website project with `react-expert`, `frontend-patterns`, `typescript-pro`, `tdd-workflow`, and `performance-optimizer` installed:

```markdown
# CLAUDE.md — my-website

## Always-Active Skills
- `javascript-pro`

## Default Agents
- `build-error-resolver`, `typescript-reviewer`, `code-reviewer`, `performance-optimizer`

## Dynamic Skill Selection

### Frontend / UI / Styling / Components / Design
Triggers: frontend, UI, styling, CSS, layout, design, component, animation...
Skills: `react-expert`, `frontend-patterns`, `typescript-pro`
Agents: `typescript-reviewer`, `performance-optimizer`

### Testing / TDD
Triggers: test, TDD, unit test, coverage...
Skills: `tdd-workflow`
Agents: `tdd-guide`

### Performance / Optimisation
Triggers: performance, optimise, slow, speed...
Agents: `performance-optimizer`
```

---

## Installation

### Prerequisites

- Python 3.10+
- PowerShell 7+ (Windows)
- [Claude Code](https://claude.ai/code) installed
- Optionally: [everything-claude-code](https://github.com/Jeffallan/everything-claude-code) for a full skill library

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
[adaptive-skills] ✓ my-project | stack: nodejs | skills: javascript-pro
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
    "agents": ["code-reviewer"],
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
