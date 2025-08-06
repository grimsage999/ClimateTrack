import requests
import trafilatura
import re
from datetime import datetime, timedelta
import time
import random
from typing import List, Dict, Optional
import config
from api_client import EnhancedFundingClient, get_funding_data

class FundingScraper:
    """Scraper for climate tech funding data from public sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Initialize enhanced API client from APITest2 integration
        self.enhanced_client = EnhancedFundingClient()
        
    def scrape_techcrunch(self) -> List[Dict]:
        """Scrape funding news from TechCrunch"""
        results = []
        
        try:
            # Search for climate tech funding articles
            # FOCUSED SEARCH: Target specific subsectors only
            search_terms = [
                "grid modernization funding",
                "smart grid investment", 
                "transmission funding",
                "carbon capture funding",
                "direct air capture investment",
                "carbon storage funding"
            ]
            
            for term in search_terms:
                # TechCrunch search URL
                search_url = f"https://techcrunch.com/?s={term.replace(' ', '+')}"
                
                try:
                    response = self.session.get(search_url, timeout=10)
                    if response.status_code == 200:
                        # Extract text content
                        text_content = trafilatura.extract(response.text)
                        if text_content:
                            # Parse for funding information
                            funding_events = self._extract_funding_info(text_content, 'TechCrunch')
                            results.extend(funding_events)
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    print(f"Error scraping TechCrunch for term '{term}': {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error in TechCrunch scraping: {str(e)}")
            
        return results
    
    def scrape_venturebeat(self) -> List[Dict]:
        """Scrape funding news from VentureBeat"""
        results = []
        
        try:
            # VentureBeat funding section
            url = "https://venturebeat.com/category/funding/"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                text_content = trafilatura.extract(response.text)
                if text_content:
                    funding_events = self._extract_funding_info(text_content, 'VentureBeat')
                    results.extend(funding_events)
                    
        except Exception as e:
            print(f"Error scraping VentureBeat: {str(e)}")
            
        return results
    
    def scrape_crunchbase_news(self) -> List[Dict]:
        """Scrape funding news from Crunchbase News"""
        results = []
        
        try:
            # Crunchbase News funding section
            url = "https://news.crunchbase.com/venture/"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                text_content = trafilatura.extract(response.text)
                if text_content:
                    funding_events = self._extract_funding_info(text_content, 'Crunchbase News')
                    results.extend(funding_events)
                    
        except Exception as e:
            print(f"Error scraping Crunchbase News: {str(e)}")
            
        return results
    
    def scrape_climate_tech_news(self) -> List[Dict]:
        """Scrape from climate tech specific news sources"""
        results = []
        
        climate_sources = [
            "https://www.greentechmedia.com/",
            "https://www.cleantech.com/"
        ]
        
        for url in climate_sources:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    text_content = trafilatura.extract(response.text)
                    if text_content:
                        funding_events = self._extract_funding_info(text_content, url)
                        results.extend(funding_events)
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                continue
                
        return results
    
    def _extract_funding_info(self, text_content: str, source: str) -> List[Dict]:
        """Extract funding information from text content"""
        funding_events = []
        
        try:
            # Split text into sentences/paragraphs
            paragraphs = text_content.split('\n')
            
            for paragraph in paragraphs:
                # Look for funding indicators
                funding_keywords = [
                    'raised', 'funding', 'investment', 'round', 'series',
                    'million', 'billion', 'venture capital', 'led by'
                ]
                
                if any(keyword.lower() in paragraph.lower() for keyword in funding_keywords):
                    # Extract company name (usually at the beginning)
                    company_match = re.search(r'^([A-Za-z\s&]+?)\s+(?:raised|secured|announced)', paragraph, re.IGNORECASE)
                    company = company_match.group(1).strip() if company_match else None
                    
                    # Extract funding amount
                    amount_match = re.search(r'\$(\d+(?:\.\d+)?)\s*(million|billion|M|B)', paragraph, re.IGNORECASE)
                    amount = None
                    if amount_match:
                        value = float(amount_match.group(1))
                        unit = amount_match.group(2).lower()
                        if unit in ['million', 'm']:
                            amount = value * 1000000
                        elif unit in ['billion', 'b']:
                            amount = value * 1000000000
                    
                    # Extract funding stage
                    stage_match = re.search(r'(pre-seed|seed|series [a-z]|growth|venture)', paragraph, re.IGNORECASE)
                    stage = stage_match.group(1) if stage_match else None
                    
                    # Extract investor
                    investor_match = re.search(r'led by ([^,\n]+)', paragraph, re.IGNORECASE)
                    investor = investor_match.group(1).strip() if investor_match else None
                    
                    # Only add if we have meaningful data
                    if company and (amount or stage or investor):
                        funding_events.append({
                            'company': company,
                            'amount': amount,
                            'stage': stage,
                            'lead_investor': investor,
                            'description': paragraph[:200] + '...' if len(paragraph) > 200 else paragraph,
                            'source': source,
                            'scraped_date': datetime.now().isoformat(),
                            'raw_text': paragraph
                        })
        
        except Exception as e:
            print(f"Error extracting funding info: {str(e)}")
        
        return funding_events
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scrape all configured sources"""
        all_results = []
        
        print("Scraping TechCrunch...")
        all_results.extend(self.scrape_techcrunch())
        
        print("Scraping VentureBeat...")
        all_results.extend(self.scrape_venturebeat())
        
        print("Scraping Crunchbase News...")
        all_results.extend(self.scrape_crunchbase_news())
        
        print("Scraping Climate Tech sources...")
        all_results.extend(self.scrape_climate_tech_news())
        
        # Remove duplicates based on company name
        seen_companies = set()
        unique_results = []
        
        for result in all_results:
            company_key = result.get('company', '').lower().strip()
            if company_key and company_key not in seen_companies:
                seen_companies.add(company_key)
                unique_results.append(result)
        
        print(f"Found {len(unique_results)} unique funding events")
        return unique_results
