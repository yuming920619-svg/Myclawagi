---
name: special-topic-discussion
description: Generate Google Form-ready audience evaluation drafts for 「專題討論 / Special Topic Discussion」 talks from a list of speaker names and report topics, and optionally archive the result to GitHub. Use when the user provides speaker names plus presentation topics/titles and wants: (1) the form questions整理成文字, (2) per-speaker required-answer draft comments, (3) short evaluation text that must satisfy a minimum-length requirement such as 至少 30 字 per item, or (4) the final draft written into the Myclawagi repo under `Special Topic Discussion/` and pushed to GitHub.
---

# Special Topic Discussion

## Overview

Use this skill to turn a speaker/topic list into a reusable audience-scoring draft for the user's course discussion form.
Default output should match the existing workflow: focus on required fields, generate paste-ready comments, and treat GitHub archival as the default fixed workflow for this user unless the user explicitly says not to sync yet.

## Workflow

### 1. Confirm the input shape

Expect input like one of these:
- `1. 蘇沂晨 微塑膠量測`
- `2. 范揚楷 海上浮台量測海洋data`
- `3. 楊竣凱 風浪中船速減損與分析`

Extract for each speaker:
- speaker name
- presentation topic/title
- order (if present)

If the user already gave a Google Form URL and asked what needs to be filled, inspect the form first and summarize only the questions that matter.

### 2. Use the known form pattern

For this workflow, default to the existing audience-evaluation pattern:
- basic required fields: date, student ID, name
- per speaker required fields:
  1. speaker name
  2. research content and academic depth
  3. interdisciplinary explanation ability
  4. slide structure and logical organization
  5. expression skills and professional attitude
  6. Q&A response and on-site reaction
- each scoring dimension needs a short required comment

If the live form differs, prefer the live form.

### 3. Generate comments conservatively

When the user only gives speaker names and topics, do **not** pretend to know detailed presentation performance.

Default behavior:
- use conservative, generic-but-plausible comments derived from the topic itself
- keep tone natural and usable in a course form
- default score suggestion to `4/5` unless the user provided stronger signals
- treat the form minimum as a hard requirement: if the form says at least 30 Chinese characters, generate comments safely above that floor rather than aiming vaguely near it
- prefer about 32–45 Chinese characters per required comment unless the user requests a different length

Good pattern:
- tie the comment to topic clarity, practical value, structure, explanation, or likely research significance
- avoid overclaiming experimental results, data quality, or Q&A performance unless the user mentioned them

### 4. Output format

When the user wants direct filling help, return a clean per-speaker block.

Recommended format:
- `講者姓名：...`
- `1. 研究內容與學術深度（建議分數：4/5）`
- one paste-ready comment
- repeat for dimensions 2 to 5

Prefer a compact format over long prose.

### 5. GitHub archiving workflow

For this user, treat GitHub sync as a fixed default step for this workflow once a usable draft exists or new speaker blocks are added, unless the user explicitly says not to push yet.

Repository convention for this user:
- repo path: `/home/node/.openclaw/workspace/Myclawagi`
- archive folder: `Special Topic Discussion/`
- filename pattern: `YYYY-MM-DD_觀眾評分表草稿.md`

Suggested markdown structure:
- title
- date
- purpose / note
- basic fields reminder
- one section per speaker
- each dimension with suggested score and comment

When continuing the same day's discussion sheet:
- update the existing `YYYY-MM-DD_觀眾評分表草稿.md` instead of creating scattered new files
- append new speakers in order
- keep earlier speaker blocks unchanged unless the user asked for a rewrite

When the user wants an alternate version for classmates, reuse, or wording variation on the same day:
- create a separate sibling file such as `YYYY-MM-DD_觀眾評分表草稿_第二版.md`
- do not overwrite the original version
- commit and push the alternate version as its own file

### 6. Commit and push safely

When pushing to GitHub:
1. write the markdown file into the repo folder
2. `git add` only the new/updated discussion file
3. `git commit` with a focused message
4. `git push origin main`
5. if push is rejected because remote moved, run:
   - `git fetch origin main`
   - `git pull --rebase origin main`
   - `git push origin main`

Do not sweep unrelated workspace changes into the commit.

## Output quality rules

- Use Traditional Chinese.
- Prefer direct, paste-ready text.
- Keep comments short and low-risk, but never below the form's minimum length requirement.
- If the form requires at least 30 characters, aim slightly above the threshold to avoid edge-case counting failures.
- If evidence is weak, sound cautious rather than overly specific.
- If the user asks for “只有必答題”, omit optional feedback sections.
- If the user asks for “整理好”, return a cleaner block without repeated explanation.

## Example trigger patterns

Trigger this skill when the user says things like:
- `這是今天專題討論的講者和題目，幫我生成表單評論`
- `幫我整理這個專題討論 google 表單要填什麼`
- `根據這些講者和主題，幫我寫 30 字左右評論`
- `把剛剛那份專題討論評分稿推到 GitHub`
- `下次遇到專題討論就照這套流程跑`
