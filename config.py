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

class EconomicConfig:
    """Configuration class for economic analysis system"""
    
    def __init__(self):
        # API Keys and Authentication
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.FRED_API_KEY = os.getenv('FRED_API_KEY')
        
        # LangSmith Configuration (Optional)
        self.LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')
        self.LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'true')
        self.LANGCHAIN_ENDPOINT = os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
        self.LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT', 'economic-analysis')
        
        # Model Configuration
        self.DEFAULT_MODEL = "gpt-4"
        self.TEMPERATURE = 0.2
        self.MAX_TOKENS = 4000
        
        # Data Source Configuration
        self.DEFAULT_PERIOD = "5y"
        self.DEFAULT_FREQUENCY = "q"
        
        # Analysis Configuration
        self.ANALYSIS_TYPES = [
            "comprehensive", "gdp_focus", "inflation_focus", "industry_performance", "market_trend",
            "tech_industry_performance", "healthcare_industry_performance", "finance_industry_performance",
            "energy_industry_performance", "supply_chain_analysis"
        ]
        
        # Output Directories
        self.CHART_OUTPUT_DIR = "charts"
        self.REPORT_OUTPUT_DIR = "reports"
        self.DATA_CACHE_DIR = "data_cache"
        
        # Rate Limiting
        self.FRED_RATE_LIMIT = 120
        self.ALPHA_VANTAGE_RATE_LIMIT = 5
        self.YAHOO_RATE_LIMIT = 2000
        
        # Economic Indicators Configuration
        self.CORE_INDICATORS = {
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
            
            # Employment Indicators (kept for comprehensive analysis)
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
            
            # Monetary Policy Indicators (kept for comprehensive analysis)
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
            },
            
            # Tech Industry Specific Indicators
            'tech_employment': {
                'fred_id': 'CES5051000001',  # Computer Systems Design Employment
                'name': 'Technology Sector Employment',
                'category': 'tech'
            },
            'software_employment': {
                'fred_id': 'CES5051200001',  # Software Publishers Employment  
                'name': 'Software Services Employment',
                'category': 'tech'
            },
            'tech_production': {
                'fred_id': 'IPG334111N',  # Computer and Electronic Product Manufacturing
                'name': 'Technology Product Manufacturing',
                'category': 'tech'
            },
            'semiconductor_shipments': {
                'fred_id': 'NEWORDERS',  # Use as proxy for semiconductor activity
                'name': 'Semiconductor Industry Activity',
                'category': 'tech'
            },

            # Healthcare Industry Indicators
            'healthcare_employment': {
                'fred_id': 'CES6562000001',  # Healthcare Employment
                'name': 'Healthcare Sector Employment', 
                'category': 'healthcare'
            },
            'healthcare_spending': {
                'fred_id': 'HLTHCPCPIUS',  # Healthcare CPI
                'name': 'Healthcare Price Index',
                'category': 'healthcare'
            },

            # Finance Industry Indicators  
            'finance_employment': {
                'fred_id': 'CES5552000001',  # Finance and Insurance Employment
                'name': 'Finance Sector Employment',
                'category': 'finance'
            },
            'bank_lending': {
                'fred_id': 'TOTLL',  # Total Loans and Leases
                'name': 'Bank Lending Activity', 
                'category': 'finance'
            },

            # Energy Industry Indicators
            'energy_employment': {
                'fred_id': 'CES1021100001',  # Oil and Gas Employment
                'name': 'Energy Sector Employment',
                'category': 'energy'
            },
            'oil_production': {
                'fred_id': 'WCRFPUS',  # US Crude Oil Production
                'name': 'US Oil Production',
                'category': 'energy'
            },

            # Supply Chain Indicators
            'supply_chain_pressure': {
                'fred_id': 'GSCPI',  # Global Supply Chain Pressure Index
                'name': 'Supply Chain Pressure Index',
                'category': 'supply_chain'
            },
            'transportation_costs': {
                'fred_id': 'CPIUFDTR',  # Transportation CPI
                'name': 'Transportation Cost Index',
                'category': 'supply_chain'
            },

            # General Industry Performance Indicators
            'manufacturing_pmi': {
                'fred_id': 'MANEMP',
                'name': 'Manufacturing Employment',
                'category': 'industry'
            },
            'retail_sales': {
                'fred_id': 'RSAFS',
                'name': 'Advance Retail Sales',
                'category': 'industry'
            },
            'construction_spending': {
                'fred_id': 'TTLCONS',
                'name': 'Total Construction Spending',
                'category': 'industry'
            },
            'business_inventories': {
                'fred_id': 'BUSINV',
                'name': 'Total Business Inventories',
                'category': 'industry'
            },
            'factory_orders': {
                'fred_id': 'AMTMNO',
                'name': 'Manufacturers New Orders',
                'category': 'industry'
            },
            
            # Market Trend Indicators
            'corporate_profits': {
                'fred_id': 'CP',
                'name': 'Corporate Profits After Tax',
                'category': 'market'
            },
            'business_investment': {
                'fred_id': 'PNFI',
                'name': 'Private Nonresidential Fixed Investment',
                'category': 'market'
            },
            'credit_growth': {
                'fred_id': 'TOTLL',
                'name': 'Total Consumer Credit Outstanding',
                'category': 'market'
            },
            'stock_market_cap': {
                'fred_id': 'DDDM01USA156NWDB',
                'name': 'Stock Market Capitalization to GDP',
                'category': 'market'
            }
        }
        
        # Alpha Vantage Economic Indicators
        self.ALPHA_VANTAGE_INDICATORS = {
            'real_gdp': 'REAL_GDP',
            'cpi_monthly': 'CPI',
            'inflation': 'INFLATION',
            'retail_sales': 'RETAIL_SALES',
            'durables': 'DURABLES',
            'consumer_sentiment': 'CONSUMER_SENTIMENT',
            'business_sentiment': 'BUSINESS_SENTIMENT'
        }
        
        # Regional Economic Data
        self.REGIONAL_INDICATORS = {
            'california_unemployment': 'CAUR',
            'texas_unemployment': 'TXUR',
            'new_york_unemployment': 'NYUR',
            'florida_unemployment': 'FLUR'
        }
        
        # International Comparison Indicators
        self.INTERNATIONAL_INDICATORS = {
            'canada_gdp': 'CANGDPNQDSMEI',
            'uk_gdp': 'GBRRGDPQDSNAQ',
            'germany_gdp': 'DEUQ',
            'japan_gdp': 'JPNRGDPQDSNAQ',
            'china_gdp': 'CHNGDPNQDSMEI'
        }

    #@classmethod
    def validate(self) -> None:
        """Validate configuration and required environment variables"""
        #config = cls()
        
        # Check required API keys
        if not self.OPENAI_API_KEY: #config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if not self.ALPHA_VANTAGE_API_KEY: #config.ALPHA_VANTAGE_API_KEY:
            warnings.warn("ALPHA_VANTAGE_API_KEY not found. Alpha Vantage data will not be available.")
        
        if not self.FRED_API_KEY: #config.FRED_API_KEY:
            warnings.warn("FRED_API_KEY not found. Using FRED without API key (lower rate limits).")
        
        # Create output directories if they don't exist
        os.makedirs(self.CHART_OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.REPORT_OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.DATA_CACHE_DIR, exist_ok=True)
        
        print("✅ Economic Analysis configuration validated successfully")

    def get_indicator_by_category(self, category: str) -> Dict[str, Dict[str, str]]:
        """Get all indicators for a specific category"""
        return {
            key: value for key, value in self.CORE_INDICATORS.items() 
            if value.get('category') == category
        }
    
    def get_analysis_indicators(self, analysis_type: str) -> List[str]:
        """Get recommended indicators for specific analysis type"""
        indicator_mapping = {
            'gdp_focus': ['gdp', 'gdp_real', 'gdp_growth', 'industrial_production', 'capacity_utilization'],
            'inflation_focus': ['cpi', 'core_cpi', 'pce', 'core_pce', 'fed_rate'],
            'market_trend': ['corporate_profits', 'business_investment', 'credit_growth', 'stock_market_cap', '10y_treasury', 'consumer_confidence'],
            'industry_performance': ['tech_employment', 'software_employment', 'tech_production', 'healthcare_employment', 'healthcare_spending', 'finance_employment', 'bank_lending', 'energy_employment', 'oil_production', 'supply_chain_pressure', 'transportation_costs'],
            'tech_industry_performance': ['tech_employment', 'software_employment', 'tech_production', 'semiconductor_shipments', 'business_investment', 'industrial_production'],
            'healthcare_industry_performance': ['healthcare_employment', 'healthcare_spending', 'business_investment'],
            'finance_industry_performance': ['finance_employment', 'bank_lending', 'fed_rate', '10y_treasury'],
            'energy_industry_performance': ['energy_employment', 'oil_production', 'business_investment'],
            'supply_chain_performance': ['supply_chain_pressure', 'transportation_costs', 'industrial_production']
        }
        
        return indicator_mapping.get(analysis_type, ['gdp', 'cpi', 'industrial_production'])

# Export configuration instance
Config = EconomicConfig()