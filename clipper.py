from tkinter import Tk, Canvas, Frame
from PIL import ImageGrab, Image
import pytesseract
import pyperclip

class Clipper:
    def __init__(self, master):
        self.master = master
        self.master.attributes('-alpha', 0.2)
        self.master.overrideredirect(True)
        self.frame = Canvas(self.master, width=master.winfo_screenwidth(), height=master.winfo_screenheight(), bg='white')
        self.frame.bind("<Button-1>", self.mousePress)
        self.frame.bind("<B1-Motion>", self.mouseMove)
        self.frame.bind("<ButtonRelease-1>", self.mouseDepress)
        self.frame.pack()

    def draw(self, start, end):
        self.frame.delete("all")
        self.frame.create_rectangle(start, end, dash=10, outline='black', width=3)

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
        self.master.destroy()

        left = min(self.start[0], self.end[0])
        upper = min(self.start[1], self.end[1])
        right = max(self.start[0], self.end[0])
        lower = max(self.start[1], self.end[1])

        im = ImageGrab.grab(bbox=(left,upper,right,lower))
        im.save('output.png')

        text = pytesseract.image_to_string(im, lang='jpn')
        with open("output.txt", "w", encoding='utf-8') as out:
            out.write(text)
        print(text)
        pyperclip.copy(text)

#root = Tk()
#clipper = Clipper(root)
#root.mainloop()
