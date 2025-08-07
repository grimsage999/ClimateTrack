# sources/scraper.py (v22 - Fixed and Cleaned)

import os
import re
import sys
import time
import json
from typing import List, Dict, Optional
import requests
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

import config
from data.data_manager import DataManager

load_dotenv()

# Use OpenRouter with OPENAI2 for deployment compatibility
client = OpenAI(
    api_key=config.OPENAI2_API_KEY,
    base_url=config.OPENROUTER_BASE_URL,
    default_headers=config.OPENROUTER_DEFAULT_HEADERS,
)

def _parse_amount_string(amount_str) -> float:
    """
    Parses a string like '$12.5m' or '€200 million' into a float representing millions.
    """
    if amount_str is None or not isinstance(amount_str, str):
        return 0.0
    
    cleaned_str = str(amount_str).lower().strip()
    if 'undisclosed' in cleaned_str:
        return 0.0
    
    # Remove currency symbols and other noise
    cleaned_str = re.sub(r'[$\€,]', '', cleaned_str)
    
    # Find the numeric part of the string
    numeric_match = re.search(r'([\d\.]+)', cleaned_str)
    if not numeric_match:
        return 0.0
        
    value = float(numeric_match.group(1))
    
    # Apply multipliers
    if 'b' in cleaned_str or 'billion' in cleaned_str:
        return value * 1000  # Convert billions to millions
    # 'm' or 'million' is the default, so no multiplier needed
    
    return value

