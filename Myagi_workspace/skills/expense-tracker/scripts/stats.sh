#!/usr/bin/env bash
# expenses/stats.sh — 記帳統計工具
# Usage:
#   stats.sh weekly [YYYY-MM-DD]   — 指定日期所在那週的統計（預設本週）
#   stats.sh monthly [YYYY-MM]     — 指定月份統計（預設本月）
#   stats.sh daily [YYYY-MM-DD]    — 指定日期統計（預設今天）
#   stats.sh range YYYY-MM-DD YYYY-MM-DD — 指定區間統計

set -euo pipefail
EXPENSE_DIR="${EXPENSE_DIR:-/home/node/.openclaw/workspace/expenses}"
MODE="${1:-weekly}"

# Helper: sum & categorize from stdin (expects CSV with header)
summarize() {
  awk -F',' 'NR==1{next} {
    total += $5
    cat[$3] += $5
    count++
  }
  END {
    if (count == 0) { print "（無消費紀錄）"; exit }
    printf "💰 總計：$%d（%d 筆）\n\n", total, count
    printf "📊 分類明細：\n"
    for (k in cat) {
      printf "  %-8s $%d\n", k, cat[k]
    }
  }'
}

# Helper: get all relevant CSV lines matching a date range
# Args: start_date end_date (inclusive, YYYY-MM-DD)
filter_range() {
  local start="$1" end="$2"
  # Figure out which month files to scan
  local s_ym="${start:0:7}" e_ym="${end:0:7}"
  local header_printed=0

  for f in "$EXPENSE_DIR"/*.csv; do
    [ -f "$f" ] || continue
    local fym
    fym="$(basename "$f" .csv)"
    # Only scan relevant months
    if [[ "$fym" < "$s_ym" ]] || [[ "$fym" > "$e_ym" ]]; then
      continue
    fi
    while IFS= read -r line; do
      if [[ "$line" == date,* ]]; then
        if [ "$header_printed" -eq 0 ]; then
          echo "$line"
          header_printed=1
        fi
        continue
      fi
      local d="${line%%,*}"
      if [[ ! "$d" < "$start" && ! "$d" > "$end" ]]; then
        echo "$line"
      fi
    done < "$f"
  done
}

case "$MODE" in
  daily)
    TARGET="${2:-$(TZ=Asia/Taipei date +%Y-%m-%d)}"
    echo "📅 日報：$TARGET"
    echo "---"
    filter_range "$TARGET" "$TARGET" | summarize
    ;;
  weekly)
    # Get Monday of target week
    TARGET="${2:-$(TZ=Asia/Taipei date +%Y-%m-%d)}"
    DOW=$(date -d "$TARGET" +%u)  # 1=Mon 7=Sun
    MON=$(date -d "$TARGET -$((DOW-1)) days" +%Y-%m-%d)
    SUN=$(date -d "$MON +6 days" +%Y-%m-%d)
    echo "📅 週報：$MON ~ $SUN"
    echo "---"
    filter_range "$MON" "$SUN" | summarize
    ;;
  monthly)
    TARGET="${2:-$(TZ=Asia/Taipei date +%Y-%m)}"
    FIRST="$TARGET-01"
    LAST=$(date -d "$FIRST +1 month -1 day" +%Y-%m-%d)
    echo "📅 月報：$TARGET"
    echo "---"
    filter_range "$FIRST" "$LAST" | summarize
    ;;
  range)
    START="$2"
    END="$3"
    echo "📅 區間統計：$START ~ $END"
    echo "---"
    filter_range "$START" "$END" | summarize
    ;;
  *)
    echo "Usage: stats.sh {daily|weekly|monthly|range} [args]"
    exit 1
    ;;
esac
