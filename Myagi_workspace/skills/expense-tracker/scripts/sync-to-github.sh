#!/usr/bin/env bash
# sync-to-github.sh — 產生 Excel 並推送到 GitHub repo 的 Expense tracking 資料夾
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXPENSE_DIR="${EXPENSE_DIR:-/home/node/.openclaw/workspace/expenses}"
REPO_DIR="/home/node/.openclaw/workspace/Myclawagi"
TARGET_DIR="$REPO_DIR/Expense tracking"
XLSX_NAME="expenses.xlsx"

# 1. Generate Excel
echo "📊 Generating Excel..."
node "$SCRIPT_DIR/csv2xlsx.js" "$TARGET_DIR/$XLSX_NAME"

# 2. Also copy raw CSVs for reference
echo "📋 Copying CSV files..."
for f in "$EXPENSE_DIR"/*.csv; do
  [ -f "$f" ] && cp "$f" "$TARGET_DIR/"
done

# 3. Git pull, commit & push
cd "$REPO_DIR"
echo "🔄 Pulling latest..."
git pull --rebase origin main 2>&1 || true
git add "Expense tracking/"
if git diff --cached --quiet; then
  echo "✅ No changes to push."
else
  TODAY=$(TZ=Asia/Taipei date +%Y-%m-%d)
  git commit -m "📝 記帳更新 $TODAY"
  git push origin main 2>&1 || git push origin master 2>&1
  echo "✅ Pushed to GitHub."
fi
