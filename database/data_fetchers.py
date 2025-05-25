#!/usr/bin/env python
# coding: utf-8

"""
Data fetching functions for cognitive warfare dashboard.
Adapted from RUW data fetchers to work with cognitive warfare schema.
"""

import logging
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional, Any
from sqlalchemy import text
from database.connection import get_engine
from config import SEARCH_RESULT_LIMIT

def fetch_all_sources() -> List[str]:
    """
    Fetch all unique sources from the records table.
    
    Returns:
        List[str]: List of source names
    """
    try:
        engine = get_engine()
        query = """
        SELECT DISTINCT original_source 
        FROM records 
        WHERE original_source IS NOT NULL 
        ORDER BY original_source
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(query))
            sources = [row[0] for row in result.fetchall()]
        
        logging.info(f"Fetched {len(sources)} unique sources")
        return sources
        
    except Exception as e:
        logging.error(f"Error fetching sources: {e}")
        return []

def fetch_date_range() -> Tuple[Optional[date], Optional[date]]:
    """
    Fetch the min and max dates from the records table.
    
    Returns:
        Tuple[Optional[date], Optional[date]]: (min_date, max_date)
    """
    try:
        engine = get_engine()
        query = """
        SELECT MIN(publication_date) as min_date, MAX(publication_date) as max_date
        FROM records 
        WHERE publication_date IS NOT NULL
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(query))
            row = result.fetchone()
            
        min_date = row[0] if row and row[0] else None
        max_date = row[1] if row and row[1] else None
        
        logging.info(f"Date range: {min_date} to {max_date}")
        return min_date, max_date
        
    except Exception as e:
        logging.error(f"Error fetching date range: {e}")
        return None, None

def fetch_category_data(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None
) -> pd.DataFrame:
    """
    Fetch taxonomy category data for sunburst visualization.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        
    Returns:
        pd.DataFrame: Category data with columns [category, subcategory, sub_subcategory, count]
    """
    try:
        engine = get_engine()
        
        # Build the base query
        query = """
        SELECT 
            SPLIT_PART(cc."HLTP", ' - ', 1) as category,
            SPLIT_PART(cc."HLTP", ' - ', 2) as subcategory,
            COALESCE(cc."3rd_level_TE", cc."2nd_level_TE", 'Other') as sub_subcategory,
            COUNT(*) as count
        FROM chunk_classifications cc
        JOIN chunks c ON cc.chunk_id = c.chunk_id
        JOIN records r ON c.record_id = r.record_id
        WHERE cc.is_relevant = true 
            AND cc."HLTP" IS NOT NULL
        """
        
        # Add filters
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
            
        if languages and 'ALL' not in languages:
            placeholders = ','.join([f':lang_{i}' for i in range(len(languages))])
            query += f" AND r.language IN ({placeholders})"
            for i, lang in enumerate(languages):
                params[f'lang_{i}'] = lang
        
        query += """
        GROUP BY 
            SPLIT_PART(cc."HLTP", ' - ', 1),
            SPLIT_PART(cc."HLTP", ' - ', 2),
            COALESCE(cc."3rd_level_TE", cc."2nd_level_TE", 'Other')
        ORDER BY category, subcategory, sub_subcategory
        """
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        logging.info(f"Fetched category data: {len(df)} rows")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching category data: {e}")
        return pd.DataFrame(columns=['category', 'subcategory', 'sub_subcategory', 'count'])

