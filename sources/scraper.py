# sources/scraper.py (Merged - AI-Powered Subsector Classification with Deployment Compatibility)

import os
import re
import sys
import time
import json
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI

# Add project root to path and import utilities
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

import config
from data.data_manager import DataManager
from utils import parse_funding_amount

load_dotenv()

# Use OpenRouter with OPENAI2 for deployment compatibility
client = OpenAI(
    api_key=config.OPENAI2_API_KEY,
    base_url=config.OPENROUTER_BASE_URL,
    default_headers=config.OPENROUTER_DEFAULT_HEADERS,
)

def _crawl_ctvc_links(pages_to_load=3) -> List[str]:
    """
    Deployment-ready CTVC crawler using both API and direct scraping methods
    Falls back gracefully for maximum reliability
    """
    print("🕵️  Crawling CTVC Newsletter using hybrid approach...")
    
    # Method 1: Try API first (more reliable)
    try:
        api_url = "https://www.ctvc.co/ghost/api/content/posts/"
        params = {
            'key': '9faa8677cc07b3b2c3938b15d3', 
            'filter': 'tag:newsletter', 
            'limit': 6, 
            'fields': 'url', 
            'include': 'tags'
        }
        headers = {'User-Agent': 'Mozilla/5.0'}
        all_urls = set()
        
        for page in range(1, min(pages_to_load + 1, 4)):  # Limit API calls for deployment
            params['page'] = page
            response = requests.get(api_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            posts = data.get('posts', [])
            if not posts:
                break
            for post in posts:
                all_urls.add(post['url'])
            print(f"   -> API: Fetched page {page}, found {len(posts)} articles. Total unique: {len(all_urls)}")
            time.sleep(0.5)
        
        if all_urls:
            print(f"   -> API method successful: {len(all_urls)} URLs found")
            return list(all_urls)
    
    except Exception as e:
        print(f"   -> API method failed: {e}")
    
    # Method 2: Fallback to direct scraping
    try:
        base_url = "https://www.ctvc.co/tag/newsletter/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(base_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        unique_urls = set()
        
        for link_tag in soup.select('div.flex-1 h3 > a'):
            if 'href' in link_tag.attrs:
                unique_urls.add("https://www.ctvc.co" + link_tag['href'])
        
        print(f"   -> Direct scraping fallback: Found {len(unique_urls)} articles")
        return list(unique_urls)
    
    except Exception as e:
        print(f"   -> Both methods failed: {e}")
        return []

def _scrape_deals_block(url: str) -> str:
    """
    Scrapes the 'Deals of the Week' section from a CTVC newsletter
    """
    print(f"  Scraping URL for deals block: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find main content area
        main_content = soup.find('div', class_=lambda c: c and 'content' in c and 'prose' in c)
        if not main_content:
            return "Content not found."
        
        # Look for deals heading
        deals_heading = main_content.find(['h2', 'h3'], 
                                        string=lambda t: t and 'deals of the week' in t.lower())
        if not deals_heading:
            return "Content not found."
        
        print("   -> 'Deals of the Week' heading found.")
        content_parts = []
        stop_headings = ["in the news", "exits", "new funds", "pop-up", 
                        "opportunities & events", "jobs"]
        
        # Extract content until next major section
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

def _extract_deal_data(deal_string: str) -> Dict:
    """
    AI-powered extraction with subsector classification
    """
    prompt = f"""From the deal announcement text, extract the startup_name, amount_raised, funding_stage, all investors, AND infer the subsector.

**Valid Subsectors to choose from:**
- Energy (generation, storage, grid, batteries, fusion)
- Mobility (EVs, aviation, micromobility, charging)
- Food & Agriculture (agtech, alternative proteins, sustainable farming)
- Industrials (green steel, cement, chemicals, manufacturing)
- Carbon (carbon capture, removal, utilization, markets)
- Built Environment (HVAC, green buildings, sustainable materials)
- Climate Adaptation (risk modeling, water, resilience)

**Instructions:**
- The startup name is the first bolded name.
- The amount is the bolded dollar/euro value.
- If a single investor is mentioned, they are the lead_investor.
- If multiple investors are listed, the first is the lead_investor.
- **Infer the subsector from the company description using the list above.**
- If a value is not present, use null.

**Example:**
Text: "✈️ AIR, a Haifa, Israel-based eVTOL developer, raised $23m in Series A funding from Entrée Capital."
JSON Output: {{"startup_name": "AIR", "amount_raised": "$23m", "funding_stage": "Series A", "lead_investor": "Entrée Capital", "other_investors": [], "subsector": "Mobility"}}

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
    Cleans AI output and uses utility parser for amount conversion
    """
    if not data:
        return {}
    
    # Handle lead investor
    lead = data.get('lead_investor') or data.get('lead_investors')
    others = data.get('other_investors') or data.get('investors')
    
    if isinstance(lead, list) and lead:
        if not others:
            others = []
        others.extend(lead[1:])
        lead = lead[0]
    
    # Parse amount using utility function
    amount_str = data.get('amount_raised')
    numeric_amount = parse_funding_amount(amount_str)
    
    # Clean and structure data
    cleaned = {k: v for k, v in {
        'company': data.get('startup_name'),
        'amount': numeric_amount,
        'stage': data.get('funding_stage') or data.get('stage'),
        'lead_investor': lead,
        'other_investors': others,
        'sector': data.get('subsector')
    }.items() if v is not None and v != 'null' and v != ['null']}
    
    return cleaned

def scrape_ctvc_deals(data_manager: DataManager, pages_to_load=3, target_deal_count=15) -> List[Dict]:
    """
    Main function to scrape CTVC deals with AI-powered extraction
    """
    processed_urls = data_manager.load_processed_urls()
    newsletter_urls = _crawl_ctvc_links(pages_to_load=pages_to_load)
    new_deals = []
    
    for url in newsletter_urls:
        if len(new_deals) >= target_deal_count:
            print(f"🎯 Target of {target_deal_count} new deals reached. Halting scan.")
            break
        
        if url in processed_urls:
            continue
            
        print(f"\n--- Processing article: {url} ---")
        deals_block = _scrape_deals_block(url)
        
        if deals_block != "Content not found.":
            # Split by emoji patterns to identify individual deals
            emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001FA00-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]+')
            deal_chunks = emoji_pattern.split(deals_block)[1:]
            emojis = emoji_pattern.findall(deals_block)
            deal_lines = [emojis[i] + chunk.strip() for i, chunk in enumerate(deal_chunks) if i < len(emojis)]
            
            print(f"   -> Found {len(deal_lines)} potential deals.")
            
            for line in deal_lines:
                if len(new_deals) >= target_deal_count:
                    break
                    
                if 'raised' in line or 'funding' in line:
                    time.sleep(1.5)  # Rate limiting for AI calls
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

# Test block for standalone execution
if __name__ == "__main__":
    print("--- Running scraper.py in Standalone Test Mode ---")
    
    # Create DataManager instance for testing
    test_data_manager = DataManager()
    
    # Test with limited scope
    latest_deals = scrape_ctvc_deals(test_data_manager, pages_to_load=1, target_deal_count=5)
    
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
