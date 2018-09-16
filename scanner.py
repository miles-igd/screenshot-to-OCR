import numpy as np
import cv2
import pytesseract
import util
import threading
import tkinter

from PIL import Image, ImageDraw
from operator import itemgetter
from itertools import groupby, tee, islice, chain, product, zip_longest

def multi_boxer(boxes, img, master, language):
    master.disable()
    master.status_text.set('Starting Tesseract...')
    master.left_pane.output_box.config(state=tkinter.NORMAL)
    master.left_pane.output_box.delete(1.0, tkinter.END)
    master.left_pane.output_box.config(state=tkinter.DISABLED)
    open('output.txt', 'w').close()

    for box in boxes:
        master.status_text.set('Passing: '+str((box[0], box[1])))
        cropped = img.crop((box[0], box[1], box[2], box[3]))
        text = util.fixString(pytesseract.image_to_string(cropped, lang=language))

        with open("output.txt", "a", encoding='utf-8') as out:
            out.write('\n'+'-----'+str((box[0], box[1]))+'-----'+'\n')
            out.write(text)
        master.left_pane.output_box.config(state=tkinter.NORMAL)
        master.left_pane.output_box.insert(tkinter.END, '-----'+str((box[0], box[1]))+'-----'+'\n'+text+'\n')
        master.left_pane.output_box.config(state=tkinter.DISABLED)
    master.status_text.set('Finished.')
    master.enable()


class Boxer:
    def __init__(self, img, threshold, anchor=(0,0)):
        self.anchor = anchor
        self.boxes = scan(img, threshold)
        self.images = []

        if len(self.boxes) > 1:
            for box in self.boxes:
                im = img.crop((box[0][0], box[1][0], box[0][1], box[1][1]))
                self.images.append(Boxer(im, threshold, anchor=(box[0][0]+anchor[0], box[1][0]+anchor[1])))

            self.box = None
            self.image = None
        elif len(self.boxes) == 1:
            box = self.boxes[0]
            self.box = (box[0][0]+anchor[0], box[1][0]+anchor[1], box[0][1]+anchor[0], box[1][1]+anchor[1])

            #im = img.crop(self.box)
            #self.image = im
        else:
            self.box = None
            self.image = None

    def get_boxes(self):
        boxes = self._Get_boxes()
        return list(zip(*[iter(boxes)]*4))

    def _Get_boxes(self):
        boxes = []
        if self.images:
            for image in self.images:
                boxes.append(image._Get_boxes())
        else:
            if self.box:
                boxes.append(self.box)

        return list(chain.from_iterable(boxes))


def _Prev_and_next(iterable):
    prevs, items, nexts = tee(iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

def debug_draw(img, threshold):
    img = img.convert('RGB')
    h_img = img.copy()

    w, h = img.size
    draw = ImageDraw.Draw(img)
    segments = _Scan_w(img, threshold)
    print(segments)

    for segment in segments:
        draw.line([(segment[0], 0), (segment[0], h)], fill=(0,255,0), width=3)
        draw.line([(segment[1], 0), (segment[1], h)], fill=(255,0,0), width=3)

    segments = _Scan_h(h_img, threshold)
    print(segments)

    for segment in segments:
        draw.line([(0, segment[0]), (w, segment[0])], fill=(0,255,0), width=3)
        draw.line([(0, segment[1]), (w, segment[1])], fill=(255,0,0), width=3)

    img.save('debug_draw.png')

def scan(img, threshold, debug = False):
    img = img.convert('RGB')

    w_segments = _Scan_w(img, threshold)
    h_segments = _Scan_h(img, threshold)
    boxes = list(product(w_segments, h_segments))

    return boxes

def _Closing(img):
    img = np.array(img)

    kernel = np.ones((2,2), np.uint8)
    closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    return Image.fromarray(closing)

def _Clean(segments, threshold):
    to_remove = []
    for segment in segments:
        if segment[1] - segment[0] < threshold:
            to_remove.append(segment)

    for removing in to_remove:
        segments.remove(removing)

    return segments

def _Scan_xy(img, threshold, sectors, clean = True):
    ranges = []
    for k,g in groupby(enumerate(sectors),lambda x:x[0]-x[1]):
        group = (map(itemgetter(1),g))
        group = list(map(int,group))
        ranges.append((group[0],group[-1]))

    segments = []

    if not ranges:
        return segments

    current = ranges[0]

    for _, item, nxt in _Prev_and_next(ranges):
        if nxt is None:
            segments.append(current)
            continue

        if nxt[0] - current[1] < threshold:
            current = (current[0], nxt[1])
        else:
            segments.append(current)
            current = nxt

    if clean:
        segments = _Clean(segments, threshold)

    return segments

def _Scan_w(img, threshold, clean = True, close = False):
    columns, rows = img.size

    if close:
        img = _Closing(img)

    sectors = []
    for column in range(columns):
        col_im = img.crop((column, 0, column+1, rows))
        col_hist = col_im.histogram()

        if col_hist[0] > 1:
            sectors.append(column)

    return _Scan_xy(img, threshold, sectors, clean)

def _Scan_h(img, threshold, clean = True, close = False):
    columns, rows = img.size

    if close:
        img = _Closing(img)

    sectors = []
    for row in range(rows):
        row_im = img.crop((0, row, columns, row+1))
        row_hist = row_im.histogram()

        if row_hist[0] > 1:
            sectors.append(row)

    return _Scan_xy(img, threshold, sectors, clean)
