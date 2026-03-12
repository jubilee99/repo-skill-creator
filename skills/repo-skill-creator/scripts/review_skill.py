#!/usr/bin/env python3
"""Review a skill against the richer PDF-style checklist."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from repo_skill_lib import load_openai_yaml, parse_frontmatter

ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "allowed-tools",
    "metadata",
}
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_RECOMMENDED_WORDS = 5000
RESERVED_PREFIXES = ("claude", "anthropic")


def word_count(text: str) -> int:
    return len(re.findall(r"\b\S+\b", text))


def has_heading(body: str, heading: str) -> bool:
    pattern = rf"^##+\s+.*{re.escape(heading)}.*$"
    return re.search(pattern, body, re.IGNORECASE | re.MULTILINE) is not None


def add_finding(findings: dict[str, list[str]], level: str, message: str) -> None:
    findings[level].append(message)


def review_skill(skill_dir: Path) -> dict[str, Any]:
    findings: dict[str, list[str]] = {"errors": [], "warnings": [], "info": []}
    frontmatter, body = parse_frontmatter(skill_dir)
    skill_md_path = skill_dir / "SKILL.md"

    unexpected_keys = set(frontmatter) - ALLOWED_FRONTMATTER_KEYS
    if unexpected_keys:
        add_finding(
            findings,
            "errors",
            f"Unexpected frontmatter keys: {', '.join(sorted(unexpected_keys))}.",
        )

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        add_finding(findings, "errors", "Frontmatter 'name' is missing or invalid.")
        name = ""
    else:
        name = name.strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            add_finding(findings, "errors", "Skill name must use lowercase letters, digits, and hyphens only.")
        if len(name) > MAX_SKILL_NAME_LENGTH:
            add_finding(findings, "errors", f"Skill name exceeds {MAX_SKILL_NAME_LENGTH} characters.")
        if name.startswith("-") or name.endswith("-") or "--" in name:
            add_finding(findings, "errors", "Skill name cannot start/end with hyphen or contain consecutive hyphens.")
        if any(name.startswith(prefix) for prefix in RESERVED_PREFIXES):
            add_finding(findings, "errors", "Skill names starting with 'claude' or 'anthropic' are reserved.")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        add_finding(findings, "errors", "Frontmatter 'description' is missing or invalid.")
        description = ""
    else:
        description = description.strip()
        if len(description) > MAX_DESCRIPTION_LENGTH:
            add_finding(findings, "errors", f"Description exceeds {MAX_DESCRIPTION_LENGTH} characters.")
        if "<" in description or ">" in description:
            add_finding(findings, "errors", "Description cannot contain angle brackets.")
        lowered = description.lower()
        if "use when" not in lowered:
            add_finding(findings, "warnings", "Description should include an explicit 'Use when ...' trigger phrase.")
        if not any(token in lowered for token in ("asks", "mentions", "says", "repo", "workflow", "file", ".md")):
            add_finding(findings, "warnings", "Description may be too abstract; add more concrete trigger language.")

    compatibility = frontmatter.get("compatibility")
    if compatibility:
        add_finding(
            findings,
            "info",
            "Frontmatter includes 'compatibility'. Note that the local quick_validate.py script does not check it.",
        )

    metadata = frontmatter.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        add_finding(findings, "warnings", "Frontmatter 'metadata' should be a mapping.")

    if word_count(body) > MAX_RECOMMENDED_WORDS:
        add_finding(findings, "warnings", f"SKILL.md body exceeds the recommended {MAX_RECOMMENDED_WORDS} words.")

    for heading in ("Overview", "Workflow", "Examples", "Troubleshooting"):
        if not has_heading(body, heading):
            add_finding(findings, "warnings", f"Body is missing a `{heading}` section.")

    if "references/" in body and not (skill_dir / "references").exists():
        add_finding(findings, "warnings", "Body references `references/` but the folder does not exist.")
    if (skill_dir / "references").exists() and "references/" not in body:
        add_finding(findings, "warnings", "Skill has a `references/` folder but SKILL.md does not point to it.")
    if (skill_dir / "scripts").exists() and "scripts/" not in body:
        add_finding(findings, "warnings", "Skill has a `scripts/` folder but SKILL.md does not mention it.")
    if (skill_dir / "assets").exists() and "assets/" not in body:
        add_finding(findings, "warnings", "Skill has an `assets/` folder but SKILL.md does not mention it.")

    openai_yaml = load_openai_yaml(skill_dir)
    if openai_yaml is None:
        add_finding(findings, "warnings", "agents/openai.yaml is missing.")
    else:
        interface = openai_yaml.get("interface")
        if not isinstance(interface, dict):
            add_finding(findings, "warnings", "agents/openai.yaml is missing an interface section.")
        else:
            display_name = interface.get("display_name")
            short_description = interface.get("short_description")
            default_prompt = interface.get("default_prompt")
            if not display_name:
                add_finding(findings, "warnings", "openai.yaml should include interface.display_name.")
            if not isinstance(short_description, str) or not (25 <= len(short_description) <= 64):
                add_finding(findings, "warnings", "openai.yaml short_description should be 25-64 characters.")
            if not isinstance(default_prompt, str) or f"${name}" not in default_prompt:
                add_finding(findings, "warnings", "openai.yaml default_prompt should explicitly mention the skill as `$skill-name`.")

    return {
        "skill_path": str(skill_md_path),
        "errors": findings["errors"],
        "warnings": findings["warnings"],
        "info": findings["info"],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# Skill Review", "", f"- Skill: `{report['skill_path']}`", ""]
    for level, title in (("errors", "Errors"), ("warnings", "Warnings"), ("info", "Info")):
        lines.append(f"## {title}")
        items = report[level]
        if items:
            lines.extend(f"- {item}" for item in items)
        else:
            lines.append("- None")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a skill using the richer PDF-style checklist.")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings as well as errors")
    args = parser.parse_args()

    report = review_skill(Path(args.skill_path).resolve())
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        print(render_markdown(report))

    if report["errors"]:
        return 1
    if args.strict and report["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
