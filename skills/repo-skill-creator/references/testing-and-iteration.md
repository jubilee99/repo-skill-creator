# Testing And Iteration

Use this when the generated skill is structurally valid but not yet proven in real use.

## Testing Levels

### Manual

- Fastest feedback loop.
- Use for new skills and early refinement.
- Run obvious trigger prompts, paraphrased prompts, and unrelated prompts.

### Scripted

- Use when the workflow matters enough to repeat frequently.
- Store representative prompts and expected behaviors.
- Compare revisions of the same skill after editing descriptions or workflow steps.

### Programmatic

- Use for productized or scaled deployments.
- Measure trigger rate, failures, retries, and token usage over a test set.

## Three Test Categories

### Triggering

- Should trigger on obvious requests.
- Should trigger on paraphrases.
- Should not trigger on unrelated work.

### Functional

- The workflow completes correctly.
- Repo-specific commands succeed.
- Error handling covers the expected edge cases.

### Performance

- Compare baseline vs. skill-enabled runs.
- Track messages, tool calls, failures, and retries.
- Keep notes on whether the skill reduced clarification loops.

## Iteration Signals

### Under-triggering

- The skill does not load for obvious tasks.
- Users keep invoking it manually.

Fix:

- Add clearer trigger language to the description.
- Include the exact words users actually say.

### Over-triggering

- The skill loads for unrelated tasks.
- Users disable it or ignore it.

Fix:

- Narrow the scope.
- Remove generic phrases.
- Add negative examples to the test plan.

### Execution Problems

- The skill loads but still needs repeated correction.
- Repo validation commands fail or are skipped.

Fix:

- Add missing steps to the body.
- Move fragile logic into `scripts/`.
- Rewrite vague instructions as explicit validations.
