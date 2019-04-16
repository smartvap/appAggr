# Tesseract Init Script
# wget https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w32-setup-v4.1.0.20190314.exe
# Install tesseract
# Add tesseract.exe path to environment PATH
# Add TESSDATA_PREFIX environment variable, point to Tesseract-OCR\tessdata
# Show version
tesseract -v
# Show support languages
tesseract --list-langs
# install python tesseract
pip install pytesser3
pip install pytesseract
pip install wheel
# wget https://download.lfd.uci.edu/pythonlibs/u2hcgva4/autopy3-0.51.1-cp37-cp37m-win32.whl
pip install 