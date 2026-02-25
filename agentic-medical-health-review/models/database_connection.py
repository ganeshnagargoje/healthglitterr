"""
Database Connection Manager

Handles PostgreSQL database connections with context manager support
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Optional


class DatabaseConnection:
    """Database connection manager with context manager support"""
    
    def __init__(self):
        self.conn: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extensions.cursor] = None
    
    def connect(self) -> bool:
        """
        Establish database connection using environment variables
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=os.getenv('POSTGRES_PORT', '5432'),
                database=os.getenv('POSTGRES_DB', 'medical_health_review'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres')
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def close(self):
        """Close database connection and cursor"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def commit(self):
        """Commit current transaction"""
        if self.conn:
            self.conn.commit()
    
    def rollback(self):
        """Rollback current transaction"""
        if self.conn:
            self.conn.rollback()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic commit/rollback"""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
