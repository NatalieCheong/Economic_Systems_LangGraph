#!/usr/bin/env python3
"""
Configuration settings for Economic Analysis AI Agents with LangGraph
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
import warnings
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class EconomicConfig:
    """Configuration class for economic analysis system"""
    
    # API Keys and Authentication
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    ALPHA_VANTAGE_API_KEY: str = os.getenv('ALPHA_VANTAGE_API_KEY')
    FRED_API_KEY: str = os.getenv('FRED_API_KEY')  # FRED API key (optional but recommended for higher rate limits)
    
    # LangSmith Configuration (Optional)
    LANGSMITH_API_KEY: str = os.getenv('LANGSMITH_API_KEY')
    LANGCHAIN_TRACING_V2: str = os.getenv('LANGCHAIN_TRACING_V2', 'true')
    LANGCHAIN_ENDPOINT: str = os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
    LANGCHAIN_PROJECT: str = os.getenv('LANGCHAIN_PROJECT', 'economic-analysis')
    
    # Model Configuration
    DEFAULT_MODEL: str = "gpt-4"
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 4000
    
    # Data Source Configuration
    DEFAULT_PERIOD: str = "5y"  # Default period for economic data
    DEFAULT_FREQUENCY: str = "q"  # Default frequency: 'a' (annual), 'q' (quarterly), 'm' (monthly), 'd' (daily)
    
    # Analysis Configuration
    ANALYSIS_TYPES: List[str] = ["comprehensive", "gdp_focus", "inflation_focus", "employment_focus", "monetary_policy"]
    
    # Output Directories
    CHART_OUTPUT_DIR: str = "charts"
    REPORT_OUTPUT_DIR: str = "reports"
    DATA_CACHE_DIR: str = "data_cache"
    
    # Rate Limiting
    FRED_RATE_LIMIT: int = 120  # requests per minute for FRED API
    ALPHA_VANTAGE_RATE_LIMIT: int = 5  # requests per minute for Alpha Vantage free tier
    YAHOO_RATE_LIMIT: int = 2000  # requests per hour for Yahoo Finance
    
    # Economic Indicators Configuration
    CORE_INDICATORS: Dict[str, Dict[str, str]] = {
        # GDP and Growth Indicators
        'gdp': {
            'fred_id': 'GDP',
            'name': 'Gross Domestic Product',
            'category': 'growth'
        },
        'gdp_real': {
            'fred_id': 'GDPC1',
            'name': 'Real Gross Domestic Product',
            'category': 'growth'
        },
        'gdp_growth': {
            'fred_id': 'A191RL1Q225SBEA',
            'name': 'Real GDP Growth Rate',
            'category': 'growth'
        },
        
        # Inflation Indicators
        'cpi': {
            'fred_id': 'CPIAUCSL',
            'name': 'Consumer Price Index',
            'category': 'inflation'
        },
        'core_cpi': {
            'fred_id': 'CPILFESL',
            'name': 'Core Consumer Price Index',
            'category': 'inflation'
        },
        'pce': {
            'fred_id': 'PCEPI',
            'name': 'Personal Consumption Expenditures Price Index',
            'category': 'inflation'
        },
        'core_pce': {
            'fred_id': 'PCEPILFE',
            'name': 'Core Personal Consumption Expenditures Price Index',
            'category': 'inflation'
        },
        
        # Employment Indicators
        'unemployment': {
            'fred_id': 'UNRATE',
            'name': 'Unemployment Rate',
            'category': 'employment'
        },
        'nonfarm_payrolls': {
            'fred_id': 'PAYEMS',
            'name': 'Total Nonfarm Payrolls',
            'category': 'employment'
        },
        'labor_force_participation': {
            'fred_id': 'CIVPART',
            'name': 'Labor Force Participation Rate',
            'category': 'employment'
        },
        'jobless_claims': {
            'fred_id': 'ICSA',
            'name': 'Initial Jobless Claims',
            'category': 'employment'
        },
        
        # Monetary Policy Indicators
        'fed_rate': {
            'fred_id': 'FEDFUNDS',
            'name': 'Federal Funds Rate',
            'category': 'monetary'
        },
        '10y_treasury': {
            'fred_id': 'GS10',
            'name': '10-Year Treasury Constant Maturity Rate',
            'category': 'monetary'
        },
        '2y_treasury': {
            'fred_id': 'GS2',
            'name': '2-Year Treasury Constant Maturity Rate',
            'category': 'monetary'
        },
        'yield_curve': {
            'fred_id': 'T10Y2Y',
            'name': '10-Year Treasury Constant Maturity Minus 2-Year Treasury',
            'category': 'monetary'
        },
        
        # Consumer and Business Confidence
        'consumer_confidence': {
            'fred_id': 'CSCICP03USM665S',
            'name': 'Consumer Confidence Index',
            'category': 'sentiment'
        },
        'consumer_sentiment': {
            'fred_id': 'UMCSENT',
            'name': 'University of Michigan Consumer Sentiment',
            'category': 'sentiment'
        },
        
        # Housing Market
        'housing_starts': {
            'fred_id': 'HOUST',
            'name': 'Housing Starts',
            'category': 'housing'
        },
        'home_sales': {
            'fred_id': 'EXHOSLUSM495S',
            'name': 'Existing Home Sales',
            'category': 'housing'
        },
        
        # Industrial and Manufacturing
        'industrial_production': {
            'fred_id': 'INDPRO',
            'name': 'Industrial Production Index',
            'category': 'industrial'
        },
        'capacity_utilization': {
            'fred_id': 'TCU',
            'name': 'Capacity Utilization',
            'category': 'industrial'
        },
        
        # Trade and International
        'trade_balance': {
            'fred_id': 'BOPGSTB',
            'name': 'Trade Balance: Goods and Services',
            'category': 'trade'
        }
    }
    
    # Alpha Vantage Economic Indicators
    ALPHA_VANTAGE_INDICATORS: Dict[str, str] = {
        'real_gdp': 'REAL_GDP',
        'cpi_monthly': 'CPI',
        'inflation': 'INFLATION',
        'retail_sales': 'RETAIL_SALES',
        'durables': 'DURABLES',
        'unemployment_rate': 'UNEMPLOYMENT',
        'nonfarm_payroll': 'NONFARM_PAYROLL'
    }
    
    # Regional Economic Data
    REGIONAL_INDICATORS: Dict[str, str] = {
        'california_unemployment': 'CAUR',
        'texas_unemployment': 'TXUR',
        'new_york_unemployment': 'NYUR',
        'florida_unemployment': 'FLUR'
    }
    
    # International Comparison Indicators
    INTERNATIONAL_INDICATORS: Dict[str, str] = {
        'canada_gdp': 'CANGDPNQDSMEI',
        'uk_gdp': 'GBRRGDPQDSNAQ',
        'germany_gdp': 'DEUQ',
        'japan_gdp': 'JPNRGDPQDSNAQ',
        'china_gdp': 'CHNGDPNQDSMEI'
    }

    @classmethod
    def validate(cls) -> None:
        """Validate configuration and required environment variables"""
        config = cls()
        
        # Check required API keys
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if not config.ALPHA_VANTAGE_API_KEY:
            warnings.warn("ALPHA_VANTAGE_API_KEY not found. Alpha Vantage data will not be available.")
        
        if not config.FRED_API_KEY:
            warnings.warn("FRED_API_KEY not found. Using FRED without API key (lower rate limits).")
        
        # Create output directories if they don't exist
        os.makedirs(config.CHART_OUTPUT_DIR, exist_ok=True)
        os.makedirs(config.REPORT_OUTPUT_DIR, exist_ok=True)
        os.makedirs(config.DATA_CACHE_DIR, exist_ok=True)
        
        print("✅ Economic Analysis configuration validated successfully")

    @classmethod
    def get_indicator_by_category(cls, category: str) -> Dict[str, Dict[str, str]]:
        """Get all indicators for a specific category"""
        config = cls()
        return {
            key: value for key, value in config.CORE_INDICATORS.items() 
            if value.get('category') == category
        }
    
    @classmethod
    def get_analysis_indicators(cls, analysis_type: str) -> List[str]:
        """Get recommended indicators for specific analysis type"""
        indicator_mapping = {
            'comprehensive': list(cls.CORE_INDICATORS.keys()),
            'gdp_focus': ['gdp', 'gdp_real', 'gdp_growth', 'industrial_production', 'capacity_utilization'],
            'inflation_focus': ['cpi', 'core_cpi', 'pce', 'core_pce', 'fed_rate'],
            'industry_performance': ['manufacturing_pmi', 'retail_sales', 'construction_spending', 'business_inventories', 'factory_orders', 'industrial_production'],
            'market_trend': ['corporate_profits', 'business_investment', 'credit_growth', 'stock_market_cap', '10y_treasury', 'consumer_confidence']
        }
        
        return indicator_mapping.get(analysis_type, ['gdp', 'cpi', 'industrial_production', 'retail_sales'])

# Export configuration instance
Config = EconomicConfig