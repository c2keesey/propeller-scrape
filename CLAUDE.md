# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A web scraper for propeller.la that detects new concert tickets in target cities (LA, SF, Boulder) and sends Telegram notifications. Also includes a Telegram bot that lets you send messages to a headless Claude Code session to modify the repo remotely.

## Commands

```bash
# Run the scraper (checks for new shows, sends notifications)
uv run python src/scraper.py

# Run the Telegram bot listener
uv run python bot.py

# Cron wrapper for scraper
./run_scraper.sh

# Bot wrapper (for systemd/background)
./run_bot.sh
```

## Architecture

- **src/scraper.py** — Scrapes propeller.la/rewards, parses HTML with BeautifulSoup, detects new shows by comparing against `data/shows.json`. Checks individual show pages for target city availability via `div.shop_sizes` elements.
- **src/notifier.py** — Sends notifications via Telegram, terminal, and macOS (if available). Loads credentials from `.env`.
- **bot.py** — Telegram bot that long-polls for messages, routes them to a headless Claude Code session (`claude -p`), auto-commits any changes Claude makes, and replies with results. Maintains session continuity via `.bot_session`.
- **telegram_toolkit/** — Telegram API wrapper and cron utilities, shared with tech-digest.
- **data/shows.json** — Tracks all seen shows with metadata (first_seen, notified, is_show, target_locations).

## Key Patterns

- Claude CLI is invoked as a subprocess (`claude -p`) for bot interactions
- The bot auto-commits and pushes any file changes Claude makes, with commit messages prefixed `Auto:`
- Send `/reset` to the bot to clear the Claude session
- Always use `uv run` not bare `python`
- Target cities: Los Angeles, San Francisco, Boulder
