# File Name: main.py
import sys
from PySide6.QtWidgets import QApplication
from core.state import AppState
from database.manager import BangerWaveDatabase
from ui.main_window import BangerWaveMainWindow

def main():
    # 1. Initialize native Qt Core Application infrastructure
    app = QApplication(sys.argv)
    
    # 2. Boot up your non-UI logic layers inside core memory registers
    state = AppState()
    db = BangerWaveDatabase()
    
    # 3. Instantiate and render the architectural master interface layout window
    window = BangerWaveMainWindow(state, db)
    window.show()
    
    # 4. Hand execution over to the native cross-platform OS thread processing loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


