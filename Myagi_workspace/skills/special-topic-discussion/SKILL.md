---
name: special-topic-discussion
description: >
  Generate paste-ready audience evaluation comments for 「專題討論 / Special Topic Discussion」 course talks.
  Use when the user provides speaker names and presentation topics/titles and wants:
  per-speaker scoring comments for a Google Form, draft text that meets a minimum character-length requirement (e.g. 至少 30 字),
  or the final draft archived to GitHub.
  Trigger on phrases like: 專題討論、觀眾評分、表單評論、幫我寫評論、推到 GitHub、整理評分稿、填表單、講者評論.
  Also trigger when the user gives a numbered list of names + topics that looks like a speaker roster.
---

# Special Topic Discussion — Audience Evaluation Draft Generator

## Quick Reference

- **Form URL**: `https://docs.google.com/forms/d/e/1FAIpQLSdwErRB-iovGdkh1sQRJBfBmbUPKH053GHufSs2c8hmguY3ow/viewform`
- **Target repo**: `Myclawagi` → `Special Topic Discussion/`
- **Filename**: `YYYY-MM-DD_觀眾評分表草稿.md`
- **Default score**: 4/5
- **Comment length**: 32–45 Chinese characters (hard floor: 30)

---

## Phase 1 — Parse Input

Expect input shaped like:

```
1. 蘇沂晨 微塑膠量測
2. 范揚楷 海上浮台量測海洋data
3. 楊竣凱 風浪中船速減損與分析
```

Extract per speaker:
- **order** (序號)
- **name** (講者姓名)
- **topic** (報告主題)

If anything is ambiguous, ask once to confirm before generating.

---

## Phase 2 — Generate Comments

### 2.1 Form Dimensions

Each speaker has **5 required scoring dimensions** (names are fixed — use exactly these labels):

| # | Dimension Label | Short Key |
|---|----------------|-----------|
| 1 | 研究內容與學術深度 | content |
| 2 | 跨領域解釋能力 | interdisciplinary |
| 3 | 投影片架構與邏輯組織 | slides |
| 4 | 表達技巧與專業態度 | delivery |
| 5 | 問答回應與臨場反應 | qa |

Plus basic required fields (日期、學號、姓名) — remind the user once at the top.

### 2.2 Writing Rules

Core principles — apply to every comment:

1. **Length**: 32–45 Chinese characters. Treat 30 as a hard floor; never output a comment under 30 characters. When a draft lands at 30–31, rewrite to a safer margin.
2. **Tone**: natural audience-style — something a real listener could type on the spot. One sentence per item. No mini-essay, no analysis paragraph.
3. **Evidence calibration**: infer only reasonable angles from the topic title (problem importance, method choice, engineering relevance, system trade-offs, validation path, application value). When evidence is weak, use cautious framing: `若能進一步…`, `若後續能補充…`, `若在分析中納入…`.
4. **No overclaiming**: never fabricate experimental results, data quality, novelty, or Q&A performance that the user didn't mention.
5. **Score default**: 4/5 unless the user signals otherwise.

### 2.3 Anti-Repetition Rules

The most common failure mode is producing structurally identical sentences across speakers. Prevent this:

**Across speakers** — vary **which angle** each dimension highlights. For the same dimension #, different speakers should emphasize different facets:

| Dimension | Possible angles (rotate across speakers) |
|-----------|------------------------------------------|
| 1 content | research value · method design · validation depth · problem framing · data scope |
| 2 interdisciplinary | background linkage · accessibility · application-context · method-to-problem bridge |
| 3 slides | structure completeness · comparison flow · result arrangement · transition smoothness · conclusion clarity |
| 4 delivery | figure support · explanation rhythm · key-point delivery · technical clarity · professionalism |
| 5 qa | method choice · parameter setting · result interpretation · comparison basis · engineering trade-off · model limitation · practical application |

**Across dimensions within one speaker** — don't let items 1–4 share the same sentence skeleton. Vary sentence structure, not just swapped nouns.

**Dimension 5 (qa) deserves special attention**: anchor it to the speaker's actual topic. Pick one likely technical angle (e.g., model assumptions, parameter sensitivity, ecological meaning). Never fall back to a generic `若能再補充…整體會更完整` pattern for every speaker.

