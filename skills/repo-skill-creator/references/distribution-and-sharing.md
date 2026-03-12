# Distribution And Sharing

Use this when the skill is ready to leave local iteration and be shared with other users.

## Current Distribution Approach

### For Individuals

1. Package the skill folder.
2. Zip it if needed.
3. Upload it to Claude.ai or place it in the local skills directory for Claude Code.

### For Teams

- Host the skill in version control.
- Keep release notes or change notes outside the skill folder.
- Use a separate README for human readers, not inside the skill folder.

## Recommended Packaging Flow

1. Validate the skill.
2. Review it with `scripts/review_skill.py`.
3. Generate a distribution bundle with `scripts/create_distribution_bundle.py`.
4. Share the zip plus human-facing docs from the bundle output directory.

## Positioning Guidance

When writing the human README:

- Focus on outcomes, not implementation details.
- Explain what becomes faster or more reliable with the skill.
- If the skill complements MCP or another integration, explain the combination clearly.

## Do Not Do

- Do not add `README.md` inside the skill folder itself.
- Do not bury installation instructions only inside `SKILL.md`.
- Do not ship a vague skill without example prompts or validation steps.
