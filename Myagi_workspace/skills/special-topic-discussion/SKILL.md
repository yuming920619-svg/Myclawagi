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

### 3. Generate comments conservatively but with real depth

When the user only gives speaker names and topics, do **not** pretend to know detailed presentation performance.

Default behavior:
- write comments from the topic itself, but avoid sounding empty, formulaic, or one-sided
- keep tone natural and usable in a course form
- default score suggestion to `4/5` unless the user provided stronger signals
- treat the form minimum as a hard requirement: if the form says at least 30 Chinese characters, generate comments safely above that floor rather than aiming vaguely near it
- for this user, prefer **short audience-style comments** by default: each item should read like something a real listener could type on the spot, not a mini review paragraph
- prefer about **32–45 Chinese characters** per required comment unless the user requests a different length or a more detailed version

Depth rules:
- infer only **reasonable research-level angles** from the title/topic, such as: problem importance, engineering relevance, method choice, analysis depth, system trade-offs, application value, or expected technical challenges
- make the comment feel more substantive by mentioning one likely analytical dimension (for example: model assumptions, comparison baseline, practical constraints, design trade-offs, validation path, or application scenario)
- keep the language cautiously framed when evidence is weak, using patterns like `若能進一步...`, `若後續能補充...`, `若在分析中納入...`, instead of pretending those details were already shown in the talk
- avoid overclaiming experimental results, data quality, novelty, or Q&A performance unless the user mentioned them
- avoid writing praise that is so generic it could fit any topic without modification
- when slide evidence is rich, use it to choose **which concrete angle to mention**, but still keep the final sentence compact and listener-like

Good pattern:
- tie the comment to topic clarity, practical value, structure, explanation, and likely research significance
- if the title suggests a technical method or application domain, reflect that in the wording
- prefer balanced comments: acknowledge topic value, then point to one meaningful direction for deeper analysis or clearer explanation
- keep each item to **one natural sentence** whenever possible; do not let it expand into a mini-essay

Anti-template rule for all dimensions (1–5):
- do **not** let items 1–4 drift into the same repeated sentence skeleton across all speakers
- vary the angle for each dimension according to the speaker's actual topic or slide evidence: for example, one speaker's first item may stress research value, another may stress method design, another may stress validation depth
- spread sentence shapes across the batch instead of repeating the same patterns such as `有把 A 跟 B 連起來`, `整體脈絡算清楚`, `看得出準備相當認真`
- for item 2, vary between background linkage, interdisciplinary accessibility, application-context explanation, or method-to-problem connection
- for item 3, vary between structure completeness, comparison flow, result arrangement, conclusion clarity, or transition smoothness
- for item 4, vary between figure support, explanation rhythm, key-point delivery, technical clarity, or professionalism in presentation
- even when keeping the same score and overall stance, make the wording and emphasis genuinely different across speakers

Q&A-dimension rule (very important):
- do **not** let the fifth item (`問答回應與臨場反應`) collapse into the same repeated template for every speaker
- anchor the fifth item to the speaker's actual topic or slide evidence, choosing one likely angle such as: method choice, parameter setting, result interpretation, comparison basis, engineering trade-off, ecological meaning, model limitation, or practical application
- when evidence is weak, still make it topic-specific rather than generic; avoid repeatedly writing the same `若能再補充...整體會更完整` pattern across all speakers
- vary the sentence shape across speakers: some can focus on explanation clarity, some on result interpretation, some on trade-offs, and some on application meaning
- if the slides already show clear results or validation, let the fifth item refer to those specifics instead of falling back to a generic placeholder

### 4. Output format

When the user wants direct filling help, return a clean per-speaker block.

Recommended format:
- `講者姓名：...`
- `1. 研究內容與學術深度（建議分數：4/5）`
- one paste-ready comment
- repeat for dimensions 2 to 5

Preferred default output for this user:
- short-form audience comments
- one sentence per item
- direct paste-ready wording
- no analysis paragraph before or after the block unless the user asks

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

Classmate-version wording rules:
- keep the same speaker order, score suggestions, and overall evaluation direction as the original unless the user asks for different scoring
- rewrite every comment with noticeably different wording; do not just change a few words mechanically
- keep the same default length discipline: short audience-style comments, usually about 32–45 Chinese characters and safely above the form minimum
- make the tone easy to copy/share with classmates: natural, neutral, and paste-ready
- avoid overly personal phrasing, rare wording, or details that would make multiple classmates' answers look obviously copied from one source
- prefer the same meaning with alternate phrasing, not a change in evaluation stance

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
- **Before returning or pushing a draft, validate every generated comment one by one**; if any item is under the minimum by plain character count, rewrite it before sending.
- When a sentence lands close to the threshold, prefer rewriting it to a safer margin instead of trying to skate exactly on 30.
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
