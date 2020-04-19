import threading
from program.gui import run_gui
from program import utils

# INIT SOFTWARE
if __name__ == '__main__':
    thread_gui = threading.Thread(target=run_gui, name='thread_gui')

    utils.log_to_file('Program started')
    thread_gui.start()
