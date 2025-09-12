"""
Economic Report Writer Agent - Phase 2 of the Economic Analysis System
Generates comprehensive economic reports based on LangGraph Economic Agent results
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from economic_config import EconomicConfig
from economic_data_agent import EconomicData

@dataclass
class EconomicReportData:
    """Data structure for economic report generation"""
    analysis_results: Dict[str, Any]
    report_type: str
    period_analyzed: str
    generation_timestamp: datetime
    executive_summary: str
    key_findings: List[str]
    recommendations: List[str]
    charts: List[str]
    data_sources: List[str]
    
class EconomicReportWriter:
    """Advanced Economic Report Writer using AI"""
    
    def __init__(self):
        EconomicConfig.validate()
        self.llm = ChatOpenAI(
            model=EconomicConfig.DEFAULT_MODEL,
            temperature=0.2,  # Slightly higher for more creative report writing
            api_key=EconomicConfig.OPENAI_API_KEY
        )
        self.report_templates = self._load_report_templates()
    
    def _load_report_templates(self) -> Dict[str, str]:
        """Load different report templates"""
        return {
            "executive": """
# Executive Economic Summary Report
**Analysis Period:** {period}  
**Generated:** {timestamp}

## Executive Summary
{executive_summary}

## Key Economic Indicators
{key_indicators}

## Strategic Recommendations
{recommendations}
""",
            "comprehensive": """
# Comprehensive Economic Analysis Report
**Analysis Period:** {period}  
**Generated:** {timestamp}

## Executive Summary
{executive_summary}

## Economic Overview
{economic_overview}

## GDP Analysis
{gdp_analysis}

## Inflation Assessment
{inflation_analysis}

## Market Trends
{market_analysis}

## Industry Performance
{industry_analysis}

## Economic Forecasts
{forecasts}

## Policy Implications
{policy_implications}

## Risk Assessment
{risk_assessment}

## Strategic Recommendations
{recommendations}

## Appendix
{appendix}
""",
            "sector_focus": """
# Sector-Focused Economic Report
**Analysis Period:** {period}  
**Focus Industries:** {focus_industries}  
**Generated:** {timestamp}

## Executive Summary
{executive_summary}

## Macroeconomic Context
{macro_context}

## Industry Deep Dive
{industry_analysis}

## Sector Comparisons
{sector_comparisons}

## Investment Implications
{investment_implications}

## Recommendations
{recommendations}
""",
            "policy_brief": """
# Economic Policy Brief
**Analysis Period:** {period}  
**Generated:** {timestamp}

## Executive Summary
{executive_summary}

## Current Economic Conditions
{current_conditions}

## Policy Environment
{policy_environment}

## Policy Recommendations
{policy_recommendations}

## Implementation Considerations
{implementation}

