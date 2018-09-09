from tkinter import *
from PIL import ImageGrab, Image, ImageTk

def start(root, re_func, event=None):
    clipper_window = Toplevel(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
    clipper_app = Clipper(clipper_window, re_func, width=root.winfo_screenwidth(), height=root.winfo_screenheight())

class Clipper(Canvas):
    def __init__(self, root, re_func, *args, alpha=0.2, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.return_function = re_func
        self.initItems(alpha)
        self.initUI()

    def initItems(self, alpha):
        self.master.attributes('-alpha', alpha)
        self.master.attributes('-topmost', True)
        self.master.overrideredirect(True)

        self.bind("<Button-1>", self.mousePress)
        self.bind("<B1-Motion>", self.mouseMove)
        self.bind("<ButtonRelease-1>", self.mouseDepress)

    def initUI(self):
        self.pack()

    def draw(self, start, end):
        self.delete("all")
        self.create_rectangle(start, end, dash=10, outline='black', width=3)

    def mousePress(self, event):
        self.start = (event.x, event.y)
        self.end = self.start
        self.draw(self.start, self.end)

    def mouseMove(self, event):
        self.end = (event.x, event.y)
        self.draw(self.start, self.end)

    def mouseDepress(self, event):
        self.end = (event.x, event.y)
        self.draw(self.start, self.end)

        left = min(self.start[0], self.end[0])
        upper = min(self.start[1], self.end[1])
        right = max(self.start[0], self.end[0])
        lower = max(self.start[1], self.end[1])

        im = ImageGrab.grab(bbox=(left,upper,right,lower))
        self.return_function(im)
        self.master.destroy()
