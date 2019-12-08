# -- coding: utf-8 --
import cv2, os, glob
import csv
import numpy as np
from collections import defaultdict, Counter
from cf import SCREEN_DIR, USER_AGENT, BASE_DIR
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore
import sqlite3 as sql3
import string

from bs4 import BeautifulSoup
import requests, time
import nltk
from nltk import word_tokenize
import pprint, threading
import shutil

from paroleparole import inutili



from nltk.corpus import stopwords

PATH_SEPARATE = os.path.join(SCREEN_DIR, 'da_concatenare')
PATH_CONCATENATE = os.path.join(SCREEN_DIR, 'concatenate')
PATH_DOM_BLUE = os.path.join(SCREEN_DIR, 'Domande BlueStacks')
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

        cv2.imwrite('out{}.png'.format(n+500), vis)
        print('fatto')

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
            #if n == 10:
            #    break
            print(immagine)
            try:
                scrivente = csv.writer(log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                print(immagine)
                drivers = ''
                el = Elaboratore(immagine)
                el.salva_i_pezzi()
                id = Identificatore(el.pezzi)
                id.prepara_url_da_ricercare(id.domanda, id.risposte)
                pp = Punteggiatore([id.domanda_url, id.risp_url], id.risposte, id.domanda)
                #print('Thread attivi: ', end='')
                #print(threading.active_count())



                #win = Guiatore(id.risposte, [id.domanda_url, id.risp_url], drivers, pp.risultati_soup_google)
                #win.crea_layout_per_gui(pp.dizionario_di_risposte_e_punteggi)
                #win.crea_layout_per_gui(pp.dizionario_di_risposte_e_key_punteggi)
                #pp = Punteggiatore([id.domanda_url, id.risp_url], id.risposte)
                mess = '****** Domanda numero: {} ******'.format(n)
                print(mess)
                print(id.domanda)
                print(id.risposte)
                print(pp.dizionario_di_risposte_e_key_punteggi)
                scrivente.writerow([])
                scrivente.writerow([mess, '****', '****', '****'])
                scrivente.writerow([id.domanda, 'SoloD', '+Risp', 'TOT'])
                for i in range(3):
                    scrivente.writerow([id.risposte[i], pp.dizionario_di_risposte_e_key_punteggi[id.risposte[i]]['_d_R_'], pp.dizionario_di_risposte_e_key_punteggi[id.risposte[i]]['_dr_R_'],
                                        pp.dizionario_di_risposte_e_key_punteggi[id.risposte[i]]['_d_R_'] + pp.dizionario_di_risposte_e_key_punteggi[id.risposte[i]]['_dr_R_']])
            except AttributeError:
                print(immagine, 'AttributeErrr')
                continue
            except IndexError:
                print(immagine, 'IndexError')
                continue
            time.sleep(5)



def download_site(url):
    print(url)
    start = time.time()
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

            # Quando hai i box dei risultati, sotto la classe 'g' non trovi invece le classi r o st
            if not st or not r:
                # Andiamo alla ricerca di eventuali box (infame capoluogo calabrese)
                s = g.find('div', attrs={'class': 'Z0LcW'})  # contiene il trafiletto per catanzaro (ma sotto ha un'altra classe) e la sinossi del film rocknrolla (direttamente)
                if not s: # Bisogna capire se ci sono altre possibili classi che si possono aprire
                    #tit = g.find('div', attrs={'class': 'JpTGae'})  #In alcune answer box questa classe contiene il titolo
                    s = g.find('span', attrs={'class': 'e24Kjd'})  # c'è il trafiletto di wikipedia, ed alcuni sunti vari
                    if not s:
                        continue
                stringa =  s.text

            if st and r:
                tit = r.text
                corp = st.text
                stringa = tit + '\n' + corp

            stringa = '\n--> '.join(stringa.split('...'))

            risultato.append(stringa)
        return risultato

def creatore_gui(dati):
    sg.ChangeLookAndFeel('GreenTan')
    layout = []
    if len(dati) % 2:
        dati.append('')
    lungh_lista = len(dati)//2
    print(lungh_lista//2)
    for n, dato in enumerate(dati):
        print (n)
        layout.append(

                [sg.Multiline(dato, size=(50, 4))]) #, sg.Multiline(dati[n+lungh_lista], size=(50, 4))])


        if n == 6: #(lungh_lista-1):
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

def ottieni_database():
    db_file = os.path.join(SCREEN_DIR,  'archivio_domande.db')
    # Connettiamo il database e verifichiamo che ci siano le tabelle
    db = sql3.connect(db_file)
    """Verifica che il database abbia la sue tabelle, altrimenti le crea"""
    try:
        # cerca la tabella file_salvati nel database
        db.execute("SELECT * FROM Domande")
        print("Database già esistente, da aggiornare")
    except:
        # crea le tabelle nel database
        print("Database da creare!")
        db.execute(
            'CREATE TABLE "Domande" ( `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `Domanda` TEXT NOT NULL, `Immagine` TEXT UNIQUE, `Categoria` TEXT, `Keyword` TEXT, `Problema` TEXT  )')
        db.execute(
            'CREATE TABLE `Risposte` ( `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `Risposta` TEXT, `RispCorretta` INTEGER, `IDDomanda` INTEGER NOT NULL, `PtiDom` INTEGER, `PtiDomRisp` INTEGER, `PtiTot` INTEGER   )')
        db.execute(
            'CREATE TABLE `RispDom` ( `IDRisp` INTEGER NOT NULL UNIQUE, `IDDom` INTEGER NOT NULL )')
        db.execute(
            'CREATE TABLE `Links_Google` ( `SoloDom` TEXT NOT NULL, `DomRisp` TEXT NOT NULL, `IDDom` INTEGER NOT NULL )')
    return db

def is_doppione(db, cursore, immagine, domanda):
    try:
        cursore.execute('SELECT ID FROM Domande WHERE Immagine=? or Domanda=?', (str(immagine), str(domanda)))
        x = cursore.fetchone()
    except sql3.IntegrityError:
        print("Domanda, già presente nel database")
        return False
    else:
        if not x:
            return False
        return True

def popola_database(db, cursore, domanda, immagine, risposte, dict_pti, linkDom, linkDomRisp):
    """Popola il database"""
    """try:
        cursore.execute('SELECT ID FROM Domande WHERE Domanda=? or Immagine =?', (str(domanda), str(immagine)))
    except sql3.IntegrityError:
        print("Domanda, già presente nel database")
        return
    else:"""
    domanda = " ".join(domanda.split("\n"))
    print("AGGIUNGIAMOLA!")
    cursore.execute('INSERT INTO Domande(Domanda, Immagine) VALUES(?,?)',
                    (str(domanda), str(immagine)))
    db.commit()

    #cursore.execute('SELECT ID FROM Domande WHERE Domanda=?', (str(domanda),))
    cursore.execute('SELECT max(ID) FROM Domande')
    id_domanda = cursore.fetchone()[0]

    for i, risposta in enumerate(risposte):
        risposta = " ".join(risposta.split("\n"))
        cursore.execute('INSERT INTO Risposte(Risposta, IDDomanda, PtiDom, PtiDomRisp, PtiTot ) VALUES(?,?,?,?,?)',
                        (str(risposta), id_domanda,
                         int(dict_pti[risposte[i]]['_d_R_']),
                         int(dict_pti[risposte[i]]['_dr_R_']),
                         int(dict_pti[risposte[i]]['_d_R_']) + int(dict_pti[risposte[i]]['_dr_R_'])))
        db.commit()

        #cursore.execute('SELECT ID FROM Risposte WHERE Risposta=?', (str(risposta),))
        id_risp = cursore.lastrowid

        cursore.execute('INSERT INTO RispDom(IDRisp, IDDom) VALUES(?,?)',
                        (id_risp, id_domanda))
        db.commit()

    cursore.execute('INSERT INTO Links_Google(SoloDom, DomRisp, IDDom) VALUES(?,?,?)',
                    (str(linkDom), str(linkDomRisp), id_domanda))
    db.commit()
    return False

def lavora_database():
    db_file = os.path.join(SCREEN_DIR, 'archivio_domande.db')
    # Connettiamo il database e verifichiamo che ci siano le tabelle
    db = sql3.connect(db_file)
    cursore = db.cursor()
    domande = db.execute("SELECT Domanda FROM Domande")
    for n, d in enumerate(domande, 1):
        #d = " ".join(d[0].split("\n"))
        #db.execute("UPDATE Domande SET Domanda = ? WHERE ID = ?", (d,n))
        print(d[0])

def get_keyword_database():
    # Creo una nuova tabella nel db per le parole chiave, se c'è l'aggiorno semplicemente
    # Ogni domanda presente nel database viene analizzata
    # Elimino le parole inutili
    # Seleziono le parole in maiuscolo o tra virgolette (keyword vere e proprie)
    # Salvo tutte le altre (sostantivi)
    db_file = os.path.join(SCREEN_DIR, 'archivio_domande.db')
    # Connettiamo il database e verifichiamo che ci siano le tabelle
    db = sql3.connect(db_file)
    domande = db.execute("SELECT Domanda FROM Domande")
    print(inutili)
    with open(os.path.join(PATH_DOM_RSP, 'keywords.csv'), 'w', newline='') as log:
        for domanda in domande:
            print(domanda)
            d = domanda[0].replace('\'', ' ')
            print(d)
            d = d.split()
            print(d)

            virgolettato = False
            parole = []
            for parola in d:

                if '"' in parola and virgolettato:
                    # riconosce il termine del virgolettato"
                    p += ' ' + parola
                    virgolettato = False
                    parole.append(p)
                    continue

                elif '"' in parola and not virgolettato:
                    # riconosce "l'inizio
                    if parola[-1] == '"' or parola[-2] == '"':
                        # riconosce quando virgoletti una singola "parola"
                        parole.append(parola)
                        continue
                    virgolettato = True
                    p = parola
                    continue

                elif '"' not in parola and virgolettato:
                    # riconosce le parole nel mezzo della virgolettata
                    p += ' ' + parola
                    continue

                if parola.lower() not in inutili:
                    parole.append(parola)
            try:
                scrivente = csv.writer(log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                scrivente.writerow([domanda])
                p = ' '.join(parole)
                print(p)
                scrivente.writerow([p])
                scrivente.writerow()
            except:
                print('Errore')

            #parole = [parola for parola in d if parola.lower() not in inutili]



def istogramma_database():
    db_file = os.path.join(SCREEN_DIR, 'archivio_domande.db')
    # Connettiamo il database e verifichiamo che ci siano le tabelle
    db = sql3.connect(db_file)
    hist = dict()
    domande = db.execute("SELECT Domanda FROM Domande")
    for domanda in domande:
        for d in domanda[0].split():
            d = d.strip(string.punctuation + string.whitespace)
            d = d.lower()
            hist[d] = hist.get(d, 0) + 1
    return hist

def processa_istogramma_database(nome='istogramma_domande.csv'):
    h = istogramma_database()
    with open(os.path.join(PATH_DOM_RSP, nome), 'w', newline='') as log:
        for k, v in h.items():
            try:
                scrivente = csv.writer(log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                scrivente.writerow([k, v])
            except:
                print('Errore')

def problemi_database_sposta_immagini():
    db_file = os.path.join(SCREEN_DIR, 'archivio_domande.db')
    # Connettiamo il database e verifichiamo che ci siano le tabelle
    db = sql3.connect(db_file)
    path_problematiche = os.path.join(SCREEN_DIR, 'PROBLEMATICHE')
    path_p_identificazione = os.path.join(path_problematiche, 'Identificazione')
    path_p_acquisizione = os.path.join(path_problematiche, 'Acquisizione')
    path_p_risposte = os.path.join(path_problematiche, 'Mancate_Risposte')
    if not os.path.isdir(path_problematiche):
        os.makedirs(path_problematiche)
        os.makedirs(path_p_identificazione)
        os.makedirs(path_p_acquisizione)
        os.makedirs(path_p_risposte)
    hist = dict()
    domande_immagini = db.execute("SELECT Immagine, Problema FROM Domande WHERE Problema IS NOT NULL")
    risps = db.execute("SELECT IDDomanda, ID  FROM Risposte")
    list_dom = []

    # Serve per trovare nel db quelle domande in cui le risposte riconosciute non sono 3, ma sono di meno o di più
    """
    for n, tupla in enumerate(risps.fetchall()):
        list_dom.append(tupla[0])
    conta = Counter(list_dom)
    print(conta)
    for id in conta:
        if conta[id] != 3:
            query = "Update Domande SET Problema = ? where ID = ?"
            data = ('Ric_Risposte', id)
            db.execute(query, data)
    """
    # Fine

    for d in domande_immagini:
        img = d[0]
        if d[1] == 'Identificazione':
            path_destinazione = os.path.join(path_p_identificazione, os.path.basename(d[0]))
            try:
                shutil.move(d[0], os.path.join(path_p_identificazione, os.path.basename(d[0])))
            except Exception as e:
                print(e)
        elif d[1] == 'Acquisizione':
            path_destinazione = os.path.join(path_p_acquisizione, os.path.basename(d[0]))
            try:
                shutil.move(d[0], os.path.join(path_p_acquisizione, os.path.basename(d[0])))
            except Exception as e:
                print(e)
        elif d[1] == 'Ric_Risposte':
            path_destinazione = os.path.join(path_p_risposte, os.path.basename(d[0]))
            try:
                shutil.move(d[0], os.path.join(path_p_risposte, os.path.basename(d[0])))
            except Exception as e:
                print(e)
        else:
            continue
        sql_update_query = """Update Domande SET Immagine = ? where Immagine = ?"""
        data = (path_destinazione, img)

        db.execute(sql_update_query, data)
        db.commit()

def main_database():
    #sorted(glob.glob('*.png'), key=os.path.getmtime)
    immagini_da_studiare = sorted(glob.glob(os.path.join(PATH_DOM_BLUE, '*'), recursive=True), key=os.path.getmtime, reverse=True) + sorted(glob.glob(
        os.path.join(PATH_DOM_RSP, '*'), recursive=True), key=os.path.getmtime, reverse=True)
    #immagini_da_studiare = glob.glob(os.path.join(PATH_DOM_BLUE, '*'), recursive=True) + glob.glob(os.path.join(PATH_DOM_RSP, '*'), recursive=True)
    db = ottieni_database()
    cursore = db.cursor()

    for n, immagine in enumerate(immagini_da_studiare):
        print(immagine)
        tempo_attesa = 3
        # Controllo se l'immagine è già presente nel database, in quel caso vado oltre.

        try:
            el = Elaboratore(immagine)
            el.salva_i_pezzi()
            id = Identificatore(el.pezzi)
            if is_doppione(db, cursore, immagine, id.domanda):
                print("Doppione")
                tempo_attesa = 0
                continue
            id.prepara_url_da_ricercare(id.domanda, id.risposte)
            pp = Punteggiatore([id.domanda_url, id.risp_url], id.risposte, id.domanda)

            #id.domanda = " ".join(id.domanda.split("\n"))
            popola_database(db,
                            cursore,
                            id.domanda,
                            immagine,
                            id.risposte,
                            pp.dizionario_di_risposte_e_key_punteggi,
                            id.domanda_url,
                            id.risp_url)


        except Exception as e:
            print(e)
            continue
        finally:
            time.sleep(tempo_attesa)

if __name__ == '__main__':
    #aggancia_dom_e_risp()
    #diario_csv()
    #get_keyword_database()
    main_database()
    #lavora_database()
    #processa_istogramma_database()
    #problemi_database_sposta_immagini()
    #nltk_prova()
    #scrape()
    #trova_risposta('https://www.google.com/search?q=trama+del+film+rocknrolla&oq=trama+del+film+rocknrolla',
    #               ['revolver', 'film', 'banca'])
    urls = [
        'https://www.google.com/search?q=a+cosa+corrisponde+sigla+usa&oq=a+cosa+corrisponde+sigla+usa',
        'https://www.google.com/search?q=capoluogo+della+calabria',
        'https://www.google.com/search?q=trama+del+film+rocknrolla&oq=trama+del+film+rocknrolla',
        'https://www.google.com/search?q=chi+è+il+ministro+degli+affari+esteri+europeo',
        'https://www.google.com/search?&q=what+are+the+possible+box+in+a+google+search',

        ]
    #ris = download_site(urls[-1])
    #creatore_gui(ris)
    #for url in urls:
    #    ris = download_site(url) #[0])
    #    creatore_gui(ris)
    #    time.sleep(6)
