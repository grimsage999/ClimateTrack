# main.py (v2 - Refactored for focused CTVC scraper)

import streamlit as st
import time
from datetime import datetime

# Import our single, powerful scraper
from sources.scraper import scrape_ctvc_deals 

# Core and Data components
from core.funding_event import FundingEventCollection
from data.data_manager import DataManager
from data.vc_sample_data import create_focused_vc_sample_data
from ui.dashboard import VCDashboard

def initialize_app():
    """Initialize application components"""
    data_manager = DataManager()
    dashboard = VCDashboard()
    return {'data_manager': data_manager, 'dashboard': dashboard}

def ingest_funding_data(data_manager) -> FundingEventCollection:
    """
    Simplified data ingestion workflow for CTVC.
    """
    with st.spinner("Scanning CTVC for the latest climate tech deals..."):
        # --- CHANGE: Pass the data_manager instance to the scraper ---
        new_deals_data = scrape_ctvc_deals(data_manager, pages_to_load=2)
    
    if not new_deals_data:
        st.warning("No new deals found in this scan.")
        # Reload existing data to refresh the view
        return load_existing_data(data_manager)
    
    with st.spinner("Storing validated deals..."):
        data_manager.save_funding_data(new_deals_data)
        st.success(f"✅ Found and saved {len(new_deals_data)} new VC deals!")
    
    # Return all data, including the new deals, to update the dashboard
    return load_existing_data(data_manager)

def load_existing_data(data_manager) -> FundingEventCollection:
    """Load existing funding data from storage"""
    try:
        df = data_manager.load_funding_data()
        if df.empty:
            return FundingEventCollection([])
        
        events = []
        for _, row in df.iterrows():
            try:
                from core.funding_event import FundingEvent
                # We can simplify this since our data is cleaner now
                event = FundingEvent.from_dict(row.to_dict())
                events.append(event)
            except Exception:
                continue
        
        return FundingEventCollection(events)
        
    except Exception as e:
        st.error(f"Error loading existing data: {str(e)}")
        return FundingEventCollection([])

def main():
    """Main application entry point"""
    components = initialize_app()
    data_manager = components['data_manager']
    dashboard = components['dashboard']
    
    # Handle user actions
    if st.session_state.get('refresh_data'):
        events = ingest_funding_data(data_manager)
        del st.session_state['refresh_data']
    elif st.session_state.get('load_sample'):
        with st.spinner("Loading focused VC sample data..."):
            sample_events_data = create_focused_vc_sample_data()
            data_manager.save_funding_data(sample_events_data)
            st.success("✅ Loaded 10 focused VC deals")
        events = load_existing_data(data_manager)
        del st.session_state['load_sample']
    else:
        events = load_existing_data(data_manager)
    
    # Render dashboard
    dashboard.render(events)

if __name__ == "__main__":
    main()