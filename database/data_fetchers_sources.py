#!/usr/bin/env python
# coding: utf-8

"""
Data fetchers for sources analysis in the cognitive warfare dashboard.
"""

import logging
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional, Any
from sqlalchemy import text
from database.connection import get_engine

def fetch_corpus_stats(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None
) -> Dict[str, Any]:
    """
    Fetch overall corpus statistics.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        
    Returns:
        Dict[str, Any]: Corpus statistics
    """
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            COUNT(DISTINCT r.record_id) as total_records,
            COUNT(DISTINCT c.chunk_id) as total_chunks,
            COUNT(DISTINCT cc.id) as total_classifications,
            AVG(LENGTH(c.chunk_text)) as avg_chunk_length,
            COUNT(DISTINCT r.original_source) as unique_sources,
            COUNT(DISTINCT r.language) as unique_languages,
            AVG(cc.confidence) as avg_confidence,
            MIN(r.publication_date) as min_date,
            MAX(r.publication_date) as max_date
        FROM records r
        LEFT JOIN chunks c ON r.record_id = c.record_id
        LEFT JOIN chunk_classifications cc ON c.chunk_id = cc.chunk_id AND cc.is_relevant = true
        WHERE 1=1
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
        
        with engine.connect() as conn:
            result = conn.execute(text(query), params).fetchone()
        
        if result:
            stats = {
                'total_records': result[0] or 0,
                'total_chunks': result[1] or 0,
                'total_classifications': result[2] or 0,
                'avg_chunk_length': result[3] or 0,
                'unique_sources': result[4] or 0,
                'unique_languages': result[5] or 0,
                'avg_confidence': result[6] or 0,
                'min_date': result[7],
                'max_date': result[8],
                'classification_rate': (result[2] or 0) / max(result[1] or 1, 1),
                'date_range': f"{result[7]} to {result[8]}" if result[7] and result[8] else "N/A"
            }
        else:
            stats = {
                'total_records': 0,
                'total_chunks': 0,
                'total_classifications': 0,
                'avg_chunk_length': 0,
                'unique_sources': 0,
                'unique_languages': 0,
                'avg_confidence': 0,
                'classification_rate': 0,
                'date_range': 'N/A'
            }
        
        logging.info(f"Fetched corpus stats: {stats['total_records']} records")
        return stats
        
    except Exception as e:
        logging.error(f"Error fetching corpus stats: {e}")
        return {
            'total_records': 0,
            'total_chunks': 0,
            'total_classifications': 0,
            'avg_chunk_length': 0,
            'unique_sources': 0,
            'unique_languages': 0,
            'avg_confidence': 0,
            'classification_rate': 0,
            'date_range': 'N/A'
        }

def fetch_source_distribution(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None
) -> pd.DataFrame:
    """
    Fetch source distribution data.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        
    Returns:
        pd.DataFrame: Source distribution data
    """
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            r.original_source as source,
            COUNT(DISTINCT r.record_id) as count,
            COUNT(DISTINCT c.chunk_id) as chunks,
            COUNT(DISTINCT cc.id) as classifications
        FROM records r
        LEFT JOIN chunks c ON r.record_id = c.record_id
        LEFT JOIN chunk_classifications cc ON c.chunk_id = cc.chunk_id AND cc.is_relevant = true
        WHERE r.original_source IS NOT NULL
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
        
        query += " GROUP BY r.original_source ORDER BY count DESC"
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        logging.info(f"Fetched source distribution: {len(df)} sources")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching source distribution: {e}")
        return pd.DataFrame(columns=['source', 'count', 'chunks', 'classifications'])

def fetch_language_distribution(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None
) -> pd.DataFrame:
    """
    Fetch language distribution data.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        
    Returns:
        pd.DataFrame: Language distribution data
    """
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            COALESCE(r.language, 'Unknown') as language,
            COUNT(DISTINCT r.record_id) as count,
            COUNT(DISTINCT c.chunk_id) as chunks,
            COUNT(DISTINCT cc.id) as classifications
        FROM records r
        LEFT JOIN chunks c ON r.record_id = c.record_id
        LEFT JOIN chunk_classifications cc ON c.chunk_id = cc.chunk_id AND cc.is_relevant = true
        WHERE 1=1
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
        
        query += " GROUP BY r.language ORDER BY count DESC"
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        logging.info(f"Fetched language distribution: {len(df)} languages")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching language distribution: {e}")
        return pd.DataFrame(columns=['language', 'count', 'chunks', 'classifications'])

