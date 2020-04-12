import threading
from gui import run_gui
from utils import log_to_file

# INIT SOFTWARE
if __name__ == "__name__":
    log_to_file('Program started')
    thread_gui = threading.Thread(target=run_gui())
    log_to_file('GUI thread started')
    thread_gui.start()
