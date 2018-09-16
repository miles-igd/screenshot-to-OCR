## Screenshot to OCR, and Text Isolator

Given an image with text, and an image without. This will isolate the text and pass it through Tesseract using pytesseract.

#### Prerequisites

```
Python 3.6+
Tesseract 3.05 or 4.00+
```
##### Libraries
```
OpenCV2
pytesseract
numpy
Pillow
pyperclip
```

### Example (WebComic from xkcd.com)
#### Inputs (File #1 and File #2)
![File 1](https://imgs.xkcd.com/comics/complex_numbers.png)
***
![File 2](https://i.imgur.com/t90F4U8.png)
#### Outputs (Boxes and Text)
![Boxes](https://i.imgur.com/8MLWIoY.png)
***
```
-----(0, 0)-----
DOES ANY OF THIS REALLY

HAVE. TO DO WITH THE

SQUARE ROOT OF -1? OR

DO MATHEMATICIANS JUST

THINK THEY'RE T00 COOL

FOR REGULAR VECTORS?
|
-----(196, 0)-----
COMPLEX NUMBERS ARENT JUST VECTORS.
THEYRE A PROFOUND EXTENSION OF REAL
NUMBERS, LAYING THE FOUNDATION FOR THE
FUNDAMENTAL THEOREM OF ALGEBRA AND
THE ENTIRE FIELD OF COMPLEX ANALYSIS.
-----(510, 0)-----
AND WERE TOO COOL.
FOR REGULAR VECTORS.

revi |
rn
```
#### Instructions
```
python app.py

--- WIP ---
```