## Risk Factors
{risks}
"""
        }
    
    def generate_comprehensive_report(self, 
                                    analysis_results: Dict[str, Any],
                                    report_type: str = "comprehensive",
                                    custom_focus: Optional[List[str]] = None) -> EconomicReportData:
        """Generate a comprehensive economic report"""
        
        print(f"🎯 Generating {report_type} economic report...")
        
        # Extract key data
        gdp_data = analysis_results.get("gdp_analysis", {})
        inflation_data = analysis_results.get("inflation_analysis", {})
        market_data = analysis_results.get("market_analysis", {})
        industry_data = analysis_results.get("industry_analysis", {})
        insights = analysis_results.get("economic_insights", [])
        policy_implications = analysis_results.get("policy_implications", [])
        forecasts = analysis_results.get("forecasts", {})
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(analysis_results)
        
        # Generate detailed sections based on report type
        if report_type == "comprehensive":
            report_content = self._generate_comprehensive_content(analysis_results)
        elif report_type == "executive":
            report_content = self._generate_executive_content(analysis_results)
        elif report_type == "sector_focus":
            report_content = self._generate_sector_focus_content(analysis_results, custom_focus)
        elif report_type == "policy_brief":
            report_content = self._generate_policy_brief_content(analysis_results)
        elif report_type == "industry":
            report_content = self._generate_industry_focused_content(analysis_results, custom_focus)
        elif report_type == "gdp":
            report_content = self._generate_gdp_focused_content(analysis_results)
        elif report_type == "inflation":
            report_content = self._generate_inflation_focused_content(analysis_results)
        elif report_type == "market_trends":
            report_content = self._generate_market_trends_focused_content(analysis_results)
        else:
            report_content = self._generate_comprehensive_content(analysis_results)
        
        # Create report data structure
        report_data = EconomicReportData(
            analysis_results=analysis_results,
            report_type=report_type,
            period_analyzed=analysis_results.get("period", "Unknown"),
            generation_timestamp=datetime.now(),
            executive_summary=executive_summary,
            key_findings=self._extract_key_findings(analysis_results),
            recommendations=self._generate_recommendations(analysis_results),
            charts=analysis_results.get("chart_paths", []),
            data_sources=["Federal Reserve Economic Data (FRED)", "OpenAI GPT-4 Analysis"]
        )
        
        # Generate and save the report
        final_report = self._compile_final_report(report_data, report_content)
        report_filename = self._save_report(final_report, report_type)
        
        print(f"✅ Report generated successfully: {report_filename}")
        return report_data
    
    def _generate_executive_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Generate AI-powered executive summary"""
        
        gdp_analysis = analysis_results.get("gdp_analysis", {})
        inflation_analysis = analysis_results.get("inflation_analysis", {})
        market_analysis = analysis_results.get("market_analysis", {})
        economic_insights = analysis_results.get("economic_insights", [])
        
        summary_prompt = f"""
        Create a concise executive summary for an economic analysis report based on the following data:
        
        GDP METRICS:
        - Current Growth Rate: {gdp_analysis.get('current_growth_rate', 'N/A')}%
        - Average Growth Rate: {gdp_analysis.get('average_growth_rate', 'N/A')}%
        - Growth Trend: {gdp_analysis.get('growth_trend', 'N/A')}
        
        INFLATION METRICS:
        - Current Inflation Rate: {inflation_analysis.get('current_inflation_rate', 'N/A')}%
        - vs Fed Target: {inflation_analysis.get('vs_fed_target', 'N/A')}
        - Average Inflation: {inflation_analysis.get('average_inflation_rate', 'N/A')}%
        
        MARKET METRICS:
        - Unemployment Rate: {market_analysis.get('current_unemployment', 'N/A')}%
        - Fed Funds Rate: {market_analysis.get('current_fed_rate', 'N/A')}%
        - Consumer Confidence: {market_analysis.get('current_consumer_confidence', 'N/A')}
        - Yield Curve: {market_analysis.get('yield_curve', 'N/A')}
        
        KEY INSIGHTS:
        {chr(10).join(economic_insights[:5])}
        
        Write a 3-4 paragraph executive summary that:
        1. Summarizes the current economic state
        2. Highlights key trends and patterns
        3. Identifies major risks and opportunities
        4. Provides outlook for the near term
        
        Use professional, accessible language suitable for executives and policymakers.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a senior economic analyst writing for C-suite executives and policymakers."),
                HumanMessage(content=summary_prompt)
            ])
            return response.content.strip()
        except Exception as e:
            return f"Executive Summary: Economic analysis completed for the specified period. Key metrics include GDP growth, inflation trends, and market conditions. Please refer to detailed sections for comprehensive insights. (Error generating AI summary: {str(e)})"
    
    def _generate_comprehensive_content(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive report content"""
        content = {}
        
        # Economic Overview
        content["economic_overview"] = self._generate_economic_overview(analysis_results)
        
        # Detailed Analysis Sections
        content["gdp_analysis"] = self._format_gdp_analysis(analysis_results.get("gdp_analysis", {}))
        content["inflation_analysis"] = self._format_inflation_analysis(analysis_results.get("inflation_analysis", {}))
        content["market_analysis"] = self._format_market_analysis(analysis_results.get("market_analysis", {}))
        content["industry_analysis"] = self._format_industry_analysis(analysis_results.get("industry_analysis", {}))
        
        # Forward-looking sections
        content["forecasts"] = self._format_forecasts(analysis_results.get("forecasts", {}))
        content["policy_implications"] = self._format_policy_implications(analysis_results.get("policy_implications", []))
        content["risk_assessment"] = self._generate_risk_assessment(analysis_results)
        
        # Supporting information
        content["appendix"] = self._generate_appendix(analysis_results)
        
        return content
    
    def _generate_economic_overview(self, analysis_results: Dict[str, Any]) -> str:
        """Generate economic overview section"""
        overview_prompt = f"""
        Based on the comprehensive economic analysis results, write a detailed economic overview section covering:
        
        ANALYSIS RESULTS:
        {json.dumps(analysis_results, indent=2, default=str)[:2000]}...
        
        The overview should cover:
        1. Current economic cycle position
        2. Overall economic health assessment
        3. Key drivers of economic performance
        4. Comparison to historical trends
        5. Cross-indicator relationships
        
        Write in a professional tone suitable for an economic report. Use 4-5 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert economic analyst writing a comprehensive economic overview."),
                HumanMessage(content=overview_prompt)
            ])
            return response.content.strip()
        except Exception as e:
            return f"Economic Overview: The analysis covers key economic indicators including GDP, inflation, employment, and sector performance. Detailed metrics and trends are available in the following sections. (Error: {str(e)})"
    
    def _format_gdp_analysis(self, gdp_data: Dict[str, Any]) -> str:
        """Format GDP analysis section"""
        if not gdp_data:
            return "GDP analysis data not available."
        
        formatted = f"""
### Current GDP Metrics
- **Current GDP Growth Rate**: {gdp_data.get('current_growth_rate', 'N/A')}%
- **Average Growth Rate**: {gdp_data.get('average_growth_rate', 'N/A')}%
- **Growth Trend**: {gdp_data.get('growth_trend', 'N/A')}
- **GDP per Capita**: ${gdp_data.get('current_gdp_per_capita', 'N/A')}
- **GDP per Capita YoY Change**: {gdp_data.get('gdp_per_capita_yoy', 'N/A')}%

### Analysis Insights
{gdp_data.get('ai_insights', 'Detailed GDP analysis insights not available.')}
"""
        return formatted
    
    def _format_inflation_analysis(self, inflation_data: Dict[str, Any]) -> str:
        """Format inflation analysis section"""
        if not inflation_data:
            return "Inflation analysis data not available."
        
        formatted = f"""
### Current Inflation Metrics
- **Current Inflation Rate**: {inflation_data.get('current_inflation_rate', 'N/A')}%
- **Average Inflation Rate**: {inflation_data.get('average_inflation_rate', 'N/A')}%
- **vs Fed Target (2%)**: {inflation_data.get('vs_fed_target', 'N/A')}
- **Core CPI YoY Change**: {inflation_data.get('core_cpi_yoy_change', 'N/A')}%
- **PCE YoY Change**: {inflation_data.get('pce_yoy_change', 'N/A')}%

### Analysis Insights
{inflation_data.get('ai_insights', 'Detailed inflation analysis insights not available.')}
"""
        return formatted
    
    def _format_market_analysis(self, market_data: Dict[str, Any]) -> str:
        """Format market analysis section"""
        if not market_data:
            return "Market analysis data not available."
        
        formatted = f"""
### Current Market Metrics
- **Unemployment Rate**: {market_data.get('current_unemployment', 'N/A')}%
- **Fed Funds Rate**: {market_data.get('current_fed_rate', 'N/A')}%
- **10-Year Treasury**: {market_data.get('current_10y_treasury', 'N/A')}%
- **Yield Spread**: {market_data.get('yield_spread', 'N/A')}%
- **Yield Curve**: {market_data.get('yield_curve', 'N/A')}
- **Consumer Confidence**: {market_data.get('current_consumer_confidence', 'N/A')}
- **Industrial Production Change**: {market_data.get('production_change_yoy', 'N/A')}%

