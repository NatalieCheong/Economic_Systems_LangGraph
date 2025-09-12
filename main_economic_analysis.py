import os
import sys
from datetime import datetime
from langgraph_economic_agent import LangGraphEconomicAgent
from economic_config import EconomicConfig
from economic_report_writer import EconomicReportWriter

def main():
    """Main execution function"""
    print("🏛️  LangGraph Economic Analysis System")
    print("=" * 50)
    
    try:
        # Validate configuration
        EconomicConfig.validate()
        print("✅ Configuration validated")
        
        # Initialize the economic agent
        print("🚀 Initializing LangGraph Economic Agent...")
        agent = LangGraphEconomicAgent()
        print("✅ Agent initialized successfully")
        
        # Configuration options
        analysis_options = {
            "1": ("comprehensive", "10y", ["tech", "healthcare", "energy"]),
            "2": ("gdp", "5y", []),
            "3": ("inflation", "5y", []),
            "4": ("market_trends", "3y", []),
            "5": ("industry", "5y", ["tech", "healthcare", "energy"])
        }
        
        print("\n📊 Select Analysis Type:")
        print("1. Comprehensive Economic Analysis (10 years, all indicators)")
        print("2. GDP Analysis (5 years)")
        print("3. Inflation Analysis (5 years)")
        print("4. Market Trends Analysis (3 years)")
        print("5. Industry Performance Analysis (5 years)")
        
        choice = input("\nEnter your choice (1-5) or press Enter for comprehensive: ").strip()
        if not choice:
            choice = "1"
        
        if choice not in analysis_options:
            print("❌ Invalid choice. Running comprehensive analysis...")
            choice = "1"
        
        analysis_type, period, focus_industries = analysis_options[choice]
        
        print(f"\n🔍 Running {analysis_type} analysis for {period}...")
        print(f"📈 Focus industries: {', '.join(focus_industries) if focus_industries else 'None'}")
        print("⏳ This may take a few minutes...\n")
        
        # Run the analysis
        start_time = datetime.now()
        
        result = agent.run_analysis(
            analysis_type=analysis_type,
            period=period,
            focus_industries=focus_industries
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).seconds
        
        # Display results
        print("\n" + "=" * 50)
        print("📋 ANALYSIS COMPLETE")
        print("=" * 50)
        
        print(f"⏱️  Analysis Duration: {duration} seconds")
        print(f"📊 Analysis Type: {analysis_type.upper()}")
        print(f"📅 Period: {period}")
        
        # Show messages
        print("\n📝 Process Messages:")
        for message in result.get("messages", []):
            print(f"  {message}")
        
        # Show error messages if any
        if result.get("error_messages"):
            print("\n⚠️  Warnings/Errors:")
            for error in result.get("error_messages", []):
                print(f"  ❌ {error}")
        
        # Show key insights
        if result.get("economic_insights"):
            print("\n💡 Key Economic Insights:")
            for i, insight in enumerate(result.get("economic_insights", [])[:5], 1):
                print(f"  {i}. {insight}")
        
        # Show chart paths
        if result.get("chart_paths"):
            print("\n📈 Generated Visualizations:")
            for chart in result.get("chart_paths", []):
                print(f"  📊 {chart}")
        
        # Show policy implications
        if result.get("policy_implications"):
            print("\n🏛️  Policy Implications:")
            for i, policy in enumerate(result.get("policy_implications", [])[:3], 1):
                print(f"  {i}. {policy}")
        
        print("\n" + "=" * 50)
        print("✅ Economic analysis completed successfully!")
        print("📁 Check the 'economic_reports' and 'economic_charts' directories for detailed outputs.")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file has OPENAI_API_KEY and FRED_API_KEY")
        print("2. Verify internet connection for FRED API access")
        print("3. Ensure all required packages are installed")
        sys.exit(1)

def run_custom_analysis():
    """Run custom analysis with user-defined parameters"""
    print("🛠️  Custom Economic Analysis")
    print("=" * 30)
    
    try:
        # Initialize agents
        agent = LangGraphEconomicAgent()
        report_writer = EconomicReportWriter()
        
        # Get custom parameters
        period = input("Enter analysis period (e.g., '5y', '10y'): ").strip() or "10y"
        
        print("\nAvailable industries: tech, healthcare, energy")
        industries_input = input("Enter industries (comma-separated) or press Enter for all: ").strip()
        
        if industries_input:
            focus_industries = [ind.strip().lower() for ind in industries_input.split(",")]
            focus_industries = [ind for ind in focus_industries if ind in ["tech", "healthcare", "energy"]]
        else:
            focus_industries = ["tech", "healthcare", "energy"]
        
        # Report type selection
        print("\nReport types: comprehensive, executive, policy_brief, sector_focus")
        report_type = input("Enter report type or press Enter for comprehensive: ").strip() or "comprehensive"
        
        print(f"\n🔍 Running custom analysis...")
        print(f"📅 Period: {period}")
        print(f"📈 Industries: {', '.join(focus_industries)}")
        print(f"📝 Report Type: {report_type}")
        
        # Phase 1: Analysis
        print("\n📊 Running economic analysis...")
        result = agent.run_analysis(
            analysis_type="comprehensive",
            period=period,
            focus_industries=focus_industries
        )
        
        # Phase 2: Report Generation
        print("📝 Generating report...")
        report_data = report_writer.generate_comprehensive_report(
            result,
            report_type=report_type,
            custom_focus=focus_industries if report_type == "sector_focus" else None
        )
        
        # Generate dashboard
        print("📊 Creating executive dashboard...")
        dashboard_path = report_writer.create_executive_dashboard(result)
        
        print("\n✅ Custom analysis completed!")
        print(f"📊 Generated {len(result.get('chart_paths', []))} visualizations")
        print(f"💡 {len(result.get('economic_insights', []))} insights generated")
        print(f"📝 Report type: {report_type}")
        print(f"📈 Dashboard: {dashboard_path}")
        
    except Exception as e:
        print(f"❌ Error in custom analysis: {str(e)}")

