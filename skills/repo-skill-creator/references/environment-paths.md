# Environment Paths

Prefer portable defaults and explicit overrides over machine-specific absolute paths.

## Global Skill Location

- Default Codex skills directory: `${CODEX_HOME:-$HOME/.codex}/skills`
- Optional override for generators: `CODEX_SKILLS_DIR`

Create globally reusable skills here when they should be available across repos. If a skill should stay versioned with a single repository, place it in a repo-local folder and document that location clearly.

## System Skill Creator Tools

- Initializer: resolve the installed system `skill-creator` under the same skills root when possible.
- Validator: use the `quick_validate.py` that ships with your installed system `skill-creator`.
- Optional override for custom installs: `SKILL_CREATOR_SYSTEM_PATH`

Use the initializer for new skills and the validator before finishing. Avoid hardcoding user-specific home directories into the generated skill or its packaging docs.

## Workspace Roots

- Do not assume a fixed multi-repo workspace root.
- Analyze the repository path the user explicitly points at.
- If your environment has a shared workspace, treat it as a convenience only, not part of the skill's trigger logic.

## Local Notes

- Repo analysis should prefer `AGENTS.md`, `WORKFLOW.md`, `README.md`, and common manifests.
- Keep MCP-server or config-specific knowledge in references, not in target skill frontmatter, unless the dependency must affect triggering.
- When sharing a generated skill, remove local checkout paths, user names, and machine-only assumptions from examples and docs.
