import cv2, os, glob
import csv
import numpy as np
from collections import defaultdict
from cf import SCREEN_DIR, USER_AGENT
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore
from Guiatore import Guiatore
from bs4 import BeautifulSoup
import requests, time
import nltk
from nltk import word_tokenize
import pprint
import PySimpleGUI as sg
from nltk.corpus import stopwords

PATH_SEPARATE = os.path.join(SCREEN_DIR, 'da_concatenare')
PATH_CONCATENATE = os.path.join(SCREEN_DIR, 'concatenate')
PATH_DOM_RSP = os.path.join(SCREEN_DIR, 'Domande_Risposte')
print(PATH_SEPARATE)
print(PATH_CONCATENATE)

def aggancia_dom_e_risp():
    """Serve a incollare insieme gli screenshot in cui ho domande e risposte staccate"""
    if not os.path.isdir(PATH_CONCATENATE):
        os.makedirs(PATH_CONCATENATE)

    # Ottengo la lista di files nella cartella PATH_SEPARATE
    files = glob.glob(os.path.join(PATH_SEPARATE, '*'), recursive=True)
    # Ordino la lista in base alla data di creazione dei file (così da avere in successione: domanda + rispsota)
    files.sort(key=os.path.getmtime)

    # dalla lista separo le domande dalle risposte, gli elementi pari sono domande, i dispari le risposte
    dom = files[::2]
    risp = files[1::2]


    for n in range (len(dom)):
        dom1 = cv2.imread(dom[n])
        ris1 = cv2.imread(risp[n])
        # Prese le immagini le concateno l'una sopra l'altra (axis 0)
        vis = np.concatenate((dom1, ris1), axis=0)

        cv2.imwrite('out{}.png'.format(n), vis)

def diario():
    immagini_da_studiare = glob.glob(os.path.join(PATH_DOM_RSP, '*'), recursive=True)
    print(immagini_da_studiare)
    with open(os.path.join(PATH_DOM_RSP, 'diario.txt'), 'w') as log:
        for n, immagine in enumerate(immagini_da_studiare):
            #if n == 10:
            #    break
            try:
                el = Elaboratore(immagine)
                id = Identificatore(el.pezzi)
                print(id.domanda)
                print(id.risposte)
                mess = '****** Domanda numero: {} ******'.format(n)
                log.write(mess + '\n')
                log.write(id.domanda + '\n\t')
                log.write('\n\t'.join(id.risposte))
                log.write('\n' + '\n')
            except:
                continue

