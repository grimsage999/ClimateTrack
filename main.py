# main.py (v6 - Definitive State Management Fix)

import streamlit as st
import time
import os # <-- NEW IMPORT
from datetime import datetime

from sources.scraper import scrape_ctvc_deals 
from core.funding_event import FundingEvent, FundingEventCollection
from data.data_manager import DataManager
from data.vc_sample_data import create_focused_vc_sample_data
from ui.dashboard import VCDashboard

def initialize_app():
    """Initialize application components"""
    data_manager = DataManager()
    dashboard = VCDashboard()
    return {'data_manager': data_manager, 'dashboard': dashboard}

def ingest_funding_data(data_manager):
    """
    Data ingestion workflow that consumes the scraper's generator for real-time UI feedback.
    """
    new_deals_data = []
    deals_found_count = 0
    with st.status("Scanning for the latest climate tech deals...", expanded=True) as status:
        status.write("🕵️  Initializing CTVC scan...")
        
        for deal in scrape_ctvc_deals(data_manager, pages_to_load=3, target_deal_count=15):
            new_deals_data.append(deal)
            deals_found_count += 1
            status.update(label=f"Scan in progress... Found {deals_found_count} deals. Latest: **{deal.get('company')}**")

        if not new_deals_data:
            status.update(label="Scan complete. No new deals found.", state="complete", expanded=False)
            time.sleep(2)
            return
        
        status.write(f"💾 Saving {len(new_deals_data)} new deals to database...")
        data_manager.save_funding_data(new_deals_data)
        status.update(label=f"Success! Added {len(new_deals_data)} new deals.", state="complete", expanded=False)
        time.sleep(2)

def load_existing_data(data_manager) -> FundingEventCollection:
    """Load existing funding data from storage"""
    try:
        df = data_manager.load_funding_data()
        if df.empty:
            return FundingEventCollection([])
        
        events = [FundingEvent.from_dict(row.to_dict()) for _, row in df.iterrows()]
        return FundingEventCollection(events)
        
    except Exception as e:
        st.error(f"Error loading existing data: {e}")
        return FundingEventCollection([])

def main():
    """Main application entry point"""
    components = initialize_app()
    data_manager = components['data_manager']
    dashboard = components['dashboard']
    
    # --- This is a much cleaner control flow ---

    # 1. Set up sidebar and session state flags
    with st.sidebar:
        st.header("Deal Flow Controls")
        st.subheader("⚡ Data Collection")
        
        if st.button("🔎 Find New Deals", type="primary", key="sidebar_refresh",
                    help="Scans CTVC for the latest funding deals. Stops after finding up to 15 new deals."):
            st.session_state['action'] = 'refresh'
            st.rerun()
        
        if st.button("📋 Load VC Sample Data", key="sidebar_sample"):
            st.session_state['action'] = 'load_sample'
            st.rerun()

        # --- THE NEW DEBUGGING TOOL ---
        st.subheader("⚠️ Danger Zone")
        if st.button("🗑️ Clear All Data", help="Deletes the local CSV and log files to start fresh."):
            st.session_state['action'] = 'clear_data'
            st.rerun()

    # 2. Execute actions based on flags
    if st.session_state.get('action') == 'refresh':
        del st.session_state['action'] # Consume the flag
        ingest_funding_data(data_manager)
        st.rerun() # Force a final rerun to load the newly saved data
    
    elif st.session_state.get('action') == 'load_sample':
        del st.session_state['action']
        with st.spinner("Loading focused VC sample data..."):
            sample_events_data = create_focused_vc_sample_data()
            data_manager.save_funding_data(sample_events_data)
            st.success("✅ Loaded 10 focused VC deals")
        st.rerun()

    elif st.session_state.get('action') == 'clear_data':
        del st.session_state['action']
        try:
            # Manually delete the files
            if os.path.exists(data_manager.funding_file):
                os.remove(data_manager.funding_file)
            if os.path.exists(data_manager.processed_urls_file):
                os.remove(data_manager.processed_urls_file)
            st.success("✅ All local data cleared successfully!")
            time.sleep(2)
        except Exception as e:
            st.error(f"Error clearing data: {e}")
        st.rerun()

    # 3. Always load data and render the dashboard on every run
    events = load_existing_data(data_manager)
    dashboard.render(events)

if __name__ == "__main__":
    main()