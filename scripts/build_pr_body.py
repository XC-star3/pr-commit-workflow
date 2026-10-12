#!/usr/bin/env python3
"""Build a PR body with What/Why/How fields and sanitized audit metadata."""

from __future__ import annotations

import argparse
import os
import platform
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def value_or_placeholder(value: Optional[str], label: str) -> str:
    value = (value or "").strip()
    return value if value else f"<{label}>"


def sanitize_metadata(value: str) -> str:
    """Keep allowlisted environment values on one harmless Markdown line."""
    return value.replace("\r", " ").replace("\n", " ").replace("`", "'").strip()[:160]


def first_env(*names: str, default: str = "unknown") -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return default


def detect_harness() -> str:
    explicit = os.environ.get("AGENT_HARNESS", "").strip()
    if explicit:
        return explicit
    if os.environ.get("CODEX_MODEL") or Path.home().joinpath(".codex").is_dir():
        return "codex"
    if os.environ.get("CLAUDE_MODEL") or Path.home().joinpath(".claude").is_dir():
        return "claude"
    return "unknown"


def collect_metadata() -> List[Tuple[str, str]]:
    terminal = first_env("TERM_PROGRAM", "LC_TERMINAL")
    terminal_version = first_env("TERM_PROGRAM_VERSION", "LC_TERMINAL_VERSION", default="")
    if terminal_version:
        terminal = f"{terminal} {terminal_version}"
    return [
        ("Harness", detect_harness()),
        (
            "Model",
            first_env(
                "CODEX_MODEL",
                "OPENAI_MODEL",
                "ANTHROPIC_MODEL",
                "CLAUDE_MODEL",
                "CURSOR_MODEL",
                "LLM_MODEL",
            ),
        ),
        (
            "Thinking level",
            first_env(
                "THINKING_LEVEL",
                "CODEX_THINKING_LEVEL",
                "OPENAI_THINKING_LEVEL",
            ),
        ),
        ("Terminal", terminal),
        ("System", platform.platform()),
        ("Python", platform.python_version()),
    ]


def read_prompt_history(path: Optional[str]) -> List[Tuple[str, str]]:
    if not path:
        return []
    entries: List[Tuple[str, str]] = []
    current_timestamp: Optional[str] = None
    current_prompt: List[str] = []

    def flush() -> None:
        if current_timestamp is not None:
            entries.append((current_timestamp, "\n".join(current_prompt)))

    with open(path, encoding="utf-8") as handle:
        for number, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip("\r\n")
            if not line.strip() and current_timestamp is None:
                continue
            if "\t" in line:
                flush()
                current_timestamp, prompt = line.split("\t", 1)
                current_timestamp = current_timestamp.strip()
                current_prompt = [prompt]
            elif current_timestamp is not None:
                current_prompt.append(line)
            else:
                raise ValueError(
                    f"Prompt history line {number} must contain timestamp<TAB>prompt"
                )
    flush()
    return entries


def build_body(
    what: Optional[str],
    why: Optional[str],
    how: Optional[str],
    review_mode: str,
    prompt_history_file: Optional[str] = None,
) -> str:
    lines = [
        "## What",
        "",
        value_or_placeholder(what, "observable change"),
        "",
        "## Why",
        "",
        value_or_placeholder(why, "problem, requirement, or user value"),
        "",
        "## How",
        "",
        value_or_placeholder(how, "implementation approach and boundaries"),
        "",
        "## Verification",
        "",
        "- `<command>`: <result>",
        "",
        "## Review",
        "",
        f"- Mode: `{review_mode}`",
        "- Findings: <summary or 'None'>",
        "",
        "## Risks and follow-up",
        "",
        "<remaining risk, compatibility note, rollout detail, or 'None known'>",
        "",
        "## Environment metadata",
        "",
    ]

    lines.extend(f"- {key}: `{sanitize_metadata(value)}`" for key, value in collect_metadata())
    history = read_prompt_history(prompt_history_file)
    if history:
        lines.extend(["", "## Prompt History", ""])
        short_history = [entry for entry in history if len(entry[1]) <= 200 and "\n" not in entry[1]]
        long_history = [entry for entry in history if entry not in short_history]
        if short_history:
            lines.extend(["| ISO-8601 | Prompt |", "| --- | --- |"])
            lines.extend(
                f"| {sanitize_metadata(timestamp)} | {prompt.replace('|', '\\|')} |"
                for timestamp, prompt in short_history
            )
        for timestamp, prompt in long_history:
            lines.extend(
                [
                    "",
                    f"### {sanitize_metadata(timestamp)}",
                    "",
                    "~~~~text",
                    prompt,
                    "~~~~",
                ]
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--what")
    parser.add_argument("--why")
    parser.add_argument("--how")
    parser.add_argument("--review-mode", choices=("human", "ai"), default="human")
    parser.add_argument(
        "--prompt-history-file",
        help="TSV file containing one ISO-8601 timestamp<TAB>verbatim prompt per line",
    )
    parser.add_argument("--output", help="Write to a file instead of stdout")
    args = parser.parse_args()
    try:
        body = build_body(
            args.what,
            args.why,
            args.how,
            args.review_mode,
            args.prompt_history_file,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(body)
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
