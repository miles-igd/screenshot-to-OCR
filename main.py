from pathlib import Path

from tkinter import filedialog
from tkinter import *

from googletrans import Translator

from PIL import ImageTk, Image

import pytesseract
import os
import clipper
import isolate

def resizeHeight(wsize, image):
    ratio = min(wsize[0]/image.size[0], wsize[1]/image.size[1])
    return image.resize((int(image.size[0]*ratio), int(image.size[1]*ratio)))

class MainWindow:
    def __init__(self, master):
        self.translator = Translator()
        self.selected = 0
        self.files = []

        self.master = master
        self.master.bind('q', self.startClipper)

        #self.notebook = ttk.Notebook(self.master)

        self.menu_bar = Menu(self.master)
        self.menu_bar.add_command(label='Quit', command=self.master.quit)
        self.menu_bar.add_command(label='Batch', command=self.batchConvert)
        self.menu_bar.add_command(label='Debug')

        self.option_menu = Menu(self.menu_bar, tearoff=0)
        self.always_on_top_var = IntVar()
        self.use_folder_one_only = IntVar()
        self.option_menu.add_checkbutton(label="Always on Top", command=self.updateAlwaysOnTop, variable=self.always_on_top_var)
        self.option_menu.add_checkbutton(label="Use only one folder", variable=self.use_folder_one_only)
        self.menu_bar.add_cascade(label="Options", menu=self.option_menu)

        self.master.config(menu=self.menu_bar)

        #parent paned
        self.l_pane = PanedWindow(self.master, showhandle=False)
        self.l_pane.pack(fill=BOTH, expand=1)

        #left paned
        self.c_pane = PanedWindow(self.l_pane, orient=VERTICAL, width=250, showhandle=False)
        self.l_pane.add(self.c_pane)

        ###start Buttons
        #button Frame
        self.button_frame = Frame(self.c_pane)
        self.c_pane.add(self.button_frame)

        #clipper Button
        self.clipper_button = Button(self.button_frame, text='Clipper', command=self.startClipper)
        self.clipper_button.pack(side=LEFT)
        #self.c_pane.add(self.clipper_button)

        #clear Button
        self.clear_button = Button(self.button_frame, text='Clear', command=self.clearOutput)
        self.clear_button.pack(side=LEFT)

        #compare Button
        self.compare_button = Button(self.button_frame, text='Compare', command=self.compareDirectories)
        self.compare_button.pack(side=LEFT)

        ###end Buttons
        #image Entries
        self.path_one_frame = Frame(self.c_pane)
        self.path_two_frame = Frame(self.c_pane)

        self.path_one = Label(self.path_one_frame, text='folder one:')
        self.path_one_entry = Entry(self.path_one_frame)
        self.path_one_button = Button(self.path_one_frame, text='...', command=self.setPathOne)

        self.path_two_label = Label(self.path_two_frame, text='folder two:')
        self.path_two_entry = Entry(self.path_two_frame)
        self.path_two_button = Button(self.path_two_frame, text='...', command=self.setPathTwo)

        self.path_one_button.pack(side=RIGHT)
        self.path_one.pack(side=LEFT)
        self.path_one_entry.pack(fill=X)

        self.path_two_button.pack(side=RIGHT)
        self.path_two_label.pack(side=LEFT)
        self.path_two_entry.pack(fill=X)


        self.path_one_entry.insert(0, './one')
        self.path_two_entry.insert(0, './two')
        self.c_pane.add(self.path_one_frame)
        self.c_pane.add(self.path_two_frame)

        #output
        self.output_box = Text(self.c_pane)
        self.output_box.config(state=DISABLED)
        self.c_pane.add(self.output_box, height=250)
        #translated
        self.translate_box = Text(self.c_pane)
        self.translate_box.config(state=DISABLED)
        self.c_pane.add(self.translate_box, height=250)
        self.output_img = None

        self.image_box = Label(self.c_pane, image=self.output_img, bg='white')
        self.c_pane.add(self.image_box, height=250)

        self.r_pane = PanedWindow(width=600, orient=VERTICAL, showhandle=False)
        self.l_pane.add(self.r_pane)

        ###start Buttons
        #button Frame 2
        self.button_frame2 = Frame(self.r_pane)

        #cycle Buttons
        self.next_button = Button(self.button_frame2, text='Next', command=self.cycleNext)
        self.prev_button = Button(self.button_frame2, text='Previous', command=self.cyclePrev)
        self.next_button.pack(side=RIGHT)
        self.prev_button.pack(side=RIGHT)

        #file Label
        self.file_text = StringVar()
        self.file_label = Label(self.button_frame2, textvariable=self.file_text)
        self.file_label.pack(side=RIGHT)

        self.r_pane.add(self.button_frame2)
        ###end Buttons

        #composite Image + mouse event
        self.composite_img = None
        self.composite_box = Canvas(self.r_pane, image=self.composite_img, bg='white')
        self.r_pane.add(self.composite_box)
        self.composite_box.bind("<B1-Motion>", self.mouseMove)

        #self.notebook.add(self.l_pane, text='Compare')
        #self.notebook.pack()

        #automatic
        #self.automatic = Frame(self.notebook)
        #self.notebook.add(self.automatic, text='Automatic')

        #status Bar
        self.status_text = StringVar()
        self.status_bar = Label(self.master, textvariable=self.status_text, bd=1, relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)

    def updateAlwaysOnTop(self):
        if self.always_on_top_var.get() == 0:
            self.master.attributes('-topmost', False)
        else:
            self.master.attributes('-topmost', True)


    def batchConvert(self):
        pass

    def startClipper(self, event=None):
        self.clipper_window = Toplevel(self.master, width=self.master.winfo_screenwidth(), height=self.master.winfo_screenheight())
        self.clipper_app = clipper.Clipper(self.clipper_window, self)

    def clearOutput(self, event=None):
        self.output_box.config(state=NORMAL)
        self.translate_box.config(state=NORMAL)
        self.output_box.delete(1.0, END)
        self.translate_box.delete(1.0, END)
        self.output_box.config(state=DISABLED)
        self.translate_box.config(state=DISABLED)

    def updateImage(self, image):
        self.output_img = image
        self.image_box.configure(image=self.output_img)
        self.image_box.image = self.output_img

    #clean_button
    def setPathOne(self):
        filepath = filedialog.askdirectory(initialdir = os.path.dirname(os.path.abspath(__file__)), title="Select folder")
        if (filepath == ""):
            return None

        self.path_one_entry.delete(0, END)
        self.path_one_entry.insert(0, filepath)

    #raw_button
    def setPathTwo(self):
        filepath = filedialog.askdirectory(initialdir = os.path.dirname(os.path.abspath(__file__)), title="Select folder")
        if (filepath == ""):
            return None

        self.path_two_entry.delete(0, END)
        self.path_two_entry.insert(0, filepath)

    #next_button
    def cycleNext(self):
        if not self.files:
            print('No files loaded')
            return None
        self.selected = (self.selected + 1)%len(self.files)
        self.updateComposite()

    #prev_button
    def cyclePrev(self):
        if not self.files:
            print('No files loaded')
            return None
        self.selected = (self.selected - 1)%len(self.files)
        self.updateComposite()

    def updateOutput(self, text, event=None):
        self.output_box.config(state=NORMAL)
        self.output_box.insert(END, text+'\n'+'------\n')
        self.output_box.config(state=DISABLED)

    def translate(self, text):
        translation = self.translator.translate(text, dest='en')
        print(translation)
        self.translate_box.config(state=NORMAL)
        self.translate_box.insert(END, translation.text+'\n'+'------\n')
        self.translate_box.config(state=DISABLED)

    def mouseMove(self, event):
        self.status_text.set(event)
        #self.status_text.set(('x:',event.x,'y:', event.y))
        pass

    def compareDirectories(self):
        path_one = Path(self.path_one_entry.get())
        path_two = Path(self.path_two_entry.get())
        path_out = Path('./output/')

        if (path_out / '.lock').exists():
            print('Locked')
            self.files = list(path_out.glob('*.png'))
            self.updateComposite()
            return False
        else:
            (path_out / '.lock').touch(exist_ok=True)

        files_one = list(path_one.glob('*.jpg'))
        files_two = list(path_two.glob('*.jpg'))

        file_pairs = []
        for file_one in files_one:
            for file_two in files_two:
                if file_one.name[:3] == file_two.name[:3]:
                    file_pairs.append(isolate.subtract(file_one, file_two, path_out))

        self.files = file_pairs
        self.updateComposite()

    def updateComposite(self):
        self.file_text.set('File: '+str(self.selected+1)+'/'+str(len(self.files)))

        self.composite_box.delete("all")
        im = Image.open(self.files[self.selected])
        text = pytesseract.image_to_string(im, lang='jpn')
        im = resizeHeight((self.composite_box.winfo_width(), self.composite_box.winfo_height()), im)

        self.image_ref = ImageTk.PhotoImage(im)
        self.composite_box.create_image((0,0), image=self.image_ref, anchor=NW)

        text = text.replace('〈', 'く') #convert to right ku
        with open("output.txt", "w", encoding='utf-8') as out:
            out.write(text)
        self.clearOutput()
        self.updateOutput(text)
        self.translate(text)

root = Tk()
app = MainWindow(root)
root.mainloop()
