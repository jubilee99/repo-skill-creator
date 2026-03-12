# MEMORY

## Purpose

This repo is the public packaging home for the shared `repo-skill-creator` Codex skill.

## Durable Notes

- Keep the distributed skill in `skills/repo-skill-creator/`.
- Keep human-facing repository docs at the root, not inside the skill folder.
- Validate the packaged skill with both the minimal validator and the richer review script before publishing changes.
- Do not hardcode user-specific home paths or workspace roots in packaged docs, references, or script defaults.
- Prefer `CODEX_HOME`, `CODEX_SKILLS_DIR`, and `SKILL_CREATOR_SYSTEM_PATH` overrides over machine-local absolute paths.
