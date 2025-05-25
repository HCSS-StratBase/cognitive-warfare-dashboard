#!/usr/bin/env python
# coding: utf-8

"""
Helper utilities for the cognitive warfare dashboard.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from dash import html
import dash_bootstrap_components as dbc

def format_number(num: Union[int, float]) -> str:
    """
    Format a number with thousand separators.
    
    Args:
        num: Number to format
        
    Returns:
        str: Formatted number string
    """
    if num is None:
        return "0"
    return f"{num:,}"

def format_chunk_row(row: pd.Series, index: int) -> dbc.Card:
    """
    Format a chunk row for display.
    
    Args:
        row: Pandas Series containing chunk data
        index: Row index
        
    Returns:
        dbc.Card: Formatted chunk card
    """
    # Truncate long text
    chunk_text = row.get('chunk_text', '')
    if len(chunk_text) > 500:
        chunk_text = chunk_text[:500] + "..."
    
    # Format metadata
    title = row.get('title', 'No title')
    authors = row.get('authors', 'Unknown')
    source = row.get('source', 'Unknown')
    pub_date = row.get('publication_date', 'Unknown')
    taxonomy = row.get('taxonomy_path', 'Not classified')
    confidence = row.get('confidence', 'N/A')
    
    return dbc.Card([
        dbc.CardHeader([
            html.H6(f"Chunk {index + 1}: {title[:100]}...", className="mb-0")
        ]),
        dbc.CardBody([
            html.P(chunk_text, style={'fontSize': '0.9rem', 'marginBottom': '10px'}),
            
            dbc.Row([
                dbc.Col([
                    html.Strong("Authors: "), authors[:100] + ("..." if len(str(authors)) > 100 else "")
                ], width=6),
                dbc.Col([
                    html.Strong("Source: "), source
                ], width=6)
            ], className="mb-2"),
            
            dbc.Row([
                dbc.Col([
                    html.Strong("Date: "), str(pub_date)
                ], width=6),
                dbc.Col([
                    html.Strong("Confidence: "), str(confidence)
                ], width=6)
            ], className="mb-2"),
            
            html.P([
                html.Strong("Taxonomy: "), 
                html.Span(taxonomy, style={'color': '#2196F3'})
            ], className="mb-0")
        ])
    ], className="mb-3")

def get_unique_filename(prefix: str, extension: str) -> str:
    """
    Generate a unique filename with timestamp.
    
    Args:
        prefix: Filename prefix
        extension: File extension
        
    Returns:
        str: Unique filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{unique_id}.{extension}"

def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """
    Convert hex color to rgba with alpha.
    
    Args:
        hex_color: Hex color string
        alpha: Alpha value (0-1)
        
    Returns:
        str: RGBA color string
    """
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})'

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def create_comparison_text(data1: Dict, data2: Dict) -> str:
    """
    Create comparison text between two data sets.
    
    Args:
        data1: First data set
        data2: Second data set
        
    Returns:
        str: Comparison text
    """
    total1 = data1.get('total', 0)
    total2 = data2.get('total', 0)
    
    if total1 == 0 and total2 == 0:
        return "Both selections contain no data."
    elif total1 == 0:
        return f"Selection 1 is empty, Selection 2 contains {total2:,} items."
    elif total2 == 0:
        return f"Selection 2 is empty, Selection 1 contains {total1:,} items."
    else:
        ratio = total1 / total2 if total2 > 0 else float('inf')
        if ratio > 1:
            return f"Selection 1 is {ratio:.1f}x larger than Selection 2 ({total1:,} vs {total2:,} items)."
        else:
            return f"Selection 2 is {1/ratio:.1f}x larger than Selection 1 ({total2:,} vs {total1:,} items)."

def validate_search_query(query: str, mode: str) -> tuple[bool, str]:
    """
    Validate search query based on mode.
    
    Args:
        query: Search query
        mode: Search mode
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Search query cannot be empty"
    
    if len(query) < 2:
        return False, "Search query must be at least 2 characters long"
    
    if len(query) > 1000:
        return False, "Search query too long (max 1000 characters)"
    
    if mode == 'boolean':
        # Basic boolean query validation
        invalid_chars = ['<', '>', '=', ';', '--']
        for char in invalid_chars:
            if char in query:
                return False, f"Invalid character in boolean query: {char}"
    
    return True, ""

def format_date_range(start_date: datetime, end_date: datetime) -> str:
    """
    Format date range for display.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        str: Formatted date range
    """
    if not start_date and not end_date:
        return "All dates"
    elif not start_date:
        return f"Until {end_date.strftime('%Y-%m-%d')}"
    elif not end_date:
        return f"From {start_date.strftime('%Y-%m-%d')}"
    else:
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        float: Division result or default
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default