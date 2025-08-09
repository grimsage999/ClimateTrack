"""
Business logic for filtering and processing VC deal data
Applies investment criteria and formats data for VC associate workflows
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
from core.funding_event import FundingEvent, FundingEventCollection

class VCDealProcessor:
    """
    Process and filter funding events according to VC associate criteria
    Focus: Grid Modernization & Carbon Capture, Seed & Series A deals
    """
    
    def __init__(self):
        # VC investment criteria
        self.target_subsectors = ["Grid Modernization", "Carbon Capture"]  
        self.target_stages = ["Seed", "Series A"]
        self.min_amount = 0.5  # $500K minimum
        self.max_amount = 100  # $100M maximum for early stage
        
        # Date filters
        self.default_lookback_days = 365  # 1 year default
    
    def process_raw_events(self, raw_events: List[Dict]) -> FundingEventCollection:
        """
        Process raw event data into filtered VC deal collection
        Applies all business rules and validation
        """
        events = []
        
        for raw_event in raw_events:
            # Convert to FundingEvent
            if isinstance(raw_event, dict):
                try:
                    event = FundingEvent.from_dict(raw_event)
                    
                    # Apply VC filters
                    if self._meets_vc_criteria(event):
                        events.append(event)
                        
                except Exception as e:
                    print(f"Error processing event: {e}")
                    continue
        
        return FundingEventCollection(events)
    
    def _meets_vc_criteria(self, event: FundingEvent) -> bool:
        """Check if event meets VC associate investment criteria"""
        return (
            # Sector focus
            event.subsector in self.target_subsectors and
            
            # Stage focus  
            event.funding_stage in self.target_stages and
            
            # Amount range
            self.min_amount <= event.amount_raised <= self.max_amount and
            
            # Data quality
            bool(event.startup_name) and
            bool(event.lead_investor) and
            event.confidence_score >= 0.3  # Minimum confidence threshold
        )
    
    def filter_by_date_range(self, events: FundingEventCollection, 
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> FundingEventCollection:
        """Filter events by date range"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=self.default_lookback_days)).strftime('%Y-%m-%d')
        
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        filtered_events = []
        for event in events.events:
            try:
                event_date = datetime.fromisoformat(event.published_date.split('T')[0])
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
                
                if start_dt <= event_date <= end_dt:
                    filtered_events.append(event)
                    
            except (ValueError, AttributeError):
                # Include events with invalid dates (don't filter out)
                filtered_events.append(event)
        
        return FundingEventCollection(filtered_events)
    
    def filter_by_subsector(self, events: FundingEventCollection, 
                          subsector: str) -> FundingEventCollection:
        """Filter events by specific subsector"""
        if subsector not in self.target_subsectors:
            return FundingEventCollection([])
        
        return events.filter_by_sector(subsector)
    
    def filter_by_stage(self, events: FundingEventCollection,
                       stage: str) -> FundingEventCollection:
        """Filter events by funding stage"""
        if stage not in self.target_stages:
            return FundingEventCollection([])
        
        return events.filter_by_stage(stage)
    
    def filter_by_amount_range(self, events: FundingEventCollection,
                             min_amount: float, max_amount: float) -> FundingEventCollection:
        """Filter events by funding amount range"""
        filtered_events = [
            event for event in events.events
            if min_amount <= event.amount_raised <= max_amount
        ]
        return FundingEventCollection(filtered_events)
    
    def prioritize_by_lead_investor(self, events: FundingEventCollection,
                                  priority_investors: List[str]) -> List[FundingEvent]:
        """Prioritize deals by strategic lead investors"""
        priority_deals = []
        regular_deals = []
        
        for event in events.events:
            is_priority = any(
                investor.lower() in event.lead_investor.lower() 
                for investor in priority_investors
            )
            
            if is_priority:
                priority_deals.append(event)
            else:
                regular_deals.append(event)
        
        # Sort by amount within each group
        priority_deals.sort(key=lambda x: x.amount_raised, reverse=True)
        regular_deals.sort(key=lambda x: x.amount_raised, reverse=True)
        
        return priority_deals + regular_deals
    
    def generate_deal_intelligence(self, events: FundingEventCollection) -> Dict:
        """Generate VC deal intelligence summary"""
        if not events.events:
            return {'error': 'No deals found'}
        
        # Basic metrics
        total_deals = events.get_deal_count()
        total_funding = events.get_total_funding()
        avg_deal_size = total_funding / total_deals if total_deals > 0 else 0
        
        # Sector analysis
        sector_breakdown = events.get_sector_breakdown()
        sector_funding = {}
        for sector in self.target_subsectors:
            sector_events = events.filter_by_sector(sector)
            sector_funding[sector] = sector_events.get_total_funding()
        
        # Stage analysis
        stage_breakdown = events.get_stage_breakdown()
        stage_funding = {}
        for stage in self.target_stages:
            stage_events = events.filter_by_stage(stage)
            stage_funding[stage] = stage_events.get_total_funding()
        
        # Investor analysis
        unique_investors = events.get_unique_investors()
        investor_activity = {}
        for investor in unique_investors[:10]:  # Top 10
            investor_deals = events.filter_by_investor(investor)
            investor_activity[investor] = {
                'deal_count': investor_deals.get_deal_count(),
                'total_funding': investor_deals.get_total_funding()
            }
        
        # Recent activity (last 90 days)
        recent_cutoff = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        recent_events = self.filter_by_date_range(events, start_date=recent_cutoff)
        
        return {
            'overview': {
                'total_deals': total_deals,
                'total_funding': round(total_funding, 1),
                'average_deal_size': round(avg_deal_size, 1),
                'unique_investors': len(unique_investors)
            },
            'sector_analysis': {
                'deal_breakdown': sector_breakdown,
                'funding_breakdown': {k: round(v, 1) for k, v in sector_funding.items()}
            },
            'stage_analysis': {
                'deal_breakdown': stage_breakdown,
                'funding_breakdown': {k: round(v, 1) for k, v in stage_funding.items()}
            },
            'investor_activity': investor_activity,
            'recent_activity': {
                'deals_90d': recent_events.get_deal_count(),
                'funding_90d': round(recent_events.get_total_funding(), 1)
            },
            'top_deals': [
                event.get_deal_summary() 
                for event in sorted(events.events, key=lambda x: x.amount_raised, reverse=True)[:5]
            ]
        }
    
    def export_for_weekly_report(self, events: FundingEventCollection) -> str:
        """Generate formatted weekly deal report for VC associates"""
        if not events.events:
            return "No new deals this week."
        
        # Sort by date and amount
        sorted_events = sorted(
            events.events, 
            key=lambda x: (x.published_date, x.amount_raised), 
            reverse=True
        )
        
        report = f"Weekly VC Deal Report - Climate Tech\n"
        report += f"=====================================\n\n"
        
        # Executive summary
        total_deals = len(sorted_events)
        total_funding = sum(e.amount_raised for e in sorted_events)
        
        report += f"Executive Summary:\n"
        report += f"• {total_deals} new deals tracked\n"
        report += f"• ${total_funding:.1f}M total funding\n"
        report += f"• Average deal size: ${total_funding/total_deals:.1f}M\n\n"
        
        # Deals by sector
        grid_deals = [e for e in sorted_events if e.subsector == "Grid Modernization"]
        carbon_deals = [e for e in sorted_events if e.subsector == "Carbon Capture"]
        
        if grid_deals:
            report += f"Grid Modernization ({len(grid_deals)} deals):\n"
            for event in grid_deals:
                report += f"• {event.get_deal_summary()}\n"
            report += "\n"
        
        if carbon_deals:
            report += f"Carbon Capture ({len(carbon_deals)} deals):\n"
            for event in carbon_deals:
                report += f"• {event.get_deal_summary()}\n"
            report += "\n"
        
        # Notable investors
        investors = {}
        for event in sorted_events:
            investors[event.lead_investor] = investors.get(event.lead_investor, 0) + 1
        
        active_investors = sorted(investors.items(), key=lambda x: x[1], reverse=True)[:5]
        
        report += f"Most Active Investors:\n"
        for investor, count in active_investors:
            report += f"• {investor}: {count} deal{'s' if count > 1 else ''}\n"
        
        return report
    
    def detect_market_signals(self, events: FundingEventCollection) -> Dict:
        """Detect market signals and trends for VC intelligence"""
        if len(events.events) < 5:
            return {'signals': [], 'trends': [], 'note': 'Insufficient data for signal detection'}
        
        signals = []
        trends = []
        
        # Convert to DataFrame for analysis
        df = events.to_dataframe()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        if df.empty:
            return {'signals': [], 'trends': [], 'note': 'No valid date data'}
        
        # Recent activity surge
        recent_30d = df[df['date'] >= (datetime.now() - timedelta(days=30))]
        previous_30d = df[(df['date'] >= (datetime.now() - timedelta(days=60))) & 
                         (df['date'] < (datetime.now() - timedelta(days=30)))]
        
        if len(recent_30d) > len(previous_30d) * 1.5:
            signals.append("Deal activity surge in last 30 days")
        
        # Large deal detection
        avg_amount = df['amount'].mean()
        large_deals = df[df['amount'] > avg_amount * 2]
        if len(large_deals) > 0:
            signals.append(f"{len(large_deals)} unusually large deals detected")
        
        # Investor concentration
        investor_counts = df['lead_investor'].value_counts()
        if len(investor_counts) > 0 and investor_counts.iloc[0] > len(df) * 0.3:  # One investor > 30% of deals
            signals.append(f"High investor concentration: {investor_counts.index[0]} very active")
        
        # Sector trends
        sector_counts = df['sector'].value_counts()
        if len(sector_counts) >= 2:
            dominant_sector = sector_counts.index[0]
            if sector_counts.iloc[0] > sector_counts.iloc[1] * 1.5:
                trends.append(f"{dominant_sector} deals dominating ({sector_counts.iloc[0]} vs {sector_counts.iloc[1]})")
        elif len(sector_counts) == 1:
            dominant_sector = sector_counts.index[0]
            trends.append(f"{dominant_sector} is the only active sector ({sector_counts.iloc[0]} deals)")
        
        # Stage trends
        stage_counts = df['stage'].value_counts()
        if 'Series A' in stage_counts.index and 'Seed' in stage_counts.index:
            if stage_counts['Series A'] > stage_counts['Seed'] * 1.2:
                trends.append("Series A deals outpacing Seed rounds")
            elif stage_counts['Seed'] > stage_counts['Series A'] * 1.2:
                trends.append("Seed activity higher than Series A")
        
        return {
            'signals': signals,
            'trends': trends,
            'analysis_period': f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}",
            'data_points': len(df)
        }