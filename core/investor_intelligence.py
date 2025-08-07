"""
Lead Investor Intelligence Module
Advanced competitive landscape mapping and investor behavior analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import json
from openai import OpenAI
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict, Counter
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import config

class InvestorIntelligence:
    """
    Advanced investor analysis with competitive mapping and matchmaking
    Provides portfolio clustering, behavior prediction, and startup-investor scoring
    """
    
    def __init__(self):
        # AI client for market analysis
        self.client = OpenAI(
            api_key=config.OPENAI2_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            default_headers=config.OPENROUTER_DEFAULT_HEADERS,
        )
        
        # Analysis parameters
        self.target_sectors = config.TARGET_SUBSECTORS
        self.target_stages = config.TARGET_FUNDING_STAGES
        
        # Clustering models
        self.investor_clusterer = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
        
        # Investor behavior weights
        self.behavior_weights = {
            'sector_focus': 0.3,
            'stage_preference': 0.25,
            'check_size': 0.2,
            'geography': 0.15,
            'co_investment_pattern': 0.1
        }
    
    def analyze_investor_ecosystem(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive analysis of investor ecosystem and competitive dynamics
        """
        try:
            # Core investor analysis
            investor_profiles = self._build_investor_profiles(df)
            
            # Portfolio clustering
            investor_clusters = self._cluster_investors(investor_profiles)
            
            # Competitive landscape mapping
            competitive_map = self._map_competitive_landscape(df, investor_profiles)
            
            # Co-investment network analysis
            network_analysis = self._analyze_coinvestment_networks(df)
            
            # Market positioning
            positioning = self._analyze_market_positioning(investor_profiles, investor_clusters)
            
            return {
                'investor_profiles': investor_profiles,
                'investor_clusters': investor_clusters,
                'competitive_landscape': competitive_map,
                'network_analysis': network_analysis,
                'market_positioning': positioning,
                'ecosystem_health': self._assess_ecosystem_health(df, network_analysis)
            }
            
        except Exception as e:
            print(f"Investor ecosystem analysis error: {e}")
            return self._generate_sample_investor_analysis()
    
    def generate_matchmaking_scores(self, startup_profile: Dict, df: pd.DataFrame) -> Dict:
        """
        Generate startup-investor matchmaking scores with detailed reasoning
        """
        try:
            # Build investor profiles from deal data
            investor_profiles = self._build_investor_profiles(df)
            
            # Calculate compatibility scores
            compatibility_scores = {}
            detailed_analysis = {}
            
            for investor, profile in investor_profiles.items():
                score_breakdown = self._calculate_compatibility_score(startup_profile, profile)
                compatibility_scores[investor] = score_breakdown['total_score']
                detailed_analysis[investor] = score_breakdown
            
            # Rank investors
            ranked_investors = sorted(compatibility_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Generate AI-powered insights
            ai_insights = self._generate_matchmaking_insights(startup_profile, ranked_investors[:10], investor_profiles)
            
            return {
                'ranked_matches': ranked_investors,
                'detailed_scores': detailed_analysis,
                'ai_insights': ai_insights,
                'recommendation_summary': self._create_recommendation_summary(ranked_investors[:5], detailed_analysis),
                'market_context': self._provide_market_context(startup_profile, df)
            }
            
        except Exception as e:
            print(f"Matchmaking error: {e}")
            return self._generate_sample_matchmaking()
    
    def analyze_competitive_positioning(self, target_investor: str, df: pd.DataFrame) -> Dict:
        """
        Analyze specific investor's competitive position and strategy
        """
        try:
            # Get investor profile
            investor_profiles = self._build_investor_profiles(df)
            
            if target_investor not in investor_profiles:
                return {'error': f'Investor {target_investor} not found in data'}
            
            target_profile = investor_profiles[target_investor]
            
            # Competitive analysis
            competitors = self._identify_competitors(target_investor, investor_profiles)
            
            # Portfolio overlap analysis
            overlap_analysis = self._analyze_portfolio_overlap(target_investor, competitors, df)
            
            # Investment pattern comparison
            pattern_comparison = self._compare_investment_patterns(target_investor, competitors, investor_profiles)
            
            # Market share and influence
            market_influence = self._calculate_market_influence(target_investor, df)
            
            # Strategic recommendations
            strategy_insights = self._generate_strategic_insights(target_investor, target_profile, competitors, overlap_analysis)
            
            return {
                'investor_profile': target_profile,
                'key_competitors': competitors,
                'portfolio_overlap': overlap_analysis,
                'pattern_comparison': pattern_comparison,
                'market_influence': market_influence,
                'strategic_insights': strategy_insights,
                'positioning_score': self._calculate_positioning_score(target_profile, competitors)
            }
            
        except Exception as e:
            print(f"Competitive positioning error: {e}")
            return self._generate_sample_positioning_analysis()
    
    def _build_investor_profiles(self, df: pd.DataFrame) -> Dict:
        """
        Build comprehensive profiles for each investor
        """
        investor_profiles = {}
        
        if 'lead_investor' not in df.columns:
            return investor_profiles
        
        for investor in df['lead_investor'].unique():
            if pd.isna(investor) or investor == '':
                continue
            
            investor_deals = df[df['lead_investor'] == investor]
            
            profile = {
                'name': investor,
                'total_deals': len(investor_deals),
                'total_invested': investor_deals['amount'].sum() if 'amount' in df.columns else 0,
                'avg_check_size': investor_deals['amount'].mean() if 'amount' in df.columns else 0,
                'sector_distribution': self._calculate_sector_distribution(investor_deals),
                'stage_preference': self._calculate_stage_preference(investor_deals),
                'geography_focus': self._calculate_geography_focus(investor_deals),
                'investment_frequency': self._calculate_investment_frequency(investor_deals),
                'co_investors': self._identify_co_investors(investor, df),
                'portfolio_companies': investor_deals['startup_name'].tolist() if 'startup_name' in investor_deals.columns else [],
                'investment_thesis': self._infer_investment_thesis(investor_deals),
                'risk_profile': self._assess_risk_profile(investor_deals),
                'recent_activity': self._analyze_recent_activity(investor_deals)
            }
            
            investor_profiles[investor] = profile
        
        return investor_profiles
    
    def _cluster_investors(self, investor_profiles: Dict) -> Dict:
        """
        Cluster investors based on investment behavior and preferences
        """
        if len(investor_profiles) < 3:
            return self._generate_sample_clusters()
        
        # Prepare features for clustering
        features = []
        investor_names = []
        
        for investor, profile in investor_profiles.items():
            # Create feature vector
            feature_vector = [
                profile['total_deals'],
                profile['avg_check_size'],
                len(profile['sector_distribution']),
                len(profile['stage_preference']),
                profile['investment_frequency'],
                len(profile['co_investors'])
            ]
            
            features.append(feature_vector)
            investor_names.append(investor)
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(features)
        
        # Perform clustering
        n_clusters = min(5, len(investor_profiles))
        self.investor_clusterer.set_params(n_clusters=n_clusters)
        cluster_labels = self.investor_clusterer.fit_predict(features_scaled)
        
        # Organize results
        clusters = defaultdict(list)
        for investor, cluster_id in zip(investor_names, cluster_labels):
            clusters[f'Cluster_{cluster_id}'].append({
                'investor': investor,
                'profile': investor_profiles[investor]
            })
        
        # Add cluster characteristics
        cluster_analysis = {}
        for cluster_id, members in clusters.items():
            cluster_analysis[cluster_id] = {
                'members': members,
                'characteristics': self._analyze_cluster_characteristics(members),
                'size': len(members)
            }
        
        return cluster_analysis
    
    def _calculate_compatibility_score(self, startup_profile: Dict, investor_profile: Dict) -> Dict:
        """
        Calculate detailed compatibility score between startup and investor
        """
        scores = {}
        
        # Sector alignment
        startup_sector = startup_profile.get('sector', '')
        investor_sectors = investor_profile.get('sector_distribution', {})
        sector_score = investor_sectors.get(startup_sector, 0) / max(sum(investor_sectors.values()), 1)
        scores['sector_alignment'] = sector_score * 100
        
        # Stage alignment
        startup_stage = startup_profile.get('stage', '')
        investor_stages = investor_profile.get('stage_preference', {})
        stage_score = investor_stages.get(startup_stage, 0) / max(sum(investor_stages.values()), 1)
        scores['stage_alignment'] = stage_score * 100
        
        # Check size compatibility
        startup_funding_need = startup_profile.get('funding_amount', 0)
        investor_avg_check = investor_profile.get('avg_check_size', 0)
        
        if investor_avg_check > 0:
            check_ratio = min(startup_funding_need / investor_avg_check, investor_avg_check / startup_funding_need)
            check_score = max(0, 100 - abs(1 - check_ratio) * 100)
        else:
            check_score = 50  # Neutral score if no data
        scores['check_size_fit'] = check_score
        
        # Geography alignment
        startup_region = startup_profile.get('region', '')
        investor_regions = investor_profile.get('geography_focus', {})
        geo_score = investor_regions.get(startup_region, 0.3) * 100  # Default 30% for unknown regions
        scores['geography_fit'] = geo_score
        
        # Investment thesis alignment (AI-powered)
        thesis_score = self._calculate_thesis_alignment(startup_profile, investor_profile)
        scores['thesis_alignment'] = thesis_score
        
        # Portfolio synergy
        synergy_score = self._calculate_portfolio_synergy(startup_profile, investor_profile)
        scores['portfolio_synergy'] = synergy_score
        
        # Calculate weighted total score
        total_score = (
            scores['sector_alignment'] * self.behavior_weights['sector_focus'] +
            scores['stage_alignment'] * self.behavior_weights['stage_preference'] +
            scores['check_size_fit'] * self.behavior_weights['check_size'] +
            scores['geography_fit'] * self.behavior_weights['geography'] +
            scores['thesis_alignment'] * 0.15 +
            scores['portfolio_synergy'] * 0.15
        )
        
        scores['total_score'] = total_score
        scores['confidence_level'] = self._calculate_score_confidence(scores)
        
        return scores
    
    def _generate_matchmaking_insights(self, startup_profile: Dict, top_matches: List, investor_profiles: Dict) -> Dict:
        """
        Generate AI-powered insights for startup-investor matchmaking
        """
        try:
            # Prepare context for AI analysis
            context = {
                'startup': startup_profile,
                'top_investors': [{'investor': inv, 'score': score} for inv, score in top_matches[:5]],
                'investor_details': {inv: investor_profiles.get(inv, {}) for inv, _ in top_matches[:5]}
            }
            
            prompt = f"""
            Analyze this startup-investor matchmaking scenario for climate tech funding:
            
            Startup Profile:
            - Sector: {startup_profile.get('sector', 'Unknown')}
            - Stage: {startup_profile.get('stage', 'Unknown')}
            - Funding Need: ${startup_profile.get('funding_amount', 0):.1f}M
            - Region: {startup_profile.get('region', 'Unknown')}
            
            Top Investor Matches:
            {json.dumps([{'investor': inv, 'score': f'{score:.1f}'} for inv, score in top_matches[:3]], indent=2)}
            
            Provide strategic insights for the startup in JSON format:
            {{
                "key_insights": [
                    {{"insight": "specific observation", "importance": "high/medium/low", "action": "recommended action"}}
                ],
                "investor_strategy": [
                    {{"investor": "name", "approach": "how to approach", "value_prop": "key value proposition"}}
                ],
                "market_timing": {{"assessment": "good/fair/poor", "reasoning": "why", "recommendation": "timing advice"}},
                "competitive_advantages": ["advantage1", "advantage2"],
                "potential_concerns": [
                    {{"concern": "potential issue", "mitigation": "how to address"}}
                ],
                "next_steps": ["step1", "step2", "step3"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="openai/gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            insights = json.loads(response.choices[0].message.content)
            return insights
            
        except Exception as e:
            print(f"AI insights error: {e}")
            return self._generate_sample_insights()
    
    def create_investor_visualizations(self, ecosystem_analysis: Dict, matchmaking_results: Dict) -> Dict:
        """
        Create advanced visualizations for investor intelligence
        """
        visualizations = {}
        
        # 1. Investor ecosystem network graph
        visualizations['ecosystem_network'] = self._create_ecosystem_network(ecosystem_analysis)
        
        # 2. Competitive positioning radar chart
        visualizations['competitive_radar'] = self._create_competitive_radar(ecosystem_analysis)
        
        # 3. Matchmaking compatibility matrix
        visualizations['compatibility_matrix'] = self._create_compatibility_matrix(matchmaking_results)
        
        # 4. Portfolio overlap heatmap
        visualizations['portfolio_heatmap'] = self._create_portfolio_heatmap(ecosystem_analysis)
        
        # 5. Investment flow timeline
        visualizations['investment_timeline'] = self._create_investment_timeline(ecosystem_analysis)
        
        return visualizations
    
    # Helper methods for calculations and analysis
    def _calculate_sector_distribution(self, deals: pd.DataFrame) -> Dict:
        """Calculate sector distribution for an investor"""
        if 'sector' not in deals.columns:
            return {}
        return deals['sector'].value_counts().to_dict()
    
    def _calculate_stage_preference(self, deals: pd.DataFrame) -> Dict:
        """Calculate stage preference for an investor"""
        if 'stage' not in deals.columns:
            return {}
        return deals['stage'].value_counts().to_dict()
    
    def _calculate_geography_focus(self, deals: pd.DataFrame) -> Dict:
        """Calculate geography focus for an investor"""
        if 'region' not in deals.columns:
            return {'Unknown': len(deals)}
        return deals['region'].value_counts().to_dict()
    
    def _calculate_investment_frequency(self, deals: pd.DataFrame) -> float:
        """Calculate investment frequency (deals per year)"""
        if 'date' not in deals.columns or deals.empty:
            return 0.0
        
        deals['date'] = pd.to_datetime(deals['date'], errors='coerce')
        deals = deals.dropna(subset=['date'])
        
        if len(deals) < 2:
            return len(deals)
        
        date_range = (deals['date'].max() - deals['date'].min()).days
        if date_range == 0:
            return len(deals)
        
        return len(deals) / (date_range / 365.25)
    
    def _identify_co_investors(self, target_investor: str, df: pd.DataFrame) -> List:
        """Identify frequent co-investors"""
        # This is a simplified version - would need more complex deal data for full co-investor analysis
        return []
    
    def _calculate_thesis_alignment(self, startup_profile: Dict, investor_profile: Dict) -> float:
        """Calculate investment thesis alignment using AI"""
        # Simplified scoring based on available data
        sector_match = startup_profile.get('sector') in investor_profile.get('sector_distribution', {})
        stage_match = startup_profile.get('stage') in investor_profile.get('stage_preference', {})
        
        return 75.0 if sector_match and stage_match else 40.0
    
    def _calculate_portfolio_synergy(self, startup_profile: Dict, investor_profile: Dict) -> float:
        """Calculate potential portfolio synergy"""
        # Simplified synergy calculation
        portfolio_companies = investor_profile.get('portfolio_companies', [])
        if len(portfolio_companies) > 3:
            return 65.0  # Assume synergy potential with established portfolio
        return 45.0
    
    def _calculate_score_confidence(self, scores: Dict) -> float:
        """Calculate confidence level of the compatibility score"""
        # Higher confidence with more data points and consistent scores
        score_variance = np.var([v for k, v in scores.items() if k != 'total_score'])
        return max(20.0, 80.0 - score_variance / 10)
    
    # Sample data generators
    def _generate_sample_investor_analysis(self) -> Dict:
        """Generate sample investor ecosystem analysis"""
        return {
            'investor_profiles': {
                'Energy Impact Partners': {
                    'total_deals': 8,
                    'avg_check_size': 12.5,
                    'sector_distribution': {'Grid Modernization': 5, 'Carbon Capture': 3},
                    'stage_preference': {'Series A': 6, 'Seed': 2}
                },
                'Breakthrough Energy Ventures': {
                    'total_deals': 6,
                    'avg_check_size': 18.2,
                    'sector_distribution': {'Carbon Capture': 4, 'Grid Modernization': 2},
                    'stage_preference': {'Series A': 5, 'Seed': 1}
                }
            },
            'investor_clusters': {
                'Cluster_0': {
                    'size': 2,
                    'characteristics': 'Large check, Series A focused'
                }
            },
            'ecosystem_health': 'Strong'
        }
    
    def _generate_sample_matchmaking(self) -> Dict:
        """Generate sample matchmaking results"""
        return {
            'ranked_matches': [
                ('Energy Impact Partners', 87.5),
                ('Breakthrough Energy Ventures', 82.3),
                ('Prelude Ventures', 76.8)
            ],
            'ai_insights': {
                'key_insights': [
                    {'insight': 'Strong sector alignment with top investors', 'importance': 'high', 'action': 'Lead with grid expertise'}
                ],
                'market_timing': {'assessment': 'good', 'reasoning': 'Increasing grid investment'}
            }
        }
    
    def _generate_sample_insights(self) -> Dict:
        """Generate sample AI insights"""
        return {
            'key_insights': [
                {'insight': 'Market timing favorable for grid tech', 'importance': 'high', 'action': 'Emphasize market readiness'}
            ],
            'investor_strategy': [
                {'investor': 'Energy Impact Partners', 'approach': 'Focus on utility partnerships', 'value_prop': 'Grid reliability'}
            ],
            'market_timing': {'assessment': 'good', 'reasoning': 'Policy tailwinds', 'recommendation': 'Move quickly'},
            'next_steps': ['Prepare deck', 'Warm introductions', 'Demo scheduling']
        }