# -- coding: utf-8 --
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
import os, time
from pynput import mouse
from pynput.keyboard import Key, Listener
from cf import x_finale, y_finale, SCREEN_DIR, RELABOR_DIR


class ScreenGrab():
    """Oggetto deputato alla cattura dello schermo"""
    def __init__(self, cords=[]):
        # self.cords sarà una lista di 4 elementi.
        # I primi due sono x e y del punto in cui clicco.
        # Gli ultimi sono x e y calcolati grazie ai parametri che ho messo nel file cf.py
        if not os.path.isdir(SCREEN_DIR):
            os.makedirs(SCREEN_DIR)
        if not os.path.isdir(RELABOR_DIR):
            os.makedirs(RELABOR_DIR)
        self.cords = cords

    def start_screen_grab(self):
        print('Premi F6 per indicare dove inizia la schermata da catturare\n'
              'Premi F9 per riutilizzare le coordinate precedenti')
        with Listener(on_press=self.on_press) as listener:
            listener.join()
        return self.cords

    def on_press(self, key):
        print('{0} pressed'.format(key))
        if key == Key.f6:
            self.cords = []
            self.key_pressed = 'F6'
            self.get_cords_new()
            return False
        if key == Key.f9:
            """Riprende le coordinate dell'ultima schermata catturata"""
            if self.cords:
                self.key_pressed = 'F9'
                return False
            else:
                raise Exception('le coordinate sono vuote!')

    def get_cords_new(self):
        """Si attiva dopo aver premuto F6"""
        # restituisce una lista
        print('Clicca tasto sinistro nell\'angolo in alto a sinistra della domanda.')
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        """Funzione che prende le coordinate del puntatore del mouse prima quando clicchi e poi quando rilasci"""
        if pressed:
            print('Pressed at {0}'.format((x, y)))
            #self.cords.append((x, y))
            self.cords.extend([x, y])
            return False

    def calcolo_spazi_domande_e_risposte(self, x=x_finale, y=y_finale, is_solitario=False):
        # Calcola dove si trovano i rettangoli della domanda e delle risposte
        # restituisce una lista che contiene tre liste
        # 0 coordinate domanda
        # 1 coordinate risposte
        # 2 coordinate domanda + risposte

        # self.cords all'inizio è una lista il cui unico elemento è una tupla con le coordinate del punto cliccato
        #inizio_domande = list(self.cords[0])
        if is_solitario:
            largh = self.cords[2] - self.cords[0]
            altezz = self.cords[3] - self.cords[1]
            print('SOLISSIMO')
            print(self.cords)
            y_in = self.cords[1] + int(altezz * 0.265)
            y_fin = self.cords[1] + int(altezz * 0.914)
            self.cords = self.cords[0], y_in, self.cords[2], y_fin
            self.dimensioni_originali = largh, altezz
            print(self.cords)
        if len(self.cords) < 4:
            inizio_domande = self.cords
            fine_risposte = [self.cords[0] + x, self.cords[1] + y]
            self.cords = inizio_domande + fine_risposte
        return self.cords

    def is_messaggio_errore(self, punto):
        """Questa funzione utilizza un'immagine non tagliata del programma bluestacks"""
        #self.get_punto_msg_errore()
        print('QUANTO COLORI?')
        print(punto)
        colore_centro_risp_errata = self.im.getpixel(punto)
        print(colore_centro_risp_errata)
        if colore_centro_risp_errata == (53, 204, 252):
            print('RISPOSTA SBAGLIATA')
            #self.punto_corretto = self.punto[0], self.punto[1] + self.cords[1]
            return True
        return False

    def get_punto_msg_errore(self):
        """Questa funzione utilizza un'immagine tagliata del programma bluestacks"""
        altezza = self.cords[3] - self.cords[1]
        larghezza = self.cords[2] - self.cords[0]

        y_in = (0.637 * altezza) #+ self.cords[1]
        y_fin = (0.73 * altezza) #+ self.cords[1]

        x_sin = (0.139 * larghezza) #+ self.cords[0]
        x_des = (0.86 * larghezza) #+ self.cords[0]
        self.punto = int(((x_sin + x_des) / 2)), int(((y_in + y_fin) / 2))
        print("punto", self.punto)
        return self.punto



    def screen_grab(self, nome=''):
        box = tuple(self.cords)
        if not nome:
            nome = 'full_snap__'
        self.screenshot_name = (os.path.join(SCREEN_DIR, nome + str(int(time.time())) + '.png'))
        self.im = ImageGrab.grab(box)
        self.im.save(self.screenshot_name, 'PNG')
        #############################
        #box2 = self.cords[0], (self.cords[1] - 200), *self.cords[2:]
        #print('BOX222222')
        #print(box2)
        #print(box)
        #self.im2 = ImageGrab.grab(box2)
        #self.screenshot_name2 = (os.path.join(SCREEN_DIR, nome + str(int(time.time())) + 'copia.png'))
        #self.im2.save(self.screenshot_name2, 'PNG')