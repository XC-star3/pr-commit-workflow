---
name: pr-commit-workflow
description: Prepare or execute Git commits and GitHub pull requests with an explicit human or AI review mode and mandatory What/Why/How context.
---

# PR and Commit Workflow

Use this skill when the user asks to create, amend, review, push, or submit a Git commit or GitHub pull request. It provides two operation paths and two review modes; it does not grant permission for Git or GitHub mutations that the user has not requested.

## Route the request

1. Identify the operation: `commit` or `pr`. If it is unclear, ask before editing history or contacting a remote.
2. Identify the review mode:
   - `human`: the user reviews the proposed diff and message/body before the mutation. In this mode, preserve user-written intent text verbatim.
   - `ai`: the agent performs the review using [review-modes.md](references/review-modes.md), records the evidence, and may proceed only within the user's explicit authorization.
3. If the user did not choose a mode, use `human` for risky, public, shared, or externally visible changes. Use `ai` only when the user clearly delegates direct AI review/submission for the named operation.
4. Read only the relevant reference: [workflow-commit.md](references/workflow-commit.md) for commits or [workflow-pr.md](references/workflow-pr.md) for pull requests. Read [review-modes.md](references/review-modes.md) when selecting or executing a review.

## Shared requirements

- Inspect repository guidance (`AGENTS.md`, `CONTRIBUTING.md`, `README`, CI configuration), current branch, status, and the complete diff before proposing a mutation.
- The message or PR body must state **What**, **Why**, and **How**. Do not substitute a vague summary for any of these fields.
- Run the smallest relevant verification and report the exact commands and outcomes. Never claim a check passed when it was not run.
- Keep the change focused. Stop and surface unrelated changes, secrets, merge conflicts, failing checks, or an unclear user intent instead of hiding them.
- Do not use `--no-verify`, force push, delete branches, or rewrite shared history unless the user explicitly requests that exact action.
- A local commit changes repository history. Pushing, opening, or editing a PR changes a remote system; perform only the remote action the user requested and do not infer additional cleanup.

## Evidence

For AI review, include the review mode, checks run, relevant test results, and unresolved risks in the commit body or PR body. For human review, include the same information in the proposal, then wait for the user's approval when the requested operation has not already authorized the mutation.

For PR metadata, use the standard-library helper when useful:

```text
python scripts/build_pr_body.py --what "..." --why "..." --how "..." --review-mode ai --prompt-history-file prompt-history.tsv
```

The helper reads an allowlist of non-secret environment metadata only and can append a caller-supplied, timestamped prompt history. Review both before publishing them. See [pr-human-template.md](references/pr-human-template.md) for the body structure.
