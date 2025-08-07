# sources/scraper.py (Merged v21 - Deployment Compatible with Amount Parsing Fix)

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

# Add project root to path
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

# --- NEW HELPER FUNCTION TO PARSE AMOUNTS ---
def _parse_amount_string(amount_str) -> float:
    """
    Parses a string like '$12.5m' or '€200 million' into a float representing millions.
    """
    if amount_str is None or not isinstance(amount_str, str):
        return 0.0
    
    cleaned_str = str(amount_str).lower().strip()
    if 'undisclosed' in cleaned_str:
        return 0.0
    
    # Remove currency symbols and commas
    cleaned_str = re.sub(r'[$€£,]', '', cleaned_str)
    
    # Extract numeric value
    numeric_match = re.search(r'([\d\.]+)', cleaned_str)
    if not numeric_match:
        return 0.0
        
    value = float(numeric_match.group(1))
    
    # Apply multipliers
    if 'b' in cleaned_str or 'billion' in cleaned_str:
        return value * 1000  # Convert billions to millions
    
    return value  # Default is millions

# --- DEPLOYMENT-COMPATIBLE CRAWLER ---
def _crawl_ctvc_links(pages_to_load=1) -> List[str]:
    """
    Deployment-ready CTVC crawler using requests instead of Selenium
    Works reliably on Replit deployment without browser dependencies
    """
    base_url = "https://www.ctvc.co/tag/newsletter/"
    print(f"🕵️  Crawling CTVC Newsletter (deployment-ready mode)...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(base_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        unique_urls = set()
        
        for link_tag in soup.select('div.flex-1 h3 > a'):
            if 'href' in link_tag.attrs:
                unique_urls.add("https://www.ctvc.co" + link_tag['href'])
        
        print(f"   -> Found {len(unique_urls)} articles from initial page (deployment-ready)")
        print(f"   -> Note: Limited to first page for deployment compatibility")
        
        return list(unique_urls)
    
    except Exception as e:
        print(f"   -> Error crawling CTVC: {e}")
        return []