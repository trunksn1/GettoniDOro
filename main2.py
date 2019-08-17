import os
from ScreenGrabber import ScreenGrab
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore




screen_grabber = ScreenGrab()
while True:
    print('INIZIO GRAB')
    screen_grabber.start_screen_grab()
    screen_grabber.calcolo_spazi_domande_e_risposte()
    screen_grabber.screen_grab()
    print('FINE GRAB\n')

    y = Elaboratore(screen_grabber.screenshot_name)
    z = Identificatore(y.pezzi)
    pp = Punteggiatore([z.domanda_url, z.risp_url], z.risposte)

