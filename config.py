#!/usr/bin/env python
# coding: utf-8

"""
Configuration file for the Cognitive Warfare Data Analysis Dashboard.
Contains settings, constants, and configuration variables.
"""

from datetime import datetime, date

# Application metadata
APP_VERSION = "1.0.0"
APP_TITLE = "Cognitive Warfare Data Analysis Dashboard"

# Authentication
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'cognitive_warfare_2024',
    'researcher': 'cw_research_access'
}

# Date ranges
DEFAULT_START_DATE = date(2020, 1, 1)
DEFAULT_END_DATE = date(2025, 12, 31)

# Search configuration
SEARCH_RESULT_LIMIT = 10000
SEARCH_TIMEOUT_SECONDS = 120

# Theme colors for consistent UI
THEME_COLORS = {
    'primary': '#13376f',
    'secondary': '#2196F3',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Source type display mapping
SOURCE_DISPLAY_MAP = {
    'parlamint': 'Parliamentary Data',
    'google_scholar': 'Academic Papers',
    'zotero': 'Research Library',
    'lens': 'Patent Database'
}

# Language options
LANGUAGE_OPTIONS = [
    {'label': 'All Languages', 'value': 'ALL'},
    {'label': 'English', 'value': 'en'},
    {'label': 'Dutch', 'value': 'nl'},
    {'label': 'French', 'value': 'fr'},
    {'label': 'German', 'value': 'de'},
    {'label': 'Spanish', 'value': 'es'},
    {'label': 'Italian', 'value': 'it'},
    {'label': 'Portuguese', 'value': 'pt'},
    {'label': 'Russian', 'value': 'ru'},
    {'label': 'Chinese', 'value': 'zh'},
    {'label': 'Other', 'value': 'other'}
]

# Source type options
SOURCE_TYPE_OPTIONS = [
    {'label': 'All Sources', 'value': 'ALL'},
    {'label': 'Academic Papers', 'value': 'google_scholar'},
    {'label': 'Parliamentary Data', 'value': 'parlamint'},
    {'label': 'Research Library', 'value': 'zotero'},
    {'label': 'Patent Database', 'value': 'lens'}
]

# Comparison visualization options
COMPARISON_VISUALIZATION_OPTIONS = [
    {'label': 'Bar Chart', 'value': 'bar'},
    {'label': 'Sunburst Comparison', 'value': 'sunburst'},
    {'label': 'Donut Chart', 'value': 'donut'},
    {'label': 'Sankey Diagram', 'value': 'sankey'}
]

# Burstiness filter options
BURSTINESS_FILTER_OPTIONS = [
    {'label': 'Taxonomy Elements', 'value': 'taxonomy'},
    {'label': 'Keywords', 'value': 'keywords'},
    {'label': 'Named Entities', 'value': 'entities'},
    {'label': 'All Combined', 'value': 'all'}
]

# Cognitive warfare taxonomy categories
COGWAR_MAIN_CATEGORIES = [
    'Conceptual Foundations',
    'Cognitive Target Domain', 
    'Operational Scope',
    'Counter-Measures',
    'Historical Dimension',
    'Related Concepts'
]

# PDF and static report URLs
REPORT_PDF_URL = "/assets/cognitive_warfare_report.pdf"
STATIC_HTML_URL = "/assets/static_report.html"

# Pagination settings
ITEMS_PER_PAGE = 50
MAX_ITEMS_PER_PAGE = 200

# Cache settings
CACHE_TIMEOUT = 3600  # 1 hour
CACHE_SIZE_LIMIT = 1000

# Visualization settings
CHART_HEIGHT = 700
CHART_WIDTH = 700
MAX_SUNBURST_SEGMENTS = 100

# Database query limits
MAX_QUERY_RESULTS = 50000
QUERY_TIMEOUT = 300  # 5 minutes

# Progress indicator settings
PROGRESS_UPDATE_INTERVAL = 1000  # milliseconds