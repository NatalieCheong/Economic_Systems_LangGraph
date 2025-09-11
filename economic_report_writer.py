#!/usr/bin/env python3
"""
Economic Report Writer - AI agent for generating comprehensive economic analysis reports
"""

from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from datetime import datetime
import json
import os
from dataclasses import dataclass
from config import Config

@dataclass
class EconomicReportSection:
    """Structure for economic report sections"""
    title: str
    content: str
    order: int
    section_type: str

class EconomicReportWriter:
    """AI agent for generating comprehensive economic analysis reports"""
    
    def __init__(self):
        Config.validate()
        self.llm = ChatOpenAI(
            model=Config.DEFAULT_MODEL,
            temperature=0.2,
            api_key=Config.OPENAI_API_KEY
        )
    
    def generate_economic_report(self, 
                                analysis_data: Dict[str, Any], 
                                report_type: str = "comprehensive",
                                target_audience: str = "policymakers") -> Dict[str, Any]:
        """
        Generate a comprehensive economic analysis report
        
        Args:
            analysis_data: Output from LangGraphEconomicAgent
            report_type: Type of report ('executive', 'comprehensive', 'policy_brief')
            target_audience: Target audience ('policymakers', 'investors', 'academics', 'public')
        
        Returns:
            Complete report state with final report content
        """
        print(f"📝 Starting economic report generation...")
        print(f"Report Type: {report_type}")
        print(f"Target Audience: {target_audience}")
        
        # Initialize state
        state = {
            "analysis_data": analysis_data,
            "report_type": report_type,
            "target_audience": target_audience,
            "report_sections": [],
            "final_report": "",
            "report_metadata": {},
            "messages": []
        }
        
        try:
            # Execute report generation workflow
            state = self._analyze_input_data(state)
            state = self._create_executive_summary(state)
            state = self._write_economic_overview(state)
            state = self._write_growth_analysis(state)
            state = self._write_inflation_analysis(state)
            state = self._write_employment_analysis(state)
            state = self._write_monetary_policy_analysis(state)
            state = self._write_market_analysis(state)
            state = self._write_policy_implications(state)
            state = self._write_economic_outlook(state)
            state = self._write_recommendations(state)
            state = self._compile_final_report(state)
            
            print("✅ Economic report generation completed!")
            return state
            
        except Exception as e:
            print(f"❌ Economic report generation failed: {e}")
            state["messages"].append(f"Error: {str(e)}")
            return state
    
    def _analyze_input_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze input economic data to understand scope and structure"""
        print("📊 Analyzing input data for report structure...")
        
        analysis_data = state["analysis_data"]
        
        # Determine report characteristics
        indicators = analysis_data.get('indicators_analyzed', [])
        analysis_type = analysis_data.get('analysis_type', 'comprehensive')
        
        metadata = {
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'indicators_count': len(indicators),
            'indicators': indicators,
            'analysis_type': analysis_type,
            'data_period': analysis_data.get('period', 'N/A'),
            'has_growth_data': bool(analysis_data.get('growth_analysis')),
            'has_inflation_data': bool(analysis_data.get('inflation_analysis')),
            'has_employment_data': bool(analysis_data.get('employment_analysis')),
            'has_monetary_data': bool(analysis_data.get('monetary_analysis')),
            'has_charts': bool(analysis_data.get('chart_paths')),
            'data_quality_score': self._calculate_data_quality_score(analysis_data)
        }
        
        state["report_metadata"] = metadata
        state["messages"].append("Economic data analysis completed - report structure determined")
        
        return state
    
    def _calculate_data_quality_score(self, analysis_data: Dict[str, Any]) -> str:
        """Calculate overall data quality score"""
        try:
            quality_report = analysis_data.get('data_quality', {})
            successful = quality_report.get('successful_fetches', 0)
            total = quality_report.get('total_indicators', 1)
            score = (successful / total) * 100 if total > 0 else 0
            
            if score >= 90:
                return "Excellent"
            elif score >= 75:
                return "Good"
            elif score >= 60:
                return "Fair"
            else:
                return "Poor"
        except:
            return "Unknown"
    
    def _create_executive_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary section"""
        print("📝 Writing executive summary...")
        
        analysis_data = state["analysis_data"]
        metadata = state["report_metadata"]
        
        prompt = f"""
        Write a professional executive summary for an economic analysis report based on:
        
        Analysis Type: {metadata['analysis_type']}
        Data Period: {metadata['data_period']}
        Indicators Analyzed: {len(metadata['indicators'])}
        
        Key Economic Insights: {analysis_data.get('economic_insights', 'N/A')[:800]}
        
        Economic Outlook: {analysis_data.get('economic_outlook', 'N/A')[:600]}
        
        The executive summary should be:
        - Concise (3-4 paragraphs)
        - Highlight key economic findings and themes
        - Include primary economic outlook and policy implications
        - Written for senior policymakers and decision makers
        - Professional and authoritative tone
        - Focus on actionable economic intelligence
        
        Avoid technical jargon and focus on strategic implications.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a senior economic advisor writing for government officials and central bank leaders."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Executive Summary",
                content=response.content,
                order=1,
                section_type="executive_summary"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Executive summary completed")
            
        except Exception as e:
            print(f"Error creating executive summary: {e}")
            state["messages"].append(f"Error in executive summary: {str(e)}")
        
        return state
    
    def _write_economic_overview(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write economic overview section"""
        print("🌍 Writing economic overview...")
        
        analysis_data = state["analysis_data"]
        metadata = state["report_metadata"]
        
        prompt = f"""
        Write a comprehensive economic overview section covering:
        
        Analysis Period: {metadata['data_period']}
        Analysis Scope: {metadata['analysis_type']}
        Data Quality: {metadata['data_quality_score']}
        
        Economic Insights: {analysis_data.get('economic_insights', 'N/A')}
        
        The economic overview should include:
        1. Current economic environment and context
        2. Major economic themes and narratives
        3. Economic cycle position assessment
        4. Key economic challenges and opportunities
        5. Data methodology and scope explanation
        6. Report structure overview
        
        Write for informed economic audiences who need comprehensive context.
        Length: 4-5 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a chief economist providing comprehensive economic analysis."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Economic Overview",
                content=response.content,
                order=2,
                section_type="economic_overview"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Economic overview completed")
            
        except Exception as e:
            print(f"Error writing economic overview: {e}")
            state["messages"].append(f"Error in economic overview: {str(e)}")
        
        return state
    
    def _write_growth_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write growth analysis section"""
        print("📈 Writing growth analysis...")
        
        analysis_data = state["analysis_data"]
        growth_data = analysis_data.get('growth_analysis', {})
        
        if not growth_data:
            state["messages"].append("Skipped growth analysis - no data available")
            return state
        
        prompt = f"""
        Write a detailed economic growth analysis section based on:
        
        Growth Analysis Data: {json.dumps(growth_data, indent=2, default=str)}
        
        The growth analysis should cover:
        1. Current GDP growth trends and trajectory
        2. Real vs nominal growth analysis
        3. Sectoral growth contributions and drivers
        4. Productivity and capacity utilization trends
        5. Growth sustainability assessment
        6. Historical growth context and comparisons
        7. Regional growth variations (if available)
        8. Growth headwinds and tailwinds
        
        Focus on economic growth dynamics and policy implications.
        Length: 5-6 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an economic growth specialist providing detailed growth analysis."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Economic Growth Analysis",
                content=response.content,
                order=3,
                section_type="growth_analysis"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Growth analysis completed")
            
        except Exception as e:
            print(f"Error writing growth analysis: {e}")
            state["messages"].append(f"Error in growth analysis: {str(e)}")
        
        return state
    
    def _write_inflation_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write inflation analysis section"""
        print("💰 Writing inflation analysis...")
        
        analysis_data = state["analysis_data"]
        inflation_data = analysis_data.get('inflation_analysis', {})
        
        if not inflation_data:
            state["messages"].append("Skipped inflation analysis - no data available")
            return state
        
        prompt = f"""
        Write a comprehensive inflation analysis section based on:
        
        Inflation Analysis Data: {json.dumps(inflation_data, indent=2, default=str)}
        
        The inflation analysis should cover:
        1. Current inflation trends and trajectory
        2. Core vs headline inflation dynamics
        3. Inflation components and sector contributions
        4. Inflation expectations and anchoring
        5. International inflation comparisons
        6. Inflation drivers and supply/demand factors
        7. Policy implications for monetary authorities
        8. Inflation risks and scenarios
        
        Focus on price stability implications and monetary policy considerations.
        Length: 5-6 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an inflation expert and monetary policy analyst."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Inflation and Price Analysis",
                content=response.content,
                order=4,
                section_type="inflation_analysis"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Inflation analysis completed")
            
        except Exception as e:
            print(f"Error writing inflation analysis: {e}")
            state["messages"].append(f"Error in inflation analysis: {str(e)}")
        
        return state
    
    def _write_industry_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write industry performance analysis section"""
        print("🏭 Writing industry performance analysis...")
        
        analysis_data = state["analysis_data"]
        industry_data = analysis_data.get('industry_analysis', {})
        
        if not industry_data:
            state["messages"].append("Skipped industry analysis - no data available")
            return state
        
        prompt = f"""
        Write a detailed industry performance analysis section based on:
        
        Industry Analysis Data: {json.dumps(industry_data, indent=2, default=str)}
        
        The industry analysis should cover:
        1. Manufacturing sector performance and trends
        2. Retail and consumer spending patterns
        3. Construction and infrastructure activity
        4. Business inventory and supply chain dynamics
        5. Industrial production and capacity utilization
        6. Sectoral competitiveness and productivity
        7. Industry cycle positioning and outlook
        8. Cross-sectoral performance comparison
        
        Focus on industrial health and economic diversification implications.
        Length: 5-6 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are an industrial economist specializing in sectoral performance analysis."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Industry Performance Analysis",
                content=response.content,
                order=5,
                section_type="industry_analysis"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Industry performance analysis completed")
            
        except Exception as e:
            print(f"Error writing industry analysis: {e}")
            state["messages"].append(f"Error in industry analysis: {str(e)}")
        
        return state
    
    def _write_market_trends_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write market trends analysis section"""
        print("📈 Writing market trends analysis...")
        
        analysis_data = state["analysis_data"]
        market_trends_data = analysis_data.get('market_trends_analysis', {})
        
        if not market_trends_data:
            state["messages"].append("Skipped market trends analysis - no data available")
            return state
        
        prompt = f"""
        Write a comprehensive market trends analysis section based on:
        
        Market Trends Data: {json.dumps(market_trends_data, indent=2, default=str)}
        
        The market trends analysis should cover:
        1. Corporate profitability and earnings trends
        2. Business investment and capital formation
        3. Credit markets and financial intermediation
        4. Equity market performance and valuations
        5. Asset price dynamics and bubble risks
        6. Financial market liquidity and functioning
        7. Market efficiency and price discovery mechanisms
        8. Cross-market correlations and spillover effects
        
        Focus on market-economy interactions and financial stability implications.
        Length: 5-6 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a financial markets analyst specializing in market trends and dynamics."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Market Trends Analysis",
                content=response.content,
                order=6,
                section_type="market_trends_analysis"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Market trends analysis completed")
            
        except Exception as e:
            print(f"Error writing market trends analysis: {e}")
            state["messages"].append(f"Error in market trends analysis: {str(e)}")
        
        return state f"""
        Write a detailed employment and labor market analysis based on:
        
        Employment Analysis Data: {json.dumps(employment_data, indent=2, default=str)}
        
        The employment analysis should cover:
        1. Labor market health and employment trends
        2. Unemployment dynamics and characteristics
        3. Labor force participation and demographics
        4. Job creation and industry employment patterns
        5. Wage growth and compensation trends
        6. Labor market tightness and skills gaps
        7. Regional employment variations
        8. Employment policy implications
        
        Focus on labor market dynamics and social/economic implications.
        Length: 5-6 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a labor economist specializing in employment analysis."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Employment and Labor Market Analysis",
                content=response.content,
                order=5,
                section_type="employment_analysis"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Employment analysis completed")
            
        except Exception as e:
            print(f"Error writing employment analysis: {e}")
            state["messages"].append(f"Error in employment analysis: {str(e)}")
        
        return state
    
        return state