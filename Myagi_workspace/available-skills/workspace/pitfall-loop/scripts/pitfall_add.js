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
    } else {
      out._.push(a);
    }
  }
  return out;
}

function usage() {
  console.log(`Usage:
  node pitfall_add.js --title "短標題" --category code --taskType coding \
    --symptom "現象" --rootCause "根因" --fix "修法" --prevention "預防" \
    [--severity low|medium|high] [--tags a,b] [--context "補充"] [--source chat] [--skip-daily]

Required:
  --title
`);
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function utcNow() {
  return new Date();
}

function pad2(n) {
  return String(n).padStart(2, '0');
}

function utcDate(d = utcNow()) {
  return `${d.getUTCFullYear()}-${pad2(d.getUTCMonth() + 1)}-${pad2(d.getUTCDate())}`;
}

function utcTime(d = utcNow()) {
  return `${pad2(d.getUTCHours())}:${pad2(d.getUTCMinutes())} UTC`;
}

function normalizeRecurrenceKey(s) {
  return (s || '')
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 120);
}

function appendDailyNote(workspace, e) {
  const memoryDir = path.join(workspace, 'memory');
  ensureDir(memoryDir);
  const date = utcDate(new Date(e.createdAt));
  const file = path.join(memoryDir, `${date}.md`);
  if (!fs.existsSync(file)) fs.writeFileSync(file, `# ${date}\n\n`, 'utf8');

  const lines = [];
  lines.push(`## ${utcTime(new Date(e.createdAt))} — [Pitfall] ${e.title}`);
  lines.push(`- id: ${e.id}`);
  lines.push(`- category/taskType: ${e.category}/${e.taskType}`);
  if (e.symptom) lines.push(`- symptom: ${e.symptom}`);
  if (e.rootCause) lines.push(`- rootCause: ${e.rootCause}`);
  if (e.fix) lines.push(`- fix: ${e.fix}`);
  if (e.prevention) lines.push(`- prevention: ${e.prevention}`);
  fs.appendFileSync(file, `${lines.join('\n')}\n\n`, 'utf8');
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    process.exit(0);
  }

  const title = (args.title || '').trim();
  if (!title) {
    usage();
    process.exit(1);
  }

  const workspace = args.workspace
    ? path.resolve(args.workspace)
    : path.resolve(__dirname, '../../..');

  const now = utcNow();
  const entry = {
    id: `${now.getTime()}-${Math.random().toString(36).slice(2, 8)}`,
    createdAt: now.toISOString(),
    date: utcDate(now),
    title,
    category: (args.category || 'general').toLowerCase(),
    taskType: (args.taskType || 'general').toLowerCase(),
    severity: (args.severity || 'medium').toLowerCase(),
    status: (args.status || 'resolved').toLowerCase(),
    symptom: (args.symptom || '').trim(),
    rootCause: (args.rootCause || '').trim(),
    fix: (args.fix || '').trim(),
    prevention: (args.prevention || '').trim(),
    context: (args.context || '').trim(),
    source: (args.source || 'chat').toLowerCase(),
    tags: (args.tags || '')
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean)
      .map((x) => x.replace(/^#/, '').toLowerCase()),
  };

  entry.recurrenceKey = normalizeRecurrenceKey(entry.rootCause || entry.title);

  const pitfallFile = path.join(workspace, 'memory', 'pitfalls.jsonl');
  ensureDir(path.dirname(pitfallFile));
  fs.appendFileSync(pitfallFile, `${JSON.stringify(entry)}\n`, 'utf8');

  if (!args['skip-daily']) appendDailyNote(workspace, entry);

  console.log(`Added pitfall: ${entry.id}`);
  console.log(`File: ${path.relative(workspace, pitfallFile)}`);
  console.log(`category/taskType: ${entry.category}/${entry.taskType}`);
}

main();
