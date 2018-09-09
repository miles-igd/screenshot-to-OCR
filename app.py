from tkinter import filedialog
from tkinter import *
import pyperclip
import pytesseract

import util
import scanner
import clipper

class Main(PanedWindow):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.left_pane = LeftPane(self, orient=VERTICAL, width=250, showhandle=False)
        self.right_pane = RightPane(self, orient=VERTICAL, showhandle=False)

        self.initUI()
        self.initStatus()

    def initStatus(self):
        self.status_text = StringVar()
        self.status_bar = Label(self.master, textvariable=self.status_text, bd=1, relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)

    def initUI(self):
        self.master.title("Text Scanner")
        self.pack(fill=BOTH, expand=1)

class EntryFrame(Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.labels = {}
        self.entries = {}
        self.buttons = {}

        self.initUI()

    def add_entry(self, key):
        self.labels[key] = Label(self, text='key')
        self.entries[key] = Entry(self)
        self.button[key] = Button(self, text='...')

    def initUI(self):
        self.master.add(self)

class ButtonFrame(Frame):
    def __init__(self, root, *args, side=LEFT, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.side = side
        self.items = {}
        self.variables = {}
        self.functions = {}

        self.initUI()

    def add_button(self, key, function=None):
        self.functions[key] = function
        self.items[key] = Button(self, text=key, command=function)
        self.items[key].pack(side=self.side)

    def add_label(self, key):
        self.variables[key] = StringVar()
        self.items[key] = Label(self, textvariable=self.variables[key])
        self.items[key].pack(side=self.side)

    def set_label(self, key, string):
        self.variables[key].set(string)

    def initUI(self):
        self.master.add(self)

class LeftPane(PanedWindow):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.initItems()
        self.initUI()

    def initItems(self):
        self.button_frame = ButtonFrame(self, side=LEFT)
        self.button_frame.add_button('Clipper', lambda:clipper.start(self, self.clipper))
        self.output_box = Text(self)
        self.output_box.config(state=DISABLED)

    def initUI(self):
        self.add(self.button_frame)
        self.add(self.output_box, height=250)
        self.master.add(self)

    def clipper(self, im):
        text = util.fixString(pytesseract.image_to_string(im, lang='jpn'))
        with open("output.txt", "w", encoding='utf-8') as out:
            out.write(text)
        pyperclip.copy(text)

        self.output_box.config(state=NORMAL)
        self.output_box.insert(END, text+'\n')
        self.output_box.config(state=DISABLED)

class RightPane(PanedWindow):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.initItems()
        self.initUI()

    def initItems(self):
        self.button_frame = ButtonFrame(self, side=RIGHT)
        self.button_frame.add_button('Next')
        self.button_frame.add_button('Prev')
        self.button_frame.add_label('Fnum')
        self.button_frame.set_label('Fnum', '0/0')
        self.composite_img = None
        self.composite_box = Canvas(self, image=self.composite_img, bg='white')

    def initUI(self):
        self.add(self.composite_box)
        self.master.add(self)

root = Tk()
app = Main(root)
root.mainloop()
