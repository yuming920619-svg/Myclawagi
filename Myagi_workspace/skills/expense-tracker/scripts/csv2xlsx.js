#!/usr/bin/env node
// csv2xlsx.js — 將所有月份 CSV 合併為一份 Excel（含月份分頁 + 總表）
// Usage: node csv2xlsx.js <output.xlsx>

const fs = require('fs');
const path = require('path');
const XLSX = require('xlsx');

const EXPENSE_DIR = process.env.EXPENSE_DIR || '/home/node/.openclaw/workspace/expenses';
const OUTPUT = process.argv[2] || path.join(__dirname, 'expenses.xlsx');

// Parse a CSV file into rows
function parseCSV(filePath) {
  const content = fs.readFileSync(filePath, 'utf8').trim();
  if (!content) return [];
  const lines = content.split('\n');
  return lines.map(line => {
    // Simple CSV parse (no quoted commas expected)
    return line.split(',');
  });
}

// Collect all monthly CSV files
const csvFiles = fs.readdirSync(EXPENSE_DIR)
  .filter(f => /^\d{4}-\d{2}\.csv$/.test(f))
  .sort();

if (csvFiles.length === 0) {
  console.log('No CSV files found.');
  process.exit(0);
}

const wb = XLSX.utils.book_new();
const allRows = [['date', 'time', 'category', 'item', 'amount', 'note']];

for (const csvFile of csvFiles) {
  const rows = parseCSV(path.join(EXPENSE_DIR, csvFile));
  if (rows.length <= 1) continue; // header only

  const sheetName = csvFile.replace('.csv', '');

  // Convert amount to number
  const dataRows = rows.map((row, i) => {
    if (i === 0) return row; // header
    return row.map((cell, j) => j === 4 ? Number(cell) || 0 : cell);
  });

  // Add month sheet
  const ws = XLSX.utils.aoa_to_sheet(dataRows);

  // Set column widths
  ws['!cols'] = [
    { wch: 12 }, // date
    { wch: 8 },  // time
    { wch: 10 }, // category
    { wch: 20 }, // item
    { wch: 10 }, // amount
    { wch: 20 }, // note
  ];

  XLSX.utils.book_append_sheet(wb, ws, sheetName);

  // Accumulate for summary (skip header)
  for (let i = 1; i < dataRows.length; i++) {
    allRows.push(dataRows[i]);
  }
}

// Summary sheet
if (allRows.length > 1) {
  // Category summary
  const catTotals = {};
  let grandTotal = 0;
  let count = 0;
  for (let i = 1; i < allRows.length; i++) {
    const cat = allRows[i][2] || '其他';
    const amt = Number(allRows[i][4]) || 0;
    catTotals[cat] = (catTotals[cat] || 0) + amt;
    grandTotal += amt;
    count++;
  }

  const summaryRows = [
    ['📊 消費總覽', '', '', ''],
    ['', '', '', ''],
    ['總筆數', count, '總金額', grandTotal],
    ['', '', '', ''],
    ['分類', '金額', '佔比', ''],
  ];

  for (const [cat, amt] of Object.entries(catTotals).sort((a, b) => b[1] - a[1])) {
    summaryRows.push([cat, amt, grandTotal > 0 ? (amt / grandTotal * 100).toFixed(1) + '%' : '0%', '']);
  }

  const summaryWs = XLSX.utils.aoa_to_sheet(summaryRows);
  summaryWs['!cols'] = [{ wch: 12 }, { wch: 12 }, { wch: 12 }, { wch: 12 }];
  XLSX.utils.book_append_sheet(wb, summaryWs, '總覽');

  // All records sheet
  const allWs = XLSX.utils.aoa_to_sheet(allRows);
  allWs['!cols'] = [
    { wch: 12 }, { wch: 8 }, { wch: 10 }, { wch: 20 }, { wch: 10 }, { wch: 20 },
  ];
  XLSX.utils.book_append_sheet(wb, allWs, '全部紀錄');
}

if (wb.SheetNames.length === 0) {
  // No data yet — create a placeholder sheet
  const emptyWs = XLSX.utils.aoa_to_sheet([['date', 'time', 'category', 'item', 'amount', 'note'], ['（尚無紀錄）','','','',0,'']]);
  XLSX.utils.book_append_sheet(wb, emptyWs, '總覽');
}

XLSX.writeFile(wb, OUTPUT);
console.log(`Excel written to: ${OUTPUT}`);
console.log(`Sheets: ${wb.SheetNames.join(', ')}`);
console.log(`Total records: ${allRows.length - 1}`);
