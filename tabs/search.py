#!/usr/bin/env python
# coding: utf-8

"""
Search tab layout and callbacks for the cognitive warfare dashboard.
This tab provides search functionality across the database with different search modes.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

import pandas as pd
import dash
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from database.data_fetchers import fetch_search_category_data, fetch_all_text_chunks_for_search
from utils.helpers import format_chunk_row, get_unique_filename, format_number, validate_search_query
from visualizations.sunburst import create_sunburst_chart
from config import SEARCH_RESULT_LIMIT
from components.layout import create_filter_card

def create_search_tab_layout(source_options: List, min_date: datetime = None, max_date: datetime = None) -> html.Div:
    """
    Create the Search tab layout.
    
    Args:
        source_options: Source options for filters
        min_date: Minimum date for filters
        max_date: Maximum date for filters
        
    Returns:
        html.Div: Search tab layout
    """
    blue_color = "#13376f"
    
    search_tab_layout = html.Div([
        # Fixed Back to Text Chunks button
        html.Div(
            dbc.Button(
                "← Back to Text Chunks",
                id="search-back-to-chunks-button",
                color="secondary",
                style={'display': 'none'}
            ),
            style={'position': 'fixed', 'top': '10px', 'left': '10px', 'zIndex': '1000'}
        ),
        
        # Search interface
        dbc.Card([
            dbc.CardHeader(html.H5("Search Interface", className="mb-0")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Search Query:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Input(
                            id="search-query-input",
                            type="text",
                            placeholder="Enter your search query...",
                            style={'width': '100%', 'padding': '8px', 'marginBottom': '10px'}
                        )
                    ], width=12, lg=6),
                    
                    dbc.Col([
                        html.Label("Search Mode:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id="search-mode-dropdown",
                            options=[
                                {'label': 'Keyword Search', 'value': 'keyword'},
                                {'label': 'Boolean Search', 'value': 'boolean'},
                                {'label': 'Semantic Search', 'value': 'semantic'}
                            ],
                            value='keyword',
                            style={'marginBottom': '10px'}
                        )
                    ], width=12, lg=3),
                    
                    dbc.Col([
                        html.Label(" ", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dbc.Button(
                            "Search",
                            id="search-execute-button",
                            color="primary",
                            style={'width': '100%', 'backgroundColor': blue_color}
                        )
                    ], width=12, lg=3)
                ]),
                
                # Search mode help
                html.Div(id="search-mode-help", style={'marginTop': '10px'}),
                
                # Progress indicator
                html.Div(
                    id="search-progress-indicator",
                    style={'display': 'none', 'textAlign': 'center', 'margin': '20px 0'}
                )
            ])
        ], className="mb-3"),
        
        # Filters
        create_filter_card(
            id_prefix="search",
            source_options=source_options,
            min_date=min_date,
            max_date=max_date
        ),
        
        # Results container
        html.Div(id="search-results-container"),
        
        # Store for search results
        dcc.Store(id="search-results-store")
    ])
    
    return search_tab_layout

def register_search_callbacks(app):
    """Register callbacks for the Search tab."""
    
    @app.callback(
        Output("search-mode-help", "children"),
        [Input("search-mode-dropdown", "value")]
    )
    def update_search_help(search_mode):
        """Update help text based on selected search mode."""
        help_content = {
            'keyword': html.Div([
                html.P("Keyword Search: Searches for exact words or phrases in the text.", className="mb-1"),
                html.P("Example: cognitive warfare, disinformation", className="text-muted small")
            ]),
            'boolean': html.Div([
                html.P("Boolean Search: Use AND, OR, NOT operators for complex queries.", className="mb-1"),
                html.P("Example: (cognitive AND warfare) OR (information AND manipulation)", className="text-muted small")
            ]),
            'semantic': html.Div([
                html.P("Semantic Search: Finds conceptually similar content using AI.", className="mb-1"),
                html.P("Example: psychological manipulation, influence operations", className="text-muted small")
            ])
        }
        return help_content.get(search_mode, html.Div())
    
    @app.callback(
        [
            Output("search-progress-indicator", "children"),
            Output("search-progress-indicator", "style")
        ],
        [Input("search-execute-button", "n_clicks")],
        [State("search-mode-dropdown", "value")],
        prevent_initial_call=True
    )
    def show_search_progress(n_clicks, search_mode):
        """Show progress indicator during search."""
        if not n_clicks:
            return "", {'display': 'none'}
        
        progress_messages = {
            'keyword': "Searching content... (10-20 seconds)",
            'boolean': "Processing boolean query... (15-45 seconds)",
            'semantic': "Analyzing semantic similarity... (30-60 seconds)"
        }
        
        message = progress_messages.get(search_mode, "Searching...")
        
        progress_div = html.Div([
            dbc.Spinner(color="primary", size="lg"),
            html.P(message, className="mt-2")
        ])
        
        return progress_div, {'display': 'block', 'textAlign': 'center', 'margin': '20px 0'}
    
    @app.callback(
        [
            Output("search-results-container", "children"),
            Output("search-results-store", "data"),
            Output("search-progress-indicator", "style", allow_duplicate=True)
        ],
        [Input("search-execute-button", "n_clicks")],
        [
            State("search-query-input", "value"),
            State("search-mode-dropdown", "value"),
            State("search-source-dropdown", "value"),
            State("search-date-range", "start_date"),
            State("search-date-range", "end_date"),
            State("search-language-dropdown", "value")
        ],
        prevent_initial_call=True
    )
    def execute_search(n_clicks, query, search_mode, selected_sources, start_date, end_date, selected_languages):
        """Execute search and show results."""
        if not n_clicks or not query:
            return html.Div(), {}, {'display': 'none'}
        
        try:
            # Validate search query
            is_valid, error_msg = validate_search_query(query, search_mode)
            if not is_valid:
                return html.Div([
                    dbc.Alert(f"Invalid search query: {error_msg}", color="danger")
                ]), {}, {'display': 'none'}
            
            # Convert date strings to date objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            # Fetch search results for category analysis
            category_df = fetch_search_category_data(
                search_query=query,
                search_mode=search_mode,
                sources=selected_sources,
                start_date=start_date,
                end_date=end_date,
                languages=selected_languages
            )
            
            # Fetch text chunks
            chunks_df = fetch_all_text_chunks_for_search(
                search_query=query,
                search_mode=search_mode,
                sources=selected_sources,
                start_date=start_date,
                end_date=end_date,
                languages=selected_languages,
                limit=SEARCH_RESULT_LIMIT
            )
            
            if category_df.empty and chunks_df.empty:
                results_content = html.Div([
                    dbc.Alert(f"No results found for '{query}'", color="info"),
                    html.P("Try adjusting your search query or filters.", className="text-muted")
                ])
                return results_content, {}, {'display': 'none'}
            
            # Create sunburst chart from search results
            sunburst_fig = create_sunburst_chart(category_df, f"Search Results: '{query}'")
            
            # Create results summary
            total_chunks = len(chunks_df)
            total_categories = len(category_df)
            
            results_content = html.Div([
                # Results summary
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(f"{total_chunks:,}", className="text-primary mb-0"),
                                html.P("Text Chunks Found", className="mb-0")
                            ])
                        ])
                    ], width=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(f"{total_categories}", className="text-success mb-0"),
                                html.P("Taxonomy Categories", className="mb-0")
                            ])
                        ])
                    ], width=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(search_mode.title(), className="text-info mb-0"),
                                html.P("Search Mode", className="mb-0")
                            ])
                        ])
                    ], width=3),
                    
                    dbc.Col([
                        dbc.Button(
                            "View All Text Chunks",
                            id="search-view-chunks-button",
                            color="primary",
                            style={'width': '100%'}
                        )
                    ], width=3)
                ], className="mb-4"),
                
                # Sunburst chart
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dcc.Graph(
                                id="search-sunburst-chart",
                                figure=sunburst_fig,
                                config={'displayModeBar': False}
                            )
                        ], className="sunburst-container")
                    ], width=12)
                ]),
                
                # Instructions
                html.Div([
                    html.P("Click on a segment in the chart to see text chunks for that category, or use the button above to view all results.",
                           className="text-center text-muted mt-3")
                ])
            ])
            
            # Store search parameters and results
            search_data = {
                'query': query,
                'search_mode': search_mode,
                'sources': selected_sources,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'languages': selected_languages,
                'total_chunks': total_chunks
            }
            
            return results_content, search_data, {'display': 'none'}
            
        except Exception as e:
            logging.error(f"Error executing search: {e}")
            return html.Div([
                dbc.Alert(f"Error executing search: {str(e)}", color="danger")
            ]), {}, {'display': 'none'}
    
    @app.callback(
        [
            Output("search-results-container", "children", allow_duplicate=True),
            Output("search-back-to-chunks-button", "style")
        ],
        [
            Input("search-view-chunks-button", "n_clicks"),
            Input("search-sunburst-chart", "clickData")
        ],
        [State("search-results-store", "data")],
        prevent_initial_call=True
    )
    def show_search_chunks(view_all_clicks, sunburst_click, search_data):
        """Show text chunks from search results."""
        if not search_data:
            return dash.no_update, {'display': 'none'}
        
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update, {'display': 'none'}
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        try:
            # Reconstruct search parameters
            query = search_data['query']
            search_mode = search_data['search_mode']
            sources = search_data['sources']
            start_date = datetime.fromisoformat(search_data['start_date']).date() if search_data['start_date'] else None
            end_date = datetime.fromisoformat(search_data['end_date']).date() if search_data['end_date'] else None
            languages = search_data['languages']
            
            # Determine what to show based on trigger
            category_filter = None
            subcategory_filter = None
            sub_subcategory_filter = None
            
            if trigger_id == "search-sunburst-chart" and sunburst_click:
                # Extract clicked segment
                point = sunburst_click['points'][0]
                if 'currentPath' in point:
                    path_parts = point['currentPath'].split('/')
                    category_filter = path_parts[0] if len(path_parts) > 0 else None
                    subcategory_filter = path_parts[1] if len(path_parts) > 1 else None
                    sub_subcategory_filter = path_parts[2] if len(path_parts) > 2 else None
            
            # Fetch chunks
            chunks_df = fetch_all_text_chunks_for_search(
                search_query=query,
                search_mode=search_mode,
                sources=sources,
                start_date=start_date,
                end_date=end_date,
                languages=languages,
                limit=100  # Show more chunks in detail view
            )
            
            # Filter by category if sunburst was clicked
            if category_filter and not chunks_df.empty:
                if 'taxonomy_path' in chunks_df.columns:
                    chunks_df = chunks_df[chunks_df['taxonomy_path'].str.contains(category_filter, na=False)]
            
            if chunks_df.empty:
                chunks_content = [
                    html.H4(f"Search Results: '{query}'", className="selection-title"),
                    html.P("No text chunks found.", className="text-center text-muted")
                ]
            else:
                # Format chunks for display
                chunk_cards = []
                for idx, row in chunks_df.head(50).iterrows():  # Show first 50
                    chunk_cards.append(format_chunk_row(row, idx))
                
                filter_desc = f" in {category_filter}" if category_filter else ""
                chunks_content = [
                    html.H4(f"Search Results: '{query}'{filter_desc}", className="selection-title"),
                    html.P(f"Showing {min(len(chunks_df), 50)} of {len(chunks_df)} text chunks",
                           className="text-center text-muted mb-3"),
                    
                    # Download buttons
                    html.Div([
                        dbc.ButtonGroup([
                            dbc.Button("Download CSV", id="search-download-csv", color="success", size="sm"),
                            dbc.Button("Download JSON", id="search-download-json", color="info", size="sm")
                        ])
                    ], className="mb-3"),
                    
                    html.Div(chunk_cards)
                ]
            
            return chunks_content, {'display': 'block'}
            
        except Exception as e:
            logging.error(f"Error showing search chunks: {e}")
            return html.Div([
                html.P("Error loading chunks. Please try again.", className="text-danger text-center")
            ]), {'display': 'none'}
    
    @app.callback(
        [
            Output("search-results-container", "children", allow_duplicate=True),
            Output("search-back-to-chunks-button", "style", allow_duplicate=True)
        ],
        [Input("search-back-to-chunks-button", "n_clicks")],
        [State("search-results-store", "data")],
        prevent_initial_call=True
    )
    def back_to_search_results(n_clicks, search_data):
        """Return to search results view."""
        if not n_clicks or not search_data:
            return dash.no_update, dash.no_update
        
        # Recreate the search results view
        # This would need to re-fetch the category data and recreate the sunburst
        # For now, return a simple message
        return html.Div([
            html.P("Click 'Search' again to view results.", className="text-center text-muted")
        ]), {'display': 'none'}
    
    # Download callbacks
    @app.callback(
        Output("search-download-csv", "data"),
        [Input("search-download-csv", "n_clicks")],
        [State("search-results-store", "data")],
        prevent_initial_call=True
    )
    def download_search_csv(n_clicks, search_data):
        """Download search results as CSV."""
        if not n_clicks or not search_data:
            return dash.no_update
        
        try:
            # Reconstruct search and fetch data
            query = search_data['query']
            search_mode = search_data['search_mode']
            sources = search_data['sources']
            start_date = datetime.fromisoformat(search_data['start_date']).date() if search_data['start_date'] else None
            end_date = datetime.fromisoformat(search_data['end_date']).date() if search_data['end_date'] else None
            languages = search_data['languages']
            
            chunks_df = fetch_all_text_chunks_for_search(
                search_query=query,
                search_mode=search_mode,
                sources=sources,
                start_date=start_date,
                end_date=end_date,
                languages=languages,
                limit=SEARCH_RESULT_LIMIT
            )
            
            filename = get_unique_filename(f"search_results_{query[:20]}", "csv")
            return dcc.send_data_frame(chunks_df.to_csv, filename, index=False)
            
        except Exception as e:
            logging.error(f"Error downloading search CSV: {e}")
            return dash.no_update
    
    @app.callback(
        Output("search-download-json", "data"),
        [Input("search-download-json", "n_clicks")],
        [State("search-results-store", "data")],
        prevent_initial_call=True
    )
    def download_search_json(n_clicks, search_data):
        """Download search results as JSON."""
        if not n_clicks or not search_data:
            return dash.no_update
        
        try:
            # Reconstruct search and fetch data
            query = search_data['query']
            search_mode = search_data['search_mode']
            sources = search_data['sources']
            start_date = datetime.fromisoformat(search_data['start_date']).date() if search_data['start_date'] else None
            end_date = datetime.fromisoformat(search_data['end_date']).date() if search_data['end_date'] else None
            languages = search_data['languages']
            
            chunks_df = fetch_all_text_chunks_for_search(
                search_query=query,
                search_mode=search_mode,
                sources=sources,
                start_date=start_date,
                end_date=end_date,
                languages=languages,
                limit=SEARCH_RESULT_LIMIT
            )
            
            filename = get_unique_filename(f"search_results_{query[:20]}", "json")
            return dcc.send_data_frame(chunks_df.to_json, filename, orient='records', indent=2)
            
        except Exception as e:
            logging.error(f"Error downloading search JSON: {e}")
            return dash.no_update