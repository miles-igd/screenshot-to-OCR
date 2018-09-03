from tkinter import *

import clipper

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.attributes('-topmost',True)
        self.master.bind('q', self.startClipper)

        self.l_pane = PanedWindow(width=300)
        self.l_pane.pack(fill=BOTH, expand=1)

        self.r_pane = PanedWindow(self.l_pane, orient=VERTICAL)
        self.l_pane.add(self.r_pane)

        self.clipper_button = Button(self.r_pane, text='Clipper', command=self.startClipper)
        self.r_pane.add(self.clipper_button)

        self.output_box = Text(self.r_pane)
        self.r_pane.add(self.output_box, height=250)
        self.output_img = None

        self.image_box = Label(self.r_pane, image=self.output_img, bg='white')
        self.r_pane.add(self.image_box, height=250)

    def startClipper(self, event=None):
        self.clipper_window = Toplevel(self.master, width=self.master.winfo_screenwidth(), height=self.master.winfo_screenheight())
        self.clipper_app = clipper.Clipper(self.clipper_window, self)

    def updateImage(self, image):
        self.output_img = image
        self.image_box.configure(image=self.output_img)
        self.image_box.image = self.output_img
        pass

root = Tk()
app = MainWindow(root)
root.mainloop()
