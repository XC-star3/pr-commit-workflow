# PR 与 Commit 工作流

[English README](README.en.md)

这是一个面向 AI 辅助开发的 Codex skill，用于规范 Git commit 和 GitHub Pull Request 工作流。

它会根据请求进入 commit 或 PR 流程，强制说明 **What / Why / Test**，并允许每次选择人工审查或 AI 审查。它是一套工作流规范和本地辅助脚本，不是远程服务，也不是自动合并机器人。

## 功能

- 分离 commit 和 Pull Request 工作流
- 支持两种明确的审查模式：
  - **人工审查**：用户审查 diff，并保留用户提供的意图原文
  - **AI 审查**：Agent 审查实际 diff，记录发现的问题，遇到关键问题时停止提交
- 每个 commit message 和 PR body 都必须说明 What、Why、Test
- 鼓励精确暂存，并保证一个 commit 只包含一个逻辑变更
- 默认使用 draft PR，检查和审查完成后再转为 ready
- 收集经过清理的环境元数据，用于审计追踪
- 可选加入带 ISO-8601 时间戳的 Prompt History
- 同时检查普通 PR 评论和 inline review comments
- 将 create、edit、push、ready、merge、close 等 GitHub 操作保持为明确的独立动作

## 为什么需要这套工作流

AI 辅助开发产生的变更，需要让审查者清楚看到改了什么、为什么改、怎么实现、如何验证，以及由谁完成审查。这套工作流将人工意图和机器实现分开，同时在用户明确委托时支持 AI 直接审查。

## 工作流程

1. 读取仓库规则、分支状态、工作区状态和完整 diff。
2. 选择 `commit` 或 `pr`。
3. 选择 `human` 或 `ai` 审查模式。
4. 编写 What / Why / Test，并记录发现和风险。
5. 运行相关检查，以及仓库提供的完整 gate。
6. 只在用户授权的范围内创建本地 commit 或 draft PR。
7. 更新已有 PR 时，同时检查普通评论和 inline review comments。

## 安装

### 安装到 Codex skill 目录

将仓库克隆到本地 skills 目录：

```bash
git clone https://github.com/XC-star3/pr-commit-workflow.git \\
  "${CODEX_HOME:-$HOME/.codex}/skills/pr-commit-workflow"
```

如果 skill 目录已经打开，请重启 Agent 或重新加载 skills。

### 手动使用

让你的 coding agent 读取 `SKILL.md`，并在创建 commit 或 PR 时使用 `$pr-commit-workflow`。

## 使用方法

### 人工审查 commit

```text
使用 $pr-commit-workflow，以 human 模式准备一个 commit。
提交前展示完整的 commit message。
```

Commit message 包含：

```text
<type>(<scope>): <imperative summary>

What: <可观察到的变更>
Why: <问题或需求>
Test: <检查和结果>

Test: <命令和结果>
Review: human-approved
Risks: <剩余风险或 None known>
```

### AI 审查 draft PR

```text
使用 $pr-commit-workflow，以 ai 模式准备并创建 draft PR。
审查 diff，运行相关检查，并包含 What、Why、Test 和风险。
```

Agent 必须检查正常路径和失败路径、兼容性影响、输入校验、权限、错误处理、测试质量和改动范围。存在未解决的 critical finding 时，不得提交。

### 生成 PR body

```bash
python scripts/build_pr_body.py \\
  --what "Add explicit review modes" \\
  --why "Make commit and PR decisions auditable" \\
  --test "Run the relevant human or AI review checks" \\
  --review-mode ai \\
  --language zh \\
  --output pr-body.md
```

辅助脚本会从白名单中收集 Harness、Model、Thinking level、Terminal、System 和 Python 信息。发布前必须人工检查生成的文件。

使用 `--language zh` 输出中文，使用 `--language en` 输出英文；默认语言为英文。

### 加入 Prompt History

通过 `--prompt-history-file` 传入 UTF-8 文件。每条记录以时间戳、一个实际的制表符和 prompt 开始，后续行属于上一条 prompt：

```text
2026-10-12T10:00:00+08:00<TAB>Inspect the repository guidance
2026-10-12T10:01:00+08:00<TAB>Create a draft PR
```

发布前请脱敏。短 prompt 会渲染为表格，长 prompt 或多行 prompt 会渲染为代码块。

## Pull Request 命令

在验证和审查完成前使用 draft：

```bash
gh pr create --draft --body-file pr-body.md
gh pr view <id> --comments
gh api /repos/<owner>/<repo>/pulls/<id>/comments --paginate
gh pr ready <id>
```

只有在用户授权并且检查、审查都完成后，才能执行 `gh pr ready`。不得自行推断合并、关闭、评论或持续监控 PR 的权限。

## 仓库结构

```text
pr-commit-workflow/
├── SKILL.md
├── README.md
├── README.en.md
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

## 隐私与安全

- Prompt History 是可选项，发布前必须审查。
- 辅助脚本只读取指定的环境变量，并清理 Markdown 特殊字符。
- human 模式会保留人工意图，不会静默改写。
- AI 审查不能绕过未解决的 critical finding。
- force push、`--no-verify`、共享历史重写和无关远程操作都需要用户明确授权。

## 环境要求

- Git
- Python 3.8+
- GitHub CLI（`gh`，用于 GitHub PR 操作）

## 许可证

AGPL-3.0
