# File Name: database/manager.py
import sqlite3
from typing import List, Dict, Any

class BangerWaveDatabase:
    """Manages thread-safe SQLite transactions for user playlists and track caching."""
    def __init__(self, db_name: str = "bangerwave.db"):
        self.db_name = db_name
        self.initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Opens a distinct, parameterized database connection handle."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Enables column access by dictionary string keys
        return conn

    def initialize_schema(self) -> None:
        """Generates relational database tables safely if they don't exist yet."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Master Cache Table for Track Information
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_query TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    duration REAL NOT NULL
                )
            """)
            
            # Folder Index for Custom Playlists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Relational Junction Table mapping tracks to playlists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlist_tracks (
                    playlist_id INTEGER,
                    track_id INTEGER,
                    PRIMARY KEY (playlist_id, track_id),
                    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def create_playlist(self, playlist_name: str) -> bool:
        """Inserts a new playlist record; returns False if name is a duplicate."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO playlists (name) VALUES (?)", (playlist_name.strip(),))
                return True
        except sqlite3.IntegrityError:
            return False

    def get_all_playlists(self) -> List[Dict[str, Any]]:
        """Queries the database and retrieves all saved custom playlist records."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM playlists ORDER BY date_created DESC")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Playlist retrieval failure: {e}")
            return []

    def add_track_to_playlist(self, playlist_id: int, track_data: dict) -> bool:
        """Safely caches song metadata and maps it to a playlist via our junction table."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO tracks (search_query, name, duration)
                    VALUES (?, ?, ?)
                """, (track_data["query"], track_data["title"], track_data["duration"]))
                
                cursor.execute("SELECT id FROM tracks WHERE search_query = ?", (track_data["query"],))
                row = cursor.fetchone()
                if not row:
                    return False
                track_id = row["id"]
                
                cursor.execute("""
                    INSERT OR IGNORE INTO playlist_tracks (playlist_id, track_id)
                    VALUES (?, ?)
                """, (playlist_id, track_id))
                return True
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Relational insertion failure: {e}")
            return False

    def get_playlist_tracks(self, playlist_id: int) -> list: 
        """
        Retrieves all permanently cached tracks mapped to a specific playlists ID.
        Uses an INNER JOIN across the junction table to reconstruct the track list models. 
         """     

        try: 

            with self._get_connection() as conn: 
                cursor = conn.cursor() 
                # Run an inner join query to extract track rows matching our mapping  
                cursor.execute("""
                     SELECT t.id, t.search_query,t.name as title , t.duration
                     FROM tracks t 
                     INNER JOIN playlist_tracks pt ON t.id = pt.track_id
                     WHERE pt.playlist_id = ?                
                """,(playlist_id,)) 

                #Convert the sqlite3.Row elements into clean dictionary objects for the UI 

                return [dict(row) for  row in cursor.fetchall()] 
        
        except sqlite3.Error as e: 
            print(f"[DATABASE ERROR] Playlist tracks query failure: {e}")  
            return []   