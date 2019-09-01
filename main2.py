import os
from ScreenGrabber import ScreenGrab
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore
#from Guiatore import Guiatore
from helpers import ottieni_drivers



#drivers = ottieni_drivers()
screen_grabber = ScreenGrab()
while True:
    print('INIZIO GRAB')
    screen_grabber.start_screen_grab()
    screen_grabber.calcolo_spazi_domande_e_risposte()
    screen_grabber.screen_grab()
    print('FINE GRAB\n')
    el = Elaboratore(screen_grabber.screenshot_name)
    id = Identificatore(el.pezzi)
    pp = Punteggiatore([id.domanda_url, id.risp_url], id.risposte, id.domanda)
    #win = Guiatore(z.risposte, [z.domanda_url, z.risp_url], drivers, pp.risultati_soup_google)
    #win.crea_layout_per_gui(pp.dizionario_di_risposte_e_punteggi)
