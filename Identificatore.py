# -- coding: utf-8 --
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
from install_settings import PATH_INSTALLAZIONE_TESSERACT
import pytesseract
import threading
from paroleparole import inutili
import concurrent.futures
from time import time

class Identificatore():
    def __init__(self, lista_files):
        self.lista_files = lista_files
        self.risposte = []

        self.thread_local = threading.local()

        #   Prova del 30/11/2019
        start = time()
        #self.avvio_identificazione()
        self.avvia_identificazione_mp()
        print(time()-start)
        print(self.domanda)
        print(self.risposte)
        #   Fine prova

        #self.prepara_url_da_ricercare(self.domanda, self.risposte)

    def avvio_identificazione(self):
        for n, img in enumerate(self.lista_files):
            if n == 0:
                self.domanda = self.ocr_core(img)
            else:
                # Se la prima parola della risposta è una parola inutile allora la rimuoviamo
                r = self.pota_risposta(self.ocr_core(img))
                #potata la risposta allora la inseriamo nella lista
                self.risposte.append(r)


    def ocr_core(self, filename):
        """
        This function will handle the core OCR processing of images.
        """
        pytesseract.pytesseract.tesseract_cmd = PATH_INSTALLAZIONE_TESSERACT
        try:
            # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
            text = pytesseract.image_to_string(Image.open(filename), lang='ita+eng')
            if not text:
                text = pytesseract.image_to_string(Image.open(filename), lang='ita', config='--psm 13 --oem 3')
        except Exception as e:
            print("Problema con il riconoscimento di una delle immagini!")
            print(e)
            text = ''
        print(text)
        return text

    def avvia_identificazione_mp(self):
        """
        Sfrutta il multiprocessing per riconsocere più rapidamente il testo delle immagini
        :param sites:
        :return:
        """
        self.domanda = None
        self.risposte = [None, None, None]
        lista_file_enumerati = list(enumerate(self.lista_files))
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # otterrai una lista contenente due liste:
            # nella prima ci sono i risultati dell'url della domanda, nell'altro quello di domanda e risposte
            executor.map(self.ocr_core_mp, lista_file_enumerati, timeout=3000)
        #print(self.risultati)
        #input('fine')

    def ocr_core_mp(self, file_enumerati):
        """
        This function will handle the core OCR processing of images.
        """
        indice = file_enumerati[0]
        filename = file_enumerati[1]
        pytesseract.pytesseract.tesseract_cmd = PATH_INSTALLAZIONE_TESSERACT
        try:
            # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
            text = pytesseract.image_to_string(Image.open(filename), lang='ita+eng')
            if not text:
                text = pytesseract.image_to_string(Image.open(filename), lang='ita', config='--psm 13 --oem 3')
        except Exception as e:
            print("Problema con il riconoscimento di una delle immagini!")
            print(e)
            text = ''
        else:
            if indice == 0:
                self.domanda = text
            else:
                # Una volta riconosciuto il testo delle risposte elimino eventuali articoli o proposizioni inutili all'inizio
                risposta = self.pota_risposta(text)
                self.risposte[indice-1] = risposta
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
        print(self.domanda_url)
        print(self.risp_url)

    def prepara_url_da_ricercare_sent(self, domanda, risposta):
        base_url = 'https://www.google.com/search?q='
        domanda_formattata_per_ricerca = "+".join(domanda.split())
        self.link_sentimentali_lista = []
        if type(risposta) == list:
            for risp in risposta:
                if not (risp) or (risp == ' '):
                    continue
                #risp = "+".join(risp.split())
                # %22 è nell'url ciò che sostituisce il carattere delle virgolette ""
                risp = '%22{}%22'.format(risp)
                query_url = "{}+AND+({})".format(domanda_formattata_per_ricerca, risp)
                self.link_sentimentali_lista.append(base_url + query_url)
            #risposta_formattata_per_ricerca = "+OR+".join(r)
        else:
            self.link_sentimentali_lista.append(base_url + domanda_formattata_per_ricerca)
        print(self.link_sentimentali_lista)


    def pota_risposta(self, risp):
        """
        Input: Una sola delle 3 risposte
        Output: Risposta potata di eventuali parole inutili all'inizio (come articoli o preposizioni)
        """
        r = risp.replace('\'', ' ').split()
        if r[0].lower() in inutili:
            r.pop(0)
            s = " ".join(r)
            return s
        else:
            return risp

    def analizza_domanda(self, domanda, pattern):
        """Input: domanda del quiz
        Output: keyword della domanda, e flag per indirizzare le query"""

        diz_match = {"traquesti": [], "corse": [], "bandiera": [], "prima": [], "keyw1": [], "keyw2": []}
        match = {diz_match[k].append(v) for match in pattern.finditer(domanda) for k, v in match.groupdict().items() if v}

        lista_keyword = [diz_match["keyw1"] + diz_match["keyw2"]]
        if diz_match["bandiera"]:
            # Voglio cercare semplicemente: bandiera + risp1; bandiera + risp2; bandiera + risp3
            pass
        if diz_match["corse"]:
            pass
        if diz_match["prima"]:
            pass
        if lista_keyword:
            #le uso per l'analisi sentimentale dei risultati
            return lista_keyword


