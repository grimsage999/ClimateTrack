"""
Enhanced API Client for Climate Tech Funding Data
Integrated from APITest2 repository: https://github.com/PeteM573/APITest2
Focuses on Grid Modernization and Carbon Capture funding events
"""

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import json
import time
from typing import Dict, List, Optional
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import config

class EnhancedFundingClient:
    """
    Enhanced funding data client integrated from APITest2
    Attribution: Based on code from https://github.com/PeteM573/APITest2
    """
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
        self.processed_urls = set()
        
        # Focus on target sectors for VC use case
        self.target_sectors = config.TARGET_SUBSECTORS
        self.target_stages = config.TARGET_FUNDING_STAGES
        
    def setup_chrome_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver for JavaScript-rendered pages"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        try:
            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )
            return driver
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            return None
    
    def crawl_techcrunch_articles(self, page: int = 1, max_articles: int = 20) -> List[str]:
        """
        Crawl TechCrunch venture category for article links
        Enhanced with Selenium for JavaScript rendering
        """
        category_url = f"https://techcrunch.com/category/venture/page/{page}/"
        print(f"Crawling TechCrunch page {page}: {category_url}")
        
        driver = self.setup_chrome_driver()
        if not driver:
            return []
            
        try:
            driver.get(category_url)
            time.sleep(3)  # Wait for JavaScript to load
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            links = []
            for link_tag in soup.find_all('a', class_='loop-card__title-link'):
                if link_tag and 'href' in link_tag.attrs:
                    clean_link = link_tag['href'].split('?')[0]
                    if clean_link not in self.processed_urls:
                        links.append(clean_link)
                        if len(links) >= max_articles:
                            break
            
            print(f"Found {len(links)} new article links")
            return links
            
        except Exception as e:
            print(f"Error crawling TechCrunch: {e}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def scrape_article_content(self, url: str) -> Optional[Dict]:
        """
        Scrape article content from URL
        Based on APITest2 scraper logic
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().replace(' | TechCrunch', '').strip() if title_tag else "Title not found"
            
            # Extract content
            content_div = soup.find('div', class_='entry-content')
            content = ""
            if content_div:
                paragraphs = content_div.find_all('p')
                content = '\n'.join([p.get_text() for p in paragraphs])
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'soup': soup
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def classify_article_type(self, title: str, content: str) -> str:
        """
        AI-powered article classification
        Enhanced from APITest2 with focus on funding rounds
        """
        prompt = f"""You are a funding news classifier. Classify this article into one category.

Categories:
- STARTUP_FUNDING_ROUND: A specific startup raised venture capital
- FUND_ANNOUNCEMENT: VC firm announces new fund  
- GENERAL_NEWS: Other news (analysis, IPOs, etc.)

Focus on Grid Modernization and Carbon Capture sectors.

Title: "{title}"
Content: "{content[:500]}"

Respond with only the category name:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=50
            )
            
            classification = response.choices[0].message.content.strip()
            
            valid_categories = ["STARTUP_FUNDING_ROUND", "FUND_ANNOUNCEMENT", "GENERAL_NEWS"]
            if not any(cat in classification for cat in valid_categories):
                classification = "GENERAL_NEWS"
                
            return classification
            
        except Exception as e:
            print(f"Classification error: {e}")
            return "GENERAL_NEWS"
    
    def extract_funding_data(self, content: str) -> Optional[Dict]:
        """
        Extract structured funding data using AI
        Focused on VC use case: startup_name, subsector, funding_stage, amount_raised, lead_investor
        """
        prompt = f"""Extract funding information from this article. Focus ONLY on:
- Grid Modernization (grid infrastructure, transmission, smart grid, energy storage integration)  
- Carbon Capture (direct air capture, CCS, carbon removal, carbon utilization)

Extract these 5 fields with confidence scores:
1. startup_name
2. subsector: "Grid Modernization" or "Carbon Capture" (exact match required)
3. funding_stage: "Seed" or "Series A" (exact match required)
4. amount_raised: USD amount in millions
5. lead_investor: Primary investor leading the round

IGNORE if not Grid Modernization or Carbon Capture.
IGNORE if not Seed or Series A.

Article content:
{content}

Return JSON format:
{{
    "startup_name": "string or null",
    "subsector": "Grid Modernization" or "Carbon Capture" or null, 
    "funding_stage": "Seed" or "Series A" or null,
    "amount_raised": number in millions or null,
    "lead_investor": "string or null",
    "confidence_scores": {{
        "startup_name": number (0-1),
        "subsector": number (0-1),
        "funding_stage": number (0-1), 
        "amount_raised": number (0-1),
        "lead_investor": number (0-1)
    }},
    "is_target_deal": boolean
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            
            # Validate target deal criteria
            if (extracted_data.get('subsector') in self.target_sectors and 
                extracted_data.get('funding_stage') in self.target_stages):
                extracted_data['is_target_deal'] = True
            else:
                extracted_data['is_target_deal'] = False
                
            return extracted_data
            
        except Exception as e:
            print(f"Data extraction error: {e}")
            return None
    
    def validate_climate_tech_startup(self, article_soup) -> bool:
        """
        Validate if startup is actually in target climate tech sectors
        Enhanced validation from APITest2
        """
        try:
            # Find startup website link from article
            first_p = article_soup.find('div', class_='entry-content')
            if not first_p:
                return False
                
            first_p = first_p.find('p')
            startup_link_tag = first_p.find('a') if first_p else None
            
            if not startup_link_tag or 'href' not in startup_link_tag.attrs:
                return False
                
            startup_url = startup_link_tag['href']
            
            # Scrape startup homepage
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(startup_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            startup_soup = BeautifulSoup(response.content, 'lxml')
            startup_text = startup_soup.body.get_text(separator=' ', strip=True)[:1500]
            
            # AI validation for target sectors
            prompt = f"""Is this company in Grid Modernization or Carbon Capture?

