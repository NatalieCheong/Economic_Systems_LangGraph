"""
LangGraph Economic Workflow Visualizer
This module provides comprehensive visualization of the actual LangGraph economic analysis workflow
showing the real StateGraph structure with nodes and edges.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import os


class EconomicWorkflowVisualizer:
    """
    Visualizes the actual LangGraph economic analysis workflow showing the real StateGraph structure
    with nodes, edges, and conditional routing.
    """
    
    def __init__(self):
        # Define the actual LangGraph workflow structure
        self.workflow_nodes = {
            "collect_economic_data": {
                "type": "data_collection",
                "description": "Collect GDP, inflation, market, and industry data from FRED API",
                "inputs": ["analysis_type", "period", "focus_industries"],
                "outputs": ["raw_data"],
                "color": "#2E86AB",  # Blue
                "icon": "📊",
                "position": (0, 0)
            },
            "analyze_gdp": {
                "type": "analysis",
                "description": "Analyze GDP trends, growth rates, and economic indicators",
                "inputs": ["raw_data"],
                "outputs": ["gdp_analysis"],
                "color": "#A23B72",  # Purple
                "icon": "📈",
                "position": (1, 0)
            },
            "analyze_inflation": {
                "type": "analysis", 
                "description": "Analyze inflation rates, CPI trends, and price stability",
                "inputs": ["raw_data"],
                "outputs": ["inflation_analysis"],
                "color": "#F18F01",  # Orange
                "icon": "💰",
                "position": (2, 0)
            },
            "analyze_market_trends": {
                "type": "analysis",
                "description": "Analyze market trend indicators and financial conditions",
                "inputs": ["raw_data"],
                "outputs": ["market_analysis"],
                "color": "#C73E1D",  # Red
                "icon": "📊",
                "position": (3, 0)
            },
            "analyze_industry_performance": {
                "type": "analysis",
                "description": "Analyze industry-specific metrics, employment, and wages",
                "inputs": ["raw_data"],
                "outputs": ["industry_analysis"],
                "color": "#3A5F0B",  # Green
                "icon": "🏭",
                "position": (4, 0)
            },
            "generate_economic_insights": {
                "type": "ai_analysis",
                "description": "Generate AI-powered economic insights and correlations",
                "inputs": ["gdp_analysis", "inflation_analysis", "market_analysis", "industry_analysis"],
                "outputs": ["economic_insights"],
                "color": "#6A0572",  # Dark Purple
                "icon": "🤖",
                "position": (2.5, 1)
            },
            "create_visualizations": {
                "type": "visualization",
                "description": "Create charts, dashboards, and data visualizations",
                "inputs": ["economic_insights", "raw_data"],
                "outputs": ["charts", "dashboards"],
                "color": "#FF6B35",  # Bright Orange
                "icon": "📊",
                "position": (2.5, 2)
            },
            "policy_implications": {
                "type": "policy",
                "description": "Analyze policy implications and recommendations",
                "inputs": ["economic_insights"],
                "outputs": ["policy_analysis"],
                "color": "#1B4F72",  # Dark Blue
                "icon": "🏛️",
                "position": (2.5, 3)
            },
            "generate_forecasts": {
                "type": "forecasting",
                "description": "Generate economic forecasts and predictions",
                "inputs": ["economic_insights", "policy_analysis"],
                "outputs": ["forecasts"],
                "color": "#8E44AD",  # Purple
                "icon": "🔮",
                "position": (2.5, 4)
            },
            "final_report": {
                "type": "reporting",
                "description": "Generate comprehensive economic analysis report",
                "inputs": ["economic_insights", "policy_analysis", "forecasts", "charts"],
                "outputs": ["final_report"],
                "color": "#27AE60",  # Green
                "icon": "📄",
                "position": (2.5, 5)
            }
        }
        
        # Define the actual workflow edges (connections between nodes)
        self.workflow_edges = [
            # Sequential analysis flow
            ("collect_economic_data", "analyze_gdp"),
            ("analyze_gdp", "analyze_inflation"),
            ("analyze_inflation", "analyze_market_trends"),
            ("analyze_market_trends", "analyze_industry_performance"),
            
            # Convergence to AI insights
            ("analyze_industry_performance", "generate_economic_insights"),
            
            # Final processing pipeline
            ("generate_economic_insights", "create_visualizations"),
            ("create_visualizations", "policy_implications"),
            ("policy_implications", "generate_forecasts"),
            ("generate_forecasts", "final_report")
        ]
        
        # Define conditional routing (for different analysis types)
        self.conditional_routes = {
            "gdp_analysis": "analyze_inflation",
            "inflation_analysis": "analyze_market_trends", 
            "market_analysis": "analyze_industry_performance",
            "industry_analysis": "generate_economic_insights"
        }

    def create_langgraph_workflow_diagram(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a comprehensive LangGraph workflow diagram showing the actual StateGraph structure.
        
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
        
        # Use custom positions for better layout
        pos = {}
        for node_id, node_info in self.workflow_nodes.items():
            pos[node_id] = node_info["position"]
        
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
            line=dict(width=3, color='#34495E'),
            hoverinfo='none',
            mode='lines',
            name='Workflow',
            showlegend=False
        )
        
        # Prepare node data
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_info = []
        node_sizes = []
        
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
            
            # Size nodes based on type
            if node_info_dict['type'] == 'data_collection':
                node_sizes.append(100)
            elif node_info_dict['type'] == 'ai_analysis':
                node_sizes.append(120)
            elif node_info_dict['type'] == 'reporting':
                node_sizes.append(110)
            else:
                node_sizes.append(90)
        
        # Create node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=node_info,
            text=node_text,
            textposition="middle center",
            textfont=dict(size=10, color='white', family="Arial, sans-serif"),
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=3, color='white'),
                opacity=0.9
            ),
            name='Workflow Nodes',
            showlegend=False
        )
        
        # Add annotations for workflow phases
        annotations = [
            dict(
                x=2, y=-0.5,
                xref="x", yref="y",
                text="<b>Data Collection & Analysis Phase</b>",
                showarrow=False,
                font=dict(size=14, color='#2C3E50'),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#2C3E50',
                borderwidth=1
            ),
            dict(
                x=2.5, y=3,
                xref="x", yref="y",
                text="<b>AI Processing & Output Phase</b>",
                showarrow=False,
                font=dict(size=14, color='#2C3E50'),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#2C3E50',
                borderwidth=1
            )
        ]
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=dict(
                               text='<b>LangGraph Economic Analysis Workflow</b><br><sub>StateGraph Structure with Conditional Routing</sub>',
                               x=0.5,
                               font=dict(size=20, color='#2C3E50')
                           ),
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=60),
                           annotations=annotations,
                           xaxis=dict(
                               showgrid=False, 
                               zeroline=False, 
                               showticklabels=False,
                               range=[-0.5, 5]
                           ),
                           yaxis=dict(
                               showgrid=False, 
                               zeroline=False, 
                               showticklabels=False,
                               range=[-1, 6]
                           ),
                           plot_bgcolor='white',
                           paper_bgcolor='white',
                           width=1200,
                           height=800
                       ))
        
        if save_path:
            fig.write_html(save_path)
            print(f"LangGraph workflow diagram saved to: {save_path}")
        
        return fig

    def create_workflow_legend(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a legend showing the different node types and their meanings.
        
        Args:
            save_path: Optional path to save the legend as PNG
            
        Returns:
            Plotly figure object
        """
        # Group nodes by type
        type_groups = {}
        for node_id, node_info in self.workflow_nodes.items():
            node_type = node_info['type']
            if node_type not in type_groups:
                type_groups[node_type] = []
            type_groups[node_type].append((node_id, node_info))
        
        # Create legend data
        legend_data = []
        colors = []
        descriptions = []
        
        for node_type, nodes in type_groups.items():
            type_name = node_type.replace('_', ' ').title()
            color = nodes[0][1]['color']
            icon = nodes[0][1]['icon']
            
            legend_data.append(f"{icon} {type_name}")
            colors.append(color)
            descriptions.append(f"Nodes: {', '.join([n[0].replace('_', ' ').title() for n in nodes])}")
        
        # Create bar chart for legend
        fig = go.Figure(data=[go.Bar(
            x=legend_data,
            y=[1] * len(legend_data),
            marker_color=colors,
            text=descriptions,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>%{text}<extra></extra>',
            showlegend=False
        )])
        
        fig.update_layout(
            title=dict(
                text='<b>LangGraph Workflow Node Types</b>',
                x=0.5,
                font=dict(size=18, color='#2C3E50')
            ),
            xaxis_title="Node Types",
            yaxis_title="",
            xaxis=dict(tickangle=45),
            yaxis=dict(showticklabels=False),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        if save_path:
            fig.write_image(save_path)
            print(f"Workflow legend saved to: {save_path}")
        
        return fig

    def create_workflow_metadata(self, save_path: str) -> None:
        """
        Export workflow metadata to JSON file.
        
        Args:
            save_path: Path to save the JSON file
        """
        metadata = {
            "workflow_name": "LangGraph Economic Analysis",
            "description": "Actual LangGraph StateGraph workflow for economic analysis",
            "created_at": datetime.now().isoformat(),
            "langgraph_structure": {
                "nodes": self.workflow_nodes,
                "edges": self.workflow_edges,
                "conditional_routes": self.conditional_routes
            },
            "statistics": {
                "total_nodes": len(self.workflow_nodes),
                "total_edges": len(self.workflow_edges),
                "node_types": list(set(node["type"] for node in self.workflow_nodes.values())),
                "workflow_phases": ["Data Collection & Analysis", "AI Processing & Output"]
            },
            "langgraph_implementation": {
                "framework": "LangGraph StateGraph",
                "state_schema": "EconomicAnalysisState",
                "conditional_routing": True,
                "ai_integration": "OpenAI GPT-4"
            }
        }
        
        with open(save_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Workflow metadata exported to: {save_path}")

    def generate_langgraph_visualizations(self, output_dir: str = "workflow_visualizations") -> None:
        """
        Generate LangGraph workflow visualizations and save them to the specified directory.
        
        Args:
            output_dir: Directory to save all visualizations
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("🎨 Generating LangGraph Economic Workflow Visualizations...")
        
        # Generate main workflow diagram
        print("📊 Creating LangGraph workflow diagram...")
        workflow_fig = self.create_langgraph_workflow_diagram()
        workflow_fig.write_html(f"{output_dir}/langgraph_workflow_{timestamp}.html")
        
        # Generate workflow legend
        print("📋 Creating workflow legend...")
        legend_fig = self.create_workflow_legend()
        legend_fig.write_image(f"{output_dir}/workflow_legend_{timestamp}.png")
        
        # Export workflow metadata
        print("📄 Exporting workflow metadata...")
        self.create_workflow_metadata(f"{output_dir}/langgraph_metadata_{timestamp}.json")
        
        print(f"✅ LangGraph visualizations saved to: {output_dir}/")
        print(f"📁 Files created:")
        print(f"   - langgraph_workflow_{timestamp}.html")
        print(f"   - workflow_legend_{timestamp}.png")
        print(f"   - langgraph_metadata_{timestamp}.json")
        print(f"\n🎯 The workflow diagram shows the actual LangGraph StateGraph structure!")


def main():
    """Main function to demonstrate the LangGraph workflow visualizer."""
    print("🚀 LangGraph Economic Workflow Visualizer")
    print("=" * 50)
    
    # Create visualizer instance
    visualizer = EconomicWorkflowVisualizer()
    
    # Generate LangGraph workflow visualizations
    visualizer.generate_langgraph_visualizations()
    
    print("\n🎉 LangGraph workflow visualization complete!")
    print("Open the HTML file in your browser to view the interactive LangGraph workflow.")
    print("This shows the actual StateGraph structure used in the economic analysis system!")


if __name__ == "__main__":
    main()