from tkinter import *
from program.datasets import categories
from program.scraper import run_scraper
from program.utils import log_to_file


class Gui:
    root = None
    logs_string = ''

    def __init__(self):
        self.root = Tk()
        self.root.title = "Świat Książki - Scraper"

        self.show_frame('home_frame')

    def get_home_frame(self):
        home_frame = Frame(self.root)
        home_frame.grid(row=0, column=0, sticky="nsew")

        Label(home_frame, text='Wybierz kategorię książek, które chcesz pobrać').grid(column=0, columnspan=2, row=0)

        self.selected_category = StringVar()
        self.selected_category.set(None)
        i = 1
        for category in categories.keys():
            Radiobutton(home_frame, text=category, variable=self.selected_category, value=category).grid(row=i,
                                                                                                         sticky=W)
            i += 1

        submit_btn = Button(home_frame, text="Ok", command=lambda: self.show_frame('working_frame'))
        submit_btn.grid(row=i, sticky=W)

        info_lbl = Label(home_frame)
        info_lbl['text'] = ''
        info_lbl.grid(row=i + 1, sticky=W)

        return home_frame

    def get_working_frame(self):
        working_frame = Frame(self.root)
        working_frame.grid(row=0, column=0, sticky="nsew")
        Label(working_frame, text="Logi programu").grid(row=0, column=0, columnspan=2)
        self.logs_area = Text(working_frame, width=90, height=10, wrap=WORD)
        self.logs_area.grid(row=1, column=0, columnspan=2)

        # Call scrapper to work
        if self.selected_category:
            self.run_btn = Button(working_frame, text='Start',
                             command=lambda: run_scraper(str(self.selected_category.get()), self))
            self.run_btn.grid(row=2, sticky=W)
        else:
            log_to_file('Something went wrong with "selected_category"')
            self.push_log_status('Wystąpił problem z wybraną kategorią. Wyłącz program i spróbuj ponownie')

        self.turn_comp_off = BooleanVar()
        Checkbutton(
            working_frame,
            text='Wyłącz komputer po zakończeniu',
            variable=self.turn_comp_off).grid(row=3, column=0, sticky=E)

        return working_frame

    def show_frame(self, frame_name: str):
        if frame_name == 'working_frame':
            frame = self.get_working_frame()
            frame.tkraise()
        else:
            frame = self.get_home_frame()
            frame.tkraise()

    def push_log_status(self, status: str):
        self.logs_string += (status + "\n")
        self.logs_area.delete(0.0, END)
        self.logs_area.insert(0.0, self.logs_string)
        self.logs_area.see(END)


def run_gui():
    gui = Gui()
    gui.root.mainloop()
