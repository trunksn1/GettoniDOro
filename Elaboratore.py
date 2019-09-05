# -- coding: utf-8 --
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
import os, time
import cv2
import numpy as np
from cf import mult, SCREEN_DIR, RELABOR_DIR
from splitanswers import splitanswers


class Elaboratore():
    """Oggetto che prende lo screenshot e lo rielabora ottenendo alla fine 4 diverse immagini in bianco e nero 1 è la domandale altre tre sono le singole risposte"""
    def __init__(self, screenshot_name):#, coords):
        self.screenshot_name = screenshot_name
        #self.cords = coords
        self.perfeziona_immagine()
        print('ELABORIAMO:')
        print(self.screenshot_name)
        #print(self.img)
        self.get_all_cords()
        self.salva_i_pezzi()


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

        nome_f = os.path.join(RELABOR_DIR, 'Rielabor__' + os.path.basename(self.screenshot_name))
        print(self.screenshot_name)
        print(nome_f)


        cv2.imwrite(nome_f, self.img)
        """
        if 'risposta' in os.path.basename(filename):
            nome_risposta_invertita = RELABOR_DIR + f'\\Rielabor__Invertito' + os.path.basename(filename)
            img = cv2.bitwise_not(img)
            cv2.imwrite(nome_f, img)
        
        return img
        """


    def get_all_cords(self):
        # Chiamo la funzione di fabrizio per avere le coordinate delle ordinate delle risposte dell'immagine elaborata
        y_risposte = splitanswers(self.img)
        print('FABRIZIO: ', y_risposte)

        # quanto è grande l'immagine (x e y sono coordinate del punto finale posto in basso a destra)
        y, x = self.img.shape[:2]
        print("punto y = ", y)
        print("punto x =", x)

        try:
            self.cord_r1 = [120, y_risposte[5]+100, x-130, y_risposte[4]-100]
            self.cord_r2 = [120, y_risposte[3]+100, x-130, y_risposte[2]-100]
            self.cord_r3 = [120, y_risposte[1]+100, x-130, y_risposte[0]-100]
            self.cord_d = [0, 0, x, y_risposte[5]]
        except IndexError:
            self.cord_r1 = [0,0,0,0]
            self.cord_r2 = [0,0,0,0]
            self.cord_r3 = [0,0,0,0]
            self.cord_d = [0, 0, x, y_risposte[5]]

        self.cords = [self.cord_d] + [self.cord_r1] + [self.cord_r2] + [self.cord_r3]


    def salva_i_pezzi(self):
        # Partendo dall'immagine elaborata e dalla lista di coordinate, salvo singolarmente le immagini della domanda
        # e le immagini delle 3 risposte
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



