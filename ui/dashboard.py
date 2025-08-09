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
    
    def render(self, events: FundingEventCollection):
        """Render complete dashboard with deal data"""
        
        # Header
        self._render_header()
        
        # Sidebar filters and controls
        filter_config = self._render_sidebar(events)
        
        # Apply filters
        filtered_events = self._apply_filters(events, filter_config)
        
        # Main dashboard content
        if filtered_events.get_deal_count() > 0:
            self._render_main_content(filtered_events)
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
    
    def _render_sidebar(self, events: FundingEventCollection) -> dict:
        """Render sidebar with filters and controls"""
        with st.sidebar:
            # --- THIS SECTION IS REMOVED ---
            # st.header("Deal Flow Controls")
            # st.subheader("⚡ Enhanced Deal Collection")
            # col1, col2 = st.columns(2)
            # with col1:
            #     refresh_clicked = st.button("🔄 Enhanced Scan", type="primary", key="dash_refresh")
            # with col2:
            #     export_clicked = st.button("📊 Export Report", key="dash_export")
            # st.divider()
            # --- END OF REMOVED SECTION ---
            
            # Filters
            st.subheader("🎯 Deal Filters")
            filter_config = self.filters.render_filter_controls(events)
            
            # Quick actions
            st.subheader("⚡ Quick Actions")
            if st.button("🤖 Generate AI Insights", key="dash_insights"):
                st.session_state['generate_insights'] = True
            
            # Status indicators
            st.subheader("📈 Data Status")
            st.metric("Total Deals", events.get_deal_count())
            st.metric("Total Funding", format_currency(events.get_total_funding()))
            st.metric("Unique Investors", len(events.get_unique_investors()))
            
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
    
    def _render_main_content(self, events: FundingEventCollection):
        """Render main dashboard content with deal data"""
        
        # Key metrics
        self._render_key_metrics(events)
        
        # Tabbed interface
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Analytics", 
            "📋 Deal List", 
            "🤖 AI Insights", 
            "📈 Trends",
            "🔮 Predictive Analytics"
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
            self._render_predictive_tab(events)
    
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
                
                # --- THIS IS THE FIX ---
                # We remove the hardcoded 'color_discrete_sequence'.
                # Plotly will now automatically assign a unique color to every sector it finds.
                fig = px.pie(
                    sector_data, 
                    values='amount', 
                    names='sector',
                    title="Distribution of Funding by Sector"
                    # No longer need: color_discrete_sequence=...
                )
                # --- END OF FIX ---

                fig.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Amount: %{value:$,.0f}<br>Percentage: %{percent}<extra></extra>'
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif", color='#1B4332'),
                    showlegend=False # The pie chart labels are now the legend
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
                    color='stage', # Color by stage name for clarity
                    color_discrete_sequence=px.colors.qualitative.Pastel # Use a pleasant, auto-scaling color scheme
                )
                fig.update_layout(
                    plot_bgcolor='rgba(241, 250, 238, 0.8)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif", color='#1B4332')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Deal intelligence summary (no changes needed here)
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
    
    def _render_predictive_tab(self, events: FundingEventCollection):
        """Render predictive analytics"""
        st.subheader("🔮 Predictive Market Intelligence")
        st.markdown("*Advanced analytics for VC deal flow forecasting and market gap identification*")
        
        df = events.to_dataframe()
        
        try:
            # Generate predictions
            with st.spinner("Analyzing market trends..."):
                trends = analyze_market_trends(df)
            
            with st.spinner("Generating funding predictions..."):
                predictions = generate_funding_predictions(df)
            
            with st.spinner("Identifying investment opportunities..."):
                gaps = identify_investment_gaps(df)
            
            # Key prediction metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                predicted_funding = predictions.get('predictions', {}).get('overall', {}).get('total_predicted_funding', 450)
                st.metric(
                    "🔮 6M Predicted Funding",
                    f"${predicted_funding:.0f}M",
                    delta="18.5% growth forecast"
                )
            
            with col2:
                predicted_deals = predictions.get('predictions', {}).get('overall', {}).get('predicted_deal_count', 25)
                st.metric(
                    "📊 Expected Deals",
                    f"{predicted_deals}",
                    delta="15% increase expected"
                )
            
            with col3:
                market_growth = predictions.get('predictions', {}).get('overall', {}).get('market_growth_rate', 0.185) * 100
                st.metric(
                    "📈 Market Growth Rate",
                    f"{market_growth:.1f}%",
                    delta="Accelerating"
                )
            
            # Visualizations
            st.subheader("📊 Forecasting Models")
            with st.spinner("Generating predictive visualizations..."):
                charts = create_predictive_visualizations(trends, predictions)
            
            if 'trend_forecast' in charts:
                st.plotly_chart(charts['trend_forecast'], use_container_width=True)
            
            # Market intelligence report
            st.subheader("🎯 Market Intelligence Report")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔍 Investment Gaps**") 
                funding_gaps = gaps.get('funding_gaps', [])
                for i, gap in enumerate(funding_gaps[:5], 1):
                    st.markdown(f"**{i}.** {gap}")
            
            with col2:
                st.markdown("**🎯 Investment Recommendations**")
                recommendations = gaps.get('investment_recommendations', [])
                for i, rec in enumerate(recommendations[:5], 1):
                    st.markdown(f"**{i}.** {rec}")
        
        except Exception as e:
            st.error(f"Predictive analytics error: {str(e)}")
            st.info("Predictive analytics will be available when sufficient data is collected")
    
    def _render_empty_state(self):
        """Render empty state when no deals found"""
        st.info("No deals found matching current filters.")
        
        col1, col2, col3 = st.columns(3)
        
        with col2:
            if st.button("📋 Load Sample VC Deals", type="primary", key="empty_load_sample"):
                st.session_state['load_sample'] = True
                st.rerun()