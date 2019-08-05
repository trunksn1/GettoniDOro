import cv2, os, glob
import numpy as np
from cf import SCREEN_DIR
from Elaboratore import Elaboratore
from Identificatore import Identificatore
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

def scrape():
    from bs4 import BeautifulSoup
    import requests
    print('ciao')
    USER_AGENT = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

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
    x = soup.find(class_='Z0LcW')
    if x:
        try:
            sibling = x.find('a')
            print(sibling.contents[0])
        except:
            print(x.contents[0])
    else:
        for s in soup.find_all("div", class_="s"):#soup.select('.st'):#
            print(s.text)


if __name__ == '__main__':
    #aggancia_dom_e_risp()
    #diario()
    #nltk_prova()
    scrape()