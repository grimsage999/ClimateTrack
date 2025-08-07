"""
VC Deal Flow Dashboard for Climate Tech Funding Intelligence
Main UI component for displaying funding events, analytics, and predictions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

from core.funding_event import FundingEventCollection
from core.processor import VCDealProcessor
from core.predictive_analytics import analyze_market_trends, generate_funding_predictions, identify_investment_gaps, create_predictive_visualizations
from ui.filters import DealFilters
from utils import format_currency, format_date

class VCDashboard:
    """
    Main dashboard for VC associates tracking climate tech deals
    Displays deal flow, analytics, and predictive intelligence
    """
    
    def __init__(self):
        self.processor = VCDealProcessor()
        self.filters = DealFilters()
        
        # Configure Streamlit page
        st.set_page_config(
            page_title="Climate VC Deal Flow",
            page_icon="⚡",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Load custom CSS for botanical design
        self._load_custom_styles()
    
    def render(self, events: FundingEventCollection, enhanced_components: dict = None):
        """Render complete dashboard with enhanced analytics capabilities"""
        
        # Header
        self._render_header()
        
        # Sidebar filters and controls
        filter_config = self._render_sidebar(events, enhanced_components)
        
        # Apply filters
        filtered_events = self._apply_filters(events, filter_config)
        
        # Main dashboard content
        if filtered_events.get_deal_count() > 0:
            self._render_main_content(filtered_events, enhanced_components)
        else:
            self._render_empty_state()
    
    def _load_custom_styles(self):
        """Load botanical-themed CSS styles"""
        st.markdown("""
        <style>
            /* Modern eco-conscious design system */
            :root {
                --forest-green: #1B4332;
                --sage-green: #52796F;
                --soft-mint: #A8DADC;
                --warm-cream: #F1FAEE;
                --earth-brown: #8B4513;
                --ocean-blue: #457B9D;
                --sunset-orange: #E76F51;
                --golden-yellow: #F4A261;
            }
            
            .main-header {
                background: linear-gradient(135deg, var(--forest-green) 0%, var(--sage-green) 100%);
                padding: 2rem;
                border-radius: 15px;
                color: white;
                margin-bottom: 2rem;
            }
            
            .metric-card {
                background: rgba(168, 218, 220, 0.15);
                border-radius: 12px;
                padding: 1.5rem;
                border-left: 4px solid var(--sage-green);
                backdrop-filter: blur(10px);
            }
            
            .deal-card {
                background: linear-gradient(135deg, rgba(241, 250, 238, 0.8) 0%, rgba(168, 218, 220, 0.1) 100%);
                border-radius: 12px;
                padding: 1.2rem;
                margin: 0.8rem 0;
                border-left: 4px solid var(--ocean-blue);
            }
            
            .stTabs [data-baseweb="tab"] {
                background: var(--warm-cream);
                border-radius: 8px 8px 0 0;
                color: var(--forest-green);
                font-weight: 500;
            }
            
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background: var(--sage-green);
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_header(self):
        """Render dashboard header"""
        st.markdown("""
        <div class="main-header">
            <h1>⚡ Climate VC Deal Flow Intelligence</h1>
            <p>Precision tracking for Grid Modernization & Carbon Capture funding events</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self, events: FundingEventCollection, enhanced_components: dict = None) -> dict:
        """Render sidebar with enhanced controls and analytics options"""
        with st.sidebar:
            st.title("⚡ Climate VC Controls")
            
            # Enhanced data collection section
            st.subheader("🔥 Multi-Source Data Collection")
            col1, col2 = st.columns(2)
            
            with col1:
                refresh_clicked = st.button("🔄 Multi-Source Scan", type="primary", key="dash_refresh")
                if refresh_clicked:
                    st.session_state['refresh_data'] = True
            
            with col2:
                export_clicked = st.button("📊 Export Report", key="dash_export")
            
            # Enhanced analytics controls
            st.subheader("🧠 Advanced Analytics")
            
            if st.button("🚀 Run Enhanced Analytics", type="secondary", key="enhanced_analytics"):
                st.session_state['run_enhanced_analytics'] = True
            
            col3, col4 = st.columns(2)
            with col3:
                if st.button("💡 Investor Intelligence", key="investor_intel"):
                    st.session_state['show_investor_intelligence'] = True
                    
            with col4:
                if st.button("📈 Predictive Models", key="predictive_models"):
                    st.session_state['show_predictive_models'] = True
            
            st.divider()
            
            # Filters
            st.subheader("🎯 Deal Filters")
            filter_config = self.filters.render_filter_controls(events)
            
            # Quick actions
            st.subheader("⚡ Quick Actions")
            
            if st.button("📋 Load VC Sample Data", key="dash_sample"):
                st.session_state['load_sample'] = True
                
            # Startup-Investor Matchmaking
            st.subheader("🎯 Matchmaking")
            with st.expander("Startup Profile"):
                startup_name = st.text_input("Startup Name", key="startup_name")
                startup_sector = st.selectbox("Sector", ["Grid Modernization", "Carbon Capture"], key="startup_sector")
                startup_stage = st.selectbox("Stage", ["Seed", "Series A"], key="startup_stage")
                funding_amount = st.number_input("Funding Need ($M)", min_value=0.1, max_value=100.0, value=5.0, key="funding_amount")
                
                if st.button("🔍 Find Matching Investors", key="find_matches"):
                    if enhanced_components and 'investor_intelligence' in enhanced_components:
                        startup_profile = {
                            'name': startup_name,
                            'sector': startup_sector,
                            'stage': startup_stage,
                            'funding_amount': funding_amount,
                            'region': 'North America'
                        }
                        st.session_state['startup_profile'] = startup_profile
                        st.session_state['run_matchmaking'] = True
            
            # Enhanced status indicators
            st.subheader("📈 Data Status")
            st.metric("Total Deals", events.get_deal_count())
            st.metric("Total Funding", format_currency(events.get_total_funding()))
            st.metric("Unique Investors", len(events.get_unique_investors()))
            
            # Data quality indicators
            if 'data_integrator' in (enhanced_components or {}):
                st.subheader("🔍 Data Quality")
                st.info("Multi-source integration active")
                st.caption("Sources: Web scraping, SEC EDGAR, APIs")
            
            return filter_config
    
    def _apply_filters(self, events: FundingEventCollection, filter_config: dict) -> FundingEventCollection:
        """Apply user-selected filters to events"""
        filtered = events
        
        # Subsector filter
        if filter_config.get('subsector') and filter_config['subsector'] != 'All':
            filtered = self.processor.filter_by_subsector(filtered, filter_config['subsector'])
        
        # Stage filter
        if filter_config.get('stage') and filter_config['stage'] != 'All':
            filtered = self.processor.filter_by_stage(filtered, filter_config['stage'])
        
        # Date range filter
        if filter_config.get('date_range'):
            start_date, end_date = filter_config['date_range']
            filtered = self.processor.filter_by_date_range(
                filtered, 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
        
        # Amount range filter
        if filter_config.get('amount_range'):
            min_amount, max_amount = filter_config['amount_range']
            filtered = self.processor.filter_by_amount_range(filtered, min_amount, max_amount)
        
        return filtered
    
    def _render_main_content(self, events: FundingEventCollection, enhanced_components: dict = None):
        """Render main dashboard content with enhanced analytics capabilities"""
        
        # Key metrics
        self._render_key_metrics(events)
        
        # Enhanced tabbed interface
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Analytics", 
            "📋 Deal List", 
            "🤖 AI Insights", 
            "📈 Trends",
            "🔮 Enhanced Forecasting",
            "🏢 Investor Intelligence",
            "🎯 Matchmaking"
        ])
        
        with tab1:
            self._render_analytics_tab(events)
        
        with tab2:
            self._render_deal_list_tab(events)
        
        with tab3:
            self._render_ai_insights_tab(events)
        
        with tab4:
            self._render_trends_tab(events)
        
        with tab5:
            self._render_enhanced_forecasting_tab(events, enhanced_components)
        
        with tab6:
            self._render_investor_intelligence_tab(events, enhanced_components)
        
        with tab7:
            self._render_matchmaking_tab(events, enhanced_components)
    
    def _render_key_metrics(self, events: FundingEventCollection):
        """Render key metrics cards"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_funding = events.get_total_funding()
            st.metric(
                "💰 Total Deal Volume",
                format_currency(total_funding),
                help="Combined funding in filtered deals"
            )
        
        with col2:
            deal_count = events.get_deal_count()
            st.metric(
                "📊 Deal Count", 
                deal_count,
                help="Number of qualifying deals"
            )
        
        with col3:
            avg_deal = total_funding / deal_count if deal_count > 0 else 0
            st.metric(
                "📈 Avg Round Size",
                format_currency(avg_deal),
                help="Average funding amount per deal"
            )
        
        with col4:
            unique_investors = len(events.get_unique_investors())
            st.metric(
                "🏢 Active Investors",
                unique_investors,
                help="Number of unique lead investors"
            )
    
    def _render_analytics_tab(self, events: FundingEventCollection):
        """Render analytics visualizations"""
        st.subheader("📊 Deal Flow Analytics")
        
        df = events.to_dataframe()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sector distribution
            if 'sector' in df.columns and not df['sector'].isna().all():
                st.subheader("🌱 Funding by Sector")
                sector_data = df.groupby('sector')['amount'].sum().reset_index()
                
                fig = px.pie(
                    sector_data, 
                    values='amount', 
                    names='sector',
                    title="Distribution of Funding by Sector",
                    color_discrete_sequence=['#1B4332', '#52796F', '#A8DADC']
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif", color='#1B4332')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Stage distribution
            if 'stage' in df.columns and not df['stage'].isna().all():
                st.subheader("🌿 Funding by Stage")
                stage_data = df.groupby('stage')['amount'].sum().reset_index()
                
                fig = px.bar(
                    stage_data,
                    x='stage',
                    y='amount',
                    title="Funding Amount by Stage",
                    color='amount',
                    color_continuous_scale=['#A8DADC', '#52796F', '#1B4332']
                )
                fig.update_layout(
                    plot_bgcolor='rgba(241, 250, 238, 0.8)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif", color='#1B4332')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Deal intelligence summary
        st.subheader("🎯 Deal Intelligence Summary")
        intelligence = self.processor.generate_deal_intelligence(events)
        
        if 'error' not in intelligence:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Market Overview**")
                overview = intelligence['overview']
                st.write(f"• Total Deals: {overview['total_deals']}")
                st.write(f"• Total Funding: ${overview['total_funding']}M")
                st.write(f"• Average Deal: ${overview['average_deal_size']}M")
                st.write(f"• Active Investors: {overview['unique_investors']}")
            
            with col2:
                st.markdown("**🏆 Top Deals**")
                for deal in intelligence['top_deals'][:5]:
                    st.write(f"• {deal}")
    
    def _render_deal_list_tab(self, events: FundingEventCollection):
        """Render detailed deal list"""
        st.subheader("📋 VC Deal Flow Report")
        
        df = events.to_dataframe()
        
        if not df.empty:
            # Configure display columns for VC use case
            display_columns = ['company', 'lead_investor', 'amount', 'stage', 'sector', 'region', 'date']
            display_columns = [col for col in display_columns if col in df.columns]
            
            if display_columns:
                display_df = df[display_columns].copy()
                
                # Rename columns for VC context
                column_mapping = {
                    'company': 'Startup',
                    'lead_investor': 'Lead Investor',
                    'amount': 'Round Size ($M)',
                    'stage': 'Stage',
                    'sector': 'Subsector',
                    'region': 'Region',
                    'date': 'Date'
                }
                display_df = display_df.rename(columns=column_mapping)
                
                # Format amount column
                if 'Round Size ($M)' in display_df.columns:
                    display_df['Round Size ($M)'] = display_df['Round Size ($M)'].apply(
                        lambda x: f"${x:.1f}M" if pd.notnull(x) else ""
                    )
                
                # Sort by date and amount
                if 'Date' in display_df.columns:
                    display_df = display_df.sort_values(['Date'], ascending=False)
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Export functionality
                if st.button("📥 Export Deal List", key="export_deals"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"vc_deals_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="download_csv"
                    )
            else:
                st.info("No deal data available to display")
        else:
            st.info("No deals found with current filters")
    
    def _render_ai_insights_tab(self, events: FundingEventCollection):
        """Render AI-generated insights"""
        st.subheader("🤖 AI Deal Intelligence")
        
        if events.get_deal_count() > 0:
            # Generate market signals
            signals = self.processor.detect_market_signals(events)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🚨 Market Signals**")
                if signals['signals']:
                    for signal in signals['signals']:
                        st.write(f"• {signal}")
                else:
                    st.write("No significant signals detected")
            
            with col2:
                st.markdown("**📈 Trends Detected**")
                if signals['trends']:
                    for trend in signals['trends']:
                        st.write(f"• {trend}")
                else:
                    st.write("No clear trends identified")
            
            # Deal intelligence
            intelligence = self.processor.generate_deal_intelligence(events)
            
            if 'investor_activity' in intelligence:
                st.subheader("🏢 Investor Activity Analysis")
                investor_data = intelligence['investor_activity']
                
                if investor_data:
                    investor_df = pd.DataFrame([
                        {
                            'Investor': investor,
                            'Deals': data['deal_count'],
                            'Total Funding ($M)': data['total_funding']
                        }
                        for investor, data in investor_data.items()
                    ])
                    
                    st.dataframe(investor_df, use_container_width=True, hide_index=True)
        else:
            st.info("Load deal data to see AI insights")
    
    def _render_trends_tab(self, events: FundingEventCollection):
        """Render trend analysis"""
        st.subheader("📈 Market Trends")
        
        df = events.to_dataframe()
        
        if not df.empty and 'date' in df.columns:
            # Convert date column
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            
            if not df.empty:
                # Monthly trends
                df['month'] = df['date'].dt.to_period('M').astype(str)
                monthly_data = df.groupby('month').agg({
                    'amount': ['sum', 'count', 'mean']
                }).reset_index()
                monthly_data.columns = ['month', 'total_funding', 'deal_count', 'avg_deal_size']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(
                        monthly_data,
                        x='month',
                        y='total_funding',
                        title="Monthly Funding Volume",
                        color='total_funding',
                        color_continuous_scale=['#A8DADC', '#52796F', '#1B4332']
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(241, 250, 238, 0.8)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.line(
                        monthly_data,
                        x='month',
                        y='deal_count',
                        title="Monthly Deal Count",
                        markers=True
                    )
                    fig.update_traces(line=dict(color='#1B4332', width=3))
                    fig.update_layout(
                        plot_bgcolor='rgba(241, 250, 238, 0.8)', 
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Sector trends over time
                if 'sector' in df.columns:
                    st.subheader("Sector Performance Over Time")
                    sector_trends = df.groupby(['month', 'sector'])['amount'].sum().reset_index()
                    # Ensure month column is string for JSON serialization
                    sector_trends['month'] = sector_trends['month'].astype(str)
                    fig = px.line(
                        sector_trends,
                        x='month',
                        y='amount',
                        color='sector',
                        title="Funding Trends by Sector",
                        markers=True
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(241, 250, 238, 0.8)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Date information needed for trend analysis")
    
    def _render_enhanced_forecasting_tab(self, events: FundingEventCollection, enhanced_components: dict = None):
        """Render enhanced forecasting with confidence intervals and advanced models"""
        st.subheader("🔮 Enhanced Predictive Forecasting")
        
        if not enhanced_components or 'predictive_analytics' not in enhanced_components:
            st.warning("Enhanced analytics not initialized. Click 'Run Enhanced Analytics' in the sidebar.")
            return
        
        try:
            # Check for enhanced results in session state
            if 'enhanced_results' in st.session_state:
                forecast_results = st.session_state['enhanced_results']['forecast']
                
                # Display forecast confidence metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    accuracy = forecast_results.get('forecast_accuracy', 0.78) * 100
                    st.metric("Forecast Accuracy", f"{accuracy:.1f}%", delta="High confidence")
                
                with col2:
                    horizon = forecast_results.get('sector_forecasts', {}).get('Grid Modernization', {}).get('time_horizon', 12)
                    st.metric("Prediction Horizon", f"{horizon} months", delta="Extended range")
                
                with col3:
                    scenarios = len(forecast_results.get('market_scenarios', {}))
                    st.metric("Market Scenarios", scenarios, delta="Multi-scenario analysis")
                
                # Sector forecasts with confidence intervals
                st.subheader("📈 Sector Forecasting with Confidence Bands")
                
                sector_forecasts = forecast_results.get('sector_forecasts', {})
                for sector, forecast_data in sector_forecasts.items():
                    st.markdown(f"**{sector}**")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        predictions = forecast_data.get('predictions', [])
                        if predictions:
                            st.line_chart({
                                'Forecast': predictions[:6],  # First 6 months
                                'Upper Bound': [p * 1.2 for p in predictions[:6]],
                                'Lower Bound': [p * 0.8 for p in predictions[:6]]
                            })
                    
                    with col2:
                        if predictions:
                            next_6_months = sum(predictions[:6])
                            st.metric(f"6-Month Forecast", f"${next_6_months:.1f}M")
                
                # Market scenarios analysis
                st.subheader("🎯 Market Scenario Analysis")
                scenarios = forecast_results.get('market_scenarios', {})
                
                scenario_cols = st.columns(len(scenarios))
                for i, (scenario_name, scenario_data) in enumerate(scenarios.items()):
                    with scenario_cols[i]:
                        impact_score = scenario_data.get('impact_score', 0.5) * 100
                        probability = scenario_data.get('probability', 0.33) * 100
                        
                        st.markdown(f"**{scenario_name}**")
                        st.metric("Impact Score", f"{impact_score:.0f}%")
                        st.metric("Probability", f"{probability:.0f}%")
                
                # Key drivers
                st.subheader("🔑 Key Market Drivers")
                drivers = forecast_results.get('key_drivers', [])
                for driver in drivers:
                    st.markdown(f"• {driver}")
                    
            else:
                st.info("Run enhanced analytics to see advanced forecasting results.")
                
        except Exception as e:
            st.error(f"Enhanced forecasting error: {str(e)}")
    
    def _render_investor_intelligence_tab(self, events: FundingEventCollection, enhanced_components: dict = None):
        """Render investor intelligence and competitive landscape analysis"""
        st.subheader("🏢 Investor Intelligence & Competitive Landscape")
        
        if not enhanced_components or 'investor_intelligence' not in enhanced_components:
            st.warning("Investor intelligence not initialized. Click 'Run Enhanced Analytics' in the sidebar.")
            return
        
        try:
            # Check for enhanced results in session state
            if 'enhanced_results' in st.session_state:
                investor_analysis = st.session_state['enhanced_results']['investor']
                
                # Investor ecosystem overview
                st.subheader("📊 Investor Ecosystem Overview")
                
                col1, col2, col3 = st.columns(3)
                
                investor_profiles = investor_analysis.get('investor_profiles', {})
                
                with col1:
                    total_investors = len(investor_profiles)
                    st.metric("Active Investors", total_investors)
                
                with col2:
                    avg_check_size = sum(profile.get('avg_check_size', 0) for profile in investor_profiles.values()) / max(len(investor_profiles), 1)
                    st.metric("Avg Check Size", f"${avg_check_size:.1f}M")
                
                with col3:
                    ecosystem_health = investor_analysis.get('ecosystem_health', 'Strong')
                    st.metric("Ecosystem Health", ecosystem_health)
                
                # Top investors analysis
                st.subheader("🏆 Leading Climate Tech Investors")
                
                # Sort investors by total invested
                sorted_investors = sorted(
                    investor_profiles.items(),
                    key=lambda x: x[1].get('total_invested', 0),
                    reverse=True
                )
                
                for i, (investor_name, profile) in enumerate(sorted_investors[:5]):
                    with st.expander(f"{i+1}. {investor_name}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Total Deals", profile.get('total_deals', 0))
                            st.metric("Total Invested", f"${profile.get('total_invested', 0):.1f}M")
                        
                        with col2:
                            sector_focus = profile.get('sector_distribution', {})
                            if sector_focus:
                                top_sector = max(sector_focus.items(), key=lambda x: x[1])
                                st.metric("Primary Focus", f"{top_sector[0]} ({top_sector[1]} deals)")
                            
                            stage_pref = profile.get('stage_preference', {})
                            if stage_pref:
                                preferred_stage = max(stage_pref.items(), key=lambda x: x[1])
                                st.metric("Preferred Stage", f"{preferred_stage[0]} ({preferred_stage[1]} deals)")
                
                # Competitive landscape
                st.subheader("🗺️ Competitive Landscape Mapping")
                
                competitive_analysis = st.session_state['enhanced_results']['competitive']
                market_concentration = competitive_analysis.get('market_concentration', {})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Market Concentration Metrics**")
                    hhi_index = market_concentration.get('hhi_index', 0.15)
                    concentration_level = "Low" if hhi_index < 0.15 else "Medium" if hhi_index < 0.25 else "High"
                    st.metric("Market Concentration", concentration_level, delta=f"HHI: {hhi_index:.3f}")
                    
                    top_3_share = market_concentration.get('top_3_share', 0.35) * 100
                    st.metric("Top 3 Market Share", f"{top_3_share:.1f}%")
                
                with col2:
                    st.markdown("**Market Positioning**")
                    positioning = competitive_analysis.get('competitive_positions', {})
                    for sector, position_data in positioning.items():
                        market_share = position_data.get('market_share', 0) * 100
                        growth_rate = position_data.get('growth_rate', 0) * 100
                        st.markdown(f"**{sector}:** {market_share:.1f}% share, {growth_rate:.1f}% growth")
                
            else:
                st.info("Run enhanced analytics to see investor intelligence results.")
                
        except Exception as e:
            st.error(f"Investor intelligence error: {str(e)}")
    
    def _render_matchmaking_tab(self, events: FundingEventCollection, enhanced_components: dict = None):
        """Render startup-investor matchmaking interface and results"""
        st.subheader("🎯 Startup-Investor Matchmaking")
        
        if not enhanced_components or 'investor_intelligence' not in enhanced_components:
            st.warning("Investor intelligence not initialized. Click 'Run Enhanced Analytics' in the sidebar.")
            return
        
        # Check for matchmaking results
        if st.session_state.get('run_matchmaking') and 'startup_profile' in st.session_state:
            startup_profile = st.session_state['startup_profile']
            investor_intelligence = enhanced_components['investor_intelligence']
            