import util
import sys
from PIL import Image

fp = sys.argv[1]
#img = cv2.imread(fp)
img = Image.open(fp)
img = util.dilateImage(img)

img.save(fp+'_output.png')
