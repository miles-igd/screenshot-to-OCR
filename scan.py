import scanner
import sys, cv2
from PIL import Image, ImageDraw
from itertools import chain

import util

fp = sys.argv[1]
#img = cv2.imread(fp)
img = Image.open(fp)
img = img.convert('RGB')
draw = ImageDraw.Draw(img)


im = util.dilateImage(img)
boxes = scanner.Boxer(im, 0)
boxes = boxes.get_boxes()

print(boxes)

for box in boxes:
    draw.rectangle(box, outline=(0,255,0))

img.save(fp+'_output.png')
