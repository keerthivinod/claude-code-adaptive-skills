# claude-code-adaptive-skills

> Automatically generates a tailored `CLAUDE.md` every time you `cd` into a project folder — activating the right Claude Code skills, agents, and rules for your specific tech stack.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![PowerShell 7+](https://img.shields.io/badge/PowerShell-7%2B-blue.svg)](https://github.com/PowerShell/PowerShell)

---

## What it does

When you `cd` into a project folder, `detector.py` runs automatically and:

1. **Scans** the project files (`package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, etc.)
2. **Detects** your language, framework, and domain (Python, FastAPI, React, PyTorch, LLM APIs, etc.)
3. **Discovers** which Claude Code skills, agents, and rules you actually have installed in `~/.claude/`
4. **Writes** a `CLAUDE.md` that activates the right ones for that project

The result: every project Claude Code opens already knows exactly which skills to use — without you having to set anything up.

---

## Example output

For a Python FastAPI + React project:

```markdown
<!-- claude-code-adaptive-skills -->
# CLAUDE.md — my-api-project

## Project Stack
- **Languages:** python, nodejs, typescript
- **Frameworks:** fastapi, react
- **Domain:** llm-api, fullstack

## Active Skills
- `fastapi-expert`
- `python-pro`
- `react-expert`
- `typescript-pro`
- `fullstack-guardian`

## Recommended Agents
- `python-reviewer`
- `build-error-resolver`
- `typescript-reviewer`
- `performance-optimizer`

## Active Rules
- `~/.claude/rules/python/coding-style.md`
- `~/.claude/rules/python/testing.md`
- `~/.claude/rules/python/security.md`

## Project Commands
- **Start:** `uvicorn main:app --reload`
- **Test:** `pytest`
- **Build:** `npm run build`
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

Close and reopen your terminal. Then `cd` into any project — you'll see:

```
[adaptive-skills] ✓ my-project | stack: python, nodejs | skills: fastapi-expert, python-pro (+2 more)
```

---

## How it works

### Detection logic

| File found | Detected |
|---|---|
| `requirements.txt` / `pyproject.toml` | Python |
| `torch` / `pytorch` in deps | PyTorch domain |
| `openai` / `anthropic` / `langchain` in deps | LLM API domain |
| `fastapi` / `uvicorn` in deps | FastAPI framework |
| `flask` in deps | Flask framework |
| `django` in deps | Django framework |
| `package.json` | Node.js |
| `react` in npm deps | React framework |
| `next` in npm deps | Next.js framework |
| `tsconfig.json` or `typescript` in deps | TypeScript |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pubspec.yaml` | Dart/Flutter |
| `*.csproj` / `*.sln` | C# / .NET |
| `pom.xml` | Java (Maven) |
| `build.gradle` | Java/Kotlin (Gradle) |
| `.env` / `.env.example` | Secrets guidance |
| `Dockerfile` / `docker-compose.yml` | Docker guidance |
| Both Python + Node.js | Full-stack combo |
| `tests/` / `__tests__/` dir | TDD guidance |

### Skill mapping

The detector maps detected stack → installed skill names from `~/.claude/skills/`:

| Stack | Skills activated |
|---|---|
| Python | `python-pro`, `python-patterns` |
| FastAPI | `fastapi-expert`, `python-pro` |
| Flask | `python-pro`, `backend-patterns` |
| Django | `django-patterns` |
| React | `react-expert`, `frontend-patterns` |
| Next.js | `nextjs-developer`, `react-expert` |
| TypeScript | `typescript-pro` |
| Full-stack | `fullstack-guardian` |
| Rust | `rust-patterns` |
| Go | `golang-patterns` |
| PyTorch | `python-pro` |
| LLM API | `python-pro`, `claude-api` |
| MCP | `mcp-server-patterns` |

Only skills that are **actually installed** in your `~/.claude/skills/` are included — no phantom references.

### Agent mapping

Similarly maps detected stack → relevant agents from `~/.claude/agents/`:

| Stack | Agents recommended |
|---|---|
| Python | `python-reviewer`, `build-error-resolver` |
| PyTorch | `pytorch-build-resolver`, `python-reviewer` |
| TypeScript/React | `typescript-reviewer`, `build-error-resolver` |
| TDD | `tdd-guide`, `pr-test-analyzer` |
| All projects | `code-reviewer`, `performance-optimizer` |

---

## Usage

### Automatic (normal use)

Just `cd` into a project. CLAUDE.md is generated or refreshed automatically.

### Manual commands

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

If you manually edit a `CLAUDE.md`, the detector **will not overwrite it** (it checks for the `<!-- claude-code-adaptive-skills -->` marker). Use `--force` only when you want to regenerate from scratch.

### Uninstall

```powershell
.\install.ps1 -Uninstall
```

This removes `~/.claude/adaptive-skills/` and cleanly strips the hook from your PowerShell profile.

---

## Compatibility

| Component | Requirement |
|---|---|
| Python | 3.10+ (uses `X \| Y` union syntax) |
| PowerShell | 7.0+ (`#Requires -Version 7.0`) |
| Claude Code | Any version |
| everything-claude-code | Optional but recommended |
| Operating System | Windows (PowerShell hook); detector.py works on macOS/Linux too |

---

## macOS / Linux

The `detector.py` script itself is cross-platform. For auto-triggering on directory change, add this to your `~/.zshrc` or `~/.bashrc`:

```bash
# claude-code-adaptive-skills hook
_adaptive_skills_check() {
    python ~/.claude/adaptive-skills/detector.py "$PWD" 2>/dev/null
}
autoload -U add-zsh-hook
add-zsh-hook chpwd _adaptive_skills_check  # zsh

# For bash, use PROMPT_COMMAND:
# PROMPT_COMMAND="_adaptive_skills_check; $PROMPT_COMMAND"
```

---

## Contributing

PRs welcome! To add support for a new language or framework:

1. Add detection logic in `detect_stack()` in `detector.py`
2. Add skill mapping in `SKILL_MAP`
3. Add agent mapping in `AGENT_MAP`
4. Test with `python detector.py --dry-run /path/to/sample-project`

---

## License

MIT © Karthik Vinod — see [LICENSE](LICENSE)
