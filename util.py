from PIL import Image
import os
from pathlib import Path

def resizeHeight(wsize, image):
    ratio = min(wsize[0]/image.size[0], wsize[1]/image.size[1])
    return image.resize((int(image.size[0]*ratio), int(image.size[1]*ratio)))

def fixString(text):
    text = text.replace('〈', 'く')
    return text

def findLangs():
    if 'TESSDATA_PREFIX' in os.environ:
        root = Path(os.environ['TESSDATA_PREFIX'])
        data = root / 'tessdata'
        langs = list(data.glob('*.traineddata'))
        return [lang.name.replace(lang.suffix, '') for lang in langs]
    else:
        return ('eng', 'jpn')
