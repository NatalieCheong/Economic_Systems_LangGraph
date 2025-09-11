#!/usr/bin/env python3
"""
Main application for Economic Analysis AI Agents with LangGraph
Integrates data collection, analysis, and report generation
"""

import argparse
import sys
from typing import List, Optional
from config import Config
from langgraph_economic_agent import LangGraphEconomicAgent
from economic_report_writer import EconomicReportWriter
import json
from datetime import datetime

class EconomicAnalysisApp:
    """Main application class orchestrating the economic analysis workflow"""
    
    def __init__(self):
        """Initialize the application with agents"""
        try:
            Config.validate()
            self.economic_agent = LangGraphEconomicAgent()
            self.report_writer = EconomicReportWriter()
            print("✅ Economic Analysis Application initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize application: {e}")
            sys.exit(1)
    
    def run_analysis(self, 
                    analysis_type: str = "comprehensive",
                    period: str = "5y",
                    include_regional: bool = True,
                    include_international: bool = True,
                    generate_report: bool = True,
                    report_type: str = "comprehensive",
                    target_audience: str = "policymakers",
                    save_results: bool = True) -> dict:
        """
        Run complete economic analysis workflow
        
        Args:
            analysis_type: Type of analysis ('comprehensive', 'gdp_focus', 'inflation_focus', etc.)
            period: Analysis period ('1y', '2y', '5y', '10y')
            include_regional: Whether to include regional economic data
            include_international: Whether to include international comparison data
            generate_report: Whether to generate a written report
            report_type: Type of report ('executive', 'comprehensive', 'policy_brief')
            target_audience: Target audience ('policymakers', 'investors', 'academics', 'public')
            save_results: Whether to save results to files
        
        Returns:
            Dictionary containing analysis results and file paths
        """
        results = {
            'success': False,
            'analysis_data': None,
            'report_data': None,
            'files_created': [],
            'errors': []
        }
        
        try:
            print(f"\n🚀 Starting Economic Analysis Workflow")
            print(f"Analysis Type: {analysis_type}")
            print(f"Period: {period}")
            print(f"Regional Data: {'Yes' if include_regional else 'No'}")
            print(f"International Data: {'Yes' if include_international else 'No'}")
            print("-" * 50)
            
            # Step 1: Run economic analysis
            print("Step 1: Running comprehensive economic analysis...")
            analysis_state = self.economic_agent.analyze_economy(
                analysis_type=analysis_type,
                period=period,
                include_regional=include_regional,
                include_international=include_international
            )
            
            analysis_summary = self.economic_agent.get_analysis_summary(analysis_state)
            results['analysis_data'] = analysis_summary
            
            # Check for analysis errors
            if analysis_summary['errors']:
                print(f"⚠️ Analysis completed with warnings: {analysis_summary['errors']}")
                results['errors'].extend(analysis_summary['errors'])
            
            print("✅ Economic analysis completed successfully")
            
            # Step 2: Generate report (if requested)
            if generate_report:
                print("\nStep 2: Generating economic report...")
                
                report_state = self.report_writer.generate_economic_report(
                    analysis_data=analysis_summary,
                    report_type=report_type,
                    target_audience=target_audience
                )
                
                results['report_data'] = report_state
                print("✅ Report generation completed successfully")
                
                # Step 3: Save files (if requested)
                if save_results:
                    print("\nStep 3: Saving results...")
                    
                    # Save report
                    report_filepath = self.report_writer.save_economic_report(report_state)
                    results['files_created'].append(report_filepath)
                    
                    # Save analysis data as JSON
                    json_filepath = self._save_analysis_json(analysis_summary, analysis_type)
                    results['files_created'].append(json_filepath)
                    
                    # Chart files are already saved by the economic agent
                    results['files_created'].extend(analysis_summary.get('chart_paths', []))
                    
                    print("✅ All files saved successfully")
            
            results['success'] = True
            
            # Display summary
            self._display_summary(results)
            
        except Exception as e:
            error_msg = f"Error in economic analysis workflow: {str(e)}"
            print(f"❌ {error_msg}")
            results['errors'].append(error_msg)
        
        return results
    
    def _save_analysis_json(self, analysis_data: dict, analysis_type: str) -> str:
        """Save analysis data as JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"economic_analysis_{analysis_type}_{timestamp}.json"
        filepath = f"{Config.REPORT_OUTPUT_DIR}/{filename}"
        
        # Convert analysis data for JSON serialization
        json_data = self._prepare_json_data(analysis_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        return filepath
    
    def _prepare_json_data(self, data: dict) -> dict:
        """Prepare data for JSON serialization"""
        json_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                json_data[key] = {k: str(v) if not isinstance(v, (dict, list, str, int, float, bool, type(None))) else v 
                                 for k, v in value.items()}
            elif isinstance(value, list):
                json_data[key] = [str(item) if not isinstance(item, (dict, list, str, int, float, bool, type(None))) else item 
                                 for item in value]
            else:
                json_data[key] = value
        
        return json_data
    
    def _display_summary(self, results: dict):
        """Display a summary of the analysis results"""
        print(f"\n{'='*60}")
        print("ECONOMIC ANALYSIS WORKFLOW SUMMARY")
        print(f"{'='*60}")
        
        if results['success']:
            print("✅ Status: SUCCESS")
        else:
            print("❌ Status: FAILED")
        
        if results['analysis_data']:
            analysis = results['analysis_data']
            print(f"📊 Analysis Type: {analysis.get('analysis_type', 'N/A')}")
            print(f"📅 Period: {analysis.get('period', 'N/A')}")
            print(f"📈 Indicators Analyzed: {len(analysis.get('indicators_analyzed', []))}")
            print(f"📊 Charts Created: {len(analysis.get('chart_paths', []))}")
            print(f"📋 Data Quality: {analysis.get('data_quality', {}).get('successful_fetches', 0)}/{analysis.get('data_quality', {}).get('total_indicators', 0)} indicators")
        
        if results['report_data']:
            print("📄 Report Generated: YES")
        else:
            print("📄 Report Generated: NO")
        
        if results['files_created']:
            print(f"💾 Files Created: {len(results['files_created'])}")
            for file_path in results['files_created']:
                print(f"   - {file_path}")
        
        if results['errors']:
            print(f"⚠️ Errors/Warnings: {len(results['errors'])}")
            for error in results['errors']:
                print(f"   - {error}")
        
        print(f"{'='*60}")

    def quick_economic_analysis(self, analysis_type: str = "comprehensive", period: str = "5y") -> dict:
        """Run a quick economic analysis"""
        return self.run_analysis(
            analysis_type=analysis_type,
            period=period,
            include_regional=True,
            include_international=True,
            generate_report=True,
            report_type="comprehensive",
            target_audience="policymakers",
            save_results=True
        )
    
    def policy_brief_analysis(self, focus_area: str = "inflation_focus", period: str = "2y") -> dict:
        """Generate a focused policy brief analysis"""
        return self.run_analysis(
            analysis_type=focus_area,
            period=period,
            include_regional=False,
            include_international=True,
            generate_report=True,
            report_type="policy_brief",
            target_audience="policymakers",
            save_results=True
        )
    
    def investor_economic_analysis(self, period: str = "5y") -> dict:
        """Generate economic analysis for investors"""
        return self.run_analysis(
            analysis_type="comprehensive",
            period=period,
            include_regional=True,
            include_international=True,
            generate_report=True,
            report_type="comprehensive",
            target_audience="investors",
            save_results=True
        )

def main():
    """Main entry point for command line usage"""
    parser = argparse.ArgumentParser(
        description="Economic Analysis AI Agents with LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Comprehensive economic analysis
    python main.py --analysis-type comprehensive --period 5y
    
    # Focus on inflation analysis
    python main.py --analysis-type inflation_focus --period 2y
    
    # GDP-focused analysis
    python main.py --analysis-type gdp_focus --period 10y
    
    # Employment analysis without regional data
    python main.py --analysis-type employment_focus --no-regional
    
    # Quick analysis without report
    python main.py --analysis-type comprehensive --no-report
    
    # Policy brief for monetary policy focus
    python main.py --analysis-type monetary_policy --report-type policy_brief
        """
    )
    
    parser.add_argument(
        '--analysis-type',
        choices=['comprehensive', 'gdp_focus', 'inflation_focus', 'employment_focus', 'monetary_policy'],
        default='comprehensive',
        help='Type of economic analysis to perform (default: comprehensive)'
    )
    
    parser.add_argument(
        '--period',
        choices=['1y', '2y', '5y', '10y', '20y'],
        default='5y',
        help='Analysis period (default: 5y)'
    )
    
    parser.add_argument(
        '--report-type',
        choices=['executive', 'comprehensive', 'policy_brief'],
        default='comprehensive',
        help='Type of report to generate (default: comprehensive)'
    )
    
    parser.add_argument(
        '--target-audience',
        choices=['policymakers', 'investors', 'academics', 'public'],
        default='policymakers',
        help='Target audience for the report (default: policymakers)'
    )
    
    parser.add_argument(
        '--no-regional',
        action='store_true',
        help='Exclude regional economic data'
    )
    
    parser.add_argument(
        '--no-international',
        action='store_true',
        help='Exclude international comparison data'
    )
    
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Skip report generation (analysis only)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to files'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    args = parser.parse_args()
    
    # Initialize application
    try:
        app = EconomicAnalysisApp()
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return 1
    
    # Run analysis
    if args.interactive:
        run_interactive_mode(app)
        return 0
    else:
        results = app.run_analysis(
            analysis_type=args.analysis_type,
            period=args.period,
            include_regional=not args.no_regional,
            include_international=not args.no_international,
            generate_report=not args.no_report,
            report_type=args.report_type,
            target_audience=args.target_audience,
            save_results=not args.no_save
        )
        
        # Return appropriate exit code
        return 0 if results['success'] else 1

