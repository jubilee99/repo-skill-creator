# Skill Creation Checklist

Use this checklist before calling a repo-derived skill "done".

## Scope

- Define 2-3 concrete user requests.
- Prefer a narrow workflow over a vague repo-wide helper.
- Confirm whether the skill is best framed as:
  - `workflow-automation`
  - `mcp-enhancement`
  - `document-asset-creation`

## Frontmatter

- Keep only `name` and `description` unless there is a strong reason to add more.
- Make `description` answer both:
  - what the skill does
  - when it should trigger
- Include direct task language users might actually say.
- Avoid vague descriptions like `helps with projects`.
- Avoid angle brackets in the description.

## Body

- Keep `SKILL.md` lean.
- Move heavy repo context into `references/`.
- Put repeated or fragile operations into `scripts/`.
- Place validation instructions near the step that needs them.
- Include at least one failure mode or recovery path when the workflow is brittle.

## Validation

- Run the system validator:
  - `python3 /home/r.doi/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-path>`
- Test obvious trigger requests.
- Test paraphrased trigger requests.
- Test unrelated requests that should not trigger.
- Confirm the skill can complete the workflow with the repo's real commands.

## Iteration

- If the skill under-triggers, sharpen the description with better task language.
- If the skill over-triggers, narrow the scope and add boundaries.
- If repo work reveals missing steps, update the skill immediately instead of relying on ad hoc prompting.
