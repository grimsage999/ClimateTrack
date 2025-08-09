"""Utility functions for the Climate Tech Funding Tracker"""

import re
from datetime import datetime
from typing import Optional, Union
import pandas as pd

# --- NEW: Smart function to parse funding amount strings ---
def parse_funding_amount(amount_str: Union[str, int, float]) -> float:
    """
    Parses a funding amount string (e.g., '$10M', '€2.5 billion') into a float in millions.
    """
    if pd.isna(amount_str) or amount_str is None:
        return 0.0
    if isinstance(amount_str, (int, float)):
        return float(amount_str) # Assume it's already in millions if it's a number

    text = str(amount_str).strip().lower()
    if text in ['not specified', 'undisclosed', 'undisclosed amount']:
        return 0.0

    # Regular expression to find the number and the unit (M or B)
    # Handles formats like: $10m, 10m, €10m, $10 million, 2.5b, etc.
    match = re.search(r'(\d+(?:\.\d+)?)\s*(m|b|million|billion)', text)
    
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        
        if unit in ['b', 'billion']:
            return value * 1000  # Convert billions to millions
        elif unit in ['m', 'million']:
            return value # Already in millions
            
    # Fallback for plain numbers, assume they are in millions
    try:
        # Remove currency symbols and commas
        plain_number_str = re.sub(r'[$,€£,]', '', text)
        return float(plain_number_str)
    except ValueError:
        return 0.0 # Return 0.0 if no number can be parsed


def format_currency(amount: Union[int, float]) -> str:
    """Format currency amounts in a human-readable way"""
    if pd.isna(amount) or amount is None:
        return "N/A"
    
    try:
        amount = float(amount)
        if amount >= 1000000000:
            return f"${amount/1000000000:.1f}B"
        elif amount >= 1000000:
            return f"${amount/1000000:.1f}M"
        elif amount >= 1000:
            return f"${amount/1000:.0f}K"
        else:
            return f"${amount:,.0f}"
    except (ValueError, TypeError):
        return "N/A"

def format_date(date_input: Union[str, datetime, pd.Timestamp]) -> str:
    """Format dates in a consistent way"""
    if pd.isna(date_input) or date_input is None:
        return "N/A"
    
    try:
        if isinstance(date_input, str):
            date_obj = pd.to_datetime(date_input)
        elif isinstance(date_input, (datetime, pd.Timestamp)):
            date_obj = date_input
        else:
            return "N/A"
        
        return date_obj.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return "N/A"

def clean_company_name(name: str) -> str:
    """Clean and standardize company names"""
    if not name or pd.isna(name):
        return "Unknown"
    
    # Remove common suffixes and prefixes
    name = str(name).strip()
    name = re.sub(r'\s+(Inc\.?|LLC|Ltd\.?|Corp\.?|Corporation|Company)$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^(The\s+)', '', name, flags=re.IGNORECASE)
    
    # Clean up whitespace
    name = ' '.join(name.split())
    
    return name[:100]  # Limit length

def clean_text(text: str, max_length: int = 500) -> str:
    """Clean and standardize text fields"""
    if not text or pd.isna(text):
        return ""
    
    text = str(text).strip()
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text

def extract_amount_from_text(text: str) -> Optional[float]:
    """Extract funding amounts from text"""
    if not text:
        return None
    
    # Look for patterns like "$50M", "$2.5B", "$100 million"
    patterns = [
        r'\$(\d+(?:\.\d+)?)\s*(million|M)\b',
        r'\$(\d+(?:\.\d+)?)\s*(billion|B)\b',
        r'\$(\d+(?:\.\d+)?)\s*M\b',
        r'\$(\d+(?:\.\d+)?)\s*B\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            unit = match.group(2).lower()
            
            if unit in ['million', 'm']:
                return value * 1000000
            elif unit in ['billion', 'b']:
                return value * 1000000000
    
    return None

def standardize_stage(stage: str) -> str:
    """Standardize funding stage names"""
    if not stage or pd.isna(stage):
        return "Unknown"
    
    stage = str(stage).strip().lower()
    
    stage_mapping = {
        'pre-seed': 'Pre-Seed',
        'preseed': 'Pre-Seed',
        'seed': 'Seed',
        'series a': 'Series A',
        'series b': 'Series B', 
        'series c': 'Series C',
        'series d': 'Series D+',
        'series e': 'Series D+',
        'series f': 'Series D+',
        'growth': 'Growth',
        'late stage': 'Growth',
        'venture': 'Series A',  # Default for generic "venture"
    }
    
    for key, value in stage_mapping.items():
        if key in stage:
            return value
    
    return "Unknown"

def standardize_region(location: str) -> str:
    """Standardize geographic regions"""
    if not location or pd.isna(location):
        return "Unknown"
    
    location = str(location).lower()
    
    # North America
    if any(country in location for country in ['usa', 'us', 'united states', 'canada', 'mexico']):
        return "North America"
    if any(state in location for state in ['ca', 'ny', 'tx', 'ma', 'wa', 'california', 'new york', 'texas']):
        return "North America"
    
    # Europe
    if any(country in location for country in ['uk', 'united kingdom', 'germany', 'france', 'spain', 'italy', 'netherlands', 'sweden', 'norway', 'finland', 'denmark']):
        return "Europe"
    
    # Asia Pacific
    if any(country in location for country in ['china', 'japan', 'korea', 'india', 'singapore', 'australia', 'new zealand']):
        return "Asia Pacific"
    
    # Latin America
    if any(country in location for country in ['brazil', 'argentina', 'chile', 'colombia', 'peru']):
        return "Latin America"
    
    # Africa
    if any(country in location for country in ['south africa', 'nigeria', 'kenya', 'egypt']):
        return "Africa"
    
    # Middle East
    if any(country in location for country in ['israel', 'uae', 'saudi arabia', 'qatar']):
        return "Middle East"
    
    return "Unknown"

def validate_funding_data(data: dict) -> bool:
    """Validate funding data completeness and quality"""
    required_fields = ['company']
    
    # Check required fields
    for field in required_fields:
        if not data.get(field):
            return False
    
    # Check data quality
    if data.get('amount') and data['amount'] < 0:
        return False
    
    company_name = data.get('company', '')
    if len(company_name) < 2 or len(company_name) > 100:
        return False
    
    return True

def calculate_growth_rate(current_value: float, previous_value: float) -> Optional[float]:
    """Calculate growth rate between two values"""
    if not current_value or not previous_value or previous_value == 0:
        return None
    
    try:
        return ((current_value - previous_value) / previous_value) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def get_time_period_label(start_date: datetime, end_date: datetime) -> str:
    """Generate a human-readable time period label"""
    try:
        delta = end_date - start_date
        
        if delta.days <= 1:
            return "Today"
        elif delta.days <= 7:
            return "This Week"
        elif delta.days <= 30:
            return "This Month"
        elif delta.days <= 90:
            return "Last 3 Months"
        elif delta.days <= 365:
            return "This Year"
        else:
            return f"{start_date.strftime('%Y')} - {end_date.strftime('%Y')}"
    except:
        return "Custom Period"