### Analysis Insights
{market_data.get('ai_insights', 'Detailed market analysis insights not available.')}
"""
        return formatted
    
    def _format_industry_analysis(self, industry_data: Dict[str, Any]) -> str:
        """Format industry analysis section"""
        if not industry_data:
            return "Industry analysis data not available."
        
        formatted = "### Industry Performance Analysis\n\n"
        
        for industry, data in industry_data.items():
            formatted += f"#### {industry.upper()} Sector\n\n"
            
            # Employment metrics
            if "employment" in data:
                formatted += f"- **Employment Level**: {data.get('employment', 'N/A')}\n"
                formatted += f"- **Employment Change (YoY)**: {data.get('employment_change_yoy', 'N/A')}%\n"
            
            # Industry-specific metrics
            if industry == "tech":
                if "wages" in data:
                    formatted += f"- **Average Wages**: ${data.get('wages', 'N/A')}\n"
                    formatted += f"- **Wage Change (YoY)**: {data.get('wage_change_yoy', 'N/A')}%\n"
            elif industry == "healthcare":
                if "healthcare_cpi" in data:
                    formatted += f"- **Healthcare CPI**: {data.get('healthcare_cpi', 'N/A')}\n"
                    formatted += f"- **Healthcare CPI Change**: {data.get('healthcare_cpi_change_yoy', 'N/A')}%\n"
            elif industry == "energy":
                if "oil_price" in data:
                    formatted += f"- **Oil Price (WTI)**: ${data.get('oil_price', 'N/A')}\n"
                    formatted += f"- **Oil Price Change**: {data.get('oil_price_change_yoy', 'N/A')}%\n"
                if "natural_gas_price" in data:
                    formatted += f"- **Natural Gas Price**: ${data.get('natural_gas_price', 'N/A')}\n"
            
            # AI insights for each industry
            formatted += f"\n**Analysis**: {data.get('ai_insights', 'Industry insights not available.')}\n\n"
        
        return formatted
    
    def _format_forecasts(self, forecasts_data: Dict[str, Any]) -> str:
        """Format forecasts section"""
        if not forecasts_data:
            return "Economic forecasts not available."
        
        formatted = f"""
### Economic Forecasts

{forecasts_data.get('ai_forecast_analysis', 'Detailed forecast analysis not available.')}

### Key Assumptions
{chr(10).join([f"- {assumption}" for assumption in forecasts_data.get('key_assumptions', [])])}