def run_interactive_mode(app: EconomicAnalysisApp):
    """Run the application in interactive mode"""
    print("\n🏛️ Economic Analysis AI - Interactive Mode")
    print("=" * 50)
    
    while True:
        print("\nAvailable options:")
        print("1. Comprehensive Economic Analysis")
        print("2. GDP and Growth Focus")
        print("3. Inflation Analysis")
        print("4. Employment Analysis")
        print("5. Monetary Policy Analysis")
        print("6. Policy Brief Generation")
        print("7. Investor-Focused Analysis")
        print("8. Custom Analysis")
        print("9. Exit")
        
        try:
            choice = input("\nSelect an option (1-9): ").strip()
            
            if choice == "1":
                period = input("Enter period (1y/2y/5y/10y): ").strip() or "5y"
                print(f"\n🚀 Running comprehensive economic analysis...")
                app.quick_economic_analysis("comprehensive", period)
                
            elif choice == "2":
                period = input("Enter period (1y/2y/5y/10y): ").strip() or "5y"
                print(f"\n📈 Running GDP and growth analysis...")
                app.quick_economic_analysis("gdp_focus", period)
                
            elif choice == "3":
                period = input("Enter period (1y/2y/5y): ").strip() or "2y"
                print(f"\n💰 Running inflation analysis...")
                app.quick_economic_analysis("inflation_focus", period)
                
            elif choice == "4":
                period = input("Enter period (1y/2y/5y): ").strip() or "5y"
                print(f"\n👥 Running employment analysis...")
                app.quick_economic_analysis("employment_focus", period)
                
            elif choice == "5":
                period = input("Enter period (1y/2y/5y): ").strip() or "2y"
                print(f"\n🏦 Running monetary policy analysis...")
                app.quick_economic_analysis("monetary_policy", period)
                
            elif choice == "6":
                focus_options = ['inflation_focus', 'employment_focus', 'monetary_policy', 'gdp_focus']
                print(f"Available focus areas: {', '.join(focus_options)}")
                focus_area = input("Enter focus area: ").strip() or "inflation_focus"
                period = input("Enter period (1y/2y/5y): ").strip() or "2y"
                print(f"\n📋 Generating policy brief for {focus_area}...")
                app.policy_brief_analysis(focus_area, period)
                
            elif choice == "7":
                period = input("Enter period (2y/5y/10y): ").strip() or "5y"
                print(f"\n💼 Running investor-focused analysis...")
                app.investor_economic_analysis(period)
                
            elif choice == "8":
                print("\nCustom Economic Analysis Configuration:")
                analysis_type = input("Analysis type (comprehensive/gdp_focus/inflation_focus/industry_performance/market_trend): ").strip() or "comprehensive"
                period = input("Period (1y/2y/5y/10y/20y): ").strip() or "5y"
                report_type = input("Report type (executive/comprehensive/policy_brief): ").strip() or "comprehensive"
                target_audience = input("Target audience (policymakers/investors/academics/public): ").strip() or "policymakers"
                
                include_regional = input("Include regional data? (y/n): ").strip().lower() != 'n'
                include_international = input("Include international data? (y/n): ").strip().lower() != 'n'
                generate_report = input("Generate report? (y/n): ").strip().lower() != 'n'
                save_results = input("Save results? (y/n): ").strip().lower() != 'n'
                
                print(f"\n🚀 Running custom economic analysis...")
                app.run_analysis(
                    analysis_type=analysis_type,
                    period=period,
                    include_regional=include_regional,
                    include_international=include_international,
                    generate_report=generate_report,
                    report_type=report_type,
                    target_audience=target_audience,
                    save_results=save_results
                )
                
            elif choice == "9":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid option. Please select 1-9.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Economic analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)