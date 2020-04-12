from tkinter import *


class Gui(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.geometry("500x500")
        self.title = "Świat Książki - Scraper"

    def make_home_frame(self):
        home_frame = Frame(self.root)

        home_frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        page_name == 'startname' ?

        def run_gui():
            Gui()
