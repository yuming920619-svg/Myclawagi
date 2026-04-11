#!/usr/bin/env bash
# sync-to-github.sh — 同步 CSV 記帳檔與摘要 CSV 到 GitHub repo 的 Expense tracking 資料夾
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXPENSE_DIR="${EXPENSE_DIR:-/home/node/.openclaw/workspace/expenses}"
REPO_DIR="/home/node/.openclaw/workspace/Myclawagi"
TARGET_DIR="$REPO_DIR/Expense tracking"
SUMMARY_NAME="summary.csv"

# 1. Copy raw monthly CSVs
echo "📋 Copying monthly CSV files..."
for f in "$EXPENSE_DIR"/*.csv; do
  [ -f "$f" ] || continue
  base="$(basename "$f")"
  [[ "$base" =~ ^[0-9]{4}-[0-9]{2}\.csv$ ]] || continue
  cp "$f" "$TARGET_DIR/"
done

# 2. Generate summary CSV
echo "📊 Generating summary CSV..."
EXPENSE_DIR="$EXPENSE_DIR" node "$SCRIPT_DIR/build-summary.js" "$TARGET_DIR/$SUMMARY_NAME"

# 3. Remove legacy Excel export if present
if [ -f "$TARGET_DIR/expenses.xlsx" ]; then
  echo "🧹 Removing legacy Excel export..."
  rm -f "$TARGET_DIR/expenses.xlsx"
fi

# 4. Git fetch, rebase-safe sync, commit & push
cd "$REPO_DIR"
echo "🔄 Fetching latest..."
git fetch origin

echo "🔄 Rebasing onto latest remote..."
git pull --rebase --autostash origin main

git add "Expense tracking/"
if git diff --cached --quiet; then
  echo "✅ No changes to commit."
else
  TODAY=$(TZ=Asia/Taipei date +%Y-%m-%d)
  git commit -m "📝 記帳更新 $TODAY"
  git push origin main
  echo "✅ Pushed to GitHub."
fi
