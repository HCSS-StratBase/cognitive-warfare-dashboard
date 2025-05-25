#!/usr/bin/env python
# coding: utf-8

"""
Sources tab layout and callbacks for the cognitive warfare dashboard.
This tab provides analysis of data sources and their characteristics.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from config import DEFAULT_START_DATE, DEFAULT_END_DATE
from database.data_fetchers import fetch_all_sources
from components.layout import create_filter_card
try:
    from database.data_fetchers_sources import (
        fetch_corpus_stats,
        fetch_source_distribution,
        fetch_language_distribution,
        fetch_temporal_distribution,
        fetch_taxonomy_by_source
    )
except ImportError:
    # Define placeholder functions if import fails
    def fetch_corpus_stats(*args, **kwargs):
        return {}
    def fetch_source_distribution(*args, **kwargs):
        return pd.DataFrame()
    def fetch_language_distribution(*args, **kwargs):
        return pd.DataFrame()
    def fetch_temporal_distribution(*args, **kwargs):
        return pd.DataFrame()
    def fetch_taxonomy_by_source(*args, **kwargs):
        return pd.DataFrame()

def create_sources_tab_layout(source_options: List, min_date: datetime = None, max_date: datetime = None) -> html.Div:
    """
    Create the Sources tab layout.
    
    Args:
        source_options: Source options for filters
        min_date: Minimum date for filters
        max_date: Maximum date for filters
        
    Returns:
        html.Div: Sources tab layout
    """
    if min_date is None:
        min_date = DEFAULT_START_DATE
    if max_date is None:
        max_date = DEFAULT_END_DATE
    
    sources_tab_layout = html.Div([
        # Instructions
        dbc.Alert([
            html.H5("Source Analysis", className="mb-2"),
            html.P("Analyze the distribution and characteristics of data sources in the cognitive warfare dataset. "
                   "Explore source types, languages, temporal patterns, and taxonomy coverage.")
        ], color="info", className="mb-3"),
        
        # Filter card
        create_filter_card(
            id_prefix="sources",
            source_options=source_options,
            min_date=min_date,
            max_date=max_date
        ),
        
        # Analysis type selector
        dbc.Card([
            dbc.CardHeader([
                html.H5("Analysis Type", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(
                            id="sources-analysis-type",
                            options=[
                                {'label': 'Source Distribution', 'value': 'distribution'},
                                {'label': 'Language Analysis', 'value': 'language'},
                                {'label': 'Temporal Patterns', 'value': 'temporal'},
                                {'label': 'Taxonomy Coverage', 'value': 'taxonomy'},
                                {'label': 'Corpus Statistics', 'value': 'stats'}
                            ],
                            value='distribution',
                            placeholder="Select analysis type..."
                        )
                    ], width=9),
                    
                    dbc.Col([
                        dbc.Button(
                            "Analyze Sources",
                            id="sources-analyze-button",
                            color="primary",
                            style={'width': '100%'}
                        )
                    ], width=3)
                ])
            ])
        ], className="mb-3"),
        
        # Results container
        html.Div(id="sources-results-container"),
        
        # Store for sources data
        dcc.Store(id="sources-data-store")
    ])
    
    return sources_tab_layout

def register_sources_callbacks(app):
    """Register callbacks for the Sources tab."""
    
    @app.callback(
        [
            Output("sources-results-container", "children"),
            Output("sources-data-store", "data")
        ],
        [Input("sources-analyze-button", "n_clicks")],
        [
            State("sources-source-dropdown", "value"),
            State("sources-date-range", "start_date"),
            State("sources-date-range", "end_date"),
            State("sources-language-dropdown", "value"),
            State("sources-analysis-type", "value")
        ],
        prevent_initial_call=True
    )
    def analyze_sources(n_clicks, selected_sources, start_date, end_date, selected_languages, analysis_type):
        """Analyze sources based on selected type."""
        if not n_clicks:
            return html.Div(), {}
        
        try:
            # Convert date strings to date objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            if analysis_type == 'distribution':
                results, data = analyze_source_distribution(selected_sources, start_date, end_date, selected_languages)
            elif analysis_type == 'language':
                results, data = analyze_language_distribution(selected_sources, start_date, end_date, selected_languages)
            elif analysis_type == 'temporal':
                results, data = analyze_temporal_patterns(selected_sources, start_date, end_date, selected_languages)
            elif analysis_type == 'taxonomy':
                results, data = analyze_taxonomy_coverage(selected_sources, start_date, end_date, selected_languages)
            elif analysis_type == 'stats':
                results, data = analyze_corpus_statistics(selected_sources, start_date, end_date, selected_languages)
            else:
                results = html.Div([
                    dbc.Alert("Invalid analysis type selected.", color="danger")
                ])
                data = {}
            
            return results, data
            
        except Exception as e:
            logging.error(f"Error analyzing sources: {e}")
            return html.Div([
                dbc.Alert(f"Error analyzing sources: {str(e)}", color="danger")
            ]), {}

def analyze_source_distribution(sources: List[str], start_date, end_date, languages: List[str]) -> tuple:
    """Analyze distribution of sources."""
    try:
        # Fetch source distribution data
        source_data = fetch_source_distribution(sources, start_date, end_date, languages)
        
        if source_data.empty:
            return html.Div([
                dbc.Alert("No source data found for the selected filters.", color="warning")
            ]), {}
        
        # Create pie chart
        fig_pie = px.pie(
            source_data,
            values='count',
            names='source',
            title="Source Distribution"
        )
        
        # Create bar chart
        fig_bar = px.bar(
            source_data.sort_values('count', ascending=False),
            x='source',
            y='count',
            title="Records by Source",
            labels={'count': 'Number of Records', 'source': 'Source'}
        )
        
        # Create summary table
        summary_table = create_source_summary_table(source_data)
        
        results = html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Source Distribution (Pie Chart)"),
                        dbc.CardBody([
                            dcc.Graph(figure=fig_pie)
                        ])
                    ])
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Records by Source (Bar Chart)"),
                        dbc.CardBody([
                            dcc.Graph(figure=fig_bar)
                        ])
                    ])
                ], width=6)
            ], className="mb-3"),
            
            summary_table
        ])
        
        return results, source_data.to_dict('records')
        
    except Exception as e:
        logging.error(f"Error in source distribution analysis: {e}")
        return html.Div([
            dbc.Alert(f"Error analyzing source distribution: {str(e)}", color="danger")
        ]), {}

def analyze_language_distribution(sources: List[str], start_date, end_date, languages: List[str]) -> tuple:
    """Analyze distribution of languages."""
    try:
        # Fetch language distribution data
        lang_data = fetch_language_distribution(sources, start_date, end_date, languages)
        
        if lang_data.empty:
            return html.Div([
                dbc.Alert("No language data found for the selected filters.", color="warning")
            ]), {}
        
        # Create visualizations
        fig_pie = px.pie(
            lang_data,
            values='count',
            names='language',
            title="Language Distribution"
        )
        
        fig_bar = px.bar(
            lang_data.sort_values('count', ascending=False),
            x='language',
            y='count',
            title="Records by Language",
            labels={'count': 'Number of Records', 'language': 'Language'}
        )
        
        # Language summary
        total_records = lang_data['count'].sum()
        lang_summary = html.Div([
            html.H6("Language Summary"),
            html.P(f"Total records: {total_records:,}"),
            html.P(f"Languages represented: {len(lang_data)}"),
            html.P(f"Most common: {lang_data.loc[lang_data['count'].idxmax(), 'language']} ({lang_data['count'].max():,} records)")
        ])
        
        results = html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Language Distribution"),
                        dbc.CardBody([
                            dcc.Graph(figure=fig_pie)
                        ])
                    ])
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Records by Language"),
                        dbc.CardBody([
                            dcc.Graph(figure=fig_bar)
                        ])
                    ])
                ], width=6)
            ], className="mb-3"),
            
            dbc.Card([
                dbc.CardHeader("Language Statistics"),
                dbc.CardBody([lang_summary])
            ])
        ])
        
        return results, lang_data.to_dict('records')
        
    except Exception as e:
        logging.error(f"Error in language analysis: {e}")
        return html.Div([
            dbc.Alert(f"Error analyzing languages: {str(e)}", color="danger")
        ]), {}

def analyze_temporal_patterns(sources: List[str], start_date, end_date, languages: List[str]) -> tuple:
    """Analyze temporal patterns in sources."""
    try:
        # Fetch temporal distribution data
        temporal_data = fetch_temporal_distribution(sources, start_date, end_date, languages)
        
        if temporal_data.empty:
            return html.Div([
                dbc.Alert("No temporal data found for the selected filters.", color="warning")
            ]), {}
        
        # Create timeline chart
        fig_timeline = px.line(
            temporal_data,
            x='period',
            y='count',
            color='source',
            title="Temporal Distribution by Source",
            labels={'count': 'Number of Records', 'period': 'Time Period'}
        )
        
        # Create heatmap by year and source
        if 'year' in temporal_data.columns:
            heatmap_data = temporal_data.pivot(index='source', columns='year', values='count').fillna(0)
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Blues'
            ))
            
            fig_heatmap.update_layout(
                title="Source Activity Heatmap by Year",
                xaxis_title="Year",
                yaxis_title="Source"
            )
        else:
            fig_heatmap = go.Figure()
            fig_heatmap.update_layout(title="Insufficient data for heatmap")
        
        results = html.Div([
            dbc.Card([
                dbc.CardHeader("Temporal Patterns"),
                dbc.CardBody([
                    dcc.Graph(figure=fig_timeline)
                ])
            ], className="mb-3"),
            
            dbc.Card([
                dbc.CardHeader("Activity Heatmap"),
                dbc.CardBody([
                    dcc.Graph(figure=fig_heatmap)
                ])
            ])
        ])
        
        return results, temporal_data.to_dict('records')
        
    except Exception as e:
        logging.error(f"Error in temporal analysis: {e}")
        return html.Div([
            dbc.Alert(f"Error analyzing temporal patterns: {str(e)}", color="danger")
        ]), {}

def analyze_taxonomy_coverage(sources: List[str], start_date, end_date, languages: List[str]) -> tuple:
    """Analyze taxonomy coverage by sources."""
    try:
        # Fetch taxonomy coverage data
        taxonomy_data = fetch_taxonomy_by_source(sources, start_date, end_date, languages)
        
        if taxonomy_data.empty:
            return html.Div([
                dbc.Alert("No taxonomy data found for the selected filters.", color="warning")
            ]), {}
        
        # Create stacked bar chart
        fig_stacked = px.bar(
            taxonomy_data,
            x='source',
            y='count',
            color='category',
            title="Taxonomy Coverage by Source",
            labels={'count': 'Number of Classifications', 'source': 'Source'}
        )
        
        # Create heatmap
        heatmap_data = taxonomy_data.pivot(index='source', columns='category', values='count').fillna(0)
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Viridis'
        ))
        
        fig_heatmap.update_layout(
            title="Taxonomy Coverage Heatmap",
            xaxis_title="Cognitive Warfare Category",
            yaxis_title="Source"
        )
        
        results = html.Div([
            dbc.Card([
                dbc.CardHeader("Taxonomy Coverage by Source"),
                dbc.CardBody([
                    dcc.Graph(figure=fig_stacked)
                ])
            ], className="mb-3"),
            
            dbc.Card([
                dbc.CardHeader("Coverage Heatmap"),
                dbc.CardBody([
                    dcc.Graph(figure=fig_heatmap)
                ])
            ])
        ])
        
        return results, taxonomy_data.to_dict('records')
        
    except Exception as e:
        logging.error(f"Error in taxonomy coverage analysis: {e}")
        return html.Div([
            dbc.Alert(f"Error analyzing taxonomy coverage: {str(e)}", color="danger")
        ]), {}

def analyze_corpus_statistics(sources: List[str], start_date, end_date, languages: List[str]) -> tuple:
    """Analyze overall corpus statistics."""
    try:
        # Fetch corpus statistics
        stats = fetch_corpus_stats(sources, start_date, end_date, languages)
        
        if not stats:
            return html.Div([
                dbc.Alert("No statistics available for the selected filters.", color="warning")
            ]), {}
        
        # Create statistics cards
        stats_cards = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{stats.get('total_records', 0):,}", className="text-primary mb-0"),
                        html.P("Total Records", className="mb-0")
                    ])
                ])
            ], width=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{stats.get('total_chunks', 0):,}", className="text-success mb-0"),
                        html.P("Total Chunks", className="mb-0")
                    ])
                ])
            ], width=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{stats.get('total_classifications', 0):,}", className="text-info mb-0"),
                        html.P("Classifications", className="mb-0")
                    ])
                ])
            ], width=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{stats.get('avg_chunk_length', 0):.0f}", className="text-warning mb-0"),
                        html.P("Avg Chunk Length", className="mb-0")
                    ])
                ])
            ], width=3)
        ])
        
        # Create detailed statistics table
        detailed_stats = html.Div([
            html.H6("Detailed Statistics"),
            html.Ul([
                html.Li(f"Date range: {stats.get('date_range', 'N/A')}"),
                html.Li(f"Unique sources: {stats.get('unique_sources', 0)}"),
                html.Li(f"Languages: {stats.get('unique_languages', 0)}"),
                html.Li(f"Classification rate: {stats.get('classification_rate', 0):.1%}"),
                html.Li(f"Average confidence: {stats.get('avg_confidence', 0):.2f}")
            ])
        ])
        
        results = html.Div([
            stats_cards,
            html.Hr(),
            detailed_stats
        ])
        
        return results, stats
        
    except Exception as e:
        logging.error(f"Error in corpus statistics analysis: {e}")
        return html.Div([
            dbc.Alert(f"Error analyzing corpus statistics: {str(e)}", color="danger")
        ]), {}

def create_source_summary_table(source_data: pd.DataFrame) -> dbc.Card:
    """Create summary table for source data."""
    
    # Calculate summary statistics
    total_records = source_data['count'].sum()
    source_data['percentage'] = (source_data['count'] / total_records * 100).round(2)
    
    # Create table rows
    table_rows = []
    for _, row in source_data.iterrows():
        table_row = html.Tr([
            html.Td(row['source']),
            html.Td(f"{row['count']:,}"),
            html.Td(f"{row['percentage']:.2f}%")
        ])
        table_rows.append(table_row)
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Source"),
                html.Th("Records"),
                html.Th("Percentage")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, bordered=True, hover=True, size="sm")
    
    return dbc.Card([
        dbc.CardHeader("Source Summary"),
        dbc.CardBody([table])
    ])

# Placeholder data fetchers (to be implemented)
def fetch_source_distribution(sources, start_date, end_date, languages):
    """Fetch source distribution data."""
    from database.connection import get_engine
    from sqlalchemy import text
    
    engine = get_engine()
    query = """
    SELECT 
        r.original_source as source,
        COUNT(*) as count
    FROM records r
    WHERE 1=1
    """
    
    params = {}
    if sources and 'ALL' not in sources:
        placeholders = ','.join([f':source_{i}' for i in range(len(sources))])
        query += f" AND r.original_source IN ({placeholders})"
        for i, source in enumerate(sources):
            params[f'source_{i}'] = source
    
    if start_date:
        query += " AND r.publication_date >= :start_date"
        params['start_date'] = start_date
        
    if end_date:
        query += " AND r.publication_date <= :end_date"
        params['end_date'] = end_date
    
    query += " GROUP BY r.original_source ORDER BY count DESC"
    
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), conn, params=params)

def fetch_language_distribution(sources, start_date, end_date, languages):
    """Fetch language distribution data."""
    from database.connection import get_engine
    from sqlalchemy import text
    
    engine = get_engine()
    query = """
    SELECT 
        COALESCE(r.language, 'Unknown') as language,
        COUNT(*) as count
    FROM records r
    WHERE 1=1
    """
    
    params = {}
    if sources and 'ALL' not in sources:
        placeholders = ','.join([f':source_{i}' for i in range(len(sources))])
        query += f" AND r.original_source IN ({placeholders})"
        for i, source in enumerate(sources):
            params[f'source_{i}'] = source
    
    query += " GROUP BY r.language ORDER BY count DESC"
    
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), conn, params=params)

def fetch_temporal_distribution(sources, start_date, end_date, languages):
    """Fetch temporal distribution data."""
    from database.connection import get_engine
    from sqlalchemy import text
    
    engine = get_engine()
    query = """
    SELECT 
        DATE_TRUNC('month', r.publication_date) as period,
        EXTRACT(year FROM r.publication_date) as year,
        r.original_source as source,
        COUNT(*) as count
    FROM records r
    WHERE r.publication_date IS NOT NULL
    """
    
    params = {}
    if sources and 'ALL' not in sources:
        placeholders = ','.join([f':source_{i}' for i in range(len(sources))])
        query += f" AND r.original_source IN ({placeholders})"
        for i, source in enumerate(sources):
            params[f'source_{i}'] = source
    
    query += " GROUP BY DATE_TRUNC('month', r.publication_date), EXTRACT(year FROM r.publication_date), r.original_source ORDER BY period"
    
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), conn, params=params)

def fetch_taxonomy_by_source(sources, start_date, end_date, languages):
    """Fetch taxonomy coverage by source."""
    from database.connection import get_engine
    from sqlalchemy import text
    
    engine = get_engine()
    query = """
    SELECT 
        r.original_source as source,
        SPLIT_PART(cc.HLTP, ' - ', 1) as category,
        COUNT(*) as count
    FROM chunk_classifications cc
    JOIN chunks c ON cc.chunk_id = c.chunk_id
    JOIN records r ON c.record_id = r.record_id
    WHERE cc.is_relevant = true AND cc.HLTP IS NOT NULL
    """
    
    params = {}
    if sources and 'ALL' not in sources:
        placeholders = ','.join([f':source_{i}' for i in range(len(sources))])
        query += f" AND r.original_source IN ({placeholders})"
        for i, source in enumerate(sources):
            params[f'source_{i}'] = source
    
    query += " GROUP BY r.original_source, SPLIT_PART(cc.HLTP, ' - ', 1) ORDER BY source, category"
    
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), conn, params=params)

def fetch_corpus_stats(sources, start_date, end_date, languages):
    """Fetch corpus statistics."""
    from database.connection import get_engine
    from sqlalchemy import text
    
    engine = get_engine()
    
    # Get basic counts
    stats_query = """
    SELECT 
        COUNT(DISTINCT r.record_id) as total_records,
        COUNT(DISTINCT c.chunk_id) as total_chunks,
        COUNT(DISTINCT cc.id) as total_classifications,
        AVG(LENGTH(c.chunk_text)) as avg_chunk_length,
        COUNT(DISTINCT r.original_source) as unique_sources,
        COUNT(DISTINCT r.language) as unique_languages,
        AVG(cc.confidence) as avg_confidence
    FROM records r
    LEFT JOIN chunks c ON r.record_id = c.record_id
    LEFT JOIN chunk_classifications cc ON c.chunk_id = cc.chunk_id AND cc.is_relevant = true
    WHERE 1=1
    """
    
    params = {}
    if sources and 'ALL' not in sources:
        placeholders = ','.join([f':source_{i}' for i in range(len(sources))])
        stats_query += f" AND r.original_source IN ({placeholders})"
        for i, source in enumerate(sources):
            params[f'source_{i}'] = source
    
    with engine.connect() as conn:
        result = conn.execute(text(stats_query), params).fetchone()
        
        stats = {
            'total_records': result[0] or 0,
            'total_chunks': result[1] or 0,
            'total_classifications': result[2] or 0,
            'avg_chunk_length': result[3] or 0,
            'unique_sources': result[4] or 0,
            'unique_languages': result[5] or 0,
            'avg_confidence': result[6] or 0,
            'classification_rate': (result[2] or 0) / max(result[1] or 1, 1)
        }
        
        return stats