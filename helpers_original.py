# -- coding: utf-8 --
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
import pytesseract
import os, time
import webbrowser
import time
from cf import SCREEN_DIR, TEST_DIR, PATH_INSTALLAZIONE_TESSERACT, RELABOR_DIR, mult, CHROME
import cv2
import numpy as np
from urllib.parse import quote
import subprocess
from selenium import webdriver

driver = ''

def screen_grab(cords):
    #TODO Dovrebbe funzionare sempre!!!
    if not os.path.isdir(SCREEN_DIR):
        os.makedirs(SCREEN_DIR)
    if not os.path.isdir(RELABOR_DIR):
        os.makedirs(RELABOR_DIR)
    if type(cords) == tuple:
        #Se hai usato F4
        
        #Check OS
        if(os.name=='posix'):
            cords = [x*2 for x in cords]
        
        #Seleziona le coordinate dello schermo
        box = (cords)
        im = ImageGrab.grab(box)

        #Percorso e nome da dare agli screenshot
        if (os.name=='posix'):
            screenshot_name = (SCREEN_DIR + '/full_snap__' + str(int(time.time())) +
                           '.png')
        else:
            screenshot_name = (SCREEN_DIR + '\\full_snap__' + str(int(time.time())) +
                '.png')

        print(screenshot_name)

        #Salva lo screenshot
        im.save(screenshot_name, 'PNG')
        return screenshot_name
    else:
        #Se hai usato F6
        print(cords)
        #PRIMA PARTE PER LE DOMANDE
        #Seleziona le coordinate dello schermo
        box_domande = cords[0]
        im = ImageGrab.grab(box_domande)

        # Percorso e nome da dare agli screenshot
        if (os.name=='posix'):
            screenshot_name_d = (SCREEN_DIR + '/domanda__' + str(int(time.time())) +
                             '.png')
        else:
            screenshot_name_d = (SCREEN_DIR + '\\domanda__' + str(int(time.time())) +
                           '.png')
        print(screenshot_name_d)

        #new_size = (mult * x for x in im.size)
        #im = im.resize(new_size, Image.ANTIALIAS)

        #Salva lo screenshot
        im.save(screenshot_name_d, 'PNG')

        #Altera l'immagine per aiutare l'ocr a riconoscere il testo
        img = perfeziona_immagine(screenshot_name_d)

        #Salva l'immagine rielaborata
        if (os.name=='posix'):
            nomefile_d = TEST_DIR + f'/domanda_{str(int(time.time()))}x.png'
        else:
            nomefile_d = TEST_DIR + f'\\domanda_{str(int(time.time()))}x.png'

        cv2.imwrite(nomefile_d, img)

        # SECONDA PARTE PER LE RISPSOTE
        box_risposte = cords[1]
        im = ImageGrab.grab(box_risposte)
        if (os.name=='posix'):
            screenshot_name_r = (SCREEN_DIR + '/risposta__' + str(int(time.time())) +
                                 '.png')
        else:
            screenshot_name_r = (SCREEN_DIR + '\\risposta__' + str(int(time.time())) +
                           '.png')
        print(screenshot_name_r)

        #new_size = (mult * x for x in im.size)
        #im = im.resize(new_size, Image.ANTIALIAS)

        im.save(screenshot_name_r, 'PNG')
        img = img = perfeziona_immagine(screenshot_name_r)
        if (os.name=='posix'):
            nomefile_r = TEST_DIR + f'/risposta_{str(int(time.time()))}x.png'
        else:
            nomefile_r = TEST_DIR + f'\\risposta_{str(int(time.time()))}x.png'
        cv2.imwrite(nomefile_r, img)

        return nomefile_d, nomefile_r
        #return screenshot_name_d, screenshot_name_r