def diario_csv():
    print('SCRIVERO')
    immagini_da_studiare = glob.glob(os.path.join(PATH_DOM_RSP, '*'), recursive=True)
    with open(os.path.join(PATH_DOM_RSP, 'diario.csv'), 'w') as log:
        for n, immagine in enumerate(immagini_da_studiare):
            if n == 10:
                break
            try:
                scrivente = csv.writer(log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                print(immagine)
                el = Elaboratore(immagine)
                id = Identificatore(el.pezzi)
                win = Guiatore(id.risposte, id.lista_di_tutti_gli_url, drivers='')
                pp = Punteggiatore(id.lista_di_tutti_gli_url, id.risposte,
                                   win)  # [z.domanda_url, z.risp_url], z.risposte, win)
                #pp = Punteggiatore([id.domanda_url, id.risp_url], id.risposte)
                mess = '****** Domanda numero: {} ******'.format(n)
                print(mess)
                print(id.domanda)
                print(id.risposte)
                print(pp.punteggi)
                scrivente.writerow([])
                scrivente.writerow([mess, '****', '****', '****'])
                scrivente.writerow([id.domanda, 'SoloD', '+Risp', 'TOT'])
                for i in range(3):
                    scrivente.writerow([id.risposte[i], pp.punteggi[0][id.risposte[i]], pp.punteggi[1][id.risposte[i]], pp.punteggi[2][id.risposte[i]]])
            except AttributeError:
                print(immagine, 'AttributeErrr')
                continue
            except IndexError:
                print(immagine, 'IndexError')
                continue



def download_site(url):
    print(url)
    start = time.time()
    session = requests.Session()
    risultato = []
    with session.get(url, headers=USER_AGENT) as r:
        #print(f"Read {len(r.content)} from {url}")
        r.raise_for_status()
        #print(r)
        html_doc = r.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        #print(soup)
        #risultati_google = soup.select('.bkWMgd .st')
        for g in soup.find_all(class_='g'):
            r = g.find(class_='ellip')
            st = g.find('span', attrs={'class': 'st'})
            superfluo = g.find(class_='JolIg')
            if superfluo:
                continue

            if not st or not r:
                #risultato.append(g.text)
                s = g.find('div', attrs={'class': 'Z0LcW'})
                if not s:
                    s = g.find('span', attrs={'class': 'e24Kjd'})
                    if not s:
                        continue
                stringa = s.text
            if st and r:
                tit = r.text
                corp = st.text
                stringa = tit + '\n' + corp

            print(stringa)
            stringa = '\n--> '.join(stringa.split('...'))

            risultato.append(stringa)


            #print('-----')
        dur = time.time() - start
        print(dur)
        print()
        return risultato
        """    
        #TODO: questo funziona ma non vede il primo box che compare in alto come nel caso del capoluogo della calabria
        risultati_google = soup.find_all('div', attrs={'class':'bkWMgd'})
        for r in risultati_google:
            b = r.find_all('span', attrs={'class':'st'})
            for x in b:
                print(x.get_text())
            #pprint.pprint(b)
        """

        #pprint.pprint(risultati_google)
        #print(len(risultati_google))
        # TODO qui
        #exit()

def creatore_gui(dati):
    # TODO: il programma si blocca quando mostra la GUI, bisogna sfruttrare i thread
    sg.ChangeLookAndFeel('GreenTan')
    layout = []
    if len(dati) % 2:
        dati.append('')
    lungh_lista = len(dati)//2
    print(lungh_lista//2)
    for n, dato in enumerate(dati):
        print (n)
        layout.append(

                [sg.Multiline(dato, size=(50, 4)), sg.Multiline(dati[n+lungh_lista], size=(50, 4))]
            )

        if n == (lungh_lista-1):
            break
    pprint.pprint(layout)
    window = sg.Window('Risposte', default_element_size=(40, 1), grab_anywhere=True, return_keyboard_events=True, keep_on_top=True).Layout(layout)

    start = time.time()
    browser_mostrato = False
    while True:
        dur = time.time() - start
        # Read lancia un event loop, attraverso il parametro timeout ogni X millisecondi
        # viene restituito il contenuto del parametro timeout_key
        event, _ = window.Read(timeout=1000)
        print(dur)
        if event == 'F9:120' or event == 'Exit' or event is None:# or (dur >= 10):
            print('Tempo scaduto: ', dur)
            break
    window.Close()


def nltk_prova():
    #s = "Stavo guardando un film in televisione con protagonisti Ficarra e Picone"
    s = "Chi è il compagno di Ficarra?"
    stop = stopwords.words('italian')
    print(stop)
    print (nltk.pos_tag(word_tokenize(s)))
    x = [w for w in s.split() if w not in stop]
    print(x)

def scrape(q='', risp=''):


    ris_trovate = {}

    #q = 'https://www.google.com/search?q=Come+si+chiama+Trump%3F+AND+%28%22Donald%22+OR+%22Ciccio%22+OR+%22Caio%22%29&oq=Come+si+chiama+Trump%3F+AND+%28%22Donald%22+OR+%22Ciccio%22+OR+%22Caio%22%29'
    #q = 'https://www.google.com/search?q=capoluogo+calabria'
    #q = 'https://www.google.com/search?q=ultimo+album+di+marco+mengoni'
    #q = 'https://www.google.com/search?q=cantante+dei+guns+and+roses'
    q = 'https://www.google.com/search?q=trama+del+film+rocknrolla&oq=trama+del+film+rocknrolla'
    r = requests.get(q, headers=USER_AGENT)
    r.raise_for_status()
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    #x = soup.select('.Z0LcW')
    """x = soup.find(class_='Z0LcW')
    if x:
        try:
            sibling = x.find('a')
            print(sibling.contents[0])
        except:
            print(x.contents[0])
     else:
        for s in soup.find_all("div", class_="s"):#soup.select('.st'):#
            print(s.text)"""
    x = soup.find_all(class_='rc')
    y = soup.select('.rc')# .r .LC20lb')


    for i in y:
        #print(type(i))
        print(i)##.get_text())
        if "revolver" in str(i).lower():
            print("\n*** TROVATO ***\n")
    #print(x.get_text())

def trova_risposta(query, lista_risposte):
    r = requests.get(query, headers=USER_AGENT)
    r.raise_for_status()
    print(r)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    risultati_google = soup.select('.rc')

    punteggio = defaultdict(int)

    for risultato in risultati_google:
        for risposta in lista_risposte:
            if risposta.lower() in str(risultato).lower():
                punteggio[risposta] += 1


    print(punteggio)
    #for risultato in risultati_google:
    #    if True:
    #        pass

if __name__ == '__main__':
    #aggancia_dom_e_risp()
    diario_csv()
    #nltk_prova()
    #scrape()
    #trova_risposta('https://www.google.com/search?q=trama+del+film+rocknrolla&oq=trama+del+film+rocknrolla',
    #               ['revolver', 'film', 'banca'])
    urls = [
        'https://www.google.com/search?q=a+cosa+corrisponde+sigla+usa&oq=a+cosa+corrisponde+sigla+usa',
        'https://www.google.com/search?q=capoluogo+della+calabria',
        'https://www.google.com/search?q=trama+del+film+rocknrolla&oq=trama+del+film+rocknrolla',
        'https://www.google.com/search?q=chi+è+il+ministro+degli+affari+esteri+europeo',

        ]
    #for url in urls:
    ris = download_site(urls[0])
    creatore_gui(ris)