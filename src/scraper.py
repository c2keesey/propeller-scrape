#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Add notifier import
sys.path.append(str(Path(__file__).parent))
from notifier import notify

DATA_DIR = Path(__file__).parent.parent / "data"
SHOWS_FILE = DATA_DIR / "shows.json"
PROPELLER_URL = "https://www.propeller.la/points-rewards"

def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)

def load_existing_shows():
    if SHOWS_FILE.exists():
        with open(SHOWS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_shows(shows):
    with open(SHOWS_FILE, 'w') as f:
        json.dump(shows, f, indent=2)

def scrape_propeller_shows():
    print(f"Scraping {PROPELLER_URL}...")
    
    try:
        # First, try the rewards page
        rewards_url = "https://www.propeller.la/rewards"
        response = requests.get(rewards_url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    shows = []
    
    # Look for campaign/reward items - these appear to be the main content
    # Try multiple selectors to find the right elements
    selectors = [
        'a[href*="/campaigns/"]',  # Links to campaigns
        'a[href*="/rewards/"]',    # Links to rewards (concerts, etc)
        'div.campaign-item',
        'article.reward',
        'div[class*="reward"]',
        'div[class*="campaign"]'
    ]
    
    found_items = set()  # Use set to avoid duplicates
    
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            # Extract campaign/show info
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'span'])
            link_elem = element if element.name == 'a' else element.find('a')
            
            if title_elem or (link_elem and link_elem.text.strip()):
                title = title_elem.text.strip() if title_elem else link_elem.text.strip()
                # Clean up title - remove extra whitespace and newlines
                title = ' '.join(title.split())
                url = link_elem.get('href', '') if link_elem else ''
                
                # Skip navigation items
                if any(skip in title.lower() for skip in ['earn points', 'rewards', 'leaders', 'impact', 'learn more']):
                    continue
                
                # Make URL absolute
                if url and not url.startswith('http'):
                    url = f"https://www.propeller.la{url}"
                
                # Create unique ID based on title and URL (not date to avoid midnight duplication)
                show_id = f"{title}_{url}"
                if show_id not in found_items and title:
                    found_items.add(show_id)
                    
                    # Clean description too
                    desc = element.get_text(strip=True) if element else ''
                    desc = ' '.join(desc.split())[:200]
                    
                    show = {
                        'title': title[:100],  # Limit title length
                        'url': url,
                        'date': datetime.now().strftime('%Y-%m-%d'),  # Use current date as placeholder
                        'description': desc
                    }
                    shows.append(show)
    
    # If no campaigns found, look for any links that might be rewards
    if not shows:
        all_links = soup.find_all('a', href=lambda x: x and ('/campaigns/' in x or '/rewards/' in x))
        for link in all_links:
            if link.text.strip():
                show = {
                    'title': link.text.strip(),
                    'url': f"https://www.propeller.la{link['href']}" if not link['href'].startswith('http') else link['href'],
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'description': ''
                }
                shows.append(show)
    
    print(f"Found {len(shows)} items")
    return shows

def is_show_or_concert(show):
    """Determine if an item is a concert/show vs merchandise/other"""
    title = show['title'].lower()
    description = show.get('description', '').lower()
    url = show.get('url', '').lower()
    
    # Concert/show indicators
    show_indicators = [
        'tickets to see',
        'pair of tickets',
        'festival',
        'concert',
        'show near you',
        'at a show',
        'passes to',
        'vip passes',
        'festival passes',
        'off your tickets',
        'tour poster',  # Usually signed posters from tours
    ]
    
    # Merchandise/other indicators (exclusions)
    merch_indicators = [
        't-shirt',
        'shirt',
        'hoodie',
        'sticker',
        'tote bag',
        'hat',
        'merch',
        'puzzle',
        'rolling papers',
        'yoga mat',
        'earplugs',
        'gift card',
        'tree planted',
        'meals to families',
        'water kit',
        'donate',
        'surprise reward',
        'points to donate',
        'boost',
        'propeller merch',
        'see all merch',
        'sweepstakes',
        'lyric sheet',
        'gift wrap',
        'poster signed by',  # Generic signed posters
        'pennant',
        'patch',
        'pin supporting',
    ]
    
    text_to_check = f"{title} {description} {url}"
    
    # Check for explicit exclusions first
    if any(indicator in text_to_check for indicator in merch_indicators):
        return False
    
    # Check for show indicators
    if any(indicator in text_to_check for indicator in show_indicators):
        return True
    
    # Default to False (don't notify) if unclear
    return False