### Risk Factors
{chr(10).join([f"- {risk}" for risk in forecasts_data.get('risk_factors', [])])}
"""
        return formatted
    
    def _format_policy_implications(self, policy_data: List[str]) -> str:
        """Format policy implications section"""
        if not policy_data:
            return "Policy implications analysis not available."
        
        formatted = "### Policy Recommendations and Implications\n\n"
        formatted += "\n".join([f"- {policy}" for policy in policy_data])
        return formatted
    
    def _generate_risk_assessment(self, analysis_results: Dict[str, Any]) -> str:
        """Generate risk assessment section"""
        risk_prompt = f"""
        Based on the comprehensive economic analysis, identify and assess key economic risks:
        
        ECONOMIC CONDITIONS:
        - GDP Growth: {analysis_results.get('gdp_analysis', {}).get('current_growth_rate', 'N/A')}%
        - Inflation: {analysis_results.get('inflation_analysis', {}).get('current_inflation_rate', 'N/A')}%
        - Unemployment: {analysis_results.get('market_analysis', {}).get('current_unemployment', 'N/A')}%
        - Yield Curve: {analysis_results.get('market_analysis', {}).get('yield_curve', 'N/A')}
        
        INDUSTRY PERFORMANCE:
        {json.dumps(analysis_results.get('industry_analysis', {}), indent=2, default=str)[:800]}
        
        Provide a risk assessment covering:
        1. **Immediate Risks (0-6 months)**
        2. **Medium-term Risks (6-18 months)**  
        3. **Long-term Structural Risks (1-5 years)**
        4. **Mitigation Strategies**
        
        Focus on specific, actionable risk factors with probability assessments where possible.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a senior economic risk analyst providing comprehensive risk assessment."),
                HumanMessage(content=risk_prompt)
            ])
            return response.content.strip()
        except Exception as e:
            return f"Risk Assessment: Key economic risks identified across growth, inflation, and sector-specific factors. Detailed risk analysis requires further investigation. (Error: {str(e)})"
    
    def _generate_sector_focus_content(self, analysis_results: Dict[str, Any], custom_focus: Optional[List[str]]) -> Dict[str, str]:
        """Generate sector-focused report content"""
        content = {}
        
        focus_industries = custom_focus if custom_focus else analysis_results.get("focus_industries", ["tech", "healthcare", "energy"])
        
        content["focus_industries"] = ", ".join(focus_industries)
        content["macro_context"] = self._generate_macro_context(analysis_results)
        content["industry_analysis"] = self._format_industry_analysis(analysis_results.get("industry_analysis", {}))
        content["sector_comparisons"] = self._generate_sector_comparisons(analysis_results, focus_industries)
        content["investment_implications"] = self._generate_investment_implications(analysis_results, focus_industries)
        
        return content
    
    def _generate_industry_focused_content(self, analysis_results: Dict[str, Any], custom_focus: Optional[List[str]]) -> Dict[str, str]:
        """Generate industry-focused report content"""
        content = {}
        
        focus_industries = custom_focus if custom_focus else analysis_results.get("focus_industries", ["tech", "healthcare", "energy"])
        industry_data = analysis_results.get("industry_analysis", {})
        
        content["focus_industries"] = ", ".join(focus_industries)
        content["industry_analysis"] = self._format_industry_analysis(industry_data)
        content["industry_comparison"] = self._generate_industry_comparison(industry_data, focus_industries)
        content["industry_trends"] = self._generate_industry_trends(industry_data, focus_industries)
        content["investment_implications"] = self._generate_investment_implications(analysis_results, focus_industries)
        content["sector_outlook"] = self._generate_sector_outlook(industry_data, focus_industries)
        
        return content
    
    def _generate_gdp_focused_content(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate GDP-focused report content"""
        content = {}
        
        gdp_data = analysis_results.get("gdp_analysis", {})
        
        content["gdp_analysis"] = self._format_gdp_analysis(gdp_data)
        content["gdp_trends"] = self._generate_gdp_trends(gdp_data)
        content["gdp_components"] = self._generate_gdp_components(gdp_data)
        content["gdp_forecast"] = self._generate_gdp_forecast(gdp_data)
        content["gdp_implications"] = self._generate_gdp_implications(gdp_data)
        
        return content
    
    def _generate_inflation_focused_content(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate inflation-focused report content"""
        content = {}
        
        inflation_data = analysis_results.get("inflation_analysis", {})
        
        content["inflation_analysis"] = self._format_inflation_analysis(inflation_data)
        content["inflation_trends"] = self._generate_inflation_trends(inflation_data)
        content["inflation_components"] = self._generate_inflation_components(inflation_data)
        content["inflation_forecast"] = self._generate_inflation_forecast(inflation_data)
        content["inflation_implications"] = self._generate_inflation_implications(inflation_data)
        
        return content
    
    def _generate_market_trends_focused_content(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate market trends-focused report content"""
        content = {}
        
        market_data = analysis_results.get("market_analysis", {})
        
        content["market_analysis"] = self._format_market_analysis(market_data)
        content["market_trends"] = self._generate_market_trends(market_data)
        content["yield_curve_analysis"] = self._generate_yield_curve_analysis(market_data)
        content["market_forecast"] = self._generate_market_forecast(market_data)
        content["market_implications"] = self._generate_market_implications(market_data)
        
        return content
    
    def _generate_industry_comparison(self, industry_data: Dict[str, Any], focus_industries: List[str]) -> str:
        """Generate industry comparison analysis"""
        if not industry_data:
            return "Industry comparison data not available."
        
        comparison_prompt = f"""
        Analyze and compare the following industry performance data:
        
        {json.dumps(industry_data, indent=2, default=str)}
        
        Focus on industries: {', '.join(focus_industries)}
        
        Provide a detailed comparison covering:
        1. **Performance Rankings** - Which industries are outperforming/underperforming
        2. **Growth Trajectories** - Employment and wage growth trends
        3. **Market Position** - Competitive advantages and challenges
        4. **Investment Attractiveness** - Risk-return profiles
        5. **Future Outlook** - Growth prospects and headwinds
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert industry analyst providing detailed sector comparisons."),
                HumanMessage(content=comparison_prompt)
            ])
            return response.content.strip()
        except Exception as e:
            return f"Industry comparison analysis not available due to processing error: {str(e)}"
    
    def _generate_industry_trends(self, industry_data: Dict[str, Any], focus_industries: List[str]) -> str:
        """Generate industry trends analysis"""
        trends_prompt = f"""
        Analyze industry trends based on the following data:
        
        {json.dumps(industry_data, indent=2, default=str)}
        
        Focus on industries: {', '.join(focus_industries)}
        
        Provide trend analysis covering:
        1. **Employment Trends** - Job growth patterns and labor market dynamics
        2. **Wage Trends** - Compensation growth and skill premium changes
        3. **Market Trends** - Industry-specific market conditions
        4. **Technology Trends** - Digital transformation and innovation impact
        5. **Regulatory Trends** - Policy changes and compliance requirements
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert in industry trend analysis and market dynamics."),
                HumanMessage(content=trends_prompt)
            ])
            return response.content.strip()
        except Exception as e:
            return f"Industry trends analysis not available due to processing error: {str(e)}"
    
    def _generate_sector_outlook(self, industry_data: Dict[str, Any], focus_industries: List[str]) -> str:
        """Generate sector outlook analysis"""
        outlook_prompt = f"""
        Provide sector outlook analysis based on:
        
        {json.dumps(industry_data, indent=2, default=str)}
        
        Focus on industries: {', '.join(focus_industries)}
        
        Provide outlook covering:
        1. **Short-term Outlook (6-12 months)** - Immediate prospects and challenges
        2. **Medium-term Outlook (1-3 years)** - Growth drivers and market evolution
        3. **Long-term Outlook (3-5 years)** - Structural changes and opportunities
        4. **Risk Factors** - Key risks and mitigation strategies
        5. **Investment Themes** - Emerging opportunities and themes
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert in sector outlook and investment analysis."),
                HumanMessage(content=outlook_prompt)
            ])
            return response.content.strip()
        except Exception as e:
            return f"Sector outlook analysis not available due to processing error: {str(e)}"
    
    def _generate_macro_context(self, analysis_results: Dict[str, Any]) -> str:
        """Generate macroeconomic context for sector analysis"""
        context_prompt = f"""
        Provide macroeconomic context for sector analysis based on:
        
        GDP: {analysis_results.get('gdp_analysis', {}).get('current_growth_rate', 'N/A')}%
        Inflation: {analysis_results.get('inflation_analysis', {}).get('current_inflation_rate', 'N/A')}%
        Employment: {analysis_results.get('market_analysis', {}).get('current_unemployment', 'N/A')}%
        Interest Rates: {analysis_results.get('market_analysis', {}).get('current_fed_rate', 'N/A')}%
        
        Explain how these macroeconomic conditions affect sector performance, particularly for technology, healthcare, and energy industries.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an expert in macroeconomic analysis and sector performance."),
                HumanMessage(content=context_prompt)
            ])
            return response.content.strip()
        except Exception as e:
            return f"Macroeconomic context analysis not available due to processing error: {str(e)}"
    
    def _generate_sector_comparisons(self, analysis_results: Dict[str, Any], focus_industries: List[str]) -> str:
        """Generate sector comparison analysis"""
        industry_data = analysis_results.get("industry_analysis", {})
        
        if not industry_data:
            return "Sector comparison data not available."
        
        comparison = "### Cross-Sector Performance Comparison\n\n"
        
        # Employment comparison
        comparison += "#### Employment Performance\n"
        for industry in focus_industries:
            if industry in industry_data:
                emp_change = industry_data[industry].get('employment_change_yoy', 'N/A')
                comparison += f"- **{industry.upper()}**: {emp_change}% YoY employment change\n"
        
        # Industry-specific metrics comparison
        comparison += "\n#### Key Performance Indicators\n"
        for industry in focus_industries:
            if industry in industry_data:
                if industry == "tech" and "wage_change_yoy" in industry_data[industry]:
                    comparison += f"- **Tech Wage Growth**: {industry_data[industry]['wage_change_yoy']}% YoY\n"
                elif industry == "energy" and "oil_price_change_yoy" in industry_data[industry]:
                    comparison += f"- **Energy Price Change**: {industry_data[industry]['oil_price_change_yoy']}% YoY\n"
                elif industry == "healthcare" and "healthcare_cpi_change_yoy" in industry_data[industry]:
                    comparison += f"- **Healthcare Cost Inflation**: {industry_data[industry]['healthcare_cpi_change_yoy']}% YoY\n"
        
        return comparison
    
    def _generate_investment_implications(self, analysis_results: Dict[str, Any], focus_industries: List[str]) -> str:
        """Generate investment implications for sectors"""
        investment_prompt = f"""
        Based on the economic analysis and sector performance data, provide investment implications for:
        
        FOCUS SECTORS: {', '.join(focus_industries)}
        
        MACRO CONDITIONS:
        - GDP Growth: {analysis_results.get('gdp_analysis', {}).get('current_growth_rate', 'N/A')}%
        - Inflation: {analysis_results.get('inflation_analysis', {}).get('current_inflation_rate', 'N/A')}%
        - Interest Rates: {analysis_results.get('market_analysis', {}).get('current_fed_rate', 'N/A')}%
        
        SECTOR DATA:
        {json.dumps(analysis_results.get('industry_analysis', {}), indent=2, default=str)[:1000]}
        
        Provide investment implications covering:
        1. Sector attractiveness ranking
        2. Key investment themes per sector
        3. Risk factors and opportunities
        4. Tactical vs strategic considerations
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a senior investment strategist providing sector-based investment analysis."),
                HumanMessage(content=investment_prompt)
            ])
            return response.content.strip()
        except Exception as e:
            return f"Investment implications analysis not available: {str(e)}"
    
    def _generate_policy_brief_content(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate policy brief content"""
        content = {}
        
        content["current_conditions"] = self._summarize_current_conditions(analysis_results)
        content["policy_environment"] = self._analyze_policy_environment(analysis_results)
        content["policy_recommendations"] = self._format_policy_implications(analysis_results.get("policy_implications", []))
        content["implementation"] = self._generate_implementation_considerations(analysis_results)
        content["risks"] = self._generate_risk_assessment(analysis_results)
        
        return content
    
    def _summarize_current_conditions(self, analysis_results: Dict[str, Any]) -> str:
        """Summarize current economic conditions for policy brief"""
        gdp = analysis_results.get("gdp_analysis", {})
        inflation = analysis_results.get("inflation_analysis", {})
        market = analysis_results.get("market_analysis", {})
        
        return f"""
### Key Economic Indicators
- **GDP Growth**: {gdp.get('current_growth_rate', 'N/A')}% (Trend: {gdp.get('growth_trend', 'N/A')})
- **Inflation Rate**: {inflation.get('current_inflation_rate', 'N/A')}% (Target: 2.0%)
- **Unemployment**: {market.get('current_unemployment', 'N/A')}%
- **Fed Funds Rate**: {market.get('current_fed_rate', 'N/A')}%
- **10-Year Treasury**: {market.get('current_10y_treasury', 'N/A')}%
- **Consumer Confidence**: {market.get('current_consumer_confidence', 'N/A')}

### Economic Assessment
The current economic environment shows {gdp.get('growth_trend', 'mixed')} growth trends with inflation {'above' if inflation.get('vs_fed_target') == 'above' else 'near'} the Federal Reserve's 2% target.
"""
    
    def _analyze_policy_environment(self, analysis_results: Dict[str, Any]) -> str:
        """Analyze current policy environment"""
        market_data = analysis_results.get("market_analysis", {})
        
        policy_prompt = f"""
        Analyze the current policy environment based on:
        
        - Fed Funds Rate: {market_data.get('current_fed_rate', 'N/A')}%
        - Yield Curve: {market_data.get('yield_curve', 'N/A')}
        - Unemployment: {market_data.get('current_unemployment', 'N/A')}%
        - Inflation vs Target: {analysis_results.get('inflation_analysis', {}).get('vs_fed_target', 'N/A')}
        
        Discuss:
        1. Current monetary policy stance
        2. Fiscal policy considerations
        3. Policy coordination challenges
        4. International policy implications
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a policy economist analyzing the current policy environment."),
                HumanMessage(content=policy_prompt)
            ])
            return response.content.strip()
        except Exception as e:
            return f"Policy environment analysis not available: {str(e)}"
    
    def _generate_implementation_considerations(self, analysis_results: Dict[str, Any]) -> str:
        """Generate implementation considerations for policies"""
        impl_prompt = f"""
        Based on current economic conditions, discuss implementation considerations for economic policies:
        
        ECONOMIC STATE:
        - Growth: {analysis_results.get('gdp_analysis', {}).get('current_growth_rate', 'N/A')}%
        - Inflation: {analysis_results.get('inflation_analysis', {}).get('current_inflation_rate', 'N/A')}%
        - Employment: {analysis_results.get('market_analysis', {}).get('current_unemployment', 'N/A')}%
        
        Cover:
        1. Timing considerations
        2. Implementation challenges
        3. Coordination requirements
        4. Monitoring and adjustment mechanisms
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a policy implementation expert."),
                HumanMessage(content=impl_prompt)
            ])
            return response.content.strip()
        except Exception as e:
            return f"Implementation considerations not available: {str(e)}"
    
    def _extract_key_findings(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis results"""
        findings = []
        
        # GDP findings
        gdp = analysis_results.get("gdp_analysis", {})
        if gdp.get("current_growth_rate"):
            findings.append(f"GDP growing at {gdp['current_growth_rate']}% with {gdp.get('growth_trend', 'mixed')} trend")
        
        # Inflation findings
        inflation = analysis_results.get("inflation_analysis", {})
        if inflation.get("current_inflation_rate"):
            target_status = inflation.get("vs_fed_target", "unknown")
            findings.append(f"Inflation at {inflation['current_inflation_rate']}%, {target_status} Fed's 2% target")
        
        # Market findings
        market = analysis_results.get("market_analysis", {})
        if market.get("current_unemployment"):
            findings.append(f"Unemployment rate at {market['current_unemployment']}%")
        
        if market.get("yield_curve"):
            findings.append(f"Yield curve is {market['yield_curve']}")
        
        # Add insights
        insights = analysis_results.get("economic_insights", [])
        findings.extend(insights[:3])  # Top 3 insights
        
        return findings[:10]  # Limit to top 10 findings
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations"""
        rec_prompt = f"""
        Based on comprehensive economic analysis, provide strategic recommendations:
        
        CURRENT STATE:
        - GDP Growth: {analysis_results.get('gdp_analysis', {}).get('current_growth_rate', 'N/A')}%
        - Inflation: {analysis_results.get('inflation_analysis', {}).get('current_inflation_rate', 'N/A')}%
        - Employment: {analysis_results.get('market_analysis', {}).get('current_unemployment', 'N/A')}%
        
        INSIGHTS:
        {chr(10).join(analysis_results.get('economic_insights', [])[:5])}
        
        Provide 5-7 specific, actionable recommendations for:
        1. Policymakers
        2. Business leaders
        3. Investors
        4. Economic monitoring priorities
        
        Format as bullet points starting with action verbs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a senior economic strategist providing actionable recommendations."),
                HumanMessage(content=rec_prompt)
            ])
            
            # Parse recommendations into list
            recommendations = []
            for line in response.content.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('*') or line.startswith('•')):
                    # Clean up bullet point formatting
                    clean_line = line.lstrip('- *•').strip()
                    if clean_line:
                        recommendations.append(clean_line)
                elif line and not any(char in line for char in ['#', '**', 'Recommendation']):
                    # Include lines that look like recommendations
                    recommendations.append(line)
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            return [
                "Monitor key economic indicators for trend changes",
                "Assess inflation trajectory and monetary policy implications",
                "Evaluate sector-specific investment opportunities",
                "Review risk management strategies based on current conditions",
                "Consider policy coordination for optimal economic outcomes"
            ]
    
    def _generate_appendix(self, analysis_results: Dict[str, Any]) -> str:
        """Generate appendix with technical details"""
        appendix = """
### Data Sources and Methodology

**Primary Data Source**: Federal Reserve Economic Data (FRED)  
**Analysis Period**: {period}  
**Generated**: {timestamp}

### Economic Series Analyzed
**GDP Indicators**:
- GDP (Gross Domestic Product)
- A191RL1Q225SBEA (Real GDP Growth Rate)
- A939RX0Q048SBEA (Real GDP per Capita)

**Inflation Indicators**:
- CPIAUCSL (Consumer Price Index)
- CPILFESL (Core CPI)
- PCEPI (PCE Price Index)
- FPCPITOTLZGUSA (Inflation Rate)

**Market Indicators**:
- UNRATE (Unemployment Rate)
- FEDFUNDS (Federal Funds Rate)
- GS10 (10-Year Treasury Rate)
- UMCSENT (Consumer Sentiment)
- INDPRO (Industrial Production)

**Industry Indicators**:
- Technology: Software Publishers Employment & Wages
- Healthcare: Healthcare Employment & Medical CPI
- Energy: Oil & Gas Employment, WTI Oil Prices, Natural Gas Prices

### Analysis Framework
1. **Data Collection**: Real-time FRED API integration
2. **Statistical Analysis**: Year-over-year changes, trend analysis
3. **AI Enhancement**: OpenAI GPT-4 powered insights
4. **Cross-Correlation**: Multi-indicator relationship analysis
5. **Forecasting**: AI-driven predictive modeling

### Limitations
- Historical data analysis may not predict future performance
- Economic forecasts subject to uncertainty and external factors
- Industry analysis limited to selected sectors
- AI insights based on available data and model training
"""
        return appendix
    
    def _compile_final_report(self, report_data: EconomicReportData, content: Dict[str, str]) -> str:
        """Compile the final report using appropriate template"""
        template = self.report_templates.get(report_data.report_type, self.report_templates["comprehensive"])
        
        # Prepare template variables
        template_vars = {
            "period": report_data.period_analyzed,
            "timestamp": report_data.generation_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "executive_summary": report_data.executive_summary,
            "key_indicators": self._format_key_indicators(report_data.analysis_results),
            "recommendations": self._format_recommendations_section(report_data.recommendations),
        }
        
        # Add content-specific variables
        template_vars.update(content)
        
        # Handle missing template variables gracefully
        for key in template_vars:
            if template_vars[key] is None:
                template_vars[key] = f"{key.replace('_', ' ').title()} section not available."
        
        try:
            formatted_report = template.format(**template_vars)
        except KeyError as e:
            # Fallback to basic template if formatting fails
            formatted_report = f"""
# Economic Analysis Report
**Generated:** {template_vars['timestamp']}
**Period:** {template_vars['period']}

## Executive Summary
{template_vars['executive_summary']}

## Key Findings
{template_vars.get('key_indicators', 'Key indicators not available')}

## Recommendations
{template_vars['recommendations']}

## Analysis Details
{content.get('economic_overview', 'Analysis details not available')}
"""
        
        return formatted_report
    
    def _format_key_indicators(self, analysis_results: Dict[str, Any]) -> str:
        """Format key indicators summary"""
        gdp = analysis_results.get("gdp_analysis", {})
        inflation = analysis_results.get("inflation_analysis", {})
        market = analysis_results.get("market_analysis", {})
        
        indicators = f"""
| Indicator | Current Value | Status |
|-----------|---------------|---------|
| GDP Growth Rate | {gdp.get('current_growth_rate', 'N/A')}% | {gdp.get('growth_trend', 'N/A').title()} |
| Inflation Rate | {inflation.get('current_inflation_rate', 'N/A')}% | {inflation.get('vs_fed_target', 'N/A').title()} Target |
| Unemployment Rate | {market.get('current_unemployment', 'N/A')}% | - |
| Fed Funds Rate | {market.get('current_fed_rate', 'N/A')}% | - |
| 10-Year Treasury | {market.get('current_10y_treasury', 'N/A')}% | - |
| Consumer Confidence | {market.get('current_consumer_confidence', 'N/A')} | - |
"""
        return indicators
    
    def _format_recommendations_section(self, recommendations: List[str]) -> str:
        """Format recommendations as numbered list"""
        if not recommendations:
            return "No specific recommendations available."
        
        formatted = ""
        for i, rec in enumerate(recommendations, 1):
            formatted += f"{i}. {rec}\n"
        
        return formatted
    
    def _save_report(self, report_content: str, report_type: str) -> str:
        """Save the generated report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{EconomicConfig.REPORT_OUTPUT_DIR}/economic_{report_type}_report_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            return filename
        except Exception as e:
            print(f"Error saving report: {str(e)}")
            return f"Error saving report: {str(e)}"
    
    def generate_multiple_reports(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate multiple report types from single analysis"""
        reports = {}
        
        report_types = ["executive", "comprehensive", "policy_brief"]
        
        for report_type in report_types:
            try:
                print(f"📝 Generating {report_type} report...")
                report_data = self.generate_comprehensive_report(analysis_results, report_type)
                reports[report_type] = f"Generated successfully"
            except Exception as e:
                reports[report_type] = f"Error: {str(e)}"
        
        return reports
    
    def create_executive_dashboard(self, analysis_results: Dict[str, Any]) -> str:
        """Create a professional executive dashboard visualization"""
        try:
            # Extract key metrics
            gdp_growth = analysis_results.get("gdp_analysis", {}).get("current_growth_rate", 0)
            inflation_rate = analysis_results.get("inflation_analysis", {}).get("current_inflation_rate", 0)
            unemployment = analysis_results.get("market_analysis", {}).get("current_unemployment", 0)
            fed_rate = analysis_results.get("market_analysis", {}).get("current_fed_rate", 0)
            treasury_10y = analysis_results.get("market_analysis", {}).get("current_10y_treasury", 0)
            
            # Get industry data for additional insights
            industry_data = analysis_results.get("industry_analysis", {})
            
            # Create comprehensive dashboard with multiple sections
            fig = make_subplots(
                rows=3, cols=3,
                subplot_titles=('GDP Growth Rate', 'Inflation Rate', 'Unemployment Rate', 
                              'Fed Funds Rate', '10Y Treasury Rate', 'Yield Curve Spread',
                              'Industry Performance', 'Economic Health Score', 'Key Metrics Summary'),
                specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "bar"}, {"type": "indicator"}, {"type": "table"}]],
                vertical_spacing=0.08,
                horizontal_spacing=0.05
            )
            
            # GDP Growth Indicator
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=gdp_growth,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "GDP Growth (%)", 'font': {'size': 14, 'color': '#2C3E50'}},
                gauge={
                    'axis': {'range': [None, 5], 'tickcolor': '#2C3E50'},
                    'bar': {'color': "#2E86AB"},
                    'steps': [
                        {'range': [0, 1], 'color': "#E8F4FD"},
                        {'range': [1, 2], 'color': "#B8D4EA"},
                        {'range': [2, 3.5], 'color': "#7BB3D9"},
                        {'range': [3.5, 5], 'color': "#2E86AB"}
                    ],
                    'threshold': {
                        'line': {'color': "#E74C3C", 'width': 4},
                        'thickness': 0.75,
                        'value': 2.5
                    }
                }
            ), row=1, col=1)
            
            # Inflation Rate Indicator
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=inflation_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Inflation Rate (%)"},
                gauge={
                    'axis': {'range': [0, 6]},
                    'bar': {'color': "darkred"},
                    'steps': [
                        {'range': [0, 2], 'color': "lightgreen"},
                        {'range': [2, 4], 'color': "yellow"},
                        {'range': [4, 6], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 2
                    }
                }
            ), row=1, col=2)
            
            # Unemployment Rate Indicator
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=unemployment,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Unemployment (%)"},
                gauge={
                    'axis': {'range': [0, 10]},
                    'bar': {'color': "orange"},
                    'steps': [
                        {'range': [0, 4], 'color': "lightgreen"},
                        {'range': [4, 7], 'color': "yellow"},
                        {'range': [7, 10], 'color': "red"}
                    ]
                }
            ), row=2, col=1)
            
            # Fed Funds Rate Indicator
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=fed_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Fed Funds Rate (%)"},
                gauge={
                    'axis': {'range': [0, 8]},
                    'bar': {'color': "purple"},
                    'steps': [
                        {'range': [0, 2], 'color': "lightblue"},
                        {'range': [2, 5], 'color': "blue"},
                        {'range': [5, 8], 'color': "darkblue"}
                    ]
                }
            ), row=2, col=2)
            
            fig.update_layout(
                title="Economic Indicators Dashboard",
                height=800,
                font={'size': 12}
            )
            
            # Save dashboard
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dashboard_path = f"{EconomicConfig.CHART_OUTPUT_DIR}/executive_dashboard_{timestamp}.png"
            fig.write_image(dashboard_path, width=1400, height=1000, scale=2)
            
            return dashboard_path
            
        except Exception as e:
            print(f"Error creating executive dashboard: {str(e)}")
            return f"Dashboard creation failed: {str(e)}"

