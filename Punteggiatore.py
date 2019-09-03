# -- coding: utf-8 --
from bs4 import BeautifulSoup
import requests
from cf import USER_AGENT, TEMPLATE_DIR
import concurrent.futures
import queue, threading
import pprint
import webbrowser,os
from jinja2 import Environment, FileSystemLoader

class Punteggiatore():
    def __init__(self, urls, lista_risposte, domanda):
        self.thread_local = threading.local()
        self.lista_url = urls
        self.domanda = domanda
        self.lista_risposte = lista_risposte

        self.download_all_sites(urls)
        self.chiama_ottieni_punti()
        #self.scrivo_html_con_risultati_e_l_apro()
        print(TEMPLATE_DIR)
        self.rendo_template_html()


    def crea_dizionario_delle_risposte_e_punteggi(self):
        # crea un dizionario con 3 chiavi, ovvero le 3 risposte,
        # i valori delle 3 chiavi è un altro dizionario in cui le chiavi sono le key della gui,
        # ed il suo valore è il punteggio
        self.devoto_oli = {}
        for risp in self.lista_risposte:
            self.devoto_oli[risp] = {}

    def download_site_preserva_html(self, url):
        # Tenta di guardare anche nei box di google
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
            return risultato

    def download_all_sites(self, sites):
        # Preso da un articolo su RealPython che parlava di Concurrency/multiprocessing
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # otterrai una lista contenente due liste, nella prima ci sono i risultati dell'url della domanda, nell'altro quello di domanda e risposte
            self.risultati_soup_google = list(executor.map(self.download_site_preserva_html, sites, timeout=3000))


    def chiama_ottieni_punti(self):
        self.dizionario_di_risposte_e_key_punteggi = {}
        #key = ['_d_RX_', '_dr_RX_']
        key = ['_d_R_', '_dr_R_']

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            self.risultati_google_evidenziati = list(executor.map(self.ottieni_punti_new_per_executor, [
            (self.risultati_soup_google[0], key[0]),
                (self.risultati_soup_google[1], key[1])
                ]))

    def ottieni_punti_new_per_executor(self, risultati_google_e_key):
        # versione per gli executor
        # risultati_google_e_key[0]: corrisponde ai risultati_google
        # risultati_google_e_key[1]: corrisponde alle key che servono in seguito per la gui (formato simile a _D_RX_)

        for n, risposta in enumerate(self.lista_risposte):
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

    def scrivo_html_con_risultati_e_l_apro(self):
        # Con questa funzione scrivo io la pagina HTML,
        # a differenza della gui, posso evidenziare nei risultati eventuali risposte!
        # ed è una rottura in meno di cazzo
        with open('domanda.html', 'w', encoding="utf-8") as pisstaking:
            pisstaking.write('<head><link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css" rel="stylesheet"/></head>')
            pisstaking.write('<font face="verdana" color="green">' + self.domanda +'<br></font>')
            pisstaking.write('<table class="table"><tr>')
            pisstaking.write('<th scope="col">#</th><th scope="col">SoloD</th><th scope="col">Dom+R</th><th scope="col"><b>TOTALE</b></th></tr></thead>')
            pisstaking.write('<tbody>')
            for n, rsp in enumerate(self.lista_risposte):
                pisstaking.write('<tr><th scope="row">{}</th>'.format(rsp))
                pisstaking.write('<td>{}</td>'.format(self.dizionario_di_risposte_e_key_punteggi[rsp]['_d_R{}_'.format(n+1)]))
                pisstaking.write('<td>{}</td>'.format(self.dizionario_di_risposte_e_key_punteggi[rsp]['_dr_R{}_'.format(n+1)]))
                pisstaking.write('<td>{}</td>'.format(self.dizionario_di_risposte_e_key_punteggi[rsp]['_d_R{}_'.format(n+1)] + self.dizionario_di_risposte_e_key_punteggi[rsp]['_dr_R{}_'.format(n+1)]))
                pisstaking.write('</tr>')
            pisstaking.write('</tbody></table>')
            #for n, ris in enumerate(self.risultati_soup_google[0]):
            for n in range(10): # n è pari a dieci, perchè sono dieci i risultati mostrati da google!
                pisstaking.write('<div class="container-fluid">')
                pisstaking.write('<div class="row">')
                pisstaking.write('<div class="col">')
                if n == 0:
                    pisstaking.write('<b>' + 'Domanda' + '</b>')
                pisstaking.write('<br>')
                pisstaking.write('----------------')
                pisstaking.write('<br>')
                try:
                    pisstaking.write(self.risultati_soup_google[0][n])
                except IndexError:
                    print('Non ci sono risultati da mostrare per la sola domanda!')
                    pisstaking.write('<br>')

                pisstaking.write('</div>')
                pisstaking.write('<div class="col">')
                if n == 0:
                    pisstaking.write('<b>' + 'Domanda & Risposte' + '</b>')
                pisstaking.write('<br>')
                pisstaking.write('----------------')
                pisstaking.write('<br>')
                try:
                    pisstaking.write(self.risultati_soup_google[1][n])
                except IndexError:
                    print('Non ci sono risultati da mostrare per domanda e risposte!')
                    pisstaking.write('<br>')
                pisstaking.write('</div></div></div>')

        webbrowser.open(os.path.join('file://', os.getcwd(), 'domanda.html'))

    def rendo_template_html(self):
        pprint.pprint(self.dizionario_di_risposte_e_key_punteggi)
        pprint.pprint(self.risultati_soup_google)
        file_loader = FileSystemLoader(TEMPLATE_DIR)
        env = Environment(loader=file_loader)
        template = env.get_template('base.html')

        with open('domanda.html', 'w', encoding="utf-8") as pisstaking:
            pisstaking.write(
                template.render(domanda=self.domanda,
                                lista_risposte=self.lista_risposte,
                                diz_risposte_e_key_punteggi=self.dizionario_di_risposte_e_key_punteggi,
                                risultati_soup_google=self.risultati_soup_google))

        webbrowser.open('domanda.html')

if __name__ == '__main__':
    lista_urls = ['https://www.google.com/search?q=de+bello+gallico+roma', 'https://www.google.com/search?q=modi+di+dire',]
    lista_risp = ['Caio', 'Cesare', 'Sempronio']
    x = Punteggiatore(lista_urls, lista_risp)