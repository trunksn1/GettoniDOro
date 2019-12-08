# -- coding: utf-8 --
try:
    from PIL import ImageGrab, Image
except ImportError:
    import Image
from install_settings import PATH_INSTALLAZIONE_TESSERACT
import pytesseract
import threading
from paroleparole import inutili, banned_words
import concurrent.futures
from time import time
import re
import urllib

class Identificatore():
    def __init__(self, lista_files):
        self.lista_files = lista_files
        self.risposte = []

        self.thread_local = threading.local()

        #   Prova del 30/11/2019
        #start = time()
        #self.avvio_identificazione()
        self.avvia_identificazione_mp()
        #print(time()-start)
        #print(self.domanda)
        #print(self.risposte)
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

    def prepara_url_da_ricercare(self, domanda, risposta, query=''):
        base_url = 'https://www.google.com/search?q='
        self.query_urls = []
        if not query:
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


            query_url = "{}+AND+({})".format(domanda_formattata_per_ricerca, risposta_formattata_per_ricerca)

            # Indirizzo della sola domanda
            self.domanda_url = base_url + "{}".format(domanda_formattata_per_ricerca)
            # Indirizzo per domanda + risposte
            self.risp_url = base_url + query_url

            print(self.domanda_url)
            print(self.risp_url)
            self.query_urls = [self.domanda_url, self.risp_url]

        elif query == 'traquesti':
            for q in self.queries:
                self.query_urls.append(base_url + q)
            print(self.query_urls)


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

    def elimina_parole_inutili(self, lista_parole):
        keywords = []
        for parola in lista_parole:
            if parola.lower() not in banned_words:
                keywords.append(parola)
        print(keywords)
        return keywords

    def trova_keyword(self, regex_patt_compilato='', domanda='', diz=[]):
        """L'idea è di restituire una lista contenente la query da fare su google
        Se la query restituita da questa funzione è vuota, allora il programma userà il metodo classico"""
        if not regex_patt_compilato:
            regex_patt_compilato = re.compile(r'''
    
    (?P<traquesti>(?:[Qq]ual.?|[Ch]i)?(?:\D*?\bquest.\b|\D*?\bloro\b))|         # Cerca "Quale tra questi|Chi tra loro"
    \b(?P<corse>Moto\s?[GPgp]+?|Formula\s(?:1|uno|Uno)|Gran\sPremio)\b| # cerca riferimenti alle gare di corsa
    (?P<bandiera>\bbandier.\b)|                                         # cerca bandiere
    (?P<serietv>(?:\D*?stagioni)?\b[Ss]erie\s?[Tt].*?\b(?:\D*?stagioni)?)|                                # cerca il numero di stagioni di serie TV
    (?P<prima>\bprim.|pi[uù] recente\b)|                                # Cerca riferimenti temporali
    (?P<keyw1>\b[A-Z][a-z]+\b)|                                         # Cerca parole inizianti con la maiuscola
    \"(?P<keyw2>.+?)\"|                                                 # cerca frasi tra "virgolette"
    (?P<keyw3>\w+)                                                      # restanti parole
    ''', re.VERBOSE)
#"[^"]*?"
        #mo = regex.search(domanda)
        d = domanda
        mo = regex_patt_compilato.findall(d)

        diz = {"traquesti": [], "corse": [], "bandiera": [], "serietv": [], "prima": [], "keyw1": [], "keyw2": [], "keyw3": []}

        _ = { diz[k].append(v)  for m in regex_patt_compilato.finditer(d) for k, v in m.groupdict().items() if v }
        print(diz)
        # flag che deve indirizzare il modo in cui fare la ricerca su google
        flag_ricerca = ""   #classico, comparativo (cerca dom e risposta), specifico (query creata ad arte)
        query = ''
        self.queries = []
        flag_query = ''
        keywords3 = []
        # Se ci sono altre keywords (maiuscole o virgolettati) allora cerca le parole rimanenti dalla domanda
        # Se non ci sono Maiuscole o virgolettati è inutile che perdo tempo a cercare altre keywords
        if diz['keyw1'] or diz['keyw2']:
            keywords3 = self.elimina_parole_inutili(diz['keyw3'])
            self.keywords = diz['keyw1'] + diz['keyw2'] + keywords3
        else:
            self.keywords = self.elimina_parole_inutili(diz['keyw3'])


        if diz["corse"]:
            #TODO
            pass
            base_query = 'posizioni '
            keywords = diz['corse'] + diz['keyw1'] + diz['keyw2']
            query = ' '.join(keywords)
            print(query)
            input('STOP')
        elif diz["serietv"]:
            # TODO
            pass
            if diz['traquesti']:
                base_query = 'numero stagioni '
                for risp in self.risposte:
                    self.queries.append(urllib.parse.quote_plus(base_query + risp))
                print(self.queries)
            else:
                keywords = diz['keyw1'] + diz['keyw2']
                query = ' '.join(keywords)
                print(query)
            input('STOP')
        elif diz["bandiera"]:
            pass
        #elif diz["prima"]:
        #    pass
        elif diz["traquesti"]:
            flag_query = 'traquesti'

            stringa_pulita = self.domanda.replace(diz["traquesti"][0], '')
            print(stringa_pulita)
            for risp in self.risposte:
                #self.queries.append(urllib.parse.quote_plus(stringa_pulita + ' AND "' + risp + '"'))
                #self.queries.append(urllib.parse.quote_plus(self.domanda + ' AND "' + risp + '"'))
                #self.queries.append(urllib.parse.quote_plus('"' + risp + '"'))
                self.queries.append(urllib.parse.quote_plus('"' + risp + '"' + ' AND ' + stringa_pulita))

            print(self.queries)
        return flag_query

        """
        print(d)
        print(mo)
        print(diz)

        for item, v in diz.items():
            print(v)
            if v:
                print(item, v)

        try:
            print('griyos')
            for g in mo.groups():
                print(g)
            print(mo.groups())
            #print(mo.group())
        except:
            print('except')
            #print(len(mo))
            for g in mo:
                print(g)
        """