#!/bin/bash

# Propeller Scraper Automation Script
# This script is designed to run via cron and handles logging and error reporting

# Set up paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/scraper.log"
ERROR_LOG="$SCRIPT_DIR/logs/error.log"

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Function to log with timestamp
log_with_timestamp() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to send error notification via Telegram
send_error_notification() {
    local error_msg="$1"
    cd "$SCRIPT_DIR"
    
    # Load environment variables
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # Send error to Telegram if configured
    if [ ! -z "$TELEGRAM_BOT_TOKEN" ] && [ ! -z "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d chat_id="$TELEGRAM_CHAT_ID" \
            -d text="🚨 Propeller Scraper Error: $error_msg" \
            -d parse_mode="Markdown" > /dev/null 2>&1
    fi
}

# Start logging
log_with_timestamp "Starting Propeller scraper..."

# Change to script directory
cd "$SCRIPT_DIR"

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    log_with_timestamp "Loaded environment variables from .env"
fi

# Run the scraper
/opt/homebrew/bin/uv run python src/scraper.py >> "$LOG_FILE" 2>> "$ERROR_LOG"
EXIT_CODE=$?

# Check if script completed successfully
if [ $EXIT_CODE -eq 0 ]; then
    log_with_timestamp "Scraper completed successfully"
else
    error_msg="Scraper failed with exit code $EXIT_CODE"
    log_with_timestamp "ERROR: $error_msg"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $error_msg" >> "$ERROR_LOG"
    send_error_notification "$error_msg"
fi

# Keep logs under control (keep last 1000 lines)
if [ -f "$LOG_FILE" ]; then
    tail -n 1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

if [ -f "$ERROR_LOG" ]; then
    tail -n 500 "$ERROR_LOG" > "$ERROR_LOG.tmp" && mv "$ERROR_LOG.tmp" "$ERROR_LOG"
fi

exit $EXIT_CODE