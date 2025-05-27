# propeller-scrape

A smart web scraper that monitors the Propeller rewards website for new concert tickets and shows, with intelligent location filtering for your target cities.

## Overview
This Python script automatically checks the Propeller rewards website for new show listings and sends notifications when concerts become available in Los Angeles, San Francisco, or Boulder. It goes beyond basic scraping by examining individual show pages to find specific venue locations and ticket availability.

## Features
- **Smart Show Detection**: Distinguishes between concerts/shows and merchandise using keyword analysis
- **Location-Specific Filtering**: Only notifies for shows in Los Angeles, San Francisco, or Boulder
- **Individual Page Analysis**: Visits each show page to extract venue details and availability
- **Availability Tracking**: Shows whether tickets are available or sold out for each venue
- **Duplicate Prevention**: Tracks seen shows to avoid repeat notifications
- **Multi-Platform Notifications**: Telegram push notifications + terminal output + macOS native notifications
- **Cron-Friendly**: Minimal output when no new shows found, perfect for automation

## Tech Stack
- **Python** with uv for dependency management
- **requests** for HTTP requests
- **BeautifulSoup** for HTML parsing
- **JSON files** for local storage

## Project Structure
```
propeller-scrape/
├── src/
│   ├── scraper.py      # Main scraping logic
│   └── notifier.py     # Notification handling
├── data/
│   └── shows.json      # Local storage of seen shows
├── pyproject.toml      # Project config and dependencies
└── README.md
```

## Setup

### 1. Install Dependencies
```bash
uv sync
```

### 2. Set Up Telegram Notifications (Recommended)
```bash
# Run the interactive setup script
./setup_telegram.sh
```

This will guide you through:
1. Creating a Telegram bot via @BotFather
2. Getting your bot token and chat ID
3. Setting up environment variables

### 3. Basic Usage
```bash
# Run the scraper once
uv run python src/scraper.py

# Test notifications only
uv run python src/notifier.py
```

### Automation Setup

#### Local Cron (Requires Computer Always On)

**Recommended approach using the wrapper script:**
```bash
# Make the script executable
chmod +x /path/to/propeller-scrape/run_scraper.sh

# Set up cron job using the wrapper script (every 15 minutes)
*/15 * * * * /path/to/propeller-scrape/run_scraper.sh

# For testing (every minute)
* * * * * /path/to/propeller-scrape/run_scraper.sh
```

**Alternative direct approach:**
```bash
# Requires full paths since cron has limited PATH
*/15 * * * * cd /path/to/propeller-scrape && /opt/homebrew/bin/uv run python src/scraper.py
```

**Note:** Local cron requires your machine to be powered on and awake. Missed runs are not executed later.

#### Troubleshooting Cron Setup

**Check if cron job is running:**
```bash
# View current cron jobs
crontab -l

# Monitor cron activity (check logs)
tail -f /path/to/propeller-scrape/logs/scraper.log
tail -f /path/to/propeller-scrape/logs/error.log
```

**Common issues:**
- **"command not found"**: Cron has limited PATH, use full paths (`/opt/homebrew/bin/uv`)
- **"No such file"**: Use absolute paths, not relative paths
- **JSON errors**: Check `logs/error.log` for parsing issues

#### Cloud Alternatives (24/7 Operation)
For reliable 24/7 monitoring without keeping your computer on:

- **GitHub Actions** - Free cron jobs in GitHub's cloud (recommended)
- **Cloud VPS** - $5/month DigitalOcean/Linode server
- **Raspberry Pi** - $35 mini computer for home automation
- **AWS Lambda** - Serverless functions with scheduled triggers

## Example Output

### When New Shows Found
```
Found 2 new show(s) in target cities:
  - Earn a Pair of Tickets To See Remy Bond at a Show Near You (2025-05-27)
    • 6/26/25 @ The Independent | San Francisco, CA - ✓ Available
    • 6/27/25 @ El Rey Theatre | Los Angeles, CA - ✓ Available
  - Earn a Pair of Tickets To See Samia at a Show Near You (2025-05-27)
    • 9/19/25 @ The Fonda Theatre | Los Angeles, CA - ✓ Available
    • 9/20/25 @ The Fillmore | San Francisco, CA - ✗ Sold Out
```

### When No New Shows
```
No new shows found in target cities (Los Angeles, San Francisco, Boulder)
```

### Telegram Notification Example
When a new show is found, you'll receive a Telegram message like:
```
🎵 **New Show: Earn a Pair of Tickets To See The Weeknd**

📍 **Available in your cities:**
✅ `6/25/25 @ SoFi Stadium | Los Angeles, CA`
❌ SOLD OUT `6/27/25 @ Chase Center | San Francisco, CA`

🔗 [View Show Details](https://www.propeller.la/rewards/...)
```

## Target Cities

The scraper monitors for shows in these cities:
- **Los Angeles, CA** (including "LA, CA" variants)
- **San Francisco, CA** (including "SF, CA" variants)  
- **Boulder, CO**

To modify target cities, edit the `target_cities` dictionary in `src/scraper.py:184`.

## Data Storage

Show data is stored in `data/shows.json` with the following structure:
```json
{
  "show_id": {
    "title": "Show Title",
    "url": "https://propeller.la/rewards/...",
    "date": "2025-05-27",
    "description": "Show description",
    "first_seen": "2025-05-27T13:48:00.273859",
    "notified": false,
    "is_show": true,
    "target_locations": [
      {
        "raw_text": "6/26/25 @ The Independent | San Francisco, CA",
        "city": "san francisco", 
        "available": true
      }
    ]
  }
}
```
