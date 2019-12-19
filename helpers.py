import queue, threading
from selenium import webdriver
#from cf import WEBDRIVER_PATH, dimensioni_browser, coordinate_drivers_browser
import re
from collections import ChainMap
import timeit
import multiprocessing as mp
import json

def set_driver_new(coordinate_browser, queue):
    driver = webdriver.Chrome(WEBDRIVER_PATH)
    driver.set_window_size(*dimensioni_browser)
    driver.set_window_position(*coordinate_browser)
    queue.put(driver)

def queue_driver_to_list( driv_queue):
        drivers = []
        while True:
            try:
                driv = driv_queue.get()
                print(driv)
            except queue.Empty:
                continue
            if driv:
                drivers.append(driv)
            if len(drivers) == 2:
                break
        return drivers

def ottieni_drivers():
    print('sono nella funzione degli helpers: ottieni drivers')
    drivers_queue = queue.Queue()
    threading.Thread(target=set_driver_new, args=(coordinate_drivers_browser[0], drivers_queue,), daemon=False).start()
    threading.Thread(target=set_driver_new, args=(coordinate_drivers_browser[1], drivers_queue,), daemon=False).start()
    drivers = queue_driver_to_list(drivers_queue)
    print(drivers)
    return drivers


def trova_keyword(regex_patt_compilato='', domanda=''):
    domanda1 = 'Rosa Parks, la cosidetta "signora dei pullman", è nata nell\'anno:'
    domanda2 = 'Al Gran premio di MotoGP o di formula uno tifiamo Ferrari in Formula 1\n'
    domanda3 = 'Quale tra questi Re del Portogallo è il più pagato?'
    domanda4 = 'Tra queste canzoni, quale è stata scritta per prima?'
    domanda5 = 'Quale tra queste aziende ha il ricavato maggiore in Lettonia?'
    domanda6 = 'Quale tra questi Stati è più popolato?'
    domanda7 = 'Quale tra questi Stati è più popolato ed ha la bandiera più Falsa prima di "tua nonna" e "tua sorella"?'
    domanda8 = 'Quale tra questi "Classici" Disney è stato distribuito prima?'
    domanda9 = 'Al Gran Premio di Formula 1 di Gran  Bretagna 2019, Charles Leclerc è arrivato prima di "tua nonna" che pilota in Moto Gp di merda:'
    domanda0 = 'Chi di loro è il più grande Stronzo del Mondo nella serie TV "ciucciami il cazzo"?'
    domanda11= 'Quale di queste serie TV trasmesse su Netflix è composta da meno stagioni?'
    domanda12 = 'Quante stagioni ha la serie televisiva "mi trombo tua nonna su Netflix"?'
    domanda13 = 'Quante stagioni ci sono nel calendario tigrino?'
    domanda14 = 'Chi tra loro ha chiuso in miglior posizione il Gran Premio della Malesia di MotoGP?'
    domanda15 = 'Quale tra questi artisti è un\'icona femminista?'

    if not regex_patt_compilato:
        regex_patt_compilato = re.compile(r'''

            (?P<traquesti>(?:[Qq]ual.?|[Ch]i)?(?:\D*?quest.|\D*?loro))|         # Cerca "Quale tra questi|Chi tra loro"
            \b(?P<corse>Moto\s?[GPgp]+?|Formula\s(?:1|uno|Uno)|Gran\sPremio)\b| # cerca riferimenti alle gare di corsa
            (?P<bandiera>\bbandier.\b)|                                         # cerca bandiere
            (?P<serietv>(?:\D*?stagioni)?\b[Ss]erie\s?[Tt].*?\b(?:\D*?stagioni)?)|                                # cerca il numero di stagioni di serie TV
            (?P<prima>\bprim.|pi[uù] recente\b)|                                # Cerca riferimenti temporali
            (?P<keyw1>\b[A-Z][a-z]+\b)|                                         # Cerca parole inizianti con la maiuscola
            \"(?P<keyw2>.+?)\"|                                                 # cerca frasi tra "virgolette"
            (?P<keyw3>\w+)                                                      # restanti parole
            ''', re.VERBOSE)
