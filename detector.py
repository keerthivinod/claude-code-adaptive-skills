"""
claude-code-adaptive-skills — detector.py
==========================================
Scans a project folder, detects the tech stack, discovers which Claude Code
skills are actually installed, and writes a tailored CLAUDE.md that activates
the right skills and agents for the project.

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

VERSION = "2.0.0"
MARKER  = "<!-- claude-code-adaptive-skills -->"

SKILL_MAP: dict[str, list[str]] = {
    "python":     ["python-pro", "python-patterns"],
    "nodejs":     ["javascript-pro"],
    "typescript": ["typescript-pro"],
    "rust":       ["rust-patterns"],
    "go":         ["golang-patterns"],
    "cpp":        ["cpp-coding-standards"],
    "java":       ["java-coding-standards"],
    "kotlin":     ["kotlin-patterns"],
    "dart":       ["dart-flutter-patterns"],
    "csharp":     ["dotnet-patterns"],
    "php":        ["laravel-patterns"],
    "flask":      ["python-pro", "backend-patterns"],
    "fastapi":    ["fastapi-expert", "python-pro"],
    "django":     ["django-patterns"],
    "react":      ["react-expert", "frontend-patterns"],
    "nextjs":     ["nextjs-developer", "react-expert"],
    "vue":        ["frontend-patterns"],
    "express":    ["backend-patterns"],
    "nestjs":     ["nestjs-expert", "nestjs-patterns"],
    "springboot": ["springboot-patterns"],
    "ktor":       ["kotlin-ktor-patterns"],
    "laravel":    ["laravel-patterns"],
    "flutter":    ["dart-flutter-patterns"],
    "pytorch":        ["python-pro"],
    "tensorflow":     ["python-pro"],
    "huggingface":    ["python-pro"],
    "llm-api":        ["python-pro", "claude-api"],
    "data-science":   ["python-pro", "python-patterns"],
    "vector-db":      ["python-pro", "backend-patterns"],
    "ai-ml-generic":  ["python-pro"],
    "mcp":            ["mcp-server-patterns"],
    "android":        ["android-clean-architecture"],
    "fullstack":  ["fullstack-guardian"],
    "tdd":        ["tdd-workflow"],
    "e2e":        ["e2e-testing"],
    "api-design": ["api-design"],
}

AGENT_MAP: dict[str, list[str]] = {
    "python":     ["python-reviewer", "build-error-resolver"],
    "nodejs":     ["build-error-resolver", "typescript-reviewer"],
    "typescript": ["typescript-reviewer"],
    "react":      ["build-error-resolver", "typescript-reviewer"],
    "pytorch":    ["pytorch-build-resolver", "python-reviewer"],
    "rust":       ["rust-build-resolver", "rust-reviewer"],
    "go":         ["go-build-resolver", "go-reviewer"],
    "java":       ["java-build-resolver", "java-reviewer"],
    "kotlin":     ["kotlin-build-resolver", "kotlin-reviewer"],
    "cpp":        ["cpp-build-resolver", "cpp-reviewer"],
    "dart":       ["dart-build-resolver", "flutter-reviewer"],
    "fullstack":  ["code-reviewer", "performance-optimizer"],
    "tdd":        ["tdd-guide", "pr-test-analyzer"],
}

PROJECT_INDICATORS = {
    "package.json", "requirements.txt", "pyproject.toml", "setup.py",
    "Pipfile", "Cargo.toml", "go.mod", "Makefile", "CMakeLists.txt",
    "build.gradle", "pom.xml", ".git", "Dockerfile", "docker-compose.yml",
    "docker-compose.yaml", "composer.json", "Gemfile", "pubspec.yaml",
}


def find_claude_dir() -> "Path | None":
    candidates = [
        Path.home() / ".claude",
        Path(os.environ.get("USERPROFILE", "")) / ".claude",
        Path(os.environ.get("HOME", "")) / ".claude",
    ]
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
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        return ""


def detect_stack(project_path: Path) -> dict:
    detected: dict = {
        "languages": [], "frameworks": [], "domains": [],
        "tools": [], "commands": {},
        "has_env": False, "has_docker": False, "has_git": False,
        "has_tests": False, "has_ci": False,
    }
    try:
        entries = list(project_path.iterdir())
    except PermissionError:
        return detected

    file_names = {e.name for e in entries if e.is_file()}
    dir_names  = {e.name for e in entries if e.is_dir()}

    detected["has_git"]    = ".git" in dir_names
    detected["has_env"]    = bool(file_names & {".env", ".env.example", ".env.local", ".env.sample"})
    detected["has_docker"] = bool(file_names & {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"})
    detected["has_ci"]     = bool(dir_names & {".github", ".gitlab", ".circleci"})

    py_markers = {"requirements.txt", "pyproject.toml", "setup.py", "Pipfile", "setup.cfg"}
    has_python = bool(file_names & py_markers) or bool(list(project_path.glob("*.py")))

    if has_python:
        detected["languages"].append("python")
        deps = _read_text(project_path / "requirements.txt") + _read_text(project_path / "pyproject.toml")

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
            (["openai", "anthropic", "langchain", "llama_index", "groq", "together"], "llm-api"),
            (["numpy", "pandas", "sklearn", "scikit-learn", "matplotlib", "scipy"], "data-science"),
            (["zep", "mem0", "chromadb", "pinecone", "weaviate", "qdrant", "faiss"], "vector-db"),
            (["mcp", "fastmcp"], "mcp"),
        ]:
            if any(kw in deps for kw in keywords):
                detected["domains"].append(domain)

        for keywords, tool in [
            (["pytest"], "pytest"), (["black"], "black"),
            (["ruff"], "ruff"), (["mypy"], "mypy"),
        ]:
            if any(kw in deps for kw in keywords):
                detected["tools"].append(tool)

        if "pytest" in detected["tools"] or (project_path / "tests").is_dir():
            detected["has_tests"] = True
            detected["commands"]["test"] = "pytest"

        ai_dirs = {"models", "checkpoints", "embeddings", "inference", "training", "data", "datasets", "weights"}
        if ai_dirs & dir_names:
            if not any(d in detected["domains"] for d in ["pytorch", "tensorflow", "huggingface"]):
                detected["domains"].append("ai-ml-generic")

    if "package.json" in file_names:
        detected["languages"].append("nodejs")
        pkg = _read_json(project_path / "package.json")
        deps_dict = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        dep_str = " ".join(deps_dict.keys()).lower()
        scripts = pkg.get("scripts", {})

        for keywords, name in [
            (["react", "@types/react"], "react"), (["next"], "nextjs"),
            (["vue", "@vue"], "vue"), (["express"], "express"),
            (["@nestjs/core", "nestjs"], "nestjs"), (["svelte"], "svelte"),
        ]:
            if any(kw in dep_str for kw in keywords):
                detected["frameworks"].append(name)

        if "typescript" in dep_str or (project_path / "tsconfig.json").exists():
            detected["languages"].append("typescript")

        for keywords, tool in [
            (["vite"], "vite"), (["jest"], "jest"), (["vitest"], "vitest"),
            (["playwright"], "playwright"), (["tailwindcss"], "tailwind"),
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


def build_claude_md(project_path, stack, active_skills, active_agents, active_rules):
    project_name = project_path.name
    langs   = ", ".join(stack["languages"])  or "unknown"
    fws     = ", ".join(stack["frameworks"]) or "none"
    domains = ", ".join(stack["domains"])    or "general"

    lines = [
        MARKER,
        f"# CLAUDE.md — {project_name}",
        f"> Generated by [claude-code-adaptive-skills](https://github.com/keerthivinod/claude-code-adaptive-skills) v{VERSION}",
        f"> Re-run `python ~/.claude/adaptive-skills/detector.py` to refresh.",
        "",
        "## Project Stack",
        f"- **Languages:** {langs}",
        f"- **Frameworks:** {fws}",
        f"- **Domain:** {domains}",
        "",
    ]

    if active_skills:
        lines += ["## Active Skills", "Claude Code should apply these installed skills for this project:", ""]
        for s in active_skills:
            lines.append(f"- `{s}`")
        lines.append("")
    else:
        lines += ["## Skills", "> No matching skills found in your Claude Code installation.", "> Install skills from https://github.com/Jeffallan/everything-claude-code", ""]

    if active_agents:
        lines += ["## Recommended Agents", "Invoke these agents for specific tasks:", ""]
        for a in active_agents:
            lines.append(f"- `{a}`")
        lines.append("")

    if active_rules:
        lines += ["## Active Rules", "These rule files are automatically applied:", ""]
        for r in active_rules:
            lines.append(f"- `~/.claude/{r}`")
        lines.append("")

    cmds = stack.get("commands", {})
    if cmds:
        lines += ["## Project Commands", ""]
        for label, cmd in cmds.items():
            lines.append(f"- **{label.capitalize()}:** `{cmd}`")
        lines.append("")

    guidance: list = []
    if "python" in stack["languages"]:
        guidance += ["### Python",
            "- Use virtual environment: activate with `.\\venv\\Scripts\\activate` (Windows) or `source venv/bin/activate`",
            "- Load secrets via `python-dotenv` — never hardcode",
            "- Type hints required on all function signatures (enforced by `python-pro` skill)"]
    if "pytorch" in stack["domains"]:
        guidance += ["### PyTorch / CUDA",
            "- Always check `torch.cuda.is_available()` before training",
            "- Call `model.eval()` and use `torch.no_grad()` during inference",
            "- Pin torch version in requirements.txt — CUDA compatibility is version-sensitive"]
    if "llm-api" in stack["domains"]:
        guidance += ["### LLM API",
            "- Store all API keys in `.env` (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)",
            "- Handle rate limits with retry logic (exponential backoff)",
            "- For local models via LM Studio: set `ANTHROPIC_BASE_URL=http://localhost:1234`"]
    if "vector-db" in stack["domains"]:
        guidance += ["### Vector DB / Memory",
            "- Connection strings go in `.env` — never in code",
            "- Match embedding dimensions between your model and the index",
            "- Batch upserts are faster than single inserts"]
    if "fullstack" in stack["domains"]:
        guidance += ["### Full-Stack",
            "- Run backend and frontend in separate terminals",
            "- CORS must be configured on the backend to allow frontend origin",
            "- API base URL in frontend `.env` as `VITE_API_URL` or `REACT_APP_API_URL`"]
    if stack.get("has_docker"):
        guidance += ["### Docker",
            "- Rebuild after dependency changes: `docker-compose up --build`",
            "- Never put secrets in Dockerfile — use env files or Docker secrets"]

    if guidance:
        lines += ["## Guidance", ""] + guidance + [""]

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
    force   = "--force"   in args
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
        print(f"[adaptive-skills] ERROR: '{project_path}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    try:
        all_names = {e.name for e in project_path.iterdir()}
    except PermissionError as exc:
        print(f"[adaptive-skills] ERROR: Cannot read '{project_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    is_project = (bool(all_names & PROJECT_INDICATORS) or
                  bool(list(project_path.glob("*.csproj"))) or
                  bool(list(project_path.glob("*.cpp"))))
    if not is_project:
        sys.exit(0)

    claude_dir = claude_arg or find_claude_dir()
    available_skills = discover_skills(claude_dir) if claude_dir else set()
    available_agents = discover_agents(claude_dir) if claude_dir else set()
    available_rules  = discover_rules(claude_dir)  if claude_dir else []

    stack         = detect_stack(project_path)
    active_skills = resolve_skills(stack, available_skills)
    active_agents = resolve_agents(stack, available_agents)

    lang_rule_map = {"python": "rules/python", "nodejs": "rules/js",
                     "typescript": "rules/ts", "rust": "rules/rust", "go": "rules/go"}
    filtered_rules = []
    for rule in available_rules:
        for lang, prefix in lang_rule_map.items():
            if lang in stack["languages"] and rule.startswith(prefix):
                filtered_rules.append(rule)
                break
        else:
            if rule.startswith("rules/common"):
                filtered_rules.append(rule)

    content = build_claude_md(project_path, stack, active_skills, active_agents, filtered_rules)

    if dry_run:
        print(content)
        return

    output_path = project_path / "CLAUDE.md"
    if not force and output_path.exists():
        existing = output_path.read_text(encoding="utf-8", errors="ignore")
        if MARKER not in existing:
            print("[adaptive-skills] CLAUDE.md exists (manual edit). Use --force to overwrite.")
            sys.exit(0)

    output_path.write_text(content, encoding="utf-8")
    langs_str  = ", ".join(stack["languages"]) or "none"
    skills_str = ", ".join(active_skills[:4])  or "none installed"
    if len(active_skills) > 4:
        skills_str += f" (+{len(active_skills) - 4} more)"
    print(f"[adaptive-skills] ✓ {project_path.name} | stack: {langs_str} | skills: {skills_str}")


if __name__ == "__main__":
    main()