def check_show_locations(show_url):
    """Check if a show has locations in target cities (LA, SF, Boulder)"""
    target_cities = {
        'los angeles': ['los angeles', 'la, ca', ', ca'],
        'san francisco': ['san francisco', 'sf, ca'],
        'boulder': ['boulder', 'boulder, co']
    }
    
    try:
        response = requests.get(show_url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching show page {show_url}: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for location information in shop_sizes elements
    location_elements = soup.select('div.shop_sizes')
    matching_locations = []
    
    for element in location_elements:
        location_text = element.get('data-size', '')
        if not location_text:
            # Fallback - check text content
            location_text = element.get_text(strip=True)
        
        location_lower = location_text.lower()
        
        # Check for target cities
        for city_name, city_variants in target_cities.items():
            for variant in city_variants:
                if variant in location_lower:
                    # Check availability using data-qty attribute (0 = sold out, 1+ = available)
                    data_qty = element.get('data-qty', '0')
                    is_available = data_qty != '0' and data_qty != ''
                    
                    # Also check text content for sold out indicators as fallback
                    if is_available:
                        is_available = not any(unavailable_term in location_lower for unavailable_term in [
                            'sold out', 'fully redeemed', 'unavailable', 'no longer available'
                        ])
                    
                    matching_locations.append({
                        'raw_text': location_text,
                        'city': city_name,
                        'available': is_available
                    })
                    break  # Don't check other variants once we find a match
    
    return matching_locations

def detect_new_shows(current_shows, existing_shows):
    new_shows = []
    
    for show in current_shows:
        show_id = f"{show['title']}_{show['url']}"
        if show_id not in existing_shows:
            # Only add to new_shows if it's actually a concert/show
            if is_show_or_concert(show):
                # Skip if the title itself indicates it's sold out
                if any(sold_out_term in show['title'].lower() for sold_out_term in [
                    'sold out', 'fully redeemed', 'unavailable'
                ]):
                    show['target_locations'] = []
                else:
                    # Check for target city locations
                    target_locations = check_show_locations(show['url'])
                    show['target_locations'] = target_locations
                    
                    # Only notify if there are shows in target cities that are available
                    available_locations = [loc for loc in target_locations if loc.get('available', True)]
                    if available_locations:
                        show['target_locations'] = available_locations  # Only include available locations
                        new_shows.append(show)
            
            # Still track all items in existing_shows, but mark if it's a show
            existing_shows[show_id] = {
                **show,
                'first_seen': datetime.now().isoformat(),
                'notified': False,
                'is_show': is_show_or_concert(show),
                'target_locations': show.get('target_locations', [])
            }
        else:
            # For existing shows, check if we need to update location data
            existing_show = existing_shows[show_id]
            if (existing_show.get('is_show', False) and 
                'target_locations' not in existing_show and 
                not existing_show.get('notified', False)):
                
                # Check locations for existing shows that haven't been checked yet
                target_locations = check_show_locations(show['url'])
                existing_show['target_locations'] = target_locations
                
                # If we find available target locations, add to new_shows for notification
                available_locations = [loc for loc in target_locations if loc.get('available', True)]
                if available_locations:
                    show['target_locations'] = available_locations  # Only include available locations
                    new_shows.append(show)
    
    return new_shows

def main():
    ensure_data_dir()
    
    existing_shows = load_existing_shows()
    current_shows = scrape_propeller_shows()
    
    if not current_shows:
        print("No shows found or error occurred")
        return
    
    new_shows = detect_new_shows(current_shows, existing_shows)
    
    if new_shows:
        print(f"Found {len(new_shows)} new show(s) in target cities:")
        for show in new_shows:
            print(f"  - {show['title']} ({show['date']})")
            if show.get('target_locations'):
                for location in show['target_locations']:
                    status = "✓ Available" if location['available'] else "✗ Sold Out"
                    print(f"    • {location['raw_text']} - {status}")
        
        # Send notifications
        notify(new_shows)
        
        # Mark shows as notified
        for show in new_shows:
            show_id = f"{show['title']}_{show['url']}"
            if show_id in existing_shows:
                existing_shows[show_id]['notified'] = True
    else:
        print("No new shows found in target cities (Los Angeles, San Francisco, Boulder)")
    
    save_shows(existing_shows)
    print(f"Total shows tracked: {len(existing_shows)}")

if __name__ == "__main__":
    main()