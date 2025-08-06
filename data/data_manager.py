import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import config

class DataManager:
    """Manage funding data storage and retrieval"""
    
    def __init__(self):
        self.data_dir = "data"
        self.funding_file = os.path.join(self.data_dir, "climate_funding.csv")
        self.metadata_file = os.path.join(self.data_dir, "metadata.json")
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_funding_data(self, funding_events: List[Dict]):
        """Save funding events to CSV file"""
        try:
            # Convert to DataFrame
            new_df = pd.DataFrame(funding_events)
            
            # Load existing data if it exists
            if os.path.exists(self.funding_file):
                existing_df = pd.read_csv(self.funding_file)
                
                # Combine and remove duplicates
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                
                # Remove duplicates based on company name and amount
                combined_df = combined_df.drop_duplicates(
                    subset=['company', 'amount'], 
                    keep='first'
                )
            else:
                combined_df = new_df
            
            # Save to CSV
            combined_df.to_csv(self.funding_file, index=False)
            
            # Update metadata
            self._update_metadata(len(funding_events), len(combined_df))
            
            print(f"Saved {len(funding_events)} new funding events")
            print(f"Total events in database: {len(combined_df)}")
            
        except Exception as e:
            print(f"Error saving funding data: {str(e)}")
    
    def load_funding_data(self) -> pd.DataFrame:
        """Load funding data from CSV file"""
        try:
            if os.path.exists(self.funding_file):
                df = pd.read_csv(self.funding_file)
                
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
    
    def filter_by_date_range(self, df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Filter data by date range"""
        try:
            if 'date' in df.columns:
                mask = (df['date'] >= start_date) & (df['date'] <= end_date)
                return df[mask].copy()
            return df
        except Exception as e:
            print(f"Error filtering by date: {str(e)}")
            return df
    
    def filter_by_sector(self, df: pd.DataFrame, sectors: List[str]) -> pd.DataFrame:
        """Filter data by climate tech sectors"""
        try:
            if 'sector' in df.columns and sectors:
                return df[df['sector'].isin(sectors)].copy()
            return df
        except Exception as e:
            print(f"Error filtering by sector: {str(e)}")
            return df
    
    def filter_by_stage(self, df: pd.DataFrame, stages: List[str]) -> pd.DataFrame:
        """Filter data by funding stages"""
        try:
            if 'stage' in df.columns and stages:
                return df[df['stage'].isin(stages)].copy()
            return df
        except Exception as e:
            print(f"Error filtering by stage: {str(e)}")
            return df
    
    def filter_by_region(self, df: pd.DataFrame, regions: List[str]) -> pd.DataFrame:
        """Filter data by geographic regions"""
        try:
            if 'region' in df.columns and regions:
                return df[df['region'].isin(regions)].copy()
            return df
        except Exception as e:
            print(f"Error filtering by region: {str(e)}")
            return df
    
    def get_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Get summary statistics for the dataset"""
        try:
            stats = {
                'total_deals': len(df),
                'total_funding': df['amount'].sum() if 'amount' in df.columns else 0,
                'avg_deal_size': df['amount'].mean() if 'amount' in df.columns else 0,
                'median_deal_size': df['amount'].median() if 'amount' in df.columns else 0,
                'unique_companies': df['company'].nunique() if 'company' in df.columns else 0,
                'unique_investors': df['lead_investor'].nunique() if 'lead_investor' in df.columns else 0,
                'unique_sectors': df['sector'].nunique() if 'sector' in df.columns else 0,
                'date_range': {
                    'start': df['date'].min().isoformat() if 'date' in df.columns and len(df) > 0 and not df['date'].isna().all() else None,
                    'end': df['date'].max().isoformat() if 'date' in df.columns and len(df) > 0 and not df['date'].isna().all() else None
                }
            }
            return stats
        except Exception as e:
            print(f"Error calculating summary stats: {str(e)}")
            return {}
    
    def export_to_json(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """Export data to JSON format"""
        try:
            if filename is None:
                filename = f"climate_funding_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convert DataFrame to JSON
            json_data = df.to_json(orient='records', date_format='iso', indent=2)
            
            # Save to file
            export_path = os.path.join(self.data_dir, filename)
            with open(export_path, 'w') as f:
                f.write(json_data or "{}")
            
            return export_path
        except Exception as e:
            print(f"Error exporting to JSON: {str(e)}")
            return ""
    
    def export_to_csv(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """Export data to CSV format"""
        try:
            if filename is None:
                filename = f"climate_funding_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            export_path = os.path.join(self.data_dir, filename)
            df.to_csv(export_path, index=False)
            
            return export_path
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return ""
    
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
    
    def get_metadata(self) -> Dict:
        """Get metadata information"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading metadata: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Remove data older than specified number of days"""
        try:
            df = self.load_funding_data()
            if not df.empty and 'date' in df.columns:
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                filtered_df = df[df['date'] >= cutoff_date]
                
                if len(filtered_df) < len(df):
                    filtered_df.to_csv(self.funding_file, index=False)
                    removed_count = len(df) - len(filtered_df)
                    print(f"Removed {removed_count} old funding events")
                    return removed_count
            return 0
        except Exception as e:
            print(f"Error cleaning up old data: {str(e)}")
            return 0
