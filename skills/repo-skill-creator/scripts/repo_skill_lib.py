#!/usr/bin/env python3
"""Helpers for building repo-derived Codex skills."""

from __future__ import annotations

import json
import re
import subprocess
import textwrap
import tomllib
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml

SYSTEM_SKILL_ROOT = Path("/home/r.doi/.codex/skills/.system/skill-creator")
DEFAULT_OUTPUT_PATH = Path("/home/r.doi/.codex/skills")
DEFAULT_RESOURCES = ["scripts", "references"]
MAX_CONTEXT_FILES = 8
MAX_HEADINGS_PER_DOC = 6
NOISY_PARTS = {"node_modules", ".git", "__pycache__", "dist", "build", "coverage", ".next", "deps"}
NOISY_PREFIXES = ("log", "state")

DOC_PRIORITY_PATTERNS: tuple[tuple[str, int], ...] = (
    ("AGENTS.md", 0),
    ("**/AGENTS.md", 1),
    ("WORKFLOW.md", 2),
    ("**/WORKFLOW.md", 3),
    ("**/*.WORKFLOW.md", 4),
    ("README.md", 5),
    ("**/README.md", 6),
    ("README*", 7),
    ("CONTRIBUTING.md", 8),
    ("HANDOFF.md", 9),
    ("**/SPEC.md", 10),
    ("docs/**/workflow*.md", 11),
    ("docs/**/architecture*.md", 12),
    ("docs/**/design*.md", 13),
    ("docs/**/*.md", 14),
)

MANIFEST_RULES: tuple[tuple[str, str], ...] = (
    ("package.json", "node"),
    ("pnpm-lock.yaml", "pnpm"),
    ("package-lock.json", "npm"),
    ("yarn.lock", "yarn"),
    ("bun.lockb", "bun"),
    ("pyproject.toml", "python"),
    ("requirements.txt", "python"),
    ("poetry.lock", "python"),
    ("mix.exs", "elixir"),
    ("Cargo.toml", "rust"),
    ("go.mod", "go"),
    ("Gemfile", "ruby"),
    ("composer.json", "php"),
    ("Dockerfile", "docker"),
    ("docker-compose.yml", "docker-compose"),
    ("docker-compose.yaml", "docker-compose"),
    ("Makefile", "make"),
)

ASSET_HINT_PATTERNS = (
    "assets/**",
    "templates/**",
    "boilerplate/**",
    "prompts/**",
    "*.prompt",
    "*.svg",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.pptx",
    "*.docx",
)


