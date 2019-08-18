from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import requests
from cf import USER_AGENT
import time
import concurrent.futures
import threading
from Guiatore import Guiatore

class Punteggiatore():
    def __init__(self, urls, lista_risposte, oggetto_creatore_gui):
        self.win = oggetto_creatore_gui #Guiatore(lista_risposte, urls)
        self.thread_local = threading.local()
        self.lista_url = urls
        self.lista_risposte = lista_risposte

        self.download_all_sites(urls)
        self.punteggi.append(self.punteggio_totale)
        #print("nel ponteggiatore: \n")
        print(self.punteggi[0])
        print(self.punteggi[1])
        print(self.punteggi[-1])    # punteggio totale


        # TODO CANCELLA/COMMENTA STA LINEA ALTRIMENTI IL PROGRAMMA TERMINA!
        Test = False
        if not Test:
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
            #print(soup)
            risultati_google = soup.select('.rc')
            return risultati_google

    def download_all_sites(self, sites):
        start = time.time()
        # Preso da un articolo su RealPython che parlava di Concurrency/multiprocessing
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            risultati_soup_google = executor.map(self.download_site, sites)
            self.punteggi = list(executor.map(self.ottieni_punti, risultati_soup_google))
        self.punteggio_totale = Counter(self.punteggi[0]) + Counter(self.punteggi[1])  # 0 è solo dom, 1 è dom + risp
        dur = time.time() - start
        print(dur)

    def ottieni_punti(self, risultati_google):
        punteggio = defaultdict(int)
        for risultato in risultati_google:
            for risposta in self.lista_risposte:
                if risposta.lower() in str(risultato).lower():
                    punteggio[risposta] += 1
        print('singolo puneggio: \n')
        print(punteggio)
        return punteggio


if __name__ == '__main__':
    lista_urls = ['https://www.google.com/search?q=de+bello+gallico+roma', 'https://www.google.com/search?q=modi+di+dire',]
    lista_risp = ['Caio', 'Cesare', 'Sempronio']
    x = Punteggiatore(lista_urls, lista_risp)