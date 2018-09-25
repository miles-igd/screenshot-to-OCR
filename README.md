## Screenshot to OCR, and Text Isolator

Given an image with text, and an image without. This will isolate the text and pass it through Tesseract using pytesseract.

#### Prerequisites

```
Python 3.6+
Tesseract 3.05 or 4.00+
```
##### Libraries
```
opencv-python
pytesseract
numpy
Pillow
pyperclip
```

### Example (WebComic from xkcd.com)
#### Inputs (File #1 and File #2)
![File 1](https://imgs.xkcd.com/comics/complex_numbers.png)
***
![File 2](https://i.imgur.com/2AY030T.png)
#### Outputs (Boxes and Text)
![Boxes](https://i.imgur.com/I3Sp94d.png)
***
```
-----(0, 0)-----
DOES ANY OF THIS REALLY
HAVE. TO DO WITH THE
SQUARE ROOT OF -1? OR
DO MATHEMATICIANS JUST
THINK THEY'RE T00 COOL
FOR REGULAR VECTORS?
-----(197, 0)-----
COMPLEX NUMBERS ARENT JUST VECTORS.
THEYRE A PROFOUND EXTENSION OF REAL
NUMBERS, LAYING THE FOUNDATION FOR THE
FUNDAMENTAL THEOREM OF ALGEBRA AND
THE ENTIRE FIELD OF COMPLEX ANALYSIS.
-----(511, 0)-----
AND WERE TOO COOL.
FOR REGULAR VECTORS.
-----(517, 58)-----
T KNEW IT!
```
#### Instructions
```
python app.py

--- WIP ---
```
