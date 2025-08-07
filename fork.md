Climate Tech Funding Tracker – August 2025 Update
What’s New in This Session
1. Refactored Architecture
Job-to-be-Done Structure: The codebase is now organized by functional domains (core, data, sources, ui) instead of generic file types.
Main Entry Point: The main application now runs from main.py instead of app.py.
Focused VC Workflow: All logic is streamlined for VC associates tracking Grid Modernization and Carbon Capture deals at Seed and Series A stages.
2. Enhanced Scraper Integration
The CTVC newsletter scraper (sources/scraper.py) is now the primary data ingestion tool, using Selenium for JavaScript-rendered content and OpenAI for deal extraction.
Deduplication: Scraped URLs are tracked using the DataManager’s new processed_urls.log to avoid duplicate deal entries.
3. Data Management Improvements
data_manager.py now includes:
Methods to load and append processed URLs.
Improved deduplication logic for funding events.
Metadata tracking for data freshness and event counts.
4. Sample Data for VC Testing
vc_sample_data.py provides focused sample deals for Grid Modernization and Carbon Capture, with realistic fields and recent dates.
5. Utility and Validation Enhancements
utils.py includes robust formatting, cleaning, and validation functions for currency, dates, company names, and funding data.
6. Configuration Centralization
All key parameters (target sectors, funding stages, regions, API keys, file paths) are now managed in config.py.
7. Streamlit UI Modernization
The UI is modularized under ui (see dashboard.py), with a botanical design and interactive controls for VC workflows.
8. Predictive Analytics Engine
predictive_analytics.py provides market forecasting, investment gap analysis, and trend visualizations using ML and AI.
9. Improved Testing
test_app.py verifies imports and basic functionality for all major modules.
Summary:
This session focused on making the system more modular, VC-centric, and robust for real-world deal flow tracking. The application is now easier to maintain, extend, and use for focused climate tech investment research.