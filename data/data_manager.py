# data/data_manager.py (v2 - With Proactive Data Cleaning)

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import config

class DataManager:
    """Manage funding data storage and retrieval"""
    
    def __init__(self):
        self.data_dir = config.DATA_DIRECTORY
        self.funding_file = os.path.join(self.data_dir, config.FUNDING_DATA_FILE)
        self.metadata_file = os.path.join(self.data_dir, config.METADATA_FILE)
        self.processed_urls_file = os.path.join(self.data_dir, "processed_urls.log")
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_processed_urls(self) -> Set[str]:
        if not os.path.exists(self.processed_urls_file):
            return set()
        try:
            with open(self.processed_urls_file, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f)
        except Exception as e:
            print(f"   -> 🔴 Could not load processed URLs file: {e}")
            return set()

    def add_processed_url(self, url: str):
        try:
            with open(self.processed_urls_file, 'a', encoding='utf-8') as f:
                f.write(f"{url}\n")
        except Exception as e:
            print(f"   -> 🔴 Could not write to processed URLs file: {e}")

    def save_funding_data(self, funding_events: List[Dict]):
        if not funding_events:
            return
        
        try:
            new_df = pd.DataFrame(funding_events)
            
            if os.path.exists(self.funding_file):
                existing_df = pd.read_csv(self.funding_file)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df['amount'] = pd.to_numeric(combined_df['amount'], errors='coerce')
                dedupe_keys = ['company', 'amount', 'stage']
                final_df = combined_df.drop_duplicates(subset=[k for k in dedupe_keys if k in combined_df.columns], keep='last')
            else:
                final_df = new_df
            
            final_df.to_csv(self.funding_file, index=False)
            self._update_metadata(len(new_df), len(final_df))
            
        except Exception as e:
            print(f"Error saving funding data: {str(e)}")
    
    def load_funding_data(self) -> pd.DataFrame:
        """Load funding data from CSV file with proactive cleaning."""
        try:
            if os.path.exists(self.funding_file):
                df = pd.read_csv(self.funding_file)
                
                # --- THIS IS THE FIX ---
                # Define columns that should always be strings
                string_columns = [
                    'company', 'sector', 'stage', 'lead_investor', 'location', 
                    'region', 'description', 'source_url', 'source', 
                    'other_investors', 'keywords'
                ]
                
                # Ensure all string columns exist before trying to fill them
                for col in string_columns:
                    if col in df.columns:
                        # Replace NaN values with empty strings to prevent errors
                        df[col] = df[col].fillna('')
                # --- END OF FIX ---

                # Convert date columns
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                if 'processed_date' in df.columns:
                    df['processed_date'] = pd.to_datetime(df['processed_date'], errors='coerce')
                
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error loading funding data: {str(e)}")
            return pd.DataFrame()
    
    def _update_metadata(self, new_events: int, total_events: int):
        """Update metadata file with latest information"""
        try:
            metadata = {
                'last_updated': datetime.now().isoformat(),
                'total_events': total_events,
                'new_events_added': new_events,
                'data_sources': config.DATA_SOURCES,
                'version': '1.0'
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Error updating metadata: {str(e)}")