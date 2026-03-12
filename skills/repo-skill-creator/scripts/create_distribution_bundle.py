#!/usr/bin/env python3
"""Create a distribution bundle for a skill outside the skill folder."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

from repo_skill_lib import load_openai_yaml, parse_frontmatter, title_case_skill_name


def read_repo_context(skill_dir: Path) -> dict[str, str]:
    path = skill_dir / "references" / "repo-context.md"
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    title_match = re.search(r"^# Repo Context: (.+)$", content, re.MULTILINE)
    if title_match:
        result["repo_name"] = title_match.group(1).strip()
    for key, pattern in (
        ("archetype", r"- Suggested skill archetype: `([^`]+)`"),
        ("reason", r"- Why: (.+)"),
    ):
        match = re.search(pattern, content)
        if match:
            result[key] = match.group(1).strip()
    return result


def zip_skill(skill_dir: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skill_dir.rglob("*")):
            if not path.is_file():
                continue
            archive.write(path, arcname=f"{skill_dir.name}/{path.relative_to(skill_dir)}")


def build_readme(skill_name: str, description: str, interface: dict[str, str], repo_context: dict[str, str]) -> str:
    display_name = interface.get("display_name") or title_case_skill_name(skill_name)
    default_prompt = interface.get("default_prompt") or f"Use ${skill_name} for this workflow."
    lines = [
        f"# {display_name}",
        "",
        description,
        "",
        "## What You Get",
        "",
        "- A reusable skill folder ready for Claude.ai or Claude Code.",
        "- Repo-specific workflow guidance instead of generic prompting.",
        "- Bundled references and scripts when the workflow needs them.",
        "",
    ]
    if repo_context:
        lines.extend(
            [
                "## Context",
                "",
                f"- Repo: `{repo_context.get('repo_name', 'unknown')}`",
                f"- Suggested archetype: `{repo_context.get('archetype', 'unknown')}`",
                f"- Why: {repo_context.get('reason', 'No repo context summary found.')}",
                "",
            ]
        )

    lines.extend(
        [
            "## Quick Start",
            "",
            "1. Download the zip bundle.",
            "2. Upload the zipped skill to Claude.ai or copy the skill folder into your Claude Code skills directory.",
            f"3. Start with: `{default_prompt}`",
            "",
            "## Why This Exists",
            "",
            "- Reduce repeated explanation of repo conventions.",
            "- Improve trigger accuracy with repo-specific task language.",
            "- Make validation and troubleshooting repeatable across sessions.",
            "",
        ]
    )
    return "\n".join(lines)


def build_install_guide(skill_name: str) -> str:
    lines = [
        f"# Install {skill_name}",
        "",
        "## Claude.ai",
        "",
        "1. Open Claude.ai.",
        "2. Go to Settings > Capabilities > Skills.",
        "3. Upload the zipped skill folder.",
        "4. Enable the skill and test a representative prompt.",
        "",
        "## Claude Code",
        "",
        "1. Copy the skill folder into your Codex/Claude Code skills directory.",
        "2. Verify `SKILL.md` is at the top level of the skill folder.",
        "3. Start a new task and use an obvious trigger prompt first.",
        "",
        "## Validation Before Sharing",
        "",
        "- Run the local validator and the full review script.",
        "- Test obvious, paraphrased, and unrelated prompts.",
        "- Confirm the skill works on a real task, not only on a static review.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a distribution bundle for a skill.")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where bundle docs and zip should be written",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_path).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    frontmatter, _body = parse_frontmatter(skill_dir)
    openai_yaml = load_openai_yaml(skill_dir) or {}
    interface = openai_yaml.get("interface") if isinstance(openai_yaml, dict) else {}
    if not isinstance(interface, dict):
        interface = {}
    repo_context = read_repo_context(skill_dir)

    zip_path = output_dir / f"{skill_dir.name}.zip"
    readme_path = output_dir / "README.md"
    install_path = output_dir / "INSTALL.md"

    zip_skill(skill_dir, zip_path)
    readme_path.write_text(
        build_readme(frontmatter["name"], frontmatter["description"], interface, repo_context),
        encoding="utf-8",
    )
    install_path.write_text(build_install_guide(frontmatter["name"]), encoding="utf-8")

    print(f"Wrote {zip_path}")
    print(f"Wrote {readme_path}")
    print(f"Wrote {install_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
