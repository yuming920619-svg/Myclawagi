# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice
**Areas**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix | promoted | promoted_to_skill

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being worked on |
| `resolved` | Issue fixed or knowledge integrated |
| `wont_fix` | Decided not to address (reason in Resolution) |
| `promoted` | Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md |
| `promoted_to_skill` | Extracted as a reusable skill |

## Skill Extraction Fields

When a learning is promoted to a skill, add these fields:

```markdown
**Status**: promoted_to_skill
**Skill-Path**: skills/skill-name
```

Example:
```markdown
## [LRN-20250115-001] best_practice

**Logged**: 2025-01-15T10:00:00Z
**Priority**: high
**Status**: promoted_to_skill
**Skill-Path**: skills/docker-m1-fixes
**Area**: infra

### Summary
Docker build fails on Apple Silicon due to platform mismatch
...
```

---


## [LRN-20260318-001] correction

**Logged**: 2026-03-18T09:32:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
When the user asks about gpt-5-mini / gpt-5-nano, do not answer with gpt-5.4-mini / gpt-5.4-nano. Confirm the exact model family first.

### Details
The user asked for pricing and pros/cons of gpt-5-mini and gpt-5-nano. I incorrectly answered with gpt-5.4-mini and gpt-5.4-nano information. This happened because I mixed the OpenClaw catalog naming (gpt-5-mini / gpt-5-nano) with newer OpenAI docs that mention gpt-5.4-mini / gpt-5.4-nano.

### Suggested Action
Before answering model/pricing questions, restate the exact model IDs requested and verify the provider naming in current docs/catalog. If there is a naming mismatch between OpenClaw and provider docs, call it out explicitly instead of assuming they are interchangeable.

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: models, pricing, correction, openai, openclaw

---
