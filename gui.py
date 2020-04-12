from tkinter import *
from datasets import categories
from scraper import Scraper


class NavigationPage(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.geometry("500x500")
        self.title = "Świat Książki - Scraper"

        root = Frame(self)
        root.pack(side="top", fill="both", expand=True)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=0)

        self.frames = {}

        for F in (StartPage, WorkingPage):
            page_name = F.__name__
            frame = F(parent=root, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        Label(self, text='Wybierz kategorię książek, które chcesz pobrać').grid(column=0, columnspan=2, row=0)

        self.selected_category = StringVar()
        self.selected_category.set(None)
        i = 1
        for category in categories.keys():
            Radiobutton(self, text=category, variable=self.selected_category, value=category).grid(row=i, sticky=W)
            i += 1

        self.submit_btn = Button(self, text="Ok", command=self.go_to_working_page)
        self.submit_btn.grid(row=i, sticky=W)

        self.info_lbl = Label(self)
        self.info_lbl['text'] = ''
        self.info_lbl.grid(row=i + 1, sticky=W)

    def go_to_working_page(self):
        if self.selected_category.get() in categories.keys():
            self.controller.show_frame("WorkingPage")
        else:
            self.info_lbl['text'] = 'Musisz wybrać kategorię'


class WorkingPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.create_widgets()

    def create_widgets(self):
        # self.button = Button(self, text="Go to the start page", command=lambda: self.controller.show_frame("StartPage"))
        self.start_scrap_btn = Button(self, text="Go to the start page",
                                      command=lambda: self.controller.show_frame("StartPage"))

        self.start_scrap_btn.grid()

    def start_scraping(self):
        cat = self.selected_category.get()
        scraper = Scraper(cat)
        scraper.run_scraper()


# main
def run_gui():
    app = NavigationPage()
    app.mainloop()