def normalize_skill_name(raw_name: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", raw_name.strip().lower())
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def title_case_skill_name(skill_name: str) -> str:
    return " ".join(part.capitalize() for part in skill_name.split("-"))


def run_command(args: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return completed.stdout.strip()


def discover_repo_root(path: str | Path) -> Path:
    candidate = Path(path).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    git_root = run_command(["git", "-C", str(candidate), "rev-parse", "--show-toplevel"])
    return Path(git_root).resolve() if git_root else candidate


def list_repo_files(repo_root: Path) -> list[Path]:
    git_files = run_command(["git", "-C", str(repo_root), "ls-files"])
    if git_files:
        return [repo_root / line for line in git_files.splitlines() if line.strip()]

    files: list[Path] = []
    for path in repo_root.rglob("*"):
        if path.is_file():
            files.append(path)
    return files


def repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def is_noise_path(path: Path, repo_root: Path) -> bool:
    rel = repo_relative(path, repo_root)
    for part in rel.split("/"):
        if part in NOISY_PARTS:
            return True
        if any(part.startswith(prefix) for prefix in NOISY_PREFIXES):
            return True
        if ".backup-" in part:
            return True
    return False


def read_text(path: Path, limit_lines: int = 220) -> str:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = path.read_text(encoding="utf-8", errors="ignore")
    return "\n".join(content.splitlines()[:limit_lines])


def extract_markdown_headings(content: str, limit: int = MAX_HEADINGS_PER_DOC) -> list[str]:
    headings = []
    for line in content.splitlines():
        if re.match(r"^#{1,3}\s+\S", line):
            headings.append(re.sub(r"^#{1,3}\s+", "", line).strip())
        if len(headings) >= limit:
            break
    return headings


def extract_preview_lines(content: str, limit: int = 4) -> list[str]:
    preview = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        preview.append(stripped)
        if len(preview) >= limit:
            break
    return preview


def collect_context_files(repo_root: Path, files: list[Path]) -> list[Path]:
    rel_map = {
        repo_relative(path, repo_root): path
        for path in files
        if not is_noise_path(path, repo_root)
    }
    scored: dict[str, tuple[int, int]] = {}
    for rel in rel_map:
        for pattern, base_score in DOC_PRIORITY_PATTERNS:
            if fnmatch(rel, pattern):
                score = (base_score, len(rel.split("/")))
                if rel not in scored or score < scored[rel]:
                    scored[rel] = score

    if not scored:
        for rel, path in rel_map.items():
            name = path.name.lower()
            if path.suffix.lower() == ".md" and any(
                token in name for token in ("readme", "workflow", "guide", "design", "spec", "runbook")
            ):
                scored[rel] = (9, len(rel.split("/")))

    ordered = sorted(scored.items(), key=lambda item: (item[1][0], item[1][1], item[0]))
    return [rel_map[rel] for rel, _score in ordered[:MAX_CONTEXT_FILES]]


def detect_package_manager(files: list[Path], repo_root: Path) -> str:
    rels = {repo_relative(path, repo_root) for path in files}
    if "pnpm-lock.yaml" in rels:
        return "pnpm"
    if "yarn.lock" in rels:
        return "yarn"
    if "bun.lockb" in rels:
        return "bun"
    return "npm"


def detect_package_manager_for_dir(files: list[Path], repo_root: Path, manifest_dir: Path) -> str:
    rel_dir = repo_relative(manifest_dir, repo_root)
    rels = {repo_relative(path, repo_root) for path in files}
    for filename, manager in (
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("bun.lockb", "bun"),
        ("package-lock.json", "npm"),
    ):
        candidate = f"{rel_dir}/{filename}" if rel_dir != "." else filename
        if candidate in rels:
            return manager
    return detect_package_manager(files, repo_root)


def format_command(command: str, cwd: Path, repo_root: Path) -> str:
    rel_dir = repo_relative(cwd, repo_root)
    if rel_dir == ".":
        return command
    return f"cd {rel_dir} && {command}"


def find_by_name(files: list[Path], repo_root: Path, filename: str) -> list[Path]:
    matches = [path for path in files if path.name == filename and not is_noise_path(path, repo_root)]
    return sorted(
        matches,
        key=lambda path: (len(repo_relative(path, repo_root).split("/")), repo_relative(path, repo_root)),
    )


def parse_makefile_targets(path: Path) -> list[str]:
    targets: list[str] = []
    for line in read_text(path, limit_lines=300).splitlines():
        match = re.match(r"^([A-Za-z0-9_.-]+):(?:\s|$)", line)
        if not match:
            continue
        target = match.group(1)
        if target.startswith("."):
            continue
        if target not in targets:
            targets.append(target)
    return targets[:8]


def analyze_manifests(repo_root: Path, files: list[Path]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    rels = {
        repo_relative(path, repo_root): path
        for path in files
        if not is_noise_path(path, repo_root)
    }
    manifests: list[dict[str, Any]] = []
    stacks: list[str] = []
    commands: list[str] = []

    def add_stack(value: str) -> None:
        if value not in stacks:
            stacks.append(value)

    def add_command(value: str) -> None:
        if value and value not in commands:
            commands.append(value)

    seen_manifests: set[tuple[str, str]] = set()

    def add_manifest(path: Path, manifest_type: str, **details: Any) -> None:
        rel_path = repo_relative(path, repo_root)
        key = (rel_path, manifest_type)
        if key in seen_manifests:
            return
        seen_manifests.add(key)
        entry: dict[str, Any] = {"path": rel_path, "type": manifest_type}
        entry.update(details)
        manifests.append(entry)

    for rel_path, stack in MANIFEST_RULES:
        path = rels.get(rel_path)
        if path:
            add_stack(stack)

    for pyproject in find_by_name(files, repo_root, "pyproject.toml")[:4]:
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            data = {}
        add_stack("python")
        add_manifest(pyproject, "python")
        project_scripts = ((data.get("project") or {}).get("scripts") or {}).keys()
        for script_name in sorted(project_scripts):
            add_command(format_command(f"python -m {script_name}", pyproject.parent, repo_root))
        for command in ("pytest", "ruff check .", "ruff format .", "mypy ."):
            add_command(format_command(command, pyproject.parent, repo_root))

    for requirements in find_by_name(files, repo_root, "requirements.txt")[:4]:
        add_stack("python")
        add_manifest(requirements, "python")
        add_command(format_command("pytest", requirements.parent, repo_root))

    for mix_file in find_by_name(files, repo_root, "mix.exs")[:4]:
        add_stack("elixir")
        add_manifest(mix_file, "elixir")
        for command in ("mix deps.get", "mix test", "mix format"):
            add_command(format_command(command, mix_file.parent, repo_root))

    for cargo_file in find_by_name(files, repo_root, "Cargo.toml")[:4]:
        add_stack("rust")
        add_manifest(cargo_file, "rust")
        for command in ("cargo test", "cargo fmt", "cargo clippy"):
            add_command(format_command(command, cargo_file.parent, repo_root))

    for go_file in find_by_name(files, repo_root, "go.mod")[:4]:
        add_stack("go")
        add_manifest(go_file, "go")
        for command in ("go test ./...", "go vet ./..."):
            add_command(format_command(command, go_file.parent, repo_root))

    for package_json in find_by_name(files, repo_root, "package.json")[:4]:
        package_manager = detect_package_manager_for_dir(files, repo_root, package_json.parent)
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        scripts = sorted((data.get("scripts") or {}).keys())
        add_stack("node")
        add_manifest(package_json, "node", scripts=scripts[:10])
        for script_name in ("lint", "test", "build", "dev", "start", "check", "typecheck", "format"):
            if script_name in scripts:
                add_command(format_command(f"{package_manager} run {script_name}", package_json.parent, repo_root))
        deps = {
            *list((data.get("dependencies") or {}).keys()),
            *list((data.get("devDependencies") or {}).keys()),
        }
        for dep_name, label in (
            ("react", "react"),
            ("next", "next.js"),
            ("vite", "vite"),
            ("typescript", "typescript"),
            ("express", "express"),
            ("astro", "astro"),
            ("svelte", "svelte"),
            ("vue", "vue"),
        ):
            if dep_name in deps:
                add_stack(label)

    for makefile in find_by_name(files, repo_root, "Makefile")[:4]:
        targets = parse_makefile_targets(makefile)
        add_stack("make")
        add_manifest(makefile, "make", targets=targets)
        for target in ("test", "lint", "build", "check", "validate", "format"):
            if target in targets:
                add_command(format_command(f"make {target}", makefile.parent, repo_root))

    for compose_name in ("docker-compose.yml", "docker-compose.yaml"):
        for compose_file in find_by_name(files, repo_root, compose_name)[:4]:
            add_stack("docker-compose")
            add_manifest(compose_file, "docker-compose")
            add_command(format_command("docker compose config", compose_file.parent, repo_root))

    return manifests, stacks, commands


def analyze_docs(repo_root: Path, files: list[Path]) -> list[dict[str, Any]]:
    docs = []
    for path in collect_context_files(repo_root, files):
        content = read_text(path)
        headings = extract_markdown_headings(content)
        previews = extract_preview_lines(content)
        docs.append(
            {
                "path": repo_relative(path, repo_root),
                "headings": headings,
                "preview": previews,
            }
        )
    return docs


def detect_assets(repo_root: Path, files: list[Path]) -> list[str]:
    rels = {
        repo_relative(path, repo_root): path
        for path in files
        if not is_noise_path(path, repo_root)
    }
    found: list[str] = []
    for pattern in ASSET_HINT_PATTERNS:
        for path in repo_root.glob(pattern):
            if not path.is_file():
                continue
            rel = repo_relative(path, repo_root)
            if rel in rels and rel not in found:
                found.append(rel)
    return found[:8]


def classify_archetype(repo_name: str, stacks: list[str], docs: list[dict[str, Any]]) -> tuple[str, str]:
    text_blob = " ".join(
        [repo_name]
        + stacks
        + [doc["path"] for doc in docs]
        + [heading for doc in docs for heading in doc["headings"]]
        + [line for doc in docs for line in doc["preview"]]
    ).lower()

    if any(token in text_blob for token in ("mcp", "connector", "extension", "playwright", "linear")):
        return "mcp-enhancement", "Repo docs or stack mention MCP-style tool integration."

    if any(token in text_blob for token in ("design", "ui", "frontend", "component", "layout", "theme")) and any(
        token in stacks for token in ("react", "next.js", "vite", "typescript", "vue", "svelte")
    ):
        return "document-asset-creation", "Repo signals point to frontend or design-heavy output."

    return "workflow-automation", "Repo signals point to repeated implementation or operational workflows."


def suggest_resources(
    docs: list[dict[str, Any]],
    commands: list[str],
    assets: list[str],
) -> list[dict[str, str]]:
    suggestions = [
        {
            "name": "references",
            "reason": "Keep repo conventions, commands, and glossary entries out of SKILL.md.",
        }
    ]

    if commands or any("workflow" in doc["path"].lower() for doc in docs):
        suggestions.append(
            {
                "name": "scripts",
                "reason": "Use scripts for repeated validation, scaffolding, or fragile repo-specific automation.",
            }
        )

    if assets:
        suggestions.append(
            {
                "name": "assets",
                "reason": "Repo already contains template-like files or artifacts that may need to be copied into outputs.",
            }
        )

    return suggestions


def build_trigger_phrases(repo_name: str, docs: list[dict[str, Any]], archetype: str) -> list[str]:
    phrases = [
        f"work in the {repo_name} repo",
        f"follow {repo_name} conventions",
        f"turn {repo_name} workflows into a skill",
        f"build a repo skill for {repo_name}",
    ]

    if any(doc["path"].endswith("AGENTS.md") for doc in docs):
        phrases.append(f"follow the {repo_name} AGENTS.md instructions")
    if any("workflow" in doc["path"].lower() for doc in docs):
        phrases.append(f"reuse the {repo_name} workflow as a skill")
    if archetype == "mcp-enhancement":
        phrases.append(f"teach Codex how to use the {repo_name} MCP workflow")

    seen: list[str] = []
    for phrase in phrases:
        if phrase not in seen:
            seen.append(phrase)
    return seen[:6]


def build_description(repo_name: str, docs: list[dict[str, Any]], stacks: list[str]) -> str:
    repo_label = repo_name.replace("-", " ")
    stack_text = ""
    if stacks:
        stack_text = " using the repo's " + ", ".join(stacks[:4]) + " workflows"

    signals = []
    if any(doc["path"].endswith("AGENTS.md") for doc in docs):
        signals.append("AGENTS.md guidance")
    if any("workflow" in doc["path"].lower() for doc in docs):
        signals.append("workflow docs")
    if any(doc["path"].lower().startswith("docs/") for doc in docs):
        signals.append("project docs")

    signal_text = ""
    if signals:
        signal_text = " Read " + ", ".join(signals[:3]) + " before making assumptions."

    return (
        f"Repository-specific workflow and conventions for {repo_label}. "
        f"Use when Codex needs to work inside the {repo_name} repo, follow project-specific commands or docs, "
        f"or convert repeated implementation steps into a reusable skill{stack_text}.{signal_text}"
    )


def build_repo_analysis(repo_path: str | Path) -> dict[str, Any]:
    repo_root = discover_repo_root(repo_path)
    files = list_repo_files(repo_root)
    manifests, stacks, commands = analyze_manifests(repo_root, files)
    docs = analyze_docs(repo_root, files)
    assets = detect_assets(repo_root, files)
    archetype, archetype_reason = classify_archetype(repo_root.name, stacks, docs)
    resource_suggestions = suggest_resources(docs, commands, assets)

    return {
        "repo_root": str(repo_root),
        "repo_name": repo_root.name,
        "manifests": manifests,
        "tech_stack": stacks,
        "docs": docs,
        "assets": assets,
        "commands": commands[:10],
        "archetype": archetype,
        "archetype_reason": archetype_reason,
        "suggested_resources": resource_suggestions,
        "trigger_phrases": build_trigger_phrases(repo_root.name, docs, archetype),
        "description": build_description(repo_root.name, docs, stacks),
    }


def analysis_to_markdown(analysis: dict[str, Any]) -> str:
    lines = [
        f"# Repo Context: {analysis['repo_name']}",
        "",
        f"- Root: `{analysis['repo_root']}`",
        f"- Suggested skill archetype: `{analysis['archetype']}`",
        f"- Why: {analysis['archetype_reason']}",
        "",
        "## Tech Stack",
    ]

    if analysis["tech_stack"]:
        lines.extend(f"- {item}" for item in analysis["tech_stack"])
    else:
        lines.append("- No obvious stack signals found from common manifests.")

    lines.extend(["", "## Manifests"])
    if analysis["manifests"]:
        for manifest in analysis["manifests"]:
            details = []
            if manifest.get("type"):
                details.append(f"type: {manifest['type']}")
            if manifest.get("scripts"):
                details.append("scripts: " + ", ".join(manifest["scripts"]))
            if manifest.get("targets"):
                details.append("targets: " + ", ".join(manifest["targets"]))
            detail_text = f" ({'; '.join(details)})" if details else ""
            lines.append(f"- `{manifest['path']}`{detail_text}")
    else:
        lines.append("- No common manifests detected.")

    lines.extend(["", "## Docs"])
    if analysis["docs"]:
        for doc in analysis["docs"]:
            lines.append(f"- `{doc['path']}`")
            if doc["headings"]:
                lines.append(f"  headings: {', '.join(doc['headings'])}")
            elif doc["preview"]:
                lines.append(f"  preview: {' | '.join(doc['preview'])}")
    else:
        lines.append("- No high-signal markdown docs were detected.")

    lines.extend(["", "## Candidate Commands"])
    if analysis["commands"]:
        lines.extend(f"- `{command}`" for command in analysis["commands"])
    else:
        lines.append("- No canonical validation commands inferred automatically.")

    lines.extend(["", "## Suggested Resources"])
    for resource in analysis["suggested_resources"]:
        lines.append(f"- `{resource['name']}`: {resource['reason']}")

    lines.extend(["", "## Trigger Phrases"])
    lines.extend(f"- {phrase}" for phrase in analysis["trigger_phrases"])

    if analysis["assets"]:
        lines.extend(["", "## Asset-Like Files"])
        lines.extend(f"- `{asset}`" for asset in analysis["assets"])

    lines.extend(["", "## Draft Description", analysis["description"], ""])
    return "\n".join(lines)


def draft_outline_markdown(
    analysis: dict[str, Any],
    skill_name: str,
    selected_resources: list[str],
) -> str:
    title = title_case_skill_name(skill_name)
    lines = [
        f"# Draft Outline For {title}",
        "",
        "## Use Cases To Confirm",
        f"- Work inside `{analysis['repo_name']}` while following repo-specific conventions.",
        "- Turn repeated implementation or operational steps into deterministic instructions.",
        "- Add only the repo knowledge that would otherwise need to be rediscovered in each session.",
        "",
        "## Recommended First Sections",
        "- Overview",
        "- Workflow",
        "- Validation",
        "- Failure handling",
        "- Resource map",
        "",
        "## Suggested Trigger Phrases",
    ]
    lines.extend(f"- {phrase}" for phrase in analysis["trigger_phrases"])

    lines.extend(["", "## Commands To Verify", *[f"- `{command}`" for command in analysis["commands"] or ["Add real validation commands manually."]]])

    lines.extend(["", "## Resource Decisions"])
    for resource in analysis["suggested_resources"]:
        marker = "selected" if resource["name"] in selected_resources else "not selected yet"
        lines.append(f"- `{resource['name']}` ({marker}): {resource['reason']}")

    if analysis["docs"]:
        lines.extend(["", "## Docs To Read Before Finalizing"])
        lines.extend(f"- `{doc['path']}`" for doc in analysis["docs"])

    lines.extend(
        [
            "",
            "## Manual Review Questions",
            "- Which 2-3 user requests should trigger this skill every time?",
            "- Which repo commands are authoritative enough to include as validation steps?",
            "- Which details belong in `references/` instead of the main `SKILL.md` body?",
            "",
        ]
    )
    return "\n".join(lines)


def render_skill_md(
    skill_name: str,
    analysis: dict[str, Any],
    selected_resources: list[str],
    frontmatter_extras: dict[str, Any] | None = None,
) -> str:
    title = title_case_skill_name(skill_name)
    docs = [f"`{doc['path']}`" for doc in analysis["docs"][:4]]
    doc_text = ", ".join(docs) if docs else "repo docs"
    stack_text = ", ".join(analysis["tech_stack"][:5]) if analysis["tech_stack"] else "repo-specific tooling"
    command_lines = analysis["commands"][:6] or ["Add canonical repo validation commands here."]
    trigger_lines = analysis["trigger_phrases"][:5]
    example_requests = build_example_requests(analysis)
    troubleshooting_lines = build_troubleshooting_items(analysis)

    resource_lines = [
        "- `references/repo-context.md`: Generated repo scan with docs, manifests, and candidate commands.",
        "- `references/draft-outline.md`: Repo-specific planning notes for refining this draft.",
        "- `references/test-plan.md`: Trigger, functional, and performance checks derived from repo signals.",
    ]
    if "scripts" in selected_resources:
        resource_lines.append("- `scripts/`: Add deterministic helpers for repeated or fragile repo workflows.")
    if "assets" in selected_resources:
        resource_lines.append("- `assets/`: Add repo templates or starter files only if they are used in real outputs.")

    frontmatter = render_frontmatter(skill_name, analysis["description"], frontmatter_extras)

    body = f"""{frontmatter}

# {title}

## Overview

Use this skill when working inside `{analysis["repo_name"]}` and the task depends on repo-specific conventions, repeated workflows, or documents that should not be re-discovered from scratch. Start by reading `references/repo-context.md`, then confirm the exact outcome before changing code.

## Workflow

1. Confirm the task belongs to `{analysis["repo_name"]}` and restate the intended outcome.
2. Read {doc_text} before making assumptions about commands, structure, or project rules.
3. Prefer the repo's canonical commands and file layout over generic language-model defaults.
4. Move repeated, fragile, or validation-heavy steps into `scripts/` instead of expanding prose in this file.
5. Validate with the repo's real commands before finalizing.
6. Update this skill when the repo adds new tooling, workflows, or constraints.

## Repo Signals

- Primary stack: {stack_text}
- Suggested archetype: `{analysis["archetype"]}`
- Why: {analysis["archetype_reason"]}

## Trigger Examples

{chr(10).join(f"- {line}" for line in trigger_lines)}

## Validation

{chr(10).join(f"- `{line}`" if not line.startswith("Add ") else f"- {line}" for line in command_lines)}

## Examples

{chr(10).join(f"- {line}" for line in example_requests)}

## Troubleshooting

{chr(10).join(f"- {line}" for line in troubleshooting_lines)}

## Testing Notes

- Run the checks in `references/test-plan.md`.
- Compare behavior with and without this skill enabled when the workflow matters.
- Update the trigger phrases if obvious or paraphrased requests fail to load the skill.

## Resource Map

{chr(10).join(resource_lines)}

## Draft Status

- This draft was generated from repo signals and needs a manual review before production use.
- Replace generic validation or trigger text with the repo's strongest examples.
- Keep frontmatter focused on what the skill does and when it should trigger.
"""
    return body


def default_interface_values(skill_name: str, repo_name: str) -> dict[str, str]:
    display_name = title_case_skill_name(skill_name)
    short_description = f"Repo-specific workflows for {repo_name}"
    if len(short_description) > 64:
        short_description = f"Repo workflows for {repo_name}"[:64]
    default_prompt = (
        f"Use ${skill_name} to follow the {repo_name} repository workflows, commands, and conventions."
    )
    return {
        "display_name": display_name,
        "short_description": short_description,
        "default_prompt": default_prompt,
    }


def parse_resource_arg(raw_value: str, analysis: dict[str, Any]) -> list[str]:
    value = raw_value.strip().lower()
    if value in ("", "auto"):
        result = DEFAULT_RESOURCES.copy()
        if any(item["name"] == "assets" for item in analysis["suggested_resources"]):
            result.append("assets")
        return result

    items = [item.strip() for item in raw_value.split(",") if item.strip()]
    seen: list[str] = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


def wrap_paragraph(text: str) -> str:
    return "\n".join(textwrap.wrap(text, width=92))


def parse_metadata_args(items: list[str]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid metadata '{item}'. Use key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Invalid metadata '{item}'. Key is empty.")
        metadata[key] = value
    return metadata


def parse_frontmatter(skill_path: str | Path) -> tuple[dict[str, Any], str]:
    path = Path(skill_path)
    skill_md = path / "SKILL.md" if path.is_dir() else path
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
    if not match:
        raise ValueError(f"Invalid or missing frontmatter in {skill_md}")
    frontmatter = yaml.safe_load(match.group(1)) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError(f"Frontmatter must be a mapping in {skill_md}")
    return frontmatter, match.group(2)


def load_openai_yaml(skill_dir: str | Path) -> dict[str, Any] | None:
    path = Path(skill_dir) / "agents" / "openai.yaml"
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return None
    return data


def render_frontmatter(skill_name: str, description: str, extras: dict[str, Any] | None = None) -> str:
    data: dict[str, Any] = {"name": skill_name, "description": description}
    extras = extras or {}
    for key in ("license", "compatibility", "allowed-tools", "metadata"):
        value = extras.get(key)
        if value not in (None, "", {}, []):
            data[key] = value
    rendered = yaml.safe_dump(data, sort_keys=False, allow_unicode=False).strip()
    return f"---\n{rendered}\n---"


def build_example_requests(analysis: dict[str, Any]) -> list[str]:
    repo_name = analysis["repo_name"]
    docs = [doc["path"] for doc in analysis["docs"][:3]]
    examples = [
        f'User says: "Work in the {repo_name} repo and follow its documented workflow."',
        f'User says: "Turn the repeated {repo_name} implementation steps into a reusable skill."',
    ]
    if docs:
        examples.append(f'User says: "Read {docs[0]} and apply those repo rules before changing code."')
    if analysis["archetype"] == "mcp-enhancement":
        examples.append(f'User says: "Use the {repo_name} MCP-oriented workflow instead of generic tool calling."')
    return examples[:4]


def build_negative_trigger_examples(analysis: dict[str, Any]) -> list[str]:
    repo_name = analysis["repo_name"]
    examples = [
        'User says: "What is the weather today?"',
        'User says: "Write a generic Python script."',
        f'User says: "Give me general advice unrelated to {repo_name}."',
    ]
    if analysis["archetype"] == "document-asset-creation":
        examples.append('User says: "Create a random spreadsheet with no repo context."')
    return examples[:4]


def build_troubleshooting_items(analysis: dict[str, Any]) -> list[str]:
    items = [
        "If the skill over-triggers, narrow the description and remove generic wording like 'helps with this repo'.",
        "If the skill under-triggers, add the exact user phrasing your team actually uses.",
    ]
    if analysis["commands"]:
        items.append("If validation is unreliable, replace guessed commands with the repo's canonical commands.")
    if any(doc["path"].endswith("AGENTS.md") for doc in analysis["docs"]):
        items.append("If outputs conflict with the repo, re-read `AGENTS.md` and move the missing rule into references.")
    if any("workflow" in doc["path"].lower() for doc in analysis["docs"]):
        items.append("If the workflow order keeps drifting, encode the order explicitly in numbered steps or scripts.")
    return items[:5]


def build_test_plan_markdown(skill_name: str, analysis: dict[str, Any]) -> str:
    title = title_case_skill_name(skill_name)
    trigger_examples = build_example_requests(analysis)
    negative_examples = build_negative_trigger_examples(analysis)
    validation_commands = analysis["commands"][:6]

    lines = [
        f"# Test Plan For {title}",
        "",
        "## 1. Triggering Tests",
        "",
        "### Should Trigger",
    ]
    lines.extend(f"- {item}" for item in trigger_examples)
    lines.extend(["", "### Should Not Trigger"])
    lines.extend(f"- {item}" for item in negative_examples)
    lines.extend(
        [
            "",
            "## 2. Functional Tests",
            "",
            "- Confirm the skill reads the repo context before editing code.",
            "- Confirm the skill uses repo-specific commands instead of generic defaults.",
            "- Confirm errors and edge cases mentioned in the repo docs are handled explicitly.",
        ]
    )
    if validation_commands:
        lines.append("- Validate with these commands:")
        lines.extend(f"  - `{command}`" for command in validation_commands)
    else:
        lines.append("- Add the repo's real validation commands before calling the skill production-ready.")

    lines.extend(
        [
            "",
            "## 3. Performance Comparison",
            "",
            "Compare one representative task with and without the skill.",
            "",
            "- Baseline: note messages, tool calls, retries, and token usage without the skill.",
            f"- With `{skill_name}`: note messages, tool calls, retries, and token usage with the skill.",
            "- Record whether the skill reduced clarification loops or validation failures.",
            "",
            "## 4. Test Surfaces",
            "",
            "- Manual: run the trigger and functional tests in Claude.ai or Claude Code.",
            "- Scripted: automate stable test prompts in Claude Code when the workflow becomes important.",
            "- Programmatic: use the API only if this skill is moving into productized or large-scale use.",
            "",
            "## 5. Iteration Notes",
            "",
            "- If the skill misses obvious prompts, improve the description.",
            "- If the skill fires on unrelated prompts, tighten the scope and add negative examples.",
            "- If the workflow succeeds only after manual correction, move the missing logic into the skill body or scripts.",
            "",
        ]
    )
    return "\n".join(lines)
