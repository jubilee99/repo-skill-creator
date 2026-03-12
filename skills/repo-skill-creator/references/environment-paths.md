# Environment Paths

Use these defaults for this machine.

## Global Skill Location

- `/home/r.doi/.codex/skills`

Create globally reusable skills here when they should be available across repos in this environment.

## System Skill Creator Tools

- Initializer:
  `/home/r.doi/.codex/skills/.system/skill-creator/scripts/init_skill.py`
- Validator:
  `/home/r.doi/.codex/skills/.system/skill-creator/scripts/quick_validate.py`

Use the initializer for new skills and the validator before finishing.

## Workspace Roots

- Main multi-repo workspace:
  `/volume1/docker`
- Example trusted repos from current config:
  - `/volume1/docker`
  - `/volume1/docker/m365schedule`
  - `/volume1/docker/synaple`
  - `/volume1/docker/symphony`

## Local Notes

- Repo analysis should prefer `AGENTS.md`, `WORKFLOW.md`, `README.md`, and common manifests.
- Current MCP servers configured in `/home/r.doi/.codex/config.toml` include `linear` and `playwright`.
- Keep this environment knowledge in references, not in target skill frontmatter, unless the dependency must affect triggering.
