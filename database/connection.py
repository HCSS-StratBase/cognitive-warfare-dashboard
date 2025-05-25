#!/usr/bin/env python
# coding: utf-8

"""
Database connection utilities for cognitive warfare dashboard.
"""

import logging
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

# Import the engine from schema.py
from schema import engine

def get_engine():
    """
    Get the database engine.
    
    Returns:
        sqlalchemy.engine.Engine: Database engine
    """
    return engine

def dispose_engine():
    """
    Dispose of the database engine and clean up connections.
    """
    try:
        engine.dispose()
        logging.info("Database engine disposed successfully")
    except Exception as e:
        logging.error(f"Error disposing database engine: {e}")

def test_connection():
    """
    Test the database connection.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logging.error(f"Database connection test failed: {e}")
        return False

def get_session():
    """
    Get a database session.
    
    Returns:
        sqlalchemy.orm.Session: Database session
    """
    Session = sessionmaker(bind=engine)
    return Session()

def execute_query(query: str, params: dict = None):
    """
    Execute a query and return results.
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        Result set
    """
    try:
        with engine.connect() as conn:
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))
            return result.fetchall()
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        raise

def create_search_indexes():
    """
    Create search indexes for better performance.
    """
    try:
        with engine.connect() as conn:
            # Create GIN indexes for full-text search
            conn.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chunks_text_gin 
                ON chunks USING gin(to_tsvector('english', chunk_text))
            """))
            
            conn.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_records_content_gin 
                ON records USING gin(to_tsvector('english', primary_content_text))
            """))
            
            conn.commit()
            logging.info("Search indexes created successfully")
    except Exception as e:
        logging.error(f"Error creating search indexes: {e}")
        raise