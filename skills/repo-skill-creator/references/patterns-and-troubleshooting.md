# Patterns And Troubleshooting

Use this when the workflow shape is unclear or the generated skill behaves poorly.

## Patterns

### Sequential Workflow Orchestration

Use when the task has an order that should not drift.

- Encode step order explicitly.
- Validate after each stage.
- Include rollback or recovery notes.

### Multi-Service Coordination

Use when the workflow spans multiple services or tool domains.

- Separate the work into phases.
- Pass outputs from one phase into the next.
- Validate before switching systems.

### Iterative Refinement

Use when the output gets better through review loops.

- Generate an initial result.
- Validate.
- Fix issues.
- Repeat until quality is acceptable.

### Context-Aware Tool Selection

Use when one outcome can be achieved by different tools.

- Define the decision criteria.
- State the fallback.
- Explain the tool choice.

### Domain-Specific Intelligence

Use when the value is mostly in expert judgment rather than tool access.

- Put the core logic in the skill.
- Validate before acting.
- Keep an audit trail when decisions matter.

## Troubleshooting

### Skill Does Not Trigger

- Tighten the description around concrete phrases.
- Add file types, repo names, workflow names, and user wording.

### Skill Triggers Too Often

- Remove broad phrasing.
- Clarify what the skill does not handle.

### Instructions Are Ignored

- Move critical instructions higher in the file.
- Replace vague wording with explicit checks.
- Move deterministic checks into scripts.

### Large Context

- Shrink `SKILL.md`.
- Move heavy detail into `references/`.
- Avoid enabling too many broad skills at once.
