# -- coding: utf-8 --
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
import os, time, threading
import cv2
import numpy as np
from cf import mult, SCREEN_DIR, RELABOR_DIR, TEST_DIR, PATH_INSTALLAZIONE_TESSERACT, WEBDRIVER_PATH, \
    coordinate_browser, dimensioni_browser, USER_AGENT
from selenium import webdriver
import pytesseract
import webbrowser
from Mostratore import Mostratore

driver = ''
drivers = None

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

        # Indirizzo della sola domanda
        domanda_url = base_url + "{}".format(domanda_formattata_per_ricerca)
        # Indirizzo per domanda + risposte
        risp_url = base_url + query_url
        """
        # Funziona, prova a usare il multithreading con due selenium per velocizzare
        # Combinato:
        start_time = time.time()
        webbrowser.get().open(risp_url, new=0, autoraise=True)

        if not driver:
            driver = webdriver.Chrome(WEBDRIVER_PATH)
            driver.set_window_size(*dimensioni_browser)
            driver.set_window_position(*coordinate_browser)
            driver.get(domanda_url)
        else:
            driver.get(domanda_url)

        duration = time.time() - start_time
        print('Duration: ', duration)
        Mostratore([domanda_url, risp_url], risposta)
        """
        # Funziona anche questa, ma non c'è chissà che vantaggio in termini di tempo, siamo veramente simili
        from multiprocessing.dummy import Pool as ThreadPool
        global drivers
        start_time = time.time()
        pool = ThreadPool(4)
        if not drivers:
            coordinate_dr = [(0,0), (1000,0)]
            drivers = pool.map(self.set_driver, coordinate_dr)
            #print('drivers:\n', drivers)
        pool.map(self.open_website, [(domanda_url, drivers[0]), (risp_url, drivers[1])])
        duration = time.time() - start_time
        print('Durata: ', duration)
        Mostratore([domanda_url, risp_url], risposta)
        

    def set_driver(self, coordinate_browser):
        driver = webdriver.Chrome(WEBDRIVER_PATH)
        driver.set_window_size(*dimensioni_browser)
        driver.set_window_position(*coordinate_browser)
        return driver


    def open_website(self, sito_e_driver):
        print(sito_e_driver)
        sito_e_driver[1].get(sito_e_driver[0])
