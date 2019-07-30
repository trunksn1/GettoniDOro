import os
from ScreenGrabber import ScreenGrab
from Elaboratore import Elaboratore
from Identificatore import Identificatore


while True:
    print('INIZIO GRAB')
    screen_grabber = ScreenGrab()
    screen_grabber.start_screen_grab()
    screen_grabber.calcolo_spazi_domande_e_risposte()
    screen_grabber.screen_grab()
    print('FINE GRAB\n')

    y = Elaboratore(screen_grabber.screenshot_name)
    z = Identificatore(y.pezzi)
