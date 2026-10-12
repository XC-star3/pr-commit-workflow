# Review modes

Select one mode per commit or PR. Record the mode in the message or body.

## Human review

Use when the user wants approval, when the change is public or high risk, or when intent is not fully specified.

1. Prepare the diff, checks, proposed message/body, and a short risk list.
2. Ask the user to review the complete proposal. Keep user-written What and Why text unchanged.
3. Apply only requested corrections, then perform the authorized commit or PR action.

The agent still performs basic mechanical checks and reports findings; human review means the user makes the final content and risk decision.

## AI review

Use only when the user explicitly chooses direct AI review or delegates it for the named operation.

Review the actual diff, not just the task description:

- correctness on the normal path and failure paths;
- regression, compatibility, and migration impact;
- input validation, permissions, secrets, and unsafe command construction;
- concurrency, resource cleanup, and error handling when relevant;
- test quality and whether tests exercise real behavior;
- scope, repository conventions, and documentation impact.

Classify findings as `critical`, `needs-fix`, `observation`, or `none`. Do not submit with an unresolved `critical` finding. Fix `needs-fix` findings before submission unless the user explicitly accepts the risk. Record the commands, results, and any accepted risk in the commit or PR evidence.

## Mode selection table

| Situation | Recommended mode | Reason |
| --- | --- | --- |
| Public API, schema, auth, migration, or production behavior | `human` | A second decision maker should approve impact and intent. |
| Small local change with explicit direct delegation | `ai` | The scope and authorization are clear. |
| User supplied a specific What/Why statement | `human` | Preserve the user's intent as the source of truth. |
| Existing PR update after requested review feedback | Match the existing PR mode | Keep evidence and expectations consistent. |
