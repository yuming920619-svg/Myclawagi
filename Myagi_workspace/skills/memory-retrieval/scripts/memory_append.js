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
      if (!next || next.startsWith('--')) {
        out[key] = true;
      } else {
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
  node memory_append.js --text "note" [--title "short title"] [--tags tag1,tag2]
  node memory_append.js --scope longterm --text "stable preference"

Options:
  --scope daily|longterm   default: daily
  --date YYYY-MM-DD        daily file date (default: today in UTC)
  --title TEXT             short heading
  --text TEXT              required note body
  --tags a,b,c             optional comma-separated tags
  --workspace PATH         workspace root (default: auto)
`);
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function pad2(n) {
  return String(n).padStart(2, '0');
}

function utcDate() {
  const d = new Date();
  return `${d.getUTCFullYear()}-${pad2(d.getUTCMonth() + 1)}-${pad2(d.getUTCDate())}`;
}

function utcTime() {
  const d = new Date();
  return `${pad2(d.getUTCHours())}:${pad2(d.getUTCMinutes())} UTC`;
}

function appendDaily(file, title, text, tags, source) {
  const dateHeader = `# ${path.basename(file, '.md')}\n\n`;
  if (!fs.existsSync(file)) {
    fs.writeFileSync(file, dateHeader, 'utf8');
  }

  const lines = [];
  lines.push(`## ${utcTime()}${title ? ` — ${title}` : ''}`);
  if (source) lines.push(`- source: ${source}`);
  if (tags.length) lines.push(`- tags: ${tags.map((t) => `#${t}`).join(' ')}`);

  const bodyLines = text
    .split(/\r?\n/)
    .map((x) => x.trim())
    .filter(Boolean);

  if (bodyLines.length === 1) {
    lines.push(`- note: ${bodyLines[0]}`);
  } else {
    lines.push('- note:');
    for (const bl of bodyLines) lines.push(`  - ${bl}`);
  }

  fs.appendFileSync(file, `${lines.join('\n')}\n\n`, 'utf8');
}

function appendLongterm(file, title, text, tags) {
  const date = utcDate();
  const time = utcTime();
  if (!fs.existsSync(file)) {
    fs.writeFileSync(file, '# Memory\n\n## Auto-captured\n\n', 'utf8');
  }

  let current = fs.readFileSync(file, 'utf8');
  if (!current.includes('## Auto-captured')) {
    current = `${current.trim()}\n\n## Auto-captured\n\n`;
    fs.writeFileSync(file, current, 'utf8');
  }

  const tagText = tags.length ? ` [${tags.join(', ')}]` : '';
  const titleText = title ? `${title}: ` : '';
  const entry = `- ${date} ${time} — ${titleText}${text}${tagText}\n`;
  fs.appendFileSync(file, entry, 'utf8');
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    process.exit(0);
  }

  const text = (args.text || '').trim();
  if (!text) {
    usage();
    process.exit(1);
  }

  const scope = (args.scope || 'daily').toLowerCase();
  if (!['daily', 'longterm'].includes(scope)) {
    console.error('Invalid --scope. Use daily or longterm.');
    process.exit(1);
  }

  const workspace = args.workspace
    ? path.resolve(args.workspace)
    : path.resolve(__dirname, '../../..');

  const tags = (args.tags || '')
    .split(',')
    .map((x) => x.trim())
    .filter(Boolean)
    .map((x) => x.replace(/^#/, ''));

  const title = (args.title || '').trim();

  if (scope === 'daily') {
    const date = (args.date || utcDate()).trim();
    const memoryDir = path.join(workspace, 'memory');
    ensureDir(memoryDir);
    const file = path.join(memoryDir, `${date}.md`);
    appendDaily(file, title, text, tags, args.source || 'chat');
    console.log(`Appended daily memory: ${path.relative(workspace, file)}`);
    return;
  }

  const file = path.join(workspace, 'MEMORY.md');
  appendLongterm(file, title, text, tags);
  console.log(`Appended long-term memory: ${path.relative(workspace, file)}`);
}

main();
