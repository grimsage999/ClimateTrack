# sources/scraper.py

import os
import re
import time
import json
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import config
from data.data_manager import DataManager # <-- NEW IMPORT

load_dotenv()

client = OpenAI(
  api_key=config.OPENAI_API_KEY,
  base_url=config.OPENROUTER_BASE_URL,
  default_headers=config.OPENROUTER_DEFAULT_HEADERS,
)

# ... (the internal _crawl, _scrape, _extract, _clean functions are unchanged) ...

def _crawl_ctvc_links(pages_to_load=1) -> List[str]:
    base_url = "https://www.ctvc.co/tag/newsletter/"
    print(f"🕵️  Crawling CTVC Newsletter with Selenium...")
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = None
    
    try:
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        driver.set_page_load_timeout(45)
        driver.get(base_url)
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.flex-1 h3 > a')))
        time.sleep(2)

        for i in range(pages_to_load):
            try:
                load_more_button = driver.find_element(By.CSS_SELECTOR, "a.load-more")
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", load_more_button)
                print(f"   -> Clicked 'Load More' ({i+1}/{pages_to_load})...")
                time.sleep(3)
            except Exception:
                print("   -> 'Load More' button not found.")
                break
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        unique_urls = set()
        for link_tag in soup.select('div.flex-1 h3 > a'):
            if 'href' in link_tag.attrs:
                unique_urls.add("https://www.ctvc.co" + link_tag['href'])
        
        print(f"   -> Found {len(unique_urls)} unique articles after loading more.\n")
        return list(unique_urls)
    
    except Exception as e:
        print(f"   -> 🔴 Error crawling CTVC with Selenium: {e.__class__.__name__}")
        return []
    finally:
        if driver:
            driver.quit()

def _scrape_deals_block(url: str) -> str:
    import requests
    print(f"  Scraping URL for deals block: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        
        main_content = soup.find('div', class_=lambda c: c and 'content' in c and 'prose' in c)
        if not main_content:
            return "Content not found."

        deals_heading = main_content.find(['h2', 'h3'], string=lambda t: t and 'deals of the week' in t.lower())
        if not deals_heading:
            return "Content not found."
            
        print("   -> 'Deals of the Week' heading found.")
        content_parts = []
        stop_headings = ["in the news", "exits", "new funds", "pop-up", "opportunities & events", "jobs"]
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
    lead = data.get('lead_investor') or data.get('lead_investors')
    others = data.get('other_investors') or data.get('investors')
    
    if isinstance(lead, list) and lead:
        if not others: others = []
        others.extend(lead[1:])
        lead = lead[0]

    cleaned = {k: v for k, v in {
        'company': data.get('startup_name'), 'amount': data.get('amount_raised'),
        'stage': data.get('funding_stage'), 'lead_investor': lead, 'other_investors': others
    }.items() if v is not None and v != 'null' and v != ['null']}
    
    return cleaned

# --- PRIMARY HOOK FUNCTION FOR main.py ---

def scrape_ctvc_deals(data_manager: DataManager, pages_to_load=1) -> List[Dict]:
    """
    Main function for the UI to call.
    Orchestrates scraping and extracting CTVC deals.
    """
    # --- CHANGE: Use the DataManager to load URLs ---
    processed_urls = data_manager.load_processed_urls()
    
    newsletter_urls = _crawl_ctvc_links(pages_to_load=pages_to_load)
    
    new_deals = []
    
    for url in newsletter_urls:
        if url in processed_urls:
            continue
            
        print(f"\n--- Processing article: {url} ---")
        deals_block = _scrape_deals_block(url)
        
        if deals_block != "Content not found.":
            # ... (emoji splitting logic is unchanged) ...
            emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001FA00-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]+')
            deal_chunks = emoji_pattern.split(deals_block)[1:]
            emojis = emoji_pattern.findall(deals_block)
            deal_lines = [emojis[i] + chunk.strip() for i, chunk in enumerate(deal_chunks)]
            
            print(f"   -> Found {len(deal_lines)} potential deals.")
            for line in deal_lines:
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
        
        # --- CHANGE: Use the DataManager to save the URL ---
        data_manager.add_processed_url(url)
            
    return new_deals