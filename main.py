import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import init_db
from gui.login import LoginWindow
from gui.app import MainApp


def start():
    def on_login_success():
        app = MainApp()
        app.mainloop()

    login = LoginWindow(on_success=on_login_success)
    login.mainloop()


if __name__ == "__main__":
    init_db()
    start()
