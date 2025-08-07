# config.py

"""Configuration settings for the Climate Tech Funding Tracker"""

import os

# Data sources
DATA_SOURCES = [
    "TechCrunch",
    "VentureBeat", 
    "Crunchbase News",
    "Green Tech Media",
    "CleanTech.com"
]

# FOCUSED VC USE CASE: Target climate tech subsectors only
TARGET_SUBSECTORS = [
    "Grid Modernization",
    "Carbon Capture"
]

# Grid Modernization keywords for scraping
GRID_KEYWORDS = [
    "grid infrastructure", "transmission", "distribution", "smart grid", 
    "energy storage integration", "grid analytics", "demand response",
    "grid modernization", "power grid", "electrical grid"
]

# Carbon Capture keywords for scraping  
CARBON_KEYWORDS = [
    "direct air capture", "carbon capture and storage", "CCS", 
    "carbon utilization", "carbon removal", "DAC", "carbon capture",
    "carbon storage", "CO2 capture"
]

# FOCUSED VC USE CASE: Target funding stages only
TARGET_FUNDING_STAGES = [
    "Seed",
    "Series A"
]

# All funding stages for reference
ALL_FUNDING_STAGES = [
    "Pre-Seed",
    "Seed", 
    "Series A",
    "Series B",
    "Series C", 
    "Series D+",
    "Growth",
    "Unknown"
]

# Geographic regions
REGIONS = [
    "North America",
    "Europe",
    "Asia Pacific",
    "Latin America",
    "Africa",
    "Middle East"
]

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Direct OpenAI access
OPENAI2_API_KEY = os.getenv("OPENAI2")        # OpenRouter access for scraping

# OpenRouter Configuration for CTVC scraping
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_HEADERS = {
    "HTTP-Referer": "https://github.com/climate-tech-vc-tracker",
    "X-Title": "Climate Tech Funding Tracker",
}

# Scraping configuration
SCRAPE_DELAY_MIN = 1  # Minimum delay between requests (seconds)
SCRAPE_DELAY_MAX = 3  # Maximum delay between requests (seconds)
REQUEST_TIMEOUT = 10  # HTTP request timeout (seconds)

# Data processing
MIN_FUNDING_AMOUNT = 100000  # Minimum funding amount to consider (USD)
MAX_COMPANY_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500

# Auto-refresh settings
AUTO_REFRESH_INTERVAL = 1800  # 30 minutes in seconds
DATA_RETENTION_DAYS = 365  # Keep data for 1 year

# File paths
DATA_DIRECTORY = "data"
FUNDING_DATA_FILE = "climate_funding.csv"
METADATA_FILE = "metadata.json"

# UI Configuration
PAGE_TITLE = "Climate Tech Funding Tracker"
PAGE_ICON = "🌱"
DEFAULT_CHART_HEIGHT = 400

# Feature flags
ENABLE_AUTO_REFRESH = True
ENABLE_AI_INSIGHTS = True
ENABLE_EXPORT = True
ENABLE_ADVANCED_FILTERS = True