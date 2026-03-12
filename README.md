# Repo Skill Creator

An opinionated Codex skill pack for turning an existing repository into a reusable
skill.

This repo packages the `repo-skill-creator` skill as a shareable GitHub repository.
The skill itself lives under `skills/repo-skill-creator/` so the repository can
contain human-facing docs without polluting the skill folder.

## What It Does

The packaged skill helps Codex:

- analyze a real repository before writing a skill
- scaffold a repo-derived skill with repo context
- review skill quality beyond basic frontmatter validation
- generate test plans for trigger, functional, and performance checks
- create a distribution bundle with a zip plus human-facing install docs

The current implementation is tailored to the local environment conventions used in
`/home/r.doi/.codex/skills` and `/volume1/docker`.

## Repo Layout

```text
repo-skill-creator/
├── README.md
├── AGENTS.md
├── HANDOFF.md
├── .agent/memory/MEMORY.md
└── skills/
    └── repo-skill-creator/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── scripts/
        └── references/
```

## Install

Copy the skill folder into your Codex skills directory:

```bash
cp -R skills/repo-skill-creator ~/.codex/skills/
```

If you want to inspect the skill before installing, start with:

- `skills/repo-skill-creator/SKILL.md`
- `skills/repo-skill-creator/references/skill-creation-checklist.md`

## Validate

Basic validator:

```bash
python3 /home/r.doi/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/repo-skill-creator
```

Richer review:

```bash
python3 skills/repo-skill-creator/scripts/review_skill.py skills/repo-skill-creator
```

## Example Usage

Analyze a repo:

```bash
python3 skills/repo-skill-creator/scripts/analyze_repo.py /path/to/repo
```

Scaffold a repo-derived skill:

```bash
python3 skills/repo-skill-creator/scripts/init_repo_skill.py /path/to/repo my-skill
```

Create a distribution bundle for a finished skill:

```bash
python3 skills/repo-skill-creator/scripts/create_distribution_bundle.py \
  skills/repo-skill-creator \
  --output-dir /tmp/repo-skill-creator-dist
```

## License

MIT
