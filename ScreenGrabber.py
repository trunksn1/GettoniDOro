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
    def __init__(self):
        # self.cords sarò una lista di 4 elementi.
        # I primi due sono x e y del punto in cui clicco.
        # Gli ultimi sono x e y calcolati grazie ai parametri che ho messo nel file cf.py
        self.cords = []
        if not os.path.isdir(SCREEN_DIR):
            os.makedirs(SCREEN_DIR)
        if not os.path.isdir(RELABOR_DIR):
            os.makedirs(RELABOR_DIR)

    def start_screen_grab(self):
        print('Premi F6 per indicare dove inizia la schermata da catturare\n'
              'Premi F9 per riutilizzare le coordinate precedenti')
        with Listener(on_press=self.on_press) as listener:
            listener.join()
        return self.cords

    def on_press(self, key):
        print('{0} pressed'.format(key))
        global cords
        if key == Key.f6:
            self.cords = []
            self.key_pressed = 'F6'
            self.get_cords_new()
            return False
        if key == Key.f9:
            """Riprende le coordinate dell'ultima schermata catturata"""
            print(self.cords)
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

    def calcolo_spazi_domande_e_risposte(self,x=x_finale, y=y_finale):
        # Calcola dove si trovano i rettangoli della domanda e delle risposte
        # restituisce una lista che contiene tre liste
        # 0 coordinate domanda
        # 1 coordinate risposte
        # 2 coordinate domanda + risposte

        # self.cords all'inizio è una lista il cui unico elemento è una tupla con le coordinate del punto cliccato
        #inizio_domande = list(self.cords[0])
        inizio_domande = self.cords
        fine_risposte = [self.cords[0] + x, self.cords[1] + y]
        self.cords = inizio_domande + fine_risposte

    def screen_grab(self, nome=''):
        box = (self.cords)
        if not nome:
            nome = 'full_snap__'
        self.screenshot_name = (os.path.join(SCREEN_DIR, nome + str(int(time.time())) + '.png'))
        self.im = ImageGrab.grab(box)
        self.im.save(self.screenshot_name, 'PNG')
