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

# Climate tech sectors
CLIMATE_SECTORS = [
    "Solar Energy",
    "Wind Energy", 
    "Energy Storage",
    "Carbon Capture & Storage",
    "Sustainable Transport & Mobility",
    "Agriculture Technology",
    "Green Building & Materials",
    "Clean Water & Treatment",
    "Circular Economy & Waste",
    "Climate Adaptation",
    "Other Climate Tech"
]

# Funding stages
FUNDING_STAGES = [
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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
