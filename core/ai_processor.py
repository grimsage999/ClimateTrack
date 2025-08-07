import json
import os
from typing import Dict, List, Optional
import pandas as pd
from openai import OpenAI
import config

class AIProcessor:
    """AI-powered processing of funding data using OpenAI"""
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            default_headers=config.OPENROUTER_DEFAULT_HEADERS,
        )
        
    def process_funding_event(self, raw_data: Dict) -> Optional[Dict]:
        """Process and classify funding events for focused VC deal flow tracking"""
        try:
            prompt = f"""
            You are an expert data extraction agent focused on climate tech funding events for VC deal flow tracking.
            
            CRITICAL FOCUS: Only extract deals that match ALL criteria:
            1. Subsector: Must be exactly "Grid Modernization" OR "Carbon Capture" 
            2. Funding Stage: Must be exactly "Seed" OR "Series A"
            3. Must have clear funding information
            
            Grid Modernization includes: grid infrastructure, transmission, distribution, smart grid, energy storage integration, grid analytics, demand response
            Carbon Capture includes: direct air capture, carbon capture and storage (CCS), carbon utilization, carbon removal technologies
            
            Raw funding data:
            Company: {raw_data.get('company', 'Unknown')}
            Amount: {raw_data.get('amount', 'Unknown')}
            Stage: {raw_data.get('stage', 'Unknown')}
            Investor: {raw_data.get('lead_investor', 'Unknown')}
            Description: {raw_data.get('description', 'Unknown')}
            
            Extract ONLY these 5 essential fields:
            1. startup_name: Company receiving funding
            2. subsector: "Grid Modernization" or "Carbon Capture" (exact match required)
            3. funding_stage: "Seed" or "Series A" (exact match required)
            4. amount_raised: USD amount in millions
            5. lead_investor: Primary/lead investor (HIGHEST PRIORITY - VC firms track competitors)
            
            IGNORE any funding events outside Grid Modernization or Carbon Capture.
            IGNORE any funding stages other than Seed or Series A.
            
            Respond with JSON in this exact format:
            {{
                "is_target_deal": boolean,
                "startup_name": "string or null",
                "subsector": "Grid Modernization" or "Carbon Capture" or null,
                "funding_stage": "Seed" or "Series A" or null,
                "amount_raised": number in millions USD or null,
                "lead_investor": "string or null",
                "region": "geographic region or null", 
                "date": "funding date in YYYY-MM-DD format or null",
                "confidence_scores": {{
                    "startup_name": number (0-1),
                    "subsector": number (0-1), 
                    "funding_stage": number (0-1),
                    "amount_raised": number (0-1),
                    "lead_investor": number (0-1)
                }}
            }}
            
            If no qualifying deal found, return {{"is_target_deal": false}}.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in climate technology and venture capital. Analyze funding events and classify them accurately."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content or "{}")
            
            # Add metadata
            result['processed_date'] = pd.Timestamp.now().isoformat()
            result['source'] = raw_data.get('source', 'Unknown')
            result['ai_processed'] = True
            
            return result
            
        except Exception as e:
            print(f"Error processing funding event: {str(e)}")
            return None
    
    def classify_climate_sector(self, company_description: str) -> Dict:
        """Classify a company into specific climate tech sectors"""
        try:
            prompt = f"""
            Classify the following company description into specific climate technology sectors.
            
            Description: {company_description}
            
            Available sectors:
            - Solar Energy
            - Wind Energy
            - Energy Storage
            - Carbon Capture & Storage
            - Sustainable Transport & Mobility
            - Agriculture Technology
            - Green Building & Materials
            - Clean Water & Treatment
            - Circular Economy & Waste
            - Climate Adaptation
            - Other Climate Tech
            
            Respond with JSON:
            {{
                "primary_sector": "main sector",
                "secondary_sectors": ["list", "of", "additional", "sectors"],
                "confidence": number between 0 and 1,
                "reasoning": "brief explanation"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in climate technology categorization."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content or "{}")
            
        except Exception as e:
            print(f"Error classifying climate sector: {str(e)}")
            return {"primary_sector": "Other Climate Tech", "confidence": 0.0}
    
    def extract_location_info(self, text: str) -> Dict:
        """Extract and standardize location information"""
        try:
            prompt = f"""
            Extract location information from the following text and standardize it.
            
            Text: {text}
            
            Respond with JSON:
            {{
                "city": "city name or null",
                "state_province": "state/province or null", 
                "country": "country name or null",
                "region": "geographic region (North America, Europe, Asia Pacific, Latin America, Africa, Middle East)",
                "confidence": number between 0 and 1
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in geographic data extraction and standardization."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content or "{}")
            
        except Exception as e:
            print(f"Error extracting location: {str(e)}")
            return {"region": "Unknown", "confidence": 0.0}
    
    def generate_market_insights(self, df: pd.DataFrame) -> Optional[Dict]:
        """Generate AI-powered market insights from funding data"""
        try:
            # Prepare data summary for AI analysis with proper JSON serialization
            summary_data = {
                "total_deals": int(len(df)),
                "total_funding": float(df['amount'].sum()) if 'amount' in df.columns else 0.0,
                "avg_deal_size": float(df['amount'].mean()) if 'amount' in df.columns else 0.0,
                "sectors": {str(k): int(v) for k, v in df['sector'].value_counts().to_dict().items()} if 'sector' in df.columns else {},
                "stages": {str(k): int(v) for k, v in df['stage'].value_counts().to_dict().items()} if 'stage' in df.columns else {},
                "regions": {str(k): int(v) for k, v in df['region'].value_counts().to_dict().items()} if 'region' in df.columns else {},
                "top_investors": {str(k): int(v) for k, v in df['lead_investor'].value_counts().head(10).to_dict().items()} if 'lead_investor' in df.columns else {}
            }
            
            prompt = f"""
            Analyze the following climate tech funding data and provide market insights.
            
            Data Summary:
            {json.dumps(summary_data, indent=2)}
            
            Provide analysis in the following areas:
            1. Key market trends and patterns
            2. Investment opportunities and gaps
            3. Geographic distribution insights
            4. Sector performance analysis
            5. Stage distribution patterns
            
            Respond with JSON:
            {{
                "trends": "markdown-formatted analysis of key trends",
                "opportunities": "markdown-formatted investment opportunities",
                "analysis": "markdown-formatted detailed market analysis",
                "recommendations": "markdown-formatted recommendations",
                "risk_factors": "markdown-formatted potential risks"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior climate tech venture capital analyst with deep market expertise."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content or "{}")
            
        except Exception as e:
            print(f"Error generating market insights: {str(e)}")
            return None
    
    def standardize_funding_stage(self, stage_text: str) -> str:
        """Standardize funding stage nomenclature"""
        try:
            prompt = f"""
            Standardize the following funding stage to one of the standard categories:
            
            Input: {stage_text}
            
            Standard categories:
            - Pre-Seed
            - Seed
            - Series A
            - Series B
            - Series C
            - Series D+
            - Growth
            - Unknown
            
            Respond with just the standardized category name.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in venture capital funding terminology."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            return (response.choices[0].message.content or "Unknown").strip()
            
        except Exception as e:
            print(f"Error standardizing stage: {str(e)}")
            return "Unknown"
