"""
LLM-powered data extraction for climate tech funding events
Converts raw news articles into structured VC deal data
"""

import json
import os
import config
from typing import Dict, Optional, List
from openai import OpenAI
from core.funding_event import FundingEvent, FundingEventValidator

class FundingDataExtractor:
    """
    Extract structured funding data from raw news content using AI
    Focused on VC deal intelligence: startup, sector, stage, amount, lead investor
    """
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "openai/gpt-4o"  # OpenRouter format for model
        # OpenRouter API setup using OPENAI2 secret for CTVC scraping
        self.client = OpenAI(
            api_key=config.OPENAI2_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            default_headers=config.OPENROUTER_DEFAULT_HEADERS,
        )
    
    def extract_funding_event(self, raw_content: Dict) -> Optional[FundingEvent]:
        """
        Extract structured funding event from raw article content
        Returns FundingEvent if valid VC deal, None otherwise
        """
        try:
            # Handle different input formats
            if isinstance(raw_content, dict) and 'is_target_deal' in raw_content:
                # Already processed by enhanced API client
                return self._format_enhanced_data(raw_content)
            
            # Extract structured data using AI
            extracted_data = self._ai_extract_deal_data(raw_content)
            if not extracted_data:
                return None
            
            # Create funding event
            event = FundingEvent(
                startup_name=extracted_data.get('startup_name', ''),
                subsector=extracted_data.get('subsector', ''),
                funding_stage=extracted_data.get('funding_stage', ''),
                amount_raised=float(extracted_data.get('amount_raised', 0)),
                lead_investor=extracted_data.get('lead_investor', ''),
                published_date=raw_content.get('date', ''),
                source_url=raw_content.get('source_url', ''),
                source=raw_content.get('source', 'Web Scraping'),
                region=extracted_data.get('region'),
                confidence_score=extracted_data.get('confidence_score', 0.0)
            )
            
            # Validate event meets VC criteria  
            if event.is_valid_vc_deal():
                return event
            else:
                return None
                
        except Exception as e:
            print(f"Extraction error: {e}")
            return None
    
    def _ai_extract_deal_data(self, raw_content: Dict) -> Optional[Dict]:
        """Use AI to extract structured deal data from raw content"""
        
        content_text = self._prepare_content_for_extraction(raw_content)
        
        prompt = f"""You are a VC funding analyst extracting deal data for climate tech investments.

ONLY EXTRACT deals that are:
1. Subsector: Grid Modernization (grid infrastructure, smart grid, transmission, distribution, energy storage grid integration) OR Carbon Capture (direct air capture, CCS, carbon utilization, carbon removal)
2. Funding Stage: Seed OR Series A only  
3. Clear funding announcement with specific dollar amount and lead investor

Extract these 5 essential fields:
- startup_name: Company that raised funding
- subsector: "Grid Modernization" or "Carbon Capture" (exact match required)
- funding_stage: "Seed" or "Series A" (exact match required)
- amount_raised: Dollar amount in millions (numeric)
- lead_investor: Primary investor leading the round

IGNORE if not in target subsectors or funding stages.

Content: {content_text}

Return JSON:
{{
    "startup_name": "string or null",
    "subsector": "Grid Modernization" or "Carbon Capture" or null,
    "funding_stage": "Seed" or "Series A" or null,
    "amount_raised": number or null,
    "lead_investor": "string or null",
    "region": "string or null",
    "confidence_score": number (0-1),
    "is_target_deal": boolean
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            
            # Validate target deal criteria
            if (extracted_data.get('subsector') in self.target_subsectors and 
                extracted_data.get('funding_stage') in self.target_stages and
                extracted_data.get('amount_raised', 0) > 0):
                extracted_data['is_target_deal'] = True
            else:
                extracted_data['is_target_deal'] = False
                
            return extracted_data
            
        except Exception as e:
            print(f"AI extraction error: {e}")
            return None
    
    def _prepare_content_for_extraction(self, raw_content: Dict) -> str:
        """Prepare raw content for AI extraction"""
        content_parts = []
        
        if raw_content.get('title'):
            content_parts.append(f"Title: {raw_content['title']}")
        
        if raw_content.get('content'):
            # Limit content length for AI processing
            content = raw_content['content'][:2000]
            content_parts.append(f"Content: {content}")
        
        if raw_content.get('summary'):
            content_parts.append(f"Summary: {raw_content['summary']}")
        
        return '\n\n'.join(content_parts)
    
    def _format_enhanced_data(self, enhanced_data: Dict) -> Optional[FundingEvent]:
        """Format data from enhanced API client"""
        try:
            event = FundingEvent(
                startup_name=enhanced_data.get('startup_name', ''),
                subsector=enhanced_data.get('subsector', ''),
                funding_stage=enhanced_data.get('funding_stage', ''),
                amount_raised=float(enhanced_data.get('amount_raised', 0)),
                lead_investor=enhanced_data.get('lead_investor', ''),
                published_date=enhanced_data.get('published_date', ''),
                source_url=enhanced_data.get('source_url', ''),
                source=enhanced_data.get('source', 'Enhanced API'),
                confidence_score=enhanced_data.get('confidence_scores', {}).get('startup_name', 0.8)
            )
            
            return event if event.is_valid_vc_deal() else None
            
        except Exception as e:
            print(f"Enhanced data formatting error: {e}")
            return None
    
    def batch_extract_events(self, raw_content_list: List[Dict]) -> List[FundingEvent]:
        """Extract funding events from multiple raw content items"""
        events = []
        
        for raw_content in raw_content_list:
            event = self.extract_funding_event(raw_content)
            if event:
                events.append(event)
        
        return events
    
    def validate_extraction_quality(self, events: List[FundingEvent]) -> Dict:
        """Analyze quality of extracted events"""
        total_events = len(events)
        valid_events = sum(1 for e in events if FundingEventValidator.is_valid(e))
        
        sector_distribution = {}
        stage_distribution = {}
        confidence_scores = []
        
        for event in events:
            # Sector distribution
            sector_distribution[event.subsector] = sector_distribution.get(event.subsector, 0) + 1
            
            # Stage distribution  
            stage_distribution[event.funding_stage] = stage_distribution.get(event.funding_stage, 0) + 1
            
            # Confidence scores
            confidence_scores.append(event.confidence_score)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            'total_extracted': total_events,
            'valid_events': valid_events,
            'validation_rate': valid_events / total_events if total_events > 0 else 0,
            'sector_distribution': sector_distribution,
            'stage_distribution': stage_distribution,
            'average_confidence': avg_confidence,
            'quality_score': (valid_events / total_events * 0.7 + avg_confidence * 0.3) if total_events > 0 else 0
        }

class ArticleClassifier:
    """Classify articles as funding announcements vs general news"""
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o" # Keep the model here
        # --- NEW: Use config for client setup ---
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            default_headers=config.OPENROUTER_DEFAULT_HEADERS,
        )
    
    def classify_article(self, title: str, content: str) -> str:
        """
        Classify article type for funding event detection
        Returns: 'STARTUP_FUNDING_ROUND', 'FUND_ANNOUNCEMENT', 'GENERAL_NEWS'
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
    
    def is_funding_announcement(self, title: str, content: str) -> bool:
        """Check if article is a startup funding announcement"""
        classification = self.classify_article(title, content)
        return classification == "STARTUP_FUNDING_ROUND"