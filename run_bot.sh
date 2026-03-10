#!/bin/bash

# Propeller Bot - Telegram bot listener
# Runs the bot that routes messages to a headless Claude Code session

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/bot.log"

mkdir -p "$SCRIPT_DIR/logs"
cd "$SCRIPT_DIR"

if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting propeller-scrape bot..." >> "$LOG_FILE"

uv run python bot.py 2>&1 | tee -a "$LOG_FILE"
