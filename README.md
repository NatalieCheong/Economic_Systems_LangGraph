# Economic Analysis AI Agents with LangGraph

A comprehensive economic analysis system that uses LangGraph to orchestrate AI agents for macroeconomic analysis and automated report generation. The system fetches real-time economic data from multiple authoritative sources including FRED, Alpha Vantage, and Yahoo Finance, performs sophisticated economic analysis, and generates professional-grade economic reports.

## 🌟 Features

### Core Economic Analysis Capabilities
- **Multi-Source Data Integration**: Fetch data from FRED (Federal Reserve), Alpha Vantage, and Yahoo Finance
- **Comprehensive Economic Indicators**: GDP, inflation, employment, monetary policy, and market sentiment analysis
- **Advanced Economic Analytics**: Growth trends, inflation dynamics, labor market analysis, and policy implications
- **AI-Powered Insights**: LLM-generated economic narratives and strategic recommendations
- **Professional Visualizations**: Economic dashboards and trend analysis charts
- **Real-time Data Processing**: Live economic data with automated quality validation

### 10-Step Economic Analysis Workflow
1. **Data Collection**: Multi-source economic data aggregation with quality validation
2. **Growth Analysis**: GDP, productivity, and economic expansion assessment
3. **Inflation Analysis**: Price trends, core vs headline inflation, and policy implications
4. **Employment Analysis**: Labor market health, unemployment dynamics, and workforce trends
5. **Monetary Policy Analysis**: Federal Reserve policy, interest rates, and financial conditions
6. **Market Sentiment Analysis**: Financial markets, consumer confidence, and risk indicators
7. **Economic Insights Generation**: AI-powered synthesis of cross-indicator relationships
8. **Visualization Creation**: Economic dashboards and comprehensive chart generation
9. **Policy Implications Analysis**: Strategic recommendations for policymakers
10. **Economic Outlook Generation**: Short, medium, and long-term economic forecasts

### Professional Report Generation
- **Executive Summaries**: Strategic insights for senior decision-makers
- **Comprehensive Analysis**: Detailed economic assessment with data-driven insights
- **Policy Briefs**: Focused analysis for specific economic areas
- **Multiple Audiences**: Tailored content for policymakers, investors, academics, and public

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (Required for LangGraph)
- **OpenAI API Key** (Required for AI analysis)
- **Alpha Vantage API Key** (Recommended for enhanced data)
- **FRED API Key** (Optional but recommended for higher rate limits)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/YourUsername/Economic_Analysis_LangGraph.git
cd Economic_Analysis_LangGraph

# Create virtual environment with Python 3.11+
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Create .env file with your API keys
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
FRED_API_KEY=your_fred_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=economic-analysis
EOF
```

### 3. Basic Usage

```bash
# Run comprehensive economic analysis
python main.py --analysis-type comprehensive --period 5y

# Focus on inflation analysis
python main.py --analysis-type inflation_focus --period 2y

# Generate policy brief
python main.py --analysis-type monetary_policy --report-type policy_brief

# Interactive mode
python main.py --interactive
```

## 📊 Data Sources and Economic Indicators

### Federal Reserve Economic Data (FRED)
- **GDP and Growth**: Real GDP, GDP growth rate, industrial production
- **Inflation**: CPI, Core CPI, PCE, Core PCE price indices
- **Employment**: Unemployment rate, nonfarm payrolls, labor force participation
- **Monetary Policy**: Federal funds rate, Treasury yields, yield curve
- **Regional Data**: State-level unemployment and economic indicators
- **International**: Global GDP comparisons and trade data

### Alpha Vantage Economic Indicators
- **Real GDP**: Quarterly real gross domestic product data
- **Consumer Prices**: Monthly CPI and inflation data
- **Employment**: Unemployment rates and nonfarm payroll data
- **Retail Sales**: Consumer spending and economic activity indicators

### Yahoo Finance Market Data
- **Equity Markets**: S&P 500, NASDAQ, Dow Jones indices
- **Fixed Income**: Treasury bonds, corporate bonds, yield curves
- **Commodities**: Gold, oil, agricultural commodities
- **Currencies**: US Dollar Index, major currency pairs
- **Volatility**: VIX and market stress indicators

## 🏗️ System Architecture

### Core Components

#### 1. Economic Data Agent (`economic_data_agent.py`)
- Multi-source data fetching and validation
- Economic indicator calculation and analysis
- Data quality assessment and reporting
- Comprehensive economic dashboard generation

#### 2. LangGraph Economic Agent (`langgraph_economic_agent.py`)
- 10-step economic analysis workflow orchestration
- AI-powered economic insight generation
- Cross-indicator relationship analysis
- Policy implications assessment

#### 3. Economic Report Writer (`economic_report_writer.py`)
- Professional economic report generation
- Multiple report formats and audiences
- Structured economic narrative creation
- Policy recommendations synthesis

#### 4. Main Application (`main.py`)
- Command-line interface and interactive mode
- Workflow orchestration and error handling
- Results compilation and file management

### Configuration (`config.py`)
- Centralized system configuration
- Economic indicator definitions
- API rate limiting and data source management
- Output directory and file management

## 📈 Analysis Types and Capabilities

### Comprehensive Analysis
- Full economic assessment across all major indicators
- Growth, inflation, employment, and monetary policy analysis
- Regional and international comparisons
- Complete policy implications and outlook

### Focused Analysis Options
- **GDP Focus**: Economic growth, productivity, and expansion analysis
- **Inflation Focus**: Price stability, inflation trends, and monetary policy
- **Industry Performance**: Manufacturing, retail, construction, and sectoral analysis
- **Market Trend**: Corporate profitability, investment, credit markets, and financial dynamics

### Report Types
- **Executive Reports**: Strategic insights for senior leadership
- **Comprehensive Reports**: Detailed analysis with full methodology
- **Policy Briefs**: Focused recommendations for specific areas

## 📊 Sample Analysis Results

### Economic Indicators Coverage
- **50+ Core Economic Indicators** from authoritative sources
- **Real-time Data Processing** with quality validation
- **Historical Context** with trend analysis and cyclical assessment
- **Cross-indicator Correlations** and causation analysis

### Generated Outputs
- **Economic Dashboards**: Professional visualizations with trend analysis
- **Comprehensive Reports**: 15-20 page institutional-quality analysis
- **Policy Recommendations**: Specific, actionable guidance for decision-makers
- **Economic Forecasts**: Short, medium, and long-term projections

## 🔧 Advanced Configuration

### Analysis Customization
```python
# Custom economic analysis
from economic_main_app import EconomicAnalysisApp