def fetch_temporal_distribution(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None,
    granularity: str = 'month'
) -> pd.DataFrame:
    """
    Fetch temporal distribution data.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        granularity: Time granularity ('day', 'week', 'month', 'year')
        
    Returns:
        pd.DataFrame: Temporal distribution data
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
        
        date_trunc = date_trunc_map.get(granularity, 'month')
        
        query = f"""
        SELECT 
            DATE_TRUNC('{date_trunc}', r.publication_date) as period,
            EXTRACT(year FROM r.publication_date) as year,
            r.original_source as source,
            COUNT(DISTINCT r.record_id) as count,
            COUNT(DISTINCT c.chunk_id) as chunks,
            COUNT(DISTINCT cc.id) as classifications
        FROM records r
        LEFT JOIN chunks c ON r.record_id = c.record_id
        LEFT JOIN chunk_classifications cc ON c.chunk_id = cc.chunk_id AND cc.is_relevant = true
        WHERE r.publication_date IS NOT NULL
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
        
        query += f"""
        GROUP BY 
            DATE_TRUNC('{date_trunc}', r.publication_date),
            EXTRACT(year FROM r.publication_date),
            r.original_source
        ORDER BY period, source
        """
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        # Convert period to datetime
        df['period'] = pd.to_datetime(df['period'])
        
        logging.info(f"Fetched temporal distribution: {len(df)} rows")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching temporal distribution: {e}")
        return pd.DataFrame(columns=['period', 'year', 'source', 'count', 'chunks', 'classifications'])

def fetch_taxonomy_by_source(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None
) -> pd.DataFrame:
    """
    Fetch taxonomy coverage by source.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        
    Returns:
        pd.DataFrame: Taxonomy coverage data
    """
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            r.original_source as source,
            SPLIT_PART(cc."HLTP", ' - ', 1) as category,
            SPLIT_PART(cc."HLTP", ' - ', 2) as subcategory,
            COUNT(*) as count,
            AVG(cc.confidence) as avg_confidence
        FROM chunk_classifications cc
        JOIN chunks c ON cc.chunk_id = c.chunk_id
        JOIN records r ON c.record_id = r.record_id
        WHERE cc.is_relevant = true 
            AND cc."HLTP" IS NOT NULL
            AND r.original_source IS NOT NULL
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
            r.original_source,
            SPLIT_PART(cc."HLTP", ' - ', 1),
            SPLIT_PART(cc."HLTP", ' - ', 2)
        ORDER BY source, category, subcategory
        """
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        logging.info(f"Fetched taxonomy by source: {len(df)} rows")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching taxonomy by source: {e}")
        return pd.DataFrame(columns=['source', 'category', 'subcategory', 'count', 'avg_confidence'])

def fetch_taxonomy_combinations(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None
) -> pd.DataFrame:
    """
    Fetch taxonomy combinations data.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        
    Returns:
        pd.DataFrame: Taxonomy combinations data
    """
    try:
        # This is a simplified version - could be enhanced for more complex analysis
        return fetch_taxonomy_by_source(sources, start_date, end_date, languages)
        
    except Exception as e:
        logging.error(f"Error fetching taxonomy combinations: {e}")
        return pd.DataFrame()

def fetch_chunks_data(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None,
    limit: int = 1000
) -> pd.DataFrame:
    """
    Fetch chunks data for analysis.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        limit: Maximum number of chunks to return
        
    Returns:
        pd.DataFrame: Chunks data
    """
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            c.chunk_id,
            c.chunk_text,
            LENGTH(c.chunk_text) as chunk_length,
            r.original_source as source,
            r.language,
            r.publication_date,
            r.title,
            cc.HLTP as taxonomy_path,
            cc.confidence
        FROM chunks c
        JOIN records r ON c.record_id = r.record_id
        LEFT JOIN chunk_classifications cc ON c.chunk_id = cc.chunk_id AND cc.is_relevant = true
        WHERE 1=1
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
        
        query += f" ORDER BY r.publication_date DESC LIMIT {limit}"
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        logging.info(f"Fetched chunks data: {len(df)} chunks")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching chunks data: {e}")
        return pd.DataFrame()

def fetch_documents_data(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None,
    limit: int = 1000
) -> pd.DataFrame:
    """
    Fetch documents/records data for analysis.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        limit: Maximum number of documents to return
        
    Returns:
        pd.DataFrame: Documents data
    """
    try:
        engine = get_engine()
        
        query = """
        SELECT 
            r.record_id,
            r.title,
            r.authors_speakers_list as authors,
            r.publication_date,
            r.publication_year,
            r.original_source as source,
            r.language,
            r.record_type,
            LENGTH(r.primary_content_text) as content_length,
            COUNT(DISTINCT c.chunk_id) as chunk_count,
            COUNT(DISTINCT cc.id) as classification_count
        FROM records r
        LEFT JOIN chunks c ON r.record_id = c.record_id
        LEFT JOIN chunk_classifications cc ON c.chunk_id = cc.chunk_id AND cc.is_relevant = true
        WHERE 1=1
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
        
        query += f"""
        GROUP BY 
            r.record_id, r.title, r.authors_speakers_list, r.publication_date,
            r.publication_year, r.original_source, r.language, r.record_type,
            r.primary_content_text
        ORDER BY r.publication_date DESC 
        LIMIT {limit}
        """
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        logging.info(f"Fetched documents data: {len(df)} documents")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching documents data: {e}")
        return pd.DataFrame()

