"""
Focused sample data for VC deal flow tracking
Grid Modernization and Carbon Capture deals only (Seed/Series A)
"""

from typing import List, Dict
from datetime import datetime, timedelta
import random

def create_focused_vc_sample_data() -> List[Dict]:
    """Create focused sample data for VC associates tracking Grid Modernization and Carbon Capture deals"""
    
    # Generate dates from last 30 days for recent deal flow
    base_date = datetime.now()
    
    sample_deals = [
        {
            "company": "GridFlow Technologies", 
            "amount": 18.0,
            "stage": "Series A", 
            "lead_investor": "Energy Impact Partners",
            "other_investors": ["Shell Ventures", "Breakthrough Energy Ventures"],
            "sector": "Grid Modernization",
            "region": "North America",
            "location": "Boston, MA",
            "date": (base_date - timedelta(days=5)).strftime("%Y-%m-%d"),
            "description": "AI-powered grid optimization platform for real-time demand response and load balancing",
            "source": "TechCrunch",
            "confidence_score": 0.96,
            "keywords": ["grid optimization", "demand response", "AI", "load balancing"],
            "source_url": "https://techcrunch.com/gridflow-series-a",
            "published_date": (base_date - timedelta(days=5)).strftime("%Y-%m-%d")
        },
        {
            "company": "CarbonVault Systems", 
            "amount": 35.0,
            "stage": "Series A", 
            "lead_investor": "Khosla Ventures",
            "other_investors": ["Microsoft Climate Innovation Fund", "Amazon Climate Pledge Fund"],
            "sector": "Carbon Capture",
            "region": "North America", 
            "location": "Palo Alto, CA",
            "date": (base_date - timedelta(days=7)).strftime("%Y-%m-%d"),
            "description": "Direct air capture technology with enhanced mineralization storage and 99% capture rate",
            "source": "VentureBeat",
            "confidence_score": 0.94,
            "keywords": ["direct air capture", "DAC", "carbon storage", "mineralization"],
            "source_url": "https://venturebeat.com/carbonvault-funding",
            "published_date": (base_date - timedelta(days=7)).strftime("%Y-%m-%d")
        },
        {
            "company": "SmartGrid Analytics", 
            "amount": 12.5,
            "stage": "Seed", 
            "lead_investor": "Congruent Ventures",
            "other_investors": ["Clean Energy Ventures", "Powerhouse Ventures"],
            "sector": "Grid Modernization",
            "region": "North America",
            "location": "Austin, TX", 
            "date": (base_date - timedelta(days=10)).strftime("%Y-%m-%d"),
            "description": "Machine learning platform for predictive grid maintenance and fault detection",
            "source": "Crunchbase News",
            "confidence_score": 0.92,
            "keywords": ["predictive maintenance", "grid analytics", "machine learning", "fault detection"],
            "source_url": "https://news.crunchbase.com/smartgrid-seed",
            "published_date": (base_date - timedelta(days=10)).strftime("%Y-%m-%d")
        },
        {
            "company": "AtmosCapture Inc", 
            "amount": 8.2,
            "stage": "Seed", 
            "lead_investor": "First Round Capital",
            "other_investors": ["Lowercarbon Capital", "Prime Impact Fund"],
            "sector": "Carbon Capture",
            "region": "North America",
            "location": "Denver, CO",
            "date": (base_date - timedelta(days=12)).strftime("%Y-%m-%d"),
            "description": "Modular direct air capture units for distributed carbon removal at industrial scale",
            "source": "CleanTech.com", 
            "confidence_score": 0.90,
            "keywords": ["modular DAC", "distributed capture", "carbon removal", "industrial scale"],
            "source_url": "https://cleantech.com/atmoscapture-seed",
            "published_date": (base_date - timedelta(days=12)).strftime("%Y-%m-%d")
        },
        {
            "company": "TransmissionIQ",
            "amount": 22.0,
            "stage": "Series A",
            "lead_investor": "NEA (New Enterprise Associates)",
            "other_investors": ["GE Ventures", "Siemens Next47"],
            "sector": "Grid Modernization", 
            "region": "North America",
            "location": "San Jose, CA",
            "date": (base_date - timedelta(days=14)).strftime("%Y-%m-%d"),
            "description": "Advanced transmission line monitoring using IoT sensors and digital twin technology",
            "source": "TechCrunch",
            "confidence_score": 0.93,
            "keywords": ["transmission monitoring", "IoT sensors", "digital twin", "grid infrastructure"],
            "source_url": "https://techcrunch.com/transmissioniq-series-a",
            "published_date": (base_date - timedelta(days=14)).strftime("%Y-%m-%d")
        },
        {
            "company": "CO2 Solutions Ltd",
            "amount": 15.8,
            "stage": "Series A",
            "lead_investor": "Obvious Ventures", 
            "other_investors": ["Climate Capital", "Energy Innovation Capital"],
            "sector": "Carbon Capture",
            "region": "Europe",
            "location": "London, UK",
            "date": (base_date - timedelta(days=16)).strftime("%Y-%m-%d"),
            "description": "Enzyme-enhanced carbon capture technology for industrial emission reduction",
            "source": "Green Tech Media",
            "confidence_score": 0.89,
            "keywords": ["enzyme capture", "industrial emissions", "carbon utilization", "CCS"],
            "source_url": "https://greentechmedia.com/co2solutions-funding",
            "published_date": (base_date - timedelta(days=16)).strftime("%Y-%m-%d")
        },
        {
            "company": "MicroGrid Dynamics",
            "amount": 6.5,
            "stage": "Seed",
            "lead_investor": "Powerhouse Ventures",
            "other_investors": ["Clean Energy Trust", "Elemental Excelerator"],
            "sector": "Grid Modernization",
            "region": "North America", 
            "location": "Portland, OR",
            "date": (base_date - timedelta(days=18)).strftime("%Y-%m-%d"),
            "description": "Autonomous microgrid control systems for resilient distributed energy networks",
            "source": "VentureBeat",
            "confidence_score": 0.91,
            "keywords": ["microgrid", "autonomous control", "distributed energy", "grid resilience"],
            "source_url": "https://venturebeat.com/microgrid-seed",
            "published_date": (base_date - timedelta(days=18)).strftime("%Y-%m-%d")
        },
        {
            "company": "AirMend Technologies",
            "amount": 28.5,
            "stage": "Series A",
            "lead_investor": "Breakthrough Energy Ventures",
            "other_investors": ["Shopify Sustainability Fund", "Stripe Climate"],
            "sector": "Carbon Capture",
            "region": "North America",
            "location": "Montreal, Canada", 
            "date": (base_date - timedelta(days=20)).strftime("%Y-%m-%d"),
            "description": "Scalable direct air capture with permanent geological storage partnerships",
            "source": "Crunchbase News",
            "confidence_score": 0.95,
            "keywords": ["scalable DAC", "geological storage", "permanent removal", "carbon credits"],
            "source_url": "https://news.crunchbase.com/airmend-series-a",
            "published_date": (base_date - timedelta(days=20)).strftime("%Y-%m-%d")
        },
        {
            "company": "GridSecure Systems",
            "amount": 4.8,
            "stage": "Seed",
            "lead_investor": "Clean Energy Ventures",
            "other_investors": ["Energy Foundry", "Evok Innovations"],
            "sector": "Grid Modernization",
            "region": "North America",
            "location": "Chicago, IL",
            "date": (base_date - timedelta(days=22)).strftime("%Y-%m-%d"),
            "description": "Cybersecurity platform specifically designed for smart grid infrastructure protection",
            "source": "CleanTech.com",
            "confidence_score": 0.88,
            "keywords": ["grid cybersecurity", "smart grid", "infrastructure protection", "cyber threats"],
            "source_url": "https://cleantech.com/gridsecure-seed",
            "published_date": (base_date - timedelta(days=22)).strftime("%Y-%m-%d")
        },
        {
            "company": "CaptureTech Innovations",
            "amount": 11.2,
            "stage": "Seed",
            "lead_investor": "Lowercarbon Capital",
            "other_investors": ["Climate Technology Fund", "Version One Ventures"],
            "sector": "Carbon Capture",
            "region": "North America",
            "location": "Vancouver, Canada",
            "date": (base_date - timedelta(days=25)).strftime("%Y-%m-%d"),
            "description": "Ocean-based direct air capture using novel sorbent materials and renewable energy",
            "source": "TechCrunch",
            "confidence_score": 0.87,
            "keywords": ["ocean capture", "sorbent materials", "renewable powered", "maritime DAC"],
            "source_url": "https://techcrunch.com/capturetech-seed",
            "published_date": (base_date - timedelta(days=25)).strftime("%Y-%m-%d")
        }
    ]
    
    return sample_deals

if __name__ == "__main__":
    deals = create_focused_vc_sample_data()
    print(f"Generated {len(deals)} focused VC deals")
    for deal in deals[:3]:  # Show first 3 deals
        print(f"- {deal['company']}: ${deal['amount']}M {deal['stage']} led by {deal['lead_investor']}")