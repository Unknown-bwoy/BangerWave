import sqlite3
from typing import List, Dict, Any, Optional

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
            
            # Relational Junction Table mapping tracks to playlists with cascade protection
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

    def add_track_to_playlist(self,playlist_id: int,track_data:dict) -> bool:
       """Safely caches song and maps it to a playlist via our junction table. 
          Prevent table duplication and thread-clapping using single context blocks. 
       """ 
       try: 
           with self._get_connection() as conn: 
               cursor = conn.cursor() 

               # Step 1:Cache the track metadata safely; ignore if it alreafy exists 
               cursor.execute("""INSERT OR IGNORE INTO tracks (search_query,name,duration)
                              VALUES (?,?,?)
               """, (track_data["query"], track_data["title"],track_data["duration"]))

               # Step 2: Grab the unique primary key ID of that cached  track record 
               cursor.execute("SELECT id FROM  tracks WHERE search_query = ?",(track_data["query"],)) 
               row = cursor.fetchone() 
               if not row: 
                   return False 
               track_id = row["id"] 

               # Step 3: Insert the mapping into our composite junction table
               cursor.execute("""
                   INSERT OR IGNORE INTO playlist_tracks (playlist_id,track_id)
                   VALUES (?, ?)
                 """, (playlist_id, track_id)) 
               
                #SQLite auto-commits upon successful exit of this context scope block     
               print(f"[DATA SUCCESS] Mapped Track ID {track_id} to Playlist ID {playlist_id}") 
               return True
       except sqlite3.Error as e:
            print(f"[DATA ERROR] Relational insertion failure: {e}") 
            return False   

    def get_playlist_tracks(self, playlist_id:int) -> list: 
        """Retrieves all permanent cached tracks mapped to a specific playlist ID."""
        try: 
            with self._get_connection() as conn: 
                cursor = conn.cursor() 
                # Run on timer join query to pull track rows matching our junction mapping 
                cursor.execute("""
                     SELECT t.id,t.search_query,t.name as title,t.duration 
                     FROM tracks t  
                     INNER JOIN playlist_tracks pt ON t.id = pt.track_id 
                     WHERE pt.playlist_id = ? 
            """, (playlist_id,)) 

                # Convert the sqlite3.Row elements into clean dictionary models 
                return [dict(row) for row in cursor.fetchall()] 
        except sqlite3.Error as e: 
            print(f"[DATA ERROR] Playlist retrieval query failure: {e}") 
            return []