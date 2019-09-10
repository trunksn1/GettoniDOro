import install_settings
from ScreenGrabber import ScreenGrab
from Elaboratore import Elaboratore
from Identificatore import Identificatore
from Punteggiatore import Punteggiatore
#from Guiatore import Guiatore
import time




#TODO: controllare se nel file install_settings c'è il percorso di PyTesseract, se non c'è ottienilo (via GUI)
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

