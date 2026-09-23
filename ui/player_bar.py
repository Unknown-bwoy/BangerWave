# File Name: ui/player_bar.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSlider, QFrame
from PySide6.QtCore import Qt, Slot

class BangerWavePlayerBar(QFrame):
    """Bottom media console component managing playback state, timeline, and volume scaling."""
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.setObjectName("PlayerBarFrame")
        self.setStyleSheet("""
            QFrame#PlayerBarFrame {
                background-color: #181818;
                border-radius: 12px;
                padding: 10px;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #FFFFFF;
                font-size: 18px;
            }
            QPushButton:hover {
                color: #1DB954;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #404040;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #1DB954;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                width: 10px;
                margin: -3px 0;
                border-radius: 5px;
            }
        """)

        # Main layout flows horizontally (Left info, Center controls, Right volume)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # 1. Left Track Metadata Zone
        left_zone = QWidget()
        left_layout = QVBoxLayout(left_zone)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)
        
        self.title_label = QLabel("No Track Selected")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.artist_label = QLabel("Unknown Artist")
        self.artist_label.setStyleSheet("color: #A7A7A7; font-size: 11px;")
        
        left_layout.addWidget(self.title_label)
        left_layout.addWidget(self.artist_label)

        # 2. Center Playback Controls Zone
        center_zone = QWidget()
        center_layout = QVBoxLayout(center_zone)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(4)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.play_btn = QPushButton("▶")
        self.play_btn.clicked.connect(self.toggle_playback_action)
        btn_row.addWidget(self.play_btn)
        
        # Timeline Slider Row
        timeline_row = QHBoxLayout()
        timeline_row.setContentsMargins(0, 0, 0, 0)
        
        self.time_start = QLabel("0:00")
        self.time_start.setStyleSheet("font-size: 10px; color: #A7A7A7;")
        self.timeline_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeline_slider.setValue(0)
        self.time_end = QLabel("0:00")
        self.time_end.setStyleSheet("font-size: 10px; color: #A7A7A7;")
        
        timeline_row.addWidget(self.time_start)
        timeline_row.addWidget(self.timeline_slider)
        timeline_row.addWidget(self.time_end)

        center_layout.addLayout(btn_row)
        center_layout.addLayout(timeline_row)

        # 3. Right Volume Control Zone
        right_zone = QWidget()
        right_layout = QHBoxLayout(right_zone)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        vol_icon = QLabel("🔊")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFixedWidth(90)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.state.volume * 100))
        self.volume_slider.valueChanged.connect(self.on_volume_slide)
        
        right_layout.addWidget(vol_icon)
        right_layout.addWidget(self.volume_slider)

        # Append zones to main horizontal frame
        layout.addWidget(left_zone, stretch=2)
        layout.addWidget(center_zone, stretch=5)
        layout.addWidget(right_zone, stretch=2)

        # Bind Reactive State Signals
        self.state.track_changed.connect(self.update_track_labels)
        self.state.playback_toggled.connect(self.update_play_icon)

    @Slot(dict)
    def update_track_labels(self, track: dict):
        """Refreshes text fields when the playing track changes."""
        self.title_label.setText(track.get("title", "Unknown Track"))
        self.artist_label.setText("Web Stream Asset")
        duration = track.get("duration", 0)
        m, s = divmod(int(duration), 60)
        self.time_end.setText(f"{m}:{s:02d}")

    @Slot(bool)
    def update_play_icon(self, is_playing: bool):
        """Swaps play/pause symbols based on system execution states."""
        self.play_btn.setText("⏸" if is_playing else "▶")

    def toggle_playback_action(self):
        """Notifies the state engine to switch play/pause parameters."""
        new_state = not self.state.is_playing
        self.state.set_playing_state(new_state)

    def on_volume_slide(self, value: int):
        """Normalizes slider metrics and updates state volume thresholds."""
        normalized = value / 100.0
        self.state.set_volume(normalized)
