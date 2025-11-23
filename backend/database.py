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
            
            # Create users table with authentication fields
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT,
                    expo_push_token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            # Create emergencies table for POC polling
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emergencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    latitude REAL,
                    longitude REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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


def create_emergency(user_id: int, latitude: float, longitude: float) -> int:
    """
    Create an emergency event in the database.
    
    Args:
        user_id: User identifier
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        int: Emergency ID
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO emergencies (user_id, latitude, longitude)
                VALUES (?, ?, ?)
            """, (user_id, latitude, longitude))
            return cursor.lastrowid
    except Exception as e:
        print(f"Error creating emergency: {e}")
        return -1


def get_recent_emergencies(since_timestamp: str = None, exclude_user_id: int = None) -> List[Dict[str, Any]]:
    """
    Get recent emergency events.
    
    Args:
        since_timestamp: Only return emergencies after this timestamp (ISO format)
        exclude_user_id: Exclude emergencies from this user
        
    Returns:
        List of emergency dictionaries
    """
    try:
        # Ensure table exists
        db.initialize_tables()
        
        # Convert ISO timestamp to SQLite format if provided
        if since_timestamp:
            # Remove 'Z' suffix and replace 'T' with space for SQLite comparison
            since_timestamp = since_timestamp.replace('Z', '').replace('T', ' ')
            # Also handle milliseconds - SQLite stores without them
            if '.' in since_timestamp:
                since_timestamp = since_timestamp.split('.')[0]
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Handle None values properly
            if since_timestamp and exclude_user_id is not None:
                print(f"🔍 Query: created_at > '{since_timestamp}' AND user_id != {exclude_user_id}")
                cursor.execute("""
                    SELECT id, user_id, latitude, longitude, created_at
                    FROM emergencies
                    WHERE created_at > ? AND user_id != ?
                    ORDER BY created_at DESC
                """, (since_timestamp, exclude_user_id))
            elif since_timestamp:
                print(f"🔍 Query: created_at > '{since_timestamp}'")
                cursor.execute("""
                    SELECT id, user_id, latitude, longitude, created_at
                    FROM emergencies
                    WHERE created_at > ?
                    ORDER BY created_at DESC
                """, (since_timestamp,))
            elif exclude_user_id is not None:
                print(f"🔍 Query: user_id != {exclude_user_id}")
                cursor.execute("""
                    SELECT id, user_id, latitude, longitude, created_at
                    FROM emergencies
                    WHERE user_id != ?
                    ORDER BY created_at DESC
                """, (exclude_user_id,))
            else:
                print("🔍 Query: ALL emergencies (last 50)")
                cursor.execute("""
                    SELECT id, user_id, latitude, longitude, created_at
                    FROM emergencies
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
            
            rows = cursor.fetchall()
            print(f"📊 Found {len(rows) if rows else 0} rows")
            
            # CRITICAL: Always return a list, never None
            if rows is None:
                return []
            if not rows:
                return []
            
            # Convert rows to dictionaries with proper formatting
            result = []
            for row in rows:
                if row:
                    row_dict = dict(row)
                    # Ensure created_at is a string (ISO format)
                    if 'created_at' in row_dict and row_dict['created_at']:
                        if isinstance(row_dict['created_at'], str):
                            pass  # Already a string
                        else:
                            # Convert datetime to ISO string
                            row_dict['created_at'] = row_dict['created_at'].isoformat()
                    # Ensure all required fields are present
                    if all(key in row_dict for key in ['id', 'user_id', 'latitude', 'longitude', 'created_at']):
                        result.append(row_dict)
            
            print(f"✅ Returning {len(result)} emergencies")
            # Final safety check - ensure we return a list
            return result if isinstance(result, list) else []
    except Exception as e:
        print(f"Error in get_recent_emergencies: {e}")
        import traceback
        traceback.print_exc()
        # Return empty list on error instead of crashing
        return []

        
def register_push_token(user_id: int, expo_push_token: str, name: str = None) -> bool:
    """
    Register or update a user's Expo push token.
    User must already exist (created via registration).
    
    Args:
        user_id: User identifier
        expo_push_token: Expo push notification token
        name: Optional user name (will update if provided)
        
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
                # Update existing user's push token and optionally name
                if name:
                    cursor.execute("""
                        UPDATE users 
                        SET expo_push_token = ?, name = ?
                        WHERE id = ?
                    """, (expo_push_token, name, user_id))
                else:
                    cursor.execute("""
                        UPDATE users 
                        SET expo_push_token = ?
                        WHERE id = ?
                    """, (expo_push_token, user_id))
                return True
            else:
                print(f"User {user_id} does not exist. Cannot register push token.")
                return False
    except Exception as e:
        print(f"Error registering push token: {e}")
        return False


# Global database instance
db = Database()

