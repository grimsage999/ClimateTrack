# main.py (v2 - Refactored for focused CTVC scraper)

import streamlit as st
import time
from datetime import datetime

# Enhanced modules for advanced analytics
from sources.data_source_integration import MultiSourceDataIntegrator
from core.enhanced_predictive_analytics import EnhancedPredictiveAnalytics
from core.investor_intelligence import InvestorIntelligence

# Core and Data components
from core.funding_event import FundingEventCollection
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

def ingest_funding_data(data_manager, data_integrator) -> FundingEventCollection:
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
    """Enhanced main application entry point with advanced analytics"""
    components = initialize_app()
    data_manager = components['data_manager']
    dashboard = components['dashboard']
    data_integrator = components['data_integrator']
    predictive_analytics = components['predictive_analytics']
    investor_intelligence = components['investor_intelligence']
    
    # Handle user actions
    if st.session_state.get('refresh_data'):
        events = ingest_funding_data(data_manager, data_integrator)
        del st.session_state['refresh_data']
    elif st.session_state.get('load_sample'):
        with st.spinner("Loading focused VC sample data..."):
            sample_events_data = create_focused_vc_sample_data()
            data_manager.save_funding_data(sample_events_data)
            st.success("✅ Loaded 10 focused VC deals")
        events = load_existing_data(data_manager)
        del st.session_state['load_sample']
    elif st.session_state.get('run_enhanced_analytics'):
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
        del st.session_state['run_enhanced_analytics']
    else:
        events = load_existing_data(data_manager)
    
    # Pass enhanced components to dashboard
    dashboard.render(events, enhanced_components={
        'predictive_analytics': predictive_analytics,
        'investor_intelligence': investor_intelligence,
        'data_integrator': data_integrator
    })

if __name__ == "__main__":
    main()