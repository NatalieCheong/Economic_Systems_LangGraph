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

            # Only write relevant analysis sections
            analysis_data = state["analysis_data"]
            if 'gdp' in analysis_data.get('analysis_type', ''):
                state = self._write_growth_analysis(state)
            elif 'inflation' in analysis_data.get('analysis_type', ''):
                state = self._write_inflation_analysis(state)
            elif 'industry' in analysis_data.get('analysis_type', ''):
                state = self._write_industry_analysis(state)

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
            'has_industry_data': bool(analysis_data.get('industry_analysis')),
            'has_market_trends_data': bool(analysis_data.get('market_trends_analysis')),
            'has_tech_data': bool(analysis_data.get('tech_industry_analysis')),
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
        
        sector_focus = industry_data.get('sector_focus', 'general')
        analysis_type = analysis_data.get('analysis_type', '')
        
        # Create industry-specific prompt
        if 'tech' in analysis_type:
            industry_focus = "technology sector, including software development, hardware manufacturing, semiconductors, and digital services"
        elif 'healthcare' in analysis_type:
            industry_focus = "healthcare sector, including medical devices, pharmaceuticals, and healthcare services"
        elif 'finance' in analysis_type:
            industry_focus = "financial services sector, including banking, insurance, and fintech"
        elif 'energy' in analysis_type:
            industry_focus = "energy sector, including oil & gas, renewable energy, and utilities"
        else:
            industry_focus = f"{sector_focus} industry sector"
        
        prompt = f"""
        Write a detailed industry performance analysis focused specifically on the {industry_focus} based on:
        
        Industry Analysis Data: {json.dumps(industry_data, indent=2, default=str)}
        
        The analysis should cover:
        1. Current {sector_focus} industry health and key performance metrics
        2. Employment trends and workforce dynamics specific to {sector_focus}
        3. {sector_focus.title()}-specific growth drivers and market opportunities
        4. Industry challenges and competitive pressures in {sector_focus}
        5. Technology adoption and innovation trends in {sector_focus}
        6. Regulatory environment and policy impacts on {sector_focus}
        7. Supply chain considerations specific to {sector_focus}
        8. Future outlook and strategic implications for the {sector_focus} sector
        
        Focus exclusively on the {sector_focus} sector. Avoid generic economic analysis.
        Provide specific insights about this industry's performance, challenges, and opportunities.
        Length: 5-6 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=f"You are a {sector_focus} industry analyst with deep expertise in this specific sector. Provide industry-specific analysis, not general economic commentary."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title=f"{sector_focus.title()} Industry Performance Analysis",
                content=response.content,
                order=5,
                section_type="industry_analysis"
            )
            
            state["report_sections"].append(section)
            state["messages"].append(f"{sector_focus} industry analysis completed")
            
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
        
        return state
    
    def _write_market_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write market and sentiment analysis section"""
        print("📊 Writing market and sentiment analysis...")
        
        analysis_data = state["analysis_data"]
        sentiment_data = analysis_data.get('sentiment_analysis', {})
        
        if not sentiment_data:
            state["messages"].append("Skipped market analysis - no data available")
            return state
        
        prompt = f"""
        Write a detailed market and sentiment analysis section based on:
        
        Market Sentiment Data: {json.dumps(sentiment_data, indent=2, default=str)}
        
        The market analysis should cover:
        1. Financial market performance and trends
        2. Market sentiment and investor confidence
        3. Risk appetite and volatility indicators
        4. Consumer and business confidence trends
        5. Market-economy relationship analysis
        6. Financial stability considerations
        7. Market expectations and forward-looking indicators
        8. Behavioral economic factors
        
        Focus on how market conditions reflect and influence economic fundamentals.
        Length: 4-5 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a market analyst and behavioral economist."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Market and Sentiment Analysis",
                content=response.content,
                order=7,
                section_type="market_analysis"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Market analysis completed")
            
        except Exception as e:
            print(f"Error writing market analysis: {e}")
            state["messages"].append(f"Error in market analysis: {str(e)}")
        
        return state
    
    def _write_policy_implications(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write policy implications section"""
        print("🏛️ Writing policy implications...")
        
        analysis_data = state["analysis_data"]
        analysis_type = analysis_data.get('analysis_type', '')
        policy_data = analysis_data.get('policy_implications', '')
        
        # Determine sector-specific focus and build prompt accordingly
        if 'tech_industry' in analysis_type:
            sector_focus = "technology industry"
            specific_policies = """
            1. Technology sector workforce development and retraining programs
            2. R&D tax incentives for tech innovation and AI development
            3. Immigration policies for skilled tech workers and STEM talent
            4. Data privacy and cybersecurity regulatory frameworks
            5. Antitrust and competition policies for big tech companies
            6. Support for tech startups and venture capital investment
            7. Infrastructure policies for 5G, broadband, and digital connectivity
            8. International trade policies affecting semiconductor and tech supply chains
            """
            prompt = f"""
            Write comprehensive {sector_focus} policy implications based on the analysis:
            
            Industry Analysis: {analysis_data.get('industry_analysis', {}).get('industry_assessment', 'N/A')[:500]}
            
            Economic Context: {analysis_data.get('economic_insights', 'N/A')[:300]}
            
            Focus on these {sector_focus}-specific policy areas:
            {specific_policies}
            
            The policy implications should address:
            1. Regulatory policies specific to the {sector_focus}
            2. Workforce and education policies for this sector
            3. Innovation and R&D support policies
            4. Tax and fiscal policies affecting this industry
            5. International trade and competitiveness policies
            6. Infrastructure and technology policies
            7. Market competition and antitrust considerations
            8. Long-term strategic policies for sector growth
            
            Provide specific, actionable policy recommendations for the {sector_focus}.
            Length: 5-6 paragraphs.
            """
            system_content = f"You are a {sector_focus} policy analyst providing sector-specific policy recommendations."
            section_title = f"{sector_focus.title()} Policy Implications and Recommendations"
        elif 'healthcare_industry' in analysis_type:
            sector_focus = "healthcare industry"
            specific_policies = """
            1. Healthcare workforce training and retention programs
            2. FDA regulatory policies for medical devices and pharmaceuticals
            3. Medicare/Medicaid reimbursement policies
            4. Health data privacy and interoperability standards
            5. Telemedicine and digital health regulations
            6. Public health infrastructure investment
            7. Drug pricing and pharmaceutical competition policies
            8. International coordination on health emergency response
            """
            prompt = f"""
            Write comprehensive {sector_focus} policy implications based on the analysis:
            
            Industry Analysis: {analysis_data.get('industry_analysis', {}).get('industry_assessment', 'N/A')[:500]}
            
            Economic Context: {analysis_data.get('economic_insights', 'N/A')[:300]}
            
            Focus on these {sector_focus}-specific policy areas:
            {specific_policies}
            
            The policy implications should address:
            1. Regulatory policies specific to the {sector_focus}
            2. Workforce and education policies for this sector
            3. Innovation and R&D support policies
            4. Tax and fiscal policies affecting this industry
            5. International trade and competitiveness policies
            6. Infrastructure and technology policies
            7. Market competition and antitrust considerations
            8. Long-term strategic policies for sector growth
            
            Provide specific, actionable policy recommendations for the {sector_focus}.
            Length: 5-6 paragraphs.
            """
            system_content = f"You are a {sector_focus} policy analyst providing sector-specific policy recommendations."
            section_title = f"{sector_focus.title()} Policy Implications and Recommendations"
        else:
            # Fallback to the original generic policy implications prompt
            prompt = f"""
            Write a comprehensive policy implications section based on:
        
            Policy Analysis: {policy_data}
        
            Economic Context: {analysis_data.get('economic_insights', 'N/A')[:500]}
        
            The policy implications section should cover:
            1. Monetary policy recommendations and considerations
            2. Fiscal policy implications and needs
            3. Regulatory and structural policy requirements
            4. International policy coordination needs
            5. Policy risks and unintended consequences
            6. Policy timing and sequencing considerations
            7. Long-term policy framework implications
            8. Policy effectiveness and implementation challenges
        
            Focus on actionable policy recommendations for government and central bank officials.
            Length: 5-6 paragraphs.
            """
            system_content = "You are a senior policy economist advising government and central bank officials."
            section_title = "Policy Implications and Recommendations"
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_content),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title=section_title,
                content=response.content,
                order=8,
                section_type="policy_implications"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Policy implications completed")
            
        except Exception as e:
            print(f"Error writing policy implications: {e}")
            state["messages"].append(f"Error in policy implications: {str(e)}")
        
        return state
    
    def _write_economic_outlook(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write economic outlook section"""
        print("🔮 Writing economic outlook...")
        
        analysis_data = state["analysis_data"]
        analysis_type = analysis_data.get('analysis_type', '')
        outlook_data = analysis_data.get('economic_outlook', '')
        
        if 'tech_industry' in analysis_type:
            sector_focus = "technology industry"
            outlook_factors = """
            - AI and machine learning adoption trends
            - Cloud computing and digital transformation demand
            - Semiconductor supply chain recovery
            - Tech employment and talent availability
            - Venture capital and tech investment flows
            - Regulatory impacts from antitrust and data privacy laws
            - International competition in tech innovation
            - Consumer and enterprise technology spending
            """
        elif 'healthcare_industry' in analysis_type:
            sector_focus = "healthcare industry"
            outlook_factors = """
            - Aging population and healthcare demand growth
            - Medical device and pharmaceutical innovation
            - Healthcare digitization and telemedicine adoption
            - Healthcare workforce availability
            - Drug pricing and regulatory changes
            - Health insurance and reimbursement trends
            - Medical research and development investment
            - Public health infrastructure needs
            """
        else:
            return self._write_generic_economic_outlook(state)
        
        prompt = f"""
        Write a comprehensive {sector_focus} economic outlook based on:
        
        Industry Analysis: {analysis_data.get('industry_analysis', {}).get('industry_assessment', 'N/A')[:500]}
        
        Key Economic Insights: {analysis_data.get('economic_insights', 'N/A')[:400]}
        
        Consider these {sector_focus}-specific factors:
        {outlook_factors}
        
        The outlook should cover:
        1. Short-term {sector_focus} outlook (6-12 months)
        2. Medium-term sector projections (1-3 years)
        3. Long-term industry trends (3-5 years)
        4. Sector-specific growth drivers and constraints
        5. Technology adoption and innovation trends
        6. Market opportunities and competitive dynamics
        7. Risk factors specific to this industry
        8. Investment and business strategy implications
        
        Provide specific forecasts and confidence levels for the {sector_focus}.
        Length: 5-6 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=f"You are a {sector_focus} economist providing strategic sector forecasts."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title=f"{sector_focus.title()} Economic Outlook and Projections",
                content=response.content,
                order=9,
                section_type="economic_outlook"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Economic outlook completed")
            
        except Exception as e:
            print(f"Error writing economic outlook: {e}")
            state["messages"].append(f"Error in economic outlook: {str(e)}")
        
        return state

    def _write_generic_economic_outlook(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write generic economic outlook section (fallback)"""
        analysis_data = state["analysis_data"]
        outlook_data = analysis_data.get('economic_outlook', '')
        
        prompt = f"""
        Write a comprehensive economic outlook section based on:
        
        Economic Outlook: {outlook_data}
        
        Key Economic Insights: {analysis_data.get('economic_insights', 'N/A')[:500]}
        
        The economic outlook section should cover:
        1. Short-term economic forecast (3-6 months)
        2. Medium-term economic projections (6-18 months)
        3. Long-term economic trends (2-5 years)
        4. Economic scenario analysis and probabilities
        5. Key economic risks and uncertainties
        6. Growth, inflation, and sector projections
        7. Economic cycles and structural changes
        8. Confidence intervals and forecast accuracy
        
        Provide specific, quantitative forecasts where possible with confidence levels.
        Length: 5-6 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a chief economist providing strategic economic forecasts."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Economic Outlook and Projections",
                content=response.content,
                order=9,
                section_type="economic_outlook"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Economic outlook completed")
            
        except Exception as e:
            print(f"Error writing economic outlook: {e}")
            state["messages"].append(f"Error in economic outlook: {str(e)}")
        
        return state
    
    def _write_recommendations(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write recommendations section"""
        print("💡 Writing strategic recommendations...")
        
        analysis_data = state["analysis_data"]
        analysis_type = analysis_data.get('analysis_type', '')
        
        if 'tech_industry' in analysis_type:
            return self._write_tech_industry_recommendations(state)
        elif 'healthcare_industry' in analysis_type:
            return self._write_healthcare_industry_recommendations(state)
        else:
            return self._write_generic_recommendations(state)

    def _write_tech_industry_recommendations(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write tech industry specific recommendations"""
        analysis_data = state["analysis_data"]
        industry_data = analysis_data.get('industry_analysis', {})
        
        prompt = f"""
        Write strategic recommendations specifically for the technology industry based on:
        
        Tech Industry Analysis: {industry_data.get('industry_assessment', 'N/A')[:600]}
        
        Economic Context: {analysis_data.get('economic_insights', 'N/A')[:400]}
        
        Provide tech industry-specific recommendations in these areas:
        
        1. Technology Innovation Strategy (0-12 months):
           - AI/ML investment priorities and R&D focus areas
           - Cloud infrastructure and digital transformation strategies
           - Emerging technology adoption (quantum computing, AR/VR, IoT)
        
        2. Workforce and Talent Strategy (3-18 months):
           - Tech talent acquisition and retention strategies
           - Skills development and retraining programs
           - STEM education partnerships and initiatives
        
        3. Market and Investment Strategy (6-24 months):
           - Tech startup ecosystem development
           - Venture capital and private equity focus areas
           - International market expansion strategies
        
        4. Regulatory and Compliance Strategy (12-36 months):
           - Data privacy and cybersecurity compliance preparation
           - Antitrust and competition law adaptation
           - International regulatory coordination
        
        5. Supply Chain and Operations (immediate-24 months):
           - Semiconductor supply chain diversification
           - Manufacturing reshoring and nearshoring strategies
           - Tech hardware and software supply chain resilience
        
        6. Sustainability and ESG (12-60 months):
           - Green technology development priorities
           - Carbon footprint reduction in tech operations
           - Sustainable tech manufacturing practices
        
        Focus on actionable strategies specific to technology companies and the tech ecosystem.
        Provide specific timelines and implementation priorities.
        Length: 6-7 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a technology industry strategist providing specific recommendations for tech companies and the tech ecosystem."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Technology Industry Strategic Recommendations",
                content=response.content,
                order=10,
                section_type="recommendations"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Tech industry strategic recommendations completed")
            
        except Exception as e:
            print(f"Error writing tech recommendations: {e}")
            state["messages"].append(f"Error in tech recommendations: {str(e)}")
        
        return state

    def _write_healthcare_industry_recommendations(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write healthcare industry specific recommendations"""
        analysis_data = state["analysis_data"]
        industry_data = analysis_data.get('industry_analysis', {})
        
        prompt = f"""
        Write strategic recommendations specifically for the healthcare industry based on:
        
        Healthcare Industry Analysis: {industry_data.get('industry_assessment', 'N/A')[:600]}
        
        Economic Context: {analysis_data.get('economic_insights', 'N/A')[:400]}
        
        Provide healthcare industry-specific recommendations in these areas:
        
        1. Care Delivery and Innovation (0-12 months):
           - Telemedicine and digital health integration
           - Care pathway redesign and patient experience
           - Medical device and pharmaceutical R&D focus
        
        2. Workforce and Training (3-18 months):
           - Clinician retention and burnout mitigation
           - Upskilling for digital tools and data literacy
           - Academic and residency pipeline partnerships
        
        3. Payment and Market Strategy (6-24 months):
           - Value-based care adoption
           - Payer-provider alignment strategies
           - Market expansion and partnership models
        
        4. Compliance and Risk (12-36 months):
           - FDA, HIPAA, and data interoperability readiness
           - Supply resilience for critical therapeutics and devices
           - Cybersecurity and patient data protection
        
        5. Infrastructure and Operations (immediate-24 months):
           - Health IT modernization and interoperability
           - Capacity planning and surge readiness
           - Supply chain visibility and redundancy
        
        6. ESG and Public Health (12-60 months):
           - Sustainability in facilities and supply chains
           - Community health and equity initiatives
           - Preparedness for public health emergencies
        
        Focus on actionable strategies tailored to providers, payers, manufacturers, and health-tech.
        Provide specific timelines and implementation priorities.
        Length: 6-7 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a healthcare industry strategist providing specific recommendations for healthcare organizations."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Healthcare Industry Strategic Recommendations",
                content=response.content,
                order=10,
                section_type="recommendations"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Healthcare industry strategic recommendations completed")
            
        except Exception as e:
            print(f"Error writing healthcare recommendations: {e}")
            state["messages"].append(f"Error in healthcare recommendations: {str(e)}")
        
        return state

    def _write_generic_recommendations(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Write generic strategic recommendations (fallback)"""
        analysis_data = state["analysis_data"]
        recommendations = analysis_data.get('recommendations', [])
        policy_implications = analysis_data.get('policy_implications', '')
        economic_outlook = analysis_data.get('economic_outlook', '')
        
        prompt = f"""
        Write a detailed recommendations section based on the complete economic analysis:
        
        Policy Implications: {policy_implications[:800]}
        
        Economic Outlook: {economic_outlook[:800]}
        
        Existing Recommendations: {recommendations[0] if recommendations else 'None available'}
        
        The recommendations section should include:
        1. Specific monetary policy recommendations
        2. Fiscal policy recommendations and priorities
        3. Structural and regulatory policy suggestions
        4. Business and investment strategy implications
        5. Risk management recommendations
        6. International coordination recommendations
        7. Monitoring and early warning indicators
        8. Implementation timelines and priorities
        
        Structure recommendations by:
        - Immediate actions (0-3 months)
        - Short-term actions (3-12 months)  
        - Medium-term strategies (1-3 years)
        - Long-term structural reforms (3+ years)
        
        Be specific and actionable while acknowledging uncertainties.
        Length: 6-7 paragraphs.
        """
        
        try:
            response = self.llm.invoke([
                SystemMessage(content="You are a senior economic advisor providing strategic recommendations to policymakers."),
                HumanMessage(content=prompt)
            ])
            
            section = EconomicReportSection(
                title="Strategic Recommendations",
                content=response.content,
                order=10,
                section_type="recommendations"
            )
            
            state["report_sections"].append(section)
            state["messages"].append("Strategic recommendations completed")
            
        except Exception as e:
            print(f"Error writing recommendations: {e}")
            state["messages"].append(f"Error in recommendations: {str(e)}")
        
        return state
    
    def _compile_final_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Compile all sections into the final economic report"""
        print("📄 Compiling final economic report...")
        
        metadata = state["report_metadata"]
        sections = sorted(state["report_sections"], key=lambda x: x.order)
        
        # Create report header
        header = f"""
COMPREHENSIVE ECONOMIC ANALYSIS REPORT
{metadata['analysis_type'].upper()} ECONOMIC ASSESSMENT

Report Date: {metadata['created_date']}
Analysis Period: {metadata['data_period']}
Analysis Type: {metadata['analysis_type'].title()}
Indicators Analyzed: {metadata['indicators_count']}
Data Quality Assessment: {metadata['data_quality_score']}

{'=' * 80}
"""
        
        # Compile sections
        report_content = [header]
        
        for section in sections:
            section_header = f"\n{section.title.upper()}\n{'-' * len(section.title)}\n"
            report_content.append(section_header + section.content + "\n")
        
        # Add footer with disclaimers
        footer = f"""
{'=' * 80}

IMPORTANT DISCLAIMERS AND LIMITATIONS:

Economic Analysis Disclaimer:
• This report is for informational and educational purposes only
• Economic forecasts are subject to significant uncertainty and may not materialize
• Past economic performance does not guarantee future results
• Economic analysis is based on available data and current conditions
• Users should conduct independent analysis and consult qualified economists

Data and Methodology Limitations:
• Analysis depends on data quality and availability from third-party sources
• Economic indicators may be revised by statistical agencies
• Time lags in data publication may affect current economic assessment
• Model limitations and assumptions may influence analytical outcomes

Policy and Investment Disclaimer:
• This report does not constitute policy advice or investment recommendations
• Economic conditions can change rapidly and unpredictably
• Policy decisions should consider broader political and social factors
• Consult qualified advisors before making policy or investment decisions

Report generated by AI Economic Analysis System
Economic Analysis Period: {metadata['data_period']}
Report Generation Date: {metadata['created_date']}
Charts and Visualizations: {'Available' if metadata['has_charts'] else 'Not Available'}
"""
        
        final_report = '\n'.join(report_content) + footer
        state["final_report"] = final_report
        state["messages"].append("Final economic report compilation completed")
        
        return state
    
    def save_economic_report(self, report_state: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save the generated economic report to a file"""
        if not filename:
            analysis_type = report_state["report_metadata"]["analysis_type"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"economic_report_{analysis_type}_{timestamp}.txt"
        
        filepath = os.path.join(Config.REPORT_OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_state["final_report"])
        
        print(f"📄 Economic report saved to: {filepath}")
        return filepath

# Example usage and integration
if __name__ == "__main__":
    print("🚀 Economic Report Writer test completed successfully!")