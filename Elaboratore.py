# -- coding: utf-8 --
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
import os, time
import cv2
import numpy as np
from cf import mult, SCREEN_DIR, RELABOR_DIR, taglio_x_sinistra, taglio_x_destra, taglio_y_rielab
from splitanswers import splitanswers


class Elaboratore():
    """Oggetto che prende lo screenshot e lo rielabora ottenendo alla fine 4 diverse immagini in bianco e nero 1 è la domandale altre tre sono le singole risposte"""
    def __init__(self, screenshot_name):
        self.screenshot_name = screenshot_name

        self.perfeziona_immagine()
        print('ELABORIAMO:')
        print(self.screenshot_name)
        self.get_all_cords()
        #self.salva_i_pezzi()


    def perfeziona_immagine(self):
        """Va fatta dopo avere diviso le immagini di domande e risposte"""
        # Apre l'immagine con CV2
        self.img = cv2.imread(os.path.join(SCREEN_DIR, self.screenshot_name))

        height, width = self.img.shape[:2]
        print("Pre misure: ")
        print(height, width)

        # aumenta le dimensioni dell'immagine
        self.img = cv2.resize(self.img, None, fx=mult, fy=mult, interpolation=cv2.INTER_CUBIC)

        # Convert to gray
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        # Apply dilation and erosion to remove some noise
        kernel = np.ones((1, 1), np.uint8)
        self.img = cv2.dilate(self.img, kernel, iterations=1)
        self.img = cv2.erode(self.img, kernel, iterations=1)

        # Apply blur to smooth out the edges
        self.img = cv2.GaussianBlur(self.img, (5, 5), 0)

        # Apply threshold to get image with only b&w (binarization)
        self.img = cv2.threshold(self.img, 10, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # Trovato in https://stackoverflow.com/questions/45549963/how-to-improve-text-extraction-from-an-image
        # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

        # Questa cosa nn serve, tanto l'immagine rielaborata è nella variabile img
        #nome_f = os.path.join(RELABOR_DIR, 'Rielabor__' + os.path.basename(self.screenshot_name))
        #print(self.screenshot_name)
        #print(nome_f)
        #cv2.imwrite(nome_f, self.img)


    def get_all_cords(self):
        # Chiamo la funzione di fabrizio per avere le coordinate delle ordinate delle risposte dell'immagine elaborata
        y_risposte = splitanswers(self.img)
        print('FABRIZIO: ', y_risposte)

        # Controllo subito di avere le coordinate sufficienti dall'immagine rielaborata
        #if not self.are_valid_coords_for_risposte(y_risposte):
        #    self.cords = []
        #    return

        # quanto è grande l'immagine (x e y sono coordinate del punto finale posto in basso a destra)
        y, x = self.img.shape[:2]
        print("punto y = ", y)
        print("punto x =", x)

        try:
            self.cord_r1 = [taglio_x_sinistra, y_risposte[5]+taglio_y_rielab, x-taglio_x_destra, y_risposte[4]-taglio_y_rielab]
            self.cord_r2 = [taglio_x_sinistra, y_risposte[3]+taglio_y_rielab, x-taglio_x_destra, y_risposte[2]-taglio_y_rielab]
            self.cord_r3 = [taglio_x_sinistra, y_risposte[1]+taglio_y_rielab, x-taglio_x_destra, y_risposte[0]-taglio_y_rielab]
            self.cord_d = [0, 0, x, y_risposte[5]]
        except IndexError:
            print('Elaboratore: get_all_cords IndexError')
            self.cords = []
            return
            #self.cord_r1 = [0,0,0,0]
            #self.cord_r2 = [0,0,0,0]
            #self.cord_r3 = [0,0,0,0]
            #try:
            #   self.cord_d = [0, 0, x, y_risposte[5]]
            #except IndexError:
            #   self.cord_d = [0, 0, 0, 0]

        self.cords = [self.cord_d] + [self.cord_r1] + [self.cord_r2] + [self.cord_r3]


    def are_valid_coords_for_risposte(self, coords):
        if len(coords) < 6:
            print('Manca una coordinata delle caselle risposte')
            return False
        elif (coords[0] - coords[1] < 400) or (coords[2] - coords[3] < 400) or (coords[4] - coords[5] < 400):
            print('qualche problema a trovare una casella risposte')
            return False
        return True


    def salva_i_pezzi(self):
        # Input: immagine in bianco e nero elaborata e lista di coordinate delle risposte
        # Output: salvo singolarmente le immagini della domanda e delle 3 risposte
        self.pezzi = []

        for n, cord in enumerate(self.cords):
            # Adesso taglio l'immagine originale nei diversi pezzi grazie alle coordinate ottenute prima
            # la funzione copy() serve perchè altrimenti l'immagine originale viene modificata.
            crop_img = self.img[cord[1]:cord[3], cord[0]:cord[2]].copy()

            if n == 0:
                screenshot_name = os.path.join(SCREEN_DIR, 'domanda__' + str(int(time.time())) + '.png')
            else:
                screenshot_name = os.path.join(SCREEN_DIR, 'risposta_{}__'.format(n) + str(int(time.time())) + '.png')

            print(cord)
            print(screenshot_name)
            self.pezzi.append(screenshot_name)

            # Salva lo screenshot
            cv2.imwrite(screenshot_name, crop_img)



