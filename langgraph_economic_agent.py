#!/usr/bin/env python3
"""
LangGraph Economic Analysis Agent - Multi-step economic analysis workflow
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import operator
import json
from datetime import datetime
from economic_data_agent import EconomicDataAgent, EconomicData
from config import Config

class EconomicAnalysisState(TypedDict):
    """State for the economic analysis workflow"""
    analysis_type: str
    period: str
    include_regional: bool
    include_international: bool
    raw_economic_data: Optional[EconomicData]
    processed_analysis: Dict[str, Any]
    insights: str
    recommendations: List[str]
    messages: Annotated[List, operator.add]
    chart_paths: List[str]
    error_messages: List[str]
    policy_implications: str
    economic_outlook: str

class LangGraphEconomicAgent:
    """LangGraph-based economic analysis agent with 8-step workflow"""
    
    def __init__(self):
        Config.validate()
        self.llm = ChatOpenAI(
            model=Config.DEFAULT_MODEL,
            temperature=Config.TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        self.economic_agent = EconomicDataAgent()
        self.graph = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the focused economic analysis workflow"""
        workflow = StateGraph(EconomicAnalysisState)
        
        # Add focused nodes based on analysis type
        workflow.add_node("data_collection", self._collect_economic_data)
        
        # Conditional analysis based on type
        workflow.add_node("gdp_analysis", self._analyze_economic_growth)
        workflow.add_node("inflation_analysis", self._analyze_inflation_trends)
        workflow.add_node("market_trends_analysis", self._analyze_market_sentiment)
        workflow.add_node("industry_analysis", self._analyze_industry_performance)
        
        workflow.add_node("generate_insights", self._generate_economic_insights)
        workflow.add_node("create_visualizations", self._create_economic_visualizations)
        workflow.add_node("policy_implications", self._analyze_policy_implications)
        workflow.add_node("economic_outlook", self._generate_economic_outlook)
        
        # Set entry point
        workflow.set_entry_point("data_collection")
        
        # Add conditional edges based on analysis type
        workflow.add_conditional_edges(
            "data_collection",
            self._route_analysis,
            {
                "gdp_focus": "gdp_analysis",
                "inflation_focus": "inflation_analysis", 
                "market_trend": "market_trends_analysis",
                "industry_performance": "industry_analysis",
                "tech_industry_performance": "industry_analysis",
                "healthcare_industry_performance": "industry_analysis",
                "finance_industry_performance": "industry_analysis",
                "energy_industry_performance": "industry_analysis",
                "supply_chain_performance": "industry_analysis"
            }
        )
        
        # Continue to insights generation
        for analysis_type in ["gdp_analysis", "inflation_analysis", "market_trends_analysis", "industry_analysis"]:
            workflow.add_edge(analysis_type, "generate_insights")
        
        workflow.add_edge("generate_insights", "create_visualizations")
        workflow.add_edge("create_visualizations", "policy_implications")
        workflow.add_edge("policy_implications", "economic_outlook")
        workflow.add_edge("economic_outlook", END)
        
        return workflow.compile()

    def _route_analysis(self, state: EconomicAnalysisState) -> str:
        """Route to appropriate analysis based on type"""
        analysis_type = state["analysis_type"]
        
        if "gdp" in analysis_type:
            return "gdp_focus"
        elif "inflation" in analysis_type:
            return "inflation_focus"
        elif "market" in analysis_type:
            return "market_trend"
        else:
            return "industry_performance"
    
    def _collect_economic_data(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Step 1: Collect comprehensive economic data"""
        print("📊 Step 1: Collecting comprehensive economic data...")
        
        try:
            economic_data = self.economic_agent.fetch_comprehensive_economic_data(
                analysis_type=state["analysis_type"],
                period=state["period"],
                include_regional=state.get("include_regional", True),
                include_international=state.get("include_international", True),
                include_market_data=True
            )
            
            state["raw_economic_data"] = economic_data
            state["messages"] = [f"Collected {len(economic_data.indicators)} economic indicators"]
            
            # Initialize processed analysis
            state["processed_analysis"] = {
                "data_summary": economic_data.summary_statistics,
                "data_quality": economic_data.data_quality_report
            }
            
            print(f"✅ Successfully collected data for {len(economic_data.indicators)} indicators")
            
        except Exception as e:
            error_msg = f"Error collecting economic data: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"] = [error_msg]
            state["messages"] = [error_msg]
        
        return state
    
    def _analyze_economic_growth(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Step 2: Analyze economic growth indicators"""
        print("📈 Step 2: Analyzing economic growth indicators...")
        
        try:
            economic_data = state["raw_economic_data"]
            growth_indicators = ["gdp", "gdp_real", "gdp_growth", "industrial_production"]
            
            growth_analysis = {
                "indicator_analysis": {},
                "growth_trends": {},
                "sectoral_performance": {},
                "growth_assessment": ""
            }
            
            # Analyze each growth indicator
            for indicator_id in growth_indicators:
                if indicator_id in economic_data.indicators:
                    indicator = economic_data.indicators[indicator_id]
                    analysis = self._analyze_single_indicator(indicator)
                    growth_analysis["indicator_analysis"][indicator_id] = analysis
            
            # Generate comprehensive growth assessment using LLM
            growth_prompt = f"""
            Analyze the economic growth situation based on the following indicators:
            
            {json.dumps(growth_analysis["indicator_analysis"], indent=2, default=str)}
            
            Please provide:
            1. Overall economic growth assessment
            2. Key growth trends and patterns
            3. Strengths and weaknesses in growth
            4. Comparison to historical norms
            5. Growth sustainability analysis
            
            Be specific and data-driven in your analysis.
            """
            
            response = self.llm.invoke([
                SystemMessage(content="You are a senior economist specializing in economic growth analysis."),
                HumanMessage(content=growth_prompt)
            ])
            
            growth_analysis["growth_assessment"] = response.content
            state["processed_analysis"]["growth"] = growth_analysis
            state["messages"].append("Economic growth analysis completed")
            
            print("✅ Economic growth analysis completed")
            
        except Exception as e:
            error_msg = f"Error in growth analysis: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"].append(error_msg)
        
        return state
    
    def _analyze_inflation_trends(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Step 3: Analyze inflation and price trends"""
        print("💰 Step 3: Analyzing inflation and price trends...")
        
        try:
            economic_data = state["raw_economic_data"]
            inflation_indicators = ["cpi", "core_cpi", "pce", "core_pce"]
            
            inflation_analysis = {
                "indicator_analysis": {},
                "inflation_trends": {},
                "price_pressures": {},
                "inflation_assessment": ""
            }
            
            # Analyze inflation indicators
            for indicator_id in inflation_indicators:
                if indicator_id in economic_data.indicators:
                    indicator = economic_data.indicators[indicator_id]
                    analysis = self._analyze_single_indicator(indicator, calculate_yoy=True)
                    inflation_analysis["indicator_analysis"][indicator_id] = analysis
            
            # Generate inflation assessment using LLM
            inflation_prompt = f"""
            Analyze the inflation situation based on the following data:
            
            {json.dumps(inflation_analysis["indicator_analysis"], indent=2, default=str)}
            
            Please provide:
            1. Current inflation trends and trajectory
            2. Core vs headline inflation analysis
            3. Inflationary pressures and drivers
            4. Comparison to Federal Reserve targets
            5. Inflation expectations and outlook
            6. Risk assessment (deflationary vs inflationary risks)
            
            Focus on actionable insights for policy and investment decisions.
            """
            
            response = self.llm.invoke([
                SystemMessage(content="You are an inflation expert and monetary policy analyst."),
                HumanMessage(content=inflation_prompt)
            ])
            
            inflation_analysis["inflation_assessment"] = response.content
            state["processed_analysis"]["inflation"] = inflation_analysis
            state["messages"].append("Inflation trends analysis completed")
            
            print("✅ Inflation trends analysis completed")
            
        except Exception as e:
            error_msg = f"Error in inflation analysis: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"].append(error_msg)
        
        return state
    
    def _analyze_employment_situation(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Step 4: Analyze employment and labor market conditions"""
        print("👥 Step 4: Analyzing employment and labor market...")
        
        try:
            economic_data = state["raw_economic_data"]
            employment_indicators = ["unemployment", "nonfarm_payrolls", "labor_force_participation", "jobless_claims"]
            
            employment_analysis = {
                "indicator_analysis": {},
                "labor_trends": {},
                "employment_quality": {},
                "employment_assessment": ""
            }
            
            # Analyze employment indicators
            for indicator_id in employment_indicators:
                if indicator_id in economic_data.indicators:
                    indicator = economic_data.indicators[indicator_id]
                    analysis = self._analyze_single_indicator(indicator)
                    employment_analysis["indicator_analysis"][indicator_id] = analysis
            
            # Generate employment assessment using LLM
            employment_prompt = f"""
            Analyze the employment and labor market situation based on:
            
            {json.dumps(employment_analysis["indicator_analysis"], indent=2, default=str)}
            
            Please provide:
            1. Overall labor market health assessment
            2. Employment trends and job creation analysis
            3. Labor force participation and demographic trends
            4. Unemployment characteristics and duration
            5. Labor market tightness indicators
            6. Wage growth implications
            7. Regional employment variations (if data available)
            
            Focus on labor market dynamics and policy implications.
            """
            
            response = self.llm.invoke([
                SystemMessage(content="You are a labor economist specializing in employment analysis."),
                HumanMessage(content=employment_prompt)
            ])
            
            employment_analysis["employment_assessment"] = response.content
            state["processed_analysis"]["employment"] = employment_analysis
            state["messages"].append("Employment situation analysis completed")
            
            print("✅ Employment situation analysis completed")
            
        except Exception as e:
            error_msg = f"Error in employment analysis: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"].append(error_msg)
        
        return state
    
    def _analyze_monetary_policy(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Step 5: Analyze monetary policy and financial conditions"""
        print("🏦 Step 5: Analyzing monetary policy and financial conditions...")
        
        try:
            economic_data = state["raw_economic_data"]
            monetary_indicators = ["fed_rate", "10y_treasury", "2y_treasury", "yield_curve"]
            
            monetary_analysis = {
                "indicator_analysis": {},
                "policy_stance": {},
                "financial_conditions": {},
                "monetary_assessment": ""
            }
            
            # Analyze monetary indicators
            for indicator_id in monetary_indicators:
                if indicator_id in economic_data.indicators:
                    indicator = economic_data.indicators[indicator_id]
                    analysis = self._analyze_single_indicator(indicator)
                    monetary_analysis["indicator_analysis"][indicator_id] = analysis
            
            # Generate monetary policy assessment using LLM
            monetary_prompt = f"""
            Analyze the monetary policy and financial conditions based on:
            
            {json.dumps(monetary_analysis["indicator_analysis"], indent=2, default=str)}
            
            Please provide:
            1. Current monetary policy stance assessment
            2. Interest rate trends and policy trajectory
            3. Yield curve analysis and implications
            4. Financial conditions index assessment
            5. Policy effectiveness and transmission mechanisms
            6. Future policy direction and risks
            7. Market expectations vs actual policy
            
            Focus on Federal Reserve policy implications and financial market impacts.
            """
            
            response = self.llm.invoke([
                SystemMessage(content="You are a monetary policy expert and Federal Reserve analyst."),
                HumanMessage(content=monetary_prompt)
            ])
            
            monetary_analysis["monetary_assessment"] = response.content
            state["processed_analysis"]["monetary"] = monetary_analysis
            state["messages"].append("Monetary policy analysis completed")
            
            print("✅ Monetary policy analysis completed")
            
        except Exception as e:
            error_msg = f"Error in monetary analysis: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"].append(error_msg)
        
        return state

    def _analyze_industry_performance(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Analyze specific industry performance"""
        print(f"🏭 Analyzing {state['analysis_type']} performance...")
        
        try:
            economic_data = state["raw_economic_data"]
            analysis_type = state["analysis_type"]
            
            # Get relevant indicators for this industry
            relevant_indicators = {}
            for indicator_id, indicator in economic_data.indicators.items():
                if self._is_relevant_for_industry(indicator_id, analysis_type):
                    relevant_indicators[indicator_id] = indicator
            
            # Generate industry-specific analysis using LLM
            industry_prompt = f"""
            Analyze the {analysis_type.replace('_', ' ')} based on the following indicators:
            
            {json.dumps(self._prepare_indicator_data(relevant_indicators), indent=2, default=str)}
            
            Please provide:
            1. Current industry health and performance
            2. Employment trends in this sector
            3. Industry-specific growth drivers and challenges
            4. Competitive dynamics and market positioning
            5. Future outlook for this industry
            6. Policy implications specific to this sector
            
            Focus specifically on the {analysis_type.replace('_industry_performance', '').replace('_performance', '')} sector.
            """
            
            response = self.llm.invoke([
                SystemMessage(content=f"You are an industry analyst specializing in {analysis_type.replace('_', ' ')} sector analysis."),
                HumanMessage(content=industry_prompt)
            ])
            
            industry_analysis = {
                "industry_assessment": response.content,
                "indicator_analysis": self._prepare_indicator_data(relevant_indicators),
                "sector_focus": analysis_type.replace('_industry_performance', '').replace('_performance', '')
            }
            
            state["processed_analysis"]["industry"] = industry_analysis
            state["messages"].append(f"{analysis_type.replace('_', ' ').title()} analysis completed")
            
        except Exception as e:
            error_msg = f"Error in industry analysis: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"].append(error_msg)
        
        return state

    def _is_relevant_for_industry(self, indicator_id: str, analysis_type: str) -> bool:
        """Check if indicator is relevant for specific industry analysis"""
        industry_mappings = {
            'tech_industry_performance': ['tech_employment', 'software_employment', 'tech_production', 'semiconductor_shipments', 'business_investment', 'industrial_production'],
            'healthcare_industry_performance': ['healthcare_employment', 'healthcare_spending', 'business_investment'],
            'finance_industry_performance': ['finance_employment', 'bank_lending', 'fed_rate', '10y_treasury'],
            'energy_industry_performance': ['energy_employment', 'oil_production', 'business_investment'],
            'supply_chain_performance': ['supply_chain_pressure', 'transportation_costs', 'industrial_production'],
            'industry_performance': ['tech_employment', 'healthcare_employment', 'finance_employment', 'energy_employment', 'supply_chain_pressure']
        }
        
        return indicator_id in industry_mappings.get(analysis_type, [])

    def _prepare_indicator_data(self, indicators: Dict) -> Dict:
        """Prepare indicator data for LLM analysis"""
        prepared_data = {}
        for indicator_id, indicator in indicators.items():
            if not indicator.data.empty:
                analysis = self._analyze_single_indicator(indicator)
                prepared_data[indicator_id] = {
                    'name': indicator.name,
                    'latest_value': analysis.get('latest_value'),
                    'trend': analysis.get('trend'),
                    'recent_change': analysis.get('recent_change'),
                    'category': indicator.category
                }
        return prepared_data
    
    def _analyze_market_sentiment(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Step 6: Analyze market sentiment and financial indicators"""
        print("📊 Step 6: Analyzing market sentiment and financial indicators...")
        
        try:
            economic_data = state["raw_economic_data"]
            
            sentiment_analysis = {
                "market_performance": {},
                "sentiment_indicators": {},
                "risk_indicators": {},
                "sentiment_assessment": ""
            }
            
            # Analyze market data
            if economic_data.market_data:
                for market_name, market_df in economic_data.market_data.items():
                    if not market_df.empty:
                        analysis = self._analyze_market_data(market_df, market_name)
                        sentiment_analysis["market_performance"][market_name] = analysis
            
            # Analyze sentiment indicators
            sentiment_indicators = ["consumer_confidence", "consumer_sentiment"]
            for indicator_id in sentiment_indicators:
                if indicator_id in economic_data.indicators:
                    indicator = economic_data.indicators[indicator_id]
                    analysis = self._analyze_single_indicator(indicator)
                    sentiment_analysis["sentiment_indicators"][indicator_id] = analysis
            
            # Analyze VIX from market data if available
            if "vix" in economic_data.market_data:
                vix_analysis = self._analyze_market_data(economic_data.market_data["vix"], "vix")
                sentiment_analysis["risk_indicators"]["vix"] = vix_analysis
            
            # Generate market sentiment assessment using LLM
            sentiment_prompt = f"""
            Analyze market sentiment and financial conditions based on:
            
            Market Performance: {json.dumps(sentiment_analysis["market_performance"], indent=2, default=str)}
            
            Sentiment Indicators: {json.dumps(sentiment_analysis["sentiment_indicators"], indent=2, default=str)}
            
            Risk Indicators: {json.dumps(sentiment_analysis["risk_indicators"], indent=2, default=str)}
            
            Please provide:
            1. Overall market sentiment assessment
            2. Consumer and business confidence trends
            3. Financial market stress indicators
            4. Risk appetite and volatility analysis
            5. Market-economy relationship analysis
            6. Sentiment-driven economic risks and opportunities
            
            Focus on how sentiment affects economic outlook and policy decisions.
            """
            
            response = self.llm.invoke([
                SystemMessage(content="You are a market sentiment analyst and behavioral economist."),
                HumanMessage(content=sentiment_prompt)
            ])
            
            sentiment_analysis["sentiment_assessment"] = response.content
            state["processed_analysis"]["sentiment"] = sentiment_analysis
            state["messages"].append("Market sentiment analysis completed")
            
            print("✅ Market sentiment analysis completed")
            
        except Exception as e:
            error_msg = f"Error in sentiment analysis: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"].append(error_msg)
        
        return state
    
    def _generate_economic_insights(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Step 7: Generate comprehensive economic insights"""
        print("💡 Step 7: Generating comprehensive economic insights...")
        
        try:
            # Compile all analysis results
            all_analysis = state["processed_analysis"]
            
            insights_prompt = f"""
            Based on the comprehensive economic analysis below, provide key economic insights:
            
            Growth Analysis: {all_analysis.get('growth', {}).get('growth_assessment', 'N/A')}
            
            Inflation Analysis: {all_analysis.get('inflation', {}).get('inflation_assessment', 'N/A')}
            
            Employment Analysis: {all_analysis.get('employment', {}).get('employment_assessment', 'N/A')}
            
            Monetary Policy Analysis: {all_analysis.get('monetary', {}).get('monetary_assessment', 'N/A')}
            
            Market Sentiment Analysis: {all_analysis.get('sentiment', {}).get('sentiment_assessment', 'N/A')}
            
            Please provide:
            1. Key economic themes and interconnections
            2. Economic cycle position assessment
            3. Major economic risks and opportunities
            4. Cross-indicator relationships and contradictions
            5. Economic narrative and storyline
            6. Critical economic inflection points
            
            Synthesize insights across all economic dimensions.
            """
            
            response = self.llm.invoke([
                SystemMessage(content="You are a chief economist providing strategic economic insights."),
                HumanMessage(content=insights_prompt)
            ])
            
            state["insights"] = response.content
            state["messages"].append("Economic insights generated successfully")
            
            print("✅ Economic insights generated successfully")
            
        except Exception as e:
            error_msg = f"Error generating insights: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"].append(error_msg)
            state["insights"] = "Unable to generate insights due to an error."
        
        return state
    
    def _create_economic_visualizations(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Step 8: Create comprehensive economic visualizations"""
        print("📊 Step 8: Creating economic visualizations...")
        
        chart_paths = []
        
        try:
            economic_data = state["raw_economic_data"]
            
            if economic_data:
                # Create main economic dashboard
                dashboard_path = self.economic_agent.create_economic_dashboard(economic_data)
                chart_paths.append(dashboard_path)
                
                print(f"✅ Economic dashboard created: {dashboard_path}")
            
            state["chart_paths"] = chart_paths
            state["messages"].append(f"Created {len(chart_paths)} economic visualizations")
            
        except Exception as e:
            error_msg = f"Error creating visualizations: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"].append(error_msg)
        
        return state
    
    def _analyze_policy_implications(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Step 9: Analyze policy implications and recommendations"""
        print("🏛️ Step 9: Analyzing policy implications...")
        
        try:
            all_analysis = state["processed_analysis"]
            insights = state["insights"]
            
            policy_prompt = f"""
            Based on the economic analysis and insights, analyze policy implications:
            
            Economic Insights: {insights}
            
            Key Economic Conditions:
            - Growth: {all_analysis.get('growth', {}).get('growth_assessment', 'N/A')[:200]}...
            - Inflation: {all_analysis.get('inflation', {}).get('inflation_assessment', 'N/A')[:200]}...
            - Employment: {all_analysis.get('employment', {}).get('employment_assessment', 'N/A')[:200]}...
            - Monetary Policy: {all_analysis.get('monetary', {}).get('monetary_assessment', 'N/A')[:200]}...
            
            Please provide:
            1. Federal Reserve policy implications and recommendations
            2. Fiscal policy considerations and needs
            3. Regulatory policy implications
            4. Trade and international policy considerations
            5. Long-term structural policy needs
            6. Policy risks and unintended consequences
            7. Policy coordination requirements
            
            Focus on actionable policy recommendations based on current economic conditions.
            """
            
            response = self.llm.invoke([
                SystemMessage(content="You are a senior policy economist advising government and central bank officials."),
                HumanMessage(content=policy_prompt)
            ])
            
            state["policy_implications"] = response.content
            state["messages"].append("Policy implications analysis completed")
            
            print("✅ Policy implications analysis completed")
            
        except Exception as e:
            error_msg = f"Error in policy analysis: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"].append(error_msg)
            state["policy_implications"] = "Unable to generate policy implications due to an error."
        
        return state
    
    def _generate_economic_outlook(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Step 10: Generate economic outlook and recommendations"""
        print("🔮 Step 10: Generating economic outlook and recommendations...")
        
        try:
            all_analysis = state["processed_analysis"]
            insights = state["insights"]
            policy_implications = state["policy_implications"]
            
            outlook_prompt = f"""
            Based on the comprehensive economic analysis, provide an economic outlook:
            
            Economic Insights: {insights[:500]}...
            
            Policy Implications: {policy_implications[:500]}...
            
            Please provide:
            1. Short-term economic outlook (3-6 months)
            2. Medium-term economic outlook (6-18 months)
            3. Long-term economic outlook (2-5 years)
            4. Key economic scenarios and their probabilities
            5. Major economic risks to monitor
            6. Investment and business strategy implications
            7. Specific economic forecasts and ranges
            8. Early warning indicators to watch
            
            Provide specific, actionable economic outlook with confidence levels.
            """
            
            response = self.llm.invoke([
                SystemMessage(content="You are a chief economist providing strategic economic forecasts and outlook."),
                HumanMessage(content=outlook_prompt)
            ])
            
            state["economic_outlook"] = response.content
            state["recommendations"] = [response.content]  # For compatibility
            state["messages"].append("Economic outlook and recommendations generated")
            
            print("✅ Economic outlook and recommendations generated")
            
        except Exception as e:
            error_msg = f"Error generating outlook: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_messages"].append(error_msg)
            state["economic_outlook"] = "Unable to generate economic outlook due to an error."
            state["recommendations"] = ["Unable to generate recommendations due to an error."]
        
        return state
    
    def _analyze_single_indicator(self, indicator, calculate_yoy: bool = False) -> Dict[str, Any]:
        """Analyze a single economic indicator"""
        analysis = {
            "latest_value": None,
            "latest_date": None,
            "trend": "unknown",
            "volatility": None,
            "recent_change": None,
            "yoy_change": None,
            "historical_context": {}
        }
        
        try:
            if not indicator.data.empty:
                data = indicator.data['value'].dropna()
                
                if len(data) > 0:
                    # Latest value and date
                    analysis["latest_value"] = float(data.iloc[-1])
                    analysis["latest_date"] = data.index[-1].strftime('%Y-%m-%d')
                    
                    # Recent change
                    if len(data) >= 2:
                        recent_change = data.iloc[-1] - data.iloc[-2]
                        analysis["recent_change"] = float(recent_change)
                        analysis["trend"] = "up" if recent_change > 0 else "down" if recent_change < 0 else "stable"
                    
                    # Year-over-year change if requested and data available
                    if calculate_yoy and len(data) >= 12:
                        try:
                            yoy_change = ((data.iloc[-1] - data.iloc[-13]) / data.iloc[-13]) * 100
                            analysis["yoy_change"] = float(yoy_change)
                        except (IndexError, ZeroDivisionError):
                            pass
                    
                    # Volatility (standard deviation of recent changes)
                    if len(data) >= 10:
                        recent_changes = data.pct_change().tail(10).dropna()
                        if len(recent_changes) > 0:
                            analysis["volatility"] = float(recent_changes.std())
                    
                    # Historical context
                    analysis["historical_context"] = {
                        "mean": float(data.mean()),
                        "std": float(data.std()),
                        "min": float(data.min()),
                        "max": float(data.max()),
                        "percentile_current": float((data <= data.iloc[-1]).mean() * 100)
                    }
        
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def _analyze_market_data(self, market_df, market_name: str) -> Dict[str, Any]:
        """Analyze market data from Yahoo Finance"""
        analysis = {
            "latest_price": None,
            "latest_date": None,
            "price_change": None,
            "volatility": None,
            "trend": "unknown"
        }
        
        try:
            if not market_df.empty and 'Close' in market_df.columns:
                close_prices = market_df['Close'].dropna()
                
                if len(close_prices) > 0:
                    # Latest price and date
                    analysis["latest_price"] = float(close_prices.iloc[-1])
                    analysis["latest_date"] = close_prices.index[-1].strftime('%Y-%m-%d')
                    
                    # Price change
                    if len(close_prices) >= 2:
                        price_change = ((close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2]) * 100
                        analysis["price_change"] = float(price_change)
                        analysis["trend"] = "up" if price_change > 0 else "down" if price_change < 0 else "stable"
                    
                    # Volatility (standard deviation of returns)
                    if len(close_prices) >= 20:
                        returns = close_prices.pct_change().dropna()
                        analysis["volatility"] = float(returns.std() * (252**0.5))  # Annualized volatility
        
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def analyze_economy(self, 
                       analysis_type: str = "comprehensive",
                       period: str = "5y",
                       include_regional: bool = True,
                       include_international: bool = True) -> EconomicAnalysisState:
        """
        Run the complete economic analysis workflow
        
        Args:
            analysis_type: Type of economic analysis
            period: Time period for analysis
            include_regional: Whether to include regional data
            include_international: Whether to include international data
        
        Returns:
            Complete economic analysis state
        """
        initial_state = EconomicAnalysisState(
            analysis_type=analysis_type,
            period=period,
            include_regional=include_regional,
            include_international=include_international,
            raw_economic_data=None,
            processed_analysis={},
            insights="",
            recommendations=[],
            messages=[],
            chart_paths=[],
            error_messages=[],
            policy_implications="",
            economic_outlook=""
        )
        
        print(f"🚀 Starting comprehensive economic analysis")
        print(f"Analysis Type: {analysis_type}")
        print(f"Period: {period}")
        print("-" * 50)
        
        final_state = self.graph.invoke(initial_state)
        print("✅ Economic analysis completed!")
        
        return final_state
    
    def get_analysis_summary(self, state: EconomicAnalysisState) -> Dict[str, Any]:
        """Get a structured summary of the economic analysis results"""
        economic_data = state["raw_economic_data"]
        
        return {
            'analysis_type': state['analysis_type'],
            'period': state['period'],
            'indicators_analyzed': list(economic_data.indicators.keys()) if economic_data else [],
            'growth_analysis': state['processed_analysis'].get('growth', {}),
            'inflation_analysis': state['processed_analysis'].get('inflation', {}),
            'industry_analysis': state['processed_analysis'].get('industry', {}),
            'market_trends_analysis': state['processed_analysis'].get('market_trends', {}),
            'sentiment_analysis': state['processed_analysis'].get('sentiment', {}),
            'economic_insights': state['insights'],
            'policy_implications': state['policy_implications'],
            'economic_outlook': state['economic_outlook'],
            'recommendations': state['recommendations'],
            'chart_paths': state['chart_paths'],
            'messages': state['messages'],
            'errors': state['error_messages'],
            'data_quality': economic_data.data_quality_report if economic_data else {}
        }

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    agent = LangGraphEconomicAgent()
    
    # Run comprehensive economic analysis
    result = agent.analyze_economy(
        analysis_type="comprehensive",
        period="5y",
        include_regional=True,
        include_international=True
    )
    
    summary = agent.get_analysis_summary(result)
    
    print("\n" + "="*60)
    print("ECONOMIC ANALYSIS SUMMARY")
    print("="*60)
    print(f"Analysis Type: {summary['analysis_type']}")
    print(f"Period: {summary['period']}")
    print(f"Indicators Analyzed: {len(summary['indicators_analyzed'])}")
    print(f"Charts Created: {len(summary['chart_paths'])}")
    print(f"Messages: {len(summary['messages'])}")
    
    if summary['economic_insights']:
        print(f"\nKey Economic Insights:\n{summary['economic_insights'][:500]}...")
    
    if summary['economic_outlook']:
        print(f"\nEconomic Outlook:\n{summary['economic_outlook'][:500]}...")