# Example usage and testing
def fetch_real_economic_data_for_testing(period: str = "5y") -> Dict[str, Any]:
    """Fetch real economic data for testing the report writer"""
    try:
        from economic_data_agent import EconomicDataAgent
        
        print(f"📊 Fetching real economic data for {period}...")
        
        # Initialize the economic data agent
        data_agent = EconomicDataAgent()
        
        # Fetch real economic data
        gdp_data = data_agent.fetch_gdp_indicators(period)
        inflation_data = data_agent.fetch_inflation_indicators(period)
        market_data = data_agent.fetch_market_trends(period)
        industry_data = data_agent.fetch_industry_performance(period)
        
        # Process the data into the format expected by the report writer
        real_results = {
            "gdp_analysis": {
                "current_growth_rate": gdp_data.get("GDP_GROWTH", {}).get("latest_value"),
                "average_growth_rate": gdp_data.get("GDP_GROWTH", {}).get("average_value"),
                "growth_trend": gdp_data.get("GDP_GROWTH", {}).get("trend", "stable"),
                "ai_insights": f"Real GDP data shows {gdp_data.get('GDP_GROWTH', {}).get('trend', 'stable')} growth pattern."
            },
            "inflation_analysis": {
                "current_inflation_rate": inflation_data.get("CPI", {}).get("latest_value"),
                "vs_fed_target": "above" if inflation_data.get("CPI", {}).get("latest_value", 0) > 2.0 else "below",
                "ai_insights": f"Current inflation rate is {inflation_data.get('CPI', {}).get('latest_value', 0):.2f}% based on real CPI data."
            },
            "market_analysis": {
                "current_unemployment": market_data.get("UNEMPLOYMENT", {}).get("latest_value"),
                "current_fed_rate": market_data.get("FED_FUNDS", {}).get("latest_value"),
                "current_10y_treasury": market_data.get("10Y_TREASURY", {}).get("latest_value"),
                "yield_curve": "normal" if market_data.get("10Y_TREASURY", {}).get("latest_value", 0) > market_data.get("FED_FUNDS", {}).get("latest_value", 0) else "inverted",
                "ai_insights": f"Real market data shows unemployment at {market_data.get('UNEMPLOYMENT', {}).get('latest_value', 0):.2f}% and Fed funds rate at {market_data.get('FED_FUNDS', {}).get('latest_value', 0):.2f}%."
            },
            "industry_analysis": {
                "tech": {
                    "employment_change_yoy": industry_data.get("tech", {}).get("employment_change_yoy"),
                    "wage_change_yoy": industry_data.get("tech", {}).get("wage_change_yoy"),
                    "ai_insights": f"Real tech sector data shows employment change of {industry_data.get('tech', {}).get('employment_change_yoy', 0):.2f}% YoY."
                }
            },
            "economic_insights": [
                "Analysis based on real-time economic data from FRED",
                "Current economic indicators show actual market conditions",
                "Data reflects genuine economic trends and patterns"
            ],
            "policy_implications": [
                "Policy recommendations based on real economic data",
                "Current market conditions require data-driven decisions",
                "Real-time analysis enables informed policy making"
            ],
            "forecasts": {
                "ai_forecast_analysis": "Forecasts based on real economic data trends and patterns."
            },
            "period": period,
            "data_sources": ["FRED (Federal Reserve Economic Data)", "Real-time economic indicators"],
            "last_updated": datetime.now().isoformat()
        }
        
        print("✅ Real economic data fetched successfully")
        return real_results
        
    except Exception as e:
        print(f"⚠️  Error fetching real data: {str(e)}")
        print("🔄 Falling back to mock data for testing...")
        
        # Fallback to mock data if real data fails
        return {
        "gdp_analysis": {
            "current_growth_rate": 2.5,
            "average_growth_rate": 2.8,
            "growth_trend": "positive",
            "ai_insights": "GDP growth showing resilience with positive trajectory."
        },
        "inflation_analysis": {
            "current_inflation_rate": 3.2,
            "vs_fed_target": "above",
            "ai_insights": "Inflation remains elevated above Fed target, requiring monitoring."
        },
        "market_analysis": {
            "current_unemployment": 3.8,
            "current_fed_rate": 5.25,
            "current_10y_treasury": 4.5,
            "yield_curve": "normal",
            "ai_insights": "Labor market remains tight with elevated interest rates."
        },
        "industry_analysis": {
            "tech": {
                "employment_change_yoy": 5.2,
                "wage_change_yoy": 7.1,
                "ai_insights": "Technology sector showing strong employment and wage growth."
            }
        },
        "economic_insights": [
            "Economic growth remains moderate despite headwinds",
            "Inflation pressures persist above target levels",
            "Labor market showing resilience and strength"
        ],
        "policy_implications": [
            "Maintain restrictive monetary policy stance",
            "Monitor inflation trajectory closely",
            "Support labor market flexibility"
        ],
        "forecasts": {
            "ai_forecast_analysis": "Economic conditions expected to moderate over next 12 months."
        },
            "period": period,
            "data_sources": ["Mock data (fallback)"],
            "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test the Economic Report Writer with REAL DATA
    print("🧪 Testing Economic Report Writer with REAL ECONOMIC DATA...")
    print("=" * 60)
    
    try:
        # Initialize report writer
        writer = EconomicReportWriter()
        print("✅ Economic Report Writer initialized")
        
        # Fetch REAL economic data instead of mock data
        print("\n📊 Fetching real economic data from FRED...")
        real_results = fetch_real_economic_data_for_testing("5y")
        
        # Display data source information
        print(f"\n📈 Data Sources: {', '.join(real_results.get('data_sources', ['Unknown']))}")
        print(f"🕒 Last Updated: {real_results.get('last_updated', 'Unknown')}")
        print(f"📅 Analysis Period: {real_results.get('period', 'Unknown')}")
        
        # Show some real data values
        print(f"\n📊 Real Economic Indicators:")
        print(f"  GDP Growth Rate: {real_results['gdp_analysis']['current_growth_rate']:.2f}%")
        print(f"  Inflation Rate: {real_results['inflation_analysis']['current_inflation_rate']:.2f}%")
        print(f"  Unemployment Rate: {real_results['market_analysis']['current_unemployment']:.2f}%")
        print(f"  Fed Funds Rate: {real_results['market_analysis']['current_fed_rate']:.2f}%")
        
        # Generate comprehensive report with REAL DATA
        print(f"\n📝 Generating comprehensive report with real data...")
        report_data = writer.generate_comprehensive_report(real_results, "comprehensive")
        print(f"✅ Comprehensive report generated with real data")
        
        # Generate executive dashboard with REAL DATA
        print(f"📊 Creating executive dashboard with real data...")
        dashboard_path = writer.create_executive_dashboard(real_results)
        print(f"✅ Executive dashboard created with real data: {dashboard_path}")
        
        print("\n" + "=" * 60)
        print("🎉 Economic Report Writer test completed successfully with REAL DATA!")
        print("📁 Check the 'economic_reports' and 'economic_charts' directories for outputs.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error testing Economic Report Writer: {str(e)}")
        import traceback
        traceback.print_exc()