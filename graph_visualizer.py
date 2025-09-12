"""
LangGraph Economic Workflow Visualizer
This module provides comprehensive visualization of the economic analysis workflow
including data collection, analysis nodes, and report generation.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import os


class EconomicWorkflowVisualizer:
    """
    Visualizes the LangGraph economic analysis workflow with interactive charts
    and comprehensive node relationship mapping.
    """
    
    def __init__(self):
        self.workflow_nodes = {
            "collect_economic_data": {
                "type": "data_collection",
                "description": "Collect GDP, inflation, market, and industry data from FRED API",
                "inputs": ["analysis_type", "period", "focus_industries"],
                "outputs": ["raw_data"],
                "color": "#2E86AB",  # Blue
                "icon": "📊"
            },
            "analyze_gdp": {
                "type": "analysis",
                "description": "Analyze GDP trends, growth rates, and economic indicators",
                "inputs": ["raw_data"],
                "outputs": ["gdp_analysis"],
                "color": "#A23B72",  # Purple
                "icon": "📈"
            },
            "analyze_inflation": {
                "type": "analysis", 
                "description": "Analyze inflation rates, CPI trends, and price stability",
                "inputs": ["raw_data"],
                "outputs": ["inflation_analysis"],
                "color": "#F18F01",  # Orange
                "icon": "💰"
            },
            "analyze_market_trends": {
                "type": "analysis",
                "description": "Analyze stock market trends, volatility, and sector performance",
                "inputs": ["raw_data"],
                "outputs": ["market_analysis"],
                "color": "#C73E1D",  # Red
                "icon": "📊"
            },
            "analyze_industry_performance": {
                "type": "analysis",
                "description": "Analyze industry-specific metrics, employment, and wages",
                "inputs": ["raw_data"],
                "outputs": ["industry_analysis"],
                "color": "#3A5F0B",  # Green
                "icon": "🏭"
            },
            "generate_economic_insights": {
                "type": "ai_analysis",
                "description": "Generate AI-powered economic insights and correlations",
                "inputs": ["gdp_analysis", "inflation_analysis", "market_analysis", "industry_analysis"],
                "outputs": ["economic_insights"],
                "color": "#6A0572",  # Dark Purple
                "icon": "🤖"
            },
            "create_visualizations": {
                "type": "visualization",
                "description": "Create charts, dashboards, and data visualizations",
                "inputs": ["economic_insights", "raw_data"],
                "outputs": ["charts", "dashboards"],
                "color": "#FF6B35",  # Bright Orange
                "icon": "📊"
            },
            "policy_implications": {
                "type": "policy",
                "description": "Analyze policy implications and recommendations",
                "inputs": ["economic_insights"],
                "outputs": ["policy_analysis"],
                "color": "#1B4F72",  # Dark Blue
                "icon": "🏛️"
            },
            "generate_forecasts": {
                "type": "forecasting",
                "description": "Generate economic forecasts and predictions",
                "inputs": ["economic_insights", "policy_analysis"],
                "outputs": ["forecasts"],
                "color": "#8E44AD",  # Purple
                "icon": "🔮"
            },
            "final_report": {
                "type": "reporting",
                "description": "Generate comprehensive economic analysis report",
                "inputs": ["economic_insights", "policy_analysis", "forecasts", "charts"],
                "outputs": ["final_report"],
                "color": "#27AE60",  # Green
                "icon": "📄"
            }
        }
        
        self.conditional_routes = {
            "gdp_analysis": "analyze_inflation",
            "inflation_analysis": "analyze_market_trends", 
            "market_analysis": "analyze_industry_performance",
            "industry_analysis": "generate_economic_insights"
        }
        
        self.workflow_edges = [
            ("collect_economic_data", "analyze_gdp"),
            ("analyze_gdp", "analyze_inflation"),
            ("analyze_inflation", "analyze_market_trends"),
            ("analyze_market_trends", "analyze_industry_performance"),
            ("analyze_industry_performance", "generate_economic_insights"),
            ("generate_economic_insights", "create_visualizations"),
            ("create_visualizations", "policy_implications"),
            ("policy_implications", "generate_forecasts"),
            ("generate_forecasts", "final_report")
        ]

    def create_workflow_diagram(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create an interactive workflow diagram showing the economic analysis process.
        
        Args:
            save_path: Optional path to save the diagram as HTML
            
        Returns:
            Plotly figure object
        """
        # Create NetworkX graph
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for node_id, node_info in self.workflow_nodes.items():
            G.add_node(node_id, **node_info)
        
        # Add edges
        G.add_edges_from(self.workflow_edges)
        
        # Calculate layout
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        
        # Prepare data for Plotly
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_info.append(f"{edge[0]} → {edge[1]}")
        
        # Create edge trace
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines',
            name='Workflow'
        )
        
        # Prepare node data
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_info = []
        
        for node_id, (x, y) in pos.items():
            node_x.append(x)
            node_y.append(y)
            node_info_dict = self.workflow_nodes[node_id]
            node_text.append(f"{node_info_dict['icon']} {node_id.replace('_', ' ').title()}")
            node_colors.append(node_info_dict['color'])
            
            # Create hover info
            hover_text = f"""
            <b>{node_id.replace('_', ' ').title()}</b><br>
            Type: {node_info_dict['type'].replace('_', ' ').title()}<br>
            Description: {node_info_dict['description']}<br>
            Inputs: {', '.join(node_info_dict['inputs'])}<br>
            Outputs: {', '.join(node_info_dict['outputs'])}
            """
            node_info.append(hover_text)
        
        # Create node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=node_info,
            text=node_text,
            textposition="middle center",
            textfont=dict(size=10, color='white'),
            marker=dict(
                size=80,
                color=node_colors,
                line=dict(width=2, color='white'),
                opacity=0.9
            ),
            name='Nodes'
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=dict(
                               text='<b>LangGraph Economic Analysis Workflow</b>',
                               x=0.5,
                               font=dict(size=20, color='#2C3E50')
                           ),
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Interactive workflow showing data flow from collection to final report generation",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(color='#7F8C8D', size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           plot_bgcolor='white',
                           paper_bgcolor='white',
                           width=1200,
                           height=800
                       ))
        
        if save_path:
            fig.write_html(save_path)
            print(f"Workflow diagram saved to: {save_path}")
        
        return fig

    def create_node_type_breakdown(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a breakdown chart showing the distribution of node types in the workflow.
        
        Args:
            save_path: Optional path to save the chart as PNG
            
        Returns:
            Plotly figure object
        """
        # Count node types
        type_counts = {}
        type_colors = {}
        
        for node_info in self.workflow_nodes.values():
            node_type = node_info['type']
            if node_type not in type_counts:
                type_counts[node_type] = 0
                type_colors[node_type] = node_info['color']
            type_counts[node_type] += 1
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=[t.replace('_', ' ').title() for t in type_counts.keys()],
            values=list(type_counts.values()),
            marker_colors=list(type_colors.values()),
            textinfo='label+percent+value',
            textfont_size=12,
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(
                text='<b>Workflow Node Type Distribution</b>',
                x=0.5,
                font=dict(size=18, color='#2C3E50')
            ),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.01
            ),
            width=600,
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        if save_path:
            fig.write_image(save_path)
            print(f"Node type breakdown saved to: {save_path}")
        
        return fig

    def create_data_flow_diagram(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a data flow diagram showing how data moves through the workflow.
        
        Args:
            save_path: Optional path to save the diagram as HTML
            
        Returns:
            Plotly figure object
        """
        # Define data flow stages
        stages = [
            {"name": "Input", "data": ["analysis_type", "period", "focus_industries"], "color": "#3498DB"},
            {"name": "Collection", "data": ["raw_data"], "color": "#2ECC71"},
            {"name": "Analysis", "data": ["gdp_analysis", "inflation_analysis", "market_analysis", "industry_analysis"], "color": "#E74C3C"},
            {"name": "AI Processing", "data": ["economic_insights"], "color": "#9B59B6"},
            {"name": "Visualization", "data": ["charts", "dashboards"], "color": "#F39C12"},
            {"name": "Policy", "data": ["policy_analysis"], "color": "#1ABC9C"},
            {"name": "Forecasting", "data": ["forecasts"], "color": "#34495E"},
            {"name": "Output", "data": ["final_report"], "color": "#27AE60"}
        ]
        
        # Create Sankey diagram
        source = []
        target = []
        value = []
        label = []
        color = []
        
        # Add stage labels
        for i, stage in enumerate(stages):
            label.extend(stage["data"])
            color.extend([stage["color"]] * len(stage["data"]))
        
        # Create connections between stages
        for i in range(len(stages) - 1):
            current_stage = stages[i]
            next_stage = stages[i + 1]
            
            for j, current_data in enumerate(current_stage["data"]):
                for k, next_data in enumerate(next_stage["data"]):
                    source.append(label.index(current_data))
                    target.append(label.index(next_data))
                    value.append(1)
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=label,
                color=color
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color='rgba(0,0,0,0.2)'
            )
        )])
        
        fig.update_layout(
            title=dict(
                text='<b>Economic Analysis Data Flow</b>',
                x=0.5,
                font=dict(size=18, color='#2C3E50')
            ),
            font_size=12,
            width=1000,
            height=600,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"Data flow diagram saved to: {save_path}")
        
        return fig

    def create_performance_metrics(self, execution_times: Optional[Dict[str, float]] = None, 
                                 save_path: Optional[str] = None) -> go.Figure:
        """
        Create performance metrics visualization for workflow execution.
        
        Args:
            execution_times: Optional dict of node execution times
            save_path: Optional path to save the chart as PNG
            
        Returns:
            Plotly figure object
        """
        # Default execution times if not provided
        if execution_times is None:
            execution_times = {
                "collect_economic_data": 15.2,
                "analyze_gdp": 3.1,
                "analyze_inflation": 2.8,
                "analyze_market_trends": 4.5,
                "analyze_industry_performance": 6.2,
                "generate_economic_insights": 12.8,
                "create_visualizations": 8.3,
                "policy_implications": 5.1,
                "generate_forecasts": 7.9,
                "final_report": 2.4
            }
        
        # Prepare data
        nodes = list(execution_times.keys())
        times = list(execution_times.values())
        colors = [self.workflow_nodes[node]['color'] for node in nodes]
        
        # Create bar chart
        fig = go.Figure(data=[go.Bar(
            x=[node.replace('_', ' ').title() for node in nodes],
            y=times,
            marker_color=colors,
            text=[f"{t:.1f}s" for t in times],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Execution Time: %{y:.1f} seconds<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(
                text='<b>Workflow Node Execution Times</b>',
                x=0.5,
                font=dict(size=18, color='#2C3E50')
            ),
            xaxis_title="Workflow Nodes",
            yaxis_title="Execution Time (seconds)",
            xaxis=dict(tickangle=45),
            width=1000,
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        if save_path:
            fig.write_image(save_path)
            print(f"Performance metrics saved to: {save_path}")
        
        return fig

    def create_comprehensive_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a comprehensive dashboard showing all workflow visualizations.
        
        Args:
            save_path: Optional path to save the dashboard as HTML
            
        Returns:
            Plotly figure object
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Workflow Overview', 'Node Type Distribution', 
                          'Data Flow', 'Performance Metrics'),
            specs=[[{"type": "scatter"}, {"type": "pie"}],
                   [{"type": "sankey"}, {"type": "bar"}]],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # Add workflow overview (simplified)
        G = nx.DiGraph()
        G.add_edges_from(self.workflow_edges)
        pos = nx.spring_layout(G, k=2, iterations=30, seed=42)
        
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_colors = [self.workflow_nodes[node]['color'] for node in G.nodes()]
        
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', 
                               line=dict(width=1, color='#888'), 
                               showlegend=False, hoverinfo='none'), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers',
                               marker=dict(size=20, color=node_colors),
                               showlegend=False, hoverinfo='skip'), row=1, col=1)
        
        # Add pie chart
        type_counts = {}
        type_colors = {}
        for node_info in self.workflow_nodes.values():
            node_type = node_info['type']
            if node_type not in type_counts:
                type_counts[node_type] = 0
                type_colors[node_type] = node_info['color']
            type_counts[node_type] += 1
        
        fig.add_trace(go.Pie(labels=list(type_counts.keys()),
                           values=list(type_counts.values()),
                           marker_colors=list(type_colors.values()),
                           showlegend=False), row=1, col=2)
        
        # Add performance metrics
        execution_times = {
            "Data Collection": 15.2,
            "GDP Analysis": 3.1,
            "Inflation Analysis": 2.8,
            "Market Analysis": 4.5,
            "Industry Analysis": 6.2,
            "AI Insights": 12.8,
            "Visualizations": 8.3,
            "Policy Analysis": 5.1,
            "Forecasting": 7.9,
            "Final Report": 2.4
        }
        
        fig.add_trace(go.Bar(x=list(execution_times.keys()),
                           y=list(execution_times.values()),
                           marker_color='#3498DB',
                           showlegend=False), row=2, col=2)
        
        # Update layout
        fig.update_layout(
            title=dict(
                text='<b>LangGraph Economic Analysis Workflow Dashboard</b>',
                x=0.5,
                font=dict(size=20, color='#2C3E50')
            ),
            height=800,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Update subplot titles
        fig.update_annotations(font_size=14)
        
        if save_path:
            fig.write_html(save_path)
            print(f"Comprehensive dashboard saved to: {save_path}")
        
        return fig

    def export_workflow_metadata(self, save_path: str) -> None:
        """
        Export workflow metadata to JSON file.
        
        Args:
            save_path: Path to save the JSON file
        """
        metadata = {
            "workflow_name": "LangGraph Economic Analysis",
            "description": "Comprehensive economic analysis workflow using LangGraph",
            "created_at": datetime.now().isoformat(),
            "nodes": self.workflow_nodes,
            "edges": self.workflow_edges,
            "conditional_routes": self.conditional_routes,
            "total_nodes": len(self.workflow_nodes),
            "total_edges": len(self.workflow_edges)
        }
        
        with open(save_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Workflow metadata exported to: {save_path}")

    def generate_all_visualizations(self, output_dir: str = "workflow_visualizations") -> None:
        """
        Generate all workflow visualizations and save them to the specified directory.
        
        Args:
            output_dir: Directory to save all visualizations
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("🎨 Generating LangGraph Economic Workflow Visualizations...")
        
        # Generate all visualizations
        print("📊 Creating workflow diagram...")
        workflow_fig = self.create_workflow_diagram()
        workflow_fig.write_html(f"{output_dir}/workflow_diagram_{timestamp}.html")
        
        print("🥧 Creating node type breakdown...")
        breakdown_fig = self.create_node_type_breakdown()
        breakdown_fig.write_image(f"{output_dir}/node_breakdown_{timestamp}.png")
        
        print("🌊 Creating data flow diagram...")
        flow_fig = self.create_data_flow_diagram()
        flow_fig.write_html(f"{output_dir}/data_flow_{timestamp}.html")
        
        print("⚡ Creating performance metrics...")
        perf_fig = self.create_performance_metrics()
        perf_fig.write_image(f"{output_dir}/performance_metrics_{timestamp}.png")
        
        print("📈 Creating comprehensive dashboard...")
        dashboard_fig = self.create_comprehensive_dashboard()
        dashboard_fig.write_html(f"{output_dir}/workflow_dashboard_{timestamp}.html")
        
        print("📄 Exporting workflow metadata...")
        self.export_workflow_metadata(f"{output_dir}/workflow_metadata_{timestamp}.json")
        
        print(f"✅ All visualizations saved to: {output_dir}/")
        print(f"📁 Files created:")
        print(f"   - workflow_diagram_{timestamp}.html")
        print(f"   - node_breakdown_{timestamp}.png")
        print(f"   - data_flow_{timestamp}.html")
        print(f"   - performance_metrics_{timestamp}.png")
        print(f"   - workflow_dashboard_{timestamp}.html")
        print(f"   - workflow_metadata_{timestamp}.json")


def main():
    """Main function to demonstrate the visualizer."""
    print("🚀 LangGraph Economic Workflow Visualizer")
    print("=" * 50)
    
    # Create visualizer instance
    visualizer = EconomicWorkflowVisualizer()
    
    # Generate all visualizations
    visualizer.generate_all_visualizations()
    
    print("\n🎉 Workflow visualization complete!")
    print("Open the HTML files in your browser to view interactive visualizations.")


if __name__ == "__main__":
    main()
