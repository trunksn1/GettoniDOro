import queue, threading
from selenium import webdriver
#from cf import WEBDRIVER_PATH, dimensioni_browser, coordinate_drivers_browser
import re
from collections import ChainMap
import timeit
import multiprocessing as mp

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
    
    if not regex_patt_compilato:
        regex_patt_compilato = re.compile(r'''

(?P<traquesti>(?:[Qq]ual.?)?(?:\D*?quest.))|                        # Cerca "Quale Tra questi"
\b(?P<corse>Moto\s?[GPgp]+?|Formula\s(?:1|uno|Uno)|Gran\sPremio)\b| # cerca riferimenti alle gare di corsa
(?P<bandiera>\bbandier.\b)|                                         # cerca bandiere
(?P<prima>\bprim.|pi[uù] recente\b)|                                # Cerca riferimenti temporali
(?P<keyw1>\b[A-Z][a-z]+\b)|                                         # Cerca parole inizianti con la maiuscola
\"(?P<keyw2>.+?)\"                                                  # cerca frasi tra "virgolette"
''', re.VERBOSE)
#(?P<traquesti>(?:[Qq]ual.?)?(?:\D*?quest.))|\b(?P<corse>Moto\s?[GPgp]+?|Formula\s(?:1|uno|Uno)|Gran\sPremio)\b|(?P<bandiera>\bbandier.\b)|(?P<prima>\bprim.|pi[uù] recente\b)|(?P<keyw1>[A-Z][a-z]+)|\"(?P<keyw2>.+?)\"

#(?:[Qq]ual.?)?(?:\D*?quest.)|(?:qual.?)|\bMoto\s?[GPgp]+?|Formula\s(?:1|uno|Uno)|Gran\sPremio\b|\bbandier.\b|\bprim.|pi[uù] recente\b|[A-Z][a-z]+\b|\".+?\"


    #mo = regex.search(domanda)
    d = domanda9
    mo = regex_patt_compilato.findall(d)

    diz = {"traquesti": [], "corse": [], "bandiera": [], "prima": [], "keyw1": [], "keyw2": []}

    x = { diz[k].append(v)  for m in regex_patt_compilato.finditer(d) for k, v in m.groupdict().items() if v }

    print(d)
    print(mo)
    print(diz)

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


if __name__ == '__main__':
    trova_keyword()