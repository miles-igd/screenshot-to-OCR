from tkinter import Tk, Frame, Button, Toplevel

import clipper

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.bind('q', self.startClipper)
        self.frame = Frame(self.master)
        self.clipper_button = Button(self.frame, text='Clipper', width=50, command=self.startClipper)
        self.clipper_button.pack()
        self.frame.pack()

    def startClipper(self, event=None):
        self.clipper_window = Toplevel(self.master, width=self.master.winfo_screenwidth(), height=self.master.winfo_screenheight())
        self.clipper_app = clipper.Clipper(self.clipper_window)


root = Tk()
app = MainWindow(root)
root.mainloop()
