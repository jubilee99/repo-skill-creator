#!/usr/bin/env python3
"""Analyze a repository and emit skill-design context."""

from __future__ import annotations

import argparse
import json

from repo_skill_lib import analysis_to_markdown, build_repo_analysis


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a repository for skill creation.")
    parser.add_argument("repo_path", nargs="?", default=".", help="Repo path or any path inside the repo")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format",
    )
    args = parser.parse_args()

    analysis = build_repo_analysis(args.repo_path)
    if args.format == "json":
        print(json.dumps(analysis, indent=2, ensure_ascii=True))
    else:
        print(analysis_to_markdown(analysis))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
