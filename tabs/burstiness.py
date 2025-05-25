#!/usr/bin/env python
# coding: utf-8

"""
Burstiness tab layout and callbacks for the cognitive warfare dashboard.
This tab provides analysis of bursts in taxonomic elements and temporal patterns.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

import pandas as pd
import numpy as np
import dash
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from dash.exceptions import PreventUpdate

from database.data_fetchers import fetch_timeline_data
from database.connection import get_engine
from components.layout import create_filter_card
# Define burstiness filter options
BURSTINESS_FILTER_OPTIONS = [
    {'label': 'Taxonomy Elements', 'value': 'taxonomy'},
    {'label': 'Keywords', 'value': 'keywords'},
    {'label': 'Named Entities', 'value': 'entities'},
    {'label': 'All Combined', 'value': 'all'}
]

def create_burstiness_tab_layout() -> html.Div:
    """
    Create the Burstiness tab layout.
    
    Returns:
        html.Div: Burstiness tab layout
    """
    
    burstiness_tab_layout = html.Div([
        # Instructions
        dbc.Alert([
            html.H5("Temporal Burst Analysis", className="mb-2"),
            html.P("Analyze temporal bursts in cognitive warfare taxonomy elements. "
                   "This analysis identifies periods of unusual activity or emphasis in different categories.")
        ], color="info", className="mb-3"),
        
        # Configuration
        dbc.Card([
            dbc.CardHeader([
                html.H5("Analysis Configuration", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Analysis Type:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="burst-analysis-type",
                            options=BURSTINESS_FILTER_OPTIONS,
                            value='taxonomy',
                            placeholder="Select analysis type..."
                        )
                    ], width=3),
                    
                    dbc.Col([
                        html.Label("Time Granularity:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="burst-time-granularity",
                            options=[
                                {'label': 'Daily', 'value': 'day'},
                                {'label': 'Weekly', 'value': 'week'},
                                {'label': 'Monthly', 'value': 'month'},
                                {'label': 'Quarterly', 'value': 'quarter'},
                                {'label': 'Yearly', 'value': 'year'}
                            ],
                            value='month',
                            placeholder="Select time granularity..."
                        )
                    ], width=3),
                    
                    dbc.Col([
                        html.Label("Burst Sensitivity:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Slider(
                            id="burst-sensitivity-slider",
                            min=0.1,
                            max=2.0,
                            step=0.1,
                            value=1.0,
                            marks={0.5: 'Low', 1.0: 'Medium', 1.5: 'High'},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], width=3),
                    
                    dbc.Col([
                        html.Label(" ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dbc.Button(
                            "Analyze Bursts",
                            id="burst-analyze-button",
                            color="primary",
                            style={'width': '100%'}
                        )
                    ], width=3)
                ])
            ])
        ], className="mb-3"),
        
        # Results container
        html.Div(id="burst-results-container"),
        
        # Store for burst data
        dcc.Store(id="burst-data-store")
    ])
    
    return burstiness_tab_layout

def register_burstiness_callbacks(app):
    """Register callbacks for the Burstiness tab."""
    
    @app.callback(
        [
            Output("burst-results-container", "children"),
            Output("burst-data-store", "data")
        ],
        [Input("burst-analyze-button", "n_clicks")],
        [
            State("burst-analysis-type", "value"),
            State("burst-time-granularity", "value"),
            State("burst-sensitivity-slider", "value")
        ],
        prevent_initial_call=True
    )
    def analyze_bursts(n_clicks, analysis_type, time_granularity, sensitivity):
        """Analyze temporal bursts in the data."""
        if not n_clicks:
            return html.Div(), {}
        
        try:
            # Fetch timeline data based on analysis type
            timeline_df = fetch_burst_timeline_data(analysis_type, time_granularity)
            
            if timeline_df.empty:
                return html.Div([
                    dbc.Alert("No temporal data found for burst analysis.", color="warning")
                ]), {}
            
            # Detect bursts
            burst_results = detect_bursts_in_timeline(timeline_df, sensitivity)
            
            if not burst_results:
                return html.Div([
                    dbc.Alert("No significant bursts detected. Try adjusting the sensitivity.", color="info")
                ]), {}
            
            # Create visualizations
            timeline_fig = create_burst_timeline_visualization(timeline_df, burst_results)
            heatmap_fig = create_burst_heatmap_visualization(timeline_df, burst_results)
            
            # Create burst summary
            burst_summary = create_burst_summary_table(burst_results)
            
            results_content = html.Div([
                # Summary statistics
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(f"{len(burst_results)}", className="text-primary mb-0"),
                                html.P("Bursts Detected", className="mb-0")
                            ])
                        ])
                    ], width=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(f"{len(timeline_df['category'].unique())}", className="text-success mb-0"),
                                html.P("Categories Analyzed", className="mb-0")
                            ])
                        ])
                    ], width=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(time_granularity.title(), className="text-info mb-0"),
                                html.P("Time Granularity", className="mb-0")
                            ])
                        ])
                    ], width=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(f"{sensitivity:.1f}", className="text-warning mb-0"),
                                html.P("Sensitivity Level", className="mb-0")
                            ])
                        ])
                    ], width=3)
                ], className="mb-4"),
                
                # Timeline visualization
                dbc.Card([
                    dbc.CardHeader("Burst Timeline"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="burst-timeline-chart",
                            figure=timeline_fig,
                            config={'displayModeBar': True}
                        )
                    ])
                ], className="mb-3"),
                
                # Heatmap visualization
                dbc.Card([
                    dbc.CardHeader("Burst Intensity Heatmap"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="burst-heatmap-chart",
                            figure=heatmap_fig,
                            config={'displayModeBar': True}
                        )
                    ])
                ], className="mb-3"),
                
                # Burst summary table
                burst_summary
            ])
            
            # Store burst data
            burst_data = {
                'analysis_type': analysis_type,
                'time_granularity': time_granularity,
                'sensitivity': sensitivity,
                'bursts': [burst.to_dict() for burst in burst_results],
                'timeline_data': timeline_df.to_dict('records')
            }
            
            return results_content, burst_data
            
        except Exception as e:
            logging.error(f"Error analyzing bursts: {e}")
            return html.Div([
                dbc.Alert(f"Error analyzing bursts: {str(e)}", color="danger")
            ]), {}

def fetch_burst_timeline_data(analysis_type: str, time_granularity: str) -> pd.DataFrame:
    """
    Fetch timeline data for burst analysis.
    
    Args:
        analysis_type: Type of analysis ('taxonomy', 'keywords', 'entities', 'all')
        time_granularity: Time granularity for analysis
        
    Returns:
        pd.DataFrame: Timeline data
    """
    try:
        engine = get_engine()
        
        # Date truncation based on granularity
        date_trunc_map = {
            'day': 'day',
            'week': 'week', 
            'month': 'month',
            'quarter': 'quarter',
            'year': 'year'
        }
        
        date_trunc = date_trunc_map.get(time_granularity, 'month')
        
        if analysis_type == 'taxonomy':
            query = f"""
            SELECT 
                DATE_TRUNC('{date_trunc}', r.publication_date) as period,
                SPLIT_PART(cc."HLTP", ' - ', 1) as category,
                COUNT(*) as count
            FROM chunk_classifications cc
            JOIN chunks c ON cc.chunk_id = c.chunk_id
            JOIN records r ON c.record_id = r.record_id
            WHERE cc.is_relevant = true 
                AND cc."HLTP" IS NOT NULL
                AND r.publication_date IS NOT NULL
                AND r.publication_date >= '2020-01-01'
            GROUP BY 
                DATE_TRUNC('{date_trunc}', r.publication_date),
                SPLIT_PART(cc."HLTP", ' - ', 1)
            ORDER BY period, category
            """
        else:
            # For other types, fall back to taxonomy for now
            query = f"""
            SELECT 
                DATE_TRUNC('{date_trunc}', r.publication_date) as period,
                SPLIT_PART(cc."HLTP", ' - ', 1) as category,
                COUNT(*) as count
            FROM chunk_classifications cc
            JOIN chunks c ON cc.chunk_id = c.chunk_id
            JOIN records r ON c.record_id = r.record_id
            WHERE cc.is_relevant = true 
                AND cc."HLTP" IS NOT NULL
                AND r.publication_date IS NOT NULL
                AND r.publication_date >= '2020-01-01'
            GROUP BY 
                DATE_TRUNC('{date_trunc}', r.publication_date),
                SPLIT_PART(cc."HLTP", ' - ', 1)
            ORDER BY period, category
            """
        
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
        
        # Convert period to datetime
        df['period'] = pd.to_datetime(df['period'])
        
        logging.info(f"Fetched timeline data: {len(df)} rows")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching timeline data: {e}")
        return pd.DataFrame(columns=['period', 'category', 'count'])

def detect_bursts_in_timeline(timeline_df: pd.DataFrame, sensitivity: float) -> List[Dict]:
    """
    Detect bursts in timeline data using a simple threshold method.
    
    Args:
        timeline_df: Timeline data
        sensitivity: Sensitivity parameter
        
    Returns:
        List[Dict]: List of detected bursts
    """
    bursts = []
    
    try:
        for category in timeline_df['category'].unique():
            cat_data = timeline_df[timeline_df['category'] == category].sort_values('period')
            
            if len(cat_data) < 3:  # Need at least 3 points for burst detection
                continue
            
            # Calculate rolling mean and std
            cat_data = cat_data.copy()
            cat_data['rolling_mean'] = cat_data['count'].rolling(window=3, center=True).mean()
            cat_data['rolling_std'] = cat_data['count'].rolling(window=3, center=True).std()
            
            # Detect bursts where count > mean + (sensitivity * std)
            threshold_multiplier = 2.0 / sensitivity  # Higher sensitivity = lower threshold
            cat_data['is_burst'] = (
                cat_data['count'] > 
                cat_data['rolling_mean'] + (threshold_multiplier * cat_data['rolling_std'])
            )
            
            # Group consecutive burst periods
            burst_periods = cat_data[cat_data['is_burst'] == True]
            
            for _, row in burst_periods.iterrows():
                burst = {
                    'category': category,
                    'period': row['period'],
                    'count': row['count'],
                    'baseline': row['rolling_mean'],
                    'intensity': (row['count'] - row['rolling_mean']) / (row['rolling_std'] + 1),
                    'duration': 1,  # Simplified - could calculate actual duration
                    'start_date': row['period'],
                    'end_date': row['period']
                }
                bursts.append(burst)
        
        # Sort bursts by intensity
        bursts.sort(key=lambda x: x['intensity'], reverse=True)
        
        logging.info(f"Detected {len(bursts)} bursts")
        return bursts
        
    except Exception as e:
        logging.error(f"Error detecting bursts: {e}")
        return []

def create_burst_timeline_visualization(timeline_df: pd.DataFrame, burst_results: List[Dict]) -> go.Figure:
    """Create timeline visualization showing bursts."""
    
    fig = go.Figure()
    
    # Add line for each category
    for category in timeline_df['category'].unique():
        cat_data = timeline_df[timeline_df['category'] == category].sort_values('period')
        
        fig.add_trace(go.Scatter(
            x=cat_data['period'],
            y=cat_data['count'],
            mode='lines+markers',
            name=category,
            line=dict(width=2),
            hovertemplate=f'<b>{category}</b><br>Date: %{{x}}<br>Count: %{{y:,}}<extra></extra>'
        ))
    
    # Add burst markers
    burst_periods = [burst['period'] for burst in burst_results]
    burst_counts = [burst['count'] for burst in burst_results]
    burst_categories = [burst['category'] for burst in burst_results]
    
    if burst_periods:
        fig.add_trace(go.Scatter(
            x=burst_periods,
            y=burst_counts,
            mode='markers',
            name='Detected Bursts',
            marker=dict(
                size=15,
                color='red',
                symbol='star',
                line=dict(width=2, color='darkred')
            ),
            hovertemplate='<b>BURST</b><br>Category: %{text}<br>Date: %{x}<br>Count: %{y:,}<extra></extra>',
            text=burst_categories
        ))
    
    fig.update_layout(
        title="Temporal Burst Analysis",
        xaxis_title="Time Period",
        yaxis_title="Count",
        height=500,
        hovermode='x unified'
    )
    
    return fig

def create_burst_heatmap_visualization(timeline_df: pd.DataFrame, burst_results: List[Dict]) -> go.Figure:
    """Create heatmap showing burst intensity over time."""
    
    # Create pivot table for heatmap
    pivot_df = timeline_df.pivot(index='category', columns='period', values='count').fillna(0)
    
    # Create burst intensity matrix
    burst_intensity = pivot_df.copy()
    burst_intensity[:] = 0  # Initialize with zeros
    
    # Fill in burst intensities
    for burst in burst_results:
        category = burst['category']
        period = burst['period']
        intensity = burst['intensity']
        
        if category in burst_intensity.index:
            try:
                burst_intensity.loc[category, period] = intensity
            except KeyError:
                continue  # Period not in columns
    
    fig = go.Figure(data=go.Heatmap(
        z=burst_intensity.values,
        x=[col.strftime('%Y-%m') for col in burst_intensity.columns],
        y=burst_intensity.index,
        colorscale='Reds',
        hovertemplate='<b>%{y}</b><br>Period: %{x}<br>Burst Intensity: %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Burst Intensity Heatmap",
        xaxis_title="Time Period",
        yaxis_title="Categories",
        height=400
    )
    
    return fig

def create_burst_summary_table(burst_results: List[Dict]) -> dbc.Card:
    """Create summary table of detected bursts."""
    
    if not burst_results:
        return dbc.Card([
            dbc.CardHeader("Burst Summary"),
            dbc.CardBody([
                html.P("No bursts detected.", className="text-muted")
            ])
        ])
    
    # Create table rows
    table_rows = []
    for i, burst in enumerate(burst_results[:10]):  # Show top 10 bursts
        row = html.Tr([
            html.Td(f"{i+1}"),
            html.Td(burst['category']),
            html.Td(burst['period'].strftime('%Y-%m-%d')),
            html.Td(f"{burst['count']:,}"),
            html.Td(f"{burst['baseline']:.1f}" if burst['baseline'] else "N/A"),
            html.Td(f"{burst['intensity']:.2f}"),
        ])
        table_rows.append(row)
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Rank"),
                html.Th("Category"),
                html.Th("Period"),
                html.Th("Count"),
                html.Th("Baseline"),
                html.Th("Intensity")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, bordered=True, hover=True, size="sm")
    
    return dbc.Card([
        dbc.CardHeader("Top Detected Bursts"),
        dbc.CardBody([table])
    ])

# Placeholder burst detection utilities
def detect_bursts(data: pd.Series, sensitivity: float = 1.0) -> List[Dict]:
    """Placeholder for burst detection algorithm."""
    return []

def calculate_burst_strength(data: pd.Series) -> float:
    """Placeholder for burst strength calculation."""
    return 0.0