#(?P<traquesti>(?:[Qq]ual.?)?(?:\D*?quest.))|\b(?P<corse>Moto\s?[GPgp]+?|Formula\s(?:1|uno|Uno)|Gran\sPremio)\b|(?P<bandiera>\bbandier.\b)|(?P<prima>\bprim.|pi[uù] recente\b)|(?P<keyw1>[A-Z][a-z]+)|\"(?P<keyw2>.+?)\"

#(?:[Qq]ual.?)?(?:\D*?quest.)|(?:qual.?)|\bMoto\s?[GPgp]+?|Formula\s(?:1|uno|Uno)|Gran\sPremio\b|\bbandier.\b|\bprim.|pi[uù] recente\b|[A-Z][a-z]+\b|\".+?\"


    #mo = regex.search(domanda)
    d = domanda15
    mo = regex_patt_compilato.findall(d)

    diz = {"traquesti": [], "corse": [], "bandiera": [], "serietv": [], "prima": [], "keyw1": [], "keyw2": [], 'keyw3': []}

    x = { diz[k].append(v)  for m in regex_patt_compilato.finditer(d) for k, v in m.groupdict().items() if v }

    #print(d)
    #print(mo)
    print(diz)
    print(x)
    for item, v in diz.items():
        print(v)
        if v:
            print(item, v)

    try:
        print('griyos')
        for g in mo.groups():
            print(g)
        print(mo.groups())
        #print(mo.group())
    except:
        print('except')
        #print(len(mo))
        for g in mo:
            print(g)

def copia():
    answers = {}
    lookup_info = {}
    ans1 = "Vasco Rossi"
    ans2 = "Tua Sorella"
    ans3 = "L'Impero Ottomano"
    risp = [ans1, ans2, ans3]
    counter = 1
    for ans in risp:
        answers[ans] = {
                        "answer": ans,
                        "keywords": [],
                        "score": 0,
                        "index": str(counter)
                    }
        lookup_info[ans] = []
        counter += 1
    print(answers)
    print(lookup_info)
    for i, ans in answers.items():
        print('i: ', i)
        print('ans: ', ans)
        print("lookup_info: ", lookup_info)
        l_info = lookup_info[ans['answer']]
        print("lookup_info[ans['answer']]: ", l_info)
        print()
        l_info.append("[Google]: " + "Sono un Risultato Google")
        print(l_info)
        keywords = ''   #tutti i sostantivi trovati nei risultati di google. Usa la libreria NLTK, ma in italiano?
        pacchetto = ans['answer'], keywords, l_info

def logging(modo, domanda, risposte, link, dizionario, data, errore=''):
    with open("log.txt", modo) as file:
        if errore:
            file.write('°***°***°***°***°\n')
            file.write('ERRORE-ERRORE\n')
            file.write(str(errore))
            file.write('°***°***°***°***°\n')
            file.write('\n')
            try:
                if modo == 'w':
                    file.write('+------------+\n')
                    file.write('| ' + str(data) + ' |\n')
                    file.write('+------------+\n')
                file.write('\n')
                file.write('°---°---°---°---°\n')
                file.write(str(domanda))
                file.write('°---°---°---°---°\n')
                file.write('\n')
                file.write('\n'.join(risposte))
                file.write('\n')
            except:
                pass
            finally:
                return
        if modo == 'w':
            file.write('+------------+\n')
            file.write('| ' + str(data) + ' |\n')
            file.write('+------------+\n')
        file.write('\n')
        file.write('°---°---°---°---°\n')
        file.write(str(domanda))
        file.write('°---°---°---°---°\n')
        file.write('\n')
        file.write('\n'.join(risposte))
        file.write('\n')
        file.write('\n'.join(link))
        file.write('\n')
        file.write(json.dumps(dizionario))
        file.write('\n')


if __name__ == '__main__':
    #copia()
    trova_keyword()