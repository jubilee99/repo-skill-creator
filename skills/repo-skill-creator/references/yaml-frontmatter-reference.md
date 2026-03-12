# YAML Frontmatter Reference

This is the richer frontmatter model used by `scripts/review_skill.py`.

## Required

```yaml
---
name: skill-name
description: What the skill does. Use when the user asks for the specific workflow, repo, file type, or repeated task this skill handles.
---
```

## Supported Optional Fields

```yaml
---
name: skill-name
description: ...
license: MIT
compatibility: Intended for Codex in this local environment with repo access and python3 available.
allowed-tools: Bash(python3:*) Bash(rg:*) WebFetch
metadata:
  author: Your Name
  version: 1.0.0
  mcp-server: linear
---
```

## Notes

- Keep the description under 1024 characters.
- Do not use angle brackets in the description.
- `compatibility` is useful for humans and richer review, but the local minimal validator does not check it.
- Use `metadata` for values like author, version, mcp-server, category, tags, docs URL, or support contact.
