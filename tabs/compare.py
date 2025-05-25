#!/usr/bin/env python
# coding: utf-8

"""
Compare tab layout and callbacks for the cognitive warfare dashboard.
This tab allows comparison of two different data slices using various visualization methods.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from database.data_fetchers import fetch_category_data
from components.layout import create_filter_card
from utils.helpers import create_comparison_text
from config import DEFAULT_START_DATE, DEFAULT_END_DATE

# Define comparison visualization options
COMPARISON_VISUALIZATION_OPTIONS = [
    {'label': 'Bar Chart', 'value': 'bar'},
    {'label': 'Sunburst Comparison', 'value': 'sunburst'},
    {'label': 'Donut Chart', 'value': 'donut'},
    {'label': 'Sankey Diagram', 'value': 'sankey'}
]

def create_compare_tab_layout(source_options: List, min_date: datetime = None, max_date: datetime = None) -> html.Div:
    """
    Create the Compare tab layout.
    
    Args:
        source_options: Source options for filters
        min_date: Minimum date for filters
        max_date: Maximum date for filters
        
    Returns:
        html.Div: Compare tab layout
    """
    if min_date is None:
        min_date = DEFAULT_START_DATE
    if max_date is None:
        max_date = DEFAULT_END_DATE
    
    compare_tab_layout = html.Div([
        # Instructions
        dbc.Alert([
            html.H5("Compare Data Slices", className="mb-2"),
            html.P("Configure two different data selections below and compare their taxonomy distributions. "
                   "Use different filters for each selection to analyze differences in cognitive warfare patterns.")
        ], color="info", className="mb-3"),
        
        # Selection 1
        dbc.Card([
            dbc.CardHeader([
                html.H5("Selection 1", className="mb-0 text-primary")
            ]),
            dbc.CardBody([
                create_filter_card(
                    id_prefix="compare-1",
                    source_options=source_options,
                    min_date=min_date,
                    max_date=max_date
                )
            ])
        ], className="mb-3"),
        
        # Selection 2
        dbc.Card([
            dbc.CardHeader([
                html.H5("Selection 2", className="mb-0 text-success")
            ]),
            dbc.CardBody([
                create_filter_card(
                    id_prefix="compare-2",
                    source_options=source_options,
                    min_date=min_date,
                    max_date=max_date
                )
            ])
        ], className="mb-3"),
        
        # Comparison controls
        dbc.Card([
            dbc.CardHeader([
                html.H5("Comparison Settings", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Visualization Type:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="compare-viz-type",
                            options=COMPARISON_VISUALIZATION_OPTIONS,
                            value='bar',
                            placeholder="Select visualization type..."
                        )
                    ], width=6),
                    
                    dbc.Col([
                        html.Label(" ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dbc.Button(
                            "Compare Selections",
                            id="compare-execute-button",
                            color="primary",
                            style={'width': '100%'}
                        )
                    ], width=6)
                ])
            ])
        ], className="mb-3"),
        
        # Results container
        html.Div(id="compare-results-container"),
        
        # Store for comparison data
        dcc.Store(id="compare-data-store")
    ])
    
    return compare_tab_layout

def register_compare_callbacks(app):
    """Register callbacks for the Compare tab."""
    
    @app.callback(
        [
            Output("compare-results-container", "children"),
            Output("compare-data-store", "data")
        ],
        [Input("compare-execute-button", "n_clicks")],
        [
            # Selection 1 filters
            State("compare-1-source-dropdown", "value"),
            State("compare-1-date-range", "start_date"),
            State("compare-1-date-range", "end_date"),
            State("compare-1-language-dropdown", "value"),
            
            # Selection 2 filters
            State("compare-2-source-dropdown", "value"),
            State("compare-2-date-range", "start_date"),
            State("compare-2-date-range", "end_date"),
            State("compare-2-language-dropdown", "value"),
            
            # Comparison settings
            State("compare-viz-type", "value")
        ],
        prevent_initial_call=True
    )
    def execute_comparison(n_clicks, 
                          sources1, start_date1, end_date1, languages1,
                          sources2, start_date2, end_date2, languages2,
                          viz_type):
        """Execute comparison between two data selections."""
        if not n_clicks:
            return html.Div(), {}
        
        try:
            # Convert date strings to date objects
            start_date1 = datetime.strptime(start_date1, '%Y-%m-%d').date() if start_date1 else None
            end_date1 = datetime.strptime(end_date1, '%Y-%m-%d').date() if end_date1 else None
            start_date2 = datetime.strptime(start_date2, '%Y-%m-%d').date() if start_date2 else None
            end_date2 = datetime.strptime(end_date2, '%Y-%m-%d').date() if end_date2 else None
            
            # Fetch data for both selections
            df1 = fetch_category_data(
                sources=sources1,
                start_date=start_date1,
                end_date=end_date1,
                languages=languages1
            )
            
            df2 = fetch_category_data(
                sources=sources2,
                start_date=start_date2,
                end_date=end_date2,
                languages=languages2
            )
            
            # Check if we have data
            if df1.empty and df2.empty:
                return html.Div([
                    dbc.Alert("Both selections returned no data. Please adjust your filters.", color="warning")
                ]), {}
            
            # Calculate totals
            total1 = df1['count'].sum() if not df1.empty else 0
            total2 = df2['count'].sum() if not df2.empty else 0
            
            # Create comparison visualization
            comparison_fig = create_comparison_plot(df1, df2, viz_type)
            
            # Create summary statistics
            summary_stats = create_comparison_summary_stats(df1, df2)
            
            # Create comparison text
            comparison_text = create_comparison_text(
                {'total': total1}, 
                {'total': total2}
            )
            
            results_content = html.Div([
                # Summary statistics
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Selection 1", className="text-primary"),
                            dbc.CardBody([
                                html.H4(f"{total1:,}", className="text-primary mb-0"),
                                html.P("Total Classifications", className="mb-0"),
                                html.Small(f"{len(df1)} categories" if not df1.empty else "No data", className="text-muted")
                            ])
                        ])
                    ], width=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Selection 2", className="text-success"),
                            dbc.CardBody([
                                html.H4(f"{total2:,}", className="text-success mb-0"),
                                html.P("Total Classifications", className="mb-0"),
                                html.Small(f"{len(df2)} categories" if not df2.empty else "No data", className="text-muted")
                            ])
                        ])
                    ], width=6)
                ], className="mb-3"),
                
                # Comparison text
                dbc.Alert(comparison_text, color="info", className="mb-3"),
                
                # Visualization
                dbc.Card([
                    dbc.CardHeader("Comparison Visualization"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="comparison-chart",
                            figure=comparison_fig,
                            config={'displayModeBar': True}
                        )
                    ])
                ], className="mb-3"),
                
                # Detailed comparison
                summary_stats
            ])
            
            # Store comparison data
            comparison_data = {
                'selection1': {
                    'sources': sources1,
                    'start_date': start_date1.isoformat() if start_date1 else None,
                    'end_date': end_date1.isoformat() if end_date1 else None,
                    'languages': languages1,
                    'total': total1
                },
                'selection2': {
                    'sources': sources2,
                    'start_date': start_date2.isoformat() if start_date2 else None,
                    'end_date': end_date2.isoformat() if end_date2 else None,
                    'languages': languages2,
                    'total': total2
                },
                'viz_type': viz_type
            }
            
            return results_content, comparison_data
            
        except Exception as e:
            logging.error(f"Error executing comparison: {e}")
            return html.Div([
                dbc.Alert(f"Error executing comparison: {str(e)}", color="danger")
            ]), {}
    
    @app.callback(
        Output("comparison-chart", "figure"),
        [Input("compare-viz-type", "value")],
        [State("compare-data-store", "data")],
        prevent_initial_call=True
    )
    def update_comparison_chart(viz_type, comparison_data):
        """Update comparison chart when visualization type changes."""
        if not comparison_data:
            return dash.no_update
        
        try:
            # Re-fetch data for both selections
            sel1 = comparison_data['selection1']
            sel2 = comparison_data['selection2']
            
            start_date1 = datetime.fromisoformat(sel1['start_date']).date() if sel1['start_date'] else None
            end_date1 = datetime.fromisoformat(sel1['end_date']).date() if sel1['end_date'] else None
            start_date2 = datetime.fromisoformat(sel2['start_date']).date() if sel2['start_date'] else None
            end_date2 = datetime.fromisoformat(sel2['end_date']).date() if sel2['end_date'] else None
            
            df1 = fetch_category_data(
                sources=sel1['sources'],
                start_date=start_date1,
                end_date=end_date1,
                languages=sel1['languages']
            )
            
            df2 = fetch_category_data(
                sources=sel2['sources'],
                start_date=start_date2,
                end_date=end_date2,
                languages=sel2['languages']
            )
            
            return create_comparison_plot(df1, df2, viz_type)
            
        except Exception as e:
            logging.error(f"Error updating comparison chart: {e}")
            return dash.no_update

def create_comparison_summary_stats(df1: pd.DataFrame, df2: pd.DataFrame) -> dbc.Card:
    """
    Create detailed comparison statistics.
    
    Args:
        df1: Data for selection 1
        df2: Data for selection 2
        
    Returns:
        dbc.Card: Summary statistics card
    """
    if df1.empty and df2.empty:
        return dbc.Card([
            dbc.CardHeader("Detailed Comparison"),
            dbc.CardBody([
                html.P("No data available for comparison.", className="text-muted")
            ])
        ])
    
    # Calculate category-level statistics
    categories1 = set(df1['category'].unique()) if not df1.empty else set()
    categories2 = set(df2['category'].unique()) if not df2.empty else set()
    
    common_categories = categories1.intersection(categories2)
    unique_to_1 = categories1 - categories2
    unique_to_2 = categories2 - categories1
    
    # Calculate top categories for each selection
    top_cats_1 = df1.groupby('category')['count'].sum().sort_values(ascending=False).head(5) if not df1.empty else pd.Series()
    top_cats_2 = df2.groupby('category')['count'].sum().sort_values(ascending=False).head(5) if not df2.empty else pd.Series()
    
    return dbc.Card([
        dbc.CardHeader("Detailed Comparison"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6("Category Overlap"),
                    html.P(f"Common categories: {len(common_categories)}", className="mb-1"),
                    html.P(f"Unique to Selection 1: {len(unique_to_1)}", className="mb-1"),
                    html.P(f"Unique to Selection 2: {len(unique_to_2)}", className="mb-0")
                ], width=6),
                
                dbc.Col([
                    html.H6("Top Categories"),
                    html.Div([
                        html.P("Selection 1:", className="mb-1 fw-bold"),
                        html.Ul([html.Li(f"{cat}: {count:,}") for cat, count in top_cats_1.items()]) if not top_cats_1.empty else html.P("No data", className="text-muted"),
                        
                        html.P("Selection 2:", className="mb-1 fw-bold"),
                        html.Ul([html.Li(f"{cat}: {count:,}") for cat, count in top_cats_2.items()]) if not top_cats_2.empty else html.P("No data", className="text-muted")
                    ])
                ], width=6)
            ])
        ])
    ])

# Import or create the comparison visualization function
def create_comparison_plot(df1: pd.DataFrame, df2: pd.DataFrame, viz_type: str) -> go.Figure:
    """
    Create comparison plot based on visualization type.
    
    Args:
        df1: Data for selection 1
        df2: Data for selection 2
        viz_type: Type of visualization
        
    Returns:
        go.Figure: Comparison plot
    """
    if viz_type == 'bar':
        return create_bar_comparison(df1, df2)
    elif viz_type == 'sunburst':
        return create_sunburst_comparison(df1, df2)
    elif viz_type == 'donut':
        return create_donut_comparison(df1, df2)
    else:
        return create_bar_comparison(df1, df2)  # Default

def create_bar_comparison(df1: pd.DataFrame, df2: pd.DataFrame) -> go.Figure:
    """Create side-by-side bar chart comparison."""
    import plotly.express as px
    
    # Prepare data for comparison
    if df1.empty and df2.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No data available for comparison",
            height=400
        )
        return fig
    
    # Aggregate by category for both selections
    cats1 = df1.groupby('category')['count'].sum().reset_index() if not df1.empty else pd.DataFrame(columns=['category', 'count'])
    cats2 = df2.groupby('category')['count'].sum().reset_index() if not df2.empty else pd.DataFrame(columns=['category', 'count'])
    
    cats1['selection'] = 'Selection 1'
    cats2['selection'] = 'Selection 2'
    
    # Combine data
    combined = pd.concat([cats1, cats2], ignore_index=True)
    
    if combined.empty:
        fig = go.Figure()
        fig.update_layout(title="No data to compare", height=400)
        return fig
    
    fig = px.bar(
        combined,
        x='category',
        y='count',
        color='selection',
        barmode='group',
        title="Category Comparison",
        color_discrete_map={'Selection 1': '#1f77b4', 'Selection 2': '#ff7f0e'}
    )
    
    fig.update_layout(
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig

def create_sunburst_comparison(df1: pd.DataFrame, df2: pd.DataFrame) -> go.Figure:
    """Create side-by-side sunburst comparison."""
    # For now, just show selection 1 sunburst
    # In a full implementation, you'd create subplots
    from visualizations.sunburst import create_sunburst_chart
    
    if not df1.empty:
        return create_sunburst_chart(df1, "Selection 1 Distribution")
    elif not df2.empty:
        return create_sunburst_chart(df2, "Selection 2 Distribution")
    else:
        fig = go.Figure()
        fig.update_layout(title="No data available", height=400)
        return fig

def create_donut_comparison(df1: pd.DataFrame, df2: pd.DataFrame) -> go.Figure:
    """Create donut chart comparison."""
    import plotly.express as px
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'pie'}, {'type': 'pie'}]],
        subplot_titles=('Selection 1', 'Selection 2')
    )
    
    # Selection 1 donut
    if not df1.empty:
        cats1 = df1.groupby('category')['count'].sum().reset_index()
        fig.add_trace(
            go.Pie(
                labels=cats1['category'],
                values=cats1['count'],
                hole=0.4,
                name="Selection 1"
            ),
            row=1, col=1
        )
    
    # Selection 2 donut
    if not df2.empty:
        cats2 = df2.groupby('category')['count'].sum().reset_index()
        fig.add_trace(
            go.Pie(
                labels=cats2['category'],
                values=cats2['count'],
                hole=0.4,
                name="Selection 2"
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title="Category Distribution Comparison",
        height=500
    )
    
    return fig