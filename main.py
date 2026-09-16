from flet.app import app
from flet.controls.page import Page

from core.state import AppState

from core.audio_worker import AudioWorker
from database.manager import BangerWaveDatabase
from ui.layout import BangerWaveLayout


def main(page: Page):
    # 1. Initialize your core system layers inside runtime memory
    state = AppState()
    worker = AudioWorker()
    db = BangerWaveDatabase()

    # 2. Instantiate and assemble your visual multi-pane window framework
    layout = BangerWaveLayout(page, state, worker,db)
    layout.assemble()
    
     
    # 3. Defensive cleanup: intercept the page close event and stop the worker safely
    def handle_close(_event):
        print("[SYSTEM TEARDOWN] Cleaning up background engine worker threads...")
        worker.shutdown()

    page.on_close = handle_close

if __name__ == "__main__":
    app(target=main)
