# File Name: core/state.py
from PySide6.QtCore import QObject, Signal
from typing import Dict, Any, Optional

class AppState(QObject):
    """
    Unified Application State Engine for BangerWave.
    Leverages native Qt Core Signals to implement thread-safe observer tracking
    across background streaming threads and the presentation layer.
    """
    # Define native hardware signals to communicate state updates to the UI safely
    track_changed = Signal(dict)       # Emits a dictionary payload when a new track maps
    playback_toggled = Signal(bool)    # Emits True/False when play/pause updates
    volume_mutated = Signal(float)     # Emits a normalized float (0.0 to 1.0) on volume shift

    def __init__(self):
        super().__init__()
        self.current_track: Optional[Dict[str, Any]] = None
        self.is_playing: bool = False
        self.volume: float = 0.8  # Default audio scale (0.0 to 1.0)

    def update_track(self, track_data: Dict[str, Any]) -> None:
        """Mutates the active track state and broadcasts a safe layout signal notification."""
        self.current_track = track_data
        self.is_playing = True
        self.track_changed.emit(track_data)
        self.playback_toggled.emit(True)

    def set_playing_state(self, playing: bool) -> None:
        """Toggles the stream state flag layer cleanly."""
        if self.is_playing != playing:
            self.is_playing = playing
            self.playback_toggled.emit(playing)

    def set_volume(self, volume_level: float) -> None:
        """Clamps and synchronizes core audio system boundaries."""
        self.volume = max(0.0, min(1.0, volume_level))
        self.volume_mutated.emit(self.volume)
