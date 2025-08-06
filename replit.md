# Climate Tech Funding Tracker

## Overview

The Climate Tech Funding Tracker is an AI-powered precision instrument for VC associates tracking Grid Modernization and Carbon Capture funding events. The system combines traditional web scraping with enhanced APITest2 integration for JavaScript-rendered content, uses OpenAI's GPT-4o model for classification and extraction, and presents insights through an immersive botanical-themed dashboard. Following a strategic pivot, the application now focuses exclusively on Seed and Series A deals in two target subsectors.

**Recent Architectural Refactoring (August 2025)**: The codebase has been restructured around functional domain boundaries rather than file types, creating clear job-to-be-done modules that align with VC workflow needs. The main entry point is now `main.py` instead of `app.py`, reflecting the streamlined architecture.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Refactored Architecture (Job-to-be-Done Structure)
The application has been refactored from generic file types to functional domain boundaries aligned with VC workflow needs:

**Core Domain (`/core/`)**
- `funding_event.py`: Core data model and validation for VC deals
- `extractor.py`: LLM-powered data extraction from raw news content  
- `processor.py`: Business logic for filtering and processing VC deal data
- `predictive_analytics.py`: Market forecasting and investment gap analysis

**Data Sources (`/sources/`)**
- `scraper.py`: Web scraping logic for funding news discovery
- `api_client.py`: Enhanced API client with JavaScript rendering support
- `source_registry.py`: Centralized configuration of funding data sources

**User Interface (`/ui/`)**
- `dashboard.py`: Main VC deal flow dashboard with botanical design
- `filters.py`: Interactive filtering controls for sector, stage, and amount ranges

**Data Management (`/data/`)**
- `data_manager.py`: CSV-based storage and deduplication logic
- `vc_sample_data.py`: Focused sample data for VC workflow testing

### Frontend Architecture
- **Streamlit Web Framework**: The primary user interface is built using Streamlit, providing an interactive dashboard with real-time data visualization
- **Plotly Integration**: Charts and graphs are rendered using Plotly Express and Graph Objects for interactive data visualization
- **Component-based Structure**: The UI is organized into modular components with cached resource initialization for performance

### Data Processing Pipeline  
- **Enhanced Scraping**: The `FundingScraper` integrates APITest2 functionality with Selenium for JavaScript-rendered content and AI-powered article classification
- **Focused AI Classification**: The `AIProcessor` uses GPT-4o to extract 5 essential fields (startup_name, subsector, funding_stage, amount_raised, lead_investor) with confidence scoring
- **Multi-stage Validation**: Articles are classified, data is extracted, and startups are validated against target subsectors using website analysis
- **Strategic Filtering**: Only Grid Modernization and Carbon Capture deals in Seed/Series A stages are retained
- **Predictive Analytics**: The `PredictiveAnalytics` engine provides market trend forecasting, funding predictions, and investment gap analysis using ML models and AI insights

### Data Storage & Management
- **CSV-based Storage**: Funding data is stored in CSV format for simplicity and portability
- **Duplicate Prevention**: The `DataManager` implements deduplication logic based on company name and funding amount
- **Metadata Tracking**: System maintains metadata about data freshness and processing statistics

### Configuration Management
- **Centralized Config**: All system parameters (sectors, funding stages, regions, data sources) are managed through a central configuration file
- **Environment Variables**: Sensitive data like API keys are managed through environment variables

### Utility Functions
- **Data Formatting**: Standardized currency formatting, date handling, and company name cleaning
- **Type Safety**: Strong typing throughout the codebase using Python type hints

## External Dependencies

### AI Services
- **OpenAI API**: GPT-4o model for natural language processing and data classification
- **API Key Management**: Requires OPENAI_API_KEY environment variable

### Web Scraping Infrastructure
- **Enhanced API Client**: Integrated APITest2 functionality (https://github.com/PeteM573/APITest2) for advanced scraping
- **Selenium WebDriver**: JavaScript-rendered content handling with Chrome headless mode
- **Trafilatura**: Content extraction from web pages with text processing capabilities  
- **BeautifulSoup4**: HTML parsing and data extraction
- **Rate Limiting**: Built-in delays and randomization to respect website policies

### Data Processing Libraries
- **Pandas**: Data manipulation and CSV file operations
- **JSON**: Configuration and metadata handling
- **Scikit-learn**: Machine learning models for predictive analytics and trend forecasting
- **NumPy**: Numerical computing for statistical analysis and prediction algorithms

### Visualization Framework
- **Streamlit**: Web application framework with built-in caching and session management
- **Plotly**: Interactive charting and data visualization

### Development Tools
- **Type Hints**: Comprehensive type annotations for better code maintainability
- **Error Handling**: Robust exception handling throughout the data pipeline

### Data Sources
- **TechCrunch**: Technology and startup funding news
- **VentureBeat**: Technology industry coverage
- **Crunchbase News**: Startup and investment tracking
- **Green Tech Media**: Clean technology sector news
- **CleanTech.com**: Climate technology industry coverage