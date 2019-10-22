# -- coding: utf-8 --
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
from install_settings import PATH_INSTALLAZIONE_TESSERACT
import pytesseract
import threading


class Identificatore():
    def __init__(self, lista_files):
        self.lista_files = lista_files
        self.risposte = []

        self.thread_local = threading.local()

        self.avvio_identificazione()
        self.prepara_url_da_ricercare(self.domanda, self.risposte)

    def avvio_identificazione(self):
        for n, img in enumerate(self.lista_files):
            if n == 0:
                self.domanda = self.ocr_core(img)
            else:
                self.risposte.append(self.ocr_core(img))

    def ocr_core(self, filename):
        """
        This function will handle the core OCR processing of images.
        """
        pytesseract.pytesseract.tesseract_cmd = PATH_INSTALLAZIONE_TESSERACT
        try:
            # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
            text = pytesseract.image_to_string(Image.open(filename), lang='ita')
        except Exception as e:
            print("Problema con il riconoscimento di una delle immagini!")
            print(e)
            text = ''
        print(text)
        return text

    def prepara_url_da_ricercare(self, domanda, risposta):
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
        self.domanda_url = base_url + "{}".format(domanda_formattata_per_ricerca)
        # Indirizzo per domanda + risposte
        self.risp_url = base_url + query_url

        #Punteggiatore([domanda_url, risp_url], risposta)