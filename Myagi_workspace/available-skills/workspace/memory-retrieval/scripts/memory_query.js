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
  node memory_query.js "query text" [--top 8] [--context 1] [--json]
  node memory_query.js --query "query text" --top 10 --context 2

Searches MEMORY.md + memory/*.md with lexical scoring and prints top snippets.`);
}

function isCjk(ch) {
  return /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}]/u.test(ch);
}

function buildTerms(query) {
  const q = (query || '').trim().toLowerCase();
  if (!q) return [];

  const tokenTerms = q
    .split(/[^\p{L}\p{N}_]+/u)
    .map((x) => x.trim())
    .filter((x) => x.length >= 2);

  const chars = [...q].filter((c) => isCjk(c));
  const cjkTerms = [];
  if (chars.length >= 2) {
    for (let n = 2; n <= 3; n += 1) {
      for (let i = 0; i <= chars.length - n; i += 1) {
        cjkTerms.push(chars.slice(i, i + n).join(''));
        if (cjkTerms.length >= 40) break;
      }
      if (cjkTerms.length >= 40) break;
    }
  }

  return [...new Set([q, ...tokenTerms, ...cjkTerms])];
}

function lineScore(line, query, terms) {
  const t = line.toLowerCase();
  let score = 0;

  if (query && t.includes(query)) score += 6;

  for (const term of terms) {
    if (!term || term === query) continue;
    if (t.includes(term)) {
      score += term.length >= 4 ? 2 : 1;
    }
  }

  if (/\b(todo|next|decision|preference|deadline|action)\b/i.test(line)) score += 1;
  if (/[待辦|決定|偏好|截止|提醒]/u.test(line)) score += 1;

  return score;
}

function readUtf8(file) {
  return fs.readFileSync(file, 'utf8');
}

function listMemoryFiles(workspace) {
  const files = [];
  const memoryMd = path.join(workspace, 'MEMORY.md');
  if (fs.existsSync(memoryMd)) files.push(memoryMd);

  const memoryDir = path.join(workspace, 'memory');
  if (fs.existsSync(memoryDir) && fs.statSync(memoryDir).isDirectory()) {
    for (const name of fs.readdirSync(memoryDir)) {
      if (name.endsWith('.md')) files.push(path.join(memoryDir, name));
    }
  }

  return files.sort();
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const queryRaw = args.query || args._.join(' ');
  const query = (queryRaw || '').trim().toLowerCase();

  if (!query || args.help) {
    usage();
    process.exit(query ? 0 : 1);
  }

  const topN = Math.max(1, Math.min(50, Number(args.top || 8)));
  const context = Math.max(0, Math.min(5, Number(args.context || 1)));

  const workspace = args.workspace
    ? path.resolve(args.workspace)
    : path.resolve(__dirname, '../../..');

  const files = listMemoryFiles(workspace);
  if (files.length === 0) {
    console.log('No memory files found.');
    process.exit(0);
  }

  const terms = buildTerms(query);
  const hits = [];

  for (const file of files) {
    const rel = path.relative(workspace, file);
    const lines = readUtf8(file).split(/\r?\n/);

    for (let i = 0; i < lines.length; i += 1) {
      const line = lines[i];
      if (!line || !line.trim()) continue;

      const score = lineScore(line, query, terms);
      if (score <= 0) continue;

      const start = Math.max(0, i - context);
      const end = Math.min(lines.length, i + context + 1);
      const snippet = lines.slice(start, end).join('\n').trim();

      hits.push({
        score,
        path: rel,
        line: i + 1,
        text: line.trim(),
        snippet,
      });
    }
  }

  hits.sort((a, b) => b.score - a.score || a.path.localeCompare(b.path) || a.line - b.line);
  const results = hits.slice(0, topN);

  if (args.json) {
    console.log(JSON.stringify({ query: queryRaw, totalHits: hits.length, results }, null, 2));
    return;
  }

  console.log(`Query: ${queryRaw}`);
  console.log(`Files: ${files.length} | Hits: ${hits.length} | Showing top ${results.length}`);
  console.log('');

  results.forEach((r, idx) => {
    console.log(`[${idx + 1}] score=${r.score} Source: ${r.path}#L${r.line}`);
    console.log(r.snippet);
    console.log('---');
  });
}

main();
