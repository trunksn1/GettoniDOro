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

class ScreenGrab():
    """Oggetto deputato alla cattura dello schermo"""
    def __init__(self):
        cords = []
        key_pressed = ''
        if not os.path.isdir(SCREEN_DIR):
            os.makedirs(SCREEN_DIR)
        if not os.path.isdir(RELABOR_DIR):
            os.makedirs(RELABOR_DIR)
        self.start_screen_grab()

    def start_screen_grab(self):
        print('Adesso premi F4, F9 o F6 (quest\'ultimo è ancora in fase di test)')
        with Listener(on_press=self.on_press) as listener:
            listener.join()
        return self.cords

    def on_press(self, key):
        print('{0} pressed'.format(key))
        if key == Key.f4:
            """Cliccando col mouse inizi a selezionare lo schermo, rilasci per terminare"""
            self.cords = []
            self.key_pressed = 'F4'
            self.cords = get_cords_old()
            return False
        if key == Key.f6:
            self.cords = []
            self.key_pressed = 'F6'
            self.cords = self.get_cords_new()
            return False
        if key == Key.f9:
            """Riprende le coordinate dell'ultima schermata catturata"""
            if self.cords:
                self.key_pressed = self.key_pressed
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

            cord_domande_risposte_totali = self.calcolo_spazi_domande_e_risposte()
            print(cord_domande_risposte_totali)
            self.cords = cord_domande_risposte_totali
            #return cord_domande_risposte_totali

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

        inizio_domande = list(self.cords[0])
        fine_domande = [self.cords[0][0] + x_finale, self.cords[0][1] + y_finale_domande]
        coordinate_domande = inizio_domande + fine_domande

        inizio_risposte = [inizio_domande[0], fine_domande[1]]
        fine_risposte = [fine_domande[0], inizio_risposte[1] + y_finale_risposte]
        coordinate_risposte = inizio_risposte + fine_risposte

        coordinate_totali = [coordinate_domande, coordinate_risposte, inizio_domande + fine_risposte]

        print("coord_d = ", coordinate_domande)
        print("coord_r = ", coordinate_risposte)
        print("coord_totali = ", coordinate_totali)
        return coordinate_totali
        #return coordinate_domande, coordinate_risposte

    def screen_grab(self, cords):
        # TODO Dovrebbe funzionare sempre!!!

        # Voglio che salvi sempre l'immagine con la domanda completa!
        # Sia usando F4 che F6.
        # se uso F4 perà voglio fare l'analisi dello screen senza che subisca modifiche
        box = (self.cords[2])
        screenshot_name = (SCREEN_DIR + '\\full_snap__' + str(int(time.time())) +
                           '.png')<
        self.screen_shot(box, screenshot_name)

        if self.key_pressed == 'F4':  
            # Se hai usato F4

            # Seleziona le coordinate dello schermo
            box = (self.cords[2])
            screenshot_name = (SCREEN_DIR + '\\full_snap__' + str(int(time.time())) +
                               '.png')
            self.screen_shot(box, screenshot_name)

            """
            im = ImageGrab.grab(box)

            # Percorso e nome da dare agli screenshot
            screenshot_name = (SCREEN_DIR + '\\full_snap__' + str(int(time.time())) +
                               '.png')
            print(screenshot_name)

            # Salva lo screenshot
            im.save(screenshot_name, 'PNG')
            return screenshot_name
            """
        elif self.key_pressed == 'F6':
            # Se hai usato F6
            print(cords)
            # PRIMA PARTE PER LE DOMANDE
            # Seleziona le coordinate dello schermo
            box_domande = self.cords[0]
            im = ImageGrab.grab(box_domande)

            # Percorso e nome da dare agli screenshot
            screenshot_name_d = (SCREEN_DIR + '\\domanda__' + str(int(time.time())) +
                                 '.png')
            print(screenshot_name_d)

            # new_size = (mult * x for x in im.size)
            # im = im.resize(new_size, Image.ANTIALIAS)

            # Salva lo screenshot
            im.save(screenshot_name_d, 'PNG')

            # Altera l'immagine per aiutare l'ocr a riconoscere il testo
            img = perfeziona_immagine(screenshot_name_d)

            # Salva l'immagine rielaborata
            nomefile_d = TEST_DIR + f'\\domanda_{str(int(time.time()))}x.png'
            cv2.imwrite(nomefile_d, img)

            # SECONDA PARTE PER LE RISPSOTE
            box_risposte = self.cords[1]
            im = ImageGrab.grab(box_risposte)
            screenshot_name_r = (SCREEN_DIR + '\\risposta__' + str(int(time.time())) +
                                 '.png')
            print(screenshot_name_r)

            # new_size = (mult * x for x in im.size)
            # im = im.resize(new_size, Image.ANTIALIAS)

            im.save(screenshot_name_r, 'PNG')
            img = img = perfeziona_immagine(screenshot_name_r)

            nomefile_r = TEST_DIR + f'\\risposta_{str(int(time.time()))}x.png'
            cv2.imwrite(nomefile_r, img)

            return nomefile_d, nomefile_r
            # return screenshot_name_d, screenshot_name_r

    def screen_shot(self, box, screenshot_name):
        im = ImageGrab.grab(box)
        im.save(screenshot_name, 'PNG')
