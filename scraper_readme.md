# Using `ctvc_scraper.py` on Replit

This module (`ctvc_scraper.py`) is a focused, reusable Python script for scraping and extracting climate tech funding deals from the CTVC newsletter. It is designed to work both as a standalone script and as an importable module in your Replit projects.

## Quick Start on Replit

### 1. Add Your OpenRouter API Key

- In your Replit workspace, go to the **Secrets** tab (Environment Variables).
- Add a new secret:
  - **Key:** `OPENAI_API_KEY`
  - **Value:** *(your OpenRouter API key)*

### 2. Install Required Packages

Open the Replit shell and run:

```sh
pip install openai requests beautifulsoup4 python-dotenv selenium webdriver-manager lxml
```

### 3. Enable Firefox for Selenium

Replit supports headless Firefox via `webdriver-manager`. No extra setup is needed.

### 4. Run the Module

To run the scraper directly and save results to CSV:

```sh
python ctvc_scraper.py
```

- This will crawl the latest CTVC newsletter articles, extract funding deals using the OpenRouter LLM, and save the results to `climate_funding_data_master.csv`.

### 5. Import as a Module

You can also import and use the main function in your own scripts:

```python
from ctvc_scraper import fetch_latest_ctvc_deals

deals = fetch_latest_ctvc_deals(pages_to_load=2)
print(deals)
```

## Output

- Extracted deals are saved to `climate_funding_data_master.csv`.
- Processed URLs are tracked in `processed_urls.log` to avoid duplicates.

## Notes

- All LLM calls use the [meta-llama/llama-3-8b-instruct](https://openrouter.ai/models/meta-llama/llama-3-8b-instruct) model via OpenRouter.
- Console output will show scraping and extraction progress.
- Rate limits are respected with a short delay between LLM calls.

---
```// filepath: /Users/pmolski/Documents/APITest/readme-module.md

# Using `ctvc_scraper.py` on Replit

This module (`ctvc_scraper.py`) is a focused, reusable Python script for scraping and extracting climate tech funding deals from the CTVC newsletter. It is designed to work both as a standalone script and as an importable module in your Replit projects.

## Quick Start on Replit

### 1. Add Your OpenRouter API Key

- In your Replit workspace, go to the **Secrets** tab (Environment Variables).
- Add a new secret:
 - **Key:** `OPENAI_API_KEY`
  - **Value:** *(your OpenRouter API key)*

### 2. Install Required Packages

Open the Replit shell and run:

```sh
pip install openai requests beautifulsoup4 python-dotenv selenium webdriver-manager lxml
```

### 3. Enable Firefox for Selenium

Replit supports headless Firefox via `webdriver-manager`. No extra setup is needed.

### 4. Run the Module

To run the scraper directly and save results to CSV:

```sh
python ctvc_scraper.py
```

- This will crawl the latest CTVC newsletter articles, extract funding deals using the OpenRouter LLM, and save the results to `climate_funding_data_master.csv`.

### 5. Import as a Module

You can also import and use the main function in your own scripts:

```python
from ctvc_scraper import fetch_latest_ctvc_deals

deals = fetch_latest_ctvc_deals(pages_to_load=2)
print(deals)
```

## Output

- Extracted deals are saved to `climate_funding_data_master.csv`.
- Processed URLs are tracked in `processed_urls.log` to avoid duplicates.

## Notes

- All LLM calls use the [meta-llama/llama-3-8b-instruct](https://openrouter.ai/models/meta-llama/llama-3-8b-instruct) model via OpenRouter.
- Console output will show scraping and extraction progress.
- Rate limits are respected with a short delay between LLM calls.

---