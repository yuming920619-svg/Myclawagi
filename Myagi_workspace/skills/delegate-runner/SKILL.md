---
name: delegate-runner
description: Non-blocking background task delegation with model selection (codex or claude) and completion-only reporting. Use when the user asks to dispatch a long task to a sub-agent and continue chatting without progress polling.
---

# Delegate Runner

Delegate long tasks to a background sub-agent and keep the main chat responsive.

## Rules

1. Never run long tasks in the foreground.
2. Use `sessions_spawn` to dispatch work.
3. Do not poll progress in a loop.
4. Report only two times:
   - Immediate ack: delegated + label/model
   - Final completion message when the platform pushes result
5. Poll/check status only if the user explicitly asks for progress or debugging.

## Default behavior

- Prefer model:
  - `codex` for routine coding/automation
  - `opus` for deep reasoning/writing
- `cleanup: keep` for traceability unless user asks to auto-delete.
- Set clear task scope and deliverable format in the spawned prompt.

## Spawn template

Use this structure when calling `sessions_spawn`:

- Task header: goal + constraints + output format
- Model: `default` (codex) or `opus`
- Timeout: set for long jobs (e.g., 1800-7200s)
- Label: `delegated-<topic>-<date>`
- Include a verification gate in the task prompt (lint/test/RTL) before final handoff

## Verification gate (required for coding tasks)

For code-generation/refactor/fix tasks, enforce post-generation checks before reporting success.

1. Run project checks in this order (skip missing steps):
   - Lint/format check
   - Unit tests
   - RTL simulation/regression (if repo has RTL flow)
2. If any check fails, mark result as failed and include:
   - failing command
   - concise error summary
   - log path/artifact path
   - suggested next fix step
3. Only report success when required checks pass.
4. Keep completion reporting single-shot (no progress polling).

## RTL-oriented completion format

When RTL exists, prefer this completion summary shape:

- Status: PASS / FAIL
- Scope: changed files/modules
- Commands run: exact validation commands
- Result: key metrics (e.g., vectors passed, phase counts, failures)
- Artifacts: log/report paths
- Next action: optional (only if FAIL)

## User-facing ack format

After dispatch, reply briefly:

- 已派發背景任務（模型：X，標籤：Y）。
- 我不會輪詢刷進度；完成後會一次回報結果。
- 你現在可以繼續丟別的事給我。
