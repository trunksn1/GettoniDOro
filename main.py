import numpy
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
import pytesseract
import os, time
from cf import SCREEN_DIR, PATH_INSTALLAZIONE_TESSERACT
from mouse_moves import get_cords
from keyboard_moves import start_screen_grab
import webbrowser

"""Per avviare la cattura dello schermo premi F4;
Per ripetere la cattura dello schermo selezionato premi F9"""

def screen_grab(cords):
    if not os.path.isdir(SCREEN_DIR):
        os.makedirs(SCREEN_DIR)
    box = (cords)
    im = ImageGrab.grab(box)
    screenshot_name = (SCREEN_DIR + '\\full_snap__' + str(int(time.time())) +
            '.png')
    print(screenshot_name)
    im.save(screenshot_name, 'PNG')
    return screenshot_name



def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    pytesseract.pytesseract.tesseract_cmd = PATH_INSTALLAZIONE_TESSERACT
    text = pytesseract.image_to_string(Image.open(filename))  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    print (text)
    return text


def ricerca(testo):
    testo_formattato_per_ricerca =  "+".join(testo.split())
    url = "https://www.google.com.tr/search?q={}".format(testo_formattato_per_ricerca)
    webbrowser.open_new_tab(url)



def main():
    while True:
        coordinate = start_screen_grab()
        immagine = screen_grab(coordinate)
        testo = ocr_core(immagine)
        ricerca(testo)





if __name__ == '__main__':
    main()