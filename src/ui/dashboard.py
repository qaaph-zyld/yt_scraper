"""
Metrics dashboard for monitoring YouTube data analysis.
"""
from typing import Dict, List, Any
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import time
from pathlib import Path
import json
from loguru import logger

class MetricsDashboard:
    """Real-time metrics dashboard for monitoring."""
    
    def __init__(self, metrics_dir: str = "metrics"):
        """Initialize the dashboard."""
        self.logger = logger.bind(module="metrics_dashboard")
        self.metrics_dir = Path(metrics_dir)
        
        # Initialize Dash app
        self.app = dash.Dash(__name__, 
                           title="YouTube Analysis Metrics",
                           update_title=None)
        
        self._setup_layout()
        self._setup_callbacks()
        
        self.logger.info("Initialized MetricsDashboard with metrics_dir={}", metrics_dir)
    
    def _setup_layout(self):
        """Set up the dashboard layout."""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("YouTube Analysis Metrics Dashboard",
                        style={'textAlign': 'center'}),
                html.P("Real-time monitoring of analysis performance and health",
                      style={'textAlign': 'center'})
            ], style={'marginBottom': 30}),
            
            # Time range selector
            html.Div([
                html.Label("Time Range:"),
                dcc.Dropdown(
                    id='time-range',
                    options=[
                        {'label': 'Last Hour', 'value': '1h'},
                        {'label': 'Last 24 Hours', 'value': '24h'},
                        {'label': 'Last 7 Days', 'value': '7d'}
                    ],
                    value='24h'
                )
            ], style={'width': '200px', 'margin': '10px'}),
            
            # Performance Metrics
            html.Div([
                html.H2("Performance Metrics"),
                html.Div([
                    # Analysis Duration
                    html.Div([
                        dcc.Graph(id='analysis-duration-graph')
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    
                    # Memory Usage
                    html.Div([
                        dcc.Graph(id='memory-usage-graph')
                    ], style={'width': '48%', 'display': 'inline-block'})
                ])
            ]),
            
            # Content Analysis
            html.Div([
                html.H2("Content Analysis"),
                html.Div([
                    # Topic Distribution
                    html.Div([
                        dcc.Graph(id='topic-distribution-graph')
                    ], style={'width': '48%', 'display': 'inline-block'}),
                    
                    # Content Length
                    html.Div([
                        dcc.Graph(id='content-length-graph')
                    ], style={'width': '48%', 'display': 'inline-block'})
                ])
            ]),
            
            # Error Tracking
            html.Div([
                html.H2("Error Tracking"),
                html.Div([
                    html.Div(id='error-table')
                ])
            ]),
            
            # Auto-refresh
            dcc.Interval(
                id='interval-component',
                interval=5*1000,  # 5 seconds
                n_intervals=0
            )
        ])
    
    def _setup_callbacks(self):
        """Set up dashboard callbacks."""
        @self.app.callback(
            [Output('analysis-duration-graph', 'figure'),
             Output('memory-usage-graph', 'figure'),
             Output('topic-distribution-graph', 'figure'),
             Output('content-length-graph', 'figure'),
             Output('error-table', 'children')],
            [Input('interval-component', 'n_intervals'),
             Input('time-range', 'value')]
        )
        def update_graphs(n, time_range):
            try:
                # Calculate time range
                now = time.time()
                if time_range == '1h':
                    start_time = now - 3600
                elif time_range == '24h':
                    start_time = now - 86400
                else:  # 7d
                    start_time = now - 604800
                
                # Load metrics data
                metrics = self._load_metrics(start_time)
                
                # Create figures
                duration_fig = self._create_duration_graph(metrics)
                memory_fig = self._create_memory_graph(metrics)
                topic_fig = self._create_topic_graph(metrics)
                content_fig = self._create_content_graph(metrics)
                error_table = self._create_error_table(metrics)
                
                return duration_fig, memory_fig, topic_fig, content_fig, error_table
                
            except Exception as e:
                self.logger.error("Error updating dashboard: {}", str(e))
                return self._create_error_figure(), self._create_error_figure(), \
                       self._create_error_figure(), self._create_error_figure(), \
                       html.Div("Error loading data")
    
    def _load_metrics(self, start_time: float) -> Dict[str, pd.DataFrame]:
        """Load metrics data from files."""
        metrics = {}
        
        for metric_file in self.metrics_dir.glob("*.json"):
            try:
                with open(metric_file) as f:
                    data = json.load(f)
                
                # Filter by time range
                data = [d for d in data if d['timestamp'] >= start_time]
                
                if data:
                    df = pd.DataFrame(data)
                    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                    metrics[metric_file.stem] = df
                    
            except Exception as e:
                self.logger.error("Error loading {}: {}", metric_file.name, str(e))
        
        return metrics
    
    def _create_duration_graph(self, metrics: Dict[str, pd.DataFrame]) -> go.Figure:
        """Create analysis duration graph."""
        df = metrics.get('analysis_duration')
        if df is None or df.empty:
            return self._create_empty_figure("No Analysis Duration Data")
        
        fig = px.line(df, x='datetime', y='value',
                     title='Analysis Duration Over Time',
                     labels={'value': 'Duration (s)', 'datetime': 'Time'})
        return fig
    
    def _create_memory_graph(self, metrics: Dict[str, pd.DataFrame]) -> go.Figure:
        """Create memory usage graph."""
        df = metrics.get('memory_usage')
        if df is None or df.empty:
            return self._create_empty_figure("No Memory Usage Data")
        
        fig = px.line(df, x='datetime', y='value',
                     title='Memory Usage Over Time',
                     labels={'value': 'Memory (MB)', 'datetime': 'Time'})
        return fig
    
    def _create_topic_graph(self, metrics: Dict[str, pd.DataFrame]) -> go.Figure:
        """Create topic distribution graph."""
        df = metrics.get('topic_count')
        if df is None or df.empty:
            return self._create_empty_figure("No Topic Data")
        
        fig = px.histogram(df, x='value',
                          title='Topic Distribution',
                          labels={'value': 'Topics per Analysis'})
        return fig
    
    def _create_content_graph(self, metrics: Dict[str, pd.DataFrame]) -> go.Figure:
        """Create content length graph."""
        df = metrics.get('content_length')
        if df is None or df.empty:
            return self._create_empty_figure("No Content Length Data")
        
        fig = px.scatter(df, x='datetime', y='value',
                        title='Content Length Over Time',
                        labels={'value': 'Characters', 'datetime': 'Time'})
        return fig
    
    def _create_error_table(self, metrics: Dict[str, pd.DataFrame]) -> html.Div:
        """Create error tracking table."""
        df = metrics.get('error_count')
        if df is None or df.empty:
            return html.Div("No Errors Recorded")
        
        # Create table
        table_header = [
            html.Thead(html.Tr([
                html.Th("Time"),
                html.Th("Error Type"),
                html.Th("Message")
            ]))
        ]
        
        rows = []
        for _, row in df.iterrows():
            rows.append(html.Tr([
                html.Td(row['datetime'].strftime('%Y-%m-%d %H:%M:%S')),
                html.Td(row['labels'].get('error_type', 'Unknown')),
                html.Td(row['labels'].get('message', 'No message'))
            ]))
        
        table_body = [html.Tbody(rows)]
        
        return html.Table(
            table_header + table_body,
            style={'width': '100%', 'textAlign': 'left'}
        )
    
    def _create_empty_figure(self, message: str = "No Data") -> go.Figure:
        """Create an empty figure with a message."""
        return go.Figure().add_annotation(
            x=0.5, y=0.5,
            text=message,
            font=dict(size=20),
            showarrow=False,
            xref="paper", yref="paper"
        )
    
    def _create_error_figure(self) -> go.Figure:
        """Create an error figure."""
        return self._create_empty_figure("Error Loading Data")
    
    def run(self, host: str = "0.0.0.0", port: int = 8050, debug: bool = False):
        """Run the dashboard server."""
        self.logger.info("Starting dashboard server on {}:{}", host, port)
        self.app.run_server(host=host, port=port, debug=debug)
