# -- coding: utf-8 --
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
import cv2
import numpy as np
import pytesseract
import webbrowser
import os, time
from pynput import mouse
from pynput.keyboard import Key, Listener
from selenium import webdriver
from cf import x_finale, y_finale_risposte, y_iniziale_risposte, y_finale_domande, SCREEN_DIR, RELABOR_DIR, TEST_DIR
from splitanswers import splitanswers

cords = []

class ScreenGrab():
    """Oggetto deputato alla cattura dello schermo"""
    def __init__(self):
        global cords
        self.cords = cords
        key_pressed = ''
        if not os.path.isdir(SCREEN_DIR):
            os.makedirs(SCREEN_DIR)
        if not os.path.isdir(RELABOR_DIR):
            os.makedirs(RELABOR_DIR)
        self.start_screen_grab()
        self.screen_grab()
        #self.get_all_cords()

    def start_screen_grab(self):
        print('Adesso premi F4, F9 o F6 (quest\'ultimo è ancora in fase di test)')
        with Listener(on_press=self.on_press) as listener:
            listener.join()
        return self.cords

    def on_press(self, key):
        print('{0} pressed'.format(key))
        global cords
        if key == Key.f6:
            cords = []
            self.key_pressed = 'F6'
            self.get_cords_new()
            return False
        if key == Key.f9:
            """Riprende le coordinate dell'ultima schermata catturata"""
            print(self.cords)
            if cords:
                self.key_pressed = 'F9'
                return False
        if key == Key.f7:
            """Per testare"""
            ## ocr_test()
            self.key_pressed = 'F7'
            return False

    def get_cords_new(self):
        """Si attiva dopo aver premuto F6"""
        # restituisce una lista
        print('Clicca tasto sinistro nell\'angolo in alto a sinistra della domanda.')
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

            self.calcolo_spazi_domande_e_risposte()


    def on_click(self, x, y, button, pressed):
        """Funzione che prende le coordinate del puntatore del mouse prima quando clicchi e poi quando rilasci"""

        if pressed:
            print('Pressed at {0}'.format((x, y)))
            self.cords.append((x, y))
        else:
            print('Released at {0}'.format((x, y)))
            #self.cords.append((x, y))
            return False

    def calcolo_spazi_domande_e_risposte(self):
        # Calcola dove si trovano i rettangoli della domanda e delle risposte
        # restituisce una lista che contiene tre liste
        # 0 coordinate domanda
        # 1 coordinate risposte
        # 2 coordinate domanda + risposte
        global cords
        inizio_domande = list(self.cords[0])
        fine_risposte = [self.cords[0][0] + x_finale, self.cords[0][1] + y_finale_domande + y_finale_risposte]
        self.cords = inizio_domande + fine_risposte
        cords = self.cords
        print(self.cords)



    def screen_grab(self, nome=''):
        # TODO Dovrebbe funzionare sempre!!!


        box = (self.cords)# cords[0][2] è la lista che contiene le coordinate dello schermo con domande + risposte

        nome = '\\full_snap__'

        self.screenshot_name = (SCREEN_DIR + nome + str(int(time.time())) + '.png')
        self.im = ImageGrab.grab(box)
        self.im.save(self.screenshot_name, 'PNG')
        #self.im = cv2.imread(os.path.join(SCREEN_DIR, self.screenshot_name))



