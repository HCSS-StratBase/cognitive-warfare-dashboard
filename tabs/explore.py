#!/usr/bin/env python
# coding: utf-8

"""
Explore Tab for Cognitive Warfare Dashboard
---------------------------------------------
This tab provides an interactive sunburst visualization for exploring
the cognitive warfare taxonomy with drill-down capabilities exactly like RUW app.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from database.data_fetchers import (
    fetch_category_data,
    fetch_text_chunks_for_explore,
    fetch_chunk_text_for_chunk_ids
)
from components.layout import create_filter_card, create_pagination_controls
from utils.helpers import validate_dates, format_chunk_card
from visualizations.sunburst import create_sunburst_chart
from utils.cache import get_cached_or_fetch

logger = logging.getLogger(__name__)


def create_explore_tab_layout(source_options: List[Dict], min_date: str, max_date: str) -> html.Div:
    """
    Create the layout for the Explore tab exactly matching RUW app structure.
    
    Args:
        source_options: List of source options for dropdown
        min_date: Minimum date for date picker
        max_date: Maximum date for date picker
        
    Returns:
        html.Div: Complete explore tab layout
    """
    return html.Div([
        # Filter card exactly like RUW
        dbc.Row([
            dbc.Col([
                create_filter_card(
                    "explore",
                    source_options,
                    min_date,
                    max_date
                )
            ], width=12)
        ], className="mb-3"),
        
        # Main content area - exactly matching RUW structure
        html.Div(id="explore-content", children=[
            # Initial sunburst visualization with exact RUW styling
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Cognitive Warfare Taxonomy Distribution", className="mb-0")
                        ]),
                        dbc.CardBody([
                            html.Div([
                                dcc.Graph(
                                    id="sunburst-chart",
                                    config={'displayModeBar': False},
                                    style={'height': '700px'}
                                )
                            ], className="sunburst-container")
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ])
        ]),
        
        # Download components exactly like RUW
        dcc.Download(id="download-dataframe-csv"),
        dcc.Download(id="download-dataframe-json"),
        
        # Hidden storage for clicked data
        html.Div(id="sunburst-clicked-data", style={"display": "none"}),
        
        # Loading component
        dcc.Loading(
            id="explore-loading",
            type="default",
            children=html.Div(id="explore-loading-output")
        )
    ])


def register_explore_callbacks(app: dash.Dash) -> None:
    """
    Register all callbacks for the Explore tab exactly matching RUW app.
    
    Args:
        app: Dash application instance
    """
    
    @app.callback(
        Output("sunburst-chart", "figure"),
        [
            Input("explore-apply-filters", "n_clicks")
        ],
        [
            State("explore-sources", "value"),
            State("explore-start-date", "date"),
            State("explore-end-date", "date"),
            State("explore-languages", "value")
        ],
        prevent_initial_call=False
    )
    def update_sunburst_chart(n_clicks, sources, start_date, end_date, languages):
        """
        Update the sunburst chart based on filter selections - using ALL corpus data.
        """
        try:
            # Validate and format dates
            start_date, end_date = validate_dates(start_date, end_date)
            
            # Get ALL category data from entire corpus
            df = fetch_category_data(sources, start_date, end_date, languages)
            
            if df.empty:
                # Return empty chart with RUW styling
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available for the selected filters",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, 
                    showarrow=False,
                    font=dict(size=16)
                )
                fig.update_layout(
                    height=700,
                    showlegend=False,
                    paper_bgcolor='white',
                    plot_bgcolor='white'
                )
                return fig
            
            # Create sunburst chart with exact RUW formatting
            fig = create_sunburst_chart(df, "Cognitive Warfare Taxonomy Distribution")
            logger.info(f"Fetched category data: {len(df)} rows from entire corpus")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error updating sunburst chart: {e}")
            # Return error figure with RUW styling
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error loading data: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="red")
            )
            fig.update_layout(
                height=700,
                showlegend=False,
                paper_bgcolor='white',
                plot_bgcolor='white'
            )
            return fig

    @app.callback(
        Output("explore-content", "children"),
        [
            Input("sunburst-chart", "clickData")
        ],
        [
            State("explore-sources", "value"),
            State("explore-start-date", "date"),
            State("explore-end-date", "date"),
            State("explore-languages", "value")
        ],
        prevent_initial_call=True
    )
    def handle_sunburst_click(click_data, sources, start_date, end_date, languages):
        """
        Handle clicks on sunburst chart to show text chunks - exactly like RUW app.
        """
        if not click_data:
            return dash.no_update
            
        try:
            # Extract clicked category information exactly like RUW
            point = click_data['points'][0]
            clicked_label = point.get('label', '')
            
            if not clicked_label:
                return dash.no_update
            
            # Validate dates
            start_date, end_date = validate_dates(start_date, end_date)
            
            # Fetch ALL text chunks for the clicked category from entire corpus
            chunks_df = fetch_text_chunks_for_explore(
                clicked_label, sources, start_date, end_date, languages
            )
            
            if chunks_df.empty:
                return [
                    dbc.Alert(
                        f"No text chunks found for category: {clicked_label}",
                        color="info",
                        className="mt-3"
                    ),
                    create_back_button()
                ]
            
            # Create chunk cards with exact RUW formatting
            chunk_cards = []
            for idx, row in chunks_df.head(50).iterrows():
                card = format_chunk_card(row, idx)
                chunk_cards.append(card)
            
            return [
                dbc.Row([
                    dbc.Col([
                        html.H4(f"Text Chunks for: {clicked_label}", className="selection-title"),
                        html.P(f"Showing {min(len(chunks_df), 50)} of {len(chunks_df)} chunks", 
                               className="text-muted")
                    ], width=10),
                    dbc.Col([
                        create_back_button()
                    ], width=2, className="text-right")
                ], className="mb-3"),
                html.Div(chunk_cards, className="mt-3")
            ]
            
        except Exception as e:
            logger.error(f"Error handling sunburst click: {e}")
            return [
                dbc.Alert(
                    f"Error loading chunks: {str(e)}",
                    color="danger",
                    className="mt-3"
                ),
                create_back_button()
            ]

    @app.callback(
        Output("explore-content", "children", allow_duplicate=True),
        [
            Input("back-to-sunburst", "n_clicks")
        ],
        prevent_initial_call=True
    )
    def back_to_sunburst(n_clicks):
        """
        Return to main sunburst view exactly like RUW app.
        """
        if n_clicks:
            return [
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H5("Cognitive Warfare Taxonomy Distribution", className="mb-0")
                            ]),
                            dbc.CardBody([
                                html.Div([
                                    dcc.Graph(
                                        id="sunburst-chart",
                                        config={'displayModeBar': False},
                                        style={'height': '700px'}
                                    )
                                ], className="sunburst-container")
                            ])
                        ], className="shadow-sm")
                    ], width=12)
                ])
            ]
        return dash.no_update
    
    # Download callbacks exactly like RUW
    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("download-csv-button", "n_clicks"),
        [
            State("explore-sources", "value"),
            State("explore-start-date", "date"),
            State("explore-end-date", "date"),
            State("explore-languages", "value")
        ],
        prevent_initial_call=True
    )
    def download_csv(n_clicks, sources, start_date, end_date, languages):
        if n_clicks:
            try:
                start_date, end_date = validate_dates(start_date, end_date)
                df = fetch_category_data(sources, start_date, end_date, languages)
                return dcc.send_data_frame(df.to_csv, "cognitive_warfare_taxonomy.csv", index=False)
            except Exception as e:
                logger.error(f"Error downloading CSV: {e}")
        return dash.no_update
    
    @app.callback(
        Output("download-dataframe-json", "data"),
        Input("download-json-button", "n_clicks"),
        [
            State("explore-sources", "value"),
            State("explore-start-date", "date"),
            State("explore-end-date", "date"),
            State("explore-languages", "value")
        ],
        prevent_initial_call=True
    )
    def download_json(n_clicks, sources, start_date, end_date, languages):
        if n_clicks:
            try:
                start_date, end_date = validate_dates(start_date, end_date)
                df = fetch_category_data(sources, start_date, end_date, languages)
                return dcc.send_data_frame(df.to_json, "cognitive_warfare_taxonomy.json", orient="records")
            except Exception as e:
                logger.error(f"Error downloading JSON: {e}")
        return dash.no_update


def create_back_button() -> dbc.Button:
    """
    Create a back button exactly like RUW app.
    
    Returns:
        dbc.Button: Back button component
    """
    return dbc.Button(
        "← Back to Overview",
        id="back-to-sunburst",
        color="primary",
        className="mb-3",
        size="sm"
    )