#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (!token.startsWith('--')) continue;
    const key = token.slice(2);
    if (key === 'dry-run') {
      out.dryRun = true;
      continue;
    }
    const next = argv[i + 1];
    if (next == null || next.startsWith('--')) {
      throw new Error(`Missing value for --${key}`);
    }
    out[key] = next;
    i += 1;
  }
  return out;
}

function requireArg(args, key) {
  const value = args[key];
  if (value == null || value === '') {
    throw new Error(`Required argument missing: --${key}`);
  }
  return value;
}

function parseCSVLine(line) {
  return line.split(',');
}

function computeMonthStats(expenseDir, month) {
  const filePath = path.join(expenseDir, `${month}.csv`);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Expense file not found for month ${month}: ${filePath}`);
  }

  const raw = fs.readFileSync(filePath, 'utf8').trim();
  const lines = raw ? raw.split('\n').filter(Boolean) : [];
  let total = 0;
  let count = 0;
  const categories = new Map();

  for (let i = 1; i < lines.length; i++) {
    const cols = parseCSVLine(lines[i]);
    const category = cols[2] || '其他';
    const amount = Number(cols[4]) || 0;
    total += amount;
    count += 1;
    categories.set(category, (categories.get(category) || 0) + amount);
  }

  return {
    total,
    count,
    summary: Array.from(categories.entries())
      .map(([category, amount]) => `${category} $${amount}`)
      .join(' | '),
  };
}

function monthLabelFromMonth(month) {
  const num = Number(String(month).split('-')[1]);
  return `${num}月`;
}

const EMOJI = {
  '餐飲': '🍱',
  '飲料': '🧋',
  '交通': '🚇',
  '日用品': '🛒',
  '娛樂': '🎮',
  '學費': '📚',
  '服飾': '👕',
  '醫療': '💊',
  '其他': '📦',
};

try {
  const args = parseArgs(process.argv.slice(2));

  const item = requireArg(args, 'item');
  const amount = requireArg(args, 'amount');
  const category = requireArg(args, 'category');
  const note = args.note || '';
  const emoji = args.emoji || EMOJI[category] || '📦';
  const expenseDir = args['expense-dir'] || '/home/node/.openclaw/workspace/expenses';

  let month = args.month;
  if (!month && args.date) {
    month = String(args.date).slice(0, 7);
  }
  if (!month) {
    throw new Error('Required argument missing: --month (or provide --date YYYY-MM-DD)');
  }

  let monthTotal = args['month-total'];
  let monthCount = args['month-count'];
  let summary = args.summary;

  if (monthTotal == null || monthCount == null || summary == null) {
    const stats = computeMonthStats(expenseDir, month);
    monthTotal = monthTotal ?? String(stats.total);
    monthCount = monthCount ?? String(stats.count);
    summary = summary ?? stats.summary;
  }

  const monthLabel = args['month-label'] || monthLabelFromMonth(month);
  const channel = args.channel || 'telegram';
  const account = args.account || 'reminder';
  const target = args.target || '8087282597';

  const lines = [
    '📝 記帳更新',
    `${emoji} ${item} $${amount}（${category}）`,
  ];

  if (note) {
    lines.push(`備註：${note}`);
  }

  lines.push(
    '',
    `📊 ${monthLabel}累計：$${monthTotal}（${monthCount}筆）`,
    `  ${summary}`,
  );

  const message = lines.join('\n');

  if (args.dryRun) {
    console.log(message);
    process.exit(0);
  }

  const result = spawnSync(
    'openclaw',
    ['message', 'send', '--channel', channel, '--account', account, '--target', target, '-m', message],
    {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    },
  );

  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);

  if (result.error) {
    throw result.error;
  }

  process.exit(result.status ?? 1);
} catch (error) {
  console.error(`send-reminder.js failed: ${error.message}`);
  process.exit(1);
}
