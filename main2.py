import install_settings
from ScreenGrabber import ScreenGrab
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore
from Sarto import Sarto
#from Guiatore import Guiatore
from cf import regex_patt_compilato
import time
from datetime import date
from helpers import logging
import multiprocessing as mp


#TODO: controllare se nel file install_settings c'è il percorso di PyTesseract, se non c'è ottienilo (via GUI)
screen_grabber = ScreenGrab()
cords = ()
counter = 0
modo = 'w'

while True:

    print('INIZIO GRAB')
    screen_grabber.start_screen_grab()
    # Calcolo solo se ho delle coordinate nuove!
    if screen_grabber.key_pressed == 'F6':
        start = time.time()
        cords = screen_grabber.calcolo_spazi_domande_e_risposte()
    # Se riutilizzo le vecchie coordinate non ho bisogno di ricalcolare nulla
    elif screen_grabber.key_pressed == 'F9':
        start = time.time()
        pass
    screen_grabber.screen_grab()
    print('FINE GRAB\n')
    el = Elaboratore(screen_grabber.screenshot_name)
    el.salva_i_pezzi()
    print('Tempo elaboratore: {}'.format(time.time()-start))
    id = Identificatore(el.pezzi)

    #TODO --------------- Esperimento
    """Esperimento per KEYWORDS"""
    # TODO quando avrò implementato la funzione Identificatore.trova_keyword()
    flag_query = id.trova_keyword(regex_patt_compilato, id.domanda)
    #print(flag_query)
    id.prepara_url_da_ricercare(id.domanda, id.risposte, flag_query)
    print('Tempo identificatore: {}'.format(time.time() - start))
    try:
        pp = Punteggiatore(id.query_urls, id.risposte, id.domanda, keywords=id.keywords)
        #print(pp.dizionario_di_risposte_e_key_punteggi)
        pp.rendo_template_html()
        print('Tempo punteggiatore: {}'.format(time.time() - start))
        print(time.time()-start)
        if counter != 0:
            modo = 'a'
        logging(modo, id.domanda, id.risposte, id.query_urls, pp.dizionario_di_risposte_e_key_punteggi, date.today())
    except Exception as e:
        print('********ERRORE*********')
        print(e)
        continue
    counter += 1

    #input('STOP')
    """FINE ESPERIMENTO"""

    #id.prepara_url_da_ricercare(id.domanda, id.risposte, query)

    """Funzionanti al 07/12/2019"""
    #id.prepara_url_da_ricercare(id.domanda, id.risposte)
    #print('Tempo identificatore: {}'.format(time.time() - start))

    #pp = Punteggiatore([id.domanda_url, id.risp_url], id.risposte, id.domanda)#, regex_patt_compilato)

    """Prova di multiprocessing
    print('IMPOSTAZIONE')
    pool = mp.Pool(processes=4)

    q = mp.Queue()
    x = pool.map(pp.do_something, q)
    #p = mp.Process(target=pp.do_something, args=(q,))
    # p_gsearch.deamon = True
    print('PreInizio')
    print(x)
    
    p.daemon = True
    p.start()
    while True:
        # Thread counts finished
        count_cur = 0
        count_max = 3

        data = q.get()
        print(data)
        if q.empty():
            count_cur += 1
            print('Fine')
            p.join()
    
    print('FUORI DAL TUNNEL')
    FINE Prova di multiprocessing"""


    #print(pp.dizionario_di_risposte_e_key_punteggi)
    #pp.rendo_template_html()
    #print('Tempo punteggiatore: {}'.format(time.time() - start))
    #print(time.time()-start)

