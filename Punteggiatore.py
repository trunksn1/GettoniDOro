# -- coding: utf-8 --
from bs4 import BeautifulSoup
import requests
from cf import USER_AGENT, TEMPLATE_DIR, CSS_DIR
import concurrent.futures
import threading
import pprint, time
import webbrowser
from jinja2 import Environment, FileSystemLoader


class Punteggiatore():
    def __init__(self, urls, lista_risposte, domanda, coordinate_click=()):
        self.thread_local = threading.local()
        self.lista_url = urls
        self.domanda = domanda
        self.lista_risposte = lista_risposte
        self.coord_click = coordinate_click
        #start = time.time()
        #self.download_all_sites(urls)
        #self.chiama_ottieni_punti()
        #print(TEMPLATE_DIR)
        #self.rendo_template_html()

        """ Introdotottu il 14/09 per miglioare efficienza"""
        if coordinate_click:
            self.prepara_dizionario_risposte_con_punteggi_e_coordinate_cliccabili()
        else:
            self.dizionario_di_risposte_e_key_punteggi = {}
        self.lista_risp_riscontri = []
        self.lista_risp_senza_riscontri = []
        self.download_all_sites(urls)
        #print(TEMPLATE_DIR)
        #self.rendo_template_html()
        #print(time.time() - start)

    def prepara_dizionario_risposte_con_punteggi_e_coordinate_cliccabili(self):
        # crea un dizionario con 3 chiavi, ovvero le 3 risposte i cui valori sono altri tre dizionari:
        # le chiavi sono i punteggi ottenuti da google, e le coordinate (una tupla) da cliccare nel quiz
        self.dizionario_di_risposte_e_key_punteggi = {i: {
            '_d_R_': 0, '_dr_R_': 0, 'coord_click': self.coord_click[n]} for n, i in enumerate(self.lista_risposte)}
        print(self.dizionario_di_risposte_e_key_punteggi)


    def download_site_preserva_html(self, url):
        # Tenta di guardare anche nei box di google
        session = requests.Session()
        risultato = []
        with session.get(url, headers=USER_AGENT) as r:
            r.raise_for_status()
            html_doc = r.text
            soup = BeautifulSoup(html_doc, 'html.parser')
            lista_riscontri = []
            lista_non_riscontri = []

            # Tutti i risultati sono al di sotto di un elemento: class='g'
            for g in soup.find_all(class_='g'):
                # Adesso cerco diverse cose:
                r = g.find(class_='ellip')  # contiene il titolo del risultato (senza l'url che sta in altra classe)
                st = g.find('span', attrs={'class': 'st'})  # racchiude il sunto del risultato

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

                """Introdotto il 14/09 per velocizzare"""
                esito, risultato = self.punti_dal_risultato(stringa, url)
                if esito:
                    lista_riscontri.append(risultato)
                else:
                    lista_non_riscontri.append(risultato)
            return lista_riscontri + lista_non_riscontri

            ### Vecchio metodo
            #    risultato.append(stringa)
            #return risultato


    def download_all_sites(self, sites):
        # Preso da un articolo su RealPython che parlava di Concurrency/multiprocessing
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # otterrai una lista contenente due liste:
            # nella prima ci sono i risultati dell'url della domanda, nell'altro quello di domanda e risposte
            self.risultati_soup_google = list(executor.map(self.download_site_preserva_html, sites, timeout=3000))
        #print(self.dizionario_di_risposte_e_key_punteggi)

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


    def punti_dal_risultato(self, risultato, url):
    #Rispetto alla vecchia implementazione analizzo subito la stringa dei risultati di google per tagliare dei cicli for
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
                self.dizionario_di_risposte_e_key_punteggi[risposta][key] += 1
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