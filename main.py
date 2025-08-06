"""
Climate VC Deal Flow Intelligence - Main Entry Point
Orchestrates the complete VC deal discovery and analysis workflow
"""

import streamlit as st
import time
from datetime import datetime

# Core components
from core.funding_event import FundingEventCollection
from core.extractor import FundingDataExtractor  
from core.processor import VCDealProcessor

# Data sources
from sources.scraper import FundingScraper
from sources.api_client import EnhancedFundingClient

# UI components
from ui.dashboard import VCDashboard

# Data management
from data.data_manager import DataManager
from data.vc_sample_data import create_focused_vc_sample_data

def initialize_app():
    """Initialize application components"""
    
    # Initialize core components
    extractor = FundingDataExtractor()
    processor = VCDealProcessor()
    scraper = FundingScraper()
    data_manager = DataManager()
    dashboard = VCDashboard()
    
    return {
        'extractor': extractor,
        'processor': processor, 
        'scraper': scraper,
        'data_manager': data_manager,
        'dashboard': dashboard
    }

def ingest_funding_data(scraper, extractor, data_manager) -> FundingEventCollection:
    """
    Main data ingestion workflow:
    1. Scrape raw funding news
    2. Extract structured insights with AI
    3. Filter to relevant VC deals
    4. Store validated events
    """
    
    # Scrape raw funding news
    with st.spinner("Scanning funding news sources..."):
        raw_events = scraper.scrape_all_sources()
    
    if not raw_events:
        st.warning("No new funding events found from sources")
        return FundingEventCollection([])
    
    # Extract structured insights with AI
    with st.spinner("Extracting deal insights with AI..."):
        extracted_events = extractor.batch_extract_events(raw_events)
    
    if not extracted_events:
        st.warning("No valid VC deals extracted from raw data")
        return FundingEventCollection([])
    
    # Create event collection
    events = FundingEventCollection(extracted_events)
    
    # Store validated events
    with st.spinner("Storing validated deals..."):
        saved_count = 0
        for event in events.events:
            if data_manager.add_funding_event(event.to_dict()):
                saved_count += 1
        
        if saved_count > 0:
            st.success(f"✅ Added {saved_count} new VC deals to database")
        else:
            st.info("No new unique deals to save")
    
    return events

def load_existing_data(data_manager) -> FundingEventCollection:
    """Load existing funding data from storage"""
    
    try:
        # Load raw data
        raw_data = data_manager.load_funding_data()
        
        if not raw_data:
            return FundingEventCollection([])
        
        # Convert to FundingEvent objects
        events = []
        for item in raw_data:
            try:
                from core.funding_event import FundingEvent
                event = FundingEvent.from_dict(item)
                if event.is_valid_vc_deal():
                    events.append(event)
            except Exception as e:
                continue  # Skip invalid events
        
        return FundingEventCollection(events)
        
    except Exception as e:
        st.error(f"Error loading existing data: {str(e)}")
        return FundingEventCollection([])

def handle_user_actions(components) -> FundingEventCollection:
    """Handle user actions and return appropriate event collection"""
    
    extractor = components['extractor']
    processor = components['processor']
    scraper = components['scraper']
    data_manager = components['data_manager']
    
    # Check for user actions in session state
    if st.session_state.get('load_sample'):
        # Load sample VC data
        with st.spinner("Loading focused VC sample data..."):
            sample_events = create_focused_vc_sample_data()
            
            # Save sample data
            for event_data in sample_events:
                data_manager.add_funding_event(event_data)
            
            st.success("✅ Loaded 10 focused VC deals")
            
            # Convert to event collection
            events = []
            for item in sample_events:
                from core.funding_event import FundingEvent
                event = FundingEvent.from_dict(item)
                events.append(event)
            
            # Clear session state
            del st.session_state['load_sample']
            
            return FundingEventCollection(events)
    
    elif st.session_state.get('refresh_data'):
        # Refresh data from sources
        events = ingest_funding_data(scraper, extractor, data_manager)
        
        # Clear session state
        del st.session_state['refresh_data']
        
        return events
    
    else:
        # Load existing data
        return load_existing_data(data_manager)

def main():
    """
    Main application entry point
    Orchestrates the complete VC deal flow intelligence workflow
    """
    
    # Initialize application
    components = initialize_app()
    dashboard = components['dashboard']
    
    # Handle user actions and get event data
    events = handle_user_actions(components)
    
    # Render dashboard with events
    dashboard.render(events)
    
    # Handle sidebar actions
    if st.sidebar.button("🔄 Enhanced Scan"):
        st.session_state['refresh_data'] = True
        st.rerun()
    
    if st.sidebar.button("📋 Load VC Sample Data"):
        st.session_state['load_sample'] = True
        st.rerun()
    
    # Export functionality
    if events.get_deal_count() > 0:
        if st.sidebar.button("📊 Export Weekly Report"):
            processor = components['processor']
            report = processor.export_for_weekly_report(events)
            
            st.sidebar.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"vc_weekly_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30 min)", value=False)
    
    if auto_refresh:
        time.sleep(1800)  # 30 minutes
        st.rerun()

if __name__ == "__main__":
    main()