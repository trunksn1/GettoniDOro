import os
import cv2
import numpy as np
from cf import mult, SCREEN_DIR, RELABOR_DIR, TEST_DIR



class Elaboratore():
    """Oggetto che prende lo screenshot e lo rielabora ottenendo alla fine 4 diverse immagini in bianco e nero 1 è la domandale altre tre sono le singole risposte"""
    def __init__(self, screenshot_name, coords):
        self.screenshot_name = screenshot_name
        self.coords = coords
        self.perfeziona_immagine()
        print('ELABORIAMO:')
        print(self.screenshot_name)

    def avvio_elaborazione(self):
        # Apre l'immagine con CV2
        self.img = cv2.imread(os.path.join(SCREEN_DIR, self.screenshot_name))

        for n, coord in enumerate(self.coords):
            if n == 0:
                nome = 'Rielabor_domanda__'
            else:
                nome = 'Rielabor_risposta{}__'.format(n)
            self.perfeziona_immagine(nome)


    def perfeziona_immagine(self, nome):
        """Va fatta dopo avere diviso le immagini di domande e risposte"""
        # Apre l'immagine con CV2
        self.img = cv2.imread(os.path.join(SCREEN_DIR, self.screenshot_name))


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

        nome_f = RELABOR_DIR + f'\\Rielabor__' + os.path.basename(self.screenshot_name)
        print(self.screenshot_name)
        print(nome_f)

        cv2.imwrite(nome_f, self.img)
        """
        if 'risposta' in os.path.basename(filename):
            nome_risposta_invertita = RELABOR_DIR + f'\\Rielabor__Invertito' + os.path.basename(filename)
            img = cv2.bitwise_not(img)
            cv2.imwrite(nome_f, img)
        """
        return img

