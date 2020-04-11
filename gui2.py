from tkinter import *


class Gui:
    root = None

    def make_root(self):
        self.root = Tk()
        self.root.geometry("500x500")
        self.root.title("Test window title")

    def make_home_frame(self):
        home_frame = Frame(self.root)

        home_frame.grid(row=0, column=0, sticky="nsew")


    def show_frame(self, page_name):
        page_name == 'startname' ? 

def run_gui():
    Gui()
