# PR + Commit Workflow

A Codex skill for high-signal Git commits and GitHub pull requests in agent-assisted development.

It routes each request through a commit or PR workflow, requires **What / Why / How** context, and lets the user choose between a human review and an AI review. It is a workflow guide with a small local helper, not a remote service or an automatic merge bot.

## What it does

- Supports separate commit and pull request workflows
- Offers two explicit review modes:
  - **Human review** — the user approves the proposed diff and preserves their intent text verbatim
  - **AI review** — the agent reviews the actual diff, records findings, and stops on critical issues
- Requires What, Why, and How for every commit message and PR body
- Encourages surgical staging and one logical change per commit
- Uses draft PRs until requested checks and review pass
- Captures sanitized environment metadata for audit trails
- Can include a caller-supplied prompt history with ISO-8601 timestamps
- Defines checks for both conversation comments and inline review comments
- Keeps GitHub mutations explicit: create, edit, push, ready, merge, and close are separate actions

## Why this workflow exists

AI-assisted changes are easier to review when the result, motivation, implementation, evidence, and review mode are visible in the Git history. The workflow keeps human intent separate from generated implementation details while still supporting direct AI review when the user delegates it.

## How it works

1. Inspect repository guidance, branch state, status, and the complete diff.
2. Choose `commit` or `pr`.
3. Choose `human` or `ai` review.
4. Write What / Why / How and record tests, findings, and risks.
5. Run the relevant checks and the repository gate when available.
6. Commit locally or create/update a draft PR only when the requested action is authorized.
7. For an existing PR, inspect both general and inline review comments before making updates.

## Installation

### Codex skill directory

Clone this repository into the local skills directory:

```bash
git clone https://github.com/XC-star3/pr-commit-workflow.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/pr-commit-workflow"
```

Restart the agent or reload skills if the directory was already open.

### Manual use

Point your coding agent at `SKILL.md` and ask it to use `$pr-commit-workflow` for a commit or pull request.

## Usage

### Human-reviewed commit

```text
Use $pr-commit-workflow to prepare a commit in human review mode.
Show me the complete message before committing.
```

The message includes:

```text
<type>(<scope>): <imperative summary>

What: <observable change>
Why: <problem or requirement>
How: <implementation approach>

Tests: <command and result>
Review: human-approved
Risks: <remaining risk or None known>
```

### AI-reviewed draft PR

```text
Use $pr-commit-workflow to prepare and create a draft PR in AI review mode.
Review the diff, run the relevant checks, and include What, Why, How, tests, and risks.
```

The agent must review normal and failure paths, compatibility impact, input validation, permissions, error handling, test quality, and scope before submission. An unresolved critical finding blocks submission.

### Build a PR body

```bash
python scripts/build_pr_body.py \
  --what "Add explicit review modes" \
  --why "Make commit and PR decisions auditable" \
  --how "Route through human or AI review checklists" \
  --review-mode ai \
  --output pr-body.md
```

The helper records Harness, Model, Thinking level, Terminal, System, and Python metadata from an allowlist. Review the generated file before publishing it.

### Include prompt history

Pass a UTF-8 file using `--prompt-history-file`. Start each entry with a timestamp, a literal tab character, and the prompt. Continuation lines belong to the preceding prompt:

```text
2026-10-12T10:00:00+08:00<TAB>Inspect the repository guidance
2026-10-12T10:01:00+08:00<TAB>Create a draft PR
```

Redact sensitive portions before publishing. Short prompts are rendered as a table; long or multiline prompts are rendered as code blocks.

## Pull request commands

Use a draft until verification and review are complete:

```bash
gh pr create --draft --body-file pr-body.md
gh pr view <id> --comments
gh api /repos/<owner>/<repo>/pulls/<id>/comments --paginate
gh pr ready <id>
```

Run `gh pr ready` only after the user authorizes changing the draft status. Do not infer permission to merge, close, comment, or monitor a PR.

## Repository layout

```text
pr-commit-workflow/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── references/
│   ├── commit-format.md
│   ├── pr-human-template.md
│   ├── review-modes.md
│   ├── workflow-commit.md
│   └── workflow-pr.md
└── scripts/
    └── build_pr_body.py
```

## Privacy and safety

- Prompt history is optional and must be reviewed before publication.
- The helper reads only named environment variables and sanitizes Markdown-sensitive characters.
- Human-written intent is preserved in human review mode and is never silently rewritten.
- AI review cannot override an unresolved critical finding.
- Force pushes, `--no-verify`, shared-history rewrites, and unrelated remote actions require explicit user authorization.

## Requirements

- Git
- Python 3.8+
- GitHub CLI (`gh`) for GitHub PR operations

## License

AGPL-3.0
