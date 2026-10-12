# Pull request workflow

Use this reference after the request has been routed to `pr`.

## 1. Preflight

- Read repository contribution guidance and CI configuration.
- Check the branch, remote, upstream relationship, and complete diff against the target base.
- Look for an existing PR for the branch before creating a duplicate.
- Check whether the project welcomes the change and whether an issue or maintainer discussion is required.
- Choose `human` or `ai` review and apply [review-modes.md](review-modes.md).
- Decide whether the PR should be draft. Default to draft until the requested checks and review pass; ask before changing a draft PR to ready.

## 2. Write the PR body

Use [pr-human-template.md](pr-human-template.md) as the body shape. The body must explain:

- **What** changed, in observable terms.
- **Why** the change is needed, tied to a user problem, bug, issue, or requirement.
- **How** it works, including important design choices and boundaries.

Also include tests, review mode, risks, and any follow-up work. In `human` mode, the user supplies the intent section. Preserve it verbatim; do not generate, polish, or reinterpret the user's Why. In `ai` mode, the agent may draft the body but must label it AI-reviewed and include concrete evidence from the diff and checks.

Use `scripts/build_pr_body.py` to append sanitized environment metadata when the repository or user wants an audit trail. If prompt history is available and the user wants auditability, provide a UTF-8 history file through `--prompt-history-file`: start each entry with `ISO-8601 timestamp<TAB>verbatim prompt`, and place continuation lines below it. Redact only sensitive portions and record that redaction. Long prompts are rendered as code blocks. Never paste arbitrary environment values or secrets into a PR body.

## 3. Verify and submit

Run the relevant checks locally and the repository's full suite or gate when one exists; if the full gate is unavailable or too costly, record the reason. Inspect the final diff and body, and confirm the target base and head. Use `gh pr create --draft --body-file <file>` for a draft, or `gh pr edit --body-file <file>` for an existing PR, only when the user requested the corresponding remote action and `gh` is authenticated. If `gh` is unavailable, provide the prepared body and the exact next command instead of claiming the PR was submitted. Use `gh pr ready <id>` only after the requested checks and review pass and the user authorizes changing draft status.

After submission, report the PR URL, draft status, base/head branches, review mode, checks, and known risks. Do not monitor, comment, merge, or close the PR unless requested.

## 4. Feedback and updates

When a reviewer requests changes, classify each comment as valid, unclear, or out of scope. For valid comments, make the smallest fix, rerun affected checks, update What/How if behavior changed, and push only when the user requested the update. For false positives, explain the concrete code or test evidence in the reply.

For an existing PR, inspect both conversation-level and inline review comments:

```text
gh pr view <id> --comments
gh api /repos/<owner>/<repo>/pulls/<id>/comments --paginate
```

Summarize each actionable comment with its file, line when available, classification, and fix status.