def _crawl_ctvc_links(pages_to_load=3) -> List[str]:
    """
    Crawl CTVC Newsletter using Ghost API for reliable deployment
    """
    print("🕵️  Crawling CTVC Newsletter using direct API calls...")
    api_url = "https://www.ctvc.co/ghost/api/content/posts/"
    params = {
        'key': '9faa8677cc07b3b2c3938b15d3',
        'filter': 'tag:newsletter',
        'limit': 6,
        'fields': 'url',
        'include': 'tags'
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    all_urls = set()
    
    for page in range(1, pages_to_load + 1):
        params['page'] = page
        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            posts = data.get('posts', [])
            
            if not posts:
                break
                
            for post in posts:
                all_urls.add(post['url'])
            
            print(f"   -> Fetched page {page}, found {len(posts)} articles. Total unique: {len(all_urls)}")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   -> 🔴 Error calling CTVC API on page {page}: {e}")
            break
    
    return list(all_urls)

def _scrape_deals_block(url: str) -> str:
    """
    Scrapes the 'Deals of the Week' section from a CTVC newsletter URL
    """
    print(f"  Scraping URL for deals block: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find the main content area
        main_content = soup.find('div', class_=lambda c: c and 'content' in c and 'prose' in c)
        if not main_content:
            return "Content not found."
        
        # Look for "Deals of the Week" heading
        deals_heading = main_content.find(['h2', 'h3'], string=lambda t: t and 'deals of the week' in t.lower())
        if not deals_heading:
            return "Content not found."
            
        print("   -> 'Deals of the Week' heading found.")
        
        content_parts = []
        stop_headings = ["in the news", "exits", "new funds", "pop-up", "opportunities & events", "jobs"]
        
        # Collect content until we hit a stop heading
        for element in deals_heading.find_next_siblings():
            if element.name in ['h2', 'h3']:
                element_text = element.get_text(strip=True).lower()
                if any(stop_word in element_text for stop_word in stop_headings):
                    break
            content_parts.append(element.get_text(separator=' ', strip=True))
        
        return "\n".join(content_parts)
        
    except Exception as e:
        print(f"   -> 🔴 Error scraping article: {e.__class__.__name__}")
        return "Content not found."

def _extract_deal_data(deal_string: str) -> Optional[Dict]:
    """
    Uses AI to extract structured deal data from text
    """
    prompt = f"""From the deal announcement text, extract: startup_name, amount_raised, funding_stage, and all investors.

**Instructions:**
- The startup name is the first bolded name.
- The amount is the bolded dollar/euro value.
- If a single investor is mentioned after "from", they are the `lead_investor`.
- If multiple investors are listed, the first is the `lead_investor` and the rest are `other_investors`.
- If a value is not present, use `null`.

**Example:**
Text: "✈️ AIR, a Haifa, Israel-based eVTOL developer, raised $23m in Series A funding from Entrée Capital."
JSON Output: {{"startup_name": "AIR", "amount_raised": "$23m", "funding_stage": "Series A", "lead_investor": "Entrée Capital", "other_investors": []}}

---
**Text to Process:** "{deal_string}"
**JSON Output:**"""

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"   -> 🔴 AI Error: {e}")
        return None

def _clean_data(data: Dict) -> Dict:
    """
    Cleans and normalizes the raw data from the AI.
    Includes amount parsing to convert to numeric values.
    """
    # Parse the amount string to numeric value
    amount_str = data.get('amount_raised')
    numeric_amount = _parse_amount_string(amount_str)

    # Handle lead investor(s)
    lead = data.get('lead_investor') or data.get('lead_investors')
    others = data.get('other_investors') or data.get('investors')
    
    # If lead is a list, take first as lead and rest as others
    if isinstance(lead, list) and lead:
        if not others:
            others = []
        others.extend(lead[1:])
        lead = lead[0]

    # Build cleaned data dict
    cleaned = {}
    
    # Map and clean each field
    field_mapping = {
        'company': data.get('startup_name'),
        'amount': numeric_amount,
        'stage': data.get('funding_stage'),
        'lead_investor': lead,
        'other_investors': others
    }
    
    for key, value in field_mapping.items():
        if value is not None and value != 'null' and value != ['null']:
            cleaned[key] = value
    
    return cleaned

def scrape_ctvc_deals(data_manager: DataManager, pages_to_load=3, target_deal_count=15):
    """
    Main function to scrape deals from CTVC newsletters.
    Yields cleaned deal data as it's found.
    """
    processed_urls = data_manager.load_processed_urls()
    newsletter_urls = _crawl_ctvc_links(pages_to_load=pages_to_load)
    deals_found_count = 0
    
    for url in newsletter_urls:
        if deals_found_count >= target_deal_count:
            print(f"🎯 Target of {target_deal_count} new deals reached. Halting scan.")
            break
            
        if url in processed_urls:
            continue
            
        print(f"\n--- Processing article: {url} ---")
        deals_block = _scrape_deals_block(url)
        
        if deals_block != "Content not found.":
            # Split deals by emoji markers
            emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001FA00-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]+')
            deal_chunks = emoji_pattern.split(deals_block)[1:]  # Skip first empty chunk
            emojis = emoji_pattern.findall(deals_block)
            
            # Reconstruct deal lines with their emojis
            deal_lines = [emojis[i] + chunk.strip() for i, chunk in enumerate(deal_chunks)]
            print(f"   -> Found {len(deal_lines)} potential deals.")
            
            for line in deal_lines:
                if deals_found_count >= target_deal_count:
                    break
                    
                # Only process lines that look like funding announcements
                if 'raised' in line or 'funding' in line:
                    time.sleep(1.5)  # Rate limiting for API
                    deal_data = _extract_deal_data(line)
                    
                    if deal_data:
                        cleaned_data = _clean_data(deal_data)
                        
                        if cleaned_data.get('company'):
                            cleaned_data['source_url'] = url
                            cleaned_data['source'] = "CTVC"
                            yield cleaned_data
                            deals_found_count += 1
                            print(f"   -> ✅ SUCCESS: Extracted '{cleaned_data['company']}'")
        
        # Mark URL as processed
        data_manager.add_processed_url(url)

# Test block for standalone execution
if __name__ == "__main__":
    print("--- Running scraper.py in Standalone Test Mode ---")
    test_data_manager = DataManager()
    latest_deals = list(scrape_ctvc_deals(test_data_manager, pages_to_load=1, target_deal_count=5))
    
    if latest_deals:
        print(f"\n--- SCRAPER TEST COMPLETE ---")
        print(f"Successfully extracted {len(latest_deals)} new deals.")
        test_data_manager.save_funding_data(latest_deals)
        print(f"Saved test results to '{test_data_manager.funding_file}'")
        
        import pprint
        print("\nSample of extracted data:")
        pprint.pprint(latest_deals[:3])
    else:
        print("\n--- SCRAPER TEST COMPLETE ---")
        print("No new deals were found during the test.")