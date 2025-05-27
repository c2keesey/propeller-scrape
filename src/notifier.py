#!/usr/bin/env python3
import subprocess
import sys
import os
import requests
from datetime import datetime
from pathlib import Path

# Load .env file if it exists
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('\'"')

def notify_terminal(title, message, locations=None):
    """Simple terminal notification for now"""
    print("\n" + "="*50)
    print(f"🎬 NEW SHOW ALERT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50)
    print(f"Title: {title}")
    print(f"Details: {message}")
    if locations:
        print("🎯 Target City Locations:")
        for location in locations:
            status = "✓ Available" if location['available'] else "✗ Sold Out"
            print(f"  • {location['raw_text']} - {status}")
    print("="*50 + "\n")

def notify_macos(title, message, locations=None):
    """macOS native notification using osascript"""
    try:
        # Add location info to message if available
        if locations:
            cities = [loc['city'].title() for loc in locations]
            message += f" (in {', '.join(set(cities))})"
        
        subprocess.run([
            'osascript', '-e',
            f'display notification "{message}" with title "{title}" sound name "default"'
        ])
    except Exception as e:
        print(f"macOS notification failed: {e}")

def notify_telegram(title, message, locations=None, show_url=None):
    """Send notification via Telegram bot"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Telegram credentials not found. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")
        return
    
    # Format message with Telegram markdown
    telegram_message = f"🎵 *{title}*\n\n"
    
    if locations:
        telegram_message += "📍 *Available in your cities:*\n"
        for location in locations:
            status = "✅" if location['available'] else "❌ SOLD OUT"
            telegram_message += f"{status} `{location['raw_text']}`\n"
        telegram_message += "\n"
    
    if show_url:
        telegram_message += f"🔗 [View Show Details]({show_url})"
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': telegram_message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✓ Telegram notification sent")
        
    except requests.RequestException as e:
        print(f"Telegram notification failed: {e}")

def notify(shows):
    """Send notifications for new shows"""
    if not shows:
        return
    
    for show in shows:
        title = f"New Show: {show['title']}"
        message = f"{show['description'][:100]}..." if show['description'] else "New show available!"
        locations = show.get('target_locations', [])
        show_url = show.get('url')
        
        # Always print to terminal
        notify_terminal(show['title'], message, locations)
        
        # Try Telegram notification first (most reliable)
        notify_telegram(title, message, locations, show_url)
        
        # Try macOS notification if on Mac (backup)
        if sys.platform == 'darwin':
            notify_macos(title, message, locations)

if __name__ == "__main__":
    # Test notification with locations
    test_show = {
        'title': 'Test Concert - The Weeknd',
        'description': 'This is a test notification for The Weeknd concert',
        'date': '2025-05-27',
        'url': 'https://www.propeller.la/rewards/test',
        'target_locations': [
            {
                'raw_text': '6/25/25 @ SoFi Stadium | Los Angeles, CA',
                'city': 'los angeles',
                'available': True
            },
            {
                'raw_text': '6/27/25 @ Chase Center | San Francisco, CA', 
                'city': 'san francisco',
                'available': False
            }
        ]
    }
    notify([test_show])