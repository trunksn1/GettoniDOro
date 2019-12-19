# -- coding: utf-8 --
from bs4 import BeautifulSoup, SoupStrainer
import requests
from cf import USER_AGENT, TEMPLATE_DIR, CSS_DIR
import concurrent.futures
import threading
import multiprocessing as mp
import pprint, time
import webbrowser
from jinja2 import Environment, FileSystemLoader
from gazpacho import Soup, get
import sys, itertools

import statistics
import paroleparole

session = None

class Punteggiatore():
    def __init__(self, urls, lista_risposte, domanda, coordinate_click=(), pattern='', keywords=''):
        #self.thread_local = threading.local()
        self.pattern = pattern
        self.keywords = keywords
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
        self.download_all()

    def prepara_dizionario_risposte_con_punteggi_e_coordinate_cliccabili(self):
        # crea un dizionario con 3 chiavi, ovvero le 3 risposte i cui valori sono altri tre dizionari:
        # le chiavi sono i punteggi ottenuti da google, e le coordinate (una tupla) da cliccare nel quiz
        if not self.coord_click:
            self.coord_click = ((0,0), (0,0), (0,0))
        if len(self.lista_url) == 2:
            self.dizionario_di_risposte_e_key_punteggi = {i: {
                '_d_R_': 0, '_dr_R_': 0, '_d_Sola': 0, 'coord_click': self.coord_click[n]} for n, i in enumerate(self.lista_risposte)}
        #print(self.dizionario_di_risposte_e_key_punteggi)
        elif len(self.lista_url) == 3:
            self.dizionario_di_risposte_e_key_punteggi = {i: {
                '_d_R_': 0, '_dr_R_': 0, '_d_Sola': 0, 'url': self.lista_url[n], 'coord_click': self.coord_click[n]} for n, i in enumerate(self.lista_risposte)}
        #print(self.dizionario_di_risposte_e_key_punteggi)


    def download_all(self):
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

        if len(self.lista_url) == 2:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # otterrai una lista contenente due liste:
                # nella prima ci sono i risultati dell'url della domanda, nell'altro quello di domanda e risposte
                self.risultati_soup_google = list(executor.map(self.download_sites, self.lista_url, timeout=3000))
                #print(self.risultati_soup_google)
        else:
        #elif len(self.lista_url) == 3:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # otterrai una lista contenente due liste:
                # nella prima ci sono i risultati dell'url della domanda, nell'altro quello di domanda e risposte
                self.risultati_soup_google = list(executor.map(self.download_sites, self.lista_risposte, timeout=3000))
                #print(self.risultati_soup_google)

        #print(self.dizionario_di_risposte_e_key_punteggi)

    def download_sites(self, url_o_risposta):
        session = requests.Session()
        lista_classi = ['Z0LcW', 'e24Kjd', 'i4J0ge']

        """['i4J0ge', 'SPZz6b', 'DESCRIZIONE_DA_INSERIRE'],
            ['i8Z77e', 'Estratti di liste'],
            ['desktop-title-content', 'desktop-title-subcontent', 'mappa']"""

        if url_o_risposta in self.lista_risposte:
            # attivo questo if, quando  passo una domanda in cui verrà fatta la ricerca tre volte
            risposta = url_o_risposta
            url = self.dizionario_di_risposte_e_key_punteggi[risposta]['url']
        else:
            # attivo questo if se invece è una ricerca classica: Dom + DomE3Risp
            url = url_o_risposta

        with session.get(url, headers=USER_AGENT) as r:
            r.raise_for_status()
            html_doc = r.text
            strainer = SoupStrainer('div', attrs={'id': 'search'})
            soup = BeautifulSoup(html_doc, 'lxml', parse_only=strainer)
            lista_riscontri = []
            lista_non_riscontri = []

            stringa = ''
            stringhe = []

            for classe in lista_classi:
                #print(risposta, classe)
                #stringhe.append(self.get_risultato_from_soup(classe))
                stringa = self.get_risultato_from_soup(classe, soup)
                if stringa:
                    #print('Trovato un risultato:\n {}'.format(stringa))
                    esito, risultato = self.punti_dal_risultato(stringa, url, 2)
                    if esito:
                        lista_riscontri.append(risultato)
                    else:
                        lista_non_riscontri.append(risultato)

            for g in soup.find_all(class_='g'):
                # Adesso cerco diverse cose:
                #print('Cerco: {}'.format(risposta))
                stringa = self.get_risultato_from_soup('st', g)
                if not stringa:
                    continue
                else:
                    #print('Trovato un risultato per {}:\n {}'.format(risposta, stringa))
                    pass
                # Introdotto il 14/09 per velocizzare
                esito, risultato = self.punti_dal_risultato(stringa, url_o_risposta)
                if esito:
                    lista_riscontri.append(risultato)
                else:
                    lista_non_riscontri.append(risultato)

            return lista_riscontri + lista_non_riscontri

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

    def punti_dal_risultato(self, risultato, url_o_risposta, mult=1):
    #Rispetto alla vecchia implementazione analizzo subito la stringa dei risultati di google per tagliare dei cicli for
    # Il parametro mult serve per dare più peso ai risultati che arrivano da alcune fonti (es: caselle speciali)
        if len(self.lista_url) == 2:
            if url_o_risposta == self.lista_url[0]: #ovvero se l'url è lo stesso url della query per la sola domanda su google
                key = '_d_R_'
            else:
                key = '_dr_R_'

            trovato = False
            for risposta in self.lista_risposte:
                """
                if risposta not in self.dizionario_di_risposte_e_key_punteggi:
                    self.dizionario_di_risposte_e_key_punteggi[risposta] = {}
                    self.dizionario_di_risposte_e_key_punteggi[risposta][key] = 0
                else:
                    if key not in self.dizionario_di_risposte_e_key_punteggi[risposta]:
                        self.dizionario_di_risposte_e_key_punteggi[risposta].update({key: 0})
                """
                self.controlla_dizionario(key, risposta)

                index_risultato = str(risultato).lower().find(risposta.lower())
                if index_risultato >= 0:  # se il metodo find non trova niente restiuisce -1
                    # 1)Se trovo una isposta nel risultat la evidenzio nell'HTML
                    risultato = risultato[:index_risultato] + '<b>{}</b>'.format(risposta) + risultato[index_risultato + len(risposta):]
                    # 2) Aggiorno il punteggio
                    self.dizionario_di_risposte_e_key_punteggi[risposta][key] += 1 * mult
                    trovato = True
            return trovato, risultato

        else:
        #elif len(self.lista_url) == 3:
            key = '_d_Sola_'
            trovato = False
            risposta = url_o_risposta
            #print(self.keywords)
            self.controlla_dizionario(key, risposta)
            for keyword in self.keywords:
                #print(keyword)
                index_risultato = str(risultato).lower().find(keyword.lower())
                index_risposta = str(risultato).lower().find(risposta.lower())
                if index_risultato >= 0:  # se il metodo find non trova niente restiuisce -1
                    # 1)Se trovo una risposta nel risultat la evidenzio nell'HTML
                    #print('stottoline: {}'.format(keyword))
                    risultato = risultato[:index_risultato] + '<b>{}</b>'.format(keyword) + risultato[index_risultato + len(keyword):]
                    # 2)Aggiorno il punteggio
                    if index_risposta >= 0:
                        #print('Trovato: {}'.format(risposta))
                        self.dizionario_di_risposte_e_key_punteggi[risposta][key] += (1 * mult)
                        #risultato = risultato[:index_risposta] + '<b>{}</b>'.format(risposta) + risultato[index_risposta + len(risposta):]
                        trovato = True
                        mult += 1
                    else:
                        self.dizionario_di_risposte_e_key_punteggi[risposta][key] += (0.1 * mult)
                    #trovato = True
            if mult == 2:
                trovato = True
            if ('Wikipedia' and risposta) in risultato:
                #print('COMBO: {}'.format(risultato))
                trovato = True
            return trovato, risultato

    def get_risultato_from_soup(self, sunto_css_class, soup):
        sunto_titolo = {'i4J0ge': 'SPZz6b',
                        'e24Kjd': 'LC20lb',
                        'st': 'LC20lb',
                        'Z0LcW': 'e24Kjd'}
        sunto = soup.find(class_=sunto_css_class)
        """
        try:
            print('Sunto trovato:\n {}'.format(sunto.text))
        except:
            return
        """
        stringa = ''
        if not sunto:
            return
        else:
            try:
                titolo = soup.find(class_=sunto_titolo[sunto_css_class])
            except:
                titolo = ''
            finally:
                stringa = str(titolo) + '<br>' + str(sunto)
        return stringa
        """
        try:
            if not sunto.text:
                return
            else:
                try:
                    titolo = soup.find(class_=sunto_titolo[sunto_css_class])
                except:
                    titolo = ''
                finally:
                    stringa = str(titolo) + '<br>' + str(sunto)
            return stringa
        except Exception as e:
            print(e)
            return
        """

    def produci_stringa_risultato(self, soup, css_class_testo, titolo='', testo=''):
        if not testo:
            testo = soup.find(class_=css_class_testo)
        else:
            titolo = soup.find(class_=css_class_testo)
        stringa = str(titolo) + '<br>' + str(testo)
        return stringa

    def controlla_dizionario(self, key, risposta):
        if risposta not in self.dizionario_di_risposte_e_key_punteggi:
            self.dizionario_di_risposte_e_key_punteggi[risposta] = {}
            self.dizionario_di_risposte_e_key_punteggi[risposta][key] = 0
        else:
            if key not in self.dizionario_di_risposte_e_key_punteggi[risposta]:
                self.dizionario_di_risposte_e_key_punteggi[risposta].update({key: 0})

    def rendo_template_html(self):
        file_loader = FileSystemLoader(TEMPLATE_DIR)
        env = Environment(loader=file_loader)
        if len(self.lista_url) == 2:
            template = env.get_template('base2.html')
        else:
            template = env.get_template('base3.html')

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