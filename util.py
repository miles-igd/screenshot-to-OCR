from PIL import Image
import cv2
import os
import numpy as np
from pathlib import Path

def resizeHeight(wsize, image):
    ratio = min(wsize[0]/image.size[0], wsize[1]/image.size[1])
    return image.resize((int(image.size[0]*ratio), int(image.size[1]*ratio)))

def fixString(text):
    text = text.replace('〈', 'く')
    text = text.replace(' ', '')
    text = text.replace(':', '.')
    return text

def dilateImage(img):
    img = np.array(img)
    closek = np.ones((2,2),np.uint8)
    dilation = cv2.dilate(img,closek,iterations = 1)
    kernel = np.ones((27,27),np.uint8)
    erosion = cv2.erode(dilation,kernel,iterations = 1)
    img = Image.fromarray(erosion)
    return img

def findLangs():
    if 'TESSDATA_PREFIX' in os.environ:
        data = Path(os.environ['TESSDATA_PREFIX'])
        langs = list(data.glob('*.traineddata'))
        return [lang.name.replace(lang.suffix, '') for lang in langs]
    else:
        return ('eng', 'jpn', 'jpn_vert')
