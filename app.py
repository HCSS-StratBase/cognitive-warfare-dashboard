#!/usr/bin/env python
# coding: utf-8

"""
Cognitive Warfare Data Analysis Dashboard
-------------------------------------------
This dashboard provides tools to explore, search, and compare data related to
cognitive warfare research, with enhanced visualizations and performance optimizations.
"""

import logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

import os
import sys
from datetime import datetime

# Import Dash components
import dash
import dash_auth
from dash import html, dcc
import dash_bootstrap_components as dbc

# Import application components
from config import VALID_USERNAME_PASSWORD_PAIRS, APP_VERSION
from config import DEFAULT_START_DATE, DEFAULT_END_DATE
from database.connection import get_engine, dispose_engine
from database.data_fetchers import fetch_all_sources, fetch_date_range
from tabs.explore import create_explore_tab_layout, register_explore_callbacks
from tabs.search import create_search_tab_layout, register_search_callbacks
from tabs.compare import create_compare_tab_layout, register_compare_callbacks
from tabs.burstiness import create_burstiness_tab_layout, register_burstiness_callbacks
from tabs.sources import create_sources_tab_layout, register_sources_callbacks
from components.layout import create_header, create_about_modal
from utils.cache import clear_cache

# Define the consistent color for all components
THEME_BLUE = "#13376f"  # Dark blue color

