from fredapi import Fred
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from economic_config import EconomicConfig

@dataclass
class EconomicData:
    """Data structure to hold economic information"""
    series_id: str
    series_name: str
    data: pd.Series
    units: str
    frequency: str
    last_updated: datetime
    notes: str
    
    def get_latest_value(self) -> Optional[float]:
        """Get the most recent value"""
        if self.data is not None and not self.data.empty:
            return self.data.iloc[-1]
        return None
    
    def get_yoy_change(self) -> Optional[float]:
        """Get year-over-year change"""
        if self.data is not None and len(self.data) >= 12:
            try:
                current = self.data.iloc[-1]
                year_ago = self.data.iloc[-13] if len(self.data) >= 13 else self.data.iloc[0]
                return ((current - year_ago) / year_ago) * 100
            except:
                return None
        return None

class EconomicDataAgent:
    """Agent for collecting and processing economic data from FRED"""
    
    def __init__(self):
        self.fred = Fred(api_key=EconomicConfig.FRED_API_KEY)
        
    def fetch_economic_data(self, series_id: str, start_date: str = None, 
                          end_date: str = None) -> EconomicData:
        """Fetch data for a specific FRED series"""
        try:
            # Get series info
            info = self.fred.get_series_info(series_id)
            
            # Fetch the data
            data = self.fred.get_series(
                series_id, 
                start=start_date, 
                end=end_date
            )
            
            return EconomicData(
                series_id=series_id,
                series_name=info['title'],
                data=data,
                units=info['units'],
                frequency=info['frequency'],
                last_updated=info['last_updated'],
                notes=info['notes']
            )
            
        except Exception as e:
            print(f"Error fetching data for {series_id}: {str(e)}")
            return None
    
    def fetch_gdp_indicators(self, period: str = "10y") -> Dict[str, EconomicData]:
        """Fetch GDP-related indicators"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(period[:-1]) * 365)
        
        gdp_data = {}
        
        gdp_series = ["GDP", "GDP_GROWTH", "GDP_PER_CAPITA"]
        for series_key in gdp_series:
            series_id = EconomicConfig.FRED_SERIES[series_key]
            data = self.fetch_economic_data(
                series_id, 
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            if data:
                gdp_data[series_key.lower()] = data
                
        return gdp_data
    
    def fetch_inflation_indicators(self, period: str = "10y") -> Dict[str, EconomicData]:
        """Fetch inflation-related indicators"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(period[:-1]) * 365)
        
        inflation_data = {}
        
        inflation_series = ["CPI", "CORE_CPI", "PCE", "INFLATION_RATE"]
        for series_key in inflation_series:
            series_id = EconomicConfig.FRED_SERIES[series_key]
            data = self.fetch_economic_data(
                series_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            if data:
                inflation_data[series_key.lower()] = data
                
        return inflation_data
    
    def fetch_market_trends(self, period: str = "10y") -> Dict[str, EconomicData]:
        """Fetch market trend indicators"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(period[:-1]) * 365)
        
        market_data = {}
        
        market_series = ["UNEMPLOYMENT", "FED_FUNDS", "10Y_TREASURY", 
                        "CONSUMER_CONFIDENCE", "INDUSTRIAL_PRODUCTION"]
        for series_key in market_series:
            series_id = EconomicConfig.FRED_SERIES[series_key]
            data = self.fetch_economic_data(
                series_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            if data:
                market_data[series_key.lower()] = data
                
        return market_data
    
    def fetch_industry_performance(self, period: str = "10y") -> Dict[str, Dict[str, EconomicData]]:
        """Fetch industry-specific performance data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(period[:-1]) * 365)
        
        industry_data = {
            "tech": {},
            "healthcare": {},
            "energy": {}
        }
        
        # Tech industry
        tech_series = ["TECH_EMPLOYMENT", "TECH_WAGES"]
        for series_key in tech_series:
            series_id = EconomicConfig.FRED_SERIES[series_key]
            data = self.fetch_economic_data(
                series_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            if data:
                industry_data["tech"][series_key.lower()] = data
        
        # Healthcare industry
        healthcare_series = ["HEALTHCARE_EMPLOYMENT", "HEALTHCARE_CPI"]
        for series_key in healthcare_series:
            series_id = EconomicConfig.FRED_SERIES[series_key]
            data = self.fetch_economic_data(
                series_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            if data:
                industry_data["healthcare"][series_key.lower()] = data
        
        # Energy industry
        energy_series = ["ENERGY_EMPLOYMENT", "OIL_PRICE", "NATURAL_GAS"]
        for series_key in energy_series:
            series_id = EconomicConfig.FRED_SERIES[series_key]
            data = self.fetch_economic_data(
                series_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            if data:
                industry_data["energy"][series_key.lower()] = data
                
        return industry_data
    
    def calculate_economic_correlations(self, data_dict: Dict[str, EconomicData]) -> pd.DataFrame:
        """Calculate correlations between economic indicators"""
        # Combine all series into a DataFrame
        combined_df = pd.DataFrame()
        
        for key, econ_data in data_dict.items():
            if econ_data and econ_data.data is not None:
                combined_df[key] = econ_data.data
        
        if not combined_df.empty:
            return combined_df.corr()
        return pd.DataFrame()
    
    def create_economic_dashboard_chart(self, gdp_data: Dict[str, EconomicData],
                                      inflation_data: Dict[str, EconomicData]) -> go.Figure:
        """Create a comprehensive economic dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('GDP Growth', 'Inflation Rate', 'GDP Level', 'Core CPI'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # GDP Growth
        if 'gdp_growth' in gdp_data and gdp_data['gdp_growth']:
            fig.add_trace(
                go.Scatter(
                    x=gdp_data['gdp_growth'].data.index,
                    y=gdp_data['gdp_growth'].data.values,
                    name='GDP Growth Rate',
                    line=dict(color='blue')
                ),
                row=1, col=1
            )
        
        # Inflation Rate
        if 'inflation_rate' in inflation_data and inflation_data['inflation_rate']:
            fig.add_trace(
                go.Scatter(
                    x=inflation_data['inflation_rate'].data.index,
                    y=inflation_data['inflation_rate'].data.values,
                    name='Inflation Rate',
                    line=dict(color='red')
                ),
                row=1, col=2
            )
        
        # GDP Level
        if 'gdp' in gdp_data and gdp_data['gdp']:
            fig.add_trace(
                go.Scatter(
                    x=gdp_data['gdp'].data.index,
                    y=gdp_data['gdp'].data.values,
                    name='GDP',
                    line=dict(color='green')
                ),
                row=2, col=1
            )
        
        # Core CPI
        if 'core_cpi' in inflation_data and inflation_data['core_cpi']:
            fig.add_trace(
                go.Scatter(
                    x=inflation_data['core_cpi'].data.index,
                    y=inflation_data['core_cpi'].data.values,
                    name='Core CPI',
                    line=dict(color='orange')
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            title_text="Economic Indicators Dashboard",
            showlegend=True
        )
        
        return fig