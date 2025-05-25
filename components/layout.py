#!/usr/bin/env python
# coding: utf-8

"""
Layout components for the cognitive warfare dashboard.
Provides functions to create reusable UI components.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, date

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from config import APP_VERSION, LANGUAGE_OPTIONS, SOURCE_TYPE_OPTIONS, REPORT_PDF_URL

def create_header() -> html.Div:
    """
    Create the dashboard header with title and buttons.
    
    Returns:
        html.Div: Header component
    """
    blue_color = "#13376f"
    
    return html.Div([
        html.Div([
            # Left side - logos and title exactly like RUW
            html.Div([
                html.Img(
                    src="/static/HCSS_Beeldmerk_Blauw_RGB.svg",
                    style={'height': '40px', 'marginRight': '15px'}
                ),
                html.Img(
                    src="/static/rubase_logo_4.svg", 
                    style={'height': '40px', 'marginRight': '15px'}
                ),
                html.H2("Cognitive Warfare Data Analysis Dashboard", 
                       style={'margin': 0, 'color': 'white'})
            ], style={'flex': '1', 'display': 'flex', 'alignItems': 'center'}),
            
            # Right side - buttons
            html.Div([
                dbc.Button(
                    "About", 
                    id="open-about-main", 
                    className="about-button",
                    style={'marginRight': '10px', 'backgroundColor': blue_color}
                ),
                dbc.Button(
                    "Clear Cache",
                    id="clear-cache-button", 
                    className="about-button",
                    style={'backgroundColor': blue_color}
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'display': 'flex', 
            'alignItems': 'center', 
            'justifyContent': 'space-between',
            'width': '100%'
        })
    ], className="app-header")

def create_about_modal() -> dbc.Modal:
    """
    Create the about modal dialog.
    
    Returns:
        dbc.Modal: About modal component
    """
    return dbc.Modal([
        dbc.ModalHeader("About Cognitive Warfare Dashboard"),
        dbc.ModalBody([
            html.H5("Dashboard Overview"),
            html.P([
                "This dashboard provides comprehensive analysis tools for cognitive warfare research data. ",
                "Explore taxonomy classifications, search through content, compare different data slices, ",
                "analyze temporal patterns, and examine source distributions."
            ]),
            
            html.H5("Features"),
            html.Ul([
                html.Li("Interactive sunburst visualizations of cognitive warfare taxonomy"),
                html.Li("Advanced search with keyword, boolean, and semantic modes"),
                html.Li("Comparative analysis between different data subsets"),
                html.Li("Burst detection for identifying temporal patterns"),
                html.Li("Source analysis and statistics")
            ]),
            
            html.H5("Data Sources"),
            html.P([
                "The dashboard analyzes data from multiple sources including academic papers, ",
                "parliamentary proceedings, research libraries, and patent databases, classified ",
                "according to a comprehensive cognitive warfare taxonomy."
            ]),
            
            html.Hr(),
            html.P([
                f"Version: {APP_VERSION} | ",
                html.A("Documentation", href=REPORT_PDF_URL, target="_blank")
            ], style={'fontSize': '0.9rem', 'color': '#666'})
        ]),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-about", className="ml-auto")
        ),
    ], id="about-modal", size="lg")

def create_filter_card(
    id_prefix: str,
    source_options: List[Dict],
    min_date: date = None,
    max_date: date = None,
    show_language_filter: bool = True,
    show_additional_filters: bool = False
) -> dbc.Card:
    """
    Create a filter card with common filters.
    
    Args:
        id_prefix: Prefix for component IDs
        source_options: Source options for dropdown
        min_date: Minimum date for date picker
        max_date: Maximum date for date picker
        show_language_filter: Whether to show language filter
        show_additional_filters: Whether to show additional filters
        
    Returns:
        dbc.Card: Filter card component
    """
    filters = []
    
    # Source filter
    filters.append(
        dbc.Col([
            html.Label("Sources:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id=f"{id_prefix}-source-dropdown",
                options=source_options,
                value=['ALL'],
                multi=True,
                placeholder="Select sources..."
            )
        ], width=12, lg=3)
    )
    
    # Date range filter
    filters.append(
        dbc.Col([
            html.Label("Date Range:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.DatePickerRange(
                id=f"{id_prefix}-date-range",
                start_date=min_date,
                end_date=max_date,
                display_format='YYYY-MM-DD',
                style={'width': '100%'}
            )
        ], width=12, lg=3)
    )
    
    # Language filter
    if show_language_filter:
        filters.append(
            dbc.Col([
                html.Label("Languages:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id=f"{id_prefix}-language-dropdown",
                    options=LANGUAGE_OPTIONS,
                    value=['ALL'],
                    multi=True,
                    placeholder="Select languages..."
                )
            ], width=12, lg=3)
        )
    
    # Filter button
    filters.append(
        dbc.Col([
            html.Label(" ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dbc.Button(
                "Apply Filters", 
                id=f"{id_prefix}-filter-button",
                color="primary",
                style={'width': '100%'}
            )
        ], width=12, lg=3)
    )
    
    return dbc.Card([
        dbc.CardHeader(html.H5("Filters", className="mb-0")),
        dbc.CardBody([
            dbc.Row(filters)
        ])
    ], className="filter-card mb-3")

def create_pagination_controls(
    id_prefix: str,
    current_page: int = 1,
    total_pages: int = 1,
    items_per_page: int = 50
) -> html.Div:
    """
    Create pagination controls.
    
    Args:
        id_prefix: Prefix for component IDs
        current_page: Current page number
        total_pages: Total number of pages
        items_per_page: Items per page
        
    Returns:
        html.Div: Pagination controls
    """
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("Items per page:", style={'marginRight': '10px'}),
                dcc.Dropdown(
                    id=f"{id_prefix}-items-per-page",
                    options=[
                        {'label': '25', 'value': 25},
                        {'label': '50', 'value': 50},
                        {'label': '100', 'value': 100},
                        {'label': '200', 'value': 200}
                    ],
                    value=items_per_page,
                    style={'width': '100px', 'display': 'inline-block'}
                )
            ], width="auto"),
            
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("« First", id=f"{id_prefix}-first-page", size="sm"),
                    dbc.Button("‹ Prev", id=f"{id_prefix}-prev-page", size="sm"),
                    html.Span(
                        f"Page {current_page} of {total_pages}",
                        style={'padding': '0 15px', 'lineHeight': '31px'}
                    ),
                    dbc.Button("Next ›", id=f"{id_prefix}-next-page", size="sm"),
                    dbc.Button("Last »", id=f"{id_prefix}-last-page", size="sm")
                ])
            ], width="auto")
        ], justify="between", align="center")
    ], style={'margin': '20px 0'})

def create_download_buttons(id_prefix: str) -> html.Div:
    """
    Create download buttons for data export.
    
    Args:
        id_prefix: Prefix for component IDs
        
    Returns:
        html.Div: Download buttons
    """
    return html.Div([
        dbc.ButtonGroup([
            dbc.Button(
                [html.I(className="fas fa-download"), " CSV"],
                id=f"{id_prefix}-download-csv",
                color="success",
                size="sm"
            ),
            dbc.Button(
                [html.I(className="fas fa-download"), " JSON"],
                id=f"{id_prefix}-download-json",
                color="info",
                size="sm"
            )
        ])
    ], style={'marginBottom': '10px'})

def create_stats_summary(
    total_chunks: int,
    total_records: int,
    date_range: str,
    selected_filters: Dict
) -> dbc.Card:
    """
    Create a summary statistics card.
    
    Args:
        total_chunks: Total number of chunks
        total_records: Total number of records
        date_range: Date range string
        selected_filters: Dictionary of selected filters
        
    Returns:
        dbc.Card: Stats summary card
    """
    return dbc.Card([
        dbc.CardHeader(html.H5("Selection Summary", className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4(f"{total_chunks:,}", className="text-primary mb-0"),
                    html.P("Text Chunks", className="mb-0")
                ], width=3),
                
                dbc.Col([
                    html.H4(f"{total_records:,}", className="text-success mb-0"),
                    html.P("Documents", className="mb-0")
                ], width=3),
                
                dbc.Col([
                    html.H6(date_range, className="text-info mb-0"),
                    html.P("Date Range", className="mb-0")
                ], width=3),
                
                dbc.Col([
                    html.H6(f"{len(selected_filters.get('sources', []))} sources", className="text-warning mb-0"),
                    html.P("Selected", className="mb-0")
                ], width=3)
            ])
        ])
    ], className="mb-3")