def fetch_time_series_data(
    metric: str = 'records',
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    languages: List[str] = None,
    granularity: str = 'month'
) -> pd.DataFrame:
    """
    Fetch time series data for various metrics.
    
    Args:
        metric: Metric to analyze ('records', 'chunks', 'classifications')
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        languages: List of languages to filter by
        granularity: Time granularity
        
    Returns:
        pd.DataFrame: Time series data
    """
    try:
        if metric == 'records':
            return fetch_temporal_distribution(sources, start_date, end_date, languages, granularity)
        else:
            # For other metrics, use records as base for now
            return fetch_temporal_distribution(sources, start_date, end_date, languages, granularity)
            
    except Exception as e:
        logging.error(f"Error fetching time series data: {e}")
        return pd.DataFrame()

def fetch_language_time_series(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    granularity: str = 'month'
) -> pd.DataFrame:
    """
    Fetch language distribution over time.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        granularity: Time granularity
        
    Returns:
        pd.DataFrame: Language time series data
    """
    try:
        engine = get_engine()
        
        date_trunc = granularity if granularity in ['day', 'week', 'month', 'year'] else 'month'
        
        query = f"""
        SELECT 
            DATE_TRUNC('{date_trunc}', r.publication_date) as period,
            COALESCE(r.language, 'Unknown') as language,
            COUNT(DISTINCT r.record_id) as count
        FROM records r
        WHERE r.publication_date IS NOT NULL
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
        
        query += f"""
        GROUP BY 
            DATE_TRUNC('{date_trunc}', r.publication_date),
            r.language
        ORDER BY period, language
        """
        
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn, params=params)
        
        # Convert period to datetime
        df['period'] = pd.to_datetime(df['period'])
        
        logging.info(f"Fetched language time series: {len(df)} rows")
        return df
        
    except Exception as e:
        logging.error(f"Error fetching language time series: {e}")
        return pd.DataFrame(columns=['period', 'language', 'count'])

def fetch_database_time_series(
    sources: List[str] = None,
    start_date: date = None,
    end_date: date = None,
    granularity: str = 'month'
) -> pd.DataFrame:
    """
    Fetch database/source distribution over time.
    
    Args:
        sources: List of sources to filter by
        start_date: Start date filter
        end_date: End date filter
        granularity: Time granularity
        
    Returns:
        pd.DataFrame: Database time series data
    """
    try:
        # This is essentially the same as fetch_temporal_distribution
        return fetch_temporal_distribution(sources, start_date, end_date, None, granularity)
        
    except Exception as e:
        logging.error(f"Error fetching database time series: {e}")
        return pd.DataFrame()