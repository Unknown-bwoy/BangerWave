# File Name: ui/main_window.py
from PySide6.QtWidgets import  (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QLabel, QPushButton, QFrame, 
                             QStackedWidget, QInputDialog, QMessageBox)
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput
from PySide6.QtCore import  Qt,Slot,QUrl
from ui.search_view import BangerWaveSearchView
from ui.player_bar import BangerWavePlayerBar

class BangerWaveMainWindow(QMainWindow):
    """
    Master Structural Layout Shell for BangerWave. 
    Leverages QStackQWidget to implement fluid page toggling between 
    the Search Dashboard and active local playlist track listings.
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
            QMainWindow { background-color: #121212; }
            QLabel { color: #FFFFFF; font-family: 'Segoe UI', Arial, sans-serif; }
            QFrame#SidebarFrame { background-color: #000000; border-radius: 8px; }
            QFrame#ViewportFrame { background-color: #181818; border-radius: 8px; }
            QPushButton {
                background-color: transparent;
                color: #B3B3B3;
                border: none;
                font-weight: bold;
                text-align: left;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton:hover { color: #FFFFFF; }
            QPushButton#AddPlaylistBtn {
                color: #1DB954;
                font-size: 16px;
                text-align: right;
            }
        """)

        # 3. Initialise Audio Engine pipelines natively in memory registers 
        self.audio_output = QAudioOutput() 
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(self.state.volume) 

        # 4. Assemble the central viewport structural architecture
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        master_vertical_layout = QVBoxLayout(central_widget)
        master_vertical_layout.setContentsMargins(12, 12, 12, 12)
        master_vertical_layout.setSpacing(12)
        
       
        workspace_horizontal_layout = QHBoxLayout()
        workspace_horizontal_layout.setSpacing(12)
        
        # ──► A. The Left Sidebar Component Frame
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("SidebarFrame")
        sidebar_frame.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(17, 22, 17, 17)
        
        # Sidebar text header titles and button rows
        brand_title = QLabel("BangerWave")
        brand_title.setStyleSheet("font-size: 25px; font-weight: bold; color: #1DB954; margin-bottom: 17px;")
        sidebar_layout.addWidget(brand_title)
        
        search_nav_btn = QPushButton(" 🔍  Search Dashboard") 
        search_nav_btn.clicked.connect(lambda: self.view_stack.setCurrentIndex(0)) #Snaps viewport card back to search 
        sidebar_layout.addWidget(search_nav_btn)

        # Playlist Header Layout block with trailing Creation Action Button 
        playlist_header_row = QHBoxLayout()
        playlist_header_lbl = QLabel("Your Playlists")
        playlist_header_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #A7A7A7; text-transform: uppercase;")
        
        add_playlist_btn = QPushButton("➕") 
        add_playlist_btn.setFixedSize(25,25)
        add_playlist_btn.clicked.connect(self.trigger_create_playlist_dialog) 
        add_playlist_btn.setObjectName("AddPlaylistBtn")

        playlist_header_row.addWidget(playlist_header_lbl)
        playlist_header_row.addWidget(add_playlist_btn) 
        sidebar_layout.addLayout(playlist_header_row)
        
        # Concrete variable stack to list folders dynamically
        self.playlist_container = QVBoxLayout()
        sidebar_layout.addLayout(self.playlist_container)
        sidebar_layout.addStretch() # Forces elements to stay tightly packed at the top

        
        # ──► B. Right Central Viewport Page Stack Layer Component
        viewport_frame = QFrame()
        viewport_frame.setObjectName("ViewportFrame")
        viewport_layout = QVBoxLayout(viewport_frame)
        viewport_layout.setContentsMargins(17, 17, 17, 17)

        # MASTER SWITCH STACK: Replaces loose container boxes with card stacks 
        self.view_stack = QStackedWidget()

        #  Card Index 0: Build and Mount the Main Streaming Search Dashboard View 
        self.search_view = BangerWaveSearchView(self.state, self.db)
        self.view_stack.addWidget(self.search_view)
        
        # Card Index 1: Create a dedicated dynamic list view frame shell for tracking playlist entries
        self.playlist_tracks_view = QWidget()
        self.playlist_tracks_layout = QVBoxLayout(self.playlist_tracks_view)
        self.playlist_tracks_layout.setContentsMargins(1,1,1,1) 
        self.playlist_title_lbl = QLabel("Select a Playlist")
        self.playlist_title_lbl.setStyleSheet("font-size: 23px; font-weight:bold; margin-bottom: 10px;")
        self.playlist_tracks_layout.addWidget(self.playlist_title_lbl)


        # Add an inner tracking column for individual track items rows 
        self.track_list_container = QVBoxLayout() 
        self.playlist_tracks_layout.addLayout(self.track_list_container)
        self.playlist_tracks_layout.addStretch() 

        #Add side-by-side components to the workspace horizontal row container split 
        workspace_horizontal_layout.addWidget(sidebar_frame)
        workspace_horizontal_layout.addWidget(viewport_frame)

        # ──► C. The Persistent Bottom Media Console Player Bar
        self.player_bar = BangerWavePlayerBar(self.state)
        
        # Pack the main structural sections cleanly down the primary structural column
        master_vertical_layout.addLayout(workspace_horizontal_layout, stretch=1)
        master_vertical_layout.addWidget(self.player_bar)
        
        # 5. Connect Active Reactive Core Audio Pipeline Observers
        self.state.track_changed.connect(self.on_track_mutated) 
        self.state.volume_mutated.connect(lambda vol: self.audio_output.setVolume(vol))
        self.state.playback_toggled.connect(self.handle_playback_toggle_signal) 

        # Connect hardware timeless clock loops 
        self.media_player.durationChanged.connect(self.handle_media_duration_changed)
        self.media_player.positionChanged.connect(self.handle_media_postion_changed)
        
        # Map folders into layout rows at startup
        self.refresh_sidebar_playlists()

    def trigger_create_playlist_dialog(self): 
        """Spawns a clean native desktop string input window overlay box to store custom playlist entries."""
        text,ok = QInputDialog.getText(self, "Create Playlists", "Enter a name for your fresh playlist:")
        if ok  and  text.strip(): 
            success = self.db.create_playlist(text.strip())
            if success: 
                self.refresh_sidebar_playlists()
            else:
                QMessageBox.warning(self, "Duplicate Folder", "A playlist named that already exists inside your responsitory.")

    def refresh_sidebar_playlists(self):
        """Queries database and renders directory folder buttons down the left menu column."""
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
            folder_button.setStyleSheet("font-size: 15px; font-weight: normal; color: #B3B3B3;")
            folder_button.clicked.connect(lambda checked=False, f_id=folder["id"], f_name=folder["name"]: self.load_playlist_tracks_into_viewport(f_id, f_name)) 
            self.playlist_container.addWidget(folder_button)

    def load_playlist_tracks_into_viewport(self, playlist_id: int, playlist_name: str): 
        """Fetches track from SQLite matching the requested index and flips the central card view layout.""" 
        # Update your page headers text properties 
        self.playlist_title_lbl.setText(f" 📁 {playlist_name}") 

        # Clear previous rows from inner layout container 
        while self.track_list_container.count(): 
            item = self.track_list_container.takeAt(0)
            if item is not None: 
                widget = item.widget()
                if widget is not None: 
                    widget.deleteLater() 


        # Pull relational track tables  rows straight out of SQLite  
        tracks = self.db.get_playlist_tracks(playlist_id) 
        if not tracks: 
            empty_lbl = QLabel("This playlist folder is not empty. Search for music and add songs here!")
            empty_lbl.setStyleSheet("color: #A7A7A7; font-style: italic;")
            self.track_list_container.addWidget(empty_lbl)

        else: 
            for track in tracks: 
                track_row = QFrame()
                track_row.setStyleSheet("background-color: #242424; padding:  8px; border-radius: 4px; margin-bottom: 4px;")
                row_layout = QHBoxLayout(track_row) 


                lbl_layout = QVBoxLayout()
                t_lbl = QLabel(track["title"]) 
                t_lbl.setStyleSheet("font-weight: bold; color: white;") 
                


        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer() 

        #Linking player to output channels 
        self.media_player.setAudioOutput(self.audio_output)  
        
       
        # Sync the core volume threshold straight to the hardware driver layout 
        self.audio_output.setVolume(self.state.volume) 

        # Connect state modifiers to interactive player methods 
        self.state.playback_toggled.connect(self.handle_playback_toggle_signal) 
        self.state.volume_mutated.connect(lambda vol: self.audio_output.setVolume(vol))
        self.media_player.durationChanged.connect(self.handle_media_duration_changed) 
        self.media_player.positionChanged.connect(self.handle_media_postion_changed) 

    @Slot(dict) 
    def on_track_mutated(self, track_data: dict): 
        """Track mutation slot listener. 
           Executes terminal tracking telemetry logging and routes direct streaming HTTP CDN link payloads
           straight down to the QMediaPlayer engine 
           
        """
        print(f"[AUDIO CORE] Loading streaming source token: {track_data['title']}") 
        print(f"[UI REACTION] Top-level Main window received stream payload: {track_data['title']}") 

       
        stream_url = track_data.get("url") 
        if stream_url: 
            # Set the media source to the unexpired direct streaming CDN URL Link 
            self.media_player.setSource(QUrl(stream_url))  
            # Command the audio driver to instantly start streaming the buffer array 
            self.media_player.play() 

    @Slot(bool) 
    def handle_playback_toggle_signal(self, should_play: bool): 
        """Intercepts playback state updates and routes commands straight to the engine"""
        if should_play: 
            self.media_player.play() 
        else: 
            self.media_player.pause() 

        

    @Slot(int)
    def handle_media_duration_changed(self,duration_ms: int): 
        """Fires once when a track loads, establishing the slider's max max boundary""" 
        # Convert eaw millisecs down to clean seconds for our slider tracking 
        total_secs = int(duration_ms / 1000) 
        self.player_bar.timeline_slider.setRange(0, total_secs) 

        #sync the text timestamp on the right side of the bar  
        m, s = divmod(total_secs,60) 
        self.player_bar.time_end.setText(f"{m}:{s:02d}") 

    @Slot(int) 
    def handle_media_postion_changed(self, position_ms: int): 
        """Fires continuously during active streaming to animate the slider handle """ 
        current_secs = int(position_ms /  1000) 

        # Block the slider signal to momentarily toa avoid feedback stutter while updating the position 
        self.player_bar.timeline_slider.blockSignals(True) 
        self.player_bar.timeline_slider.setValue(current_secs) 
        self.player_bar.timeline_slider.blockSignals(False) 

        # Sync the running text timer label on left side of the bar 
        m, s = divmod(current_secs, 60) 
        self.player_bar.time_start.setText(f"{m}:{s:02d}") 
        