"""
Interactive filters for VC deal flow dashboard
Provides sector, stage, date, and amount filtering controls
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from core.funding_event import FundingEventCollection
import pandas as pd 
class DealFilters:
    """
    Interactive filter controls for VC deal analysis
    Focused on Grid Modernization & Carbon Capture criteria
    """
    
    def __init__(self):
        self.target_subsectors = ["Grid Modernization", "Carbon Capture"]
        self.target_stages = ["Seed", "Series A"]
    
    def render_filter_controls(self, events: FundingEventCollection) -> Dict:
        """Render all filter controls and return filter configuration"""
        
        filter_config = {}
        
        # Subsector filter
        filter_config['subsector'] = self._render_subsector_filter()
        
        # Funding stage filter  
        filter_config['stage'] = self._render_stage_filter()
        
        # Date range filter
        filter_config['date_range'] = self._render_date_filter()
        
        # Amount range filter
        filter_config['amount_range'] = self._render_amount_filter(events)
        
        # Lead investor filter
        filter_config['investor'] = self._render_investor_filter(events)
        
        # Reset filters button
        if st.button("🔄 Reset All Filters"):
            self._reset_filters()
            st.rerun()
        
        return filter_config
    
    def _render_subsector_filter(self) -> Optional[str]:
        """Render subsector selection filter"""
        subsector_options = ["All"] + self.target_subsectors
        
        selected_subsector = st.selectbox(
            "🏭 Subsector Focus",
            options=subsector_options,
            index=0,
            help="Filter deals by climate tech subsector"
        )
        
        return selected_subsector if selected_subsector != "All" else None
    
    def _render_stage_filter(self) -> Optional[str]:
        """Render funding stage selection filter"""
        stage_options = ["All"] + self.target_stages
        
        selected_stage = st.selectbox(
            "💰 Funding Stage",
            options=stage_options,
            index=0,
            help="Filter deals by funding stage"
        )
        
        return selected_stage if selected_stage != "All" else None
    
    def _render_date_filter(self) -> Optional[Tuple[datetime, datetime]]:
        """Render date range filter"""
        st.markdown("📅 **Date Range**")
        
        # Default to last 6 months
        default_start = datetime.now() - timedelta(days=180)
        default_end = datetime.now()
        
        # Date range selector - split into separate inputs to avoid conflicts
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=default_start.date(),
                min_value=datetime(2020, 1, 1).date(),
                max_value=datetime.now().date(),
                key="filter_start_date"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=default_end.date(),
                min_value=datetime(2020, 1, 1).date(),
                max_value=datetime.now().date(),
                key="filter_end_date"
            )
        
        # Handle the date input return values properly
        if start_date and end_date:
            return (datetime.combine(start_date, datetime.min.time()),
                   datetime.combine(end_date, datetime.max.time()))
        
        return None
    
    def _render_amount_filter(self, events: FundingEventCollection) -> Optional[Tuple[float, float]]:
        """Render funding amount range filter"""
        if events.get_deal_count() == 0:
            return None
        
        st.markdown("💵 **Funding Amount Range ($M)**")
        
        # Get min/max from data
        amounts = [event.amount_raised for event in events.events if event.amount_raised > 0]
        
        if not amounts:
            return None
        
        min_amount = min(amounts)
        max_amount = max(amounts)
        
        # Create reasonable defaults
        default_min = max(0.5, min_amount)  # At least $500K
        default_max = min(100, max_amount)  # Max $100M for early stage
        
        # Slider for amount range
        amount_range = st.slider(
            "Amount range",
            min_value=float(min_amount),
            max_value=float(max_amount),
            value=(float(default_min), float(default_max)),
            step=0.5,
            help="Filter deals by funding amount"
        )
        
        return amount_range
# In ui/filters.py

    def _render_investor_filter(self, events: FundingEventCollection) -> Optional[str]:
        """Render lead investor filter"""
        if events.get_deal_count() == 0:
            return None
        
        investors = events.get_unique_investors()
        
        if not investors:
            return None
        
        # --- THIS IS THE FIX ---
        # Convert all items to strings to prevent sorting errors with mixed types (str and float/NaN)
        investors = sorted([str(i) for i in investors if pd.notna(i)])
        # --- END FIX ---

        investor_options = ["All"] + investors
        
        selected_investor = st.selectbox(
            "🏢 Lead Investor",
            options=investor_options,
            index=0,
            help="Filter deals by lead investor"
        )
        
        return selected_investor if selected_investor != "All" else None
    
    def _reset_filters(self):
        """Reset all filters to default values"""
        # Clear any session state filter values
        filter_keys = [
            'subsector_filter',
            'stage_filter', 
            'date_filter',
            'amount_filter',
            'investor_filter'
        ]
        
        for key in filter_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_active_filter_summary(self, filter_config: Dict) -> str:
        """Generate summary of active filters for display"""
        active_filters = []
        
        if filter_config.get('subsector'):
            active_filters.append(f"Subsector: {filter_config['subsector']}")
        
        if filter_config.get('stage'):
            active_filters.append(f"Stage: {filter_config['stage']}")
        
        if filter_config.get('date_range'):
            start_date, end_date = filter_config['date_range']
            active_filters.append(f"Date: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        if filter_config.get('amount_range'):
            min_amt, max_amt = filter_config['amount_range']
            active_filters.append(f"Amount: ${min_amt:.1f}M - ${max_amt:.1f}M")
        
        if filter_config.get('investor'):
            active_filters.append(f"Investor: {filter_config['investor']}")
        
        if not active_filters:
            return "No active filters"
        
        return " | ".join(active_filters)
    
    def export_filter_config(self, filter_config: Dict) -> Dict:
        """Export filter configuration for saving/sharing"""
        export_config = {}
        
        for key, value in filter_config.items():
            if key == 'date_range' and value:
                start_date, end_date = value
                export_config[key] = {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            else:
                export_config[key] = value
        
        return export_config

class QuickFilters:
    """Pre-configured quick filter options for common VC use cases"""
    
    @staticmethod
    def get_recent_deals_filter() -> Dict:
        """Filter for deals in last 30 days"""
        return {
            'date_range': (
                datetime.now() - timedelta(days=30),
                datetime.now()
            )
        }
    
    @staticmethod  
    def get_large_deals_filter() -> Dict:
        """Filter for Series A deals > $10M"""
        return {
            'stage': 'Series A',
            'amount_range': (10.0, 100.0)
        }
    
    @staticmethod
    def get_grid_modernization_filter() -> Dict:
        """Filter for Grid Modernization focus"""
        return {
            'subsector': 'Grid Modernization'
        }
    
    @staticmethod
    def get_carbon_capture_filter() -> Dict:
        """Filter for Carbon Capture focus"""  
        return {
            'subsector': 'Carbon Capture'
        }
    
    @staticmethod
    def get_seed_focus_filter() -> Dict:
        """Filter for Seed stage deals"""
        return {
            'stage': 'Seed',
            'amount_range': (0.5, 10.0)
        }
    
    @staticmethod
    def render_quick_filter_buttons() -> Optional[Dict]:
        """Render quick filter buttons and return selected filter"""
        st.markdown("⚡ **Quick Filters**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📅 Recent (30d)"):
                return QuickFilters.get_recent_deals_filter()
            
            if st.button("⚡ Grid Modernization"):
                return QuickFilters.get_grid_modernization_filter()
            
            if st.button("🌱 Seed Focus"):
                return QuickFilters.get_seed_focus_filter()
        
        with col2:
            if st.button("💰 Large Deals (>$10M)"):
                return QuickFilters.get_large_deals_filter()
            
            if st.button("🏭 Carbon Capture"):
                return QuickFilters.get_carbon_capture_filter()
        
        return None