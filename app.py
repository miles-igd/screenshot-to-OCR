from pathlib import Path
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
from PIL import Image, ImageTk, ImageDraw
import pyperclip
import pytesseract
import os
import json
import cv2
import numpy as np
import threading


import util
import scanner
import clipper
import subtractor

class Main(PanedWindow):
    def __init__(self, root, window, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.window = window

        self.left_pane = LeftPane(self, orient=VERTICAL, width=250, showhandle=False)
        self.right_pane = RightPane(self, orient=VERTICAL, showhandle=False)
        self.items = [self.left_pane.button_frame, self.left_pane.entry_frame, self.right_pane.button_frame]

        self.initUI()
        self.initStatus()

    def disable(self):
        for item in self.items:
            item.disable()

    def enable(self):
        for item in self.items:
            item.enable()

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
        self.bframes = {}
        self.frames = {}
        self.labels = {}
        self.entries = {}
        self.buttons = {}

        self.items = {}

        self.initUI()

    def add_button_frame(self, key, sid):
        self.bframes[key] = ButtonFrame(self, side=LEFT)
        self.bframes[key].pack(side=TOP)

    def add_button(self, framekey, key, func=None):
        self.items[key] = self.bframes[framekey].add_button(key, function=func)

    def add_entry(self, key):
        self.frames[key] = Frame(self)
        self.labels[key] = Label(self.frames[key], text=key)
        self.entries[key] = Entry(self.frames[key])
        self.buttons[key] = Button(self.frames[key], text='...', command=lambda:self.set_path(key))

        self.set_entry(key, './'+key+'/')
        self.frames[key].pack(side=TOP, fill=X)
        self.labels[key].pack(side=LEFT)
        self.buttons[key].pack(side=RIGHT)
        self.entries[key].pack(fill=X)

    def disable(self):
        for key in self.bframes:
            self.bframes[key].disable()

    def enable(self):
        for key in self.bframes:
            self.bframes[key].enable()

    def set_entry(self, key, text):
        self.entries[key].delete(0, END)
        self.entries[key].insert(0, text)

    def set_path(self, key):
        filepath = filedialog.askdirectory(initialdir = os.path.dirname(os.path.abspath(__file__)), title="Select folder")
        if (filepath == ""):
            return None

        self.set_entry(self, key, filepath)

    def get_path(self, key):
        return self.entries[key].get()

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

    def add_combobox(self, key, vals, bindings=()):
        self.items[key] = ttk.Combobox(self, width=4, values=vals)

        if bindings:
            self.functions[key] = bindings[1]
            self.items[key].bind(bindings[0], self.functions[key])

        self.items[key].pack(side=self.side)

    def set_combobox(self, key, value):
        self.items[key].set(value)

    def add_entry(self, key, bindings=()):
        self.items[key] = Entry(self)

        if bindings:
            self.functions[key] = bindings[1]
            self.items[key].bind(bindings[0], self.functions[key])

        self.items[key].pack(side=self.side)

    def get_entry(self, key):
        return self.items[key].get()

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

    def disable(self):
        for key in self.items:
            self.items[key].config(state=DISABLED)

    def enable(self):
        for key in self.items:
            self.items[key].config(state=NORMAL)

    def initUI(self):
        if hasattr(self.master, 'add'):
            self.master.add(self)
        else:
            pass

class LeftPane(PanedWindow):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.lang = self.master.window.properties['lang']

        self.choices = util.findLangs()
        self.initItems()
        self.initUI()

    def initItems(self):
        self.button_frame = ButtonFrame(self, side=LEFT)
        self.button_frame.add_button('Clipper', lambda:clipper.start(self, self.clipper))
        self.button_frame.add_button('Clear', self.clear)
        self.button_frame.add_label('Lang')
        self.button_frame.set_label('Lang', 'lang:')
        self.button_frame.add_combobox('Language', self.choices, ('<<ComboboxSelected>>', self.update_properties))
        self.button_frame.set_combobox('Language', self.lang)

        self.entry_frame = EntryFrame(self)
        self.entry_frame.add_entry('FP1')
        self.entry_frame.add_entry('FP2')
        self.entry_frame.add_button_frame('ButtonFrame', CENTER)
        self.entry_frame.add_button('ButtonFrame', 'Process Paths', self.process_thread)
        self.entry_frame.add_button('ButtonFrame', 'Copy Output')
        self.output_box = Text(self)
        self.output_box.config(state=DISABLED)

    def initUI(self):
        self.add(self.button_frame)
        self.add(self.output_box, height=250)
        self.master.add(self)

    def update_properties(self, event):
        self.master.window.properties['lang'] = event.widget.get()

    def process_thread(self):
        threading.Thread(target=self.process).start()

    def process(self):
        self.master.right_pane.selected = 0
        self.master.disable()
        self.master.status_text.set('Processing...')
        fp_one = Path(self.entry_frame.get_path('FP1'))
        fp_two = Path(self.entry_frame.get_path('FP2'))
        fp_out = Path('./output/')
        fp_out.mkdir(exist_ok=True)

        if (fp_out / '.lock').exists():
            self.master.status_text.set('./output/.lock exists. ..loading from ./output/')
            file_list = list(fp_out.glob('*.png'))
            mask_files = {}
            for file in file_list:
                mask_files[file.name[:3]] = file

            orig_files = {}
            boxes = {}
            if (fp_out / 'boxes.json').exists():
                with open((fp_out / 'boxes.json'), "r") as file:
                    boxes = json.load(file)
            else:
                for filename, filepath in mask_files.items():
                    img = Image.open(filepath)
                    width, height = img.size
                    img = util.dilateImage(img)
                    boxer = scanner.Boxer(img, 0)
                    boxes[filename] = boxer.get_boxes()
                with open((fp_out / 'boxes.json'), "w") as file:
                    json.dump(boxes, file)

            if (fp_out / 'orig.json').exists():
                with open((fp_out / 'orig.json'), "r") as file:
                    orig_files = json.load(file)

            self.master.right_pane.boxes = boxes
            self.master.right_pane.orig_files = orig_files
            self.master.right_pane.files = mask_files
            self.master.right_pane.update_composite()
            return False
        else:
            (fp_out / '.lock').touch(exist_ok=True)

        files_one = list(fp_one.glob('*.jpg')) + list(fp_one.glob('*.png')) + list(fp_one.glob('*.bmp')) + list(fp_one.glob('*.psd'))
        files_two = list(fp_two.glob('*.jpg')) + list(fp_two.glob('*.png')) + list(fp_two.glob('*.bmp')) + list(fp_two.glob('*.psd'))

        orig_files = {}
        mask_files = {}
        for file_one in files_one:
            for file_two in files_two:
                if file_one.name[:3] == file_two.name[:3]:
                    orig_files[file_one.name[:3]] = (str(file_one), str(file_two))
                    mask_files[file_one.name[:3]] = subtractor.subtract(file_one, file_two, fp_out)

        boxes = {}
        for filename, filepath in mask_files.items():
            img = Image.open(filepath)
            width, height = img.size
            img = util.dilateImage(img)
            boxer = scanner.Boxer(img, 0)
            boxes[filename] = boxer.get_boxes()

        with open((fp_out / 'boxes.json'), "w") as file:
            json.dump(boxes, file)

        with open((fp_out / 'orig.json'), "w") as file:
            json.dump(orig_files, file)

        self.master.right_pane.boxes = boxes
        self.master.right_pane.orig_files = orig_files
        self.master.right_pane.files = mask_files
        self.master.right_pane.update_composite()
        self.master.enable()
        self.master.status_text.set('Processing success')

    def clear(self):
        self.output_box.config(state=NORMAL)
        self.output_box.delete(1.0, END)
        self.output_box.config(state=DISABLED)

    def clipper(self, im):
        try:
            text = pytesseract.image_to_string(im, lang=self.master.window.properties['lang'])
            if self.master.window.properties['lang'] in ['jpn', 'jpn_vert']:
                text = util.fixString(text)
        except pytesseract.pytesseract.TesseractError as e:
            self.master.status_text.set(str(e))
            self.master.enable()
            return None

        with open("output.txt", "w", encoding='utf-8') as out:
            out.write(text)
        pyperclip.copy(text)

        self.output_box.config(state=NORMAL)
        self.output_box.insert(END, text+'\n')
        self.output_box.config(state=DISABLED)
        self.master.enable()

class RightPane(PanedWindow):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.boxes = {}
        self.orig_files = {}
        self.files = {}
        self.selected = 0
        self.initItems()
        self.initUI()

    def initItems(self):
        self.button_frame = ButtonFrame(self, side=RIGHT)
        self.button_frame.add_button('Next', self.cycle_next)
        self.button_frame.add_button('Prev', self.cycle_prev)
        self.button_frame.add_label('Fnum')
        self.button_frame.set_label('Fnum', 'File: None')
        self.button_frame.add_entry('Index', bindings=('<Return>', self.index_entry))
        self.composite_img = None
        self.composite_box = Canvas(self, image=self.composite_img, bg='white')

    def initUI(self):
        self.add(self.composite_box)
        self.master.add(self)

    def index_entry(self, event):
        try:
            self.selected = int(self.button_frame.get_entry('Index')) - 1
            list(self.files.items())[self.selected]
        except (ValueError, IndexError) as e:
            self.master.status_text.set(str(e))
            return e

        self.update_composite()

    def cycle_next(self):
        if not self.files:
            self.master.status_text.set('No files processed or ./output/ is empty. Process some files first.')
            return None
        self.selected = (self.selected + 1)%len(self.files)
        self.update_composite()

    def cycle_prev(self):
        if not self.files:
            self.master.status_text.set('No files processed or ./output/ is empty. Process some files first.')
            return None
        self.selected = (self.selected - 1)%len(self.files)
        self.update_composite()

    def update_composite(self):
        if not self.files:
            self.master.status_text.set('./output/ is empty and ./output/.lock exists. Delete /output/ folder')
            self.master.enable()
            return None

        if not type(self.selected) is int:
            self.master.status_text.set('Error: index must be int, not '+str(type(self.selected)))
            self.master.enable()
            return None

        self.button_frame.set_label('Fnum', 'File: '+str(self.selected+1)+'/'+str(len(self.files)))

        self.composite_box.delete("all")

        key, value = list(self.files.items())[self.selected]

        im = Image.open(value)
        im = im.convert('RGB')
        width, height = im.size

        if self.orig_files:
            fp_one, fp_two = self.orig_files[key]
            orig = Image.open(fp_one)
            threading.Thread(target=scanner.multi_boxer, args=(self.boxes[key], orig, self.master, self.master.window.properties['lang']), kwargs = {'fix': self.master.window.properties['lang'] in ['jpn', 'jpn_vert']}).start()
        else:
            threading.Thread(target=scanner.multi_boxer, args=(self.boxes[key], im, self.master, self.master.window.properties['lang']), kwargs = {'fix': self.master.window.properties['lang'] in ['jpn', 'jpn_vert']}).start()

        img = np.array(im)
        font = cv2.FONT_HERSHEY_SIMPLEX
        for box in self.boxes[key]:
            cv2.putText(img, str((box[0], box[1])), (box[0], box[1]-15), font, width*0.001, (255,0,0), 2, cv2.LINE_AA)
            cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0,255,0), 4)

        img = Image.fromarray(img)
        reim = util.resizeHeight((self.composite_box.winfo_width(), self.composite_box.winfo_height()), img)

        self.image_ref = ImageTk.PhotoImage(reim)
        self.composite_box.create_image((0,0), image=self.image_ref, anchor=NW)

        if self.orig_files:
            fp_one, fp_two = self.orig_files[key]
            orig = Image.open(fp_one)
            orig = util.resizeHeight((self.composite_box.winfo_width(), self.composite_box.winfo_height()), orig)
            self.orig_ref = ImageTk.PhotoImage(orig)
            self.composite_box.create_image((reim.size[0],0), image=self.orig_ref, anchor=NW)

        return True

class Window():
    def __init__(self):
        self.root = Tk()
        if Path('properties.json').exists():
            with open('properties.json', "r") as file:
                self.properties = json.load(file)
        else:
            self.properties = {'lang': 'eng', 'FP1': './FP1', 'FP2': './FP2'}
        self.app = Main(self.root, self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open('properties.json', "w") as file:
            json.dump(self.properties, file)

with Window() as window:
    window.root.mainloop()
