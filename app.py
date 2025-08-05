import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from scraper import FundingScraper
from ai_processor import AIProcessor
from data_manager import DataManager
from utils import format_currency, format_date
import config

# Configure page
st.set_page_config(
    page_title="Climate Tech Funding Tracker",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    return FundingScraper(), AIProcessor(), DataManager()

def main():
    scraper, ai_processor, data_manager = init_components()
    
    # Header
    st.title("🌱 Climate Tech Funding Tracker")
    st.markdown("*AI-powered real-time analysis of climate technology investments*")
    
    # Sidebar
    with st.sidebar:
        st.header("Controls")
        
        # Data refresh section
        st.subheader("Data Management")
        if st.button("🔄 Refresh Data", type="primary"):
            with st.spinner("Scraping latest funding data..."):
                try:
                    # Scrape new data
                    raw_data = scraper.scrape_all_sources()
                    if raw_data:
                        # Process with AI
                        processed_data = []
                        for item in raw_data:
                            processed_item = ai_processor.process_funding_event(item)
                            if processed_item and processed_item.get('is_climate_tech', False):
                                processed_data.append(processed_item)
                        
                        # Save to storage
                        if processed_data:
                            data_manager.save_funding_data(processed_data)
                            st.success(f"✅ Added {len(processed_data)} new climate tech funding events")
                            st.rerun()
                        else:
                            st.warning("No new climate tech funding events found")
                    else:
                        st.warning("No new data found from sources")
                except Exception as e:
                    st.error(f"Error refreshing data: {str(e)}")
        
        # Auto-refresh toggle
        auto_refresh = st.toggle("Auto-refresh (30 min)", value=False)
        
        # Export section
        st.subheader("Export Data")
        export_format = st.selectbox("Format", ["CSV", "JSON"])
        
        # Filters
        st.subheader("Filters")
        
    # Load existing data
    try:
        df = data_manager.load_funding_data()
        
        if df.empty:
            st.info("📊 No data available. Click 'Refresh Data' to start collecting funding information.")
            return
        
        # Apply filters in sidebar
        with st.sidebar:
            # Date range filter
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                min_date = df['date'].min().date()
                max_date = df['date'].max().date()
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
                if len(date_range) == 2:
                    df = df[(df['date'].dt.date >= date_range[0]) & 
                           (df['date'].dt.date <= date_range[1])]
            
            # Sector filter
            if 'sector' in df.columns:
                sectors = ['All'] + sorted(df['sector'].dropna().unique().tolist())
                selected_sector = st.selectbox("Sector", sectors)
                if selected_sector != 'All':
                    df = df[df['sector'] == selected_sector]
            
            # Stage filter
            if 'stage' in df.columns:
                stages = ['All'] + sorted(df['stage'].dropna().unique().tolist())
                selected_stage = st.selectbox("Funding Stage", stages)
                if selected_stage != 'All':
                    df = df[df['stage'] == selected_stage]
            
            # Region filter
            if 'region' in df.columns:
                regions = ['All'] + sorted(df['region'].dropna().unique().tolist())
                selected_region = st.selectbox("Region", regions)
                if selected_region != 'All':
                    df = df[df['region'] == selected_region]
            
            # Amount range filter
            if 'amount' in df.columns and not df['amount'].isna().all():
                min_amount = float(df['amount'].min())
                max_amount = float(df['amount'].max())
                amount_range = st.slider(
                    "Funding Amount (M USD)",
                    min_value=min_amount/1000000,
                    max_value=max_amount/1000000,
                    value=(min_amount/1000000, max_amount/1000000),
                    step=0.1
                )
                df = df[(df['amount'] >= amount_range[0]*1000000) & 
                       (df['amount'] <= amount_range[1]*1000000)]
            
            # Search
            search_term = st.text_input("🔍 Search companies, investors...")
            if search_term:
                mask = df.apply(lambda row: row.astype(str).str.contains(
                    search_term, case=False, na=False).any(), axis=1)
                df = df[mask]
            
            # Export button
            if st.button("📥 Export Filtered Data"):
                try:
                    if export_format == "CSV":
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"climate_funding_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    else:
                        json_data = df.to_json(orient='records', indent=2)
                        st.download_button(
                            label="Download JSON",
                            data=json_data,
                            file_name=f"climate_funding_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json"
                        )
                except Exception as e:
                    st.error(f"Export error: {str(e)}")
        
        # Main dashboard
        if not df.empty:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_funding = df['amount'].sum() if 'amount' in df.columns else 0
                st.metric(
                    "Total Funding",
                    format_currency(total_funding),
                    help="Total funding amount in filtered data"
                )
            
            with col2:
                deal_count = len(df)
                st.metric(
                    "Active Deals",
                    deal_count,
                    help="Number of funding events in filtered data"
                )
            
            with col3:
                avg_deal = total_funding / deal_count if deal_count > 0 else 0
                st.metric(
                    "Avg Deal Size",
                    format_currency(avg_deal),
                    help="Average funding amount per deal"
                )
            
            with col4:
                unique_investors = df['lead_investor'].nunique() if 'lead_investor' in df.columns else 0
                st.metric(
                    "Active Investors",
                    unique_investors,
                    help="Number of unique lead investors"
                )
            
            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "📋 Deal List", "🤖 AI Insights", "📈 Trends"])
            
            with tab1:
                # Visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'sector' in df.columns and not df['sector'].isna().all():
                        st.subheader("Funding by Sector")
                        sector_data = df.groupby('sector')['amount'].sum().reset_index()
                        fig = px.pie(
                            sector_data, 
                            values='amount', 
                            names='sector',
                            title="Distribution of Funding by Sector"
                        )
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'stage' in df.columns and not df['stage'].isna().all():
                        st.subheader("Funding by Stage")
                        stage_data = df.groupby('stage')['amount'].sum().reset_index()
                        fig = px.bar(
                            stage_data,
                            x='stage',
                            y='amount',
                            title="Funding Amount by Stage"
                        )
                        fig.update_layout(xaxis_title="Funding Stage", yaxis_title="Amount (USD)")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Timeline chart
                if 'date' in df.columns and not df['date'].isna().all():
                    st.subheader("Funding Timeline")
                    timeline_data = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
                    fig = px.line(
                        timeline_data,
                        x='date',
                        y='amount',
                        title="Daily Funding Activity"
                    )
                    fig.update_layout(xaxis_title="Date", yaxis_title="Amount (USD)")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Geographic distribution
                if 'region' in df.columns and not df['region'].isna().all():
                    st.subheader("Geographic Distribution")
                    geo_data = df.groupby('region').agg({
                        'amount': 'sum',
                        'company': 'count'
                    }).reset_index()
                    geo_data.columns = ['region', 'total_funding', 'deal_count']
                    
                    fig = px.scatter(
                        geo_data,
                        x='deal_count',
                        y='total_funding',
                        size='total_funding',
                        hover_data=['region'],
                        title="Deals vs Funding by Region"
                    )
                    fig.update_layout(
                        xaxis_title="Number of Deals",
                        yaxis_title="Total Funding (USD)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.subheader("Funding Events")
                
                # Display data table
                display_df = df.copy()
                if 'amount' in display_df.columns:
                    display_df['amount_formatted'] = display_df['amount'].apply(format_currency)
                if 'date' in display_df.columns:
                    display_df['date_formatted'] = display_df['date'].apply(format_date)
                
                # Select columns to display
                display_columns = [col for col in [
                    'company', 'sector', 'stage', 'amount_formatted', 
                    'lead_investor', 'date_formatted', 'location', 'description'
                ] if col in display_df.columns]
                
                if display_columns:
                    st.dataframe(
                        display_df[display_columns],
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No data columns available for display")
            
            with tab3:
                st.subheader("AI-Generated Market Intelligence")
                
                if st.button("🤖 Generate Insights"):
                    with st.spinner("Analyzing market trends with AI..."):
                        try:
                            insights = ai_processor.generate_market_insights(df)
                            if insights:
                                st.markdown("### Key Trends")
                                st.markdown(insights.get('trends', 'No trends identified'))
                                
                                st.markdown("### Investment Opportunities")
                                st.markdown(insights.get('opportunities', 'No opportunities identified'))
                                
                                st.markdown("### Market Analysis")
                                st.markdown(insights.get('analysis', 'No analysis available'))
                            else:
                                st.warning("Unable to generate insights at this time")
                        except Exception as e:
                            st.error(f"Error generating insights: {str(e)}")
            
            with tab4:
                st.subheader("Market Trends")
                
                # Trend analysis
                if 'date' in df.columns and len(df) > 1:
                    # Monthly trends
                    df['month'] = df['date'].dt.to_period('M')
                    monthly_data = df.groupby('month').agg({
                        'amount': ['sum', 'count', 'mean']
                    }).reset_index()
                    monthly_data.columns = ['month', 'total_funding', 'deal_count', 'avg_deal_size']
                    monthly_data['month'] = monthly_data['month'].astype(str)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.bar(
                            monthly_data,
                            x='month',
                            y='total_funding',
                            title="Monthly Funding Volume"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig = px.line(
                            monthly_data,
                            x='month',
                            y='avg_deal_size',
                            title="Average Deal Size Trend"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Sector trends
                    if 'sector' in df.columns:
                        st.subheader("Sector Performance")
                        sector_trends = df.groupby(['month', 'sector'])['amount'].sum().reset_index()
                        fig = px.line(
                            sector_trends,
                            x='month',
                            y='amount',
                            color='sector',
                            title="Funding Trends by Sector"
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No data matches the current filters.")
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Try refreshing the data or check your data sources.")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(1800)  # 30 minutes
        st.rerun()

if __name__ == "__main__":
    main()
