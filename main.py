import threading
from gui import run_gui

thread_gui = threading.Thread(target=run_gui())

if __name__ == "__name__":
    thread_gui.start()
