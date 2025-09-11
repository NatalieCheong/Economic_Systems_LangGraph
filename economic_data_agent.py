#!/usr/bin/env python3
"""
Economic Data Agent - Fetches and processes economic data from multiple sources
"""

import pandas as pd
import numpy as np
import yfinance as yf
import requests
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from config import Config
import warnings
import json
import os

@dataclass
class EconomicIndicator:
    """Data structure for individual economic indicators"""
    indicator_id: str
    name: str
    category: str
    data: pd.DataFrame
    source: str
    last_updated: datetime
    frequency: str
    units: str
    seasonal_adjustment: str
    notes: str

@dataclass
class EconomicData:
    """Comprehensive economic data structure"""
    analysis_type: str
    period: str
    indicators: Dict[str, EconomicIndicator]
    market_data: Dict[str, pd.DataFrame]
    regional_data: Dict[str, EconomicIndicator]
    international_data: Dict[str, EconomicIndicator]
    summary_statistics: Dict[str, Any]
    data_quality_report: Dict[str, Any]

class EconomicDataAgent:
    """Agent responsible for fetching and processing economic data from multiple sources"""
    
    def __init__(self):
        self.config = Config()
        self.fred_base_url = "https://api.stlouisfed.org/fred"
        self.alpha_vantage_base_url = "https://www.alphavantage.co/query"
        self.data_cache = {}
        
    def fetch_comprehensive_economic_data(self, 
                                        analysis_type: str = "comprehensive",
                                        period: str = None,
                                        include_regional: bool = True,
                                        include_international: bool = True,
                                        include_market_data: bool = True) -> EconomicData:
        """
        Fetch comprehensive economic data from multiple sources
        
        Args:
            analysis_type: Type of economic analysis ('comprehensive', 'gdp_focus', etc.)
            period: Data period ('1y', '2y', '5y', '10y')
            include_regional: Whether to include regional economic data
            include_international: Whether to include international comparison data
            include_market_data: Whether to include related market data
        
        Returns:
            EconomicData object containing all relevant economic information
        """
        period = period or self.config.DEFAULT_PERIOD
        
        print(f"📊 Starting comprehensive economic data collection...")
        print(f"Analysis Type: {analysis_type}")
        print(f"Period: {period}")
        print("-" * 50)
        
        # Get indicators for the specified analysis type
        indicator_list = self.config.get_analysis_indicators(analysis_type)
        
        # Fetch core economic indicators
        print("🏛️ Fetching core economic indicators from FRED...")
        core_indicators = self._fetch_fred_indicators(indicator_list, period)
        
        # Fetch Alpha Vantage data
        print("📈 Fetching additional indicators from Alpha Vantage...")
        alpha_vantage_data = self._fetch_alpha_vantage_data(period)
        
        # Merge Alpha Vantage data with core indicators
        all_indicators = {**core_indicators, **alpha_vantage_data}
        
        # Fetch regional data if requested
        regional_data = {}
        if include_regional:
            print("🗺️ Fetching regional economic data...")
            regional_data = self._fetch_regional_data(period)
        
        # Fetch international data if requested
        international_data = {}
        if include_international:
            print("🌍 Fetching international comparison data...")
            international_data = self._fetch_international_data(period)
        
        # Fetch related market data if requested
        market_data = {}
        if include_market_data:
            print("💹 Fetching related market data...")
            market_data = self._fetch_market_data(period)
        
        # Calculate summary statistics
        print("📊 Calculating summary statistics...")
        summary_stats = self._calculate_summary_statistics(all_indicators)
        
        # Generate data quality report
        print("🔍 Generating data quality report...")
        quality_report = self._generate_data_quality_report(all_indicators)
        
        economic_data = EconomicData(
            analysis_type=analysis_type,
            period=period,
            indicators=all_indicators,
            market_data=market_data,
            regional_data=regional_data,
            international_data=international_data,
            summary_statistics=summary_stats,
            data_quality_report=quality_report
        )
        
        print("✅ Economic data collection completed successfully")
        return economic_data
    
    def _fetch_fred_indicators(self, indicator_list: List[str], period: str) -> Dict[str, EconomicIndicator]:
        """Fetch economic indicators from FRED API"""
        indicators = {}
        start_date = self._calculate_start_date(period)
        
        for indicator_key in indicator_list:
            if indicator_key not in self.config.CORE_INDICATORS:
                continue
                
            indicator_config = self.config.CORE_INDICATORS[indicator_key]
            fred_id = indicator_config['fred_id']
            
            try:
                # Fetch series information
                series_info = self._get_fred_series_info(fred_id)
                
                # Fetch actual data
                data_df = self._get_fred_series_data(fred_id, start_date)
                
                if not data_df.empty:
                    indicator = EconomicIndicator(
                        indicator_id=indicator_key,
                        name=indicator_config['name'],
                        category=indicator_config['category'],
                        data=data_df,
                        source='FRED',
                        last_updated=datetime.now(),
                        frequency=series_info.get('frequency', 'Unknown'),
                        units=series_info.get('units', 'Unknown'),
                        seasonal_adjustment=series_info.get('seasonal_adjustment', 'Unknown'),
                        notes=series_info.get('notes', '')
                    )
                    
                    indicators[indicator_key] = indicator
                    print(f"✅ Fetched {indicator_config['name']} from FRED")
                    
                # Rate limiting
                time.sleep(0.5)  # FRED rate limiting
                
            except Exception as e:
                print(f"❌ Error fetching {indicator_config['name']} from FRED: {e}")
                continue
        
        return indicators
    
    def _get_fred_series_info(self, series_id: str) -> Dict[str, Any]:
        """Get series information from FRED"""
        params = {
            'series_id': series_id,
            'api_key': self.config.FRED_API_KEY,
            'file_type': 'json'
        }
        
        # Remove api_key if not available
        if not self.config.FRED_API_KEY:
            del params['api_key']
        
        try:
            response = requests.get(f"{self.fred_base_url}/series", params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'seriess' in data and len(data['seriess']) > 0:
                return data['seriess'][0]
            
        except Exception as e:
            print(f"Warning: Could not fetch series info for {series_id}: {e}")
        
        return {}
    
    def _get_fred_series_data(self, series_id: str, start_date: str) -> pd.DataFrame:
        """Get series data from FRED"""
        params = {
            'series_id': series_id,
            'api_key': self.config.FRED_API_KEY,
            'file_type': 'json',
            'observation_start': start_date
        }
        
        # Remove api_key if not available
        if not self.config.FRED_API_KEY:
            del params['api_key']
        
        try:
            response = requests.get(f"{self.fred_base_url}/series/observations", params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'observations' in data:
                observations = data['observations']
                
                # Convert to DataFrame
                df_data = []
                for obs in observations:
                    if obs['value'] != '.':  # FRED uses '.' for missing values
                        try:
                            df_data.append({
                                'date': pd.to_datetime(obs['date']),
                                'value': float(obs['value'])
                            })
                        except (ValueError, TypeError):
                            continue
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    df.set_index('date', inplace=True)
                    df.sort_index(inplace=True)
                    return df
            
        except Exception as e:
            print(f"Error fetching data for {series_id}: {e}")
        
        return pd.DataFrame()
    
    def _fetch_alpha_vantage_data(self, period: str) -> Dict[str, EconomicIndicator]:
        """Fetch economic data from Alpha Vantage"""
        indicators = {}
        
        if not self.config.ALPHA_VANTAGE_API_KEY:
            print("⚠️ Alpha Vantage API key not available, skipping Alpha Vantage data")
            return indicators
        
        for indicator_key, function_name in self.config.ALPHA_VANTAGE_INDICATORS.items():
            try:
                params = {
                    'function': function_name,
                    'apikey': self.config.ALPHA_VANTAGE_API_KEY,
                    'datatype': 'json'
                }
                
                response = requests.get(self.alpha_vantage_base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Parse Alpha Vantage response (structure varies by indicator)
                df = self._parse_alpha_vantage_response(data, function_name)
                
                if not df.empty:
                    indicator = EconomicIndicator(
                        indicator_id=indicator_key,
                        name=function_name.replace('_', ' ').title(),
                        category='alpha_vantage',
                        data=df,
                        source='Alpha Vantage',
                        last_updated=datetime.now(),
                        frequency='Unknown',
                        units='Unknown',
                        seasonal_adjustment='Unknown',
                        notes=f'Data from Alpha Vantage {function_name} function'
                    )
                    
                    indicators[indicator_key] = indicator
                    print(f"✅ Fetched {function_name} from Alpha Vantage")
                
                # Rate limiting for Alpha Vantage (free tier: 5 calls per minute)
                time.sleep(12)
                
            except Exception as e:
                print(f"❌ Error fetching {function_name} from Alpha Vantage: {e}")
                continue
        
        return indicators
    
    def _parse_alpha_vantage_response(self, data: Dict, function_name: str) -> pd.DataFrame:
        """Parse Alpha Vantage API response into DataFrame"""
        try:
            # Alpha Vantage responses have different structures
            # Look for the data key that contains the time series
            data_key = None
            for key in data.keys():
                if 'data' in key.lower() or 'time series' in key.lower():
                    data_key = key
                    break
            
            if not data_key:
                # Try common patterns
                possible_keys = ['data', 'Annual Time Series', 'Quarterly Time Series', 'Monthly Time Series']
                for key in possible_keys:
                    if key in data:
                        data_key = key
                        break
            
            if data_key and data_key in data:
                time_series = data[data_key]
                
                df_data = []
                for date_str, values in time_series.items():
                    try:
                        date_obj = pd.to_datetime(date_str)
                        # Get the value (Alpha Vantage usually has one main value per indicator)
                        value = None
                        if isinstance(values, dict):
                            # Find the main value key
                            for val_key, val in values.items():
                                if 'value' in val_key.lower() or len(values) == 1:
                                    value = float(val)
                                    break
                        elif isinstance(values, (int, float, str)):
                            value = float(values)
                        
                        if value is not None:
                            df_data.append({'date': date_obj, 'value': value})
                    
                    except (ValueError, TypeError, KeyError):
                        continue
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    df.set_index('date', inplace=True)
                    df.sort_index(inplace=True)
                    return df
                    
        except Exception as e:
            print(f"Error parsing Alpha Vantage response for {function_name}: {e}")
        
        return pd.DataFrame()
    
    def _fetch_regional_data(self, period: str) -> Dict[str, EconomicIndicator]:
        """Fetch regional economic data"""
        regional_indicators = {}
        start_date = self._calculate_start_date(period)
        
        for region_key, fred_id in self.config.REGIONAL_INDICATORS.items():
            try:
                data_df = self._get_fred_series_data(fred_id, start_date)
                
                if not data_df.empty:
                    indicator = EconomicIndicator(
                        indicator_id=region_key,
                        name=region_key.replace('_', ' ').title(),
                        category='regional',
                        data=data_df,
                        source='FRED',
                        last_updated=datetime.now(),
                        frequency='Monthly',
                        units='Percent',
                        seasonal_adjustment='Seasonally Adjusted',
                        notes=f'Regional data for {region_key}'
                    )
                    
                    regional_indicators[region_key] = indicator
                    print(f"✅ Fetched regional data: {region_key}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error fetching regional data {region_key}: {e}")
                continue
        
        return regional_indicators
    
    def _fetch_international_data(self, period: str) -> Dict[str, EconomicIndicator]:
        """Fetch international comparison data"""
        international_indicators = {}
        start_date = self._calculate_start_date(period)
        
        for country_key, fred_id in self.config.INTERNATIONAL_INDICATORS.items():
            try:
                data_df = self._get_fred_series_data(fred_id, start_date)
                
                if not data_df.empty:
                    indicator = EconomicIndicator(
                        indicator_id=country_key,
                        name=country_key.replace('_', ' ').title(),
                        category='international',
                        data=data_df,
                        source='FRED',
                        last_updated=datetime.now(),
                        frequency='Quarterly',
                        units='Various',
                        seasonal_adjustment='Seasonally Adjusted',
                        notes=f'International data for {country_key}'
                    )
                    
                    international_indicators[country_key] = indicator
                    print(f"✅ Fetched international data: {country_key}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error fetching international data {country_key}: {e}")
                continue
        
        return international_indicators
    
    def _fetch_market_data(self, period: str) -> Dict[str, pd.DataFrame]:
        """Fetch related market data using Yahoo Finance"""
        market_symbols = {
            'sp500': '^GSPC',           # S&P 500
            'nasdaq': '^IXIC',          # NASDAQ
            'dow': '^DJI',              # Dow Jones
            'vix': '^VIX',              # Volatility Index
            'dxy': 'DX-Y.NYB',          # US Dollar Index
            'gold': 'GC=F',             # Gold Futures
            'oil': 'CL=F',              # Crude Oil Futures
            'treasury_etf': 'TLT',      # 20+ Year Treasury Bond ETF
            'tips': 'SCHP'              # TIPS ETF
        }
        
        market_data = {}
        
        for name, symbol in market_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period=period)
                
                if not hist_data.empty:
                    market_data[name] = hist_data
                    print(f"✅ Fetched market data: {name}")
                
                time.sleep(0.1)  # Small delay to be respectful
                
            except Exception as e:
                print(f"❌ Error fetching market data {name}: {e}")
                continue
        
        return market_data
    
    def _calculate_start_date(self, period: str) -> str:
        """Calculate start date based on period"""
        end_date = datetime.now()
        
        period_mapping = {
            '1y': timedelta(days=365),
            '2y': timedelta(days=730),
            '5y': timedelta(days=1825),
            '10y': timedelta(days=3650),
            '20y': timedelta(days=7300)
        }
        
        if period in period_mapping:
            start_date = end_date - period_mapping[period]
        else:
            start_date = end_date - timedelta(days=1825)  # Default to 5 years
        
        return start_date.strftime('%Y-%m-%d')
    
    def _calculate_summary_statistics(self, indicators: Dict[str, EconomicIndicator]) -> Dict[str, Any]:
        """Calculate summary statistics for all indicators"""
        summary_stats = {
            'total_indicators': len(indicators),
            'categories': {},
            'data_ranges': {},
            'latest_values': {},
            'trends': {}
        }
        
        # Group by category
        for indicator_id, indicator in indicators.items():
            category = indicator.category
            if category not in summary_stats['categories']:
                summary_stats['categories'][category] = []
            summary_stats['categories'][category].append(indicator_id)
            
            # Calculate statistics for each indicator
            if not indicator.data.empty:
                data = indicator.data['value']
                
                # Data range
                summary_stats['data_ranges'][indicator_id] = {
                    'start_date': indicator.data.index.min().strftime('%Y-%m-%d'),
                    'end_date': indicator.data.index.max().strftime('%Y-%m-%d'),
                    'observations': len(data)
                }
                
                # Latest value
                summary_stats['latest_values'][indicator_id] = {
                    'value': float(data.iloc[-1]) if len(data) > 0 else None,
                    'date': indicator.data.index[-1].strftime('%Y-%m-%d') if len(data) > 0 else None
                }
                
                # Trend analysis (simple)
                if len(data) >= 2:
                    recent_change = data.iloc[-1] - data.iloc[-2]
                    pct_change = (recent_change / data.iloc[-2]) * 100 if data.iloc[-2] != 0 else 0
                    
                    summary_stats['trends'][indicator_id] = {
                        'recent_change': float(recent_change),
                        'percent_change': float(pct_change),
                        'direction': 'up' if recent_change > 0 else 'down' if recent_change < 0 else 'stable'
                    }
        
        return summary_stats
    
    def _generate_data_quality_report(self, indicators: Dict[str, EconomicIndicator]) -> Dict[str, Any]:
        """Generate data quality report"""
        quality_report = {
            'total_indicators': len(indicators),
            'successful_fetches': 0,
            'failed_fetches': 0,
            'data_completeness': {},
            'data_freshness': {},
            'sources': {},
            'issues': []
        }
        
        for indicator_id, indicator in indicators.items():
            if not indicator.data.empty:
                quality_report['successful_fetches'] += 1
                
                # Data completeness
                total_possible = len(indicator.data)
                actual_data = indicator.data['value'].notna().sum()
                completeness = (actual_data / total_possible) * 100 if total_possible > 0 else 0
                
                quality_report['data_completeness'][indicator_id] = {
                    'completeness_pct': float(completeness),
                    'missing_values': int(total_possible - actual_data),
                    'total_observations': int(total_possible)
                }
                
                # Data freshness
                if not indicator.data.empty:
                    latest_date = indicator.data.index.max()
                    days_old = (datetime.now() - latest_date).days
                    
                    quality_report['data_freshness'][indicator_id] = {
                        'latest_date': latest_date.strftime('%Y-%m-%d'),
                        'days_old': days_old,
                        'freshness': 'fresh' if days_old <= 7 else 'stale' if days_old <= 30 else 'very_stale'
                    }
                
                # Track sources
                source = indicator.source
                if source not in quality_report['sources']:
                    quality_report['sources'][source] = 0
                quality_report['sources'][source] += 1
                
                # Identify issues
                if completeness < 80:
                    quality_report['issues'].append(f"{indicator_id}: Low data completeness ({completeness:.1f}%)")
                
                if days_old > 60:
                    quality_report['issues'].append(f"{indicator_id}: Stale data ({days_old} days old)")
            
            else:
                quality_report['failed_fetches'] += 1
                quality_report['issues'].append(f"{indicator_id}: Failed to fetch data")
        
        return quality_report
    
    def create_economic_dashboard(self, economic_data: EconomicData, save_path: str = None) -> str:
        """Create comprehensive economic dashboard visualization"""
        
        # Set up the plot style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3)
        
        # Main title
        fig.suptitle(f'Economic Analysis Dashboard - {economic_data.analysis_type.title()}', 
                    fontsize=20, fontweight='bold', y=0.95)
        
        # Plot 1: GDP Growth
        if 'gdp_growth' in economic_data.indicators:
            ax1 = fig.add_subplot(gs[0, 0])
            gdp_data = economic_data.indicators['gdp_growth'].data
            ax1.plot(gdp_data.index, gdp_data['value'], linewidth=2, color='#1f77b4')
            ax1.set_title('GDP Growth Rate', fontweight='bold')
            ax1.set_ylabel('Percent')
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        
        # Plot 2: Inflation (CPI)
        if 'cpi' in economic_data.indicators:
            ax2 = fig.add_subplot(gs[0, 1])
            cpi_data = economic_data.indicators['cpi'].data
            # Calculate YoY inflation rate
            cpi_yoy = cpi_data['value'].pct_change(periods=12) * 100
            ax2.plot(cpi_data.index, cpi_yoy, linewidth=2, color='#ff7f0e')
            ax2.set_title('CPI Inflation Rate (YoY)', fontweight='bold')
            ax2.set_ylabel('Percent')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=2, color='red', linestyle='--', alpha=0.5, label='2% Target')
            ax2.legend()
        
        # Plot 3: Unemployment Rate
        if 'unemployment' in economic_data.indicators:
            ax3 = fig.add_subplot(gs[0, 2])
            unemp_data = economic_data.indicators['unemployment'].data
            ax3.plot(unemp_data.index, unemp_data['value'], linewidth=2, color='#2ca02c')
            ax3.set_title('Unemployment Rate', fontweight='bold')
            ax3.set_ylabel('Percent')
            ax3.grid(True, alpha=0.3)
        
        # Plot 4: Federal Funds Rate
        if 'fed_rate' in economic_data.indicators:
            ax4 = fig.add_subplot(gs[1, 0])
            fed_data = economic_data.indicators['fed_rate'].data
            ax4.plot(fed_data.index, fed_data['value'], linewidth=2, color='#d62728')
            ax4.set_title('Federal Funds Rate', fontweight='bold')
            ax4.set_ylabel('Percent')
            ax4.grid(True, alpha=0.3)
        
        # Plot 5: Yield Curve
        if 'yield_curve' in economic_data.indicators:
            ax5 = fig.add_subplot(gs[1, 1])
            yield_data = economic_data.indicators['yield_curve'].data
            ax5.plot(yield_data.index, yield_data['value'], linewidth=2, color='#9467bd')
            ax5.set_title('Yield Curve (10Y-2Y)', fontweight='bold')
            ax5.set_ylabel('Percentage Points')
            ax5.grid(True, alpha=0.3)
            ax5.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Inversion Line')
            ax5.legend()
        
        # Plot 6: Market Performance (S&P 500 if available)
        if 'sp500' in economic_data.market_data:
            ax6 = fig.add_subplot(gs[1, 2])
            sp500_data = economic_data.market_data['sp500']
            ax6.plot(sp500_data.index, sp500_data['Close'], linewidth=2, color='#8c564b')
            ax6.set_title('S&P 500 Index', fontweight='bold')
            ax6.set_ylabel('Index Level')
            ax6.grid(True, alpha=0.3)
        
        # Plot 7: Economic Indicators Heatmap
        ax7 = fig.add_subplot(gs[2, :])
        self._create_indicators_heatmap(ax7, economic_data)
        
        # Plot 8: Data Quality Summary
        ax8 = fig.add_subplot(gs[3, 0])
        self._create_data_quality_chart(ax8, economic_data.data_quality_report)
        
        # Plot 9: Trend Analysis
        ax9 = fig.add_subplot(gs[3, 1:])
        self._create_trend_analysis_chart(ax9, economic_data)
        
        # Save the chart
        if not save_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"{Config.CHART_OUTPUT_DIR}/economic_dashboard_{timestamp}.png"
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"📊 Economic dashboard saved to: {save_path}")
        return save_path
    
    def _create_indicators_heatmap(self, ax, economic_data: EconomicData):
        """Create heatmap of economic indicators performance"""
        try:
            # Prepare data for heatmap
            indicators_data = []
            indicator_names = []
            
            for indicator_id, indicator in economic_data.indicators.items():
                if not indicator.data.empty and len(indicator.data) >= 2:
                    recent_values = indicator.data['value'].tail(12)  # Last 12 periods
                    if len(recent_values) >= 2:
                        pct_changes = recent_values.pct_change().dropna()
                        if len(pct_changes) > 0:
                            avg_change = pct_changes.mean() * 100
                            indicators_data.append(avg_change)
                            indicator_names.append(indicator.name[:20])  # Truncate long names
            
            if indicators_data:
                # Create heatmap data
                heatmap_data = np.array(indicators_data).reshape(-1, 1)
                
                # Create heatmap
                im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto')
                ax.set_yticks(range(len(indicator_names)))
                ax.set_yticklabels(indicator_names, fontsize=8)
                ax.set_xticks([0])
                ax.set_xticklabels(['Recent Trend %'])
                ax.set_title('Economic Indicators Performance Heatmap', fontweight='bold')
                
                # Add colorbar
                plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            else:
                ax.text(0.5, 0.5, 'Insufficient data for heatmap', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Economic Indicators Performance Heatmap', fontweight='bold')
        
        except Exception as e:
            ax.text(0.5, 0.5, f'Error creating heatmap: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Economic Indicators Performance Heatmap', fontweight='bold')
    
    def _create_data_quality_chart(self, ax, quality_report: Dict):
        """Create data quality visualization"""
        try:
            # Data completeness pie chart
            successful = quality_report['successful_fetches']
            failed = quality_report['failed_fetches']
            
            labels = ['Successful', 'Failed']
            sizes = [successful, failed]
            colors = ['#2ca02c', '#d62728']
            
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title('Data Fetch Success Rate', fontweight='bold')
        
        except Exception as e:
            ax.text(0.5, 0.5, f'Error creating quality chart: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Data Quality Summary', fontweight='bold')
    
    def _create_trend_analysis_chart(self, ax, economic_data: EconomicData):
        """Create trend analysis chart"""
        try:
            # Extract trend information
            trends = economic_data.summary_statistics.get('trends', {})
            
            if trends:
                indicator_names = []
                percent_changes = []
                colors = []
                
                for indicator_id, trend_data in trends.items():
                    if indicator_id in economic_data.indicators:
                        indicator_names.append(economic_data.indicators[indicator_id].name[:15])
                        pct_change = trend_data.get('percent_change', 0)
                        percent_changes.append(pct_change)
                        
                        # Color coding
                        if pct_change > 0:
                            colors.append('#2ca02c')  # Green for positive
                        elif pct_change < 0:
                            colors.append('#d62728')  # Red for negative
                        else:
                            colors.append('#1f77b4')  # Blue for neutral
                
                # Create horizontal bar chart
                bars = ax.barh(indicator_names, percent_changes, color=colors)
                ax.set_xlabel('Recent Period Change (%)')
                ax.set_title('Recent Trends in Economic Indicators', fontweight='bold')
                ax.axvline(x=0, color='black', linestyle='-', alpha=0.5)
                ax.grid(True, alpha=0.3)
                
                # Add value labels on bars
                for bar, value in zip(bars, percent_changes):
                    width = bar.get_width()
                    ax.text(width + (0.1 if width >= 0 else -0.1), bar.get_y() + bar.get_height()/2,
                           f'{value:.1f}%', ha='left' if width >= 0 else 'right', va='center', fontsize=8)
            else:
                ax.text(0.5, 0.5, 'No trend data available', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Recent Trends in Economic Indicators', fontweight='bold')
        
        except Exception as e:
            ax.text(0.5, 0.5, f'Error creating trend chart: {str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Recent Trends in Economic Indicators', fontweight='bold')

    def save_economic_data(self, economic_data: EconomicData, filename: str = None) -> str:
        """Save economic data to JSON file for caching/analysis"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"economic_data_{economic_data.analysis_type}_{timestamp}.json"
        
        filepath = os.path.join(self.config.DATA_CACHE_DIR, filename)
        
        # Convert to serializable format
        serializable_data = {
            'analysis_type': economic_data.analysis_type,
            'period': economic_data.period,
            'indicators': {},
            'summary_statistics': economic_data.summary_statistics,
            'data_quality_report': economic_data.data_quality_report,
            'timestamp': datetime.now().isoformat()
        }
        
        # Convert indicators to serializable format
        for indicator_id, indicator in economic_data.indicators.items():
            serializable_data['indicators'][indicator_id] = {
                'name': indicator.name,
                'category': indicator.category,
                'source': indicator.source,
                'data': indicator.data.to_dict() if not indicator.data.empty else {},
                'metadata': {
                    'frequency': indicator.frequency,
                    'units': indicator.units,
                    'seasonal_adjustment': indicator.seasonal_adjustment,
                    'notes': indicator.notes
                }
            }
        
        with open(filepath, 'w') as f:
            json.dump(serializable_data, f, indent=2, default=str)
        
        print(f"💾 Economic data saved to: {filepath}")
        return filepath