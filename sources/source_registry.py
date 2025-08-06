"""
Registry of funding data sources for climate tech VC deal discovery
Centralizes configuration of news sources, APIs, and scraping targets
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class FundingSource:
    """Configuration for a funding data source"""
    name: str
    base_url: str
    source_type: str  # 'news_site', 'api', 'rss'
    search_terms: List[str]
    rate_limit_seconds: float = 2.0
    is_active: bool = True
    requires_api_key: bool = False
    
class FundingSourceRegistry:
    """
    Central registry of all funding data sources
    Manages source configuration for VC deal discovery
    """
    
    def __init__(self):
        self.sources = self._initialize_sources()
    
    def _initialize_sources(self) -> Dict[str, FundingSource]:
        """Initialize all known funding sources"""
        
        # Grid Modernization focused search terms
        grid_terms = [
            "grid modernization funding",
            "smart grid investment",
            "transmission funding", 
            "distribution grid funding",
            "energy storage grid funding",
            "grid infrastructure investment",
            "grid analytics funding",
            "microgrid funding"
        ]
        
        # Carbon Capture focused search terms  
        carbon_terms = [
            "carbon capture funding",
            "direct air capture investment",
            "carbon removal funding",
            "CCS funding",
            "carbon utilization investment",
            "carbon sequestration funding",
            "DAC funding",
            "carbon storage investment"
        ]
        
        # Combined climate tech terms
        combined_terms = grid_terms + carbon_terms + [
            "climate tech seed funding",
            "climate tech series a",
            "cleantech seed round",
            "cleantech series a funding"
        ]
        
        sources = {
            'techcrunch': FundingSource(
                name="TechCrunch",
                base_url="https://techcrunch.com",
                source_type="news_site",
                search_terms=combined_terms,
                rate_limit_seconds=3.0,
                is_active=True
            ),
            
            'venturebeat': FundingSource(
                name="VentureBeat", 
                base_url="https://venturebeat.com",
                source_type="news_site",
                search_terms=combined_terms,
                rate_limit_seconds=2.5,
                is_active=True
            ),
            
            'crunchbase_news': FundingSource(
                name="Crunchbase News",
                base_url="https://news.crunchbase.com",
                source_type="news_site", 
                search_terms=combined_terms,
                rate_limit_seconds=2.0,
                is_active=True
            ),
            
            'greentech_media': FundingSource(
                name="Green Tech Media",
                base_url="https://www.greentechmedia.com",
                source_type="news_site",
                search_terms=grid_terms + carbon_terms,
                rate_limit_seconds=2.0,
                is_active=True
            ),
            
            'cleantech': FundingSource(
                name="CleanTech.com",
                base_url="https://cleantech.com",
                source_type="news_site",
                search_terms=combined_terms,
                rate_limit_seconds=2.0,
                is_active=True
            ),
            
            'utility_dive': FundingSource(
                name="Utility Dive",
                base_url="https://www.utilitydive.com", 
                source_type="news_site",
                search_terms=grid_terms,
                rate_limit_seconds=2.0,
                is_active=True
            ),
            
            'energy_storage_news': FundingSource(
                name="Energy Storage News",
                base_url="https://www.energy-storage.news",
                source_type="news_site", 
                search_terms=grid_terms,
                rate_limit_seconds=2.0,
                is_active=True
            ),
            
            'carbon_pulse': FundingSource(
                name="Carbon Pulse",
                base_url="https://carbon-pulse.com",
                source_type="news_site",
                search_terms=carbon_terms,
                rate_limit_seconds=2.0,
                is_active=True
            )
        }
        
        return sources
    
    def get_active_sources(self) -> List[FundingSource]:
        """Get all active funding sources"""
        return [source for source in self.sources.values() if source.is_active]
    
    def get_source(self, name: str) -> FundingSource:
        """Get specific funding source by name"""
        return self.sources.get(name.lower())
    
    def get_sources_by_type(self, source_type: str) -> List[FundingSource]:
        """Get sources by type (news_site, api, rss)"""
        return [
            source for source in self.sources.values() 
            if source.source_type == source_type and source.is_active
        ]
    
    def get_grid_focused_sources(self) -> List[FundingSource]:
        """Get sources with strong Grid Modernization coverage"""
        grid_focused = ['utility_dive', 'energy_storage_news', 'greentech_media']
        return [self.sources[name] for name in grid_focused if name in self.sources]
    
    def get_carbon_focused_sources(self) -> List[FundingSource]:
        """Get sources with strong Carbon Capture coverage"""
        carbon_focused = ['carbon_pulse', 'greentech_media', 'cleantech']
        return [self.sources[name] for name in carbon_focused if name in self.sources]
    
    def update_source_status(self, source_name: str, is_active: bool):
        """Enable/disable a funding source"""
        if source_name.lower() in self.sources:
            self.sources[source_name.lower()].is_active = is_active
    
    def add_custom_source(self, source: FundingSource):
        """Add custom funding source"""
        self.sources[source.name.lower().replace(' ', '_')] = source
    
    def get_all_search_terms(self) -> List[str]:
        """Get all unique search terms across active sources"""
        all_terms = []
        for source in self.get_active_sources():
            all_terms.extend(source.search_terms)
        return list(set(all_terms))
    
    def get_source_priorities(self) -> Dict[str, int]:
        """Get source priority ranking for VC deal quality"""
        # Higher numbers = higher priority for VC deals
        priorities = {
            'techcrunch': 10,        # Excellent startup coverage
            'crunchbase_news': 9,    # Funding-focused
            'venturebeat': 8,        # Good tech coverage
            'greentech_media': 7,    # Climate tech specialist
            'cleantech': 6,          # Climate focused
            'utility_dive': 5,       # Grid specific
            'energy_storage_news': 5, # Grid specific
            'carbon_pulse': 4        # Carbon specific
        }
        return priorities
    
    def export_source_config(self) -> Dict:
        """Export source configuration for backup/sharing"""
        config = {}
        for name, source in self.sources.items():
            config[name] = {
                'name': source.name,
                'base_url': source.base_url,
                'source_type': source.source_type,
                'search_terms': source.search_terms,
                'rate_limit_seconds': source.rate_limit_seconds,
                'is_active': source.is_active,
                'requires_api_key': source.requires_api_key
            }
        return config

# Global registry instance
FUNDING_SOURCES = FundingSourceRegistry()

# Convenience functions
def get_active_sources() -> List[FundingSource]:
    """Get all active funding sources"""
    return FUNDING_SOURCES.get_active_sources()

def get_vc_priority_sources() -> List[FundingSource]:
    """Get sources ranked by VC deal quality"""
    priorities = FUNDING_SOURCES.get_source_priorities()
    sources = FUNDING_SOURCES.get_active_sources()
    
    # Sort by priority (highest first)
    return sorted(
        sources, 
        key=lambda x: priorities.get(x.name.lower().replace(' ', '_'), 0),
        reverse=True
    )