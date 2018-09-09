from PIL import Image

def resizeHeight(wsize, image):
    ratio = min(wsize[0]/image.size[0], wsize[1]/image.size[1])
    return image.resize((int(image.size[0]*ratio), int(image.size[1]*ratio)))

def fixString(text):
    text = text.replace('〈', 'く')
    return text
