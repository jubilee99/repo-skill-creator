#!/usr/bin/env python3
"""Scaffold a repo-derived skill with repo context references."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from repo_skill_lib import (
    DEFAULT_OUTPUT_PATH,
    SYSTEM_SKILL_ROOT,
    analysis_to_markdown,
    build_repo_analysis,
    build_test_plan_markdown,
    default_interface_values,
    draft_outline_markdown,
    normalize_skill_name,
    parse_metadata_args,
    parse_resource_arg,
    render_skill_md,
)


def run_init_skill(
    skill_name: str,
    output_path: Path,
    resources: list[str],
    interface_values: dict[str, str],
) -> None:
    command = [
        "python3",
        str(SYSTEM_SKILL_ROOT / "scripts" / "init_skill.py"),
        skill_name,
        "--path",
        str(output_path),
        "--resources",
        ",".join(resources),
    ]
    for key, value in interface_values.items():
        command.extend(["--interface", f"{key}={value}"])

    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a skill from repo signals.")
    parser.add_argument("repo_path", help="Repo path or any path inside the repo")
    parser.add_argument("skill_name", help="New skill name; normalized to kebab-case")
    parser.add_argument(
        "--output-path",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Directory that will contain the new skill folder",
    )
    parser.add_argument(
        "--resources",
        default="auto",
        help="Comma-separated resources or 'auto' (default: scripts,references and assets when hinted)",
    )
    parser.add_argument("--display-name", help="Override interface.display_name")
    parser.add_argument("--short-description", help="Override interface.short_description")
    parser.add_argument("--default-prompt", help="Override interface.default_prompt")
    parser.add_argument("--license", dest="license_name", help="Optional frontmatter license value")
    parser.add_argument("--compatibility", help="Optional frontmatter compatibility note")
    parser.add_argument("--allowed-tools", help="Optional frontmatter allowed-tools value")
    parser.add_argument(
        "--metadata",
        action="append",
        default=[],
        help="Optional frontmatter metadata key=value pair (repeatable)",
    )
    parser.add_argument(
        "--no-test-plan",
        action="store_true",
        help="Skip generating references/test-plan.md",
    )
    args = parser.parse_args()

    skill_name = normalize_skill_name(args.skill_name)
    if not skill_name:
        raise SystemExit("Skill name must contain at least one letter or digit.")

    analysis = build_repo_analysis(args.repo_path)
    resources = parse_resource_arg(args.resources, analysis)
    output_path = Path(args.output_path).resolve()
    skill_dir = output_path / skill_name
    if skill_dir.exists():
        raise SystemExit(f"Skill directory already exists: {skill_dir}")

    interface_values = default_interface_values(skill_name, analysis["repo_name"])
    if args.display_name:
        interface_values["display_name"] = args.display_name
    if args.short_description:
        interface_values["short_description"] = args.short_description
    if args.default_prompt:
        interface_values["default_prompt"] = args.default_prompt

    frontmatter_extras = {
        "license": args.license_name,
        "compatibility": args.compatibility,
        "allowed-tools": args.allowed_tools,
        "metadata": parse_metadata_args(args.metadata) if args.metadata else None,
    }

    run_init_skill(skill_name, output_path, resources, interface_values)

    references_dir = skill_dir / "references"
    if not references_dir.exists():
        references_dir.mkdir(parents=True, exist_ok=True)

    (references_dir / "repo-context.md").write_text(
        analysis_to_markdown(analysis),
        encoding="utf-8",
    )
    (references_dir / "draft-outline.md").write_text(
        draft_outline_markdown(analysis, skill_name, resources),
        encoding="utf-8",
    )
    if not args.no_test_plan:
        (references_dir / "test-plan.md").write_text(
            build_test_plan_markdown(skill_name, analysis),
            encoding="utf-8",
        )
    (skill_dir / "SKILL.md").write_text(
        render_skill_md(skill_name, analysis, resources, frontmatter_extras),
        encoding="utf-8",
    )

    print(f"Seeded repo-derived skill: {skill_dir}")
    print("Added references/repo-context.md and references/draft-outline.md")
    if not args.no_test_plan:
        print("Added references/test-plan.md")
    print("Replaced the default SKILL.md with a repo-aware draft")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