### 2.4 Classmate-Version Rules

When the user asks for an alternate version (for classmates to reuse):

- Same speaker order, scores, and evaluation direction as the original
- Rewrite every comment with noticeably different wording — not just swapping a few words
- Same length discipline (32–45 characters, ≥30 floor)
- Neutral, paste-ready tone; avoid distinctive personal phrasing that would make multiple submissions look obviously copied
- Save as a sibling file: `YYYY-MM-DD_觀眾評分表草稿_第二版.md`

---

## Phase 3 — Output

### 3.1 Default Output Format

Return a clean, compact, paste-ready block per speaker:

```
### 講者 1：蘇沂晨 — 微塑膠量測

1. 研究內容與學術深度（建議分數：4/5）
   [comment]

2. 跨領域解釋能力（建議分數：4/5）
   [comment]

3. 投影片架構與邏輯組織（建議分數：4/5）
   [comment]

4. 表達技巧與專業態度（建議分數：4/5）
   [comment]

5. 問答回應與臨場反應（建議分數：4/5）
   [comment]
```

No preamble or post-analysis unless the user asks. If the user says `只有必答題`, omit optional feedback sections.

---

## Phase 4 — Validate Before Sending

Run this checklist on every generated comment before returning to the user or writing to file:

- [ ] Every comment ≥ 30 Chinese characters? (count each one; rewrite any that fall short)
- [ ] Every comment ≤ ~45 characters? (trim if bloated)
- [ ] No two speakers share the same sentence skeleton for the same dimension?
- [ ] Dimension 5 is topic-specific for each speaker, not a generic filler?
- [ ] No fabricated claims about results, data, or Q&A that the user didn't provide?
- [ ] Dimension labels match the 5 fixed names exactly?
- [ ] Traditional Chinese throughout?

If any check fails, fix it before outputting.

---

## Phase 5 — GitHub Archiving

Treat GitHub push as the **default next step** once a usable draft exists, unless the user explicitly says not to push.

### 5.1 File Convention

| Item | Value |
|------|-------|
| Repo path | `/home/node/.openclaw/workspace/Myclawagi` |
| Folder | `Special Topic Discussion/` |
| Filename | `YYYY-MM-DD_觀眾評分表草稿.md` |
| Alternate version | `YYYY-MM-DD_觀眾評分表草稿_第二版.md` |

Markdown structure:

```markdown
# 專題討論觀眾評分表草稿

- 日期：YYYY-MM-DD
- 用途：觀眾評分表填寫參考

---

## 基本欄位提醒
- 日期、學號、姓名

---

## 講者 1：[name] — [topic]

1. 研究內容與學術深度（建議分數：X/5）
   [comment]
...（5 dimensions per speaker）

## 講者 2：...
```

### 5.2 Update Rules

- **Same day, new speakers**: append to existing file; keep earlier blocks unchanged unless the user asks for a rewrite.
- **Alternate version**: create a sibling file; never overwrite the original.

### 5.3 Git Operations

```bash
# 1. Write file
# 2. Stage only the discussion file
git add "Special Topic Discussion/YYYY-MM-DD_觀眾評分表草稿.md"
# 3. Commit with focused message
git commit -m "新增/更新 YYYY-MM-DD 專題討論觀眾評分表草稿"
# 4. Push
git push origin main
# 5. If rejected (remote moved ahead):
git fetch origin main
git pull --rebase origin main
git push origin main
```

Never sweep unrelated workspace changes into the commit.

---

## Trigger Examples

| User says | Action |
|-----------|--------|
| `這是今天專題討論的講者和題目，幫我生成表單評論` | Phase 1→2→3→4→5 |
| `幫我整理這個專題討論 google 表單要填什麼` | Inspect form, summarize required fields |
| `根據這些講者和主題，幫我寫 30 字左右評論` | Phase 1→2→3→4 (skip GitHub) |
| `把剛剛那份專題討論評分稿推到 GitHub` | Phase 5 only |
| `幫我生成一份給同學的版本` | Phase 2.4 → 3 → 4 → 5 |
| `下次遇到專題討論就照這套流程跑` | Acknowledge; this skill is the stored workflow |
