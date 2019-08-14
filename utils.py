import cv2, os, glob
import numpy as np
from collections import defaultdict
from cf import SCREEN_DIR, USER_AGENT
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from bs4 import BeautifulSoup
import requests
import nltk
from nltk import word_tokenize
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
    #diario()
    #nltk_prova()
    #scrape()
    trova_risposta('https://www.google.com/search?q=trama+del+film+rocknrolla&oq=trama+del+film+rocknrolla',
                   ['revolver', 'film', 'banca'])