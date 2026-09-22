# File Name: core/audio_worker.py
from PySide6.QtCore import QRunnable, QObject, Signal, QThreadPool
from typing import Optional, Dict, Any
import yt_dlp

class WorkerSignals(QObject):
    """Defines callback notification signals for background thread execution pools."""
    result = Signal(dict)       # Fires when track scraping resolves successfully
    error = Signal(str)         # Fires with error details if extraction encounters a network failure

class AudioScrapeWorker(QRunnable):
    """Thread-isolated background task executing synchronous yt_dlp lookups."""
    def __init__(self, query_text: str):
        super().__init__()
        self.query_text = query_text
        self.signals = WorkerSignals()
        
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'skip_download': True,
            'extract_flat': False,
        }

    def run(self) -> None:
        """Execution route triggered inside the background worker thread."""
        search_target = f"ytsearch1:{self.query_text}"
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(search_target, download=False)
                if info and "entries" in info and len(info["entries"]) > 0:
                    target_entry = info["entries"][0]
                    resolved_payload = {
                        "id": target_entry.get('id'),
                        "title": target_entry.get('title', 'Unknown Track'),
                        "duration": float(target_entry.get('duration', 0.0)),
                        "url": target_entry.get('url'),
                        "query": self.query_text
                    }
                    # Thread-safely dispatch data payload back to the main UI frame
                    self.signals.result.emit(resolved_payload)
                else:
                    self.signals.error.emit("No streaming elements resolved.")
        except Exception as e:
            self.signals.error.emit(str(e))
