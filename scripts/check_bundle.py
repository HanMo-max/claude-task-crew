#!/usr/bin/env python3
"""Validate the portable bundle; no third-party dependencies or model calls."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "templates/project"
ROLES = {"explorer", "worker", "tester", "researcher", "reviewer"}


def frontmatter(path):
    content = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", content, re.S)
    if not match:
        raise ValueError(f"{path.relative_to(ROOT)}: missing frontmatter")
    fields = {}
    for line in match[1].splitlines():
        key, sep, value = line.partition(":")
        if not sep or not value.strip() or key in fields:
            raise ValueError(f"{path.relative_to(ROOT)}: malformed/duplicate field")
        fields[key] = value.strip()
    return fields


def check():
    errors = []
    skill = PROJECT / ".claude/skills/opus-orchestrator/SKILL.md"
    fields = frontmatter(skill)
    if fields.get("name") != skill.parent.name or not fields.get("description"):
        errors.append("Skill name or description is invalid")
    agents = list((PROJECT / ".claude/agents").glob("*.md"))
    if {p.stem for p in agents} != ROLES:
        errors.append("Expected exactly five documented role files")
    for path in agents:
        fields = frontmatter(path)
        if fields.get("name") != path.stem or not fields.get("description"):
            errors.append(f"{path.name}: invalid name/description")
        expected = ("opus", "low") if path.stem == "reviewer" else ("sonnet", "medium")
        if (fields.get("model"), fields.get("effort")) != expected:
            errors.append(f"{path.name}: role defaults differ from the documented bundle")
        if path.stem in {"explorer", "researcher", "reviewer"}:
            denied = {v.strip() for v in fields.get("disallowedTools", "").split(",")}
            if not {"Edit", "Write", "NotebookEdit"}.issubset(denied):
                errors.append(f"{path.name}: read-only role lost edit/write restrictions")
    if (PROJECT / "CLAUDE.md").read_text().strip() != "@AGENTS.md":
        errors.append("CLAUDE.md must import canonical AGENTS.md without duplicate rules")

    private = re.compile(
        r"(?:/" + r"Users/|/" + r"home/)[^/\s]+/"
        r"|[A-Za-z]:\\Users\\[^\\\s]+\\"
        r"|sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}"
        r"|github_pat_[A-Za-z0-9_]{16,}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    )
    for path in ROOT.rglob("*"):
        if {".git", "__pycache__"}.intersection(path.relative_to(ROOT).parts):
            continue
        if path.is_symlink():
            errors.append(f"{path.relative_to(ROOT)}: symlink outside portable content")
            continue
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if private.search(text.replace("\\\\", "\\")):
            errors.append(f"{path.relative_to(ROOT)}: potential private path or credential")
        if path.suffix == ".md":
            for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (path.parent / target.split("#", 1)[0]).resolve()
                if ROOT not in resolved.parents or not resolved.exists():
                    errors.append(f"{path.relative_to(ROOT)}: broken/outside link {target}")
    return errors


if __name__ == "__main__":
    try:
        errors = check()
    except (OSError, ValueError, UnicodeError) as exc:
        errors = [str(exc)]
    for error in errors:
        print("FAIL:", error)
    if errors:
        sys.exit(1)
    print("PASS: skill, five roles, defaults, tool restrictions and local links")
    print("PASS: finite private-path/credential pattern check; not an exhaustive audit")
    print("Static validation only; no claim about runtime routing or project quality.")
