"""Sample climate tech funding data for demonstration purposes"""

import pandas as pd
from datetime import datetime, timedelta
import random

def generate_sample_funding_data():
    """Generate realistic sample climate tech funding data"""
    
    # Sample companies with realistic climate tech focus
    companies = [
        {
            "company": "SolarFlow Technologies",
            "sector": "Solar Energy",
            "stage": "Series B",
            "amount": 45000000,
            "lead_investor": "Breakthrough Energy Ventures",
            "location": "San Francisco, CA",
            "region": "North America",
            "description": "AI-powered solar panel optimization platform for residential and commercial installations",
            "climate_tech_keywords": ["solar", "AI", "optimization", "renewable energy"],
            "confidence_score": 0.95
        },
        {
            "company": "CarbonCapture Labs",
            "sector": "Carbon Capture & Storage",
            "stage": "Series A",
            "amount": 25000000,
            "lead_investor": "Climate Pledge Fund",
            "location": "Boston, MA",
            "region": "North America",
            "description": "Direct air capture technology for industrial applications and carbon removal",
            "climate_tech_keywords": ["carbon capture", "DAC", "industrial", "carbon removal"],
            "confidence_score": 0.98
        },
        {
            "company": "GreenGrid Analytics",
            "sector": "Energy Storage",
            "stage": "Seed",
            "amount": 8500000,
            "lead_investor": "Energy Impact Partners",
            "location": "Austin, TX",
            "region": "North America",
            "description": "Grid-scale battery optimization using machine learning for renewable energy storage",
            "climate_tech_keywords": ["energy storage", "battery", "machine learning", "grid"],
            "confidence_score": 0.92
        },
        {
            "company": "EcoTransport Solutions",
            "sector": "Sustainable Transport & Mobility",
            "stage": "Series C",
            "amount": 75000000,
            "lead_investor": "TPG Rise",
            "location": "London, UK",
            "region": "Europe",
            "description": "Electric vehicle fleet management platform for enterprise and logistics",
            "climate_tech_keywords": ["electric vehicle", "fleet management", "logistics", "sustainable transport"],
            "confidence_score": 0.94
        },
        {
            "company": "AgroTech Innovations",
            "sector": "Agriculture Technology",
            "stage": "Series A",
            "amount": 18000000,
            "lead_investor": "S2G Ventures",
            "location": "Amsterdam, NL",
            "region": "Europe",
            "description": "Precision agriculture using satellite imagery and AI for sustainable farming",
            "climate_tech_keywords": ["agriculture", "precision farming", "satellite", "AI", "sustainable"],
            "confidence_score": 0.89
        },
        {
            "company": "CleanWater Systems",
            "sector": "Clean Water & Treatment",
            "stage": "Series B",
            "amount": 32000000,
            "lead_investor": "Blue Haven Initiative",
            "location": "Singapore",
            "region": "Asia Pacific",
            "description": "Advanced water purification technology for industrial and municipal applications",
            "climate_tech_keywords": ["water treatment", "purification", "industrial", "municipal"],
            "confidence_score": 0.91
        },
        {
            "company": "WindFlow Dynamics",
            "sector": "Wind Energy",
            "stage": "Growth",
            "amount": 120000000,
            "lead_investor": "Copenhagen Infrastructure Partners",
            "location": "Copenhagen, DK",
            "region": "Europe",
            "description": "Next-generation wind turbine technology with improved efficiency and reduced maintenance",
            "climate_tech_keywords": ["wind energy", "turbine", "efficiency", "renewable"],
            "confidence_score": 0.96
        },
        {
            "company": "BioMaterials Corp",
            "sector": "Green Building & Materials",
            "stage": "Seed",
            "amount": 12000000,
            "lead_investor": "Material Impact",
            "location": "Portland, OR",
            "region": "North America",
            "description": "Sustainable building materials from agricultural waste and bio-based polymers",
            "climate_tech_keywords": ["sustainable materials", "bio-based", "building", "agricultural waste"],
            "confidence_score": 0.88
        },
        {
            "company": "ClimateAdapt Technologies",
            "sector": "Climate Adaptation",
            "stage": "Pre-Seed",
            "amount": 3500000,
            "lead_investor": "Ecosystem Integrity Fund",
            "location": "Melbourne, AU",
            "region": "Asia Pacific",
            "description": "Early warning systems for climate-related disasters using IoT and satellite data",
            "climate_tech_keywords": ["climate adaptation", "early warning", "IoT", "satellite"],
            "confidence_score": 0.85
        },
        {
            "company": "CircularTech Solutions",
            "sector": "Circular Economy & Waste",
            "stage": "Series A",
            "amount": 22000000,
            "lead_investor": "Closed Loop Partners",
            "location": "São Paulo, BR",
            "region": "Latin America",
            "description": "AI-powered waste sorting and recycling optimization for urban environments",
            "climate_tech_keywords": ["circular economy", "waste sorting", "recycling", "AI"],
            "confidence_score": 0.93
        }
    ]
    
    # Generate dates in the last 30 days
    base_date = datetime.now()
    
    for i, company in enumerate(companies):
        # Add random dates within the last 30 days
        days_ago = random.randint(1, 30)
        company["date"] = (base_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        company["processed_date"] = base_date.isoformat()
        company["source"] = random.choice(["TechCrunch", "VentureBeat", "Crunchbase News", "Green Tech Media"])
        company["ai_processed"] = True
        company["is_climate_tech"] = True
        company["scraped_date"] = (base_date - timedelta(days=days_ago)).isoformat()
    
    return companies

def load_sample_data_to_manager(data_manager):
    """Load sample data into the data manager"""
    sample_data = generate_sample_funding_data()
    data_manager.save_funding_data(sample_data)
    return len(sample_data)