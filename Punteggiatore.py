from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import requests
from cf import USER_AGENT
from multiprocessing.dummy import Pool as ThreadPool
import time
import concurrent.futures
import threading
from Guiatore import Guiatore

class Punteggiatore():
    def __init__(self, urls, lista_risposte):
        self.win = Guiatore(lista_risposte)
        self.thread_local = threading.local()
        self.lista_url = urls
        #self.gui_punteggi()
        self.lista_risposte = lista_risposte
        #self.avvia_ricerca()
        self.download_all_sites(urls)
        self.punteggi.append(self.punteggio_totale)
        print("nel ponteggiatore: \n")
        print(self.punteggi, type(self.punteggi))
        self.win.avvia_aggiornatori(self.punteggi)



    def get_session(self):
        if not hasattr(self.thread_local, "session"):
            self.thread_local.session = requests.Session()
        return self.thread_local.session

    def download_site(self, url):
        session = self.get_session()
        with session.get(url, headers=USER_AGENT) as r:
            print(f"Read {len(r.content)} from {url}")
            r.raise_for_status()
            print(r)
            html_doc = r.text
            soup = BeautifulSoup(html_doc, 'html.parser')
            risultati_google = soup.select('.rc')
            return risultati_google

    def download_all_sites(self, sites):
        start = time.time()
        # Preso da un articolo su RealPython che parlava di Concurrency/multiprocessing
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            risultati_soup_google = executor.map(self.download_site, sites)
            self.punteggi = list(executor.map(self.ottieni_punti, risultati_soup_google))
        self.punteggio_totale = Counter(self.punteggi[0]) + Counter(self.punteggi[1])  # 0 è solo dom, 1 è dom + risp
        print('Punteggio totale:\n')
        print(self.punteggio_totale)
        dur = time.time() - start
        print(dur)

    def ottieni_punti(self, risultati_google):
        punteggio = defaultdict(int)
        for risultato in risultati_google:
            print(str(risultato))
            for risposta in self.lista_risposte:
                if risposta.lower() in str(risultato).lower():
                    print('Trovato {}'.format(risposta.lower()))

                    punteggio[risposta] += 1
        print('singolo puneggio: \n')
        print(punteggio)
        return punteggio
    """
    def avvia_ricerca(self):
        start = time.time()
        pool = ThreadPool(3)
        risultati_soup_google = pool.map(self.scrape_sito, self.lista_url)
        self.punteggi = pool.map(self.ottieni_punti, risultati_soup_google)
        pool.close()
        pool.join()
        self.punteggio_totale = Counter(self.punteggi[0]) + Counter(self.punteggi[1])  # 0 è solo dom, 1 è dom + risp
        print('Punteggio totale:\n')
        print(self.punteggio_totale)
        dur = time.time() - start
        print(dur)
        #self.avvia_aggiornatori()

    def scrape_sito(self, url):
        # l'obiettivo è quello di analizzare nei due URL che apro, quante volte compaiono ciascuna delle risposte!!!
        # E' necessario quindi analizzare con BS4 i due url, contare quante volte compaiono le singole risposte
        # TODO: Le singole rispsote andrebbero analizzate in modo da rimuovere parole inutili e cercare solo il succo.
        # e inviare questi dati a pysimplegui per mostrarli
        r = requests.get(url, headers=USER_AGENT)
        r.raise_for_status()
        print(r)
        html_doc = r.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        risultati_google = soup.select('.rc')
        return risultati_google

"""

if __name__ == '__main__':
    lista_urls = ['https://www.google.com/search?q=de+bello+gallico+roma', 'https://www.google.com/search?q=modi+di+dire',]
    lista_risp = ['Caio', 'Cesare', 'Sempronio']
    x = Punteggiatore(lista_urls, lista_risp)