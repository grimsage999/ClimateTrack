# main.py (v7 - Unified State Management with Enhanced Analytics)

import streamlit as st
import time
import os
from datetime import datetime

# Enhanced modules for advanced analytics
from sources.data_source_integration import MultiSourceDataIntegrator
from core.enhanced_predictive_analytics import EnhancedPredictiveAnalytics
from core.investor_intelligence import InvestorIntelligence

# Core scraper and data components
from sources.scraper import scrape_ctvc_deals 
from core.funding_event import FundingEvent, FundingEventCollection
from data.data_manager import DataManager
from data.vc_sample_data import create_focused_vc_sample_data
from ui.dashboard import VCDashboard

def initialize_app():
    """Initialize enhanced application components"""
    data_manager = DataManager()
    dashboard = VCDashboard()
    
    # Enhanced analytics modules
    data_integrator = MultiSourceDataIntegrator()
    predictive_analytics = EnhancedPredictiveAnalytics()
    investor_intelligence = InvestorIntelligence()
    
    return {
        'data_manager': data_manager, 
        'dashboard': dashboard,
        'data_integrator': data_integrator,
        'predictive_analytics': predictive_analytics,
        'investor_intelligence': investor_intelligence
    }

def ingest_funding_data_basic(data_manager):
    """
    Basic data ingestion workflow using CTVC scraper with real-time UI feedback.
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

def ingest_funding_data_enhanced(data_manager, data_integrator) -> FundingEventCollection:
    """
    Enhanced multi-source data ingestion workflow for comprehensive deal discovery
    """
    with st.spinner("Collecting data from multiple sources (web scraping, SEC EDGAR, APIs)..."):
        # Use enhanced multi-source data integrator
        comprehensive_data = data_integrator.collect_comprehensive_funding_data(lookback_days=90)
        new_deals_data = comprehensive_data.get('funding_data', [])
    
    if not new_deals_data:
        st.warning("No new deals found in this scan.")
        # Reload existing data to refresh the view
        return load_existing_data(data_manager)
    
    with st.spinner("Storing validated deals..."):
        data_manager.save_funding_data(new_deals_data)
        st.success(f"✅ Added {len(new_deals_data)} new deals from multiple sources")
    
    return load_existing_data(data_manager)

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
    """Enhanced main application entry point with advanced analytics"""
    components = initialize_app()
    data_manager = components['data_manager']
    dashboard = components['dashboard']
    data_integrator = components['data_integrator']
    predictive_analytics = components['predictive_analytics']
    investor_intelligence = components['investor_intelligence']
    
    # Set up sidebar controls
    with st.sidebar:
        st.header("Deal Flow Controls")
        st.subheader("⚡ Data Collection")
        
        # Basic data collection
        if st.button("🔎 Find New Deals (CTVC)", type="primary", key="sidebar_refresh_basic",
                    help="Scans CTVC for the latest funding deals. Stops after finding up to 15 new deals."):
            st.session_state['action'] = 'refresh_basic'
            st.rerun()
        
        # Enhanced data collection
        if st.button("🚀 Enhanced Multi-Source Scan", key="sidebar_refresh_enhanced",
                    help="Comprehensive scan using multiple data sources including APIs and SEC filings."):
            st.session_state['action'] = 'refresh_enhanced'
            st.rerun()
        
        # Sample data
        if st.button("📋 Load VC Sample Data", key="sidebar_sample"):
            st.session_state['action'] = 'load_sample'
            st.rerun()

        st.subheader("🧠 Advanced Analytics")
        if st.button("📊 Run Enhanced Analytics", key="sidebar_analytics",
                    help="Perform predictive analytics, competitive analysis, and investor intelligence."):
            st.session_state['action'] = 'run_analytics'
            st.rerun()

        # Danger zone
        st.subheader("⚠️ Danger Zone")
        if st.button("🗑️ Clear All Data", help="Deletes the local CSV and log files to start fresh."):
            st.session_state['action'] = 'clear_data'
            st.rerun()

    # Execute actions based on session state
    events = None
    
    if st.session_state.get('action') == 'refresh_basic':
        del st.session_state['action']
        ingest_funding_data_basic(data_manager)
        st.rerun()
    
    elif st.session_state.get('action') == 'refresh_enhanced':
        del st.session_state['action']
        events = ingest_funding_data_enhanced(data_manager, data_integrator)
    
    elif st.session_state.get('action') == 'load_sample':
        del st.session_state['action']
        with st.spinner("Loading focused VC sample data..."):
            sample_events_data = create_focused_vc_sample_data()
            data_manager.save_funding_data(sample_events_data)
            st.success("✅ Loaded 10 focused VC deals")
        st.rerun()

    elif st.session_state.get('action') == 'run_analytics':
        del st.session_state['action']
        events = load_existing_data(data_manager)
        
        # Run enhanced analytics
        with st.spinner("Running enhanced predictive analytics and investor intelligence..."):
            df = events.to_dataframe()
            
            # Enhanced forecasting
            forecast_results = predictive_analytics.enhanced_funding_forecast(df)
            
            # Competitive analysis  
            competitive_analysis = predictive_analytics.competitive_landscape_analysis(df)
            
            # Investor ecosystem analysis
            investor_analysis = investor_intelligence.analyze_investor_ecosystem(df)
            
            # Store results in session state
            st.session_state['enhanced_results'] = {
                'forecast': forecast_results,
                'competitive': competitive_analysis,
                'investor': investor_analysis
            }
            
            st.success("✅ Enhanced analytics complete")

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

    # Always load existing data if not already loaded
    if events is None:
        events = load_existing_data(data_manager)
    
    # Pass enhanced components to dashboard
    dashboard.render(events, enhanced_components={
        'predictive_analytics': predictive_analytics,
        'investor_intelligence': investor_intelligence,
        'data_integrator': data_integrator
    })

if __name__ == "__main__":
    main()