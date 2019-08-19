# -- coding: utf-8 --
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import requests
from cf import USER_AGENT
import concurrent.futures
import queue, threading
import pprint
import webbrowser,os
from Guiatore import Guiatore

class Punteggiatore():
    def __init__(self, urls, lista_risposte):
        self.thread_local = threading.local()
        self.lista_url = urls
        self.lista_risposte = lista_risposte

        self.download_all_sites(urls)
        self.scrivo_html_con_risultati_e_l_apro()
        #self.punteggi.append(self.punteggio_totale)
        #print("nel ponteggiatore: \n")
        #pprint.pprint(self.dizionario_di_risposte_e_punteggi)

    def crea_dizionario_delle_risposte_e_punteggi(self):
        # crea un dizionario con 3 chiavi, ovvero le 3 risposte,
        # i valori delle 3 chiavi è un altro dizionario in cui le chiavi sono le key della gui,
        # ed il suo valore è il punteggio
        self.devoto_oli = {}
        for risp in self.lista_risposte:
            self.devoto_oli[risp] = {}

    def get_session(self):
        if not hasattr(self.thread_local, "session"):
            self.thread_local.session = requests.Session()
        return self.thread_local.session

    def download_site_old(self, url):
        # il problema è che non cerca nei box speciali di google.
        session = self.get_session()
        with session.get(url, headers=USER_AGENT) as r:
            print(f"Read {len(r.content)} from {url}")
            r.raise_for_status()
            print(r)
            html_doc = r.text
            soup = BeautifulSoup(html_doc, 'html.parser')
            #print(soup)
            risultati_google = soup.select('.rc')
            return risultati_google

    def download_site_preserva_html(self, url):
        # Tenta di guardare anche nei box di google

        print('PRESERVA')
        print(url)
        session = requests.Session()
        risultato = []
        with session.get(url, headers=USER_AGENT) as r:
            r.raise_for_status()
            html_doc = r.text
            soup = BeautifulSoup(html_doc, 'html.parser')

            # Tutti i risultati sono al di sotto di un elemento: class='g'
            for g in soup.find_all(class_='g'):
                # Adesso cerco diverse cose:
                r = g.find(class_='ellip')  # contiene il titolo del risultato (senza l'url che sta in altra classe)
                st = g.find('span', attrs={'class': 'st'})  # racchiude il sunto del risultato
                superfluo = g.find(class_='JolIg')  # contiene cose inutili come il box 'People Also Search For ...'
                if superfluo:
                    continue

                if st and r:
                    stringa = str(r) + '<br>' + str(st)

                # Quando hai i box dei risultati, sotto la classe 'g' non trovi invece le classi r o st
                elif not st or not r:
                    # Andiamo alla ricerca di eventuali box (infame capoluogo calabrese)
                    s = g.find('div', attrs={
                        'class': 'Z0LcW'})  # contiene il trafiletto per catanzaro (ma sotto ha un'altra classe) e la sinossi del film rocknrolla (direttamente)
                    if s:
                        stringa = str(s)
                    else:
                        s = g.find('span', attrs={'class': 'e24Kjd'})  # c'è il trafiletto di wikipedia, ed alcuni sunti vari
                        if not s:
                            continue
                        else:
                            stringa = str(s)

                #stringa = '<br>'.join(stringa.split('...'))

                risultato.append(stringa)
            print(risultato)
            return risultato


    def download_site_pensano_alla_gui(self, url):
        # Tenta di guardare anche nei box di google
        print(url)
        session = requests.Session()
        risultato = []
        with session.get(url, headers=USER_AGENT) as r:
            r.raise_for_status()
            html_doc = r.text
            soup = BeautifulSoup(html_doc, 'html.parser')

            # Tutti i risultati sono al di sotto di un elemento: class='g'
            for g in soup.find_all(class_='g'):
                # Adesso cerco diverse cose:
                r = g.find(class_='ellip')  # contiene il titolo del risultato (senza l'url che sta in altra classe)
                st = g.find('span', attrs={'class': 'st'})  # racchiude il sunto del risultato
                superfluo = g.find(class_='JolIg')  # contiene cose inutili come il box 'People Also Search For ...'
                if superfluo:
                    continue

                if st and r:
                    tit = r.text
                    corp = st.text
                    stringa = tit + '\n' + corp

                # Quando hai i box dei risultati, sotto la classe 'g' non trovi invece le classi r o st
                elif not st or not r:
                    # Andiamo alla ricerca di eventuali box (infame capoluogo calabrese)
                    s = g.find('div', attrs={
                        'class': 'Z0LcW'})  # contiene il trafiletto per catanzaro (ma sotto ha un'altra classe) e la sinossi del film rocknrolla (direttamente)
                    if s:
                        stringa = s.text
                    else:
                        s = g.find('span', attrs={'class': 'e24Kjd'})  # c'è il trafiletto di wikipedia, ed alcuni sunti vari
                        if not s:
                            continue
                        else:
                            stringa = s.text


                stringa = '\n--> '.join(stringa.split('...'))

                risultato.append(stringa)
            #print(risultato)
            return risultato

    def download_all_sites(self, sites):
        print('**********DOWNLOAD ALL')
        # Preso da un articolo su RealPython che parlava di Concurrency/multiprocessing
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

            # otterrai una lista contenente due liste, nella prima ci sono i risultati dell'url della domanda, nell'altro quello di domanda e risposte
            self.risultati_soup_google = list(executor.map(self.download_site_preserva_html, sites))

            #self.punteggi = list(executor.map(self.ottieni_punti, self.risultati_soup_google))
            self.chiama_ottieni_punti()

    def chiama_ottieni_punti(self):
        print('INIZIO CHIAMA PNTI')
        self.dizionario_di_risposte_e_key_punteggi = {}
        self.ponte_risultati_risposte = {}
        key = ['_d_RX_', '_dr_RX_']
        #pprint.pprint(self.risultati_soup_google)
        print(len(self.risultati_soup_google))
        #self.dizionario_di_risposte_e_punteggi = list(map(self.ottieni_punti_new, self.risultati_soup_google, key))
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # self.dizionario_di_risposte_e_key_punteggi = list(executor.map(self.ottieni_punti_new_per_executor, [

            #self.ponte_risultati_risposte, \
            self.risultati_google_evidenziati = list(executor.map(self.ottieni_punti_new_per_executor, [
            (self.risultati_soup_google[0], key[0]),
                (self.risultati_soup_google[1], key[1])
                ]))
        print('FINE CHIAMA PNTI')
        pprint.pprint(self.risultati_google_evidenziati)
        print(len(self.risultati_google_evidenziati))
        pprint.pprint(self.ponte_risultati_risposte)
        pprint.pprint(self.dizionario_di_risposte_e_key_punteggi)


    def ottieni_punti_new(self, risultati_google, key):
        #Versione per la funzione semplice mapù()
        punteggio = {}
        for n, risposta in enumerate(self.lista_risposte):
            punteggio[risposta] = {} #defaultdict(int)
            #Questo è l'arzigogolo per creare la stringa della key da usare nella gui
            key = key[:-2] + str( n +1) + key[-1:]

            punteggio[risposta][key] = 0
            for risultato in risultati_google:
                if risposta.lower() in str(risultato).lower():
                    punteggio[risposta][key] += 1
        print('singolo puneggio: \n')
        print(punteggio)
        # Risultato è un dizionario fatto così:
        # {Risp1 : {'keyDom' : x, 'keyDR' : x}, Risp2 : {'keyDom' : x, 'keyDR' : x}, Risp3 : {'keyDom' : x, 'keyDR' : x}}
        return punteggio

    def ottieni_punti_new_per_executor(self, risultati_google_e_key):
        # versione per gli executor
        # risultati_google_e_key[0]: corrisponde ai risultati_google
        # risultati_google_e_key[1]: corrisponde alle key che servono in seguito per la gui (formato simile a _D_RX_)

        #ponte_risultati_risposte = {}
        for n, risposta in enumerate(self.lista_risposte):
            #punteggio[risposta] = {}  # defaultdict(int)
            # Questo è l'arzigogolo per creare la stringa della key da usare nella gui
            key = risultati_google_e_key[1][:-2] + str(n + 1) + risultati_google_e_key[1][-1:]
            #punteggio[risposta][key] = 0

            if risposta not in self.dizionario_di_risposte_e_key_punteggi:
                self.dizionario_di_risposte_e_key_punteggi[risposta] = {}
                self.dizionario_di_risposte_e_key_punteggi[risposta][key] = 0
            else:
                self.dizionario_di_risposte_e_key_punteggi[risposta].update({key: 0})

            #punteggio[risposta]['trovato_in'] = []
            for risultato in risultati_google_e_key[0]:
                if risposta.lower() in str(risultato).lower():
                    #punteggio[risposta][key] += 1
                    # Se non attacco la lista con queste operazioni non modifico la lista originaria passata alla chiamata
                    # della funzione.
                    risultati_google_e_key[0].remove(risultato)
                    risultato = str(risultato).lower().replace(risposta.lower(), '<b>' + risposta.lower() + '</b>')
                    risultati_google_e_key[0].insert(0, risultato)

                    self.dizionario_di_risposte_e_key_punteggi[risposta][key] += 1
                    """if str(risultato) not in ponte_risultati_risposte:
                        ponte_risultati_risposte[str(risultato)] = [risposta]
                    else:
                        ponte_risultati_risposte[str(risultato)].append(risposta)"""

        return risultati_google_e_key[0] #ponte_risultati_risposte, risultati_google_e_key[0]
        # dizionario_di_risposte_e_key_punteggi è una lista che contiene un dizionario fatto così:
        # [{Risp1 : {'keyDom' : x, 'keyD+R' : x }, Risp2 : { ... }]

        # ponte_risultati_risposte è invece un dizionario che in cui le key sono asociate a delle liste
        # {Risultato_google che ha una risposta all'interno : [risposta (,eventuale_altra_risposta)]}
        # non volendo più usare la gui questo dizionario mi è inutile. conservo lo scritto a futura memoria.

    def ottieni_punti(self, risultati_google):
        punteggio = defaultdict(int)
        for risultato in risultati_google:
            for risposta in self.lista_risposte:
                if risposta.lower() in str(risultato).lower():
                    punteggio[risposta] += 1
        print('singolo puneggio: \n')
        print(punteggio)
        return punteggio

    def scrivo_html_con_risultati_e_l_apro(self):
        # Con questa funzione scrivo io la pagina HTML,
        # a differenza della gui, posso evidenziare nei risultati eventuali risposte!
        # ed è una rottura in meno di cazzo
        with open('domanda.html', 'w', encoding="utf-8") as pisstaking:
            pisstaking.write('<link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css" rel="stylesheet"/>')

            for n, ris in enumerate(self.risultati_soup_google[0]):
                pisstaking.write('<div class="container">')
                pisstaking.write('<div class="row">')
                pisstaking.write('<div class="col">')
                if n == 0:
                    pisstaking.write('<b>' + 'Domanda' + '</b>')
                else:
                    pisstaking.write(ris)
                pisstaking.write('<br>')
                pisstaking.write('----------------')
                pisstaking.write('<br>')
                pisstaking.write('</div>')
                pisstaking.write('<div class="col">')
                if n == 0:
                    pisstaking.write('<b>' + 'Domanda & Risposte' + '</b>')
                else:
                    pisstaking.write(self.risultati_soup_google[1][n])
                pisstaking.write('<br>')
                pisstaking.write('----------------')
                pisstaking.write('<br>')
                pisstaking.write('</div></div></div>')

        webbrowser.open(os.path.join('file://', os.getcwd(), 'domanda.html'))

if __name__ == '__main__':
    lista_urls = ['https://www.google.com/search?q=de+bello+gallico+roma', 'https://www.google.com/search?q=modi+di+dire',]
    lista_risp = ['Caio', 'Cesare', 'Sempronio']
    x = Punteggiatore(lista_urls, lista_risp)