"""
Core data model for climate tech funding events
Defines the structure and validation for VC deal tracking
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime
import json
import pandas as pd

@dataclass
class FundingEvent:
    """
    Core data model for a climate tech funding event
    Focused on VC associate needs: startup, sector, stage, amount, lead investor
    """
    
    # Essential VC fields
    startup_name: str
    subsector: str  # "Grid Modernization" or "Carbon Capture"
    funding_stage: str  # "Seed" or "Series A"
    amount_raised: float  # in millions USD
    lead_investor: str
    
    # Supporting data
    published_date: str
    source_url: str
    source: str
    region: Optional[str] = None
    
    # Quality metrics
    confidence_score: float = 0.0
    is_target_deal: bool = False
    
    def __post_init__(self):
        """Validate funding event meets VC criteria"""
        self.is_target_deal = (
            self.subsector in ["Grid Modernization", "Carbon Capture"] and
            self.funding_stage in ["Seed", "Series A"] and
            self.amount_raised > 0
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for CSV/JSON export"""
        return {
            'company': self.startup_name,
            'sector': self.subsector,
            'stage': self.funding_stage,
            'amount': self.amount_raised,
            'lead_investor': self.lead_investor,
            'date': self.published_date,
            'source_url': self.source_url,
            'source': self.source,
            'region': self.region,
            'confidence_score': self.confidence_score,
            'is_target_deal': self.is_target_deal
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FundingEvent':
        """Create FundingEvent from dictionary data with robust type conversion."""
        try:
            # --- THIS IS THE FIX ---
            # Proactively handle potential conversion errors
            amount = float(data.get('amount', 0.0)) if pd.notna(data.get('amount')) else 0.0
            # --- END OF FIX ---
            
            return cls(
                startup_name=str(data.get('company', '')),
                subsector=str(data.get('sector', '')),
                funding_stage=str(data.get('stage', '')),
                amount_raised=amount,
                lead_investor=str(data.get('lead_investor', '')),
                published_date=str(data.get('date', '')),
                source_url=str(data.get('source_url', '')),
                source=str(data.get('source', '')),
                region=str(data.get('region', '')),
                confidence_score=float(data.get('confidence_score', 0.0)),
                is_target_deal=bool(data.get('is_target_deal', False))
            )
        except (ValueError, TypeError) as e:
            print(f"Error creating FundingEvent from dict: {data}. Error: {e}")
            # Return a default/empty event or raise an exception
            # For robustness, we'll return a non-deal event
            return cls(startup_name="Invalid Data", subsector="", funding_stage="", amount_raised=0.0, lead_investor="", published_date="", source_url="", source="")
    
    def is_valid_vc_deal(self) -> bool:
        """Check if this meets VC associate criteria"""
        return (
            bool(self.startup_name) and
            self.subsector in ["Grid Modernization", "Carbon Capture"] and
            self.funding_stage in ["Seed", "Series A"] and
            self.amount_raised > 0 and
            bool(self.lead_investor)
        )
    
    def get_deal_summary(self) -> str:
        """Get concise deal summary for VC reports"""
        return f"{self.startup_name}: ${self.amount_raised:.1f}M {self.funding_stage} led by {self.lead_investor} ({self.subsector})"

class FundingEventValidator:
    """Validates funding events against VC criteria"""
    
    VALID_SUBSECTORS = ["Grid Modernization", "Carbon Capture"]
    VALID_STAGES = ["Seed", "Series A"]
    MIN_AMOUNT = 0.5  # $500K minimum
    MAX_AMOUNT = 100  # $100M maximum for early stage
    
    @classmethod
    def validate_event(cls, event: FundingEvent) -> List[str]:
        """Return list of validation errors"""
        errors = []
        
        if not event.startup_name:
            errors.append("Missing startup name")
        
        if event.subsector not in cls.VALID_SUBSECTORS:
            errors.append(f"Invalid subsector: {event.subsector}")
        
        if event.funding_stage not in cls.VALID_STAGES:
            errors.append(f"Invalid funding stage: {event.funding_stage}")
        
        if event.amount_raised < cls.MIN_AMOUNT:
            errors.append(f"Amount too low: ${event.amount_raised}M")
        
        if event.amount_raised > cls.MAX_AMOUNT:
            errors.append(f"Amount too high for early stage: ${event.amount_raised}M")
        
        if not event.lead_investor:
            errors.append("Missing lead investor")
        
        return errors
    
    @classmethod
    def is_valid(cls, event: FundingEvent) -> bool:
        """Check if event passes validation"""
        return len(cls.validate_event(event)) == 0

class FundingEventCollection:
    """Collection of funding events with VC-focused operations"""
    
    def __init__(self, events: List[FundingEvent] = None):
        self.events = events or []
    
    def add_event(self, event: FundingEvent) -> bool:
        """Add event if it's a valid VC deal"""
        if event.is_valid_vc_deal():
            self.events.append(event)
            return True
        return False
    
    def filter_by_sector(self, sector: str) -> 'FundingEventCollection':
        """Filter events by subsector"""
        filtered = [e for e in self.events if e.subsector == sector]
        return FundingEventCollection(filtered)
    
    def filter_by_stage(self, stage: str) -> 'FundingEventCollection':
        """Filter events by funding stage"""
        filtered = [e for e in self.events if e.funding_stage == stage]
        return FundingEventCollection(filtered)
    
    def filter_by_investor(self, investor: str) -> 'FundingEventCollection':
        """Filter events by lead investor"""
        filtered = [e for e in self.events if investor.lower() in e.lead_investor.lower()]
        return FundingEventCollection(filtered)
    
    def get_total_funding(self) -> float:
        """Get total funding amount"""
        return sum(e.amount_raised for e in self.events)
    
    def get_deal_count(self) -> int:
        """Get number of deals"""
        return len(self.events)
    
    def get_unique_investors(self) -> List[str]:
        """Get list of unique lead investors"""
        return list(set(e.lead_investor for e in self.events if e.lead_investor))
    
    def get_sector_breakdown(self) -> Dict[str, int]:
        """Get deal count by sector"""
        breakdown = {}
        for event in self.events:
            breakdown[event.subsector] = breakdown.get(event.subsector, 0) + 1
        return breakdown
    
    def get_stage_breakdown(self) -> Dict[str, int]:
        """Get deal count by stage"""
        breakdown = {}
        for event in self.events:
            breakdown[event.funding_stage] = breakdown.get(event.funding_stage, 0) + 1
        return breakdown
    
    def to_dataframe(self):
        """Convert to pandas DataFrame for analysis"""
        import pandas as pd
        data = [event.to_dict() for event in self.events]
        return pd.DataFrame(data)
    
    def export_to_json(self, filename: str):
        """Export collection to JSON file"""
        data = [event.to_dict() for event in self.events]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_vc_report(self) -> str:
        """Generate VC deal flow report"""
        if not self.events:
            return "No deals found"
        
        report = f"VC Deal Flow Report\n"
        report += f"==================\n\n"
        report += f"Total Deals: {self.get_deal_count()}\n"
        report += f"Total Funding: ${self.get_total_funding():.1f}M\n"
        report += f"Unique Investors: {len(self.get_unique_investors())}\n\n"
        
        report += "Sector Breakdown:\n"
        for sector, count in self.get_sector_breakdown().items():
            report += f"  {sector}: {count} deals\n"
        
        report += "\nStage Breakdown:\n"
        for stage, count in self.get_stage_breakdown().items():
            report += f"  {stage}: {count} deals\n"
        
        report += "\nRecent Deals:\n"
        for event in self.events[-5:]:  # Last 5 deals
            report += f"  • {event.get_deal_summary()}\n"
        
        return report