def run_with_real_data():
    """Run analysis with real data and generate reports"""
    print("🏛️  LangGraph Economic Analysis System - REAL DATA MODE")
    print("=" * 60)
    
    try:
        # Validate configuration
        EconomicConfig.validate()
        print("✅ Configuration validated")
        
        # Initialize the economic agent
        print("🚀 Initializing LangGraph Economic Agent...")
        agent = LangGraphEconomicAgent()
        print("✅ Agent initialized successfully")
        
        # Initialize report writer
        print("📝 Initializing Economic Report Writer...")
        report_writer = EconomicReportWriter()
        print("✅ Report Writer initialized successfully")
        
        # Run comprehensive analysis with real data
        print("\n🔍 Running comprehensive economic analysis with REAL DATA...")
        print("📅 Analysis Period: 5 years")
        print("📈 Focus industries: tech, healthcare, energy")
        print("⏳ This may take a few minutes...\n")
        
        start_time = datetime.now()
        
        # Phase 1: Run the analysis with real data
        result = agent.run_analysis(
            analysis_type="comprehensive",
            period="5y",
            focus_industries=["tech", "healthcare", "energy"]
        )
        
        # Phase 2: Generate focused report with real data based on analysis type
        analysis_type = result.get("analysis_type", "comprehensive")
        print(f"\n📝 Generating {analysis_type} report with real data...")
        report_data = report_writer.generate_comprehensive_report(result, analysis_type)
        
        # Phase 3: Create executive dashboard with real data
        print("📊 Creating executive dashboard with real data...")
        dashboard_path = report_writer.create_executive_dashboard(result)
        
        end_time = datetime.now()
        duration = (end_time - start_time).seconds
        
        # Display results
        print("\n" + "=" * 60)
        print("📋 REAL DATA ANALYSIS COMPLETE")
        print("=" * 60)
        
        print(f"⏱️  Analysis Duration: {duration} seconds")
        print(f"📊 Analysis Type: COMPREHENSIVE (Real Data)")
        print(f"📅 Period: 5 years")
        print(f"📈 Data Sources: FRED (Federal Reserve Economic Data)")
        
        # Show messages
        print("\n📝 Process Messages:")
        for message in result.get("messages", []):
            print(f"  {message}")
        
        # Show error messages if any
        if result.get("error_messages"):
            print("\n⚠️  Warnings/Errors:")
            for error in result.get("error_messages", []):
                print(f"  ❌ {error}")
        
        # Show key insights
        if result.get("economic_insights"):
            print("\n💡 Key Economic Insights (Real Data):")
            for i, insight in enumerate(result.get("economic_insights", [])[:5], 1):
                print(f"  {i}. {insight}")
        
        # Show chart paths
        if result.get("chart_paths"):
            print("\n📈 Generated Visualizations:")
            for chart in result.get("chart_paths", []):
                print(f"  📊 {chart}")
        
        # Show policy implications
        if result.get("policy_implications"):
            print("\n🏛️  Policy Implications (Based on Real Data):")
            for i, policy in enumerate(result.get("policy_implications", [])[:3], 1):
                print(f"  {i}. {policy}")
        
        print(f"\n📊 Executive Dashboard: {dashboard_path}")
        print("\n" + "=" * 60)
        print("✅ Real data economic analysis completed successfully!")
        print("📁 Check the 'economic_reports' and 'economic_charts' directories for detailed outputs.")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during real data analysis: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file has OPENAI_API_KEY and FRED_API_KEY")
        print("2. Verify internet connection for FRED API access")
        print("3. Ensure all required packages are installed")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--custom":
            run_custom_analysis()
        elif sys.argv[1] == "--real-data":
            run_with_real_data()
        else:
            print("Usage: python main_economic_analysis.py [--custom|--real-data]")
            print("  --custom: Run custom analysis with user input")
            print("  --real-data: Run comprehensive analysis with real data")
            sys.exit(1)
    else:
        main()