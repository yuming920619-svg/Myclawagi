#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (!next || next.startsWith('--')) out[key] = true;
      else {
        out[key] = next;
        i += 1;
      }
    } else out._.push(a);
  }
  return out;
}

function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  return fs
    .readFileSync(file, 'utf8')
    .split(/\r?\n/)
    .filter(Boolean)
    .flatMap((l) => {
      try {
        return [JSON.parse(l)];
      } catch (_) {
        return [];
      }
    });
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function pad2(n) {
  return String(n).padStart(2, '0');
}

function utcDate(d = new Date()) {
  return `${d.getUTCFullYear()}-${pad2(d.getUTCMonth() + 1)}-${pad2(d.getUTCDate())}`;
}

function freq(arr, keyFn) {
  const m = new Map();
  for (const x of arr) {
    const k = keyFn(x);
    if (!k) continue;
    m.set(k, (m.get(k) || 0) + 1);
  }
  return [...m.entries()].sort((a, b) => b[1] - a[1]);
}

function top(arr, n = 5) {
  return arr.slice(0, n);
}

function normalize(s) {
  return (s || '').toLowerCase().replace(/\s+/g, ' ').trim();
}

function generateMarkdown({ days, fromDate, toDate, totalAll, recent }) {
  const byCategory = top(freq(recent, (e) => e.category || 'uncategorized'), 10);
  const byTaskType = top(freq(recent, (e) => e.taskType || 'general'), 10);
  const bySeverity = top(freq(recent, (e) => e.severity || 'unknown'), 5);

  const rootCauseFreq = top(
    freq(recent, (e) => normalize(e.rootCause || e.recurrenceKey || e.title)).filter(([k]) => k.length >= 6),
    8,
  );

  const preventionFreq = top(freq(recent, (e) => normalize(e.prevention)).filter(([k]) => k.length >= 6), 8);

  const lines = [];
  lines.push(`# 自我迭代回顧（最近 ${days} 天）`);
  lines.push('');
  lines.push(`- 區間：${fromDate} ~ ${toDate} (UTC)`);
  lines.push(`- 累積坑位總數：${totalAll}`);
  lines.push(`- 本期新增/更新：${recent.length}`);
  lines.push('');

  lines.push('## 1) 分類統計');
  if (!byCategory.length) lines.push('- 無資料');
  else byCategory.forEach(([k, c]) => lines.push(`- ${k}: ${c}`));
  lines.push('');

  lines.push('## 2) 任務型態統計');
  if (!byTaskType.length) lines.push('- 無資料');
  else byTaskType.forEach(([k, c]) => lines.push(`- ${k}: ${c}`));
  lines.push('');

  lines.push('## 3) 嚴重度分佈');
  if (!bySeverity.length) lines.push('- 無資料');
  else bySeverity.forEach(([k, c]) => lines.push(`- ${k}: ${c}`));
  lines.push('');

  lines.push('## 4) 重複根因 Top');
  if (!rootCauseFreq.length) lines.push('- 目前沒有可辨識的重複根因');
  else rootCauseFreq.forEach(([k, c]) => lines.push(`- [${c}x] ${k}`));
  lines.push('');

  lines.push('## 5) 下次任務前 Checklist（由預防措施自動彙整）');
  if (!preventionFreq.length) lines.push('- 尚無 prevention 條目，先建立 3-5 條基本檢查。');
  else preventionFreq.forEach(([k, c]) => lines.push(`- [${c}x] ${k}`));
  lines.push('');

  lines.push('## 6) 建議下週行動');
  const action1 = byCategory[0] ? `優先處理高頻類別「${byCategory[0][0]}」，先補一份 preflight checklist。` : '建立第一版分類規則與最小欄位（category/taskType/rootCause/prevention）。';
  const action2 = rootCauseFreq[0] ? `針對最常見根因（${rootCauseFreq[0][0]}）做一次流程防呆。` : '每次修完 bug 必填 rootCause 與 prevention，避免只記現象。';
  const action3 = '在每次新任務開工前，先查一次 `pitfall_query --checklist`。';
  lines.push(`1. ${action1}`);
  lines.push(`2. ${action2}`);
  lines.push(`3. ${action3}`);
  lines.push('');

  lines.push('## 7) 本期記錄（最近 10 筆）');
  const latest = recent
    .slice()
    .sort((a, b) => String(b.createdAt || '').localeCompare(String(a.createdAt || '')))
    .slice(0, 10);
  if (!latest.length) lines.push('- 無資料');
  else {
    for (const e of latest) {
      lines.push(`- ${e.date || (e.createdAt || '').slice(0, 10)} | ${e.category}/${e.taskType} | ${e.title}`);
    }
  }

  return lines.join('\n');
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const days = Math.max(1, Math.min(90, Number(args.days || 7)));

  const workspace = args.workspace
    ? path.resolve(args.workspace)
    : path.resolve(__dirname, '../../..');
  const sourceFile = path.join(workspace, 'memory', 'pitfalls.jsonl');

  const all = readJsonl(sourceFile);
  const now = new Date();
  const from = new Date(now.getTime() - days * 24 * 3600 * 1000);

  const recent = all.filter((e) => {
    const t = new Date(e.createdAt || e.date || 0).getTime();
    return Number.isFinite(t) && t >= from.getTime();
  });

  const md = generateMarkdown({
    days,
    fromDate: utcDate(from),
    toDate: utcDate(now),
    totalAll: all.length,
    recent,
  });

  if (args.json) {
    console.log(
      JSON.stringify(
        {
          source: path.relative(workspace, sourceFile),
          totalAll: all.length,
          recent: recent.length,
          days,
          markdown: md,
        },
        null,
        2,
      ),
    );
    return;
  }

  const defaultOut = path.join(workspace, 'memory', 'pitfall-reviews', `${utcDate(now)}-review.md`);
  const outFile = args.write ? path.resolve(args.write) : defaultOut;

  ensureDir(path.dirname(outFile));
  fs.writeFileSync(outFile, `${md}\n`, 'utf8');

  console.log(`Wrote review: ${path.relative(workspace, outFile)}`);
  console.log('');
  console.log(md);
}

main();
