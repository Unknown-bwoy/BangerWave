# File Name: ui/search_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QScrollArea, QFrame, QLabel, QMenu)
from PySide6.QtCore import Qt, QThreadPool, Slot
from core.audio_worker import AudioScrapeWorker

class BangerWaveSearchView(QWidget):
    """Network query panel providing asynchronous song lookup lists and save destinations."""
    def __init__(self, state, db):
        super().__init__()
        self.state = state
        self.db = db

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 1. Search Box Bar Layout Row
        search_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Search for songs, artists, or genres...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #242424;
                color: #FFFFFF;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #1DB954;
            }
        """)
        self.input_field.returnPressed.connect(self.trigger_search)

        search_btn = QPushButton("Search")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
        """)
        search_btn.clicked.connect(self.trigger_search)

        search_row.addWidget(self.input_field)
        search_row.addWidget(search_btn)
        layout.addLayout(search_row)

        # 2. Scrolling Content Output Area Grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.results_layout = QVBoxLayout(self.scroll_content)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(8)
        self.results_layout.addStretch() # Stays packed at top space parameters

        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area)

    def trigger_search(self):
        """Asynchronously dispatches a yt_dlp scraping worker task onto the global QThreadPool."""
        query = self.input_field.text().strip()
        if not query:
            return

        # Clear visual nodes and render a clean processing layout feedback label
        self.clear_results_layout()
        loading_lbl = QLabel("🔍 Fetching matching track links...")
        loading_lbl.setStyleSheet("color: #B3B3B3; font-style: italic;")
        self.results_layout.insertWidget(0, loading_lbl)

        # Instantiate the thread-isolated runnable worker class task
        worker = AudioScrapeWorker(query)
        worker.signals.result.connect(self.handle_search_success)
        worker.signals.error.connect(self.handle_search_failure)
        
        # Fire background execution without blocking frames
        QThreadPool.globalInstance().start(worker)

    @Slot(dict)
    def handle_search_success(self, track_data: dict):
        """Builds a beautiful custom dark Spotify card layout card for the resolved track result."""
        self.clear_results_layout()

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #242424;
                border-radius: 6px;
                padding: 10px;
            }
            QFrame:hover {
                background-color: #2a2a2a;
            }
            QLabel { background: transparent; }
        """)
        card_layout = QHBoxLayout(card)

        # Left Info Labels
        info_layout = QVBoxLayout()
        title = QLabel(track_data["title"])
        title.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 14px;")
        
        m, s = divmod(int(track_data["duration"]), 60)
        length = QLabel(f"Length: {m}m {s:02d}s")
        length.setStyleSheet("color: #A7A7A7; font-size: 11px;")
        
        info_layout.addWidget(title)
        info_layout.addWidget(length)
        card_layout.addLayout(info_layout, stretch=1)

        # Right Action Buttons
        play_icon_btn = QPushButton("▶")
        play_icon_btn.setFixedSize(32, 32)
        play_icon_btn.setStyleSheet("QPushButton { background-color: #1DB954; color: white; border-radius: 16px; font-size: 12px; }")
        play_icon_btn.clicked.connect(lambda: self.state.update_track(track_data))

        menu_icon_btn = QPushButton("•••")
        menu_icon_btn.setFixedSize(32, 32)
        menu_icon_btn.setStyleSheet("QPushButton { color: #B3B3B3; font-weight: bold; font-size: 14px; } QPushButton:hover { color: white; }")
        menu_icon_btn.clicked.connect(lambda: self.show_save_menu(menu_icon_btn, track_data))

        card_layout.addWidget(play_icon_btn)
        card_layout.addWidget(menu_icon_btn)
        
        self.results_layout.insertWidget(0, card)

    @Slot(str)
    def handle_search_failure(self, error_msg: str):
        self.clear_results_layout()
        err_lbl = QLabel(f"❌ Error: {error_msg}")
        err_lbl.setStyleSheet("color: #FF5555;")
        self.results_layout.insertWidget(0, err_lbl)

    def show_save_menu(self, parent_widget, track_data: dict):
        """Spawns a native contextual popup menu listing custom user playlist destinations."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #282828; color: #FFFFFF; border: 1px solid #404040; }
            QMenu::item:selected { background-color: #1DB954; }
        """)
        
        playlists = self.db.get_all_playlists()
        if not playlists:
            no_pl_action = menu.addAction("No Playlists Available")
            no_pl_action.setEnabled(False)
        else:
            for pl in playlists:
                action = menu.addAction(f"Save to {pl['name']}")
                # Route parameters dynamically via lambda closures
                action.triggered.connect(lambda checked=False, p_id=pl["id"]: self.save_to_db(p_id, track_data))
        
        menu.exec(parent_widget.mapToGlobal(parent_widget.rect().bottomLeft()))

    def save_to_db(self, playlist_id: int, track: dict):
        success = self.db.add_track_to_playlist(playlist_id, track)
        if success:
            self.input_field.setText(f"Track Saved Successfully!")

    def clear_results_layout(self):
        while self.results_layout.count() > 1:
            item = self.results_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                     widget.deleteLater()
