# Commit workflow

Use this reference after the request has been routed to `commit`.

## 1. Preflight

- Read repository-specific instructions and check `git status --short --branch`.
- Inspect the diff that will be committed (`git diff` and, for staged files, `git diff --cached`).
- Confirm the branch and intended file set. Separate unrelated changes before committing.
- Choose the review mode and apply the corresponding checklist in [review-modes.md](review-modes.md).

## 2. Build the commit context

Choose `en` or `zh` and keep the message consistent. Use the required What/Why/Test fields in that language.

Use the format in [commit-format.md](commit-format.md) for the commit message body:

```text
<type>(<scope>): <imperative summary>

What: <observable change; one focused sentence>
Why: <problem, requirement, or user value>
Test: <checks run and their outcomes>

Test: <commands and outcomes, or "Not run: <reason>">
Review: <human-approved | ai-reviewed>
Risks: <remaining risk, or "None known">
```

Keep the subject concise and imperative. Choose a repository-supported type; otherwise use `fix`, `feat`, `docs`, `test`, `refactor`, `build`, or `chore`. Do not invent a ticket number.

In `human` mode, obtain the user's What and Why wording when it is missing and keep it unchanged. The agent may propose Test, Review, and Risks, but must show the complete message before committing.

In `ai` mode, the agent may draft all fields, but it must review the staged diff, run relevant checks, and stop on a critical finding. Record the review result in `Review` and show the final message before the mutation when the user has not explicitly authorized direct commit execution.

## 3. Verify and commit

Run formatting, lint, type checks, and focused tests that are relevant to the changed code. Stage only the intended files, inspect the staged diff, then create one atomic commit. After committing, report the commit id and the checks performed. Do not push unless the user also requested a push.

## 4. Amendments

For an existing commit, inspect whether it is local or already shared. If it is the latest unpushed commit for the same logical change, amend it when that keeps the history clear. Use a new corrective commit for shared history unless the user explicitly requests a rewrite and the branch is safe to rewrite.
