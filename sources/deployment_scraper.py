"""
Deployment-ready scraper for climate tech funding data
Uses requests + BeautifulSoup instead of Selenium for Replit compatibility
"""

import requests
import time
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from openai import OpenAI
import config
import trafilatura

class DeploymentReadyScraper:
    """
    Scraper optimized for deployment on Replit
    No browser dependencies - uses requests and BeautifulSoup
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        # OpenRouter client for AI analysis
        self.client = OpenAI(
            api_key=config.OPENAI2_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            default_headers=config.OPENROUTER_DEFAULT_HEADERS,
        )
    
    def get_funding_articles(self, sources: List[str] = None) -> List[Dict]:
        """
        Get funding articles from multiple sources
        Deployment-ready approach without JavaScript rendering
        """
        if not sources:
            sources = [
                "https://techcrunch.com/category/startups/",
                "https://venturebeat.com/",
                "https://news.crunchbase.com/"
            ]
        
        articles = []
        for source in sources:
            try:
                print(f"Scraping {source}...")
                source_articles = self._scrape_source(source)
                articles.extend(source_articles)
                time.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"Error scraping {source}: {e}")
                continue
        
        return articles
    
    def _scrape_source(self, url: str) -> List[Dict]:
        """Scrape articles from a single source"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Use trafilatura for better content extraction
            content = trafilatura.extract(response.text)
            if not content:
                return []
            
            # Basic article parsing - can be enhanced per source
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Generic article extraction (customize per source)
            for article in soup.find_all(['article', 'div'], class_=lambda x: x and any(
                term in x.lower() for term in ['post', 'article', 'story', 'news']
            ))[:10]:  # Limit to 10 articles per source
                
                title_elem = article.find(['h1', 'h2', 'h3', 'a'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    # Check if potentially climate/funding related
                    if self._is_potentially_relevant(title):
                        articles.append({
                            'title': title,
                            'url': self._extract_url(article, url),
                            'source': url,
                            'content': content[:500]  # First 500 chars
                        })
            
            return articles
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []
    
    def _is_potentially_relevant(self, title: str) -> bool:
        """Quick relevance check for climate/funding keywords"""
        climate_keywords = ['climate', 'energy', 'carbon', 'grid', 'funding', 'raises', 'series', 'seed']
        title_lower = title.lower()
        return any(keyword in title_lower for keyword in climate_keywords)
    
    def _extract_url(self, article_elem, base_url: str) -> str:
        """Extract article URL"""
        link = article_elem.find('a')
        if link and link.get('href'):
            href = link['href']
            if href.startswith('http'):
                return href
            else:
                return f"{base_url.rstrip('/')}/{href.lstrip('/')}"
        return base_url
    
    def analyze_for_funding_deals(self, articles: List[Dict]) -> List[Dict]:
        """
        Use AI to analyze articles for funding deals
        Deployment-ready with proper error handling
        """
        deals = []
        
        for article in articles:
            try:
                # AI analysis using OpenRouter
                analysis = self._ai_analyze_article(article)
                if analysis and analysis.get('is_funding_deal'):
                    deals.append({
                        **article,
                        'analysis': analysis
                    })
                    
                time.sleep(1)  # Rate limiting for API calls
                
            except Exception as e:
                print(f"Error analyzing article: {e}")
                continue
        
        return deals
    
    def _ai_analyze_article(self, article: Dict) -> Optional[Dict]:
        """AI analysis of article for funding information"""
        try:
            prompt = f"""
            Analyze this article for climate tech funding information:
            
            Title: {article['title']}
            Content: {article['content']}
            
            Determine if this is about a climate tech funding round. Return JSON:
            {{
                "is_funding_deal": boolean,
                "startup_name": "string or null",
                "sector": "Grid Modernization|Carbon Capture|Other",
                "stage": "Seed|Series A|Series B|Other",
                "amount": "amount in millions or null",
                "confidence": 0.0-1.0
            }}
            """
            
            response = self.client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return None

# Alternative fallback data sources for when scraping is limited
def get_sample_funding_sources() -> List[Dict]:
    """
    Fallback funding data sources that work without JavaScript
    For deployment environments with limited scraping capabilities
    """
    return [
        {
            'title': 'Sample Climate Tech Funding Round',
            'startup_name': 'GridTech Solutions',
            'sector': 'Grid Modernization',
            'stage': 'Series A',
            'amount': 15.0,
            'source': 'Sample Data',
            'url': 'https://example.com',
            'note': 'Deployment-ready sample data'
        }
    ]