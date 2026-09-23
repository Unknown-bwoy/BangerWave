# File Name: ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, Slot
from ui.search_view import BangerWaveSearchView
from ui.player_bar import BangerWavePlayerBar

class BangerWaveMainWindow(QMainWindow):
    """
    Master Layout Shell for the BangerWave Desktop Client.
    Implements a Spotify-style multi-pane interface using PySide6 layout managers.
    """
    def __init__(self, state, db):
        super().__init__()
        self.state = state
        self.db = db
        
        # 1. Primary Window Window Configurations
        self.setWindowTitle("BangerWave Stream Client")
        self.resize(1050, 650)
        
        # 2. Master CSS-Style Sheet (QSS) for a pitch-black music client look
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#SidebarFrame {
                background-color: #000000;
                border-radius: 8px;
            }
            QFrame#ViewportFrame {
                background-color: #181818;
                border-radius: 8px;
            }
            QPushButton {
                background-color: transparent;
                color: #B3B3B3;
                border: none;
                font-weight: bold;
                text-align: left;
                padding: 6px;
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)

        # 3. Assemble the central viewport structural architecture
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Top-level layout flows vertically (Workspace on top, player bar locked below)
        master_vertical_layout = QVBoxLayout(central_widget)
        master_vertical_layout.setContentsMargins(10, 10, 10, 10)
        master_vertical_layout.setSpacing(10)
        
        # The core workspace row partition splits the sidebar and content pane horizontally
        workspace_horizontal_layout = QHBoxLayout()
        workspace_horizontal_layout.setSpacing(10)
        
        # ──► A. The Left Sidebar Component Frame
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("SidebarFrame")
        sidebar_frame.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(15, 20, 15, 15)
        
        # Sidebar text header titles and button rows
        brand_title = QLabel("BangerWave")
        brand_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1DB954; margin-bottom: 15px;")
        sidebar_layout.addWidget(brand_title)
        
        search_nav_btn = QPushButton(" 🔍  Search Dashboard")
        sidebar_layout.addWidget(search_nav_btn)
        
        playlist_header = QLabel("Your Playlists")
        playlist_header.setStyleSheet("font-size: 12px; font-weight: bold; color: #A7A7A7; margin-top: 20px; margin-bottom: 5px;")
        sidebar_layout.addWidget(playlist_header)
        
        # Concrete placeholder layout box array to map active database playlists later
        self.playlist_container = QVBoxLayout()
        sidebar_layout.addLayout(self.playlist_container)
        sidebar_layout.addStretch() # Forces elements to stay tightly packed at the top
        
        # ──► B. The Center Main Viewport Panel Frame
        viewport_frame = QFrame()
        viewport_frame.setObjectName("ViewportFrame")
        viewport_layout = QVBoxLayout(viewport_frame)
        viewport_layout.setContentsMargins(15, 15, 15, 15)
        
        # Instantiate and inject your search component panel straight into the layout manager slot
        self.search_view = BangerWaveSearchView(self.state, self.db)
        viewport_layout.addWidget(self.search_view)
        
        # Add the completed workspace frames to the split horizontal layout panel row
        workspace_horizontal_layout.addWidget(sidebar_frame)
        workspace_horizontal_layout.addWidget(viewport_frame)
        
        # ──► C. The Persistent Bottom Media Console Player Bar
        self.player_bar = BangerWavePlayerBar(self.state)
        
        # Pack the main structural sections cleanly down the primary structural column
        master_vertical_layout.addLayout(workspace_horizontal_layout, stretch=1)
        master_vertical_layout.addWidget(self.player_bar)
        
        # 4. Connect safe reactive signal tracking observers to the UI update slots
        self.state.track_changed.connect(self.on_track_mutated)
        
        # Automatically load active folders upon application launch frame boots
        self.refresh_sidebar_playlists()

    @Slot(dict)
    def on_track_mutated(self, track_data: dict):
        """Triggers automatically when the state engine broadcasts an active track change signal."""
        print(f"[UI REACTION] Top-level Main Window received stream payload: {track_data['title']}")

    def refresh_sidebar_playlists(self):
        """Queries SQLite and systematically renders playlist row labels down the sidebar column."""
        # Clean out old widget handles safely
        while self.playlist_container.count():
            item = self.playlist_container.takeAt(0)
            if item is not None:  
                widget = item.widget()
                if widget is not None:
                     widget.deleteLater()
                
        # Hit your local data storage manager functions natively
        folders = self.db.get_all_playlists()
        for folder in folders:
            folder_button = QPushButton(f" 📁  {folder['name']}")
            folder_button.setStyleSheet("font-size: 13px; font-weight: normal; color: #B3B3B3;")
            self.playlist_container.addWidget(folder_button)