app = EconomicAnalysisApp()
results = app.run_analysis(
    analysis_type="comprehensive",
    period="10y",
    include_regional=True,
    include_international=True,
    generate_report=True,
    report_type="comprehensive",
    target_audience="policymakers"
)
```

### API Integration
```python
# Direct agent usage
from langgraph_economic_agent import LangGraphEconomicAgent

agent = LangGraphEconomicAgent()
analysis_state = agent.analyze_economy(
    analysis_type="inflation_focus",
    period="2y"
)
summary = agent.get_analysis_summary(analysis_state)
```

## 📁 Project Structure

```
Economic_Analysis_LangGraph/
├── config.py                      # System configuration and settings
├── economic_data_agent.py          # Core economic data fetching and processing
├── langgraph_economic_agent.py     # LangGraph workflow orchestration
├── economic_report_writer.py       # AI-powered report generation
├── main.py                         # Main application and CLI interface
├── requirements.txt                # Python dependencies
├── .env.template                   # Environment variables template
├── charts/                         # Generated economic charts
├── reports/                        # Generated economic reports
├── data_cache/                     # Cached economic data
└── README.md                       # This file
```

## 🎯 Use Cases and Applications

### Policy Analysis
- **Central Bank Research**: Monetary policy analysis and recommendations
- **Government Analysis**: Economic policy impact assessment
- **Academic Research**: Comprehensive economic data analysis
- **Think Tank Reports**: Policy-focused economic research

### Investment Analysis
- **Economic Intelligence**: Market-economy relationship analysis
- **Risk Assessment**: Economic scenario analysis and forecasting
- **Asset Allocation**: Economic cycle-based investment strategies
- **Due Diligence**: Economic environment assessment

### Business Intelligence
- **Strategic Planning**: Economic outlook for business decisions
- **Market Research**: Economic trends affecting industries
- **Risk Management**: Economic scenario planning
- **Competitive Analysis**: Economic factors affecting competition

## ⚠️ Important Disclaimers

### Economic Analysis Disclaimer
- This system is for informational and educational purposes only
- Economic forecasts are subject to significant uncertainty
- Past economic performance does not guarantee future results
- Users should conduct independent analysis and consult qualified economists

### Data Source Limitations
- Analysis depends on data quality from third-party sources
- Economic indicators may be revised by statistical agencies
- Time lags in data publication may affect current assessments
- API rate limits may affect data availability

### Investment and Policy Disclaimer
- This system does not constitute investment advice or policy recommendations
- Economic conditions can change rapidly and unpredictably
- Consult qualified advisors before making financial or policy decisions

## 🔐 Security and Best Practices

### API Key Management
- Store API keys in environment variables
- Never commit keys to version control
- Use separate keys for development and production
- Monitor API usage and implement rate limiting

### Data Privacy
- All processing happens locally unless using external APIs
- No economic data is stored permanently without user consent
- Clear data retention policies for cached information

## 🚀 Advanced Features

### Custom Economic Models
- Integration with econometric models
- Custom indicator development and analysis
- Advanced statistical analysis and forecasting
- Machine learning-enhanced economic predictions

### Automation and Monitoring
- Scheduled economic analysis runs
- Economic alert systems for significant changes
- Automated report distribution
- Real-time economic monitoring dashboards

## 📞 Support and Documentation

### Getting Help
1. Check the configuration and setup sections
2. Review API documentation for data sources
3. Examine sample outputs and analysis results
4. Contact support for technical issues

### Contributing
- Fork the repository and create feature branches
- Follow Python coding standards and documentation
- Add tests for new economic indicators or analysis features
- Submit pull requests with detailed descriptions

## 📄 License and Attribution

### License
This project is provided under the MIT License for educational and research purposes.

### Data Attribution
- **FRED Data**: Federal Reserve Bank of St. Louis (Public Domain)
- **Alpha Vantage**: Subject to Alpha Vantage API terms and conditions
- **Yahoo Finance**: Subject to Yahoo Terms of Service

### Citation
When using this system for research or analysis, please cite:
```
Economic Analysis AI Agents with LangGraph
AI-Powered Economic Intelligence System
[Year] - [Your Organization/Name]
```

---

**Last Updated**: [Current Date]  
**Python Version**: 3.11+  
**LangGraph Version**: 0.2.16+  
**Status**: ✅ Production Ready

For detailed API documentation and advanced usage examples, see the `/docs` directory or visit our documentation website.