def create_dash_app() -> dash.Dash:
    """
    Create and configure the Dash application.
    
    Returns:
        dash.Dash: Configured Dash application
    """
    app = dash.Dash(
        __name__, 
        external_stylesheets=[dbc.themes.BOOTSTRAP], 
        assets_folder='static',
        suppress_callback_exceptions=True,
        eager_loading=True,
        update_title=None,
        assets_ignore='.*\\.scss',
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"},
            {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
            {"http-equiv": "Cache-Control", "content": "no-cache, no-store, must-revalidate"},
            {"http-equiv": "Pragma", "content": "no-cache"},
            {"http-equiv": "Expires", "content": "0"}
        ]
    )
    
    app.title = "Cognitive Warfare Data Analysis Dashboard"
    app.scripts.config.serve_locally = True
    app.css.config.serve_locally = True
    
    # Add Basic Authentication (commented out for development)
    # auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
    
    # Fetch initial data
    source_options = []
    min_date, max_date = None, None
    
    try:
        # Get source options for dropdowns
        source_list = fetch_all_sources()
        source_options = [{'label': source, 'value': source} for source in source_list]
        source_options.insert(0, {'label': 'All Sources', 'value': 'ALL'})
        
        # Get date range for date pickers
        db_min_date, max_date = fetch_date_range()
        min_date = DEFAULT_START_DATE
        
        if max_date is None:
            max_date = DEFAULT_END_DATE
            
        logging.info(f"Initial data loaded: {len(source_options)} sources, date range: {min_date} to {max_date}")
    except Exception as e:
        logging.error(f"Error loading initial data: {e}")
        source_options = [{'label': 'All Sources', 'value': 'ALL'}]
        min_date = DEFAULT_START_DATE
        max_date = DEFAULT_END_DATE
    
    # Create the tab layouts
    explore_tab = create_explore_tab_layout(source_options, min_date, max_date)
    search_tab = create_search_tab_layout(source_options, min_date, max_date)
    compare_tab = create_compare_tab_layout(source_options, min_date, max_date)
    burstiness_tab = create_burstiness_tab_layout()
    sources_tab = create_sources_tab_layout(source_options, min_date, max_date)
    
    # About modal component
    about_modal = create_about_modal()
    
    # Create the main header
    header = create_header()
    
    # Custom CSS for styling
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <style>
                body, html {
                    max-width: 100%;
                    overflow-x: hidden;
                }
                
                .dash-tab {
                    padding: 4px 12px !important;
                    height: 32px !important;
                    line-height: 24px !important;
                    margin-bottom: -1px;
                }
                
                .dash-tab--selected {
                    font-weight: 500;
                    border-top: 2px solid ''' + THEME_BLUE + ''' !important;
                }
                
                .dash-tab-content {
                    padding-top: 10px;
                }
                
                .sunburst-container {
                    display: flex;
                    justify-content: center;
                    width: 100%;
                }
                
                ._dash-loading {
                    position: fixed !important;
                    top: 50% !important;
                    left: 50% !important;
                    transform: translate(-50%, -50%) !important;
                    width: 80px !important;
                    height: 80px !important;
                    border: 8px solid #f3f3f3 !important;
                    border-top: 8px solid ''' + THEME_BLUE + ''' !important;
                    z-index: 9999 !important;
                }
                
                .dashboard-container {
                    width: 100%;
                    max-width: 1800px;
                    margin: 0 auto;
                    padding: 0 15px;
                }
                
                @media (min-width: 2000px) {
                    .dashboard-container {
                        max-width: 80%;
                    }
                }
                
                .DateInput {
                    width: 85px !important;
                }
                
                .DateInput_input {
                    padding: 2px 8px !important;
                    font-size: 0.8rem !important;
                }
                
                .about-button {
                    background-color: ''' + THEME_BLUE + ''' !important;
                    border-color: ''' + THEME_BLUE + ''' !important;
                    color: white !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                }
                
                .app-header {
                    background-color: ''' + THEME_BLUE + ''';
                    color: white;
                    padding: 10px 20px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                
                .app-header h2 {
                    margin: 0;
                    font-weight: 500;
                }
                
                .selection-title {
                    color: #2196F3;
                    font-size: 1.5rem;
                    font-weight: 500;
                    margin-top: 1rem;
                    margin-bottom: 0.5rem;
                    text-align: center;
                }
                
                .card-header {
                    background-color: ''' + THEME_BLUE + ''' !important;
                    color: white !important;
                }
                
                .btn-primary, .btn-secondary, .btn-success, .btn-info {
                    background-color: ''' + THEME_BLUE + ''' !important;
                    border-color: ''' + THEME_BLUE + ''' !important;
                }
                
                .dash-spinner .dash-spinner-inner {
                    border-top-color: ''' + THEME_BLUE + ''' !important;
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    
    # Main layout with tabs
    app.layout = html.Div([
        header,
        dcc.Tabs([
            dcc.Tab(label="Explore", children=explore_tab, className="custom-tab"),
            dcc.Tab(label="Search", children=search_tab, className="custom-tab"),
            dcc.Tab(label="Compare", children=compare_tab, className="custom-tab"),
            dcc.Tab(label="Burstiness", children=burstiness_tab, className="custom-tab"),
            dcc.Tab(label="Sources", children=sources_tab, className="custom-tab"),
        ], className="slimmer-tabs"),
        about_modal,
        # Download components
        dcc.Download(id="download-dataframe-csv"),
        dcc.Download(id="download-dataframe-json"),
        dcc.Download(id="search-download-csv"),
        dcc.Download(id="search-download-json"),
        # Local storage
        dcc.Store(id="cache-status", data={"enabled": True})
    ], className="dashboard-container")
    
    # Register callbacks for each tab
    register_explore_callbacks(app)
    register_search_callbacks(app)
    register_compare_callbacks(app)
    register_burstiness_callbacks(app)
    register_sources_callbacks(app)
    
    # Register about modal callback
    @app.callback(
        dash.Output("about-modal", "is_open", allow_duplicate=True),
        [
            dash.Input("open-about-main", "n_clicks"),
            dash.Input("close-about", "n_clicks"),
        ],
        [dash.State("about-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_about_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open
    
    # Add cache clearing callback
    @app.callback(
        dash.Output("cache-status", "data"),
        dash.Input("clear-cache-button", "n_clicks"),
        dash.State("cache-status", "data"),
        prevent_initial_call=True
    )
    def handle_clear_cache(n_clicks, cache_status):
        if n_clicks:
            clear_cache()
            cache_status["last_cleared"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return cache_status
        return dash.no_update
    
    return app


# Create app at module level for Gunicorn
app = create_dash_app()
# Expose server for Gunicorn
server = app.server

def main():
    """
    Main entry point for the application when run directly.
    """
    try:
        port = int(os.environ.get("PORT", 8051))
        app.run(debug=True, host='0.0.0.0', port=port)
        
    except Exception as e:
        logging.error(f"Error starting application: {e}")
        raise
    finally:
        dispose_engine()
        logging.info("Application resources cleaned up")


if __name__ == "__main__":
    main()