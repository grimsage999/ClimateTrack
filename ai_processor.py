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
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
        
    def process_funding_event(self, raw_data: Dict) -> Optional[Dict]:
        """Process and classify a single funding event"""
        try:
            prompt = f"""
            Analyze the following funding information and determine if it's related to climate technology.
            Extract and structure the data according to the JSON format below.
            
            Raw funding data:
            Company: {raw_data.get('company', 'Unknown')}
            Amount: {raw_data.get('amount', 'Unknown')}
            Stage: {raw_data.get('stage', 'Unknown')}
            Investor: {raw_data.get('lead_investor', 'Unknown')}
            Description: {raw_data.get('description', 'Unknown')}
            
            Climate technology includes: renewable energy, energy storage, carbon capture, 
            sustainable transport, green building, clean water, agriculture tech, 
            climate adaptation, and related environmental technologies.
            
            Respond with JSON in this exact format:
            {{
                "is_climate_tech": boolean,
                "company": "cleaned company name",
                "sector": "specific climate tech sector or null",
                "stage": "standardized funding stage",
                "amount": number or null,
                "lead_investor": "lead investor name or null",
                "location": "company location or null",
                "region": "geographic region (North America, Europe, Asia Pacific, etc.)",
                "date": "funding date in YYYY-MM-DD format or null",
                "description": "cleaned description",
                "confidence_score": number between 0 and 1,
                "climate_tech_keywords": ["list", "of", "relevant", "keywords"]
            }}
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
