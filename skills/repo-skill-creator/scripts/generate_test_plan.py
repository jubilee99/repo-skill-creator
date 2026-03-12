#!/usr/bin/env python3
"""Generate a test plan for a skill from repo analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

from repo_skill_lib import build_repo_analysis, build_test_plan_markdown, parse_frontmatter


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a test plan for a skill.")
    parser.add_argument("--repo-path", required=True, help="Repo path or path inside the repo")
    parser.add_argument("--skill-path", help="Existing skill path; uses frontmatter name when present")
    parser.add_argument("--skill-name", help="Skill name when no skill path is provided")
    parser.add_argument("--output", help="Write markdown to a file instead of stdout")
    args = parser.parse_args()

    if args.skill_path:
        frontmatter, _body = parse_frontmatter(Path(args.skill_path).resolve())
        skill_name = frontmatter["name"]
    elif args.skill_name:
        skill_name = args.skill_name
    else:
        raise SystemExit("Provide --skill-path or --skill-name.")

    analysis = build_repo_analysis(args.repo_path)
    content = build_test_plan_markdown(skill_name, analysis)

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Wrote test plan to {args.output}")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
