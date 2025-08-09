# Climate Tech Funding Tracker

## Overview

The Climate Tech Funding Tracker is an AI-powered precision instrument for VC associates tracking Grid Modernization and Carbon Capture funding events. The system combines traditional web scraping with enhanced APITest2 integration for JavaScript-rendered content, uses OpenAI's GPT-4o model for classification and extraction, and presents insights through an immersive botanical-themed dashboard. Following a strategic pivot, the application now focuses exclusively on Seed and Series A deals in two target subsectors.

**Recent Architectural Refactoring (August 2025)**: The codebase has been restructured around functional domain boundaries rather than file types, creating clear job-to-be-done modules that align with VC workflow needs. The main entry point is now `main.py` instead of `app.py`, reflecting the streamlined architecture.

**Deployment Optimization (August 2025)**: Replaced Selenium-based scraping with deployment-ready solution using requests + BeautifulSoup for Replit compatibility. Configured OpenRouter API access via OPENAI2 secret for reliable AI functionality in production.

**Major Enhancement Implementation (August 2025)**: Implemented comprehensive module upgrades to address identified drawbacks:
- **Enhanced Predictive Analytics**: Multi-source data integration, time series forecasting with confidence intervals, market scenario analysis
- **Investor Intelligence**: Competitive landscape mapping, portfolio clustering, startup-investor matchmaking with AI-powered insights  
- **Data Source Diversity**: Integrated SEC EDGAR API, multi-source data collection, quality scoring and normalization across sources
- **Advanced UI Components**: New dashboard tabs for enhanced forecasting, investor intelligence, and matchmaking with interactive visualizations

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
- `enhanced_predictive_analytics.py`: Advanced forecasting with confidence intervals, ensemble models, and scenario analysis
- `investor_intelligence.py`: Competitive landscape mapping, portfolio clustering, and investor behavior analysis

**Data Sources (`/sources/`)**
- `scraper.py`: Web scraping logic for funding news discovery
- `api_client.py`: Enhanced API client with JavaScript rendering support
- `source_registry.py`: Centralized configuration of funding data sources
- `data_source_integration.py`: Multi-source data integration with SEC EDGAR API, quality scoring, and data normalization
- `deployment_scraper.py`: Deployment-ready scraper using HTTP requests for Replit compatibility

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

### Enhanced Data Processing Pipeline  
- **Multi-Source Integration**: The `MultiSourceDataIntegrator` combines web scraping, SEC EDGAR filings, and public APIs for comprehensive deal discovery
- **Advanced Quality Scoring**: Data normalization, deduplication, and quality assessment across all sources with confidence metrics
- **Enhanced Predictive Analytics**: Ensemble machine learning models with confidence intervals, time series forecasting, and market scenario analysis
- **Investor Intelligence**: Portfolio clustering, competitive landscape mapping, and startup-investor matchmaking with AI-powered strategic insights
- **Focused AI Classification**: GPT-4o extraction of essential fields with enhanced confidence scoring and validation
- **Strategic Filtering**: Only Grid Modernization and Carbon Capture deals in Seed/Series A stages are retained with advanced criteria matching

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

### Enhanced Data Infrastructure
- **Multi-Source Data Integration**: Combines web scraping, SEC EDGAR API, and specialized climate tech APIs
- **SEC EDGAR Integration**: Form D filings for private placements and venture capital funding data  
- **Deployment-Ready Scraper**: Uses requests + BeautifulSoup for Replit compatibility (no browser dependencies)
- **Data Quality Management**: Comprehensive normalization, deduplication, and quality scoring across all sources
- **Trafilatura**: Content extraction from web pages with text processing capabilities  
- **BeautifulSoup4**: HTML parsing and data extraction
- **Rate Limiting**: Built-in delays and randomization to respect website policies

### Advanced Analytics Libraries
- **Pandas**: Data manipulation and CSV file operations
- **JSON**: Configuration and metadata handling
- **Scikit-learn**: Enhanced machine learning models for ensemble forecasting, clustering, and predictive analytics
- **NumPy**: Numerical computing for statistical analysis and prediction algorithms
- **NetworkX**: Network analysis for investor co-investment patterns and competitive landscape mapping

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