def fetch_text_chunks(
    category: str = None,
    subcategory: str = None,
    sub_subcategory: str = None,
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None,
    limit: int = SEARCH_RESULT_LIMIT,
    offset: int = 0
) -> pd.DataFrame:
    """
    Fetch text chunks based on taxonomy selection and filters.
    
    Args:
        category: Category filter
        subcategory: Subcategory filter
        sub_subcategory: Sub-subcategory filter
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        limit: Maximum number of results
        offset: Offset for pagination
        
    Returns:
        pd.DataFrame: Text chunks data
    """
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            c.chunk_id,
            c.chunk_text,
            r.title,
            r.authors_speakers_list as authors,
            r.publication_date,
            r.original_source as source,
            r.language,
            cc."HLTP" as taxonomy_path,
            cc.confidence,
            cc.explanation
        FROM chunk_classifications cc
        JOIN chunks c ON cc.chunk_id = c.chunk_id
        JOIN records r ON c.record_id = r.record_id
        WHERE cc.is_relevant = true
        """
        
        params = {}
        
        # Add taxonomy filters
        if category:
            query += ' AND cc."HLTP" LIKE :category'
            params['category'] = f"{category}%"
            
        if subcategory:
            query += ' AND cc."HLTP" LIKE :subcategory'
            params['subcategory'] = f"%{subcategory}%"
            
        if sub_subcategory and sub_subcategory != 'Other':
            query += ' AND (cc."3rd_level_TE" = :sub_subcategory OR cc."2nd_level_TE" = :sub_subcategory)'
            params['sub_subcategory'] = sub_subcategory
        
        # Add other filters (same as fetch_category_data)
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
            
        if languages and 'ALL' not in languages:
            placeholders = ','.join([f':lang_{i}' for i in range(len(languages))])
            query += f" AND r.language IN ({placeholders})"
            for i, lang in enumerate(languages):
                params[f'lang_{i}'] = lang
        
        query += " ORDER BY r.publication_date DESC, c.chunk_id"
        query += f" LIMIT {limit} OFFSET {offset}"
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        logging.info(f"Fetched {len(df)} text chunks")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching text chunks: {e}")
        return pd.DataFrame()

def fetch_search_category_data(
    search_query: str,
    search_mode: str = 'keyword',
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None
) -> pd.DataFrame:
    """
    Fetch category data based on search results.
    
    Args:
        search_query: Search query string
        search_mode: Search mode ('keyword', 'boolean', 'semantic')
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        
    Returns:
        pd.DataFrame: Category data for search results
    """
    try:
        engine = get_engine()
        
        # Base query with search
        if search_mode == 'boolean':
            # Use PostgreSQL full-text search
            search_condition = "to_tsvector('english', c.chunk_text) @@ to_tsquery('english', :search_query)"
        elif search_mode == 'semantic':
            # For now, fall back to keyword search (can be enhanced with embedding search later)
            search_condition = "c.chunk_text ILIKE :search_query"
            search_query = f"%{search_query}%"
        else:  # keyword search
            search_condition = "c.chunk_text ILIKE :search_query"
            search_query = f"%{search_query}%"
        
        query = f"""
        SELECT 
            SPLIT_PART(cc."HLTP", ' - ', 1) as category,
            SPLIT_PART(cc."HLTP", ' - ', 2) as subcategory,
            COALESCE(cc."3rd_level_TE", cc."2nd_level_TE", 'Other') as sub_subcategory,
            COUNT(*) as count
        FROM chunk_classifications cc
        JOIN chunks c ON cc.chunk_id = c.chunk_id
        JOIN records r ON c.record_id = r.record_id
        WHERE cc.is_relevant = true 
            AND cc."HLTP" IS NOT NULL
            AND {search_condition}
        """
        
        params = {'search_query': search_query}
        
        # Add filters (same logic as fetch_category_data)
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
            
        if languages and 'ALL' not in languages:
            placeholders = ','.join([f':lang_{i}' for i in range(len(languages))])
            query += f" AND r.language IN ({placeholders})"
            for i, lang in enumerate(languages):
                params[f'lang_{i}'] = lang
        
        query += """
        GROUP BY 
            SPLIT_PART(cc."HLTP", ' - ', 1),
            SPLIT_PART(cc."HLTP", ' - ', 2),
            COALESCE(cc."3rd_level_TE", cc."2nd_level_TE", 'Other')
        ORDER BY category, subcategory, sub_subcategory
        """
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        logging.info(f"Fetched search category data: {len(df)} rows")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching search category data: {e}")
        return pd.DataFrame(columns=['category', 'subcategory', 'sub_subcategory', 'count'])

def fetch_all_text_chunks_for_search(
    search_query: str,
    search_mode: str = 'keyword',
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None,
    limit: int = SEARCH_RESULT_LIMIT,
    offset: int = 0
) -> pd.DataFrame:
    """
    Fetch all text chunks matching search criteria.
    
    Args:
        search_query: Search query string
        search_mode: Search mode ('keyword', 'boolean', 'semantic')
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        limit: Maximum number of results
        offset: Offset for pagination
        
    Returns:
        pd.DataFrame: Text chunks matching search
    """
    try:
        engine = get_engine()
        
        # Build search condition based on mode
        if search_mode == 'boolean':
            search_condition = "to_tsvector('english', c.chunk_text) @@ to_tsquery('english', :search_query)"
        elif search_mode == 'semantic':
            search_condition = "c.chunk_text ILIKE :search_query"
            search_query = f"%{search_query}%"
        else:  # keyword search
            search_condition = "c.chunk_text ILIKE :search_query"
            search_query = f"%{search_query}%"
        
        query = f"""
        SELECT 
            c.chunk_id,
            c.chunk_text,
            r.title,
            r.authors_speakers_list as authors,
            r.publication_date,
            r.original_source as source,
            r.language,
            cc."HLTP" as taxonomy_path,
            cc.confidence,
            cc.explanation,
            ts_rank(to_tsvector('english', c.chunk_text), to_tsquery('english', :search_query)) as relevance_score
        FROM chunks c
        JOIN records r ON c.record_id = r.record_id
        LEFT JOIN chunk_classifications cc ON c.chunk_id = cc.chunk_id AND cc.is_relevant = true
        WHERE {search_condition}
        """
        
        params = {'search_query': search_query}
        
        # Add filters
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
            
        if languages and 'ALL' not in languages:
            placeholders = ','.join([f':lang_{i}' for i in range(len(languages))])
            query += f" AND r.language IN ({placeholders})"
            for i, lang in enumerate(languages):
                params[f'lang_{i}'] = lang
        
        if search_mode == 'boolean':
            query += " ORDER BY relevance_score DESC, r.publication_date DESC"
        else:
            query += " ORDER BY r.publication_date DESC, c.chunk_id"
        
        query += f" LIMIT {limit} OFFSET {offset}"
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        logging.info(f"Fetched {len(df)} search result chunks")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching search result chunks: {e}")
        return pd.DataFrame()

def fetch_timeline_data(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None,
    granularity: str = 'month'
) -> pd.DataFrame:
    """
    Fetch timeline data for visualizations.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        granularity: Time granularity ('day', 'week', 'month', 'year')
        
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
            'year': 'year'
        }
        
        date_trunc = date_trunc_map.get(granularity, 'month')
        
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
        """
        
        params = {}
        
        # Add filters
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
            
        if languages and 'ALL' not in languages:
            placeholders = ','.join([f':lang_{i}' for i in range(len(languages))])
            query += f" AND r.language IN ({placeholders})"
            for i, lang in enumerate(languages):
                params[f'lang_{i}'] = lang
        
        query += """
        GROUP BY 
            DATE_TRUNC('{date_trunc}', r.publication_date),
            SPLIT_PART(cc."HLTP", ' - ', 1)
        ORDER BY period, category
        """.format(date_trunc=date_trunc)
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        logging.info(f"Fetched timeline data: {len(df)} rows")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching timeline data: {e}")
        return pd.DataFrame(columns=['period', 'category', 'count'])