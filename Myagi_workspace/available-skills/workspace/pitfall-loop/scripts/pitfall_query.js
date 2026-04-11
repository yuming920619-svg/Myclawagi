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

function usage() {
  console.log(`Usage:
  node pitfall_query.js "query text" [--top 8] [--category code] [--taskType coding] [--json] [--checklist]
  node pitfall_query.js --query "telegram reminder" --category messaging --top 5
`);
}

function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/).filter(Boolean);
  const out = [];
  for (const l of lines) {
    try {
      out.push(JSON.parse(l));
    } catch (_) {}
  }
  return out;
}

function buildTerms(query) {
  const q = (query || '').toLowerCase().trim();
  if (!q) return [];
  const terms = q
    .split(/[^\p{L}\p{N}_]+/u)
    .map((x) => x.trim())
    .filter((x) => x.length >= 2);
  return [...new Set([q, ...terms])];
}

function scoreEntry(e, terms) {
  const hay = [
    e.title,
    e.symptom,
    e.rootCause,
    e.fix,
    e.prevention,
    e.context,
    (e.tags || []).join(' '),
    e.category,
    e.taskType,
  ]
    .join(' \n ')
    .toLowerCase();

  let s = 0;
  for (const t of terms) {
    if (!t) continue;
    if (hay.includes(t)) s += t.length >= 4 ? 2 : 1;
  }

  if ((e.severity || '') === 'high') s += 1;
  return s;
}

function topChecklist(entries, limit = 6) {
  const m = new Map();
  for (const e of entries) {
    const p = (e.prevention || '').trim();
    if (!p) continue;
    m.set(p, (m.get(p) || 0) + 1);
  }
  return [...m.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([text, count]) => ({ text, count }));
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    process.exit(0);
  }

  const query = (args.query || args._.join(' ') || '').trim();
  const topN = Math.max(1, Math.min(30, Number(args.top || 8)));

  const workspace = args.workspace
    ? path.resolve(args.workspace)
    : path.resolve(__dirname, '../../..');
  const file = path.join(workspace, 'memory', 'pitfalls.jsonl');

  let entries = readJsonl(file);

  if (args.category) entries = entries.filter((e) => (e.category || '').toLowerCase() === String(args.category).toLowerCase());
  if (args.taskType) entries = entries.filter((e) => (e.taskType || '').toLowerCase() === String(args.taskType).toLowerCase());
  if (args.severity) entries = entries.filter((e) => (e.severity || '').toLowerCase() === String(args.severity).toLowerCase());

  const terms = buildTerms(query);
  const scored = entries.map((e) => ({ e, score: scoreEntry(e, terms) }));

  const filtered = query ? scored.filter((x) => x.score > 0) : scored;
  filtered.sort((a, b) => b.score - a.score || String(b.e.createdAt || '').localeCompare(String(a.e.createdAt || '')));
  const results = filtered.slice(0, topN).map((x) => ({ ...x.e, _score: x.score }));

  if (args.json) {
    console.log(JSON.stringify({ query, total: entries.length, matched: filtered.length, results, checklist: topChecklist(results) }, null, 2));
    return;
  }

  console.log(`Pitfalls file: ${path.relative(workspace, file)}`);
  console.log(`Total entries: ${entries.length} | Matched: ${filtered.length} | Showing: ${results.length}`);
  if (args.category) console.log(`Category filter: ${args.category}`);
  if (args.taskType) console.log(`TaskType filter: ${args.taskType}`);
  if (query) console.log(`Query: ${query}`);
  console.log('');

  results.forEach((r, i) => {
    console.log(`[${i + 1}] (${r._score}) ${r.date || r.createdAt || 'n/a'} | ${r.category}/${r.taskType} | ${r.title}`);
    if (r.symptom) console.log(`  symptom: ${r.symptom}`);
    if (r.rootCause) console.log(`  rootCause: ${r.rootCause}`);
    if (r.prevention) console.log(`  prevention: ${r.prevention}`);
    console.log(`  id: ${r.id}`);
  });

  if (args.checklist) {
    const list = topChecklist(results);
    console.log('\nPreflight checklist (from matched pitfalls):');
    if (!list.length) console.log('- (no prevention notes yet)');
    else list.forEach((x) => console.log(`- [${x.count}x] ${x.text}`));
  }
}

main();
