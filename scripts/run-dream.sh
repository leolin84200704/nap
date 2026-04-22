#!/bin/bash
# Auto Dreaming — Memory Consolidation Script
# Runs Claude Code headless with the dream prompt
#
# Usage:
#   ./scripts/run-dream.sh          # run once
#   ./scripts/run-dream.sh --dry    # dry run (print command only)
#
# Schedule via launchd (macOS) or crontab (Linux):
#   0 20 * * * cd /path/to/nap && ./scripts/run-dream.sh >> logs/cron.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DREAM_PROMPT="$SCRIPT_DIR/dream.md"
LOG_FILE="$PROJECT_DIR/logs/dream-$(date +%Y-%m-%d).log"

# Check dependencies
if ! command -v claude &> /dev/null; then
    echo "[$(date)] ERROR: claude CLI not found in PATH" | tee -a "$LOG_FILE"
    exit 1
fi

if [ ! -f "$DREAM_PROMPT" ]; then
    echo "[$(date)] ERROR: Dream prompt not found at $DREAM_PROMPT" | tee -a "$LOG_FILE"
    exit 1
fi

# Dry run mode
if [ "${1:-}" = "--dry" ]; then
    echo "Would run:"
    echo "  cd $PROJECT_DIR && claude -p \"\$(cat $DREAM_PROMPT)\" --allowedTools Read,Write,Edit,Glob,Grep,Bash"
    exit 0
fi

echo "[$(date)] Starting Auto Dream..." | tee -a "$LOG_FILE"

cd "$PROJECT_DIR"

claude -p "$(cat "$DREAM_PROMPT")" \
    --allowedTools "Read,Write,Edit,Glob,Grep,Bash" \
    2>&1 | tee -a "$LOG_FILE"

echo "[$(date)] Auto Dream completed." | tee -a "$LOG_FILE"
