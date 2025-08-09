# sources/scraper.py (v22 - Merged and Production Ready)

import os
import re
import sys
import time
import json
from typing import List, Dict
import requests
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup

# Path-fixing code for standalone testing
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

import config
from data.data_manager import DataManager

load_dotenv()

# Standardize on the primary API key from config
client = OpenAI(
  api_key=config.OPENAI_API_KEY,
  base_url=config.OPENROUTER_BASE_URL,
  default_headers=config.OPENROUTER_DEFAULT_HEADERS,
)

# --- HELPER & INTERNAL FUNCTIONS ---

def _parse_funding_amount(amount_str: str) -> float:
    """
    Parses a string like '$12.5m' into a float representing millions.
    Adopted from the partner's branch for module portability.
    """
    if amount_str is None or not isinstance(amount_str, str):
        return 0.0
    
    cleaned_str = str(amount_str).lower().strip()
    if 'undisclosed' in cleaned_str:
        return 0.0
    
    cleaned_str = re.sub(r'[$,€£,]', '', cleaned_str)
    numeric_match = re.search(r'([\d\.]+)', cleaned_str)
    if not numeric_match:
        return 0.0
        
    value = float(numeric_match.group(1))
    
    if 'b' in cleaned_str or 'billion' in cleaned_str:
        return value * 1000
    
    return value

def _crawl_ctvc_links(pages_to_load=3) -> List[str]:
    """
    Using the superior multi-page API crawler which is Replit-compatible.
    """
    print("🕵️  Crawling CTVC Newsletter using direct API calls...")
    api_url = "https://www.ctvc.co/ghost/api/content/posts/"
    params = {'key': '9faa8677cc07b3b2c3938b15d3', 'filter': 'tag:newsletter', 'limit': 6, 'fields': 'url', 'include': 'tags'}
    headers = {'User-Agent': 'Mozilla/5.0'}
    all_urls = set()
    for page in range(1, pages_to_load + 1):
        params['page'] = page
        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            posts = data.get('posts', [])
            if not posts: break
            for post in posts: all_urls.add(post['url'])
            print(f"   -> Fetched page {page}, found {len(posts)} articles. Total unique: {len(all_urls)}")
            time.sleep(0.5)
        except Exception as e:
            print(f"   -> 🔴 Error calling CTVC API on page {page}: {e}")
            break
    return list(all_urls)

def _scrape_deals_block(url: str) -> str:
    print(f"  Scraping URL for deals block: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        main_content = soup.find('div', class_=lambda c: c and 'content' in c and 'prose' in c)
        if not main_content: return "Content not found."
        deals_heading = main_content.find(['h2', 'h3'], string=lambda t: t and 'deals of the week' in t.lower())
        if not deals_heading: return "Content not found."
        print("   -> 'Deals of the Week' heading found.")
        content_parts = []
        stop_headings = ["in the news", "exits", "new funds", "pop-up", "opportunities & events", "jobs"]
        for element in deals_heading.find_next_siblings():
            if element.name in ['h2', 'h3']:
                element_text = element.get_text(strip=True).lower()
                if any(stop_word in element_text for stop_word in stop_headings): break
            content_parts.append(element.get_text(separator=' ', strip=True))
        return "\n".join(content_parts)
    except Exception as e:
        print(f"   -> 🔴 Error scraping article: {e.__class__.__name__}")
        return "Content not found."

def _extract_deal_data(deal_string: str) -> Dict:
    """
    Using the advanced AI prompt that infers subsector.
    """
    prompt = f"""From the deal announcement text, extract the startup_name, amount_raised, funding_stage, all investors, AND infer the subsector.

**Valid Subsectors to choose from:**
- Energy, Mobility, Food & Agriculture, Industrials, Carbon, Built Environment, Climate Adaptation

**Instructions:**
- Infer the `subsector` from the company description using the list above.
- If a single investor is mentioned, they are the `lead_investor`.
- If multiple investors are listed, the first is the `lead_investor`.
- If a value is not present, use `null`.

**Example:**
Text: "✈️ AIR, a Haifa, Israel-based eVTOL developer, raised $23m in Series A funding from Entrée Capital."
JSON Output: {{"startup_name": "AIR", "amount_raised": "$23m", "funding_stage": "Series A", "lead_investor": "Entrée Capital", "other_investors": [], "subsector": "Mobility"}}

---
**Text to Process:** "{deal_string}"
**JSON Output:**"""
    try:
        response = client.chat.completions.create(model="meta-llama/llama-3-8b-instruct", response_format={"type": "json_object"}, messages=[{"role": "user", "content": prompt}])
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"   -> 🔴 AI Error: {e}")
        return None

def _clean_data(data: Dict) -> Dict:
    """
    Cleans AI output and uses the local amount parser.
    """
    lead = data.get('lead_investor') or data.get('lead_investors')
    others = data.get('other_investors') or data.get('investors')
    if isinstance(lead, list) and lead:
        if not others: others = []
        others.extend(lead[1:])
        lead = lead[0]

    amount_str = data.get('amount_raised')
    numeric_amount = _parse_funding_amount(amount_str)

    cleaned = {k: v for k, v in {
        'company': data.get('startup_name'),
        'amount': numeric_amount,
        'stage': data.get('stage'),
        'lead_investor': lead,
        'other_investors': others,
        'sector': data.get('subsector')
    }.items() if v is not None and v != 'null' and v != ['null']}
    return cleaned

# --- PRIMARY HOOK FUNCTION ---
def scrape_ctvc_deals(data_manager: DataManager, pages_to_load=3, target_deal_count=15) -> List[Dict]:
    processed_urls = data_manager.load_processed_urls()
    newsletter_urls = _crawl_ctvc_links(pages_to_load=pages_to_load)
    new_deals = []
    for url in newsletter_urls:
        if len(new_deals) >= target_deal_count:
            print(f"🎯 Target of {target_deal_count} new deals reached. Halting scan.")
            break
        if url in processed_urls: continue
        print(f"\n--- Processing article: {url} ---")
        deals_block = _scrape_deals_block(url)
        if deals_block != "Content not found.":
            emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001FA00-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]+')
            deal_chunks = emoji_pattern.split(deals_block)[1:]
            emojis = emoji_pattern.findall(deals_block)
            deal_lines = [emojis[i] + chunk.strip() for i, chunk in enumerate(deal_chunks)]
            print(f"   -> Found {len(deal_lines)} potential deals.")
            for line in deal_lines:
                if len(new_deals) >= target_deal_count: break
                if 'raised' in line or 'funding' in line:
                    time.sleep(1.5)
                    deal_data = _extract_deal_data(line)
                    if deal_data:
                        cleaned_data = _clean_data(deal_data)
                        if cleaned_data.get('company'):
                            cleaned_data['source_url'] = url
                            cleaned_data['source'] = "CTVC"
                            new_deals.append(cleaned_data)
                            print(f"   -> ✅ SUCCESS: Extracted '{cleaned_data['company']}'")
        data_manager.add_processed_url(url)
    return new_deals

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("--- Running scraper.py in Standalone Test Mode ---")
    test_data_manager = DataManager()
    latest_deals = scrape_ctvc_deals(test_data_manager, pages_to_load=1, target_deal_count=15)
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