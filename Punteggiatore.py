# -- coding: utf-8 --
from bs4 import BeautifulSoup, SoupStrainer
import requests
from cf import USER_AGENT, TEMPLATE_DIR, CSS_DIR
import concurrent.futures
import threading, multiprocessing
import pprint, time
import webbrowser
from jinja2 import Environment, FileSystemLoader
from gazpacho import Soup, get
import sys

import statistics
import paroleparole

session = None

class Punteggiatore():
    def __init__(self, urls, lista_risposte, domanda, coordinate_click=(), pattern=''):
        self.thread_local = threading.local()
        self.pattern = pattern
        self.lista_url = urls
        self.domanda = domanda
        self.lista_risposte = lista_risposte
        self.coord_click = coordinate_click
        #start = time.time()
        #self.download_all_sites(urls)
        #self.chiama_ottieni_punti()
        #print(TEMPLATE_DIR)
        #self.rendo_template_html()

        """ Introdototto il 14/09 per miglioare efficienza"""
        self.prepara_dizionario_risposte_con_punteggi_e_coordinate_cliccabili()
        self.lista_risp_riscontri = []
        self.lista_risp_senza_riscontri = []
        self.download_all_sites(urls)
        #self.download_all_sites_multip(urls)

    def prepara_dizionario_risposte_con_punteggi_e_coordinate_cliccabili(self):
        # crea un dizionario con 3 chiavi, ovvero le 3 risposte i cui valori sono altri tre dizionari:
        # le chiavi sono i punteggi ottenuti da google, e le coordinate (una tupla) da cliccare nel quiz
        if not self.coord_click:
            self.coord_click = ((0,0), (0,0), (0,0))
        self.dizionario_di_risposte_e_key_punteggi = {i: {
            '_d_R_': 0, '_dr_R_': 0, 'coord_click': self.coord_click[n]} for n, i in enumerate(self.lista_risposte)}
        #print(self.dizionario_di_risposte_e_key_punteggi)


    def download_site_preserva_html(self, url):
        # Tenta di guardare anche nei box di google
        session = requests.Session()
        risultato = []
        with session.get(url, headers=USER_AGENT) as r:
            r.raise_for_status()
            html_doc = r.text
            strainer = SoupStrainer('div', attrs={'id': 'search'})
            soup = BeautifulSoup(html_doc, 'lxml', parse_only=strainer)
            #@soup = BeautifulSoup(html_doc, 'lxml') #'html.parser')
            lista_riscontri = []
            lista_non_riscontri = []

            stringa = ''
            stringhe=[]
            resp = soup.find(class_='Z0LcW')
            snipp_text = soup.find(class_='i4J0ge')
            if resp and snipp_text:
                stringa_1 = self.produci_stringa_risultato(soup, 'e24Kjd', titolo=resp)
                stringa_2 = self.produci_stringa_risultato(soup, 'SPZz6b', testo=snipp_text)
                stringhe = [stringa_1, stringa_2]

            elif resp:
                # text = special.find('span', attrs={'class': 'e24Kjd'})
                text = soup.find(class_='e24Kjd')
                stringa = str(resp) + '<br>' + str(text)  # + '<br>' + str(sito_fonte)

            elif snipp_text:
                snipp_tit = soup.find(class_='SPZz6b')
                stringa = str(snipp_tit) + '<br>' + str(snipp_text)

            else:
            #elif not resp and not snipp_text:  # Questo snippet è quello estratto da wikipedia: mancherà il titolo tuttavia
                # https://www.google.com/search?q=Chi+tenne+il+discorso+%22|+have+a+dream%22?
                text = soup.find(class_='e24Kjd')
                if text:
                    stringa = str(text)

                else:  # Quando escono estratti di liste
                    # https://www.google.com/search?q=Qual+%C3%A8+l%27isola+pi%C3%B9+grande+d%27Italia?
                    geo = soup.find(class_='i8Z77e')
                    if geo:
                        stringa = str(geo)
                    else:
                        mappa = soup.find(class_="desktop-title-content")
                        if mappa:
                            res = soup.find(class_="desktop-title-subcontent")
                            stringa = str(mappa) + '<br>' + str(res)

            if stringa:
                esito, risultato = self.punti_dal_risultato(stringa, url, 3)
                if esito:
                    lista_riscontri.append(risultato)
                else:
                    lista_non_riscontri.append(risultato)
            elif stringhe:
                for stringa in stringhe:
                    esito, risultato = self.punti_dal_risultato(stringa, url, 3)
                    if esito:
                        lista_riscontri.append(risultato)
                    else:
                        lista_non_riscontri.append(risultato)


            """
            for special in soup.find_all(class_='ifM9O'):
                if not special:
                    mappa = soup.find(class_="desktop-title-content")
                    if mappa:
                        res = soup.find(class_="desktop-title-subcontent")
                        stringa = str(mappa) + '<br>' + str(res)
                    else:
                        break
                resp = special.find(class_='Z0LcW') # Questo è per trovare le risposte secche: fondazione imperi, dove gioca ribery
                #sito_fonte = special.find(class_='LC20lb')

                if resp:
                    #text = special.find('span', attrs={'class': 'e24Kjd'})
                    text = special.find(class_ = 'e24Kjd')
                    stringa = str(resp) + '<br>' + str(text)  # + '<br>' + str(sito_fonte)
                    print("Special1")
                    print(stringa)
                elif not resp:
                    # Questo è lo snippet generato da google che contiene una descrizione ed alcune informazioni in tab
                    # esempio https://www.google.com/search?q=Il+Regno+delle+Due+Sicilie+%C3%A8+stato+istituito:

                    snipp_text = special.find(class_='i4J0ge')
                    if snipp_text:
                        snipp_tit = special.find(class_='SPZz6b')
                        stringa = str(snipp_tit) + '<br>' + str(snipp_text)
                        print("Special2")
                        print(stringa)
                    elif not snipp_text:    # Questo snippet è quello estratto da wikipedia: mancherà il titolo tuttavia
                        # https://www.google.com/search?q=Chi+tenne+il+discorso+%22|+have+a+dream%22?
                        text = special.find(class_='e24Kjd')
                        if text:
                            stringa = str(text)

                        else:   # Quando escono estratti di liste
                            # https://www.google.com/search?q=Qual+%C3%A8+l%27isola+pi%C3%B9+grande+d%27Italia?
                            geo = special.find(class_='i8Z77e')
                            if geo:
                                stringa = str(geo)
                            else:
                                break

                esito, risultato = self.punti_dal_risultato(stringa, url, 3)
                if esito:
                    lista_riscontri.append(risultato)
                else:
                    lista_non_riscontri.append(risultato)
                """

            # Tutti i risultati SEMPLICI sono al di sotto di un elemento: class='g'
            for g in soup.find_all(class_='g'):
                # Adesso cerco diverse cose:

                r = g.find(class_='LC20lb') # contiene il titolo del risultato (senza l'url che sta in altra classe)
                st = g.find(class_='st')  # racchiude il sunto del risultato

                #r = g.find(class_='ellip')  # contiene il titolo del risultato (senza l'url che sta in altra classe)
                #st = g.find('span', attrs={'class': 'st'})  # racchiude il sunto del risultato

                if st and r:
                    stringa = str(r) + '<br>' + str(st)
                else: continue
                """ Questi sono i casi speciali di cui ci siamo rotti i coglioni sopra
                # Quando hai i box dei risultati, sotto la classe 'g' non trovi invece le classi r o st
                elif not st or not r:
                    # Andiamo alla ricerca di eventuali box (infame capoluogo calabrese)
                    r = g.find('div', attrs={
                        'class': 'Z0LcW'})  # contiene il trafiletto per catanzaro (ma sotto ha un'altra classe) e la sinossi del film rocknrolla (direttamente)
                    if r:   # sicuro che non sia if s: ??
                        stringa = str(r)
                    else:
                        r = g.find('span', attrs={'class': 'e24Kjd'})  # c'è il trafiletto di wikipedia, ed alcuni sunti vari
                        if r:
                            stringa = str(r)
                        else:
                            r = g.find('span', attrs={'class': 'Z0LcW'})
                            if r:
                                stringa = str(r)
                            else:
                                continue
                """

                """Introdotto il 14/09 per velocizzare"""
                esito, risultato = self.punti_dal_risultato(stringa, url)
                if esito:
                    lista_riscontri.append(risultato)
                else:
                    lista_non_riscontri.append(risultato)

            return lista_riscontri + lista_non_riscontri

    def produci_stringa_risultato (self, soup, css_class_testo, titolo='', testo=''):
        if not testo:
            testo = soup.find(class_=css_class_testo)
        else:
            titolo = soup.find(class_=css_class_testo)
        stringa = str(titolo) + '<br>' + str(testo)
        return stringa


    def get_keyword_domanda(self, pattern, domanda):
        """Input: domanda del quiz
        Output: keyword della domanda, e flag per indirizzare le query"""

        diz_match = {"traquesti": [], "corse": [], "bandiera": [], "prima": [], "keyw1": [], "keyw2": []}
        match = {diz_match[k].append(v) for match in pattern.finditer(domanda) for k, v in match.groupdict().items() if v}

        lista_keyword = diz_match["keyw1"] + diz_match["keyw2"]
        if lista_keyword:
            #le uso per l'analisi sentimentale dei risultati
            print(lista_keyword)
            return lista_keyword
        return


    def download_all_sites(self, sites):
        """Funzione Asincrona, contemporaneamente viene lanciata la funzione download_site_preserva_html,
        Input
         sites: lista con due url, uno per la sola domanda, uno per domanda e risposta
        grazie a executor.map, la funzione viene lanciata contemporaneamente 2 volte avendo come argomento un elemento
        dalla lista sites alla volta,
        Output = [[risultati sola domanda][risultati domanda con rispose]]
         lista contenente due liste, in una avremo i risultati dati da google cercando la sola domanda
         e nell'altra invece i risultati di domanda e risposte.
         Inoltre, i risultati sono ordinati in modo che trovi prima quelli in cui è stata trovata una delle 3 risposte
         e poi quelli senza riscontri.
        La funzione asincrona combina le liste restituite singolarmente dalla funzione download_site_preserva_html
        in una lista contenente due liste
        """
        # Preso da un articolo su RealPython che parlava di Concurrency/multiprocessing
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # otterrai una lista contenente due liste:
            # nella prima ci sono i risultati dell'url della domanda, nell'altro quello di domanda e risposte
            self.risultati_soup_google = list(executor.map(self.download_site_preserva_html, sites, timeout=3000))

        #print(self.dizionario_di_risposte_e_key_punteggi)

    """Esempio per il multiprocessing"""
    def set_global_session(self):
        global session
        if not session:
            session = requests.Session()

    def download_all_sites_multip(self, sites):
        with multiprocessing.Pool(initializer=self.set_global_session) as pool:
            pool.map(self.download_site_preserva_html_multip, sites)

    def download_site_preserva_html_multip(self, url):
        # Tenta di guardare anche nei box di google
        risultato = []
        with session.get(url, headers=USER_AGENT) as r:
            r.raise_for_status()
            html_doc = r.text
            strainer = SoupStrainer('div', attrs={'id': 'search'})
            soup = BeautifulSoup(html_doc, 'lxml', parse_only=strainer)
            #@soup = BeautifulSoup(html_doc, 'lxml') #'html.parser')
            lista_riscontri = []
            lista_non_riscontri = []

            stringa = ''
            stringhe=[]
            resp = soup.find(class_='Z0LcW')
            snipp_text = soup.find(class_='i4J0ge')
            if resp and snipp_text:
                stringa_1 = self.produci_stringa_risultato(soup, 'e24Kjd', titolo=resp)
                stringa_2 = self.produci_stringa_risultato(soup, 'SPZz6b', testo=snipp_text)
                stringhe = [stringa_1, stringa_2]

            elif resp:
                # text = special.find('span', attrs={'class': 'e24Kjd'})
                text = soup.find(class_='e24Kjd')
                stringa = str(resp) + '<br>' + str(text)  # + '<br>' + str(sito_fonte)

            elif snipp_text:
                snipp_tit = soup.find(class_='SPZz6b')
                stringa = str(snipp_tit) + '<br>' + str(snipp_text)

            else:
            #elif not resp and not snipp_text:  # Questo snippet è quello estratto da wikipedia: mancherà il titolo tuttavia
                # https://www.google.com/search?q=Chi+tenne+il+discorso+%22|+have+a+dream%22?
                text = soup.find(class_='e24Kjd')
                if text:
                    stringa = str(text)

                else:  # Quando escono estratti di liste
                    # https://www.google.com/search?q=Qual+%C3%A8+l%27isola+pi%C3%B9+grande+d%27Italia?
                    geo = soup.find(class_='i8Z77e')
                    if geo:
                        stringa = str(geo)
                    else:
                        mappa = soup.find(class_="desktop-title-content")
                        if mappa:
                            res = soup.find(class_="desktop-title-subcontent")
                            stringa = str(mappa) + '<br>' + str(res)

            if stringa:
                esito, risultato = self.punti_dal_risultato(stringa, url, 3)
                if esito:
                    lista_riscontri.append(risultato)
                else:
                    lista_non_riscontri.append(risultato)
            elif stringhe:
                for stringa in stringhe:
                    esito, risultato = self.punti_dal_risultato(stringa, url, 3)
                    if esito:
                        lista_riscontri.append(risultato)
                    else:
                        lista_non_riscontri.append(risultato)


            """
            for special in soup.find_all(class_='ifM9O'):
                if not special:
                    mappa = soup.find(class_="desktop-title-content")
                    if mappa:
                        res = soup.find(class_="desktop-title-subcontent")
                        stringa = str(mappa) + '<br>' + str(res)
                    else:
                        break
                resp = special.find(class_='Z0LcW') # Questo è per trovare le risposte secche: fondazione imperi, dove gioca ribery
                #sito_fonte = special.find(class_='LC20lb')

                if resp:
                    #text = special.find('span', attrs={'class': 'e24Kjd'})
                    text = special.find(class_ = 'e24Kjd')
                    stringa = str(resp) + '<br>' + str(text)  # + '<br>' + str(sito_fonte)
                    print("Special1")
                    print(stringa)
                elif not resp:
                    # Questo è lo snippet generato da google che contiene una descrizione ed alcune informazioni in tab
                    # esempio https://www.google.com/search?q=Il+Regno+delle+Due+Sicilie+%C3%A8+stato+istituito:

                    snipp_text = special.find(class_='i4J0ge')
                    if snipp_text:
                        snipp_tit = special.find(class_='SPZz6b')
                        stringa = str(snipp_tit) + '<br>' + str(snipp_text)
                        print("Special2")
                        print(stringa)
                    elif not snipp_text:    # Questo snippet è quello estratto da wikipedia: mancherà il titolo tuttavia
                        # https://www.google.com/search?q=Chi+tenne+il+discorso+%22|+have+a+dream%22?
                        text = special.find(class_='e24Kjd')
                        if text:
                            stringa = str(text)

                        else:   # Quando escono estratti di liste
                            # https://www.google.com/search?q=Qual+%C3%A8+l%27isola+pi%C3%B9+grande+d%27Italia?
                            geo = special.find(class_='i8Z77e')
                            if geo:
                                stringa = str(geo)
                            else:
                                break

                esito, risultato = self.punti_dal_risultato(stringa, url, 3)
                if esito:
                    lista_riscontri.append(risultato)
                else:
                    lista_non_riscontri.append(risultato)
                """

            # Tutti i risultati SEMPLICI sono al di sotto di un elemento: class='g'
            for g in soup.find_all(class_='g'):
                # Adesso cerco diverse cose:

                r = g.find(class_='LC20lb') # contiene il titolo del risultato (senza l'url che sta in altra classe)
                st = g.find(class_='st')  # racchiude il sunto del risultato

                #r = g.find(class_='ellip')  # contiene il titolo del risultato (senza l'url che sta in altra classe)
                #st = g.find('span', attrs={'class': 'st'})  # racchiude il sunto del risultato

                if st and r:
                    stringa = str(r) + '<br>' + str(st)
                else: continue
                """ Questi sono i casi speciali di cui ci siamo rotti i coglioni sopra
                # Quando hai i box dei risultati, sotto la classe 'g' non trovi invece le classi r o st
                elif not st or not r:
                    # Andiamo alla ricerca di eventuali box (infame capoluogo calabrese)
                    r = g.find('div', attrs={
                        'class': 'Z0LcW'})  # contiene il trafiletto per catanzaro (ma sotto ha un'altra classe) e la sinossi del film rocknrolla (direttamente)
                    if r:   # sicuro che non sia if s: ??
                        stringa = str(r)
                    else:
                        r = g.find('span', attrs={'class': 'e24Kjd'})  # c'è il trafiletto di wikipedia, ed alcuni sunti vari
                        if r:
                            stringa = str(r)
                        else:
                            r = g.find('span', attrs={'class': 'Z0LcW'})
                            if r:
                                stringa = str(r)
                            else:
                                continue
                """

                """Introdotto il 14/09 per velocizzare"""
                esito, risultato = self.punti_dal_risultato(stringa, url)
                if esito:
                    lista_riscontri.append(risultato)
                else:
                    lista_non_riscontri.append(risultato)

            return lista_riscontri + lista_non_riscontri

    def chiama_ottieni_punti(self):
        self.dizionario_di_risposte_e_key_punteggi = {}
        key = ['_d_R_', '_dr_R_']
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            self.risultati_google_evidenziati = list(executor.map(self.ottieni_punti_new_per_executor, [
            (self.risultati_soup_google[0], key[0]), (self.risultati_soup_google[1], key[1])
                ]))

    def ottieni_punti_new_per_executor(self, risultati_google_e_key):
        # versione per gli executor
        # risultati_google_e_key[0]: corrisponde ai risultati_google
        # risultati_google_e_key[1]: corrisponde alle key che servono in seguito per la gui (formato simile a _D_RX_)

        #for n, risposta in enumerate(self.lista_risposte):
        for risposta in self.lista_risposte:
            # Questo è l'arzigogolo per creare la stringa della key da usare nella gui
            #key = risultati_google_e_key[1][:-2] + str(n + 1) + risultati_google_e_key[1][-1:]
            key = risultati_google_e_key[1]

            if risposta not in self.dizionario_di_risposte_e_key_punteggi:
                self.dizionario_di_risposte_e_key_punteggi[risposta] = {}
                self.dizionario_di_risposte_e_key_punteggi[risposta][key] = 0
            else:
                self.dizionario_di_risposte_e_key_punteggi[risposta].update({key: 0})

            int_nuova_posizione = 0 # questo valore serve per mantenere la posizione delle ricerche
            for risultato in risultati_google_e_key[0]:
                index_risultato = str(risultato).lower().find(risposta.lower())
                if index_risultato >= 0:    #se il metodo find non trova niente restiuisce -1
                #if risposta.lower() in str(risultato).lower():
                    # 1)Se trovo una isposta nel risultat la evidenzio nell'HTML
                    # Se non attacco la lista con queste operazioni non modifico la lista originaria passata alla chiamata
                    # della funzione.
                    risultati_google_e_key[0].remove(risultato)
                    risultato = risultato[:index_risultato] + '<b>{}</b>'.format(risposta) + risultato[index_risultato+len(risposta):]
                    #risultato = str(risultato).lower().replace(risposta.lower(), '<b>' + risposta.lower() + '</b>')
                    risultati_google_e_key[0].insert(int_nuova_posizione, risultato)
                    int_nuova_posizione += 1 #in questo modo il risultato viene posto il più in alto possibile, senza perdere posizione rispetto agli altri risultati
                    # 2) Aggiorno il punteggio
                    self.dizionario_di_risposte_e_key_punteggi[risposta][key] += 1

        return risultati_google_e_key[0]
        # dizionario_di_risposte_e_key_punteggi è una lista che contiene un dizionario fatto così:
        # [{Risp1 : {'keyDom' : x, 'keyD+R' : x }, Risp2 : { ... }]

        # ponte_risultati_risposte è invece un dizionario che in cui le key sono asociate a delle liste
        # {Risultato_google che ha una risposta all'interno : [risposta (,eventuale_altra_risposta)]}
        # non volendo più usare la gui questo dizionario mi è inutile. conservo lo scritto a futura memoria.

    def punti_dal_risultato(self, risultato, url, mult=1):
    #Rispetto alla vecchia implementazione analizzo subito la stringa dei risultati di google per tagliare dei cicli for
    # Il parametro mult serve per dare più peso ai risultati che arrivano da alcune fonti (es: caselle speciali)
        if url == self.lista_url[0]: #ovvero se l'url è lo stesso url della query per la sola domanda su google
            key = '_d_R_'
        else:
            key = '_dr_R_'

        trovato = False
        for risposta in self.lista_risposte:
            if risposta not in self.dizionario_di_risposte_e_key_punteggi:
                self.dizionario_di_risposte_e_key_punteggi[risposta] = {}
                self.dizionario_di_risposte_e_key_punteggi[risposta][key] = 0
            else:
                if key not in self.dizionario_di_risposte_e_key_punteggi[risposta]:
                    self.dizionario_di_risposte_e_key_punteggi[risposta].update({key: 0})

            index_risultato = str(risultato).lower().find(risposta.lower())
            if index_risultato >= 0:  # se il metodo find non trova niente restiuisce -1
                # 1)Se trovo una isposta nel risultat la evidenzio nell'HTML
                risultato = risultato[:index_risultato] + '<b>{}</b>'.format(risposta) + risultato[index_risultato + len(risposta):]
                # 2) Aggiorno il punteggio
                self.dizionario_di_risposte_e_key_punteggi[risposta][key] += 1 * mult
                trovato = True

        return trovato, risultato

    def rendo_template_html(self):
        file_loader = FileSystemLoader(TEMPLATE_DIR)
        env = Environment(loader=file_loader)
        template = env.get_template('base2.html')
        #print(template)

        with open('domanda.html', 'w', encoding="utf-8") as pisstaking:
            pisstaking.write(
                template.render(domanda=self.domanda,
                                lista_risposte=self.lista_risposte,
                                diz_risposte_e_key_punteggi=self.dizionario_di_risposte_e_key_punteggi,
                                risultati_soup_google=self.risultati_soup_google,
                                path_to_css=CSS_DIR))

        webbrowser.open('domanda.html')

if __name__ == '__main__':
    lista_urls = ['https://www.google.com/search?q=de+bello+gallico+roma', 'https://www.google.com/search?q=modi+di+dire',]
    lista_risp = ['Caio', 'Cesare', 'Sempronio']
    x = Punteggiatore(lista_urls, lista_risp)