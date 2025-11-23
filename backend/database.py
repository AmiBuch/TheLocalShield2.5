"""
Database connection and configuration module.
Handles database initialization and connection management.
"""

import sqlite3
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from datetime import datetime


class Database:
    """Database connection manager for SQLite."""
    
    def __init__(self, db_path: str = "thelocalshield.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.initialize_tables()
    
    def connect(self):
        """Establish database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
        return self.connection
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Ensures proper connection handling and cleanup.
        """
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            # Don't close the persistent connection, just commit/rollback
            pass
    
    def initialize_tables(self):
        """Initialize database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    expo_push_token TEXT
                )
            """)
            
            # Create locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    user_id INTEGER,
                    latitude REAL,
                    longitude REAL,
                    last_updated TIMESTAMP,
                    PRIMARY KEY (user_id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            conn.commit()
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute a database query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_many(self, query: str, params_list: list):
        """Execute a query multiple times with different parameters."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()


def get_all_users() -> List[Dict[str, Any]]:
    """
    Retrieve all users from the database.
    
    Returns:
        List of dictionaries containing user data (id, name, expo_push_token)
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, expo_push_token FROM users")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_user_push_tokens_except(user_id: int) -> List[str]:
    """
    Get push tokens for all users except the specified user.
    
    Args:
        user_id: User ID to exclude from results
        
    Returns:
        List of Expo push tokens (excluding None/empty tokens)
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT expo_push_token 
            FROM users 
            WHERE id != ? AND expo_push_token IS NOT NULL AND expo_push_token != ''
        """, (user_id,))
        rows = cursor.fetchall()
        return [row['expo_push_token'] for row in rows if row['expo_push_token']]


def upsert_location(user_id: int, latitude: float, longitude: float) -> bool:
    """
    Insert or update a user's location.
    
    Args:
        user_id: User identifier
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            current_timestamp = datetime.now().isoformat()
            
            # Use INSERT OR REPLACE for upsert operation
            cursor.execute("""
                INSERT OR REPLACE INTO locations (user_id, latitude, longitude, last_updated)
                VALUES (?, ?, ?, ?)
            """, (user_id, latitude, longitude, current_timestamp))
            
            return True
    except Exception as e:
        print(f"Error upserting location: {e}")
        return False


def get_all_locations() -> List[Dict[str, Any]]:
    """
    Retrieve all location records from the database.
    
    Returns:
        List of dictionaries containing location data (user_id, latitude, longitude, last_updated)
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, latitude, longitude, last_updated 
            FROM locations
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def register_push_token(user_id: int, expo_push_token: str, name: str = None) -> bool:
    """
    Register or update a user's Expo push token.
    Creates the user if they don't exist.
    
    Args:
        user_id: User identifier
        expo_push_token: Expo push notification token
        name: Optional user name
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            user_exists = cursor.fetchone()
            
            if user_exists:
                # Update existing user's push token
                cursor.execute("""
                    UPDATE users 
                    SET expo_push_token = ?, name = COALESCE(?, name)
                    WHERE id = ?
                """, (expo_push_token, name, user_id))
            else:
                # Create new user with push token
                cursor.execute("""
                    INSERT INTO users (id, name, expo_push_token)
                    VALUES (?, ?, ?)
                """, (user_id, name or f"User {user_id}", expo_push_token))
            
            return True
    except Exception as e:
        print(f"Error registering push token: {e}")
        return False


# Global database instance
db = Database()

