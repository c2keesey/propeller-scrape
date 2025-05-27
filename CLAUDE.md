# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

```bash
# Run the main scraper
uv run python src/scraper.py

# Run specific modules for testing
uv run python src/notifier.py  # Test notifications
uv run python main.py          # Run minimal entry point

# Install dependencies
uv sync

# Run from entry point (alternative)
uv run python main.py

# Set up Telegram notifications (one-time setup)
./setup_telegram.sh

# Run via automation (recommended for cron)
./run_scraper.sh

# Check automation logs
tail -f logs/scraper.log
tail -f logs/error.log
```

## Architecture Overview

This is a web scraper for the Propeller rewards website that detects new shows/campaigns and sends notifications.

### Core Components

- **src/scraper.py** - Main scraping logic that fetches Propeller rewards page, parses HTML with BeautifulSoup, and detects new content by comparing against stored data
- **src/notifier.py** - Notification system supporting terminal output, Telegram push notifications, and macOS native notifications
- **data/shows.json** - Local storage for tracking seen shows/campaigns with metadata (first_seen, notified status)

### Data Flow

1. Scraper fetches https://www.propeller.la/rewards 
2. Parses HTML using multiple CSS selectors to find campaign/reward items
3. Compares against existing shows.json to detect new content
4. New shows trigger notifications and are saved to local storage
5. Each show gets unique ID based on title + date for deduplication

### Key Implementation Details

- Uses requests with User-Agent headers to avoid blocking
- Robust HTML parsing with fallback selectors for different page layouts
- Local JSON storage for persistence between runs
- Multi-platform notifications (Telegram, macOS osascript, terminal fallback)
- Location-specific filtering for Los Angeles, San Francisco, and Boulder
- Individual show page analysis for venue details and ticket availability
- Designed for cron job automation with minimal output when no new content found

## Automation Best Practices

### Cron Setup
- **Use run_scraper.sh** - The wrapper script handles paths, logging, and error notifications
- **Full paths required** - Cron has limited PATH, use `/opt/homebrew/bin/uv` not just `uv`
- **Absolute paths only** - Never use relative paths in cron jobs
- **Logging enabled** - All runs logged to `logs/scraper.log` and `logs/error.log`
- **Error notifications** - Script sends Telegram alerts for failures

### Troubleshooting
- **Check cron jobs**: `crontab -l`
- **Monitor logs**: `tail -f logs/scraper.log` and `tail -f logs/error.log` 
- **Common issues**: JSON syntax errors, missing environment variables, PATH issues
- **Test wrapper**: Run `./run_scraper.sh` manually to verify it works

### Current Setup
- Cron job runs every minute for testing: `* * * * * /Users/c2k/Projects/propeller-scrape/run_scraper.sh`
- Production recommended: Every 15 minutes (`*/15 * * * *`)
- Logs automatically rotated to prevent disk space issues

## Memories

- Using Telegram for notifications
- always use uv run not python for scripts
- Cron automation is fully working with wrapper script and logging