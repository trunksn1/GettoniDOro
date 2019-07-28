# -- coding: utf-8 --
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
import os, time
import cv2
import numpy as np
from cf import mult, SCREEN_DIR, RELABOR_DIR, TEST_DIR, PATH_INSTALLAZIONE_TESSERACT
from selenium import webdriver
import pytesseract
import webbrowser

driver = ''

class Identificatore():
    def __init__(self, lista_files):
        global driver
        self.lista_files = lista_files
        self.driver = driver
        self.avvio_identificazione()
        self.ricerca(self.domanda, self.risposte)

    def avvio_identificazione(self):
        self.risposte = []
        for n, file in enumerate(self.lista_files):
            if n == 0:
                self.domanda = self.ocr_core(file)
            else:
                self.risposte.append(self.ocr_core(file))


    def ocr_core(self, filename):
        """
        This function will handle the core OCR processing of images.
        """
        pytesseract.pytesseract.tesseract_cmd = PATH_INSTALLAZIONE_TESSERACT
        text = pytesseract.image_to_string(Image.open(
            filename))  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
        print(text)
        return text

    def ricerca(self, domanda, risposta=''):
        global driver
        domanda_formattata_per_ricerca = "+".join(domanda.split())
        if type(risposta) == list:
            r = []
            for risp in risposta:
                if not (risp) or (risp == ' '):
                    continue
                risp = "+".join(risp.split())
                # %22 è nell'url ciò che sostituisce il carattere delle virgolette ""
                r.append('%22{}%22'.format(risp))
            risposta_formattata_per_ricerca = "+OR+".join(r)
        else:
            risposta_formattata_per_ricerca = "+".join(risposta.split())

        base_url = 'https://www.google.com/search?q='
        query_url = "{}+AND+({})".format(domanda_formattata_per_ricerca, risposta_formattata_per_ricerca)
        domanda_url = base_url + "{}".format(domanda_formattata_per_ricerca)
        url = base_url + query_url

        # Combinato:
        webbrowser.get().open(url, new=0, autoraise=True)


        if not driver:
            driver = webdriver.Chrome('E:\ChromeDriverForSelenium\chromedriver.exe')
            driver.set_window_size(850, 1080)
            driver.set_window_position(800, 0)
            driver.get(domanda_url)
        else:
            driver.get(domanda_url)