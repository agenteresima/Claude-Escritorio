#!/usr/bin/env bash
# Quick health check — call from cron or monitoring
# Returns 0 if bot is healthy, 1 otherwise
# Usage: bash scripts/health_check.sh [API_KEY] [HOST]

API_KEY=${1:-${BOT_API_KEY:-changeme}}
HOST=${2:-localhost:8000}
THRESHOLD_DD=10   # alert if drawdown > this %

response=$(curl -sf -H "x-api-key: ${API_KEY}" "http://${HOST}/status" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "ERROR: API not reachable at ${HOST}"
    exit 1
fi

paused=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('paused','?'))")
strategy=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('active_strategy','?'))")
open_pos=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('open_positions',0))")

echo "Bot status   : $([ "$paused" = "False" ] && echo "RUNNING" || echo "PAUSED")"
echo "Strategy     : ${strategy}"
echo "Open positions: ${open_pos}"

metrics=$(curl -sf -H "x-api-key: ${API_KEY}" "http://${HOST}/metrics" 2>/dev/null)
if [ -n "$metrics" ]; then
    win_rate=$(echo "$metrics" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d.get('win_rate',0):.1f}\")" 2>/dev/null)
    total_pnl=$(echo "$metrics" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d.get('total_pnl',0):+.2f}\")" 2>/dev/null)
    echo "Win rate     : ${win_rate}%"
    echo "Total PnL    : ${total_pnl} USDT"
fi

exit 0
