import os
from dotenv import load_dotenv

load_dotenv()

# Configuration settings for Economic Systems
class EconomicConfig:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    FRED_API_KEY = os.getenv("FRED_API_KEY")
    DEFAULT_MODEL = "gpt-4"
    
    # Economic analysis parameters
    DEFAULT_PERIOD = "5y"  # 10 years for economic trends
    
    # FRED Series IDs for key economic indicators
    FRED_SERIES = {
        # GDP Data
        "GDP": "GDP",                    # Gross Domestic Product
        "GDP_GROWTH": "A191RL1Q225SBEA",  # Real GDP Growth Rate
        "GDP_PER_CAPITA": "A939RX0Q048SBEA",  # Real GDP per Capita
        
        # Inflation Data
        "CPI": "CPIAUCSL",               # Consumer Price Index
        "CORE_CPI": "CPILFESL",          # Core CPI (ex food & energy)
        "PCE": "PCEPI",                  # PCE Price Index
        "INFLATION_RATE": "FPCPITOTLZGUSA", # Inflation Rate
        
        # Market Trends
        "UNEMPLOYMENT": "UNRATE",        # Unemployment Rate
        "FED_FUNDS": "FEDFUNDS",         # Federal Funds Rate
        "10Y_TREASURY": "GS10",          # 10-Year Treasury Rate
        "CONSUMER_CONFIDENCE": "UMCSENT", # Consumer Sentiment
        "INDUSTRIAL_PRODUCTION": "INDPRO", # Industrial Production Index
        
        # Industry Performance - Tech
        "TECH_EMPLOYMENT": "CES5051200001", # Software Publishers Employment
        "TECH_WAGES": "CES5051200001",      # Use same series for wages (employment data)
        
        # Industry Performance - Healthcare
        "HEALTHCARE_EMPLOYMENT": "CES6562000001", # Healthcare Employment
        "HEALTHCARE_CPI": "CUUR0000SAM",          # Medical Care CPI (original)
        
        # Industry Performance - Energy  
        "ENERGY_EMPLOYMENT": "CES1021100001", # Oil and Gas Extraction Employment
        "OIL_PRICE": "DCOILWTICO",            # Crude Oil Prices: West Texas Intermediate
        "NATURAL_GAS": "DHHNGSP",             # Henry Hub Natural Gas Spot Price
    }
    
    # Report settings
    REPORT_OUTPUT_DIR = "economic_reports"
    CHART_OUTPUT_DIR = "economic_charts"
    
    # Analysis focus areas
    FOCUS_INDUSTRIES = ["tech", "healthcare", "energy"]
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not cls.FRED_API_KEY:
            raise ValueError("FRED_API_KEY environment variable is required")
        
        # Create output directories if they don't exist
        os.makedirs(cls.REPORT_OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.CHART_OUTPUT_DIR, exist_ok=True)