#!/usr/bin/env python3
"""Build a PR body with What/Why/Test fields and sanitized audit metadata."""

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
    test: Optional[str],
    review_mode: str,
    language: str = "en",
    prompt_history_file: Optional[str] = None,
) -> str:
    if language == "zh":
        labels = {
            "what": "做了什么（What）",
            "why": "为什么（Why）",
            "test": "测试（Test）",
            "verification": "验证",
            "review": "审查",
            "findings": "发现",
            "risks": "风险与后续工作",
            "metadata": "环境元数据",
            "history": "Prompt History",
            "observable": "可观察到的变更",
            "reason": "问题、需求或用户价值",
            "test_placeholder": "执行的检查和结果",
            "command": "命令",
            "result": "结果",
        }
    else:
        labels = {
            "what": "What",
            "why": "Why",
            "test": "Test",
            "verification": "Verification",
            "review": "Review",
            "findings": "Findings",
            "risks": "Risks and follow-up",
            "metadata": "Environment metadata",
            "history": "Prompt History",
            "observable": "observable change",
            "reason": "problem, requirement, or user value",
            "test_placeholder": "checks run and their outcomes",
            "command": "command",
            "result": "result",
        }
    findings_placeholder = "摘要或 None" if language == "zh" else "summary or 'None'"
    risk_placeholder = (
        "<剩余风险、兼容性说明、发布细节或 None known>"
        if language == "zh"
        else "<remaining risk, compatibility note, rollout detail, or 'None known'>"
    )
    lines = [
        f"## {labels['what']}",
        "",
        value_or_placeholder(what, labels["observable"]),
        "",
        f"## {labels['why']}",
        "",
        value_or_placeholder(why, labels["reason"]),
        "",
        f"## {labels['test']}",
        "",
        value_or_placeholder(test, labels["test_placeholder"]),
        "",
        f"## {labels['verification']}",
        "",
        f"- <{labels['command']}>: <{labels['result']}>",
        "",
        f"## {labels['review']}",
        "",
        f"- {'模式' if language == 'zh' else 'Mode'}: `{review_mode}`",
        f"- {labels['findings']}: <{findings_placeholder}>",
        "",
        f"## {labels['risks']}",
        "",
        risk_placeholder,
        "",
        f"## {labels['metadata']}",
        "",
    ]

    lines.extend(f"- {key}: `{sanitize_metadata(value)}`" for key, value in collect_metadata())
    history = read_prompt_history(prompt_history_file)
    if history:
        lines.extend(["", f"## {labels['history']}", ""])
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
    parser.add_argument("--test", help="Checks run and their outcomes")
    parser.add_argument("--review-mode", choices=("human", "ai"), default="human")
    parser.add_argument("--language", choices=("en", "zh"), default="en")
    parser.add_argument(
        "--prompt-history-file",
        help="UTF-8 history file: timestamp<TAB>prompt, with optional continuation lines",
    )
    parser.add_argument("--output", help="Write to a file instead of stdout")
    args = parser.parse_args()
    try:
        body = build_body(
            args.what,
            args.why,
            args.test,
            args.review_mode,
            args.language,
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
