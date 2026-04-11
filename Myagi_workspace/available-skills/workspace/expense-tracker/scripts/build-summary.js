#!/usr/bin/env node
// build-summary.js — 產生記帳摘要 CSV（各月份總額 + 全部累計）
// Usage: node build-summary.js <output.csv>

const fs = require('fs');
const path = require('path');

const EXPENSE_DIR = process.env.EXPENSE_DIR || path.join(__dirname);
const OUTPUT = process.argv[2] || path.join(__dirname, 'summary.csv');

function parseCSVLine(line) {
  return line.split(',');
}

const csvFiles = fs.readdirSync(EXPENSE_DIR)
  .filter(f => /^\d{4}-\d{2}\.csv$/.test(f))
  .sort();

const rows = [['period', 'record_count', 'total_amount']];
let grandCount = 0;
let grandTotal = 0;

for (const csvFile of csvFiles) {
  const filePath = path.join(EXPENSE_DIR, csvFile);
  const content = fs.existsSync(filePath) ? fs.readFileSync(filePath, 'utf8').trim() : '';

  if (!content) {
    rows.push([csvFile.replace('.csv', ''), '0', '0']);
    continue;
  }

  const lines = content.split('\n').filter(Boolean);
  let count = 0;
  let total = 0;

  for (let i = 1; i < lines.length; i++) {
    const cols = parseCSVLine(lines[i]);
    const amount = Number(cols[4]) || 0;
    total += amount;
    count += 1;
  }

  rows.push([csvFile.replace('.csv', ''), String(count), String(total)]);
  grandCount += count;
  grandTotal += total;
}

rows.push(['ALL_TIME', String(grandCount), String(grandTotal)]);

const output = rows.map(row => row.join(',')).join('\n') + '\n';
fs.writeFileSync(OUTPUT, output, 'utf8');

console.log(`Summary CSV written to: ${OUTPUT}`);
console.log(`Months: ${csvFiles.length}`);
console.log(`All-time total: ${grandTotal}`);
