# Climate Tech Funding Tracker

## Overview

The Climate Tech Funding Tracker is an AI-powered web application that monitors, analyzes, and visualizes climate technology investments in real-time. The system automatically scrapes funding data from multiple sources, uses OpenAI's GPT-4o model to classify and extract relevant information, and presents insights through an interactive Streamlit dashboard. The application focuses specifically on climate technology sectors including renewable energy, carbon capture, sustainable transport, and other environmental technologies.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Framework**: The primary user interface is built using Streamlit, providing an interactive dashboard with real-time data visualization
- **Plotly Integration**: Charts and graphs are rendered using Plotly Express and Graph Objects for interactive data visualization
- **Component-based Structure**: The UI is organized into modular components with cached resource initialization for performance

### Data Processing Pipeline
- **Multi-source Scraping**: The `FundingScraper` class collects funding data from multiple sources (TechCrunch, VentureBeat, Crunchbase News, Green Tech Media, CleanTech.com)
- **AI-powered Classification**: The `AIProcessor` leverages OpenAI's GPT-4o model to analyze raw funding data, determine climate tech relevance, and extract structured information
- **Data Validation**: Processed data includes confidence scores and keyword extraction to ensure quality and relevance

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
- **Requests Library**: HTTP client for web scraping operations
- **Trafilatura**: Content extraction from web pages with text processing capabilities
- **Rate Limiting**: Built-in delays and randomization to respect website policies

### Data Processing Libraries
- **Pandas**: Data manipulation and CSV file operations
- **JSON**: Configuration and metadata handling

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