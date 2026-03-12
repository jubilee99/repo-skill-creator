---
name: repo-skill-creator
description: Create and refine reusable Codex skills from an existing repository. Use when the user asks to turn repo context into a skill, analyze AGENTS.md or WORKFLOW.md before writing a skill, scaffold a new skill under /home/r.doi/.codex/skills, or says things like "this repo no skill o tsukutte", "repo kara skill ka shite", "skill creator o tsukutte", "build a skill for this repo", or "make this workflow reusable across repos".
---

# Repo Skill Creator

## Overview

Create repo-specific skills by scanning the real repository, extracting repeated workflows, scaffolding a draft skill, and validating the result before finishing.

Prefer deterministic helpers over long prose. Keep the main instructions lean, move detailed guidance into `references/`, and use `scripts/` when the same repo-analysis or scaffolding steps would otherwise be rewritten.

## Quick Start

1. Run `python3 scripts/analyze_repo.py /path/to/repo` to inspect manifests, docs, commands, and likely skill patterns.
2. Read `references/frontmatter-patterns.md` if the scope or trigger phrases are still vague.
3. Run `python3 scripts/init_repo_skill.py /path/to/repo <skill-name>` to scaffold a draft skill in `/home/r.doi/.codex/skills`.
4. Replace generic draft text with repo-specific commands, failure handling, examples, and validation steps.
5. Run both:
   - `python3 /home/r.doi/.codex/skills/.system/skill-creator/scripts/quick_validate.py <new-skill-path>`
   - `python3 scripts/review_skill.py <new-skill-path>`
6. Generate a distribution bundle when the skill is ready to share:
   - `python3 scripts/create_distribution_bundle.py <new-skill-path> --output-dir /tmp/<bundle-name>`

## Fundamentals

- Keep `SKILL.md` focused on the core workflow.
- Move deep detail into `references/`.
- Move deterministic or fragile logic into `scripts/`.
- Treat the description as the primary trigger mechanism.

## Workflow

1. Analyze the repo.
2. Plan the reusable parts.
3. Scaffold the draft skill.
4. Review and validate it.
5. Generate testing and distribution artifacts when needed.

## Planning And Design

### 1. Define a narrow skill outcome

- Choose 2-3 concrete use cases before writing files.
- Prefer a single repeated workflow over a vague repo-wide "helper" skill.
- Name the skill after the action it enables, not only after the repo.

### 2. Scan the real repository

- Run `scripts/analyze_repo.py` against the repo root or a subdirectory inside the repo.
- Read the generated doc summary before making assumptions about stack, commands, or architecture.
- If the repo has `AGENTS.md`, `WORKFLOW.md`, `README.md`, or design docs, treat them as primary signals for the skill draft.
- Read `references/environment-paths.md` when deciding whether the resulting skill should live globally in `/home/r.doi/.codex/skills` or alongside the repo for versioning.

### 3. Plan reusable contents

- Put repo-specific conventions, commands, and glossary items in `references/`.
- Put fragile or repetitive automation in `scripts/`.
- Add `assets/` only when the repo already relies on templates, starter files, prompts, or other files that should be copied into outputs.
- Use the PDF guidance distilled in `references/skill-creation-checklist.md` to keep the scope small and the trigger logic explicit.

### 4. Scaffold the draft skill

- Run `scripts/init_repo_skill.py` to call the system `init_skill.py` and seed:
  - `SKILL.md`
  - `references/repo-context.md`
  - `references/draft-outline.md`
  - `references/test-plan.md`
- Review the generated frontmatter immediately. The draft is a starting point, not the final truth.
- If the repo analysis is noisy, rerun the scaffold with a narrower repo path or rename the skill to match the actual workflow.

### 5. Harden the skill

- Keep frontmatter to `name` and `description` by default.
- Make the description contain both:
  - what the skill does
  - when it should trigger
- Add direct examples of user requests the skill should handle.
- Add validation steps and failure handling near the relevant workflow step instead of burying them at the end.
- Move long reference material out of `SKILL.md` once the body starts to feel repetitive or broad.
- Read `references/yaml-frontmatter-reference.md` when optional fields like `license`, `compatibility`, `allowed-tools`, or `metadata` are useful.

## Testing And Iteration

### 6. Validate the minimum structure

- Run the system validator:
  - `python3 /home/r.doi/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-path>`
- Run the richer reviewer:
  - `python3 scripts/review_skill.py <skill-path>`

### 7. Test behavior

- Test triggering with:
  - obvious requests
  - paraphrased requests
  - unrelated requests that should not trigger
- Generate or refresh a test plan:
  - `python3 scripts/generate_test_plan.py --repo-path /path/to/repo --skill-path <skill-path> --output <skill-path>/references/test-plan.md`
- If the skill under-triggers, expand the description with better task language.
- If the skill over-triggers, narrow the description and add scope boundaries.
- After real repo work reveals missing steps, update the skill instead of relying on ad hoc prompting next time.
- Read `references/testing-and-iteration.md` when choosing between manual, scripted, and programmatic testing.

## Distribution And Sharing

### 8. Package the skill for others

- Generate a shareable bundle outside the skill folder:
  - `python3 scripts/create_distribution_bundle.py <skill-path> --output-dir /tmp/<bundle-name>`
- Keep human-facing docs like README and INSTALL guides outside the skill folder itself.
- Read `references/distribution-and-sharing.md` before publishing or handing the skill to teammates.

## Patterns And Troubleshooting

- Read `references/patterns-and-troubleshooting.md` when the workflow shape is unclear.
- Use `review_skill.py` findings to detect vague descriptions, missing sections, and stale UI metadata.
- When the workflow requires sequential steps or multi-service coordination, encode that shape explicitly in the generated skill.

## Examples

- "Use `repo-skill-creator` to turn this repo's AGENTS.md and workflow docs into a reusable skill."
- "Analyze `symphony` and scaffold a repo-aware skill with a test plan."
- "Review this generated skill and tell me why it under-triggers."

## Resource Map

- `scripts/analyze_repo.py`: Scan a repo and print a markdown or JSON summary that is useful while designing a skill.
- `scripts/init_repo_skill.py`: Scaffold a repo-derived skill and write a first draft of `SKILL.md` plus repo context references.
- `scripts/review_skill.py`: Run a richer checklist against a skill and flag structural or trigger-quality issues.
- `scripts/generate_test_plan.py`: Generate a trigger/functional/performance test plan for a skill.
- `scripts/create_distribution_bundle.py`: Create a zip plus human-facing README and install guide outside the skill folder.
- `references/skill-creation-checklist.md`: Condensed workflow and validation checklist from the PDF guide.
- `references/frontmatter-patterns.md`: Good and bad trigger descriptions, including Japanese phrasing examples.
- `references/yaml-frontmatter-reference.md`: Supported required and optional frontmatter fields.
- `references/testing-and-iteration.md`: Guidance on trigger tests, functional tests, and iteration signals.
- `references/distribution-and-sharing.md`: Packaging and sharing guidance for finished skills.
- `references/patterns-and-troubleshooting.md`: Common workflow patterns and fixes for bad skill behavior.
- `references/environment-paths.md`: Paths, defaults, and local environment notes for this machine.

## Output Standard

- Deliver a usable skill, not only notes.
- Leave the generated skill in a validated state or state clearly what still requires manual judgment.
- Prefer repo-backed facts over generic advice.
