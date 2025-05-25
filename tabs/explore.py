#!/usr/bin/env python
# coding: utf-8

"""
Explore tab layout and callbacks for the cognitive warfare dashboard.
This tab provides exploration of the data via a sunburst chart and detailed view of text chunks.
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

from database.data_fetchers import fetch_category_data, fetch_text_chunks
from components.layout import create_filter_card, create_pagination_controls, create_download_buttons
from utils.helpers import format_chunk_row, get_unique_filename
from visualizations.sunburst import create_sunburst_chart

def create_explore_tab_layout(source_options: List, min_date: datetime = None, max_date: datetime = None) -> html.Div:
    """
    Create the Explore tab layout.
    
    Args:
        source_options: Source options for filters
        min_date: Minimum date for filters
        max_date: Maximum date for filters
        
    Returns:
        html.Div: Explore tab layout
    """
    # Try to get initial data for the sunburst chart
    try:
        df_init = fetch_category_data()
        if df_init is None or df_init.empty:
            df_init = pd.DataFrame(columns=['category', 'subcategory', 'sub_subcategory', 'count'])
    except Exception as e:
        logging.error(f"Error fetching initial data for Explore tab: {e}")
        df_init = pd.DataFrame(columns=['category', 'subcategory', 'sub_subcategory', 'count'])
    
    explore_tab_layout = html.Div([
        # Filter card
        create_filter_card(
            id_prefix="explore",
            source_options=source_options,
            min_date=min_date,
            max_date=max_date
        ),
        
        # Results container
        html.Div(id="explore-results-container", children=[
            # Initial sunburst chart
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            id="explore-sunburst-chart",
                            figure=create_sunburst_chart(df_init),
                            config={'displayModeBar': False}
                        )
                    ], className="sunburst-container")
                ], width=12)
            ]),
            
            # Selection info
            html.Div(id="explore-selection-info", children=[
                html.P("Click on a segment in the sunburst chart to explore text chunks.", 
                       className="text-center text-muted", style={'marginTop': '20px'})
            ])
        ])
    ])
    
    return explore_tab_layout

def register_explore_callbacks(app):
    """Register callbacks for the Explore tab."""
    
    @app.callback(
        [
            Output("explore-sunburst-chart", "figure"),
            Output("explore-selection-info", "children")
        ],
        [Input("explore-filter-button", "n_clicks")],
        [
            State("explore-source-dropdown", "value"),
            State("explore-date-range", "start_date"),
            State("explore-date-range", "end_date"),
            State("explore-language-dropdown", "value")
        ],
        prevent_initial_call=True
    )
    def update_explore_chart(n_clicks, selected_sources, start_date, end_date, selected_languages):
        """Update the sunburst chart based on filters."""
        if not n_clicks:
            return dash.no_update, dash.no_update
        
        try:
            # Convert date strings to date objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            # Fetch filtered data
            df = fetch_category_data(
                sources=selected_sources,
                start_date=start_date,
                end_date=end_date,
                languages=selected_languages
            )
            
            # Create sunburst chart
            fig = create_sunburst_chart(df, "Cognitive Warfare Taxonomy Distribution")
            
            # Create selection info
            total_count = df['count'].sum() if not df.empty else 0
            info = html.Div([
                html.H5(f"Total Classifications: {total_count:,}", className="selection-title"),
                html.P("Click on a segment to explore the corresponding text chunks.", 
                       className="text-center text-muted")
            ])
            
            return fig, info
            
        except Exception as e:
            logging.error(f"Error updating explore chart: {e}")
            return dash.no_update, html.Div([
                html.P("Error loading data. Please try again.", className="text-danger text-center")
            ])
    
    @app.callback(
        Output("explore-results-container", "children"),
        [Input("explore-sunburst-chart", "clickData")],
        [
            State("explore-source-dropdown", "value"),
            State("explore-date-range", "start_date"),
            State("explore-date-range", "end_date"),
            State("explore-language-dropdown", "value"),
            State("explore-sunburst-chart", "figure")
        ]
    )
    def show_chunk_details(clickData, selected_sources, start_date, end_date, selected_languages, current_figure):
        """Show detailed text chunks when sunburst segment is clicked."""
        if not clickData:
            # Return to initial state
            return [
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dcc.Graph(
                                id="explore-sunburst-chart",
                                figure=current_figure,
                                config={'displayModeBar': False}
                            )
                        ], className="sunburst-container")
                    ], width=12)
                ]),
                html.Div(id="explore-selection-info", children=[
                    html.P("Click on a segment in the sunburst chart to explore text chunks.", 
                           className="text-center text-muted", style={'marginTop': '20px'})
                ])
            ]
        
        try:
            # Extract clicked data
            point = clickData['points'][0]
            label = point.get('label', '')
            
            # Parse the hierarchical path
            # The sunburst provides the full path in the id or currentPath
            if 'currentPath' in point:
                path_parts = point['currentPath'].split('/')
            else:
                path_parts = [label]
            
            # Determine category, subcategory, sub_subcategory from path
            category = path_parts[0] if len(path_parts) > 0 else None
            subcategory = path_parts[1] if len(path_parts) > 1 else None
            sub_subcategory = path_parts[2] if len(path_parts) > 2 else None
            
            # Convert date strings to date objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            # Fetch text chunks for the selected segment
            chunks_df = fetch_text_chunks(
                category=category,
                subcategory=subcategory,
                sub_subcategory=sub_subcategory,
                sources=selected_sources,
                start_date=start_date,
                end_date=end_date,
                languages=selected_languages,
                limit=50
            )
            
            # Create back button and results
            back_button = dbc.Button(
                "← Back to Sunburst",
                id="explore-back-button",
                color="secondary",
                className="mb-3"
            )
            
            if chunks_df.empty:
                results_content = [
                    back_button,
                    html.H4(f"Selected: {label}", className="selection-title"),
                    html.P("No text chunks found for this selection.", className="text-center text-muted")
                ]
            else:
                # Format chunks for display
                chunk_cards = []
                for idx, row in chunks_df.head(20).iterrows():  # Show first 20 chunks
                    chunk_cards.append(format_chunk_row(row, idx))
                
                results_content = [
                    back_button,
                    html.H4(f"Selected: {label}", className="selection-title"),
                    html.P(f"Showing {min(len(chunks_df), 20)} of {len(chunks_df)} text chunks", 
                           className="text-center text-muted mb-3"),
                    create_download_buttons("explore"),
                    html.Div(chunk_cards)
                ]
            
            return results_content
            
        except Exception as e:
            logging.error(f"Error showing chunk details: {e}")
            return [
                html.P("Error loading chunk details. Please try again.", 
                       className="text-danger text-center")
            ]
    
    @app.callback(
        Output("explore-results-container", "children", allow_duplicate=True),
        [Input("explore-back-button", "n_clicks")],
        [State("explore-sunburst-chart", "figure")],
        prevent_initial_call=True
    )
    def go_back_to_sunburst(n_clicks, current_figure):
        """Handle back button click to return to sunburst view."""
        if not n_clicks:
            return dash.no_update
        
        return [
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            id="explore-sunburst-chart",
                            figure=current_figure,
                            config={'displayModeBar': False}
                        )
                    ], className="sunburst-container")
                ], width=12)
            ]),
            html.Div(id="explore-selection-info", children=[
                html.P("Click on a segment in the sunburst chart to explore text chunks.", 
                       className="text-center text-muted", style={'marginTop': '20px'})
            ])
        ]
    
    # Download callbacks
    @app.callback(
        Output("download-dataframe-csv", "data"),
        [Input("explore-download-csv", "n_clicks")],
        [
            State("explore-source-dropdown", "value"),
            State("explore-date-range", "start_date"),
            State("explore-date-range", "end_date"),
            State("explore-language-dropdown", "value")
        ],
        prevent_initial_call=True
    )
    def download_explore_csv(n_clicks, selected_sources, start_date, end_date, selected_languages):
        """Download explore data as CSV."""
        if not n_clicks:
            return dash.no_update
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            df = fetch_category_data(
                sources=selected_sources,
                start_date=start_date,
                end_date=end_date,
                languages=selected_languages
            )
            
            filename = get_unique_filename("cognitive_warfare_explore", "csv")
            return dcc.send_data_frame(df.to_csv, filename, index=False)
            
        except Exception as e:
            logging.error(f"Error downloading CSV: {e}")
            return dash.no_update
    
    @app.callback(
        Output("download-dataframe-json", "data"),
        [Input("explore-download-json", "n_clicks")],
        [
            State("explore-source-dropdown", "value"),
            State("explore-date-range", "start_date"),
            State("explore-date-range", "end_date"),
            State("explore-language-dropdown", "value")
        ],
        prevent_initial_call=True
    )
    def download_explore_json(n_clicks, selected_sources, start_date, end_date, selected_languages):
        """Download explore data as JSON."""
        if not n_clicks:
            return dash.no_update
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            df = fetch_category_data(
                sources=selected_sources,
                start_date=start_date,
                end_date=end_date,
                languages=selected_languages
            )
            
            filename = get_unique_filename("cognitive_warfare_explore", "json")
            return dcc.send_data_frame(df.to_json, filename, orient='records', indent=2)
            
        except Exception as e:
            logging.error(f"Error downloading JSON: {e}")
            return dash.no_update