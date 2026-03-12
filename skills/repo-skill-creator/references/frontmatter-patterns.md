# Frontmatter Patterns

Use these patterns when the generated `description` still feels generic.

## Formula

Write:

`[What the skill does]. Use when [repo-specific task language, docs, file types, or workflows].`

## Good

```yaml
---
name: symphony-release-workflow
description: Release workflow for the symphony repo. Use when Codex needs to prepare a release, follow symphony-specific deployment steps, update release notes, or verify the repo's canonical release commands and docs before shipping.
---
```

```yaml
---
name: m365schedule-sync
description: Scheduling and sync workflow for the m365schedule repo. Use when the user asks to fix calendar sync behavior, follow project-specific job conventions, debug recurring sync failures, or reuse the repo's documented workflow in a consistent way.
---
```

## Good Japanese Trigger Language

Use phrases like these inside the description when the team often prompts in Japanese:

- `"... use when the user says 'kono repo no rule ni shitagatte'"`
- `"... use when the user asks 'repo kara skill ka shite'"`
- `"... use when the user asks 'AGENTS.md ni along with this repo workflow'"`

Keep the sentence readable. Add Japanese phrases only when they improve real triggering.

## Bad

```yaml
---
name: repo-helper
description: Helps with this repository.
---
```

```yaml
---
name: workflow-skill
description: Implements internal architecture and entities.
---
```

The first is too vague. The second describes internals but not when to trigger.