def perfeziona_immagine(filename):
    #Apre l'immagine con CV2
    img = cv2.imread(os.path.join(SCREEN_DIR, filename))
    #aumenta le dimensioni dell'immagine
    img = cv2.resize(img, None, fx=mult, fy=mult, interpolation=cv2.INTER_CUBIC)

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)

    # Apply blur to smooth out the edges
    img = cv2.GaussianBlur(img, (5, 5), 0)

    # Apply threshold to get image with only b&w (binarization)
    img = cv2.threshold(img, 10, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    #Trovato in https://stackoverflow.com/questions/45549963/how-to-improve-text-extraction-from-an-image
    #img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

    nome_f = RELABOR_DIR + f'\\Rielabor__' + os.path.basename(filename)
    print(filename)
    print(nome_f)

    cv2.imwrite(nome_f, img)
    """
    if 'risposta' in os.path.basename(filename):
        nome_risposta_invertita = RELABOR_DIR + f'\\Rielabor__Invertito' + os.path.basename(filename)
        img = cv2.bitwise_not(img)
        cv2.imwrite(nome_f, img)
    """
    return img



def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    pytesseract.pytesseract.tesseract_cmd = PATH_INSTALLAZIONE_TESSERACT
    text = pytesseract.image_to_string(Image.open(filename))  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    print (text)
    return text


def ricerca(domanda, risposta=''):
    domanda_formattata_per_ricerca =  "+".join(domanda.split())
    if type(risposta) == list:
        r = []
        for risp in risposta:
            if not (risp) or (risp == ' ') :
                continue
            risp = "+".join(risp.split())
            # %22 è nell'url ciò che sostituisce il carattere delle virgolette ""
            r.append('%22{}%22'.format(risp))
        risposta_formattata_per_ricerca = "+OR+".join(r)
    else:
        risposta_formattata_per_ricerca = "+".join(risposta.split())

    base_url= 'https://www.google.com/search?q='
    query_url = "{}+AND+({})".format(domanda_formattata_per_ricerca, risposta_formattata_per_ricerca)
    domanda_url = base_url + "{}".format(domanda_formattata_per_ricerca)
    url = base_url + query_url

    # questa funzione importata da urllib mi fa vedere come il browser interpreta i caratteri dell'url:
    # mi ha fatto capire come mai non comparivano le "" nell'url
    print(quote(url))

    #Apre nella stessa TAB
    """
    webbrowser.get().open_new(domanda_url)  # , new=1, autoraise=True)
    webbrowser.get().open(url, new=0, autoraise=True)
    """

    # TEST
    # lo fa ma è LENTISSIMO
    """
    driver = webdriver.Chrome('E:\ChromeDriverForSelenium\chromedriver.exe')
    driver.set_window_size(900,1080)
    driver.set_window_position(920,0)
    driver.get(url)

    driver2 = webdriver.Chrome('E:\ChromeDriverForSelenium\chromedriver.exe')
    driver2.set_window_size(900, 1080)
    driver2.set_window_position(0, 0)
    driver2.get(domanda_url)
    """
    # Combinato:
    webbrowser.get().open(url, new=0, autoraise=True)
    global driver

    if not driver:
        if(os.name=='posix'):
            driver = webdriver.Chrome('/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome')
        else:
            driver = webdriver.Chrome('E:\ChromeDriverForSelenium\chromedriver.exe')
        
        driver.set_window_size(850, 1080)
        driver.set_window_position(800, 0)
        driver.get(domanda_url)
    else:
        driver.get(domanda_url)


    #subprocess.call([CHROME, '--window-position=0,0', '--new-window', url])
    #subprocess.call([CHROME, '--window-position=1286,0', '--window-size "120,108"', '--new-window', domanda_url])
    #webbrowser.get().open_new(domanda_url)#, new=1, autoraise=True)
    #webbrowser.get().open(domanda_url)

def ocr_test():
    pytesseract.pytesseract.tesseract_cmd = PATH_INSTALLAZIONE_TESSERACT
    for file in os.listdir(os.path.join(SCREEN_DIR, 'test')):
        text = pytesseract.image_to_string(Image.open(  #Image.open prende come secondo parametro lang='ita', non cambia molto
            os.path.join(SCREEN_DIR, 'test', file))) # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
        testo_formattato_per_ricerca = "+".join(text.split())
        url = "https://www.google.com.tr/search?q={}".format(testo_formattato_per_ricerca)
        webbrowser.open_new_tab(url)
        '''
        url = "https://www.bing.com/search?q={}".format(testo_formattato_per_ricerca)
        webbrowser.open_new_tab(url)
        url = "https://duckduckgo.com/?q={}".format(testo_formattato_per_ricerca)
        webbrowser.open_new_tab(url)
        '''
        print(text)
        time.sleep(3)

def tesseract_test():
    pass
