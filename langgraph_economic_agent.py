from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
#from langgraph.prebuilt import ToolExecutor
#from langgraph.prebuilt.tool_executor import ToolExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.schema import HumanMessage, SystemMessage
import operator
from economic_data_agent import EconomicDataAgent, EconomicData
from economic_config import EconomicConfig
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

class EconomicAnalysisState(TypedDict):
    """State for the economic analysis workflow"""
    analysis_type: str  # 'gdp', 'inflation', 'market_trends', 'industry', 'comprehensive'
    period: str
    focus_industries: List[str]
    raw_data: Dict[str, Any]
    gdp_analysis: Dict[str, Any]
    inflation_analysis: Dict[str, Any]
    market_analysis: Dict[str, Any]
    industry_analysis: Dict[str, Any]
    economic_insights: List[str]
    policy_implications: List[str]
    forecasts: Dict[str, Any]
    messages: Annotated[List, operator.add]
    chart_paths: List[str]
    error_messages: List[str]

class LangGraphEconomicAgent:
    """LangGraph-based economic analysis agent"""
    
    def __init__(self):
        EconomicConfig.validate()
        self.llm = ChatOpenAI(
            model=EconomicConfig.DEFAULT_MODEL,
            temperature=0.1,
            api_key=EconomicConfig.OPENAI_API_KEY
        )
        self.economic_agent = EconomicDataAgent()
        self._graph = None
    
    @property
    def graph(self):
        """Property to access the compiled graph for LangGraph Studio"""
        if self._graph is None:
            self._graph = self._create_workflow()
        return self._graph
    
    def _create_workflow(self):
        """Create the LangGraph workflow for economic analysis"""
        workflow = StateGraph(EconomicAnalysisState)
        
        # Add nodes
        workflow.add_node("collect_economic_data", self._collect_economic_data)
        workflow.add_node("analyze_gdp", self._analyze_gdp)
        workflow.add_node("analyze_inflation", self._analyze_inflation)
        workflow.add_node("analyze_market_trends", self._analyze_market_trends)
        workflow.add_node("analyze_industry_performance", self._analyze_industry_performance)
        workflow.add_node("generate_economic_insights", self._generate_economic_insights)
        workflow.add_node("create_visualizations", self._create_visualizations)
        workflow.add_node("policy_implications", self._analyze_policy_implications)
        workflow.add_node("generate_forecasts", self._generate_forecasts)
        workflow.add_node("final_report", self._generate_final_report)
        
        # Define the workflow with conditional routing based on analysis type
        workflow.set_entry_point("collect_economic_data")
        
        # Always collect data first
        workflow.add_edge("collect_economic_data", "analyze_gdp")
        
        # Conditional routing based on analysis type
        workflow.add_conditional_edges(
            "analyze_gdp",
            self._should_continue_to_inflation,
            {
                "inflation": "analyze_inflation",
                "skip": "generate_economic_insights"
            }
        )
        
        workflow.add_conditional_edges(
            "analyze_inflation",
            self._should_continue_to_market,
            {
                "market": "analyze_market_trends",
                "skip": "generate_economic_insights"
            }
        )
        
        workflow.add_conditional_edges(
            "analyze_market_trends",
            self._should_continue_to_industry,
            {
                "industry": "analyze_industry_performance",
                "skip": "generate_economic_insights"
            }
        )
        
        # Continue with remaining steps
        workflow.add_edge("analyze_industry_performance", "generate_economic_insights")
        workflow.add_edge("generate_economic_insights", "create_visualizations")
        workflow.add_edge("create_visualizations", "policy_implications")
        workflow.add_edge("policy_implications", "generate_forecasts")
        workflow.add_edge("generate_forecasts", "final_report")
        workflow.add_edge("final_report", END)
        
        return workflow.compile()
    
    def _should_continue_to_inflation(self, state: EconomicAnalysisState) -> str:
        """Determine if analysis should continue to inflation based on analysis type"""
        analysis_type = state.get("analysis_type", "comprehensive")
        if analysis_type in ["comprehensive", "inflation", "market_trends", "industry"]:
            return "inflation"
        return "skip"
    
    def _should_continue_to_market(self, state: EconomicAnalysisState) -> str:
        """Determine if analysis should continue to market trends based on analysis type"""
        analysis_type = state.get("analysis_type", "comprehensive")
        if analysis_type in ["comprehensive", "market_trends", "industry"]:
            return "market"
        return "skip"
    
    def _should_continue_to_industry(self, state: EconomicAnalysisState) -> str:
        """Determine if analysis should continue to industry analysis based on analysis type"""
        analysis_type = state.get("analysis_type", "comprehensive")
        if analysis_type in ["comprehensive", "industry"]:
            return "industry"
        return "skip"
    
    def _collect_economic_data(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Collect economic data from FRED based on analysis type"""
        try:
            period = state.get("period", EconomicConfig.DEFAULT_PERIOD)
            analysis_type = state.get("analysis_type", "comprehensive")
            
            # Initialize raw_data
            state["raw_data"] = {}
            
            # Collect data based on analysis type
            if analysis_type in ["comprehensive", "gdp"]:
                gdp_data = self.economic_agent.fetch_gdp_indicators(period)
                state["raw_data"]["gdp"] = gdp_data
                state["messages"].append(f"✅ Collected GDP data for {period}")
            
            if analysis_type in ["comprehensive", "inflation"]:
                inflation_data = self.economic_agent.fetch_inflation_indicators(period)
                state["raw_data"]["inflation"] = inflation_data
                state["messages"].append(f"✅ Collected inflation data for {period}")
            
            if analysis_type in ["comprehensive", "market_trends"]:
                market_data = self.economic_agent.fetch_market_trends(period)
                state["raw_data"]["market"] = market_data
                state["messages"].append(f"✅ Collected market data for {period}")
            
            if analysis_type in ["comprehensive", "industry"]:
                industry_data = self.economic_agent.fetch_industry_performance(period)
                state["raw_data"]["industry"] = industry_data
                state["messages"].append(f"✅ Collected industry data for {period}")
            
            state["messages"].append(f"✅ Successfully collected economic data for {analysis_type} analysis")
            
        except Exception as e:
            error_msg = f"Error collecting economic data: {str(e)}"
            state["error_messages"].append(error_msg)
            state["messages"].append(f"❌ {error_msg}")
        
        return state
    
    def _analyze_gdp(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Analyze GDP indicators"""
        try:
            if "gdp" not in state["raw_data"]:
                state["messages"].append("⚠️ No GDP data available for analysis")
                return state
                
            gdp_data = state["raw_data"]["gdp"]
            
            analysis = {}
            
            # Current GDP analysis
            if "gdp" in gdp_data and gdp_data["gdp"]:
                current_gdp = gdp_data["gdp"].get_latest_value()
                gdp_yoy = gdp_data["gdp"].get_yoy_change()
                
                analysis["current_gdp"] = current_gdp
                analysis["gdp_yoy_change"] = gdp_yoy
            
            # GDP Growth analysis
            if "gdp_growth" in gdp_data and gdp_data["gdp_growth"]:
                current_growth = gdp_data["gdp_growth"].get_latest_value()
                avg_growth = gdp_data["gdp_growth"].data.mean()
                
                analysis["current_growth_rate"] = current_growth
                analysis["average_growth_rate"] = avg_growth
                analysis["growth_trend"] = "positive" if current_growth > avg_growth else "negative"
            
            # GDP per Capita analysis
            if "gdp_per_capita" in gdp_data and gdp_data["gdp_per_capita"]:
                current_per_capita = gdp_data["gdp_per_capita"].get_latest_value()
                per_capita_yoy = gdp_data["gdp_per_capita"].get_yoy_change()
                
                analysis["current_gdp_per_capita"] = current_per_capita
                analysis["gdp_per_capita_yoy"] = per_capita_yoy
            
            # AI-powered GDP analysis
            gdp_prompt = f"""
            Analyze the following GDP data and provide economic insights:
            
            Current GDP: ${analysis.get('current_gdp', 'N/A')} billion
            GDP YoY Change: {analysis.get('gdp_yoy_change', 'N/A')}%
            Current Growth Rate: {analysis.get('current_growth_rate', 'N/A')}%
            Average Growth Rate: {analysis.get('average_growth_rate', 'N/A')}%
            Growth Trend: {analysis.get('growth_trend', 'N/A')}
            GDP per Capita: ${analysis.get('current_gdp_per_capita', 'N/A')}
            GDP per Capita YoY: {analysis.get('gdp_per_capita_yoy', 'N/A')}%
            
            Provide insights on:
            1. Overall economic health based on GDP metrics
            2. Growth trajectory and sustainability
            3. Productivity and living standards implications
            4. Key economic concerns or strengths
            """
            
            response = self.llm.invoke([SystemMessage(content="You are an expert economic analyst."), 
                                      HumanMessage(content=gdp_prompt)])
            analysis["ai_insights"] = response.content
            
            state["gdp_analysis"] = analysis
            state["messages"].append("✅ GDP analysis completed")
            
        except Exception as e:
            error_msg = f"Error in GDP analysis: {str(e)}"
            state["error_messages"].append(error_msg)
            state["messages"].append(f"❌ {error_msg}")
        
        return state
    
    def _analyze_inflation(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Analyze inflation indicators"""
        try:
            if "inflation" not in state["raw_data"]:
                state["messages"].append("⚠️ No inflation data available for analysis")
                return state
                
            inflation_data = state["raw_data"]["inflation"]
            
            analysis = {}
            
            # CPI Analysis
            if "cpi" in inflation_data and inflation_data["cpi"]:
                current_cpi = inflation_data["cpi"].get_latest_value()
                cpi_yoy = inflation_data["cpi"].get_yoy_change()
                
                analysis["current_cpi"] = current_cpi
                analysis["cpi_yoy_change"] = cpi_yoy
            
            # Core CPI Analysis
            if "core_cpi" in inflation_data and inflation_data["core_cpi"]:
                current_core_cpi = inflation_data["core_cpi"].get_latest_value()
                core_cpi_yoy = inflation_data["core_cpi"].get_yoy_change()
                
                analysis["current_core_cpi"] = current_core_cpi
                analysis["core_cpi_yoy_change"] = core_cpi_yoy
            
            # Inflation Rate Analysis
            if "inflation_rate" in inflation_data and inflation_data["inflation_rate"]:
                current_inflation = inflation_data["inflation_rate"].get_latest_value()
                avg_inflation = inflation_data["inflation_rate"].data.mean()
                
                analysis["current_inflation_rate"] = current_inflation
                analysis["average_inflation_rate"] = avg_inflation
                
                # Fed target is typically 2%
                analysis["vs_fed_target"] = "above" if current_inflation > 2.0 else "below"
            
            # PCE Analysis
            if "pce" in inflation_data and inflation_data["pce"]:
                current_pce = inflation_data["pce"].get_latest_value()
                pce_yoy = inflation_data["pce"].get_yoy_change()
                
                analysis["current_pce"] = current_pce
                analysis["pce_yoy_change"] = pce_yoy
            
            # AI-powered inflation analysis
            inflation_prompt = f"""
            Analyze the following inflation data and provide economic insights:
            
            Current CPI: {analysis.get('current_cpi', 'N/A')}
            CPI YoY Change: {analysis.get('cpi_yoy_change', 'N/A')}%
            Current Core CPI: {analysis.get('current_core_cpi', 'N/A')}
            Core CPI YoY Change: {analysis.get('core_cpi_yoy_change', 'N/A')}%
            Current Inflation Rate: {analysis.get('current_inflation_rate', 'N/A')}%
            Average Inflation Rate: {analysis.get('average_inflation_rate', 'N/A')}%
            vs Fed Target (2%): {analysis.get('vs_fed_target', 'N/A')}
            Current PCE: {analysis.get('current_pce', 'N/A')}
            PCE YoY Change: {analysis.get('pce_yoy_change', 'N/A')}%
            
            Provide insights on:
            1. Current inflationary pressures
            2. Core vs headline inflation dynamics
            3. Implications for monetary policy
            4. Consumer purchasing power impact
            5. Price stability outlook
            """
            
            response = self.llm.invoke([SystemMessage(content="You are an expert economic analyst specializing in inflation."), 
                                      HumanMessage(content=inflation_prompt)])
            analysis["ai_insights"] = response.content
            
            state["inflation_analysis"] = analysis
            state["messages"].append("✅ Inflation analysis completed")
            
        except Exception as e:
            error_msg = f"Error in inflation analysis: {str(e)}"
            state["error_messages"].append(error_msg)
            state["messages"].append(f"❌ {error_msg}")
        
        return state
    
    def _analyze_market_trends(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Analyze market trend indicators"""
        try:
            if "market" not in state["raw_data"]:
                state["messages"].append("⚠️ No market data available for analysis")
                return state
                
            market_data = state["raw_data"]["market"]
            
            analysis = {}
            
            # Unemployment analysis
            if "unemployment" in market_data and market_data["unemployment"]:
                current_unemployment = market_data["unemployment"].get_latest_value()
                unemployment_trend = market_data["unemployment"].data.pct_change(periods=12).iloc[-1]
                
                analysis["current_unemployment"] = current_unemployment
                analysis["unemployment_trend"] = unemployment_trend
            
            # Interest rates analysis
            if "fed_funds" in market_data and market_data["fed_funds"]:
                current_fed_rate = market_data["fed_funds"].get_latest_value()
                fed_rate_change = market_data["fed_funds"].data.pct_change(periods=12).iloc[-1]
                
                analysis["current_fed_rate"] = current_fed_rate
                analysis["fed_rate_change_yoy"] = fed_rate_change
            
            if "10y_treasury" in market_data and market_data["10y_treasury"]:
                current_10y = market_data["10y_treasury"].get_latest_value()
                treasury_change = market_data["10y_treasury"].data.pct_change(periods=12).iloc[-1]
                
                analysis["current_10y_treasury"] = current_10y
                analysis["treasury_change_yoy"] = treasury_change
                
                # Yield curve analysis (if we have both rates)
                if "current_fed_rate" in analysis:
                    yield_spread = current_10y - analysis["current_fed_rate"]
                    analysis["yield_spread"] = yield_spread
                    analysis["yield_curve"] = "inverted" if yield_spread < 0 else "normal"
            
            # Consumer confidence
            if "consumer_confidence" in market_data and market_data["consumer_confidence"]:
                current_confidence = market_data["consumer_confidence"].get_latest_value()
                confidence_change = market_data["consumer_confidence"].get_yoy_change()
                
                analysis["current_consumer_confidence"] = current_confidence
                analysis["confidence_change_yoy"] = confidence_change
            
            # Industrial production
            if "industrial_production" in market_data and market_data["industrial_production"]:
                current_production = market_data["industrial_production"].get_latest_value()
                production_change = market_data["industrial_production"].get_yoy_change()
                
                analysis["current_industrial_production"] = current_production
                analysis["production_change_yoy"] = production_change
            
            # AI-powered market trends analysis
            market_prompt = f"""
            Analyze the following market trend data and provide economic insights:
            
            Current Unemployment Rate: {analysis.get('current_unemployment', 'N/A')}%
            Unemployment Trend (YoY): {analysis.get('unemployment_trend', 'N/A')}%
            Current Fed Funds Rate: {analysis.get('current_fed_rate', 'N/A')}%
            Fed Rate Change (YoY): {analysis.get('fed_rate_change_yoy', 'N/A')}%
            Current 10Y Treasury: {analysis.get('current_10y_treasury', 'N/A')}%
            Treasury Change (YoY): {analysis.get('treasury_change_yoy', 'N/A')}%
            Yield Spread: {analysis.get('yield_spread', 'N/A')}%
            Yield Curve: {analysis.get('yield_curve', 'N/A')}
            Consumer Confidence: {analysis.get('current_consumer_confidence', 'N/A')}
            Confidence Change (YoY): {analysis.get('confidence_change_yoy', 'N/A')}%
            Industrial Production Index: {analysis.get('current_industrial_production', 'N/A')}
            Production Change (YoY): {analysis.get('production_change_yoy', 'N/A')}%
            
            Provide insights on:
            1. Labor market health and employment trends
            2. Monetary policy stance and interest rate environment
            3. Credit conditions and financial stability
            4. Economic sentiment and business cycle position
            5. Manufacturing and industrial activity
            """
            
            response = self.llm.invoke([SystemMessage(content="You are an expert economic analyst specializing in market trends."), 
                                      HumanMessage(content=market_prompt)])
            analysis["ai_insights"] = response.content
            
            state["market_analysis"] = analysis
            state["messages"].append("✅ Market trends analysis completed")
            
        except Exception as e:
            error_msg = f"Error in market trends analysis: {str(e)}"
            state["error_messages"].append(error_msg)
            state["messages"].append(f"❌ {error_msg}")
        
        return state
    
    def _analyze_industry_performance(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Analyze industry-specific performance"""
        try:
            if "industry" not in state["raw_data"]:
                state["messages"].append("⚠️ No industry data available for analysis")
                return state
                
            industry_data = state["raw_data"]["industry"]
            focus_industries = state.get("focus_industries", EconomicConfig.FOCUS_INDUSTRIES)
            
            analysis = {}
            
            for industry in focus_industries:
                if industry in industry_data:
                    industry_analysis = {}
                    industry_info = industry_data[industry]
                    
                    # Tech Industry Analysis
                    if industry == "tech":
                        if "tech_employment" in industry_info:
                            current_emp = industry_info["tech_employment"].get_latest_value()
                            emp_change = industry_info["tech_employment"].get_yoy_change()
                            industry_analysis["employment"] = current_emp
                            industry_analysis["employment_change_yoy"] = emp_change
                        
                        if "tech_wages" in industry_info:
                            current_wages = industry_info["tech_wages"].get_latest_value()
                            wage_change = industry_info["tech_wages"].get_yoy_change()
                            industry_analysis["wages"] = current_wages
                            industry_analysis["wage_change_yoy"] = wage_change
                    
                    # Healthcare Industry Analysis
                    elif industry == "healthcare":
                        if "healthcare_employment" in industry_info:
                            current_emp = industry_info["healthcare_employment"].get_latest_value()
                            emp_change = industry_info["healthcare_employment"].get_yoy_change()
                            industry_analysis["employment"] = current_emp
                            industry_analysis["employment_change_yoy"] = emp_change
                        
                        if "healthcare_cpi" in industry_info:
                            current_cpi = industry_info["healthcare_cpi"].get_latest_value()
                            cpi_change = industry_info["healthcare_cpi"].get_yoy_change()
                            industry_analysis["healthcare_cpi"] = current_cpi
                            industry_analysis["healthcare_cpi_change_yoy"] = cpi_change
                    
                    # Energy Industry Analysis
                    elif industry == "energy":
                        if "energy_employment" in industry_info:
                            current_emp = industry_info["energy_employment"].get_latest_value()
                            emp_change = industry_info["energy_employment"].get_yoy_change()
                            industry_analysis["employment"] = current_emp
                            industry_analysis["employment_change_yoy"] = emp_change
                        
                        if "oil_price" in industry_info:
                            current_oil = industry_info["oil_price"].get_latest_value()
                            oil_change = industry_info["oil_price"].get_yoy_change()
                            industry_analysis["oil_price"] = current_oil
                            industry_analysis["oil_price_change_yoy"] = oil_change
                        
                        if "natural_gas" in industry_info:
                            current_gas = industry_info["natural_gas"].get_latest_value()
                            gas_change = industry_info["natural_gas"].get_yoy_change()
                            industry_analysis["natural_gas_price"] = current_gas
                            industry_analysis["natural_gas_change_yoy"] = gas_change
                    
                    # AI-powered industry analysis
                    industry_prompt = f"""
                    Analyze the following {industry.upper()} industry performance data:
                    
                    {json.dumps(industry_analysis, indent=2)}
                    
                    Provide insights on:
                    1. Industry health and growth trajectory
                    2. Employment trends and labor market dynamics
                    3. Key economic drivers and challenges
                    4. Competitive position and outlook
                    5. Policy implications and regulatory environment
                    """
                    
                    response = self.llm.invoke([SystemMessage(content=f"You are an expert economic analyst specializing in {industry} industry analysis."), 
                                              HumanMessage(content=industry_prompt)])
                    industry_analysis["ai_insights"] = response.content
                    
                    analysis[industry] = industry_analysis
            
            state["industry_analysis"] = analysis
            state["messages"].append("✅ Industry performance analysis completed")
            
        except Exception as e:
            error_msg = f"Error in industry analysis: {str(e)}"
            state["error_messages"].append(error_msg)
            state["messages"].append(f"❌ {error_msg}")
        
        return state
    
    def _generate_economic_insights(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Generate comprehensive economic insights"""
        try:
            # Combine all analyses
            gdp_analysis = state.get("gdp_analysis", {})
            inflation_analysis = state.get("inflation_analysis", {})
            market_analysis = state.get("market_analysis", {})
            industry_analysis = state.get("industry_analysis", {})
            
            # Create comprehensive analysis prompt
            comprehensive_prompt = f"""
            Based on the following economic data analysis, provide comprehensive economic insights:
            
            GDP ANALYSIS:
            {json.dumps(gdp_analysis, indent=2, default=str)}
            
            INFLATION ANALYSIS:
            {json.dumps(inflation_analysis, indent=2, default=str)}
            
            MARKET TRENDS ANALYSIS:
            {json.dumps(market_analysis, indent=2, default=str)}
            
            INDUSTRY ANALYSIS:
            {json.dumps(industry_analysis, indent=2, default=str)}
            
            Provide a comprehensive economic assessment including:
            1. Overall economic health assessment
            2. Key economic themes and patterns
            3. Cross-indicator relationships and correlations
            4. Economic cycle position and trajectory
            5. Major risks and opportunities
            6. Sector-specific insights and implications
            7. Economic outlook and key factors to monitor
            
            Format your response as clear, actionable insights.
            """
            
            response = self.llm.invoke([SystemMessage(content="You are a senior economic strategist providing comprehensive economic analysis."), 
                                      HumanMessage(content=comprehensive_prompt)])
            
            # Parse insights into structured format
            insights = response.content.split('\n')
            insights = [insight.strip() for insight in insights if insight.strip()]
            
            state["economic_insights"] = insights
            state["messages"].append("✅ Comprehensive economic insights generated")
            
        except Exception as e:
            error_msg = f"Error generating economic insights: {str(e)}"
            state["error_messages"].append(error_msg)
            state["messages"].append(f"❌ {error_msg}")
        
        return state
    
    def _create_visualizations(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Create economic visualizations"""
        try:
            raw_data = state["raw_data"]
            chart_paths = []
            
            # Create economic dashboard (when both GDP and inflation are available)
            if "gdp" in raw_data and "inflation" in raw_data:
                fig = self.economic_agent.create_economic_dashboard_chart(
                    raw_data["gdp"], raw_data["inflation"]
                )
                
                chart_path = f"{EconomicConfig.CHART_OUTPUT_DIR}/economic_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                fig.write_image(chart_path, width=1200, height=800, scale=2)
                chart_paths.append(chart_path)
            
            # Create GDP-specific chart (when only GDP data is available)
            elif "gdp" in raw_data:
                gdp_fig = self._create_gdp_analysis_chart(raw_data["gdp"])
                if gdp_fig:
                    chart_path = f"{EconomicConfig.CHART_OUTPUT_DIR}/gdp_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    gdp_fig.write_image(chart_path, width=1200, height=800, scale=2)
                    chart_paths.append(chart_path)
            
            # Create inflation-specific chart (when only inflation data is available)
            elif "inflation" in raw_data:
                inflation_fig = self._create_inflation_analysis_chart(raw_data["inflation"])
                if inflation_fig:
                    chart_path = f"{EconomicConfig.CHART_OUTPUT_DIR}/inflation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    inflation_fig.write_image(chart_path, width=1200, height=800, scale=2)
                    chart_paths.append(chart_path)
            
            # Create industry comparison chart
            if "industry" in raw_data:
                industry_fig = self._create_industry_comparison_chart(raw_data["industry"])
                if industry_fig:
                    chart_path = f"{EconomicConfig.CHART_OUTPUT_DIR}/industry_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    industry_fig.write_image(chart_path, width=1200, height=800, scale=2)
                    chart_paths.append(chart_path)
            
            # Create market trends chart
            if "market" in raw_data:
                market_fig = self._create_market_trends_chart(raw_data["market"])
                if market_fig:
                    chart_path = f"{EconomicConfig.CHART_OUTPUT_DIR}/market_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    market_fig.write_image(chart_path, width=1200, height=800, scale=2)
                    chart_paths.append(chart_path)
            
            # Create correlation heatmap
            correlation_fig = self._create_correlation_heatmap(raw_data)
            if correlation_fig:
                chart_path = f"{EconomicConfig.CHART_OUTPUT_DIR}/correlation_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                correlation_fig.write_image(chart_path, width=1200, height=800, scale=2)
                chart_paths.append(chart_path)
            
            state["chart_paths"] = chart_paths
            state["messages"].append(f"✅ Created {len(chart_paths)} visualizations")
            
        except Exception as e:
            error_msg = f"Error creating visualizations: {str(e)}"
            state["error_messages"].append(error_msg)
            state["messages"].append(f"❌ {error_msg}")
        
        return state
    
    def _create_industry_comparison_chart(self, industry_data: Dict[str, Any]) -> go.Figure:
        """Create professional industry performance comparison chart"""
        try:
            # Create subplots for comprehensive industry analysis
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Employment Growth (YoY %)', 'Wage Growth (YoY %)', 
                              'Industry Performance Metrics', 'Sector Comparison'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "bar"}]],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            industries = ["tech", "healthcare", "energy"]
            industry_labels = ["Technology", "Healthcare", "Energy"]
            colors = ['#2E86AB', '#A23B72', '#F18F01']  # Professional color palette
            
            employment_changes = []
            wage_changes = []
            employment_levels = []
            performance_scores = []
            
            for i, industry in enumerate(industries):
                emp_change = 0
                wage_change = 0
                emp_level = 0
                
                if industry in industry_data:
                    industry_info = industry_data[industry]
                    
                    # Get employment data - check for both possible key formats
                    emp_key = f"{industry}_employment"
                    if emp_key in industry_info and industry_info[emp_key]:
                        emp_change = industry_info[emp_key].get_yoy_change() or 0
                        emp_level = industry_info[emp_key].get_latest_value() or 0
                    elif "employment" in industry_info and industry_info["employment"]:
                        emp_change = industry_info["employment"].get_yoy_change() or 0
                        emp_level = industry_info["employment"].get_latest_value() or 0
                    
                    # Get wage data - check for both possible key formats
                    wage_key = f"{industry}_wages"
                    if wage_key in industry_info and industry_info[wage_key]:
                        wage_change = industry_info[wage_key].get_yoy_change() or 0
                    elif "wages" in industry_info and industry_info["wages"]:
                        wage_change = industry_info["wages"].get_yoy_change() or 0
                
                # Append data for all industries
                employment_changes.append(emp_change)
                wage_changes.append(wage_change)
                employment_levels.append(emp_level)
                performance_scores.append(emp_change + wage_change)
            
            # Employment Growth Chart
            fig.add_trace(go.Bar(
                x=industry_labels,
                y=employment_changes,
                name='Employment Growth',
                marker_color=colors,
                marker_line=dict(color='white', width=2),
                text=[f'{val:.1f}%' for val in employment_changes],
                textposition='auto',
                showlegend=False
            ), row=1, col=1)
            
            # Wage Growth Chart
            fig.add_trace(go.Bar(
                x=industry_labels,
                y=wage_changes,
                name='Wage Growth',
                marker_color=[color.replace('AB', '72') for color in colors],  # Slightly different shade
                marker_line=dict(color='white', width=2),
                text=[f'{val:.1f}%' for val in wage_changes],
                textposition='auto',
                showlegend=False
            ), row=1, col=2)
            
            # Performance Scatter Plot
            # Only add data points where we have actual data
            valid_indices = []
            valid_x = []
            valid_y = []
            valid_labels = []
            valid_colors = []
            valid_sizes = []
            
            for i, (emp, wage, label, color, size) in enumerate(zip(employment_changes, wage_changes, industry_labels, colors, employment_levels)):
                if emp != 0 or wage != 0:  # Only include if we have some data
                    valid_x.append(emp)
                    valid_y.append(wage)
                    valid_labels.append(label)
                    valid_colors.append(color)
                    valid_sizes.append(max(size, 10))  # Minimum size for visibility
            
            if valid_x:  # Only create scatter plot if we have data
                fig.add_trace(go.Scatter(
                    x=valid_x,
                    y=valid_y,
                    mode='markers+text',
                    text=valid_labels,
                    textposition='top center',
                    marker=dict(
                        size=valid_sizes,
                        sizemode='diameter',
                        sizeref=max(valid_sizes)/50 if valid_sizes else 1,
                        color=valid_colors,
                        line=dict(width=2, color='white')
                    ),
                    showlegend=False
                ), row=2, col=1)
            else:
                # Add a note when no data is available
                fig.add_annotation(
                    text="No data available for performance metrics",
                    xref="x3", yref="y3",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=14, color='#7F8C8D'),
                    row=2, col=1
                )
            
            # Overall Performance Comparison
            fig.add_trace(go.Bar(
                x=industry_labels,
                y=performance_scores,
                name='Overall Performance',
                marker_color=colors,
                marker_line=dict(color='white', width=2),
                text=[f'{val:.1f}' for val in performance_scores],
                textposition='auto',
                showlegend=False
            ), row=2, col=2)
            
            # Update layout for professional appearance
            fig.update_layout(
                title=dict(
                    text="<b>Industry Performance Analysis Dashboard</b>",
                    x=0.5,
                    font=dict(size=20, color='#2C3E50')
                ),
                height=700,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12, color='#2C3E50')
            )
            
            # Update axes with proper labels
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5', linecolor='#2C3E50')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5', linecolor='#2C3E50')
            
            # Add specific axis labels
            fig.update_xaxes(title_text="Industry", row=1, col=1)
            fig.update_yaxes(title_text="Employment Growth (%)", row=1, col=1)
            fig.update_xaxes(title_text="Industry", row=1, col=2)
            fig.update_yaxes(title_text="Wage Growth (%)", row=1, col=2)
            fig.update_xaxes(title_text="Employment Growth (%)", row=2, col=1)
            fig.update_yaxes(title_text="Wage Growth (%)", row=2, col=1)
            fig.update_xaxes(title_text="Industry", row=2, col=2)
            fig.update_yaxes(title_text="Performance Score", row=2, col=2)
            
            # Add annotations
            fig.add_annotation(
                text="Data Source: Federal Reserve Economic Data (FRED)",
                xref="paper", yref="paper",
                x=0.5, y=-0.1,
                showarrow=False,
                font=dict(size=10, color='#7F8C8D')
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating industry comparison chart: {str(e)}")
            return None
    
    def _create_gdp_analysis_chart(self, gdp_data: Dict[str, Any]) -> go.Figure:
        """Create professional GDP analysis chart"""
        try:
            # Create subplots for comprehensive GDP analysis
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'GDP Level (Billions USD)',
                    'GDP Growth Rate (%)', 
                    'GDP Per Capita (USD)',
                    'GDP Components Analysis'
                ),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # Color scheme for professional look
            colors = {
                'gdp': '#2ECC71',
                'gdp_growth': '#E74C3C', 
                'gdp_per_capita': '#3498DB'
            }
            
            # 1. GDP Level (Top Left)
            if "gdp" in gdp_data and gdp_data["gdp"]:
                gdp_level_data = gdp_data["gdp"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in gdp_level_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=gdp_level_data.data.values,
                        mode='lines+markers',
                        name='GDP Level',
                        line=dict(color=colors['gdp'], width=3),
                        marker=dict(size=6),
                        hovertemplate='<b>GDP Level</b><br>Date: %{x}<br>Value: $%{y:,.0f}B<extra></extra>'
                    ),
                    row=1, col=1
                )
            
            # 2. GDP Growth Rate (Top Right)
            if "gdp_growth" in gdp_data and gdp_data["gdp_growth"]:
                growth_data = gdp_data["gdp_growth"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in growth_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=growth_data.data.values,
                        mode='lines+markers',
                        name='GDP Growth Rate',
                        line=dict(color=colors['gdp_growth'], width=3),
                        marker=dict(size=6),
                        fill='tonexty',
                        fillcolor='rgba(231, 76, 60, 0.1)',
                        hovertemplate='<b>GDP Growth Rate</b><br>Date: %{x}<br>Growth: %{y:.2f}%<extra></extra>'
                    ),
                    row=1, col=2
                )
            
            # 3. GDP Per Capita (Bottom Left)
            if "gdp_per_capita" in gdp_data and gdp_data["gdp_per_capita"]:
                per_capita_data = gdp_data["gdp_per_capita"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in per_capita_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=per_capita_data.data.values,
                        mode='lines+markers',
                        name='GDP Per Capita',
                        line=dict(color=colors['gdp_per_capita'], width=3),
                        marker=dict(size=6),
                        hovertemplate='<b>GDP Per Capita</b><br>Date: %{x}<br>Value: $%{y:,.0f}<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            # 4. GDP Components Analysis (Bottom Right) - Placeholder for future enhancement
            fig.add_annotation(
                text="GDP Components Analysis<br>(Future Enhancement)",
                xref="x4", yref="y4",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color='#7F8C8D'),
                row=2, col=2
            )
            
            # Update layout for professional appearance
            fig.update_layout(
                title=dict(
                    text='<b>GDP Analysis Dashboard</b>',
                    x=0.5,
                    font=dict(size=20, color='#2C3E50')
                ),
                height=800,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12, color='#2C3E50')
            )
            
            # Update axes with proper labels
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5', linecolor='#2C3E50')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5', linecolor='#2C3E50')
            
            # Add specific axis labels
            fig.update_xaxes(title_text="Year", row=1, col=1)
            fig.update_yaxes(title_text="GDP (Billions USD)", row=1, col=1)
            fig.update_xaxes(title_text="Year", row=1, col=2)
            fig.update_yaxes(title_text="Growth Rate (%)", row=1, col=2)
            fig.update_xaxes(title_text="Year", row=2, col=1)
            fig.update_yaxes(title_text="GDP Per Capita (USD)", row=2, col=1)
            fig.update_xaxes(title_text="Components", row=2, col=2)
            fig.update_yaxes(title_text="Value", row=2, col=2)
            
            return fig
            
        except Exception as e:
            print(f"Error creating GDP analysis chart: {str(e)}")
            return None
    
    def _create_inflation_analysis_chart(self, inflation_data: Dict[str, Any]) -> go.Figure:
        """Create professional inflation analysis chart"""
        try:
            # Create subplots for comprehensive inflation analysis
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Consumer Price Index (CPI)',
                    'Core CPI vs Headline CPI', 
                    'Personal Consumption Expenditures (PCE)',
                    'Inflation Rate Trends'
                ),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # Color scheme for professional look
            colors = {
                'cpi': '#E74C3C',
                'core_cpi': '#8E44AD', 
                'pce': '#3498DB',
                'inflation_rate': '#F39C12'
            }
            
            # 1. Consumer Price Index (Top Left)
            if "cpi" in inflation_data and inflation_data["cpi"]:
                cpi_data = inflation_data["cpi"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in cpi_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=cpi_data.data.values,
                        mode='lines+markers',
                        name='CPI',
                        line=dict(color=colors['cpi'], width=3),
                        marker=dict(size=6),
                        hovertemplate='<b>Consumer Price Index</b><br>Date: %{x}<br>Index: %{y:.1f}<extra></extra>'
                    ),
                    row=1, col=1
                )
            
            # 2. Core CPI vs Headline CPI (Top Right)
            if "cpi" in inflation_data and inflation_data["cpi"]:
                cpi_data = inflation_data["cpi"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in cpi_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=cpi_data.data.values,
                        mode='lines+markers',
                        name='Headline CPI',
                        line=dict(color=colors['cpi'], width=3),
                        marker=dict(size=6),
                        hovertemplate='<b>Headline CPI</b><br>Date: %{x}<br>Index: %{y:.1f}<extra></extra>'
                    ),
                    row=1, col=2
                )
            
            if "core_cpi" in inflation_data and inflation_data["core_cpi"]:
                core_cpi_data = inflation_data["core_cpi"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in core_cpi_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=core_cpi_data.data.values,
                        mode='lines+markers',
                        name='Core CPI',
                        line=dict(color=colors['core_cpi'], width=3),
                        marker=dict(size=6),
                        hovertemplate='<b>Core CPI</b><br>Date: %{x}<br>Index: %{y:.1f}<extra></extra>'
                    ),
                    row=1, col=2
                )
            
            # 3. Personal Consumption Expenditures (Bottom Left)
            if "pce" in inflation_data and inflation_data["pce"]:
                pce_data = inflation_data["pce"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in pce_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=pce_data.data.values,
                        mode='lines+markers',
                        name='PCE',
                        line=dict(color=colors['pce'], width=3),
                        marker=dict(size=6),
                        hovertemplate='<b>Personal Consumption Expenditures</b><br>Date: %{x}<br>Index: %{y:.1f}<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            # 4. Inflation Rate Trends (Bottom Right)
            if "inflation_rate" in inflation_data and inflation_data["inflation_rate"]:
                inflation_rate_data = inflation_data["inflation_rate"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in inflation_rate_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=inflation_rate_data.data.values,
                        mode='lines+markers',
                        name='Inflation Rate',
                        line=dict(color=colors['inflation_rate'], width=3),
                        marker=dict(size=6),
                        fill='tonexty',
                        fillcolor='rgba(243, 156, 18, 0.1)',
                        hovertemplate='<b>Inflation Rate</b><br>Date: %{x}<br>Rate: %{y:.2f}%<extra></extra>'
                    ),
                    row=2, col=2
                )
            
            # Update layout for professional appearance
            fig.update_layout(
                title=dict(
                    text='<b>Inflation Analysis Dashboard</b>',
                    x=0.5,
                    font=dict(size=20, color='#2C3E50')
                ),
                height=800,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12, color='#2C3E50')
            )
            
            # Update axes with proper labels
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5', linecolor='#2C3E50')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5', linecolor='#2C3E50')
            
            # Add specific axis labels
            fig.update_xaxes(title_text="Year", row=1, col=1)
            fig.update_yaxes(title_text="CPI Index", row=1, col=1)
            fig.update_xaxes(title_text="Year", row=1, col=2)
            fig.update_yaxes(title_text="CPI Index", row=1, col=2)
            fig.update_xaxes(title_text="Year", row=2, col=1)
            fig.update_yaxes(title_text="PCE Index", row=2, col=1)
            fig.update_xaxes(title_text="Year", row=2, col=2)
            fig.update_yaxes(title_text="Inflation Rate (%)", row=2, col=2)
            
            return fig
            
        except Exception as e:
            print(f"Error creating inflation analysis chart: {str(e)}")
            return None
    
    def _create_market_trends_chart(self, market_data: Dict[str, Any]) -> go.Figure:
        """Create professional market trends analysis chart"""
        try:
            # Create subplots for comprehensive market analysis
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Interest Rates & Yield Curve',
                    'Unemployment Trends', 
                    'Consumer Confidence',
                    'Industrial Production'
                ),
                specs=[[{"secondary_y": True}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # Color scheme for professional look
            colors = {
                'fed_funds': '#E74C3C',
                'treasury_10y': '#3498DB', 
                'unemployment': '#F39C12',
                'consumer_confidence': '#2ECC71',
                'industrial_production': '#9B59B6'
            }
            
            # 1. Interest Rates & Yield Curve (Top Left)
            if "fed_funds" in market_data and market_data["fed_funds"]:
                fed_data = market_data["fed_funds"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in fed_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=fed_data.data.values,
                        mode='lines+markers',
                        name='Fed Funds Rate',
                        line=dict(color=colors['fed_funds'], width=3),
                        marker=dict(size=6),
                        hovertemplate='<b>Fed Funds Rate</b><br>Date: %{x}<br>Rate: %{y:.2f}%<extra></extra>'
                    ),
                    row=1, col=1, secondary_y=False
                )
            
            if "10y_treasury" in market_data and market_data["10y_treasury"]:
                treasury_data = market_data["10y_treasury"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in treasury_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=treasury_data.data.values,
                        mode='lines+markers',
                        name='10Y Treasury',
                        line=dict(color=colors['treasury_10y'], width=3),
                        marker=dict(size=6),
                        hovertemplate='<b>10Y Treasury</b><br>Date: %{x}<br>Rate: %{y:.2f}%<extra></extra>'
                    ),
                    row=1, col=1, secondary_y=True
                )
            
            # 2. Unemployment Trends (Top Right)
            if "unemployment" in market_data and market_data["unemployment"]:
                unemp_data = market_data["unemployment"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in unemp_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=unemp_data.data.values,
                        mode='lines+markers',
                        name='Unemployment Rate',
                        line=dict(color=colors['unemployment'], width=3),
                        marker=dict(size=6),
                        fill='tonexty',
                        fillcolor='rgba(243, 156, 18, 0.1)',
                        hovertemplate='<b>Unemployment Rate</b><br>Date: %{x}<br>Rate: %{y:.2f}%<extra></extra>'
                    ),
                    row=1, col=2
                )
            
            # 3. Consumer Confidence (Bottom Left)
            if "consumer_confidence" in market_data and market_data["consumer_confidence"]:
                conf_data = market_data["consumer_confidence"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in conf_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=conf_data.data.values,
                        mode='lines+markers',
                        name='Consumer Confidence',
                        line=dict(color=colors['consumer_confidence'], width=3),
                        marker=dict(size=6),
                        hovertemplate='<b>Consumer Confidence</b><br>Date: %{x}<br>Index: %{y:.1f}<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            # 4. Industrial Production (Bottom Right)
            if "industrial_production" in market_data and market_data["industrial_production"]:
                prod_data = market_data["industrial_production"]
                # Convert datetime index to readable date strings
                date_strings = [date.strftime('%Y-%m') for date in prod_data.data.index]
                fig.add_trace(
                    go.Scatter(
                        x=date_strings,
                        y=prod_data.data.values,
                        mode='lines+markers',
                        name='Industrial Production',
                        line=dict(color=colors['industrial_production'], width=3),
                        marker=dict(size=6),
                        hovertemplate='<b>Industrial Production</b><br>Date: %{x}<br>Index: %{y:.1f}<extra></extra>'
                    ),
                    row=2, col=2
                )
            
            # Update layout for professional appearance
            fig.update_layout(
                title=dict(
                    text='<b>Market Trends Analysis Dashboard</b>',
                    x=0.5,
                    font=dict(size=20, color='#2C3E50')
                ),
                height=800,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12, color='#2C3E50')
            )
            
            # Update axes with proper labels
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5', linecolor='#2C3E50')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5', linecolor='#2C3E50')
            
            # Add specific axis labels
            fig.update_xaxes(title_text="Year", row=1, col=1)
            fig.update_yaxes(title_text="Fed Funds Rate (%)", row=1, col=1, secondary_y=False)
            fig.update_yaxes(title_text="10Y Treasury Rate (%)", row=1, col=1, secondary_y=True)
            fig.update_xaxes(title_text="Year", row=1, col=2)
            fig.update_yaxes(title_text="Unemployment Rate (%)", row=1, col=2)
            fig.update_xaxes(title_text="Year", row=2, col=1)
            fig.update_yaxes(title_text="Consumer Confidence Index", row=2, col=1)
            fig.update_xaxes(title_text="Year", row=2, col=2)
            fig.update_yaxes(title_text="Industrial Production Index", row=2, col=2)
            
            return fig
            
        except Exception as e:
            print(f"Error creating market trends chart: {str(e)}")
            return None
    
    def _create_correlation_heatmap(self, raw_data: Dict[str, Any]) -> go.Figure:
        """Create professional correlation heatmap of economic indicators"""
        try:
            # Combine key economic indicators
            combined_data = {}
            
            # GDP indicators
            if "gdp" in raw_data:
                for key, econ_data in raw_data["gdp"].items():
                    if econ_data and econ_data.data is not None:
                        combined_data[f"GDP_{key}"] = econ_data.data
            
            # Inflation indicators
            if "inflation" in raw_data:
                for key, econ_data in raw_data["inflation"].items():
                    if econ_data and econ_data.data is not None:
                        combined_data[f"Inflation_{key}"] = econ_data.data
            
            # Market indicators
            if "market" in raw_data:
                for key, econ_data in raw_data["market"].items():
                    if econ_data and econ_data.data is not None:
                        combined_data[f"Market_{key}"] = econ_data.data
            
            if len(combined_data) > 1:
                df = pd.DataFrame(combined_data)
                correlation_matrix = df.corr()
                
                # Clean up column names for better display
                clean_names = {}
                for col in correlation_matrix.columns:
                    if 'GDP_' in col:
                        clean_names[col] = col.replace('GDP_', 'GDP ').replace('_', ' ').title()
                    elif 'Inflation_' in col:
                        clean_names[col] = col.replace('Inflation_', 'Inflation ').replace('_', ' ').title()
                    elif 'Market_' in col:
                        clean_names[col] = col.replace('Market_', 'Market ').replace('_', ' ').title()
                    else:
                        clean_names[col] = col.replace('_', ' ').title()
                
                correlation_matrix = correlation_matrix.rename(columns=clean_names, index=clean_names)
                
                fig = go.Figure(data=go.Heatmap(
                    z=correlation_matrix.values,
                    x=correlation_matrix.columns,
                    y=correlation_matrix.columns,
                    colorscale='RdBu',
                    zmid=0
                ))
                
                fig.update_layout(
                    title=dict(
                        text="<b>Economic Indicators Correlation Matrix</b>",
                        x=0.5,
                        font=dict(size=18, color='#2C3E50')
                    ),
                    height=700,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial, sans-serif", size=11, color='#2C3E50'),
                    xaxis=dict(tickangle=45),
                    yaxis=dict(tickangle=0)
                )
                
                # Add text annotations for correlation values
                fig.update_traces(
                    text=correlation_matrix.round(2).values,
                    texttemplate="%{text}",
                    textfont={"size": 10},
                    hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>"
                )
                
                return fig
            
        except Exception as e:
            print(f"Error creating correlation heatmap: {str(e)}")
            return None
    
    def _analyze_policy_implications(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Analyze policy implications"""
        try:
            economic_insights = state.get("economic_insights", [])
            gdp_analysis = state.get("gdp_analysis", {})
            inflation_analysis = state.get("inflation_analysis", {})
            market_analysis = state.get("market_analysis", {})
            
            policy_prompt = f"""
            Based on the current economic conditions, analyze policy implications:
            
            CURRENT ECONOMIC STATE:
            - GDP Growth: {gdp_analysis.get('current_growth_rate', 'N/A')}%
            - Inflation Rate: {inflation_analysis.get('current_inflation_rate', 'N/A')}%
            - Unemployment: {market_analysis.get('current_unemployment', 'N/A')}%
            - Fed Funds Rate: {market_analysis.get('current_fed_rate', 'N/A')}%
            - Yield Curve: {market_analysis.get('yield_curve', 'N/A')}
            
            ECONOMIC INSIGHTS:
            {chr(10).join(economic_insights[:10])}
            
            Provide policy analysis covering:
            1. Monetary Policy Implications
            2. Fiscal Policy Considerations
            3. Regulatory Policy Recommendations
            4. Industry-Specific Policy Needs
            5. International Trade and Policy Coordination
            6. Risk Management and Contingency Planning
            
            Focus on actionable policy recommendations.
            """
            
            response = self.llm.invoke([SystemMessage(content="You are an expert policy economist advising on macroeconomic policy."), 
                                      HumanMessage(content=policy_prompt)])
            
            # Parse policy implications
            policy_implications = response.content.split('\n')
            policy_implications = [policy.strip() for policy in policy_implications if policy.strip()]
            
            state["policy_implications"] = policy_implications
            state["messages"].append("✅ Policy implications analysis completed")
            
        except Exception as e:
            error_msg = f"Error analyzing policy implications: {str(e)}"
            state["error_messages"].append(error_msg)
            state["messages"].append(f"❌ {error_msg}")
        
        return state
    
    def _generate_forecasts(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Generate economic forecasts"""
        try:
            # Get all analysis data
            gdp_analysis = state.get("gdp_analysis", {})
            inflation_analysis = state.get("inflation_analysis", {})
            market_analysis = state.get("market_analysis", {})
            industry_analysis = state.get("industry_analysis", {})
            economic_insights = state.get("economic_insights", [])
            
            forecast_prompt = f"""
            Based on comprehensive economic analysis, provide forward-looking forecasts:
            
            CURRENT ECONOMIC METRICS:
            - GDP Growth: {gdp_analysis.get('current_growth_rate', 'N/A')}%
            - Inflation: {inflation_analysis.get('current_inflation_rate', 'N/A')}%
            - Unemployment: {market_analysis.get('current_unemployment', 'N/A')}%
            - Fed Funds Rate: {market_analysis.get('current_fed_rate', 'N/A')}%
            - Consumer Confidence: {market_analysis.get('current_consumer_confidence', 'N/A')}
            
            ECONOMIC TRENDS:
            {chr(10).join(economic_insights[:8])}
            
            INDUSTRY PERFORMANCE:
            {json.dumps(industry_analysis, indent=2, default=str)[:1000]}...
            
            Provide 6-month and 12-month forecasts for:
            1. GDP Growth Rate
            2. Inflation Rate
            3. Unemployment Rate
            4. Interest Rates (Fed Funds & 10Y Treasury)
            5. Industry Performance (Tech, Healthcare, Energy)
            6. Key Economic Risks and Opportunities
            
            Include confidence levels and key assumptions for each forecast.
            """
            
            response = self.llm.invoke([SystemMessage(content="You are an expert economic forecaster with deep knowledge of economic cycles and trends."), 
                                      HumanMessage(content=forecast_prompt)])
            
            # Structure forecast data
            forecasts = {
                "6_month": {},
                "12_month": {},
                "key_assumptions": [],
                "risk_factors": [],
                "confidence_levels": {},
                "ai_forecast_analysis": response.content
            }
            
            state["forecasts"] = forecasts
            state["messages"].append("✅ Economic forecasts generated")
            
        except Exception as e:
            error_msg = f"Error generating forecasts: {str(e)}"
            state["error_messages"].append(error_msg)
            state["messages"].append(f"❌ {error_msg}")
        
        return state
    
    def _generate_final_report(self, state: EconomicAnalysisState) -> EconomicAnalysisState:
        """Generate comprehensive final report"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            report_filename = f"{EconomicConfig.REPORT_OUTPUT_DIR}/economic_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Compile comprehensive report
            report_content = f"""# Economic Analysis Report
Generated on: {timestamp}

## Executive Summary

### Key Economic Indicators
{self._format_analysis_summary(state)}

### Economic Insights
{chr(10).join([f"- {insight}" for insight in state.get('economic_insights', [])[:10]])}

## Detailed Analysis

### GDP Analysis
{state.get('gdp_analysis', {}).get('ai_insights', 'No GDP analysis available')}

### Inflation Analysis
{state.get('inflation_analysis', {}).get('ai_insights', 'No inflation analysis available')}

### Market Trends Analysis
{state.get('market_analysis', {}).get('ai_insights', 'No market analysis available')}

### Industry Performance Analysis
{self._format_industry_analysis(state.get('industry_analysis', {}))}

## Policy Implications
{chr(10).join([f"- {policy}" for policy in state.get('policy_implications', [])[:10]])}

## Economic Forecasts
{state.get('forecasts', {}).get('ai_forecast_analysis', 'No forecasts available')}

## Charts and Visualizations
Generated charts:
{chr(10).join([f"- {chart}" for chart in state.get('chart_paths', [])])}

## Data Sources
- Federal Reserve Economic Data (FRED)
- Analysis Period: {state.get('period', 'N/A')}
- Focus Industries: {', '.join(state.get('focus_industries', []))}

---
*Report generated by LangGraph Economic Analysis System*
"""
            
            # Save report
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            state["messages"].append(f"✅ Final report generated: {report_filename}")
            
        except Exception as e:
            error_msg = f"Error generating final report: {str(e)}"
            state["error_messages"].append(error_msg)
            state["messages"].append(f"❌ {error_msg}")
        
        return state
    
    def _format_analysis_summary(self, state: EconomicAnalysisState) -> str:
        """Format key metrics summary"""
        gdp = state.get('gdp_analysis', {})
        inflation = state.get('inflation_analysis', {})
        market = state.get('market_analysis', {})
        
        return f"""
- **GDP Growth Rate**: {gdp.get('current_growth_rate', 'N/A')}%
- **Inflation Rate**: {inflation.get('current_inflation_rate', 'N/A')}%
- **Unemployment Rate**: {market.get('current_unemployment', 'N/A')}%
- **Fed Funds Rate**: {market.get('current_fed_rate', 'N/A')}%
- **10-Year Treasury**: {market.get('current_10y_treasury', 'N/A')}%
- **Consumer Confidence**: {market.get('current_consumer_confidence', 'N/A')}
"""
    
    def _format_industry_analysis(self, industry_analysis: Dict[str, Any]) -> str:
        """Format industry analysis section"""
        formatted = ""
        for industry, analysis in industry_analysis.items():
            formatted += f"\n#### {industry.upper()} Industry\n"
            formatted += analysis.get('ai_insights', 'No analysis available')
            formatted += "\n"
        return formatted
    
    def run_analysis(self, analysis_type: str = "comprehensive", 
                    period: str = "10y",
                    focus_industries: List[str] = None) -> Dict[str, Any]:
        """Run the complete economic analysis workflow"""
        if focus_industries is None:
            focus_industries = EconomicConfig.FOCUS_INDUSTRIES
        
        initial_state = {
            "analysis_type": analysis_type,
            "period": period,
            "focus_industries": focus_industries,
            "raw_data": {},
            "gdp_analysis": {},
            "inflation_analysis": {},
            "market_analysis": {},
            "industry_analysis": {},
            "economic_insights": [],
            "policy_implications": [],
            "forecasts": {},
            "messages": [],
            "chart_paths": [],
            "error_messages": []
        }
        
        # Run the workflow
        final_state = self.graph.invoke(initial_state)
        
        # Ensure analysis_type is preserved in the result
        final_state["analysis_type"] = analysis_type
        final_state["period"] = period
        final_state["focus_industries"] = focus_industries
        
        return final_state