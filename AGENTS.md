# AGENTS

## 1. WHAT & WHY

This repository packages the shared `repo-skill-creator` skill for GitHub distribution.
The real skill must stay under `skills/repo-skill-creator/` so the repository root can
contain human-facing documentation without polluting the skill folder.

## 2. HOW

- Keep the skill contents in `skills/repo-skill-creator/`.
- Prefer editing the packaged skill directly in this repo once it becomes the public source.
- Validate with:
  - `python3 /home/r.doi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/repo-skill-creator`
  - `python3 skills/repo-skill-creator/scripts/review_skill.py skills/repo-skill-creator`

## 3. GUIDELINES

- Do not add extra docs inside `skills/repo-skill-creator/` unless they are part of the skill.
- Keep repo-level docs at the root.
- Remove `__pycache__` and other generated artifacts before committing.
- If the skill behavior changes, update both the root README and the skill references when needed.

## 4. ROUTER

- Skill logic: `skills/repo-skill-creator/SKILL.md`
- Human docs: `README.md`
- Durable repo memory: `.agent/memory/MEMORY.md`
- Session handoff: `HANDOFF.md`

## 5. MEMORY & HANDOFF

- Record durable repo-specific lessons in `.agent/memory/MEMORY.md`.
- Record current publishing status and next actions in `HANDOFF.md`.