Grid Modernization: grid infrastructure, transmission, distribution, smart grid, energy storage integration, grid analytics, demand response
Carbon Capture: direct air capture, CCS, carbon utilization, carbon removal technologies

Answer YES or NO only.

Company website text: "{startup_text}"

Answer:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=5
            )
            
            decision = response.choices[0].message.content.strip().upper()
            return "YES" in decision
            
        except Exception as e:
            print(f"Startup validation error: {e}")
            return False
    
    def get_funding_data(self, sector: str = None, stage: str = None, max_deals: int = 10) -> List[Dict]:
        """
        Main interface function - get funding data for specific criteria
        Enhanced from APITest2 for VC use case
        """
        print(f"Searching for {max_deals} deals in {sector or 'all target sectors'} at {stage or 'all target stages'}")
        
        funding_deals = []
        current_page = 1
        max_pages = 5
        
        while len(funding_deals) < max_deals and current_page <= max_pages:
            # Get article URLs
            article_urls = self.crawl_techcrunch_articles(page=current_page, max_articles=20)
            
            if not article_urls:
                break
                
            for url in article_urls:
                if url in self.processed_urls:
                    continue
                    
                self.processed_urls.add(url)
                
                # Scrape article
                article_data = self.scrape_article_content(url)
                if not article_data:
                    continue
                    
                # Classify article type
                article_type = self.classify_article_type(
                    article_data['title'], 
                    article_data['content']
                )
                
                if "STARTUP_FUNDING_ROUND" not in article_type:
                    continue
                    
                # Extract funding data
                funding_data = self.extract_funding_data(article_data['content'])
                if not funding_data or not funding_data.get('is_target_deal'):
                    continue
                    
                # Final validation
                if self.validate_climate_tech_startup(article_data['soup']):
                    funding_data['source_url'] = url
                    funding_data['published_date'] = time.strftime("%Y-%m-%d")
                    funding_data['source'] = 'TechCrunch Enhanced'
                    
                    # Apply filters if specified
                    if sector and funding_data.get('subsector') != sector:
                        continue
                    if stage and funding_data.get('funding_stage') != stage:
                        continue
                        
                    funding_deals.append(funding_data)
                    print(f"✅ Found target deal: {funding_data.get('startup_name')} - {funding_data.get('subsector')}")
                    
                    if len(funding_deals) >= max_deals:
                        break
                
                # Rate limiting
                time.sleep(random.uniform(2, 4))
                
            current_page += 1
        
        print(f"Retrieved {len(funding_deals)} qualifying deals")
        return funding_deals

# Convenience functions for integration
def get_funding_data(sector: str = None, stage: str = None, max_deals: int = 10) -> List[Dict]:
    """
    Main interface function for getting funding data
    Usage: data = get_funding_data(sector="Grid Modernization", stage="Seed")
    """
    client = EnhancedFundingClient()
    return client.get_funding_data(sector=sector, stage=stage, max_deals=max_deals)

def get_grid_modernization_deals(stage: str = None, max_deals: int = 10) -> List[Dict]:
    """Get Grid Modernization deals specifically"""
    return get_funding_data(sector="Grid Modernization", stage=stage, max_deals=max_deals)

def get_carbon_capture_deals(stage: str = None, max_deals: int = 10) -> List[Dict]:
    """Get Carbon Capture deals specifically"""  
    return get_funding_data(sector="Carbon Capture", stage=stage, max_deals=max_deals)

if __name__ == "__main__":
    # Test the enhanced client
    print("Testing Enhanced Funding Client...")
    deals = get_funding_data(max_deals=3)
    for deal in deals:
        print(f"- {deal.get('startup_name')}: ${deal.get('amount_raised')}M {deal.get('funding_stage')} led by {deal.get('lead_investor')}")