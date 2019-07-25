import os
SCREEN_DIR = os.path.join(os.getcwd(), 'screenshot')
TEST_DIR = os.path.join(os.getcwd(), 'test')
RELABOR_DIR = os.path.join(os.getcwd(), 'rielaborazioni')
PATH_INSTALLAZIONE_TESSERACT = r'E:\Tesseract-OCR\tesseract.exe'
CHROME = os.path.join('C:\\', 'Program Files (x86)', 'Google', 'Chrome', 'Application', 'chrome.exe')

# Moltiplicatore per Resize dell'immagine
mult = 5

# Dimensione dello screen grab
x_finale = 470

#Dimensione dello screen grab x Domande
y_finale_domande = 140

#Dimensione dello screen grab x Risposte
y_iniziale_risposte = 165
y_finale_risposte = 290